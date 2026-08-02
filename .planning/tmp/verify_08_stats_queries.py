"""Throwaway: verify Phase 8 stats aggregation query patterns against the real models on a temp DB."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # repo root

import app as app_module
TMP = tempfile.mkdtemp(prefix='gsd_verify_08_')
app_module.BASE_DIR = TMP
os.makedirs(os.path.join(TMP, 'data'), exist_ok=True)

from app import create_app, db
from app.models import Product, Order, OrderItem
from app.admin import ORDER_STATUSES

QUALIFYING = ('Đã gửi', 'Đã nhận')

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False
with app.app_context():
    db.create_all()
    # Products: p1 in-stock w/ cost, p2 out-of-stock no cost, p3 discontinued w/ cost
    p1 = Product(name='Áo', price=100000, cost_price=60000, quantity=5)
    p2 = Product(name='Quần', price=200000, cost_price=None, quantity=0)
    p3 = Product(name='Ví', price=300000, cost_price=200000, quantity=3, discontinued=True)
    db.session.add_all([p1, p2, p3])
    db.session.flush()
    # Orders
    a = Order(customer_name='A', customer_phone='1', customer_address='x', status='Đã nhận')
    b = Order(customer_name='B', customer_phone='1', customer_address='x', status='Đã gửi')
    c = Order(customer_name='C', customer_phone='1', customer_address='x', status='Đã hủy')
    d = Order(customer_name='D', customer_phone='1', customer_address='x', status='Chờ xác nhận')
    db.session.add_all([a, b, c, d])
    db.session.flush()
    db.session.add_all([
        OrderItem(order_id=a.id, product_id=p1.id, product_name='Áo', product_price=100000, product_cost_price=60000, quantity=2),
        OrderItem(order_id=a.id, product_id=p2.id, product_name='Quần', product_price=200000, product_cost_price=None, quantity=1),
        OrderItem(order_id=b.id, product_id=p3.id, product_name='Ví', product_price=300000, product_cost_price=200000, quantity=1),
        OrderItem(order_id=c.id, product_id=p1.id, product_name='Áo', product_price=100000, product_cost_price=60000, quantity=5),  # excluded (hủy)
        OrderItem(order_id=d.id, product_id=p2.id, product_name='Quần', product_price=200000, product_cost_price=None, quantity=1),  # excluded
    ])
    db.session.commit()

    # --- 1. Revenue + units (single combined query) ---
    row = (
        db.session.query(
            db.func.coalesce(db.func.sum(OrderItem.product_price * OrderItem.quantity), 0),
            db.func.coalesce(db.func.sum(OrderItem.quantity), 0),
        )
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status.in_(QUALIFYING))
        .one()
    )
    revenue, units_sold = row
    print('combined revenue/units ->', revenue, units_sold, 'expected 700000 4')

    # --- 2. Profit + count of cost-bearing items ---
    profit, profit_items = (
        db.session.query(
            db.func.coalesce(db.func.sum((OrderItem.product_price - OrderItem.product_cost_price) * OrderItem.quantity), 0),
            db.func.count(OrderItem.id),
        )
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status.in_(QUALIFYING), OrderItem.product_cost_price.isnot(None))
        .one()
    )
    print('profit/count ->', profit, profit_items, 'expected 180000 2')

    # --- 3. total qualifying items (to derive excluded count) ---
    total_qual_items = (
        db.session.query(db.func.count(OrderItem.id))
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status.in_(QUALIFYING))
        .scalar()
    )
    print('total qualifying items ->', total_qual_items, 'expected 3')

    # --- 4. status counts (established Phase 7 pattern) ---
    status_counts = dict(
        db.session.query(Order.status, db.func.count(Order.id)).group_by(Order.status).all()
    )
    total_orders = sum(status_counts.values())
    print('status_counts ->', status_counts, 'total', total_orders, 'expected dict total 4')

    # --- 5. inventory ---
    total_products = Product.query.count()
    in_stock = Product.query.filter(Product.quantity > 0, Product.discontinued.is_(False)).count()
    out_of_stock = Product.query.filter(Product.quantity == 0, Product.discontinued.is_(False)).count()
    discontinued = Product.query.filter(Product.discontinued.is_(True)).count()
    print('inventory ->', total_products, in_stock, out_of_stock, discontinued, 'expected 3 1 1 1')

    # --- 6. empty-DB coalesce check (no qualifying orders => 0, not None) ---
    empty_rev = (
        db.session.query(db.func.coalesce(db.func.sum(OrderItem.product_price * OrderItem.quantity), 0))
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status.in_(('Đã gói',)))
        .scalar()
    )
    print('empty-set coalesce ->', empty_rev, 'expected 0 (not None)')
