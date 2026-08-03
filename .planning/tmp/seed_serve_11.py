#!/usr/bin/env python
"""Seeded temp-DB server for V-02 Chrome screenshots (09-02).

Imports the seed helpers from verify_11_full.py, builds a full dataset in a
fresh temp DB, then serves the app with waitress on 127.0.0.1:8011.

To render admin pages without interactive login, a small WSGI middleware
injects a valid admin session cookie into every request lacking one. The
cookie is obtained once via a temp test client login (same SECRET_KEY).

NEVER touches the real data/app.db — the app's BASE_DIR is patched to a
fresh tempfile.mkdtemp() before create_app().

Run: SECRET_KEY=test ADMIN_PASSWORD=testpass1234 python .planning/tmp/seed_serve_11.py
"""
import os
import sys
import tempfile

os.environ.setdefault('SECRET_KEY', 'test')
os.environ.setdefault('FLASK_DEBUG', '0')

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from werkzeug.security import generate_password_hash  # noqa: E402
from waitress import serve  # noqa: E402

import io  # noqa: E402
from PIL import Image  # noqa: E402

import app as app_module  # noqa: E402
from app.db import db  # noqa: E402
from app.models import AdminUser, Product, ProductImage, Order, OrderItem  # noqa: E402
from app.image_utils import UPLOAD_DIR  # noqa: E402


def _make_thumbnail(product, uuid_name):
    """Create a dummy full-size + thumbnail image on disk for a seeded product."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    img = Image.new('RGB', (400, 400), color=(200, 200, 200))
    full_path = os.path.join(UPLOAD_DIR, uuid_name + '.jpg')
    thumb_path = os.path.join(UPLOAD_DIR, uuid_name + '_thumb.jpg')
    img.save(full_path, 'JPEG', quality=85)
    thumb = img.copy()
    thumb.thumbnail((400, 400))
    thumb.save(thumb_path, 'JPEG', quality=82)
    return uuid_name + '.jpg'


def _seed():
    """Seed a full dataset into a fresh temp DB. Returns (app, admin_cookie)."""
    tmpdir = tempfile.mkdtemp(prefix='gsd_seedserve_11_')
    app_module.BASE_DIR = tmpdir
    os.makedirs(os.path.join(tmpdir, 'data'), exist_ok=True)
    app_module.app = None
    app = app_module.create_app()
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
        db.session.add(AdminUser(username='admin', password_hash=generate_password_hash('testpass1234')))
        p1 = Product(name='Áo thun', price=100000, cost_price=60000, quantity=5, brand='H&N',
                     measurements='M', description='Áo thun thoáng', sort_order=1)
        p2 = Product(name='Quần âu', price=200000, cost_price=None, quantity=0)
        p3 = Product(name='Ví da', price=300000, cost_price=200000, quantity=3, discontinued=True)
        p4 = Product(name='Giày thể thao', price=500000, cost_price=250000, quantity=10, sort_order=2)
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()
        # Seed a thumbnail image for p1 (cart thumb will render .cart-thumb)
        fname = _make_thumbnail(p1, 'seed_p1_test')
        db.session.add(ProductImage(filename=fname, original_filename='test.jpg',
                                    product_id=p1.id, is_primary=True, sort_order=0))
        db.session.commit()
        # 25+ orders across all 5 statuses for pagination + stats
        statuses = ['Chờ xác nhận', 'Đã gói', 'Đã gửi', 'Đã nhận', 'Đã hủy']
        orders = []
        for i in range(25):
            orders.append(Order(
                customer_name=f'KH{i}', customer_phone='0123456789',
                customer_address='123 Đường phố', status=statuses[i % 5],
            ))
        db.session.add_all(orders)
        db.session.commit()
        # A couple of order items on revenue orders for stats
        o_recv = next(o for o in orders if o.status == 'Đã nhận')
        o_ship = next(o for o in orders if o.status == 'Đã gửi')
        db.session.add_all([
            OrderItem(order_id=o_recv.id, product_id=p1.id, product_name='Áo thun',
                      product_price=100000, product_cost_price=60000, quantity=2),
            OrderItem(order_id=o_recv.id, product_id=p2.id, product_name='Quần âu',
                      product_price=200000, product_cost_price=None, quantity=1),
            OrderItem(order_id=o_ship.id, product_id=p3.id, product_name='Ví da',
                      product_price=300000, product_cost_price=200000, quantity=1),
        ])
        db.session.commit()
    # Get a valid admin session cookie via test client (same SECRET_KEY signs it)
    with app.test_client() as tc:
        tc.post('/login', data={'username': 'admin', 'password': 'testpass1234'})
        # Extract session cookie
        cookie_header = tc.get('/admin/dashboard').headers.get('Cookie', '')
        # The test client stores cookies internally; use the cookie jar
        cookie = tc.get_cookie('session')
    return app, cookie, tmpdir


class AdminAuthMiddleware:
    """WSGI middleware that injects an admin session cookie into every request
    that lacks one. Lets Chrome screenshots hit admin pages without a login form.

    Local-only dev server (127.0.0.1:8011) — no production exposure.
    """

    def __init__(self, app, session_cookie_value):
        self.app = app
        self.session_cookie_value = session_cookie_value

    def __call__(self, environ, start_response):
        http_cookie = environ.get('HTTP_COOKIE', '')
        if 'session=' not in http_cookie and self.session_cookie_value:
            if http_cookie:
                http_cookie = http_cookie + '; session=' + self.session_cookie_value
            else:
                http_cookie = 'session=' + self.session_cookie_value
            environ['HTTP_COOKIE'] = http_cookie
        return self.app(environ, start_response)


def main():
    print("Seeding temp DB + capturing admin session cookie...")
    app, cookie, tmpdir = _seed()
    cookie_val = cookie.value if cookie else ''
    print(f"Temp DB at: {tmpdir} (never the real data/app.db)")
    print(f"Admin session cookie obtained: {'YES' if cookie_val else 'NO'}")

    # Wrap with auth middleware
    app.wsgi_app = AdminAuthMiddleware(app.wsgi_app, cookie_val)

    print("Serving on http://127.0.0.1:8011 — press Ctrl+C to stop.")
    serve(app, host='127.0.0.1', port=8011)


if __name__ == '__main__':
    main()
