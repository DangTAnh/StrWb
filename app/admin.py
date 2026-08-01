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


def _process_image_batch(new_files, image_order, delete_ids, product):
    """Save new files, delete marked, set sort_order/is_primary. Returns error message or None."""
    # 1. Validate the ENTIRE batch first (D-17): any failure -> return reason, save nothing
    for f in new_files:
        ok, reason = validate_image_upload(f)
        if not ok:
            return f'file “{f.filename}” không hợp lệ ({reason})'
    # 2. Delete marked existing images (D-15) — files + rows
    for img_id in delete_ids:
        img = db.session.get(ProductImage, img_id)
        if img and img.product_id == product.id:
            delete_image_files(img.filename)  # orphan-safe; failure tolerated (D-09)
            db.session.delete(img)
    # 3. Save new files (IMG-01/02/04), append to the ordered list
    ordered = []
    for img_id in image_order:  # existing kept, in displayed order
        img = db.session.get(ProductImage, img_id)
        if img and img.product_id == product.id:
            ordered.append(img)
    for f in new_files:
        fname, original = save_image_file(f)
        img = ProductImage(filename=fname, original_filename=original, product_id=product.id)
        db.session.add(img)
        ordered.append(img)
    # 4. Assign order + primary (D-12, D-13)
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
        image_order = [int(x) for x in request.form.get('image_order', '').split(',') if x.strip().lstrip('-').isdigit()]
        delete_ids = [int(x) for x in request.form.get('delete_images', '').split(',') if x.strip().lstrip('-').isdigit()]
        new_files = [f for f in request.files.getlist('images') if f and (f.filename or '').strip()]
        err = _process_image_batch(new_files, image_order, delete_ids, product)
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
        image_order = [int(x) for x in request.form.get('image_order', '').split(',') if x.strip().lstrip('-').isdigit()]
        delete_ids = [int(x) for x in request.form.get('delete_images', '').split(',') if x.strip().lstrip('-').isdigit()]
        new_files = [f for f in request.files.getlist('images') if f and (f.filename or '').strip()]
        err = _process_image_batch(new_files, image_order, delete_ids, product)
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
        image_count = product.images.count()
        db.session.delete(product)
        db.session.commit()
        flash(f'Đã xóa sản phẩm “{name}”', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/products/delete.html', product=product)
