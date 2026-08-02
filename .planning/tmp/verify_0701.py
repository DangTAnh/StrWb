"""Verify 07-01 (order list + status filter) against a temp DB — never touches data/app.db."""
import os, sys, tempfile
from werkzeug.security import generate_password_hash

import app as app_module
TMP = tempfile.mkdtemp(prefix='gsd_verify_0701_')
app_module.BASE_DIR = TMP
os.makedirs(os.path.join(TMP, 'data'), exist_ok=True)

from app import create_app, db
from app.models import AdminUser, Product, Order, OrderItem

FAILED = []
def check(name, cond):
    print(f'{name}: {"OK" if cond else "FAIL"}')
    if not cond:
        FAILED.append(name)

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False
with app.app_context():
    db.create_all()
    db.session.add(AdminUser(username='admin', password_hash=generate_password_hash('pw')))
    p1 = Product(name='Áo thun', price=100000, quantity=5, sort_order=0)
    db.session.add(p1)
    db.session.flush()
    o1 = Order(customer_name='Nguyễn A', customer_phone='0901', customer_address='HN',
               status='Chờ xác nhận')
    o2 = Order(customer_name='Trần B', customer_phone='0902', customer_address='HCM',
               status='Đã gói')
    db.session.add_all([o1, o2])
    db.session.flush()
    db.session.add_all([
        OrderItem(order_id=o1.id, product_id=p1.id, product_name='Áo thun', product_price=100000, quantity=2),
        OrderItem(order_id=o2.id, product_id=p1.id, product_name='Áo thun', product_price=100000, quantity=1),
    ])
    # 25 orders in 'Đã gửi' -> forces 2 pages at per_page=20 to test pagination
    for i in range(25):
        db.session.add(Order(customer_name=f'Khách {i}', customer_phone=f'09{i:04d}',
                             customer_address='HP', status='Đã gửi'))
    db.session.commit()

    from app.admin import ORDER_STATUSES, _order_total, order_badge_class
    check('ORDER_STATUSES exists (5 states)', ORDER_STATUSES == ('Chờ xác nhận', 'Đã gói', 'Đã gửi', 'Đã nhận', 'Đã hủy'))
    check('_order_total is Jinja global', '_order_total' in app.jinja_env.globals)
    check('order_badge_class is Jinja global', 'order_badge_class' in app.jinja_env.globals)
    check('_order_total math', _order_total(o1) == 200000)
    check('order_badge_class maps', order_badge_class('Đã gói') == 'badge-order-packed' and order_badge_class('Không có') == '')

client = app.test_client()
r = client.post('/login', data={'username': 'admin', 'password': 'pw'}, follow_redirects=True)
check('admin login', r.status_code == 200 and 'Sản phẩm' in r.get_data(as_text=True))

r = client.get('/admin/orders')
body = r.get_data(as_text=True)
check('GET /admin/orders 200', r.status_code == 200)
check('page1 shows newest orders', 'Khách 19' in body and 'badge-order-shipped' in body)
check('page1 shows 0-total rows', '0' in body)
r = client.get('/admin/orders?page=2')
body2 = r.get_data(as_text=True)
check('page2 shows older orders', 'Nguyễn A' in body2 and 'Trần B' in body2)
check('page2 shows status badges', 'badge-order-pending' in body2 and 'badge-order-packed' in body2)
check('page2 shows totals (200.000)', '200.000' in body2)
r = client.get('/admin/orders?status=Đã gửi')
pb = r.get_data(as_text=True)
import re as _re
pag_link = _re.search(r'href="([^"]*page=2[^"]*)"', pb)
check('pagination link exists (2 pages)', bool(pag_link))
check('pagination keeps ?status=', bool(pag_link) and 'status=' in pag_link.group(1))

r = client.get('/admin/orders?status=Đã gói')
body = r.get_data(as_text=True)
check('filter ?status=Đã gói works', 'Trần B' in body and 'Nguyễn A' not in body)

r = client.get('/admin/orders?page=999')
check('page 999 -> 200 (error_out=False)', r.status_code == 200)

r = client.get('/admin/')
body = r.get_data(as_text=True)
check('dashboard has Đơn hàng nav', 'Đơn hàng' in body)

print()
print('TASK_OK' if not FAILED else f'FAILED: {FAILED}')
sys.exit(0 if not FAILED else 1)
