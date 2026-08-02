from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from .db import db
from .forms import ProductForm
from .image_utils import delete_image_files, save_image_file, validate_image_upload
from .models import Product, ProductImage

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
@login_required
def _protect_admin():
    """Require login for every admin route."""
    pass


def _process_image_batch(new_files, order_stream, delete_ids, product):
    """Save new files, delete marked, set sort_order/is_primary from the displayed
    gallery order. Returns error message or None.

    ``order_stream`` is the raw ``image_order`` field value: a comma-separated
    sequence where each token is either an existing image id (int) or a new
    upload reference ``new:<i>`` (index into ``new_files``). form.html's
    ``syncOrder`` serializes the full on-screen gallery this way, so the
    persisted order always matches the order the editor displayed (D-12/D-13) —
    including newly uploaded images interleaved with existing ones.
    """
    # 1. Validate the ENTIRE batch first (D-17): any failure -> return reason, save nothing
    for f in new_files:
        ok, reason = validate_image_upload(f)
        if not ok:
            return f'file “{f.filename}” không hợp lệ ({reason})'
    # 2. Delete marked existing images (D-15) — files + rows
    delete_set = set(delete_ids)
    for img_id in delete_ids:
        img = db.session.get(ProductImage, img_id)
        if img and img.product_id == product.id:
            delete_image_files(img.filename)  # orphan-safe; failure tolerated (D-09)
            db.session.delete(img)
    # 3. Assemble the final gallery from the displayed order stream:
    #    existing images re-sorted by their submitted id, new uploads inserted
    #    at their displayed position (D-12/D-13)
    ordered = []
    placed_new = set()
    placed_existing = set()
    for token in order_stream.split(','):
        token = token.strip()
        if not token:
            continue
        if token.startswith('new:'):
            try:
                idx = int(token[4:])
            except ValueError:
                continue
            if 0 <= idx < len(new_files) and idx not in placed_new:
                placed_new.add(idx)
                fname, original = save_image_file(new_files[idx])
                img = ProductImage(filename=fname, original_filename=original, product_id=product.id)
                db.session.add(img)
                ordered.append(img)
        else:
            try:
                img_id = int(token)
            except ValueError:
                continue
            if img_id in delete_set or img_id in placed_existing:
                continue
            img = db.session.get(ProductImage, img_id)
            if img and img.product_id == product.id:
                placed_existing.add(img_id)
                ordered.append(img)
    # 4. Uploads not referenced in the order stream (e.g. no-JS form fallback) go last
    for idx, f in enumerate(new_files):
        if idx not in placed_new:
            fname, original = save_image_file(f)
            img = ProductImage(filename=fname, original_filename=original, product_id=product.id)
            db.session.add(img)
            ordered.append(img)
    # 5. Assign order + primary (D-12, D-13)
    for idx, img in enumerate(ordered):
        img.sort_order = idx
        img.is_primary = (idx == 0)
    return None


@admin_bp.route('/', methods=['GET'])
def dashboard():
    products_count = Product.query.count()
    return render_template('admin/dashboard.html', products_count=products_count)


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
        product = Product(
            name=form.name.data.strip(),
            price=form.price.data,
            cost_price=form.cost_price.data or None,
            brand=form.brand.data or None,
            measurements=form.measurements.data or None,
            description=form.description.data or None,
            quantity=form.quantity.data or 0,
            discontinued=form.discontinued.data,
            sku=form.sku.data or None,
            sort_order=form.sort_order.data or 0,
            admin_note=form.admin_note.data or None,
        )
        db.session.add(product)
        db.session.flush()  # need product.id before attaching images
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
