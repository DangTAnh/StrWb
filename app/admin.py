ưm((OrderItem.product_price - OrderItem.product_cost_price) * OrderItem.quantity), 0))
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status == 'Đã xác nhận', OrderItem.product_cost_price.isnot(None))
        .scalar()
    )

    # Q3 — total qualifying items -> derive the conditional profit note.
    total_qual_items = (
        db.session.query(db.func.count(OrderItem.id))
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status.in_(REVENUE_STATUSES))
        .scalar()
    )
    profit_note = None
    if total_qual_items - profit_items > 0:
        profit_note = f'Lợi nhuận tính trên {profit_items} sản phẩm có giá nhập.'

    # Q4 — orders by status. Same group_by pattern as admin.orders() (Phase 7 line 133-135).
    # group_by omits statuses with zero orders (Pitfall 2): template MUST use
    # status_counts.get(s, 0), never subscript.
    status_counts = dict(
        db.session.query(Order.status, db.func.count(Order.id)).group_by(Order.status).all()
    )
    total_orders = sum(status_counts.values())

    # Q5 — inventory counts (STAT-04). Use .is_(True)/.is_(False) for boolean
    # predicates (research anti-pattern: != True/False breaks on SQLite).
    total_products = Product.query.count()
    in_stock = Product.query.filter(Product.quantity > 0, Product.discontinued.is_(False)).count()
    out_of_stock = Product.query.filter(Product.quantity == 0, Product.discontinued.is_(False)).count()
    discontinued = Product.query.filter(Product.discontinued.is_(True)).count()

    return render_template(
        'admin/stats.html',
        revenue=revenue, profit=profit, profit_note=profit_note, units_sold=units_sold,
        confirmed_revenue=confirmed_revenue, confirmed_profit=confirmed_profit,
        status_counts=status_counts, total_orders=total_orders,
        total_products=total_products, in_stock=in_stock, out_of_stock=out_of_stock, discontinued=discontinued
    )


# Minimal detail route — full detail UI is 07-02; this stub exists so the
# order list template's drill-in link renders and resolves.
@admin_bp.route('/orders/<int:order_id>', methods=['GET'])
def order_detail(order_id):
    order = db.session.get(Order, order_id)
    if order is None:
        flash('Không tìm thấy đơn.', 'error')
        return redirect(url_for('admin.orders'))
    return render_template('admin/orders/detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/delete', methods=['GET', 'POST'])
def delete_order(order_id):
    """Hard-delete an order and its items (ORD-99). GET shows confirm; POST performs delete."""
    order = db.session.get(Order, order_id)
    if order is None:
        flash('Không tìm thấy đơn.', 'error')
        return redirect(url_for('admin.orders'))
    if request.method == 'POST':
        order_id = order.id
        db.session.delete(order)
        db.session.commit()
        flash(f'Đã xóa đơn #{order_id}.', 'success')
        return redirect(url_for('admin.orders'))
    return render_template('admin/orders/delete.html', order=order)


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    order = db.session.get(Order, order_id)
    if order is None:
        flash('Không tìm thấy đơn.', 'error')
        return redirect(url_for('admin.orders'))
    next_status = request.form.get('next_status', '')
    valid = TRANSITION_MAP.get(order.status, set())
    if next_status not in valid:
        flash(f'Không thể chuyển trạng thái đơn #{order.id}.', 'error')
        return redirect(url_for('admin.order_detail', order_id=order.id))
    if next_status == 'Đã xác nhận':
        # Stock decrement (ORD-11): trừ theo OrderItem.quantity, sàn 0, bỏ qua
        # item có product đã bị xóa (product_id NULL qua ON DELETE SET NULL).
        # Idempotent nhờ forward-only TRANSITION_MAP: edge 'Chờ xác nhận' ->
        # 'Đã xác nhận' duy nhất, nên POST lặp sẽ bị reject ở trên (không trừ kép).
        # ponytail: không hoàn lại tồn kho khi hủy đơn sau khi xác nhận — phạm vi
        # yêu cầu chỉ chiều xác nhận → trừ; admin chỉnh quantity thủ công nếu cần.
        for item in order.items.all():
            if item.product is not None:
                item.product.quantity = max(0, item.product.quantity - item.quantity)
    order.status = next_status
    db.session.commit()
    if next_status == 'Đã hủy':
        flash(f'Đã hủy đơn #{order.id}.', 'success')
    else:
        flash(f'Đã chuyển đơn #{order.id} sang trạng thái “{next_status}”.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order.id))


@admin_bp.route('/products', methods=['GET'])
def products():
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.order_by(Product.sort_order.asc(), Product.id.asc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/products/list.html', pagination=pagination, products=pagination.items)


@admin_bp.route('/products/new', methods=['GET', 'POST'])
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        # STT-01: auto-generate a sequential name when the field is left blank.
        # STT = next product number by id order (count + 1). A manually-typed
        # name is always preserved. Zero-padded to 3 digits (Sản phẩm 001...).
        raw_name = (form.name.data or '').strip()
        if not raw_name:
            next_seq = db.session.query(db.func.max(Product.id)).scalar() or 0
            raw_name = 'Sản phẩm {:03d}'.format(next_seq + 1)
        # SKU-01: defer auto-generate until AFTER flush — assigning from
        # max(id)+1 before insert races when two admins submit concurrently
        # (both read the same max, both write the same #N). Using product.id
        # after flush is collision-free: SQLite hands out unique ids per insert.
        raw_sku = (form.sku.data or '').strip()
        sku_was_blank = not raw_sku
        product = Product(
            name=raw_name,
            price=form.price.data,
            cost_price=form.cost_price.data,  # Optional() yields None on empty; 0 VND preserved
            brand=form.brand.data or None,
            measurements=form.measurements.data or None,
            description=form.description.data or None,
            quantity=form.quantity.data or 0,
            discontinued=form.discontinued.data,
            sku=raw_sku or None,
            sort_order=form.sort_order.data or 0,
            admin_note=form.admin_note.data or None,
        )
        db.session.add(product)
        db.session.flush()  # need product.id before attaching images
        if sku_was_blank:
            product.sku = '#{:d}'.format(product.id)
        delete_ids = [int(x) for x in request.form.get('delete_images', '').split(',') if x.strip().lstrip('-').isdigit()]
        new_files = [f for f in request.files.getlist('images') if f and (f.filename or '').strip()]
        err = _process_image_batch(new_files, request.form.get('image_order', ''), delete_ids, product)
        if err:
            db.session.rollback()
            flash(f'Không thể lưu ảnh: {err}. Chưa có ảnh nào được lưu.', 'error')
            return render_template('admin/products/form.html', form=form, product=None, is_new=True, existing_images=[])
        db.session.commit()
        flash('Lưu sản phẩm thành công', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/products/form.html', form=form, product=None, is_new=True, existing_images=[])


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        flash('Không tìm thấy sản phẩm.', 'error')
        return redirect(url_for('admin.products'))
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        form.populate_obj(product)
        if product.sort_order is None:
            product.sort_order = 0  # populate_obj writes None for empty Optional() -> NOT NULL violation; mirror new_product's `or 0`
        delete_ids = [int(x) for x in request.form.get('delete_images', '').split(',') if x.strip().lstrip('-').isdigit()]
        new_files = [f for f in request.files.getlist('images') if f and (f.filename or '').strip()]
        err = _process_image_batch(new_files, request.form.get('image_order', ''), delete_ids, product)
        if err:
            db.session.rollback()
            flash(f'Không thể lưu ảnh: {err}. Chưa có ảnh nào được lưu.', 'error')
            existing_images = product.images.order_by(ProductImage.sort_order.asc()).all()
            return render_template('admin/products/form.html', form=form, product=product, is_new=False, existing_images=existing_images)
        db.session.commit()
        flash(f'Đã cập nhật sản phẩm “{product.name}”', 'success')
        return redirect(url_for('admin.products'))
    existing_images = product.images.order_by(ProductImage.sort_order.asc()).all()
    return render_template('admin/products/form.html', form=form, product=product, is_new=False, existing_images=existing_images)


@admin_bp.route('/products/<int:product_id>/delete', methods=['GET', 'POST'])
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        flash('Không tìm thấy sản phẩm.', 'error')
        return redirect(url_for('admin.products'))
    if request.method == 'POST':
        name = product.name
        images = list(product.images.all())
        image_count = len(images)
        db.session.delete(product)
        db.session.commit()  # D-06: DB row first, then files
        deleted_total = 0
        failed_total = 0
        for img in images:  # D-05: remove files with the product
            d, f = delete_image_files(img.filename)
            deleted_total += d
            failed_total += f
        msg = f'Đã xóa sản phẩm “{name}”'
        if image_count > 0:
            msg += f' và {image_count} ảnh đã xóa'  # D-07
        flash(msg, 'success')
        if failed_total > 0:  # D-09: cleanup failure never blocks the delete
            flash(f'Cảnh báo: sản phẩm đã xóa nhưng không xóa được {failed_total} file ảnh trên đĩa.', 'warning')
        return redirect(url_for('admin.products'))
    return render_template('admin/products/delete.html', product=product)
