# Architecture Research: Order Placement + Order Tracking + Stats

**Domain:** Flask product catalog (single admin, SQLite, self-hosted, Vietnamese) — extending existing v1.0 with buy-system features
**Researched:** 2026-08-02
**Confidence:** HIGH (based on codebase inspection: app/__init__.py, admin.py, public.py, models.py, forms.py, templates)

## Executive Summary

The existing codebase is a clean Flask app-factory with 3 blueprints (`public`, `admin`, `auth`) and a flat SQLAlchemy model layer (`Product`, `ProductImage`, `AdminUser`). Adding the v1.1 buy-system features requires:

1. **Two new models** — `Order` (header: customer name, phone, address, product ref, quantity, note, status, timestamps) and `OrderStatus` (enum-like lookup or inline choices).
2. **One new optional column** — `cost_price` on `Product` (nullable Integer, admin-only visibility).
3. **Two new route clusters** — public order-placement on the product detail page (unauthenticated, public_bp) and admin order-tracking + stats dashboard (authenticated, admin_bp).
4. **Two new forms** — `OrderForm` (public, no CSRF needed for unauthenticated user but CSRFProtect is global so it applies; use Flask-WTF and render `csrf_token`) and `OrderStatusForm` (admin, small form to advance an order's status).
5. **A schema-migration strategy** — `db.create_all()` won't add the `cost_price` column or the new tables to existing deployments; the safest lightweight path is an idempotent `ALTER TABLE` + `CREATE TABLE IF NOT EXISTS` in a CLI command, with flask-migrate reserved for later schema churn.

**Integration approach:** everything slots into the existing patterns. The public blueprint gets a `POST /products/<id>/order` route that mirrors how `public_bp.product_detail` already renders. The admin blueprint gets `/admin/orders`, `/admin/orders/<id>`, `/admin/stats`, and the dashboard nav gains links. Models gain no new imports beyond what `db` and `utcnow` already provide. Forms follow the Flask-WTF + Jinja `wtf` macro pattern already established by `ProductForm`.

## Existing Architecture Review

### Current File Layout (v1.0, shipped)

```
app/
├── __init__.py        # create_app(): config, WAL pragma, extensions, 3 blueprints, format_price filter
├── db.py              # db = SQLAlchemy(), init-db CLI (create_all + upsert admin)
├── models.py          # AdminUser(UserMixin), Product, ProductImage — single base class `db.Model`
├── forms.py           # LoginForm, ProductForm — Flask-WTF, VN labels
├── auth.py            # auth_bp: /login, /logout, login_manager.user_loader
├── admin.py           # admin_bp @ /admin: /, /products, /products/new, /products/<id>/edit, /products/<id>/delete
├── public.py          # public_bp @ /: /, /products/<id>, /search — normalize_search_text, _manual_pagination
├── image_utils.py     # validate_image_upload, save_image_file (Pillow), delete_image_files
└── templates/
    ├── base.html         # <html lang="vi">, flash zone, {% block content %}
    ├── public/
    │   ├── _nav.html     # brand + search form
    │   ├── base.html     # extends base, {% block header %} = _nav
    │   ├── index.html    # product-grid (2/3/4 cols), contact-strip (Messenger)
    │   ├── product_detail.html  # gallery + price + status + Messenger CTA
    │   └── search.html
    └── admin/
        ├── dashboard.html
        └── products/{list,form,delete}.html
```

### Current Data Model (models.py — v1.0)

```python
class AdminUser(UserMixin, db.Model):  # admin_users
    id, username(unique), password_hash, created_at

class Product(db.Model):  # products
    id, name, price(Integer VND), brand, measurements(Text), description(Text),
    quantity(default=0), discontinued(Boolean default=False), sku, sort_order,
    admin_note, created_at, updated_at
    status @property  -> 'discontinued' | 'available' | 'out_of_stock'
    primary_image @property -> images.order_by(sort_order).first()
    images = relationship(ProductImage, cascade='all, delete-orphan')

class ProductImage(db.Model):  # product_images
    id, filename(UUID), original_filename, product_id(FK), is_primary, sort_order, created_at
    thumb_filename @property -> filename[:-4] + '_thumb.jpg'
```

### Current Blueprint + Route Topology

| Blueprint | Routes | Auth | Notes |
|-----------|--------|------|-------|
| `public_bp` | `/` (home, paginated 12/grid) | none | `normalize_search_text`, manual pagination |
| `public_bp` | `/products/<int:product_id>` (GET detail) | none | gallery, price, status, Messenger CTA |
| `public_bp` | `/search?q=` (GET) | none | NFD+casefold in-Python over all products |
| `admin_bp` | `/` (dashboard) | `@before_request login_required` | products_count |
| `admin_bp` | `/products` (GET list) | required | pagination 20, table with status badges |
| `admin_bp` | `/products/new` (GET/POST) | required | ProductForm + image batch processing |
| `admin_bp` | `/products/<id>/edit` (GET/POST) | required | ProductForm(obj=product) + image batch |
| `admin_bp` | `/products/<id>/delete` (GET/POST) | required | confirmation page, file deletion |
| `auth_bp` | `/login` (GET/POST) | none | Flask-Login login_user, remember=True |
| `auth_bp` | `/logout` (POST) | `@login_required` | logout_user |

### Current Config (app/__init__.py)

- `SQLALCHEMY_DATABASE_URI` = `sqlite:///` + `data/app.db`
- `SQLALCHEMY_ENGINE_OPTIONS={'connect_args': {'timeout': 30}}` + `_set_sqlite_pragma` event: `journal_mode=WAL`, `busy_timeout=30000`
- `MAX_CONTENT_LENGTH = 16MB`
- `format_price` Jinja filter: `f'{int(value):,}'.replace(',', '.') + '₫'`
- CSRF via `CSRFProtect()` global (all POST routes protected)
- `MESSENGER_URL` config var drives the public Messenger CTA

## How New Features Integrate

### 1. New Models

**Order model** — single table, one order per product (no OrderItem needed; the requirement is "each order = 1 product").

```python
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)       # snapshot at order time
    price_at_order = db.Column(db.Integer, nullable=False)        # snapshot: revenue calc
    cost_price_at_order = db.Column(db.Integer, nullable=True)     # snapshot: profit calc
    quantity = db.Column(db.Integer, default=1, nullable=False)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(30), nullable=False)
    customer_address = db.Column(db.Text, nullable=False)
    note = db.Column(db.Text, nullable=True)
    status = db.Column(db.Integer, default=1, nullable=False)     # FK to status_lookup OR enum int
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    product = db.relationship('Product', backref='orders')
```

**Schema decisions:**
- `product_name`, `price_at_order`, `cost_price_at_order` are **snapshots**. The product may be deleted or price-changed after an order is placed. Revenue/profit stats must reflect the price at order time, not the current product price.
- `quantity` defaults to 1; validator caps at `product.quantity` (can't order more than stock — though admin may choose to accept backorders; defer that nuance).
- `status` as a small-integer enum (see below) is simplest for SQLite + avoids a join table.

**Order status enum** — keep it simple, no lookup table:

```python
# In models.py, as module-level constants or a Python enum mapped to integers
ORDER_STATUS_PENDING   = 1   # 'Chờ xác nhận' — just placed
ORDER_STATUS_PACKED    = 2   # 'Đã gói'
ORDER_STATUS_SHIPPED   = 3   # 'Đã gửi'
ORDER_STATUS_DELIVERED = 4   # 'Đã nhận'
ORDER_STATUS_CANCELLED = 0   # 'Đã hủy' — edge case, admin-only

ORDER_STATUSES = [
    (ORDER_STATUS_CANCELLED, 'Đã hủy'),
    (ORDER_STATUS_PENDING, 'Chờ xác nhận'),
    (ORDER_STATUS_PACKED, 'Đã gói'),
    (ORDER_STATUS_SHIPPED, 'Đã gửi'),
    (ORDER_STATUS_DELIVERED, 'Đã nhận'),
]
```

> Rationale: The v1.1 milestone specifies only "đã gói → đã gửi → đã nhận" as the active flow. A "cancelled" bucket is included for data hygiene (orders can't be hard-deleted if stats are cumulative), but it is admin-only and out of the public view. No `OrderStatus` lookup table — adds a join for no benefit at this scale. Integer enum maps cleanly to SQLite and is trivial to query (`WHERE status >= 2`).

**Cost price on Product** — nullable Integer:

```python
# Add to existing Product model
cost_price = db.Column(db.Integer, nullable=True)  # VND, optional, admin-only
```

> Rationale: Integer matches `price` (VND, no subunit). Nullable because not all products have a recorded cost. Admin-only visibility enforced in templates (never render to public).

### 2. New Forms (forms.py)

```python
class OrderForm(FlaskForm):
    name = StringField('Họ và tên', validators=[DataRequired('Vui lòng nhập họ tên'), Length(max=200)])
    phone = StringField('Số điện thoại', validators=[DataRequired('Vui lòng nhập số điện thoại'), Length(max=30)])
    address = TextAreaField('Địa chỉ giao hàng', validators=[DataRequired('Vui lòng nhập địa chỉ'), Length(max=2000)])
    quantity = IntegerField('Số lượng', default=1, validators=[DataRequired('Vui lòng chọn số lượng'), NumberRange(min=1)])
    note = TextAreaField('Ghi chú', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Đặt hàng')
```

```python
class OrderStatusForm(FlaskForm):
    status = SelectField('Trạng thái', coerce=int, choices=ORDER_STATUSES, validators=[DataRequired()])
    note = TextAreaField('Ghi chú nội bộ', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Cập nhật')
```

> Note: `OrderForm` is public (unauthenticated) but CSRFProtect is global in v1.0 — every POST needs a CSRF token. The public form renders `{{ form.hidden_tag() }}` (already the pattern in `admin/products/form.html`). CSRF on an order form is correct (prevents cross-site order spam).

### 3. New / Modified Routes

#### Public — order placement on product detail

**No new route URL.** The form `POST`s to the existing `public.product_detail` route, which must be changed to accept `POST`:

```python
# public.py — modify existing route
@public_bp.route('/products/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404)
    form = OrderForm()
    if form.validate_on_submit() and product.status == 'available':
        # create Order, snapshot product fields, commit
        order = Order(
            product_id=product.id,
            product_name=product.name,
            price_at_order=product.price,
            cost_price_at_order=product.cost_price,
            quantity=form.quantity.data,
            customer_name=form.name.data.strip(),
            customer_phone=form.phone.data.strip(),
            customer_address=form.address.data.strip(),
            note=form.note.data or None,
        )
        # quantity validation: cap at product.quantity
        db.session.add(order)
        db.session.commit()
        flash('Đơn hàng của bạn đã được gửi. Chúng tôi sẽ liên hệ sớm nhất có thể.', 'success')
        return redirect(url_for('public.product_detail', product_id=product.id))
    images = product.images.order_by(ProductImage.sort_order.asc()).all()
    # ... existing rendering ...
    return render_template('public/product_detail.html', product=product, images=images, form=form, ...)
```

**Template change** — `product_detail.html` gains an order form block replacing the Messenger CTA button when `product.status == 'available'`:

```jinja
{% if product.status == 'available' %}
  <form method="post" class="order-form">
    {{ form.hidden_tag() }}
    <!-- name, phone, address, quantity, note fields -->
    {{ form.submit }}
  </form>
  <p class="help-text">Hoặc liên hệ trực tiếp qua Messenger để trao đổi thêm.</p>
  <a class="btn btn-secondary" href="{{ config['MESSENGER_URL'] }}" target="_blank" rel="noopener">Mua qua Messenger</a>
{% else %}
  {# existing Messenger CTA only #}
{% endif %}
```

> Rationale: The requirement says "replace the Messenger button with an order form; keep the Messenger contact strip." The order form becomes the primary CTA on the detail page for in-stock products; the Messenger link stays as a secondary option. Out-of-stock/discontinued products skip the form and show the Messenger link (admin may still negotiate).

#### Admin — order tracking + stats

**New admin routes** (all `@login_required` via the existing `before_request` hook on `admin_bp`):

```python
# admin.py — new routes
@admin_bp.route('/orders')
def orders():
    # list: recent orders, filter by status
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', type=int)  # None = all
    q = Order.query.order_by(Order.created_at.desc())
    if status:
        q = q.filter_by(status=status)
    pagination = q.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/orders/list.html', pagination=pagination, orders=pagination.items)

@admin_bp.route('/orders/<int:order_id>', methods=['GET', 'POST'])
def order_detail(order_id):
    order = db.session.get(Order, order_id)
    if order is None:
        abort(404)
    form = OrderStatusForm(obj=order)
    if form.validate_on_submit():
        order.status = form.status.data
        order.updated_at = utcnow()
        db.session.commit()
        flash('Đã cập nhật trạng thái đơn hàng.', 'success')
        return redirect(url_for('admin.order_detail', order_id=order.id))
    return render_template('admin/orders/detail.html', order=order, form=form)

@admin_bp.route('/stats')
def stats():
    # computed at request time (no caching — low volume)
    total_orders = Order.query.count()
    delivered = Order.query.filter_by(status=ORDER_STATUS_DELIVERED).count()
    total_revenue = Order.query.filter(Order.price_at_order != None).with_entities(func.sum(Order.price_at_order * Order.quantity)).scalar() or 0
    total_cost = Order.query.filter(Order.cost_price_at_order != None).with_entities(func.sum(Order.cost_price_at_order * Order.quantity)).scalar() or 0
    # products sold = sum of quantity where status >= shipped
    units_sold = db.session.scalar(
        select(func.sum(Order.quantity)).where(Order.status >= ORDER_STATUS_SHIPPED)
    ) or 0
    products_sold_count = db.session.query(func.count()).select_from(
        db.Session.query(Order.product_id).filter(Order.status >= ORDER_STATUS_SHIPPED).distinct()
    ).scalar() or 0
    # inventory
    total_inventory = db.session.scalar(db.select(func.sum(Product.quantity))) or 0
    return render_template('admin/stats.html', total_orders=total_orders, delivered=delivered,
                           total_revenue=total_revenue, total_cost=total_cost,
                           total_profit=total_revenue - total_cost,
                           units_sold=units_sold, products_sold_count=products_sold_count,
                           total_inventory=total_inventory)
```

> Note: Stats are computed at request-time via SQL `SUM`/`COUNT` aggregates — no caching needed for a single admin and low order volume. Uses SQLAlchemy `func` and `select` (Core-style for aggregation clarity). `Order.price_at_order` snapshot makes revenue correct even if product price changes later.

**Dashboard nav update** — `admin/dashboard.html` gains links to Orders and Stats:

```jinja
<a href="{{ url_for('admin.orders') }}">Đơn hàng</a>
<a href="{{ url_for('admin.stats') }}">Thống kê</a>
```

### 4. New Templates (placement matches existing structure)

```
templates/
├── public/
│   └── product_detail.html       # MODIFIED — add OrderForm, conditional CTA
└── admin/
    ├── dashboard.html            # MODIFIED — add Orders/Stats nav links
    ├── orders/
    │   ├── list.html             # NEW — order list with status filter + pagination
    │   └── detail.html           # NEW — order detail + status update form
    └── stats.html                # NEW — revenue/profit/units/inventory cards
```

> All templates extend the existing `base.html` (VN charset, `lang="vi"`, flash zone). Admin templates are inside `templates/admin/` matching the existing split.

### 5. New Forms Registration

`OrderForm` and `OrderStatusForm` go in the existing `app/forms.py` (single file, matching `LoginForm` + `ProductForm`).

## Schema Migration Strategy (existing SQLite DBs)

**Critical issue:** The v1.0 deploy uses `db.create_all()` in `init-db`. `create_all()` is **additive only** — it creates tables that don't exist but **never alters existing tables**. Adding `cost_price` to `Product` or `Order`/`orders` to an existing DB will be a no-op for the column, and the Order table won't exist for existing deployments.

**Recommended approach — lightweight idempotent CLI migration:**

Add a new CLI command `flask migrate-buy-system` (or extend `init-db`) that runs idempotent DDL:

```python
@click.command('migrate-buy-system')
@with_appcontext
def migrate_buy_system():
    """Add cost_price column + orders table for v1.1 buy system (idempotent)."""
    from .models import Order  # ensures Order is registered

    # 1. Create the orders table if it doesn't exist
    db.create_all()  # safe: no-op for existing tables

    # 2. Add cost_price column if missing (SQLite ALTER TABLE ADD COLUMN is idempotent-safe)
    col = db.session.execute(
        db.text("PRAGMA table_info(products)")
    ).fetchall()
    cols = {row[1] for row in col}  # column name is index 1
    if 'cost_price' not in cols:
        db.session.execute(db.text("ALTER TABLE products ADD COLUMN cost_price INTEGER"))
        db.session.commit()
        click.echo("Added cost_price column to products.")
    else:
        click.echo("cost_price column already present.")

    # 3. orders table — create_all handles it, but verify
    ord_col = db.session.execute(db.text("PRAGMA table_info(orders)")).fetchall()
    if not ord_col:
        click.echo("WARNING: orders table missing. Run flask db upgrade or flask init-db.")
    else:
        click.echo("orders table ready.")
```

> **Why not flask-migrate?** STACK.md marks flask-migrate 4.1.0 as "use once the product model is in active flux." v1.1 adds one column + one table — low churn. A 10-line idempotent ALTER + create_all is simpler, has no migration-file directory to commit, and works on the single-DB self-hosted model. If v1.2 adds more columns/tables, promote to flask-migrate at that point.

**Rollback plan:** SQLite supports `ALTER TABLE DROP COLUMN` in 3.35+. If a deployer needs to revert, document the manual `DELETE FROM orders; DROP TABLE orders;` and `ALTER TABLE products DROP COLUMN cost_price;` — but this is an edge case (single admin self-hosted, no CI/CD rollback expected). No automated downgrade needed.

**New deployment (greenfield):** `flask init-db` runs `db.create_all()` which includes the `orders` table and won't know about `cost_price` unless the model is already updated. So the deploy flow is:

1. Update `models.py` (add `cost_price` to Product, add `Order`).
2. `flask init-db` (creates tables including `orders`; does NOT add `cost_price` to existing tables, but greenfield DB gets it).
3. `flask migrate-buy-system` (idempotent safety net — adds `cost_price` to existing DBs, no-op on greenfield).

## Data Flow Changes

### Order placement (public, unauthenticated)

```
Browser (product page)
  → POST /products/<id> with OrderForm (CSRF token)
  → public_bp.product_detail (POST branch)
  → validate on_submit + product.status == 'available'
  → snapshot product.name, price, cost_price into Order
  → db.session.add(order) + commit
  → flash success + redirect to same product detail
  → Browser re-renders: form hidden, "Đơn hàng đã gửi" message shown
```

### Order tracking (admin, authenticated)

```
Browser (admin nav → Orders)
  → GET /admin/orders?status=<int>
  → admin_bp.orders: Order.query filtered by status, paginated
  → list.html renders table (name, phone, product, qty, price, status badge, date, actions)
  → click row → GET /admin/orders/<id>
  → admin_bp.order_detail: OrderStatusForm preloaded, POST advances status
  → commit + redirect (PRG pattern)
  → list updates with new status badge
```

### Stats computation (admin, authenticated)

```
Browser (admin nav → Stats)
  → GET /admin/stats
  → admin_bp.stats: aggregate queries (SUM(price*qty), COUNT, SUM(quantity))
  → stats.html renders cards: tổng doanh thu, lợi nhuận, số đơn, sản phẩm đã bán, tồn kho
```

## Build Order (dependency-respecting)

The v1.1 milestone adds features incrementally. Suggested phase split for implementation:

```
Phase A: Data model + migration (Order, cost_price, schema CLI)
Phase B: Public order form + product_detail integration + template
Phase C: Admin orders list + detail + status flow + templates
Phase D: Admin stats dashboard + templates + dashboard nav
Phase E: Polish (validation, error handling, Vietnamese labels)
```

**Rationale:**
- Phase A first — models must exist before any route references `Order` or `Product.cost_price`. The migration CLI must run before admin routes hit the `orders` table.
- Phase B second — public order form depends only on `Order` model + `Product` (already exists). Can be tested independently.
- Phase C third — admin order tracking depends on Phase A (model) + the orders table existing. List + detail + status flow are one unit.
- Phase D fourth — stats depends on Phase A (orders populated) + Phase C (orders tracked). Can't show meaningful stats until orders exist with real statuses.
- Phase E last — polish/validation is the same pattern as v1.0 Phase 4 (contrast, touch targets, VN labels, edge cases).

**Critical integration points (explicit):**

| Component | New or Modified | Touches |
|-----------|-----------------|---------|
| `models.py` | ADD `Order` model, ADD `cost_price` to `Product` | `db.Model`, `utcnow` (existing) |
| `forms.py` | ADD `OrderForm`, `OrderStatusForm` | `FlaskForm`, validators (existing imports) |
| `public.py` | MODIFY `product_detail` route: add `POST` method, `OrderForm` instantiation, snapshot+commit, conditional template rendering | existing `product_detail`, `Order`, `OrderForm` |
| `admin.py` | ADD 3 routes: `orders`, `order_detail`, `stats` | existing `db`, `Order`, `OrderStatusForm`, `Product` |
| `__init__.py` | ADD `migrate-buy-system` CLI command registration | existing `init_db_command` pattern |
| `templates/public/product_detail.html` | MODIFY — embed `OrderForm`, conditional CTA | existing form rendering, Messenger strip |
| `templates/admin/dashboard.html` | MODIFY — add Orders/Stats nav links | existing nav-list structure |
| `templates/admin/orders/list.html` | NEW — order list table | `pagination` pattern from products/list.html |
| `templates/admin/orders/detail.html` | NEW — order detail + status form | `OrderStatusForm`, status badges |
| `templates/admin/stats.html` | NEW — stat cards | `format_price` filter (existing) |
| `templates/admin/products/form.html` | MODIFY — add `cost_price` field (admin-only) | `ProductForm` gains field, rendered after `price` |

## Anti-Patterns to Avoid (v1.1-specific)

### Anti-Pattern: Storing live FK to product price in Order

**What people do:** `Order.subtotal = product.price` computed at display time, or `Order.product_id` used to look up current price for revenue.

**Why it's wrong:** Price changes after an order invalidates historical revenue. Profit calc breaks if `cost_price` changes.

**Do this instead:** Snapshot `price_at_order`, `cost_price_at_order`, `product_name` into the Order row at creation. Revenue = `SUM(Order.price_at_order * Order.quantity)`. Profit = `revenue - SUM(Order.cost_price_at_order * Order.quantity)`.

### Anti-Pattern: OrderItem table for single-product orders

**What people do:** Create `Order` + `OrderItem` because "that's how e-commerce works."

**Why it's wrong:** The v1.1 requirement is "each order = 1 product." An `OrderItem` join table adds a query + template layer for zero value.

**Do this instead:** Flat `Order` model with `product_id`, `quantity`, `price_at_order`. If v1.2 adds cart functionality, refactor to Order+OrderItem at that point — not preemptively.

### Anti-Pattern: Stats cached in summary table

**What people do:** Maintain a `stats_daily` rollup table updated via triggers/cron.

**Why it's wrong:** Single admin, low volume (<100 orders/month). Trigger overhead on every order write. Cron adds deployment complexity.

**Do this instead:** Compute stats at request time via SQL aggregates. If v1.2 crosses 1000 orders or 100 daily visits, add a materialized summary — not before.

### Anti-Pattern: Deleting orders to "undo"

**What people do:** `DELETE FROM orders WHERE id = ?` when admin cancels.

**Why it's wrong:** Stats are cumulative (revenue, units sold). Deleting an order creates a gap in the historical record. Also, "cancelled" is a valid business state.

**Do this instead:** Add `ORDER_STATUS_CANCELLED` (0). Set `status = 0` instead of deleting. Exclude cancelled from revenue/units-sold aggregates (`WHERE status >= SHIPPED` for units sold, `WHERE status NOT IN (CANCELLED)` for revenue if desired).

## Scalability Notes (v1.1 scope)

| Scale | Behavior | V1.1 Impact |
|-------|----------|-------------|
| 0-100 orders | SQL aggregates on `orders` table, single AdminUser writer | Stats queries are instant (<50ms). No caching needed. |
| 100-1000 orders | Pagination on order list (20/page). Stats still fast. | Phase C pagination handles it. Stats aggregation still sub-second. |
| 1000+ orders | Consider `SELECT ... INTO` cached summary, or index `status`/`created_at`. | Post-v1.1 concern. Add index on `orders(status, created_at)` if slow. |
| Concurrent admin writes | SQLite WAL allows one writer. Single admin = no contention in practice. | No change needed. busy_timeout=30s + retry in PITFALLS.md covers edge cases. |

## Sources

- Codebase inspection: `app/__init__.py` (create_app, config, extensions, blueprints), `app/models.py` (Product, ProductImage, AdminUser), `app/admin.py` (routes, before_request protection), `app/public.py` (product_detail, search, pagination), `app/forms.py` (Flask-WTF patterns), `app/templates/` (Jinja extends, csrf_token, wtf macro pattern).
- PROJECT.md v1.1 requirements: order form (tên, SĐT, địa chỉ, số lượng, ghi chú); cost price optional/admin-only; status flow (đã gói → đã gửi → đã nhận); stats (revenue, profit, order counts, products sold, inventory).
- STACK.md: Flask 3.1.3, Flask-SQLAlchemy 3.1.1, Flask-Login 0.6.3, Flask-WTF 1.3.0, SQLite WAL + busy_timeout=30s, no flask-migrate (deferred to schema churn).
- SQLite PRAGMA `table_info()` for idempotent column-existence check (standard SQLite 3.34+, already running 3.43.1 per PITFALLS.md).
- Werkzeug `generate_password_hash` / Flask-Login session model already proven in v1.0.

---
*Architecture research for: extending StoreWeb v1.0 (Flask product catalog) with order placement, order tracking, and stats dashboard (v1.1 Buy System)*
*Researched: 2026-08-02*
*Confidence: HIGH — grounded in codebase inspection and v1.0 patterns; schema-migration approach is the single LOW-confidence item (no flask-migrate yet for existing-DBs)*
