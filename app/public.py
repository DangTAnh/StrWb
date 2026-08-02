import unicodedata
from types import SimpleNamespace
from urllib.parse import urlsplit

from flask import Blueprint, render_template, request, abort, redirect, url_for, flash, session

from .db import db
from .forms import CartForm, CheckoutForm
from .models import Product, ProductImage, Order, OrderItem

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
        prev_num=page - 1 if page > 1 else None,
        next_num=page + 1 if page < pages else None,
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
    referrer = request.referrer
    back_url = (
        referrer
        if referrer and urlsplit(referrer).hostname == request.host.split(':')[0]
        else None
    )
    return render_template(
        'public/product_detail.html', product=product, images=images, back_url=back_url
    )


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
    # D-07 #2: mirror home() — out-of-range page -> 302 to last valid page (no silent clamp).
    # _manual_pagination clamps page, so compare the raw request page, not the clamped value.
    if pagination.total and page > pagination.pages:
        return redirect(url_for('public.search', q=q, page=pagination.pages))
    if page < 1:
        return redirect(url_for('public.search', q=q, page=1))
    return render_template('public/search.html', q=q, products=pagination.items, pagination=pagination)


@public_bp.route('/cart/add/<int:product_id>', methods=['POST'])
def cart_add(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404)
    form = CartForm()
    if product.status != 'available':
        flash('Số lượng không hợp lệ hoặc sản phẩm đã hết hàng.', 'error')
        return redirect(url_for('public.product_detail', product_id=product.id))
    if not form.validate():
        flash('Số lượng không hợp lệ hoặc sản phẩm đã hết hàng.', 'error')
        return redirect(url_for('public.product_detail', product_id=product.id))
    qty = form.quantity.data
    if not (1 <= qty <= product.quantity):
        flash('Số lượng không hợp lệ hoặc sản phẩm đã hết hàng.', 'error')
        return redirect(url_for('public.product_detail', product_id=product.id))
    cart = session.get('cart', {})
    cart[str(product_id)] = qty
    session['cart'] = cart
    flash(f'Đã thêm {qty} sản phẩm vào giỏ.', 'success')
    return redirect(url_for('public.cart'))


@public_bp.route('/cart', methods=['GET'])
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0
    for pid_str, qty in list(cart.items()):
        if not pid_str.isdigit():
            continue  # T-06-02: bỏ key không phải số
        product = db.session.get(Product, int(pid_str))
        if product is None:
            # T-06-02: sản phẩm đã bị xóa -> xóa khỏi giỏ, KHÔNG flash (tránh lộ thông tin id)
            cart.pop(pid_str, None)
        elif product.status != 'available':
            flash(f"Sản phẩm '{product.name}' đã ngừng bán hoặc hết hàng và được xóa khỏi giỏ.", 'info')
            cart.pop(pid_str, None)
        else:
            # MD-02: clamp qty xuống tồn kho hiện tại (stock giảm sau khi add).
            # Persist qty đã clamp để session khớp với đơn đặt được — tránh tổng tiền
            # hiển thị mà checkout sẽ reject.
            qty = min(int(qty), product.quantity)
            cart[pid_str] = qty
            items.append(SimpleNamespace(product=product, quantity=qty))
            total += product.price * qty
    session['cart'] = cart
    return render_template('public/cart.html', items=items, total=total)


@public_bp.route('/cart/update/<int:product_id>', methods=['POST'])
def cart_update(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404)
    form = CartForm()
    if not form.validate():
        flash('Số lượng vượt quá tồn kho.', 'error')
        return redirect(url_for('public.cart'))
    qty = form.quantity.data
    if product.status != 'available' or not (1 <= qty <= product.quantity):
        flash('Số lượng vượt quá tồn kho.', 'error')
        return redirect(url_for('public.cart'))
    cart = session.get('cart', {})
    if str(product_id) not in cart:
        # MD-01: route "update" không upsert — sản phẩm chưa có trong giỏ thì không thêm.
        flash('Sản phẩm không có trong giỏ hàng.', 'error')
        return redirect(url_for('public.cart'))
    cart[str(product_id)] = qty
    session['cart'] = cart
    flash('Giỏ hàng đã cập nhật.', 'success')
    return redirect(url_for('public.cart'))


@public_bp.route('/cart/remove/<int:product_id>', methods=['POST'])
def cart_remove(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    flash('Đã xóa sản phẩm khỏi giỏ.', 'success')
    return redirect(url_for('public.cart'))


@public_bp.route('/cart/checkout', methods=['POST'])
def checkout():
    # BƯỚC 1 — Honeypot silent reject (T-06-01): field 'website' điền -> bot trap.
    # Không flash, không ghi DB, không đụng session cart.
    if request.form.get('website'):
        return redirect(url_for('public.cart'))

    # BƯỚC 2 — Empty cart guard
    cart = session.get('cart', {})
    if not cart:
        flash('Giỏ hàng của bạn đang trống.', 'error')
        return redirect(url_for('public.cart'))

    # BƯỚC 3 — Form validation (tên/SĐT/địa chỉ bắt buộc, SĐT 8-11 chữ số)
    form = CheckoutForm()
    if not form.validate():
        flash('Vui lòng nhập đầy đủ Họ và tên, Số điện thoại, và Địa chỉ.', 'error')
        return redirect(url_for('public.cart'))

    # BƯỚC 4 — Server re-validate từng món (T-06-03): không tin session cart.
    # Mỗi món: product còn tồn tại + available + 1 <= qty <= tồn kho. Sai -> không tạo đơn.
    items_to_save = []
    for pid_str, qty in cart.items():
        if not str(pid_str).isdigit():
            continue  # T-06-02: bỏ key không phải số
        product = db.session.get(Product, int(pid_str))
        if product is None or product.status != 'available' or not (1 <= qty <= product.quantity):
            flash('Một số sản phẩm trong giỏ không còn khả dụng. Vui lòng kiểm tra lại giỏ hàng.', 'error')
            return redirect(url_for('public.cart'))
        items_to_save.append((product, qty))

    # BƯỚC 5 — Tạo 1 Order + nhiều OrderItem snapshot trong 1 commit (ORD-10a).
    # Snapshot product_name/price/cost_price tại thời điểm đặt từ product hiện tại.
    order = Order(
        customer_name=form.customer_name.data.strip(),
        customer_phone=form.customer_phone.data.strip(),
        customer_address=form.customer_address.data.strip(),
        customer_note=(form.customer_note.data or '').strip() or None,  # Optional: data None khi field vắng mặt
        status='Chờ xác nhận',
    )
    db.session.add(order)
    db.session.flush()  # lấy order.id
    for product, qty in items_to_save:
        db.session.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_price=product.price,
            product_cost_price=product.cost_price,
            quantity=qty,
        ))
    db.session.commit()

    # BƯỚC 6 — Xóa giỏ + success + redirect về trang chi tiết sản phẩm đầu tiên.
    # KHÔNG giảm product.quantity (ORD-12 deferred v2).
    session['cart'] = {}
    flash('Đặt hàng thành công! Chúng tôi sẽ liên hệ xác nhận qua SĐT.', 'success')
    return redirect(url_for('public.product_detail', product_id=items_to_save[0][0].id))
