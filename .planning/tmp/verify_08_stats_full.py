#!/usr/bin/env python
"""Full E2E self-check for Phase 8 Admin Stats dashboard (08-03).

Runs entirely against a temp DB (patches app.BASE_DIR before create_app).
Seeds: 3 products (incl. discontinued + NULL-cost + out-of-stock) + 4 orders
5 statuses + 5 order items. Asserts: revenue 700000, profit 180000, profit_note,
units 4, status dict, total_orders 4, inventory 3/1/1/1, plus empty-DB zeros.

Run: SECRET_KEY=test python .planning/tmp/verify_08_stats_full.py
"""
import os
import re
import sys
import tempfile

os.environ['SECRET_KEY'] = 'test'
os.environ['FLASK_DEBUG'] = '0'

# Ensure repo root (3 levels up from .planning/tmp/) is on the path.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

import app as app_module  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

from app.db import db  # noqa: E402
from app.models import AdminUser, Product, Order, OrderItem  # noqa: E402


def _setup_app(tmpdir):
    app_module.BASE_DIR = tmpdir
    os.makedirs(os.path.join(tmpdir, 'data'), exist_ok=True)
    app = app_module.create_app()
    app.config['WTF_CSRF_ENABLED'] = False
    return app


def _seed_full(tmpdir):
    app = _setup_app(tmpdir)
    with app.app_context():
        db.create_all()
        db.session.add(AdminUser(username='admin', password_hash=generate_password_hash('testpass1234')))
        p1 = Product(name='Áo', price=100000, cost_price=60000, quantity=5)            # in stock, cost
        p2 = Product(name='Quần', price=200000, cost_price=None, quantity=0)           # out of stock, NULL cost
        p3 = Product(name='Ví', price=300000, cost_price=200000, quantity=3, discontinued=True)  # discontinued
        o_recv = Order(status='Đã nhận', customer_name='KH1', customer_phone='0123', customer_address='HN')   # qualifies for revenue
        o_ship = Order(status='Đã gửi', customer_name='KH2', customer_phone='0456', customer_address=' HCM')   # qualifies for revenue
        o_cancel = Order(status='Đã hủy', customer_name='KH3', customer_phone='0789', customer_address='DN') # excluded from revenue
        o_pending = Order(status='Chờ xác nhận', customer_name='KH4', customer_phone='0111', customer_address='HP')  # excluded from revenue
        db.session.add_all([p1, p2, p3, o_recv, o_ship, o_cancel, o_pending])
        db.session.flush()
        # a: Đã nhận -> p1 qty2 (cost 60k, profit 80k) + p2 qty1 (NULL cost, excluded from profit)
        db.session.add_all([OrderItem(order_id=o_recv.id, product_id=p1.id, product_name='Áo',
                                       product_price=100000, product_cost_price=60000, quantity=2),
                            OrderItem(order_id=o_recv.id, product_id=p2.id, product_name='Quần',
                                       product_price=200000, product_cost_price=None, quantity=1)])
        # b: Đã gửi -> p3 qty1 (cost 200k, profit 100k)
        db.session.add(OrderItem(order_id=o_ship.id, product_id=p3.id, product_name='Ví',
                                 product_price=300000, product_cost_price=200000, quantity=1))
        # c: Đã hủy -> p1 qty5 (excluded from revenue/profit)
        db.session.add(OrderItem(order_id=o_cancel.id, product_id=p1.id, product_name='Áo',
                                 product_price=100000, product_cost_price=60000, quantity=5))
        # d: Chờ xác nhận -> p2 qty1 (excluded)
        db.session.add(OrderItem(order_id=o_pending.id, product_id=p2.id, product_name='Quần',
                                 product_price=200000, product_cost_price=None, quantity=1))
        db.session.commit()
    return app


def _verify_full(app):
    with app.test_client() as tc:
        tc.post('/login', data={'username': 'admin', 'password': 'testpass1234'})
        resp = tc.get('/admin/stats')
    assert resp.status_code == 200, resp.status_code
    html = resp.get_data(as_text=True)

    # Revenue: a p1(100k*2=200k) + a p2(200k*1=200k) + b p3(300k*1=300k) = 700000
    assert '700.000₫' in html, f"revenue not found in {html[:500]}"
    # Profit: a p1 (100k-60k)*2 = 80k + b p3 (300k-200k)*1 = 100k = 180000
    assert '180.000₫' in html, f"profit not found"
    # NULL-safe note: 2 cost-bearing items contributed, 1 (p2 qty1 on order a) excluded
    assert 'Lợi nhuận tính trên 2 sản phẩm có giá nhập.' in html, "profit_note missing"
    # Units sold: 2+1+1 = 4
    _assert_stat(html, 'Sản phẩm đã bán', 4)
    # Total orders: 4 (all statuses incl Đã hủy)
    _assert_stat(html, 'Tổng số đơn', 4)
    # Status breakdown: 5 statuses + Đã gói shows 0
    assert 'Đã gói' in html
    # Đã hủy = 1, Chờ xác nhận = 1, Đã gửi = 1, Đã nhận = 1, Đã gói = 0
    assert _badge_count(html, 'Đã hủy') == 1
    assert _badge_count(html, 'Chờ xác nhận') == 1
    assert _badge_count(html, 'Đã gửi') == 1
    assert _badge_count(html, 'Đã nhận') == 1
    # Inventory: total 3, in stock 1, out of stock 1, discontinued 1
    _assert_stat(html, 'Tổng sản phẩm', 3)
    _assert_stat(html, 'Còn hàng', 1)
    _assert_stat(html, 'Hết hàng', 1)
    _assert_stat(html, 'Ngừng bán', 1)
    assert 'Gồm cả sản phẩm ngừng bán.' in html
    print("  [full seed] revenue=700000, profit=180000, units=4, orders=4, inventory=3/1/1/1 ... OK")


def _verify_empty(app):
    resp = app.test_client().get('/admin/stats')
    assert resp.status_code == 302, "unauth should redirect"
    with app.test_client() as tc:
        tc.post('/login', data={'username': 'admin', 'password': 'testpass1234'})
        resp = tc.get('/admin/stats')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert '0₫' in html, "empty revenue should render 0₫"
    _assert_stat(html, 'Tổng số đơn', 0)
    _assert_stat(html, 'Tổng sản phẩm', 0)
    _assert_stat(html, 'Còn hàng', 0)
    _assert_stat(html, 'Hết hàng', 0)
    _assert_stat(html, 'Ngừng bán', 0)
    print("  [empty DB] all zeros render (0 VND, 0 don, 0 inventory) ... OK")


def _assert_stat(html, label, value):
    m = re.search(rf'<p class="stat-label">{label}</p>\s*<p class="stat-value">([^<]+)</p>', html)
    assert m, f"stat card '{label}' not found in HTML"
    actual = m.group(1).strip()
    assert actual == str(value), f"{label}: expected {value}, got {actual}"


def _badge_count(html, status):
    """Extract the integer badge value for a status in the Đơn hàng breakdown."""
    m = re.search(rf'>{re.escape(status)} <span class="badge [^"]*">(\d+)</span>', html)
    assert m, f"status breakdown for '{status}' not found"
    return int(m.group(1))


def main():
    tmpdir = tempfile.mkdtemp(prefix='gsd_verify_08_')

    print("Verify 1: Full-seed stats dashboard")
    app = _seed_full(tmpdir)
    _verify_full(app)

    print("Verify 2: Empty DB renders zeros")
    # New app on a fresh temp DIR to guarantee empty DB.
    tmpdir2 = tempfile.mkdtemp(prefix='gsd_verify_08_empty_')
    app2 = _setup_app(tmpdir2)
    with app2.app_context():
        db.create_all()
        db.session.add(AdminUser(username='admin', password_hash=generate_password_hash('testpass1234')))
        db.session.commit()
    _verify_empty(app2)

    print('TASK_OK')


if __name__ == '__main__':
    main()
