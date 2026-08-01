from flask import Blueprint, render_template, request, abort

from .db import db
from .models import Product, ProductImage

public_bp = Blueprint('public', __name__)


@public_bp.route('/', methods=['GET'])
def home():
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.order_by(Product.sort_order.asc(), Product.id.asc()).paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template('public/index.html', pagination=pagination, products=pagination.items)


@public_bp.route('/products/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404)
    images = product.images.order_by(ProductImage.sort_order.asc()).all()
    return render_template('public/product_detail.html', product=product, images=images)


@public_bp.route('/search', methods=['GET'])
def search():
    q = (request.args.get('q') or '').strip()
    return render_template('public/search.html', q=q, products=None, pagination=None)
