import unicodedata
from types import SimpleNamespace

from flask import Blueprint, render_template, request, abort, redirect, url_for

from .db import db
from .models import Product, ProductImage

public_bp = Blueprint('public', __name__)


def normalize_search_text(text):
    """D-11: NFD -> strip combining marks -> casefold. 'áo'->'ao', 'Áo'->'ao'."""
    if not text:
        return ''
    decomposed = unicodedata.normalize('NFD', text)
    stripped = ''.join(ch for ch in decomposed if unicodedata.category(ch) != 'Mn')
    return stripped.casefold()


def _manual_pagination(page, per_page, total):
    pages = max(1, -(-total // per_page))
    page = max(1, min(page, pages))
    return SimpleNamespace(
        page=page, pages=pages, per_page=per_page, total=total,
        has_prev=page > 1, has_next=page < pages,
        prev_num=page - 1 if page > 1 else 1,
        next_num=page + 1 if page < pages else pages,
    )


@public_bp.route('/', methods=['GET'])
def home():
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.order_by(Product.sort_order.asc(), Product.id.asc()).paginate(
        page=page, per_page=12, error_out=False
    )
    if pagination.total and pagination.page > pagination.pages:
        return redirect(url_for('public.home', page=pagination.pages))
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
    nq = normalize_search_text(q)
    page = request.args.get('page', 1, type=int)
    per_page = 12
    if not nq:
        return render_template('public/search.html', q=q, products=None, pagination=None)
    all_products = Product.query.order_by(Product.sort_order.asc(), Product.id.asc()).all()
    matched = [
        p for p in all_products
        if nq in normalize_search_text(p.name or '')
        or nq in normalize_search_text(p.description or '')
    ]
    pagination = _manual_pagination(page, per_page, len(matched))
    start = (pagination.page - 1) * per_page
    pagination.items = matched[start:start + per_page]
    return render_template('public/search.html', q=q, products=pagination.items, pagination=pagination)
