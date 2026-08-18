import unicodedata
from types import SimpleNamespace
from urllib.parse import urlsplit

from flask import Blueprint, render_template, request, abort, redirect, url_for, flash, session, jsonify
from flask_login import current_user

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
    # ponytail: replicate SQLAlchemy's Pagination.iter_pages() so the shared
    # pagination macro works on this hand-rolled object too.
    pages = max(1, -(-total // per_page))
    page = max(1, min(page, pages))

    def iter_pages(left_edge=1, left_current=2, right_current=2, right_edge=1):
        last = 0
        for num in range(1, pages + 1):
            if (num <= left_edge
                    or (page - left_current - 1 < num < page + right_current)
                    or num > pages - right_edge):
                if last + 1 != num:
                    yield None
                yield num
                last = num

    return SimpleNamespace(
        page=page, pages=pages, per_page=per_page, total=total,
        has_prev=page > 1, has_next=page < pages,
        prev_num=page - 1 if page > 1 else None,
        next_num=page + 1 if page < pages else None,
        iter_pages=iter_pages,
    )


@public_bp.route('/', methods=['GET'])
def home():
    # Web internal: chỉ admin đăng nhập mới xem danh sách hàng để nhập đơn.
    # Đơn của khách đến qua Messenger (ngoài web), admin vào đây quản lí/đặt hàng.
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
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


@public_bp.route('/search', methods=['GET', 'POST'])
def search():
    is_ajax = request.form.get('ajax') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    q = (request.args.get('q') or request.form.get('q', '') or '').strip()
    nq = normalize_search_text(q)
    page = request.args.get('page', request.form.get('page', 1), type=int)
    per_page = 12
    if not nq:
        if is_ajax:
            return jsonify(q=q, html='', pagination_html='')
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
        page = pagination.pages
        pagination = _manual_pagination(page, per_page, len(matched))
        start = (pagination.page - 1) * per_page
        pagination.items = matched[start:start + per_page]
    if page < 1:
        page = 1
        pagination = _manual_pagination(page, per_page, len(matched))
        start = (pagination.page - 1) * per_page
        pagination.items = matched[start:start + per_page]
    if is_ajax:
        # Render product cards server-side so client gets ready-to-insert HTML.
        html = render_template('public/_search_results.html', products=pagination.items)
        pagination_html = render_template('public/_pagination.html', pagination=pagination, q=q, endpoint='public.search')
        return jsonify(q=q, html=html, pagination_html=pagination_html)
    return render_template('public/search.html', q=q, products=pagination.items, pagination=pagination)


@public_bp.route('/cart/add/<int:product_id>', methods=['POST'])
def cart_add(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404)

    form = CartForm(formdata=request.form)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if product.status != 'available':
        msg = 'Số lượng không hợp lệ hoặc sản phẩm đã hết hàng.'
        if is_ajax:
            return jsonify({'success': False, 'error': msg, 'product_id': product.id, 'max_reached': False})
        flash(msg, 'error')
        return redirect(request.referrer or url_for('public.home'))

    if not form.validate():
        msg = 'Số lượng không hợp lệ hoặc sản phẩm đã hết hàng.'
        if is_ajax:
            return jsonify({'success': False, 'error': msg, 'product_id': product.id, 'max_reached': False})
        flash(msg, 'error')
        return redirect(request.referrer or url_for('public.home'))

    qty = form.quantity.data
    if not (1 <= qty <= product.quantity):
        msg = 'Số lượng không hợp lệ hoặc sản phẩm đã hết hàng.'
        if is_ajax:
            return jsonify({'success': False, 'error': msg, 'product_id': product.id, 'max_reached': False})
        flash(msg, 'error')
        return redirect(request.referrer or url_for('public.home'))

    cart = session.get('cart', {})
    current_qty = 0
    try:
        current_qty = int(cart.get(str(product_id), 0))
    except (TypeError, ValueError):
        current_qty = 0

    if current_qty + qty > product.quantity:
        msg = 'Số lượng không hợp lệ hoặc sản phẩm đã hết hàng.'
        if is_ajax:
            return jsonify({
                'success': False,
                'error': msg,
                'product_id': product.id,
                'cart_quantity': current_qty,
                'max_quantity': product.quantity,
                'max_reached': current_qty >= product.quantity,
            })
        flash(msg, 'error')
        return redirect(request.referrer or url_for('public.home'))

    cart[str(product_id)] = current_qty + qty
    session['cart'] = cart
    msg = f'Đã thêm {qty} sản phẩm vào giỏ.'
    total_qty = sum(int(v) for v in cart.values() if str(v).isdigit())

    if is_ajax:
        new_qty = cart[str(product_id)]
        return jsonify({
            'success': True,
            'message': msg,
            'cart_count': total_qty,
            'product_id': product.id,
            'cart_quantity': new_qty,
            'max_quantity': product.quantity,
            'max_reached': new_qty >= product.quantity,
        })

    flash(msg, 'success')
    referrer = request.referrer
    if referrer and urlsplit(referrer).hostname == request.host.split(':')[0]:
        return redirect(referrer)
    return redirect(url_for('public.home'))


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
            qty = min(max(int(qty), 0), product.quantity)
            if qty < 1:
                # Tồn kho đã về 0 (hoặc qty âm lẻ) → xóa sản phẩm khỏi giỏ, không để lại qty=0 gây lỗi input.
                if pid_str in cart:
                    del cart[pid_str]
                continue
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
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # GOM-01: trả JSON cho AJAX update — client cập nhật thành tiền mà không reload.
        line_total = product.price * qty
        total = sum(
            db.session.get(Product, int(pid)).price * q
            for pid, q in cart.items()
            if str(pid).isdigit()
            and (p := db.session.get(Product, int(pid))) is not None
            and p.status == 'available'
            and 1 <= q <= p.quantity
        )
        return jsonify(line_total=line_total, total=total)
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

    # BƯỚC 3 — Form validation (tên/SĐT/địa chỉ - tất cả Optional sau khi bỏ required)
    form = CheckoutForm()
    if not form.validate():
        flash('Vui lòng kiểm tra lại thông tin đặt hàng.', 'error')
        return redirect(url_for('public.cart'))

    # BƯỚC 3.5 — Chỉ đặt những sản phẩm được tick (CHECKOUT-01).
    # Nếu không có selected_ids (form cũ / curl / JS off) → fallback đặt tất cả để backward-compat.
    selected_ids_raw = request.form.getlist('selected_ids')
    has_selected_field = 'selected_ids' in request.form
    if has_selected_field:
        # Validate: tất cả phải là số và nằm trong cart.
        valid_ids = {pid for pid in cart.keys() if pid.isdigit()}
        selected_ids = [sid for sid in selected_ids_raw if sid.isdigit() and sid in valid_ids]
        if not selected_ids:
            flash('Vui lòng chọn ít nhất một sản phẩm để đặt hàng.', 'error')
            return redirect(url_for('public.cart'))
        # Lọc cart theo selected_ids cho phần checkout, giữ nguyên session.
        cart_to_checkout = {pid: cart[pid] for pid in selected_ids}
        # Các pid đã đặt (để xóa khỏi session ở bước 6, giữ lại phần không chọn)
        pids_to_remove = list(selected_ids)
    else:
        cart_to_checkout = dict(cart)
        pids_to_remove = list(cart.keys())

    # BƯỚC 4 — Server re-validate từng món (T-06-03): không tin session cart.
    # Mỗi món: product còn tồn tại + available + 1 <= qty <= tồn kho. Sai -> không tạo đơn.
    items_to_save = []
    for pid_str, qty in cart_to_checkout.items():
        if not str(pid_str).isdigit():
            continue  # T-06-02: bỏ key không phải số
        product = db.session.get(Product, int(pid_str))
        if product is None or product.status != 'available' or not (1 <= qty <= product.quantity):
            flash('Một số sản phẩm trong giỏ không còn khả dụng. Vui lòng kiểm tra lại giỏ hàng.', 'error')
            return redirect(url_for('public.cart'))
        items_to_save.append((product, qty))

    # LW-02: giỏ chỉ chứa key không phải số -> không có món nào hợp lệ -> guard (tránh IndexError).
    if not items_to_save:
        flash('Giỏ hàng của bạn đang trống.', 'error')
        return redirect(url_for('public.cart'))

    # BƯỚC 5 — Tạo 1 Order + nhiều OrderItem snapshot trong 1 commit (ORD-10a).
    # Snapshot product_name/price/cost_price tại thời điểm đặt từ product hiện tại.
    order = Order(
        customer_name=(form.customer_name.data or '').strip(),
        customer_phone=_normalize_phone(form.customer_phone.data or ''),
        customer_address=(form.customer_address.data or '').strip(),
        customer_note=(form.customer_note.data or '').strip() or None,  # Optional: data None khi field vắng mặt
        status='Chờ xác nhận',
    )
    db.session.add(order)
    db.session.flush()  # lấy order.id

    # GOM-01: nếu có đơn cùng SĐT đang Chờ xác nhận, gộp item vào đơn đó, lấy thông tin từ đơn này.
    # CHỈ gộp khi SĐT hợp lệ (>= 8 chữ số) — tránh gộp đơn vào nhau khi cả 2 cùng rỗng.
    existing = None
    if order.customer_phone and len(order.customer_phone) >= 8:
        existing = _merge_into_existing_order(order, items_to_save)

    if not existing:
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
        flash('Tạo đơn hàng thành công!', 'success')
    else:
        # Đơn mới bị hủy, item đã gộp vào đơn cũ.
        db.session.delete(order)
        db.session.commit()
        flash('Đơn hàng của bạn đã được gộp vào đơn trước — chúng tôi sẽ gộp gàng giao hàng.', 'success')

    # BƯỚC 6 — Xóa những sản phẩm đã đặt khỏi session cart (CHECKOUT-01).
    # Có selected_ids: chỉ xóa những sản phẩm đã chọn, giữ lại phần còn lại trong giỏ.
    # Backward-compat: xóa tất cả (đặt tất cả như cũ).
    for pid in pids_to_remove:
        cart.pop(pid, None)
    session['cart'] = cart
    return redirect(url_for('public.product_detail', product_id=items_to_save[0][0].id))


@public_bp.route('/api/customer-suggestions', methods=['GET'])
def customer_suggestions():
    """Gợi ý khách cũ: query theo tên HOẶC SĐT (khớp một phần).

    Trả JSON: [{name, phone, address, last_used_at}, ...]
    - Match theo SĐT: normalize bỏ space/dash, contains (vd gõ '0912' → gợi ý SĐT bắt đầu 0912).
    - Match theo tên: case-insensitive contains.
    - Giới hạn 5 kết quả, sắp theo đơn mới nhất.
    - Dedupe theo SĐT (giữ bản ghi mới nhất).
    """
    q = (request.args.get('q') or '').strip()
    if not q:
        return jsonify(suggestions=[])

    qn = normalize_search_text(q)
    qp = _normalize_phone(q)

    # Lấy tất cả đơn có name/phone/address liên quan (không load cả bảng nếu lớn — Phase 2 sẽ filter SQL).
    orders = (db.session.query(Order)
              .order_by(Order.created_at.desc())
              .limit(200)
              .all())

    seen_phones = set()
    suggestions = []
    for order in orders:
        # Match theo tên (case-insensitive)
        name_match = qn in normalize_search_text(order.customer_name or '')
        # Match theo SĐT (normalize)
        phone_match = qp and qp in _normalize_phone(order.customer_phone or '')
        if not (name_match or phone_match):
            continue
        # Dedupe theo SĐT
        norm_phone = _normalize_phone(order.customer_phone or '')
        if not norm_phone:
            # Không có SĐT → dedupe theo name thay thế
            norm_phone = f'name:{normalize_search_text(order.customer_name or "")}'
        if norm_phone in seen_phones:
            continue
        seen_phones.add(norm_phone)
        suggestions.append({
            'name': order.customer_name or '',
            'phone': order.customer_phone or '',
            'address': order.customer_address or '',
            'last_used_at': order.created_at.isoformat() if order.created_at else None,
        })
        if len(suggestions) >= 5:
            break

    return jsonify(suggestions=suggestions)


def _merge_into_existing_order(new_order, items_to_save):
    """GOM-01: Tìm đơn cùng SĐT đang 'Chờ xác nhận', gộp item + cập nhật thông tin khách.

    - Lấy thông tin (tên/SĐT/địa chỉ/ghi chú) từ new_order (đơn sau, mới nhất).
    - Gộp OrderItem: cộng dồn qty nếu cùng product_id, tạo mới nếu khác.
    Returns order nếu gộp thành công, None nếu không tìm thấy đơn nào.
    """
    existing = (db.session.query(Order)
                .filter(Order.id != new_order.id,
                        db.func.replace(db.func.replace(Order.customer_phone, ' ', ''), '-', '') == _normalize_phone(new_order.customer_phone),
                        Order.status == 'Chờ xác nhận')
                .order_by(Order.created_at.desc(), Order.id.desc())
                .first())
    if existing is None:
        return None

    existing.customer_name = new_order.customer_name
    existing.customer_address = new_order.customer_address
    existing.customer_note = new_order.customer_note

    for product, qty in items_to_save:
        item = (db.session.query(OrderItem)
                .filter(OrderItem.order_id == existing.id,
                        OrderItem.product_id == product.id)
                .first())
        if item is None:
            db.session.add(OrderItem(
                order_id=existing.id,
                product_id=product.id,
                product_name=product.name,
                product_price=product.price,
                product_cost_price=product.cost_price,
                quantity=qty,
            ))
        else:
            item.quantity += qty

    db.session.flush()
    return existing


def _normalize_phone(raw):
    """Chuẩn hóa SĐT: bỏ dấu cách/gạch, giữ số và dấu cộng đầu."""
    if not raw:
        return ''
    digits = ''.join(ch for ch in raw if ch.isdigit() or ch == '+')
    if digits.startswith('+'):
        digits = digits[1:]
    return digits
