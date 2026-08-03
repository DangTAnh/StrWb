"""Verify quick 260803-kaa (Đã xác nhận state + stock decrement on confirm) against a temp DB.
Never touches data/app.db — mirrors verify_0701.py pattern.
"""
import os, sys, tempfile
from werkzeug.security import generate_password_hash

os.environ['SECRET_KEY'] = 'test'  # khớp pattern verify_11_full.py / verify_08_stats_full.py
os.environ['FLASK_DEBUG'] = '0'

import app as app_module
TMP = tempfile.mkdtemp(prefix='gsd_verify_kaa_')
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
    p_live = Product(name='Áo thun', price=100000, quantity=5, sort_order=0)
    db.session.add(p_live)
    db.session.flush()
    # Order in 'Chờ xác nhận' with 2 items:
    #  - item live (product exists, qty=3)
    #  - item deleted (product_id NULL via SET NULL, qty=2) — must be skipped
    o1 = Order(customer_name='Nguyễn A', customer_phone='0901', customer_address='HN',
               status='Chờ xác nhận')
    db.session.add(o1)
    db.session.flush()
    db.session.add_all([
        OrderItem(order_id=o1.id, product_id=p_live.id, product_name='Áo thun',
                  product_price=100000, quantity=3),
        OrderItem(order_id=o1.id, product_id=None, product_name='Áo đã xóa',
                  product_price=100000, quantity=2),
    ])
    db.session.commit()
    ORDER_ID = o1.id
    PRODUCT_ID = p_live.id

    from app.admin import ORDER_STATUSES, TRANSITION_MAP, order_badge_class
    check('ORDER_STATUSES 6 states, Đã xác nhận ở vị trí 2',
          ORDER_STATUSES == ('Chờ xác nhận', 'Đã xác nhận', 'Đã gói', 'Đã gửi', 'Đã nhận', 'Đã hủy'))
    check('TRANSITION_MAP Chờ xác nhận -> {Đã xác nhận, Đã hủy}',
          TRANSITION_MAP['Chờ xác nhận'] == {'Đã xác nhận', 'Đã hủy'})
    check('TRANSITION_MAP Đã xác nhận -> {Đã gói, Đã hủy}',
          TRANSITION_MAP['Đã xác nhận'] == {'Đã gói', 'Đã hủy'})
    check('Đã gói NOT in Chờ xác nhận transitions',
          'Đã gói' not in TRANSITION_MAP['Chờ xác nhận'])
    check('order_badge_class(Đã xác nhận)', order_badge_class('Đã xác nhận') == 'badge-order-confirmed')

client = app.test_client()
client.post('/login', data={'username': 'admin', 'password': 'pw'}, follow_redirects=True)

# Reject direct Chờ xác nhận -> Đã gói (must go via Đã xác nhận)
r = client.post(f'/admin/orders/{ORDER_ID}/status', data={'next_status': 'Đã gói'},
                follow_redirects=True)
body = r.get_data(as_text=True)
with app.app_context():
    db.session.expire_all()
    order = db.session.get(Order, ORDER_ID)
    p = db.session.get(Product, PRODUCT_ID)
    check('POST Đã gói từ Chờ xác nhận bị reject', order.status == 'Chờ xác nhận')
    check('Stock không thay đổi khi reject (5)', p.quantity == 5)

# Confirm: Chờ xác nhận -> Đã xác nhận, stock 5 -> 2 (trừ 3 của item live, bỏ qua item deleted qty=2)
r = client.post(f'/admin/orders/{ORDER_ID}/status', data={'next_status': 'Đã xác nhận'},
                follow_redirects=True)
check('POST Đã xác nhận redirect 200', r.status_code == 200)
with app.app_context():
    db.session.expire_all()
    order = db.session.get(Order, ORDER_ID)
    p = db.session.get(Product, PRODUCT_ID)
    check('Order status -> Đã xác nhận', order.status == 'Đã xác nhận')
    check('Stock 5 -> 2 (trừ 3, bỏ qua item deleted)', p.quantity == 2)

# Idempotent: repeat confirm must reject (forward-only), stock unchanged
r = client.post(f'/admin/orders/{ORDER_ID}/status', data={'next_status': 'Đã xác nhận'},
                follow_redirects=True)
with app.app_context():
    db.session.expire_all()
    order = db.session.get(Order, ORDER_ID)
    p = db.session.get(Product, PRODUCT_ID)
    check('POST lặp Đã xác nhận bị reject', order.status == 'Đã xác nhận')
    check('Stock không trừ kép (vẫn 2)', p.quantity == 2)

# UI checks (detail + list filter + stats) after confirm succeeds
r = client.get(f'/admin/orders/{ORDER_ID}')
body = r.get_data(as_text=True)
check('detail has badge-order-confirmed', 'badge-order-confirmed' in body)
check('detail has "Chuyển sang: Đã gói"', 'Chuyển sang: Đã gói' in body)
for step in ['Chờ xác nhận', 'Đã xác nhận', 'Đã gói', 'Đã gửi', 'Đã nhận']:
    check(f'detail stepper có bước "{step}"', step in body)

r = client.get('/admin/orders?status=Đã xác nhận')
body = r.get_data(as_text=True)
check('orders filter dropdown có option Đã xác nhận', 'Đã xác nhận' in body and 'value="Đã xác nhận"' in body)

r = client.get('/admin/stats')
body = r.get_data(as_text=True)
check('stats breakdown có Đã xác nhận', 'Đã xác nhận' in body and 'badge-order-confirmed' in body)

print()
print('TASK_OK' if not FAILED else f'FAILED: {FAILED}')
sys.exit(0 if not FAILED else 1)
