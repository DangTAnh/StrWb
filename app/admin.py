from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from .db import db
from .forms import ProductForm
from .models import Product

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
@login_required
def _protect_admin():
    """Require login for every admin route."""
    pass


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
        db.session.commit()
        flash('Lưu sản phẩm thành công', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/products/form.html', form=form, product=None, is_new=True)


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        flash('Không tìm thấy sản phẩm.', 'error')
        return redirect(url_for('admin.products'))
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        form.populate_obj(product)
        db.session.commit()
        flash(f'Đã cập nhật sản phẩm “{product.name}”', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/products/form.html', form=form, product=product, is_new=False)


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
