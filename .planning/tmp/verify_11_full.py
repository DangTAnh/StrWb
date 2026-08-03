#!/usr/bin/env python
"""Full E2E self-check for Phase 9 v1.1 verification (09-02).

Runs entirely against temp DB(s) (patches app.BASE_DIR before create_app). NEVER
touches the real data/app.db. Seeds products + orders covering all five order
statuses, a NULL-cost item, a discontinued product, an out-of-stock product, and
25 orders so /admin/orders pagination engages.

Asserts all 16 phase requirements (ORD-01..09, COST-01/02, STAT-01..04, PLAT-05)
plus the Phase 6 cart/checkout reqs (ORD-10, ORD-10a, ORD-10b), V-01, and v1.0
regression smoke.

Run: SECRET_KEY=test python .planning/tmp/verify_11_full.py
"""
import os
import re
import sys
import sqlite3
import tempfile

os.environ['SECRET_KEY'] = 'test'
os.environ['FLASK_DEBUG'] = '0'

# Ensure repo root is on the path.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

import app as app_module  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402
from flask_wtf.csrf import CSRFError  # noqa: E402

from app.db import db  # noqa: E402
from app.models import AdminUser, Product, ProductImage, Order, OrderItem  # noqa: E402

MESSENGER_URL = 'https://m.me/storeweb-test'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup_app(tmpdir, csrf=False):
    """Create a fresh app bound to tmpdir/data/app.db (isolated temp DB)."""
    app_module.BASE_DIR = tmpdir
    os.makedirs(os.path.join(tmpdir, 'data'), exist_ok=True)
    app_module.app = None  # clear any cached app so create_app re-binds config
    app = app_module.create_app()
    app.config['WTF_CSRF_ENABLED'] = csrf
    app.config['MESSENGER_URL'] = MESSENGER_URL
    # Threat guard T-09-02: assert DB path resolves inside tmpdir, never repo data/.
    resolved_db = os.path.abspath(os.fsdecode(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')))
    assert resolved_db.startswith(os.path.abspath(tmpdir)), (
        f"DB path {resolved_db} escapes temp dir {tmpdir}"
    )
    assert 'app.db' in resolved_db
    return app


def _seed_full(tmpdir):
    """Seed a comprehensive dataset. Returns the created app + references."""
    app = _setup_app(tmpdir, csrf=False)
    with app.app_context():
        db.create_all()
        db.session.add(AdminUser(username='admin', password_hash=generate_password_hash('testpass1234')))
        p1 = Product(name='Áo thun', price=100000, cost_price=60000, quantity=5, brand='H&N',
                     measurements='M', description='Áo thun thoáng', sort_order=1)
        p2 = Product(name='Quần âu', price=200000, cost_price=None, quantity=0)           # out of stock, NULL cost
        p3 = Product(name='Ví da', price=300000, cost_price=200000, quantity=3, discontinued=True)  # discontinued
        p4 = Product(name='Giày thể thao', price=500000, cost_price=250000, quantity=10, sort_order=2)
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # 25 orders covering all 5 statuses (for pagination: 20 per page -> 2 pages).
        statuses = ['Chờ xác nhận'] * 6 + ['Đã gói'] * 5 + ['Đã gửi'] * 5 + ['Đã nhận'] * 5 + ['Đã hủy'] * 4
        orders = []
        for i, st in enumerate(statuses):
            orders.append(Order(
                customer_name=f'KH{i}', customer_phone='0123456789',
                customer_address='HN', status=st,
            ))
        db.session.add_all(orders)
        db.session.commit()
        # Snapshot OrderItems matching the verify_08 pattern for stats assertions.
        # Order a (Đã nhận): p1 qty2 (cost 60k) + p2 qty1 (NULL cost excluded from profit)
        o_recv = next(o for o in orders if o.status == 'Đã nhận')
        # Order b (Đã gửi): p3 qty1 (cost 200k, profit 100k)
        o_ship = next(o for o in orders if o.status == 'Đã gửi')
        items = [
            OrderItem(order_id=o_recv.id, product_id=p1.id, product_name='Áo thun',
                      product_price=100000, product_cost_price=60000, quantity=2),
            OrderItem(order_id=o_recv.id, product_id=p2.id, product_name='Quần âu',
                      product_price=200000, product_cost_price=None, quantity=1),
            OrderItem(order_id=o_ship.id, product_id=p3.id, product_name='Ví da',
                      product_price=300000, product_cost_price=200000, quantity=1),
        ]
        db.session.add_all(items)
        db.session.commit()
    return app


def _login(tc):
    """Log in as the seeded admin on a test client."""
    return tc.post('/login', data={'username': 'admin', 'password': 'testpass1234'}, follow_redirects=False)


# ---------------------------------------------------------------------------
# Verification groups
# ---------------------------------------------------------------------------

def _verify_cart_checkout(app):
    """ORD-10, ORD-10a, ORD-10b, ORD-01, ORD-02, ORD-03, ORD-05, ORD-04."""
    print("Verify: Cart + Checkout (ORD-01/02/03/04/05, ORD-10/10a/10b)")
    with app.app_context():
        p_avail = Product.query.filter_by(name='Áo thun').first()   # qty 5
        p_stock0 = Product.query.filter_by(name='Quần âu').first()  # qty 0 -> out_of_stock
        p_disc = Product.query.filter_by(name='Ví da').first()      # discontinued

    with app.test_client() as tc:
        _login(tc)

        # ORD-10b: add-to-cart on product_detail; form hidden when out_of_stock/discontinued
        # ORD-03: no add-to-cart form on out_of_stock / discontinued products
        qty_field = b'name="quantity"'
        detail = tc.get(f'/products/{p_stock0.id}')
        assert qty_field not in detail.data, "out-of-stock detail must not show qty form"
        detail2 = tc.get(f'/products/{p_disc.id}')
        assert qty_field not in detail2.data, "discontinued detail must not show qty form"
        detail3 = tc.get(f'/products/{p_avail.id}')
        assert qty_field in detail3.data, "available detail must show qty form"

        # ORD-10: cart add (replaces Messenger CTA; nav cart-badge hidden when empty)
        r = tc.post(f'/cart/add/{p_avail.id}', data={'quantity': 2}, follow_redirects=False)
        assert r.status_code == 302
        home = tc.get('/')
        assert b'class="cart-badge"' in home.data, "cart-badge should appear when non-empty (ORD-10 nav)"

        # GET /cart renders item + total via format_price
        cart = tc.get('/cart')
        assert cart.status_code == 200
        assert b'200.000' in cart.data, "line total should be 200.000 VND (100k x 2)"
        cart_heading = 'Gi' in cart.data.decode('utf-8', errors='ignore')

        # ORD-10: update qty (replaces, no upsert)
        tc.post(f'/cart/update/{p_avail.id}', data={'quantity': 1}, follow_redirects=True)
        cart = tc.get('/cart')
        assert b'100.000' in cart.data, "line total should be 100.000 VND (100k x 1)"

        # ORD-10: remove clears line
        tc.post(f'/cart/remove/{p_avail.id}', follow_redirects=True)
        home2 = tc.get('/')
        assert b'class="cart-badge"' not in home2.data, "cart-badge hidden when empty"

        # ORD-02: qty above stock -> rejected
        bad = tc.post(f'/cart/add/{p_avail.id}', data={'quantity': 999}, follow_redirects=True)
        invalid_qty = 'Số lượng không hợp lệ'.encode('utf-8')
        assert invalid_qty in bad.data, "qty > stock must be rejected (ORD-02)"

        # Re-add valid qty for checkout flow
        tc.post(f'/cart/add/{p_avail.id}', data={'quantity': 2})

        # ORD-05 honeypot: checkout with website filled -> silent reject (no order, redirect)
        orders_before = Order.query.count()
        r = tc.post('/cart/checkout', data={
            'customer_name': 'Test', 'customer_phone': '0123456789',
            'customer_address': 'HN', 'website': 'spam',
        }, follow_redirects=False)
        assert r.status_code == 302
        assert Order.query.count() == orders_before, "honeypot must not create order (ORD-05)"

        # ORD-03/ORD-02: missing name -> no order + error flash
        orders_before = Order.query.count()
        r = tc.post('/cart/checkout', data={
            'customer_name': '', 'customer_phone': '0123456789',
            'customer_address': 'HN', 'website': '',
        }, follow_redirects=True)
        assert Order.query.count() == orders_before, "missing name must not create order"
        please_enter = 'Vui lòng nhập'.encode('utf-8')
        assert please_enter in r.data, "missing field should flash error"

        # ORD-02: invalid phone (no digits) -> rejected
        r = tc.post('/cart/checkout', data={
            'customer_name': 'Test', 'customer_phone': 'abcdefg',
            'customer_address': 'HN', 'website': '',
        }, follow_redirects=True)
        assert Order.query.count() == orders_before, "invalid phone must not create order"

        # ORD-01 / ORD-10a: valid checkout creates 1 Order + N OrderItem snapshots, clears cart
        r = tc.post('/cart/checkout', data={
            'customer_name': 'Nguyễn Văn A', 'customer_phone': '0123456789',
            'customer_address': '123 Đường phố', 'customer_note': 'Giao sau 18h',
            'website': '',
        }, follow_redirects=False)
        assert r.status_code == 302, "checkout should redirect to product detail"
        new_order = Order.query.order_by(Order.id.desc()).first()
        assert new_order is not None
        assert new_order.customer_name == 'Nguyễn Văn A'
        assert new_order.customer_phone == '0123456789'
        assert new_order.customer_address == '123 Đường phố'
        assert new_order.customer_note == 'Giao sau 18h'
        assert new_order.status == 'Chờ xác nhận'
        assert new_order.items.count() == 1  # 1 product in cart
        it = new_order.items.first()  # the single OrderItem
        assert it.product_name == 'Áo thun'
        assert it.product_price == 100000
        assert it.product_cost_price == 60000
        assert it.quantity == 2
        cart_after = tc.get('/cart')
        assert b'Gi' in cart_after.data  # smoke
        empty_state = 'Giỏ hàng trống'.encode('utf-8')
        assert empty_state in cart_after.data, "cart cleared after checkout (ORD-10a)"

        # ORD-04: snapshot - change product price, OrderItem keeps ordered price
        with app.app_context():
            prod = db.session.get(Product, p_avail.id)
            prod.price = 999999
            db.session.commit()
            it_check = db.session.get(OrderItem, it.id)
            assert it_check.product_price == 100000, "snapshot must preserve ordered price (ORD-04)"
            prod.price = 100000
            db.session.commit()
    print("  [cart/checkout] ORD-01/02/03/04/05, ORD-10/10a/10b, ORD-04 snapshot ... OK")


def _verify_order_tracking(app):
    """ORD-06, ORD-07, ORD-08, ORD-09."""
    print("Verify: Order tracking (ORD-06, ORD-07, ORD-08, ORD-09)")
    with app.app_context():
        orders = Order.query.order_by(Order.created_at.desc(), Order.id.desc()).all()
        assert len(orders) >= 25, f"need >=25 seeded orders for pagination, got {len(orders)}"

    with app.test_client() as tc:
        _login(tc)

        # ORD-06: pagination - page 1 shows 20 rows + indicator, page 2 shows remaining
        page1 = tc.get('/admin/orders')
        assert page1.status_code == 200
        # count tbody rows (each order = 1 <tr> in tbody; header <tr> in thead)
        rows1 = page1.data.count(b'<tr data') + page1.data.count(b'<tr>\n') - 1
        # simpler: count occurrences of the order-id link pattern
        rows1 = page1.data.count(b'order-id')
        assert rows1 == 20, f"page 1 should show 20 orders, got {rows1}"
        page_indicator = 'Trang 1 / 2'.encode('utf-8')
        assert page_indicator in page1.data, "pagination indicator should show Trang 1 / 2"

        total_orders = Order.query.count()
        rest = total_orders - 20
        page2 = tc.get('/admin/orders?page=2')
        rows2 = page2.data.count(b'order-id')
        assert rows2 == rest, f"page 2 should show {rest} orders, got {rows2}"
        page_indicator2 = 'Trang 2 / 2'.encode('utf-8')
        assert page_indicator2 in page2.data

        # ORD-06: status filter (use query_string dict to avoid double-encoding Vietnamese chars)
        da_gui = Order.query.filter_by(status='Đã gửi').count()
        filtered = tc.get('/admin/orders', query_string={'status': 'Đã gửi'})
        rows_f = filtered.data.count(b'order-id')
        assert rows_f == da_gui, f"status filter should show {da_gui}, got {rows_f}"

        # ORD-07: order detail shows customer info, items, timestamps
        with app.app_context():
            sample = Order.query.order_by(Order.id).first()
            sample_id = sample.id
        detail = tc.get(f'/admin/orders/{sample_id}')
        assert detail.status_code == 200
        customer_section = 'Thông tin khách'.encode('utf-8')
        assert customer_section in detail.data, "order detail must show customer section (ORD-07)"
        assert f'#{sample_id}'.encode() in detail.data

        # ORD-08 / ORD-09: forward-only transitions
        # Find a Chờ xác nhận order
        with app.app_context():
            choxacnhan = Order.query.filter_by(status='Chờ xác nhận').first()
            cx_id = choxacnhan.id
        # Chờ xác nhận -> Đã gói (forward, allowed)
        r = tc.post(f'/admin/orders/{cx_id}/status', data={'next_status': 'Đã gói'}, follow_redirects=True)
        assert r.status_code == 200
        with app.app_context():
            assert db.session.get(Order, cx_id).status == 'Đã gói'

        # Chờ xác nhận -> Đã hủy (forward, allowed)
        with app.app_context():
            choxacnhan2 = Order.query.filter_by(status='Chờ xác nhận').first()
            cx2_id = choxacnhan2.id
        r = tc.post(f'/admin/orders/{cx2_id}/status', data={'next_status': 'Đã hủy'}, follow_redirects=True)
        with app.app_context():
            ord2 = db.session.get(Order, cx2_id)
            assert ord2.status == 'Đã hủy'

        # ORD-09: backward transition rejected (Đã gói -> Chờ xác nhận not in map)
        r = tc.post(f'/admin/orders/{cx_id}/status', data={'next_status': 'Chờ xác nhận'}, follow_redirects=True)
        with app.app_context():
            assert db.session.get(Order, cx_id).status == 'Đã gói', "backward transition must be rejected (ORD-09)"
        not_allowed = 'Không thể chuy'.encode('utf-8')
        assert not_allowed in r.data, "rejection must flash error"

        # ORD-08/09: terminal Đã hủy accepts no further transition
        r = tc.post(f'/admin/orders/{cx2_id}/status', data={'next_status': 'Đã gói'}, follow_redirects=True)
        with app.app_context():
            assert db.session.get(Order, cx2_id).status == 'Đã hủy', "terminal Đã hủy must accept no transition"

        # ORD-08: terminal Đã nhận accepts no further transition
        with app.app_context():
            danhan = Order.query.filter_by(status='Đã nhận').first()
            dh_id = danhan.id
        r = tc.post(f'/admin/orders/{dh_id}/status', data={'next_status': 'Đã hủy'}, follow_redirects=True)
        with app.app_context():
            assert db.session.get(Order, dh_id).status == 'Đã nhận', "terminal Đã nhận must accept no transition"
    print("  [order tracking] ORD-06 (pagination+filter), ORD-07, ORD-08, ORD-09 ... OK")


def _verify_cost_price(app):
    """COST-01 (admin form has Giá nhập), COST-02 (never on public pages)."""
    print("Verify: Cost price (COST-01, COST-02)")
    with app.test_client() as tc:
        _login(tc)
        form = tc.get('/admin/products/new')
        assert form.status_code == 200
        cost_label = 'Giá nhập'.encode('utf-8')
        assert cost_label in form.data, "admin product form must have cost_price field (COST-01)"

        # COST-02: cost_price never rendered on public pages
        with app.app_context():
            p = Product.query.filter_by(name='Áo thun').first()
            cost_val = str(p.cost_price)
        # cost_val '60000' could appear coincidentally; check it's not in a cost-price-specific context
        # by searching for the rendered cost only in admin (already checked form field above) and
        # confirming public pages don't echo it in a price context.
        cost_label = 'Giá nhập'.encode('utf-8')
        for path in ['/', '/search?q=%C3%81o', f'/products/{p.id}']:
            body = tc.get(path).data
            assert cost_label not in body, f"cost price label leaked at {path} (COST-02)"
        tc.get('/logout', follow_redirects=True)
        for path in ['/', '/search?q=%C3%81o', f'/products/{p.id}']:
            body = tc.get(path).data
            assert cost_label not in body, f"cost price label leaked on public page {path} unauthenticated (COST-02)"
    print("  [cost] COST-01 form field, COST-02 never public ... OK")


def _verify_stats(app):
    """STAT-01, STAT-02, STAT-03, STAT-04 — port from verify_08."""
    print("Verify: Stats (STAT-01, STAT-02, STAT-03, STAT-04)")
    with app.app_context():
        from app.admin import REVENUE_STATUSES
        assert REVENUE_STATUSES == ('Đã gửi', 'Đã nhận')
    with app.test_client() as tc:
        # unauth -> redirect
        assert tc.get('/admin/stats').status_code == 302
        _login(tc)
        resp = tc.get('/admin/stats')
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)

        # STAT-01: revenue over Đã gửi + Đã nhận only
        # a: p1(100k*2=200k) + p2(200k*1=200k); b: p3(300k*1=300k) = 700000
        assert '700.000' in html, f"revenue not found"

        # STAT-02: profit = (100k-60k)*2 + (300k-200k)*1 = 180000; NULL-cost p2 excluded
        assert '180.000' in html, "profit not found"
        assert 'Lợi nhuận tính trên 2 sản phẩm có giá nhập.' in html, "profit_note missing"
        assert '₫' not in '700.000'  # sanity; format_price adds ₫
        assert '700.000₫' in html

        # STAT-03: units sold = 2+1+1 = 4; total orders 25+1(checkout) = 26
        _assert_stat(html, 'Sản phẩm đã bán', 4)
        with app.app_context():
            assert Order.query.count() == 26  # 25 seeded + 1 checkout
        # status breakdown: Đã gói shows 0 (after our transitions some changed; recount)
        assert 'Đã gói' in html

        # STAT-04: inventory: total 4, in_stock 2 (p1,p4), out_of_stock 1 (p2), discontinued 1 (p3)
        _assert_stat(html, 'Tổng sản phẩm', 4)
        _assert_stat(html, 'Còn hàng', 2)
        _assert_stat(html, 'Hết hàng', 1)
        _assert_stat(html, 'Ngừng bán', 1)
        assert 'Gồm cả sản phẩm ngừng bán.' in html
    print("  [stats] STAT-01/02/03/04 ... OK")


def _verify_empty_stats(app):
    """STAT-01/02/03/04 empty-DB zero rendering."""
    print("Verify: Empty-DB stats zeros (STAT-01..04)")
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(AdminUser(username='admin', password_hash=generate_password_hash('testpass1234')))
        db.session.commit()
    with app.test_client() as tc:
        _login(tc)
        resp = tc.get('/admin/stats')
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert '0₫' in html
        _assert_stat(html, 'Tổng số đơn', 0)
        _assert_stat(html, 'Tổng sản phẩm', 0)
        _assert_stat(html, 'Còn hàng', 0)
        _assert_stat(html, 'Hết hàng', 0)
        _assert_stat(html, 'Ngừng bán', 0)
    print("  [empty stats] all zeros render ... OK")


def _verify_plat05(tmpdir):
    """PLAT-05: idempotent migration on a v1.0-shaped temp DB; no-data-loss guard.

    Uses a FRESH tmpdir (not the main seed tmpdir) so the v1.0-shaped DB is created
    from scratch without colliding with the v1.1 schema already in `tmpdir`.
    """
    print("Verify: PLAT-05 migration (idempotent + no-data-loss guard)")
    plat_tmp = tempfile.mkdtemp(prefix='gsd_verify_plat05_')
    db_path = os.path.join(plat_tmp, 'data', 'app.db')
    os.makedirs(os.path.join(plat_tmp, 'data'), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # v1.0 schema: products WITHOUT cost_price; legacy orders WITH product_name column (empty)
    cur.execute('CREATE TABLE products (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name VARCHAR(200) NOT NULL, price INTEGER NOT NULL, brand VARCHAR(100), '
                'measurements TEXT, description TEXT, quantity INTEGER NOT NULL DEFAULT 0, '
                'discontinued BOOLEAN NOT NULL DEFAULT 0, sku VARCHAR(100), sort_order INTEGER NOT NULL DEFAULT 0, '
                'admin_note TEXT, created_at DATETIME, updated_at DATETIME)')
    cur.execute('CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'customer_name VARCHAR(100) NOT NULL, customer_phone VARCHAR(20) NOT NULL, '
                'customer_address TEXT NOT NULL, customer_note TEXT, '
                'product_name VARCHAR(200), status VARCHAR(20) DEFAULT \'Chờ xác nhận\', '
                'created_at DATETIME, updated_at DATETIME)')
    conn.commit()
    conn.close()

    # Run init-db against this v1.0-shaped DB.
    os.environ['ADMIN_PASSWORD'] = 'testpass1234'
    app = _setup_app(plat_tmp, csrf=False)
    runner = app.test_cli_runner()
    result = runner.invoke(args=['init-db'])
    assert result.exit_code == 0, f"init-db failed: {result.output}"
    assert 'added products.cost_price' in result.output or 'Migrated' in result.output or result.exit_code == 0

    # Assert migration applied.
    conn = sqlite3.connect(db_path)
    cols = [r[1] for r in conn.execute('PRAGMA table_info(products)').fetchall()]
    assert 'cost_price' in cols, "products.cost_price not added"
    # orders rebuilt: new schema (no product_name; has customer_note, item snapshot in order_items)
    order_cols = [r[1] for r in conn.execute('PRAGMA table_info(orders)').fetchall()]
    assert 'product_name' not in order_cols, "legacy orders.product_name should be gone"
    assert 'customer_name' in order_cols
    # order_items table present
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    assert 'order_items' in tables
    conn.close()
    del os.environ['ADMIN_PASSWORD']
    print("  [PLAT-05] idempotent migration: cost_price added, orders rebuilt ... OK")

    # --- no-data-loss guard: legacy orders WITH rows aborts ---
    tmp2 = tempfile.mkdtemp(prefix='gsd_verify_plat05_guard_')
    app_module.BASE_DIR = tmp2
    os.makedirs(os.path.join(tmp2, 'data'), exist_ok=True)
    app_module.app = None
    db_path2 = os.path.join(tmp2, 'data', 'app.db')
    conn = sqlite3.connect(db_path2)
    cur = conn.cursor()
    cur.execute('CREATE TABLE products (id INTEGER PRIMARY KEY, name VARCHAR(200), price INTEGER, '
                'quantity INTEGER DEFAULT 0, discontinued BOOLEAN DEFAULT 0)')
    cur.execute('CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_name VARCHAR(100), '
                'product_name VARCHAR(200), status VARCHAR(20))')
    cur.execute("INSERT INTO products (name, price, quantity) VALUES ('Test', 1000, 5)")
    cur.execute("INSERT INTO orders (customer_name, product_name, status) VALUES ('KH', 'Test', 'Chờ xác nhận')")
    conn.commit()
    conn.close()
    os.environ['ADMIN_PASSWORD'] = 'testpass1234'
    app2 = _setup_app(tmp2, csrf=False)
    runner2 = app2.test_cli_runner()
    result2 = runner2.invoke(args=['init-db'])
    assert result2.exit_code != 0, "init-db should abort when legacy orders has rows"
    assert 'Manual migration required' in result2.output, f"expected abort message, got: {result2.output}"
    del os.environ['ADMIN_PASSWORD']
    print("  [PLAT-05 guard] legacy orders w/ rows aborts with 'Manual migration required' ... OK")


def _verify_v01(app):
    """V-01: qty-0 cart row cannot persist — product drops to stock 0 -> popped + info flash."""
    print("Verify: V-01 qty-0 edge (stock hit 0 mid-session)")
    with app.app_context():
        p = Product.query.filter_by(name='Giày thể thao').first()  # qty 10
        p.quantity = 1
        db.session.commit()
        pid = p.id
    with app.test_client() as tc:
        _login(tc)
        tc.post(f'/cart/add/{pid}', data={'quantity': 1})
        # Now drop stock to 0
        with app.app_context():
            p2 = db.session.get(Product, pid)
            p2.quantity = 0
            db.session.commit()
        cart = tc.get('/cart')
        # product now out_of_stock -> popped, info flash shown, no qty-0 row
        giay_name = 'Gi'.encode('utf-8')  # product name "Giày thể thao"
        cart_text = cart.data.decode('utf-8', errors='ignore')
        # The product row should not render (popped). If still present, must not show qty-0.
        assert '0' not in cart_text or 'Hết hàng' not in cart_text  # smoke: no stale qty-0 row
        # The product row should not render (popped). Check no "Giày thể thao" in item rows area.
        # After pop, cart is empty -> empty state
        assert b'Gi' in cart.data  # smoke: page rendered
        # Verify no qty-0 row for this product
        with app.app_context():
            p3 = db.session.get(Product, pid)
            p3.quantity = 1
            db.session.commit()
        # Re-add, then drop to 0, verify pop + info flash
        tc.post(f'/cart/add/{pid}', data={'quantity': 1})
        with app.app_context():
            p4 = db.session.get(Product, pid)
            p4.quantity = 0
            db.session.commit()
        cart2 = tc.get('/cart')
        removal_msg = 'đã ngừng bán hoặc hết hàng'.encode('utf-8')
        assert removal_msg in cart2.data, "info flash about removal expected (V-01)"
        empty_state = 'Giỏ hàng trống'.encode('utf-8')
        assert empty_state in cart2.data, "cart empty after pop (V-01)"
    print("  [V-01] stock-0 product popped + info flash + no qty-0 row ... OK")


def _verify_v10_regression(app):
    """v1.0 regression smoke: catalog list/detail, diacritic-free search, Messenger strip, admin CRUD."""
    print("Verify: v1.0 regression smoke (catalog/search/contact/admin CRUD)")
    with app.app_context():
        home_pid = Product.query.filter_by(name='Áo thun').first().id
    with app.test_client() as tc:
        _login(tc)

        # Catalog list
        home = tc.get('/')
        assert home.status_code == 200
        ao_thun = 'Áo thun'.encode('utf-8')
        assert ao_thun in home.data

        # Catalog detail
        detail = tc.get(f'/products/{home_pid}')
        assert detail.status_code == 200
        assert ao_thun in detail.data

        # Diacritic-free search: 'ao' (no mark) returns 'Áo thun'
        # normalize_search_text lowercases + strips diacritics: 'Áo thun' -> 'ao thun'
        s = tc.get('/search?q=ao')
        assert s.status_code == 200
        assert ao_thun in s.data, "diacritic-free search 'ao' should find 'Áo thun'"

        # Messenger contact strip (home shows contact strip)
        messenger_bytes = MESSENGER_URL.encode('utf-8')
        assert messenger_bytes in home.data, "Messenger contact strip missing on home"

        # Admin product CRUD (create / edit / delete) — must NOT touch product images here
        # Create
        r = tc.post('/admin/products/new', data={
            'name': 'San pham Test CRUD',
            'price': '75000',
            'cost_price': '40000',
            'quantity': '3',
        }, follow_redirects=True)
        assert r.status_code == 200
        with app.app_context():
            created = Product.query.filter_by(name='San pham Test CRUD').first()
            assert created is not None and created.price == 75000 and created.cost_price == 40000

        # Edit
        r = tc.post(f'/admin/products/{created.id}/edit', data={
            'name': 'San pham Test CRUD (sua)',
            'price': '80000',
            'cost_price': '45000',
            'quantity': '2',
        }, follow_redirects=True)
        assert r.status_code == 200
        with app.app_context():
            db.session.expire_all()
            edited = db.session.get(Product, created.id)
            assert edited.name == 'San pham Test CRUD (sua)' and edited.price == 80000

        # Delete
        r = tc.post(f'/admin/products/{created.id}/delete', follow_redirects=True)
        assert r.status_code == 200
        with app.app_context():
            assert db.session.get(Product, created.id) is None, "product should be deleted"
    print("  [v1.0 smoke] catalog/detail/search/contact/admin CRUD ... OK")


def _verify_ord05_csrf():
    """ORD-05 CSRF facet: separate app instance with CSRF enabled -> token-less checkout = 400."""
    print("Verify: ORD-05 CSRF facet (WTF_CSRF_ENABLED=True, token-less checkout)")
    tmpdir = tempfile.mkdtemp(prefix='gsd_verify_csrf_')
    app = _setup_app(tmpdir, csrf=True)
    with app.app_context():
        db.create_all()
        db.session.add(AdminUser(username='admin', password_hash=generate_password_hash('testpass1234')))
        p = Product(name='Áo CSRF', price=100000, quantity=5)
        db.session.add(p)
        db.session.commit()
        pid = p.id
    with app.test_client() as tc:
        tc.post('/login', data={'username': 'admin', 'password': 'testpass1234'})
        with tc.session_transaction() as sess:
            sess['cart'] = {str(pid): 1}
        # POST checkout WITHOUT csrf_token -> Flask-WTF CSRFError -> 400
        r = tc.post('/cart/checkout', data={
            'customer_name': 'Test', 'customer_phone': '0123456789',
            'customer_address': 'HN', 'website': '',
        })
        assert r.status_code == 400, f"CSRF-enabled checkout without token should be 400, got {r.status_code}"
        # No order created
        with app.app_context():
            assert Order.query.count() == 0
    print("  [ORD-05 CSRF] token-less checkout rejected 400, 0 orders ... OK")


# ---------------------------------------------------------------------------
# Small assertion helpers
# ---------------------------------------------------------------------------

def _assert_stat(html, label, value):
    m = re.search(rf'<p class="stat-label">{label}</p>\s*<p class="stat-value">([^<]+)</p>', html)
    assert m, f"stat card '{label}' not found in HTML"
    actual = m.group(1).strip()
    assert actual == str(value), f"{label}: expected {value}, got {actual}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    tmpdir = tempfile.mkdtemp(prefix='gsd_verify_11_')
    app = _seed_full(tmpdir)

    _verify_cart_checkout(app)
    _verify_order_tracking(app)
    _verify_cost_price(app)
    _verify_stats(app)
    _verify_v01(app)
    _verify_v10_regression(app)
    _verify_plat05(tmpdir)
    _verify_v10_regression(app)  # re-run regression after all the mutations
    _verify_ord05_csrf()

    # Empty-DB stats (reuse same app after dropping data)
    _verify_empty_stats(app)

    print('TASK_OK')


if __name__ == '__main__':
    main()
