# Pitfalls Research — Adding Orders + Tracking + Stats to Existing Flask Storefront

**Domain:** Adding order placement (public form), order status tracking, optional cost price, and revenue/profit stats to an existing Flask + SQLite storefront (StoreWeb v1.1 Buy System)
**Researched:** 2026-08-02
**Confidence:** HIGH (verified against installed Flask 3.1.3, Flask-SQLAlchemy 3.1.1, SQLite 3.43.1, wtforms validators inspected in-environment; VN phone/address formats from ITU E.164 + Viettel/Vinaphone/Mobifone standards)

## Critical Pitfalls

### Pitfall 1: Blind `ALTER TABLE ADD COLUMN` Breaks Existing DBs

**What goes wrong:**
The existing `products` table has rows. Adding `cost_price INTEGER` via `ALTER TABLE products ADD COLUMN cost_price INTEGER` works, but the column is `NULL` for all existing rows. If the application immediately starts summing `SUM(price - cost_price)` for profit, every existing row produces `NULL` (because `100000 - NULL = NULL` in SQL), and `SUM` of that is `NULL` — the stats dashboard shows zero profit, and `SUM(price - cost_price)` silently returns `NULL` instead of the revenue contribution. Admin sees "0₫ lợi nhuận" and thinks the math is broken.

**Why it happens:**
- SQLite `ALTER TABLE ADD COLUMN` does not support defaults on nullable columns in older patterns — developers add the column, then the app code assumes it is never NULL.
- The existing `init_db` command uses `db.create_all()` (DDL CREATE only, no ALTER). There is **no migration infrastructure** (flask-migrate / Alembic not installed per requirements.txt) and **no schema-version table**.
- Cost price is "optional" so the column should be nullable, but the profit formula treats NULL as 0.

**How to avoid:**
1. Add the column with an explicit default: `ALTER TABLE products ADD COLUMN cost_price INTEGER DEFAULT 0` — existing rows get `0`, new NULL-safe.
2. In SQLAlchemy model, set `cost_price = db.Column(db.Integer, default=0, nullable=False, server_default='0')` — dual default (Python + DB) for safety.
3. In profit queries, defensively coalesce: `SUM(price - COALESCE(cost_price, 0))` or wrap in Python with `(p.price - (p.cost_price or 0))`.
4. Guard: if `cost_price` is 0 (unset), label profit as "chưa nhập giá nhập" rather than showing a misleading 0₫.

**Warning signs:**
- Stats dashboard shows `0₫` revenue/profit or `None` after schema change
- `SELECT SUM(price - cost_price) FROM products` returns NULL for old rows
- `flask init-db` still uses `create_all` with no ALTER path

**Phase to address:** Phase (Order + Cost) — schema migration step must handle existing rows with a default; stats phase must coalesce NULLs.

---

### Pitfall 2: Public Order Form Has No Bot Protection → Spam / Fake Orders

**What goes wrong:**
The order form is public (`/products/<id>` page) and requires no auth. No CSRF on public forms (CSRFProtect is enabled globally but only protects POST routes that use form.validate — a simple `<form>` POST without a CSRF token gets 400). Even with CSRF, a bot that fetches the page gets the token and can spam. Within hours of launch: hundreds of fake orders, SMS gateway spam if phone is sent externally, admin inbox flooded with garbage.

**Why it happens:**
- The existing app only has CSRF on admin forms (Flask-WTF `CSRFProtect` is global, but public pages currently have no forms). Adding a public form means CSRF is already on — good — but CSRF alone does not stop automated form fillers.
- No rate limiting on the public order endpoint. nginx rate-limits `/admin/` and `/login` but **not** the public product detail route (that's by design for browsing).
- No honeypot field, no CAPTCHA, no server-side throttle.

**How to avoid:**
1. **Honeypot field**: Add a hidden text field `website` (or `honeypot`) with CSS `display:none` and `tabindex=-1`. Bots fill it, humans don't. If non-empty on submit → silently reject (return 200 OK to not alert the bot).
2. **Server-side rate limit per IP**: Track `order_count` per IP in a short-window counter (in-memory dict with TTL, or sqlite `orders.created_at` count in last N minutes). Block > N orders from same IP in 1 hour. Do NOT make this a hard dependency — degrade gracefully if store restarts.
3. **CSRF token on public form**: `form.hidden_tag()` renders it. Must be present, otherwise Flask-WTF returns 400 before the honeypot even runs.
4. **Phone validation** (see Pitfall 5) — invalid phone is a cheap bot signal.

**Warning signs:**
- Orders table grows by 50+ rows in first hour after launch with no marketing
- `phone` field contains "12345678901234567890" or random strings
- `name` field contains "asdf" or HTML

**Phase to address:** Phase (Order Placement) — honeypot + rate limit are must-fix MVP before public launch. Do not ship public order form without at least honeypot.

---

### Pitfall 3: Profit Math Uses Float or Neglects NULL Cost Price

**What goes wrong:**
Developer stores `cost_price` as `Float` (e.g., `150000.50`). Profit = `SUM(price - cost_price)`. Due to IEEE 754, `950000 - 150000.50` yields `799999.4999999999` — displayed as `799,999.50₫` with a confusing half-dong fractional. Worse, if some products have `cost_price = NULL`, the subtraction yields NULL, and `SUM` of a set with any NULL is NULL — total profit collapses to 0 or NULL.

**Why it happens:**
- Price is already Integer VND (good, per existing convention). Developer "improves" cost_price to Float to support fractional cents — VND has no subunit; this is incorrect.
- SQLAlchemy `Float` type maps to SQLite `REAL` — binary floating point, exact same problem.
- `COALESCE` / `|| 0` not applied in queries or templates.

**How to avoid:**
1. **Store `cost_price` as `Integer`** — same as `price`. VND cost price is a whole number. If admin needs to enter `150,5`, that's a UX input formatting concern, not a storage concern — store `150500`.
2. **Coalesce in queries**: Always use `(Product.price - func.coalesce(Product.cost_price, 0))` in SQLAlchemy, or `((p.price - (p.cost_price or 0)) for p in products)` in Python.
3. **Template-level guard**: If `product.cost_price` is 0 or None, show `--` or "chưa nhập" instead of `0₫` in profit breakdown, so admin knows to enter cost.
4. **Use the existing `format_price` filter** — it already does `int(value)` and comma formatting. Never bypass it for cost-related display.

**Warning signs:**
- Profit displays as `799,999.50₫` or `799,999.4999999999₫`
- Stats dashboard shows `0₫` profit right after migration even though products have cost_price set
- `cost_price` column type is `Float` or `Numeric`

**Phase to address:** Phase (Stats) — integer math enforced; this is a must-fix for correct profit display. Also affects Phase (Cost Price) schema definition.

---

### Pitfall 4: SQLite Write Locks on Concurrent Order + Admin Saves → 500 Errors

**What goes wrong:**
Orders are submitted by public users (concurrent inserts on `orders` table). Admin simultaneously edits products or updates order status (concurrent writes on `products`/`orders`). SQLite only allows one writer at a time. Default `busy_timeout` in the app config is `timeout: 30` (30 seconds via SQLALCHEMY_ENGINE_OPTIONS), but the actual SQLite pragma observed on the running DB is `5000` (5 seconds) — a discrepancy. With 5s timeout and a write-heavy window, the second writer gets `sqlite3.OperationalError: database is locked` → HTTP 500.

**Why it happens:**
- SQLite is file-based; WAL mode separates readers from one writer, but **still only one writer at a time**.
- The existing `init_db` script sets `busy_timeout` at 5000ms via the SQLAlchemy `connect_args` — but the `create_app` in `__init__.py` sets `timeout: 30` (30 seconds). The **5000ms value is what's actually on the DB** (observed via `PRAGMA busy_timeout`), meaning the app-config value of 30 may not be taking effect for new connections, or the DB was initialized with a different config.
- No retry logic on writes.

**How to avoid:**
1. **Standardize busy_timeout**: Set `SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {'timeout': 30}}` in `create_app` and verify the pragma reads 30000 on new connections. The current 5000ms is too short under write contention.
2. **Retry on `OperationalError`**: Wrap order-create and order-status-update in a retry loop (3 attempts, 100ms backoff). This is the standard Flask-SQLAlchemy + SQLite pattern.
3. **Keep gunicorn workers low**: The deploy docs say `2×CPU+1` workers (e.g., 5). With 5 workers each having a separate SQLite connection, 5 concurrent writes is the realistic ceiling before lock contention. For a low-volume store this is fine, but the retry loop must exist.
4. **Batch order inserts**: Don't do multiple `db.session.commit()` calls per order. Insert order + decrement stock in a single commit.

**Warning signs:**
- HTTP 500 on order submission during a traffic spike
- `sqlite3.OperationalError: database is locked` in gunicorn logs
- Admin gets 500 when updating order status at the same time a customer submits an order

**Phase to address:** Phase (Order Placement + Status Tracking) — retry wrapper on all writes is must-have. busy_timeout mismatch should be resolved in Phase 1 (Deployment) config.

---

### Pitfall 5: Phone Number and Address Validation Too Loose or Too Strict for VN

**What goes wrong:**
Developer applies a generic `Regexp` validator. Two failure modes:
- **Too loose**: `+84901234567` passes but so does `123456789` or `abcd1234` — admin can't call the customer.
- **Too strict**: Validator rejects `+84 90 123 4567` or `09012345678` (with country code variants) — legitimate customers get blocked, abandon checkout, email admin complaining "form broken."
Address is free-text and a bot can stuff it with 10KB of garbage, breaking the admin UI.

**Why it happens:**
- VN phone numbers: 10-11 digits. Mobile prefixes: 09x, 08x, 03x, 05x, 07x, 08x (Viettel, MobiFone, Vinaphone, Vietnamobile, Gmobile, ITel). With country code: `+84` replaces leading `0` → `+84901234567` (11 digits after +84). Landline: 10 digits city code (024 Hanoi, 028 Ho Chi Minh) or 11 digits provincial (029xxxxxxx).
- Regex must accept: `0901234567`, `090 123 4567`, `+84901234567`, `+84 90 123 4567`, `035 1234 5678`. Must reject: `123`, `+1234567890`, `abcdefghij`.
- Address has no standard format — it's free text. Length must be capped.

**How to avoid:**
1. **Phone**: Strip spaces/dashes, then validate the normalized string. Pattern: `^(0[3-9]\d{8}|02\d{8,9}|\+84[3-9]\d{7,8}|\+842\d{8,9})$` after removing spaces. Accept `0` prefix OR `+84` but not both. Display what the user typed in the admin panel (don't reformat — they may have typed a specific format).
2. **Address**: `StringField` with `Length(min=10, max=500)`. 10 chars minimum to reject garbage like "a" — but not too tight, rural addresses can be long.
3. **Name**: `Length(min=2, max=100)` — reject 1-character names, allow 2-char names (single-word surnames like "Minh" are fine, but "M" alone is not a real name).
4. **Note field**: `Length(max=2000)` — cap to prevent multi-KB bot spam.

**Warning signs:**
- Order form accepts phone = "123" or rejects "+84 90 123 4567"
- Address field contains 50KB of HTML from a bot
- Admin calls a phone number from an order and it's disconnected because the number was malformed

**Phase to address:** Phase (Order Placement) — phone/address validators are must-fix. Test with real VN number formats.

---

### Pitfall 6: Order Status Flow Allows Invalid Transitions (Skipped Steps, Regressions)

**What goes wrong:**
Admin updates status directly via a dropdown `<select>` with all 3 options. A careless click sets `delivered` on an order that was never `shipped` — or worse, sets `available` back to `packed` after delivery. The stats count "delivered" orders as revenue even though the package never reached the customer.

**Why it happens:**
- The status field is just an `Enum` or `String` column with no enforcement of sequential flow.
- The form renders all statuses as selectable options.
- No state machine constraint on transitions.

**How to avoid:**
1. **Model-level transition guard**: Define valid transitions explicitly:
   ```python
   VALID_TRANSITIONS = {
       'pending': {'packed', 'cancelled'},      # placed → packed (or cancelled by admin)
       'packed': {'shipped', 'cancelled'},       # packed → shipped
       'shipped': {'delivered', 'returned'},     # shipped → delivered
       'delivered': set(),                        # terminal
       'cancelled': set(),                        # terminal
   }
   ```
   Before updating, check `new_status in VALID_TRANSITIONS.get(current_status, set())`. If not → flash error, don't save.
2. **Form-level**: Only render valid next statuses in the dropdown. If current is `packed`, show `shipped` and `cancelled` only — don't render `delivered` or `pending`.
3. **Add `cancelled` status** — don't rely on "delete" for order cancellation. Deleted orders are invisible in stats; cancelled orders preserve the audit trail (order was placed, then cancelled). This is critical for honest revenue reporting.
4. **Timestamp each transition**: `packed_at`, `shipped_at`, `delivered_at` columns — not a single `updated_at`. Stats need "orders shipped this week" not "orders touched this week."

**Warning signs:**
- An order jumps from `pending` to `delivered` in the admin panel (no ship step)
- Admin can set an order back to `pending` after marking `shipped`
- Stats count cancelled orders as revenue

**Phase to address:** Phase (Order Tracking) — state machine is must-fix. Must include `cancelled` as a non-revenue state.

---

### Pitfall 7: Stats Count Pending/Cancelled Orders as Revenue

**What goes wrong:**
Admin sees "15,000,000₫ doanh thu" on the stats dashboard and plans inventory re-order based on that number. In reality, 4 of those 15 orders are still `pending` (never paid for, never shipped), and 2 are `cancelled`. Real revenue is 9 orders = 9,000,000₫. Inventory is overstated, cash flow is worse than expected.

**Why it happens:**
- `SUM(price * quantity)` over ALL orders in the table, without filtering by status.
- "Doanh thu" (revenue) is conflated with "orders placed." In e-commerce, revenue is recognized at shipment (or delivery), not at order placement.
- No distinction between gross (all orders) and net (completed-only) metrics.

**How to avoid:**
1. **Define revenue precisely**: Revenue = `SUM(price * quantity)` WHERE `status IN ('shipped', 'delivered')`. Only shipped orders have left the warehouse with intent to be paid on delivery (COD model). Pending/cancelled orders are not revenue.
2. **Show both metrics**: "Tạm tính: X₫" (all orders) and "Doanh thu thực tế: Y₫" (shipped/delivered only). Admin needs both to spot the pipeline.
3. **Profit = (revenue) - (cost of shipped items)**: `SUM((price - cost_price) * quantity) WHERE status IN ('shipped', 'delivered')`. Cost of `pending` orders is inventory, not expense.
4. **Products sold** = `SUM(quantity) WHERE status IN ('shipped', 'delivered')` — not pending.
5. **Inventory impact**: Only `delivered` orders should decrement stock in a strict model, but for a small store, `shipped` is the practical point. Document this decision — it's a business rule, not a technical one. Make it consistent.

**Warning signs:**
- Stats show revenue higher than actual cash in hand
- "Products sold" count includes pending orders that never shipped
- No distinction between "orders placed" and "orders completed" in the UI

**Phase to address:** Phase (Stats Dashboard) — revenue definition is must-fix. Ship the dashboard with status-filtered queries; flag this explicitly in the UI.

---

### Pitfall 8: Cost Price Visible to Public / Not Properly Hidden

**What goes wrong:**
`cost_price` is an optional field on `ProductForm` in `form.html`. A careless template edit renders `{{ product.cost_price | format_price }}` on the public product detail page or includes it in a JSON API. Competitors scrape the page, see "I bought this at 80,000₫, selling at 150,000₫" — margin leakage.

**Why it happens:**
- `cost_price` is a model column on the same `Product` object the public template receives. Jinja2 renders any attribute.
- No template review catches the leak.
- If a future JSON API endpoint is added, `Product.to_dict()` or `schema.dump(product)` includes all columns by default.

**How to avoid:**
1. **Template discipline**: `cost_price` NEVER appears in any public template. Audit: grep `cost_price` in `templates/public/`.
2. **Property access, not column**: Make `cost_price` a column but access it only via `current_user.is_authenticated` guard in admin templates — not a technical guard, but a code review checkpoint.
3. **Exclude from JSON**: If serializing products, explicitly list fields: `product.to_dict(fields=['id', 'name', 'price', ...])` — never `vars(product)` or automatic schema dumping.

**Warning signs:**
- Public product detail page shows "Giá nhập: 80,000₫"
- API endpoint returns cost_price in JSON
- Admin form has cost_price visible to non-admin (shouldn't happen with existing `@login_required` on admin routes, but the field must not leak to public templates)

**Phase to address:** Phase (Cost Price) + Phase (Order Placement public form) — must audit templates. Must-fix before cost_price is added.

---

## Moderate Pitfalls

### Pitfall 9: Stock Decrement on Pending Order Blocks Real Sales

**What goes wrong:**
Order is placed (status `pending`). Code immediately does `product.quantity -= order.quantity` and commits. A bot spammed 50 fake orders — product stock shows 0, real customer sees "Hết hàng" and leaves. Admin cancels the fake orders, restocks — but during the window, real sales were lost.

**Why it happens:**
- Stock decrement is tied to order creation, not order confirmation (`shipped`).
- No way to distinguish "reserved" inventory from "sold" inventory.

**How to avoid:**
1. **Do NOT decrement stock on order placement**. Decrement on `shipped` status transition (the point where the package leaves the warehouse). This is the standard e-commerce model.
2. If admin wants "reserved" stock (order placed but not shipped), add a `reserved_quantity` column — but for a solo seller MVP, just document: "Tồn kho giảm khi đơn hàng được gửi, không giảm khi đặt."
3. If stock reaches 0 during a `pending` window, the product shows "hết hàng" — but the admin can still see the pending order and manually restock if needed.

**Warning signs:**
- Product shows "Hết hàng" but admin dashboard shows the product has no `shipped` orders
- Real customer abandons checkout because "Hết hàng" but the item is physically still in stock

**Phase to address:** Phase (Order Placement + Stock) — stock decrement timing is must-fix for MVP correctness. Ship with "decrement on shipped" and document.

---

### Pitfall 10: Orders Table Schema Not Versioned — `init-db` Won't Migrate Existing DBs

**What goes wrong:**
The existing `init_db` command uses `db.create_all()`. It creates tables that don't exist — but it does NOT add columns to existing tables, and it does NOT create the `orders` table if the DB was already initialized in v1.0. New code queries `Order.query` → `sqlalchemy.exc.OperationalError: no such table: orders`. Crash on first order submission.

**Why it happens:**
- `db.create_all()` is DDL-only `CREATE TABLE IF NOT EXISTS`. It never alters existing tables.
- There is no `flask-migrate` / Alembic in requirements.txt. The CLAUDE.md explicitly says: "Skip flask-migrate; use db.create_all(). Add migrations only when the model gains columns/tables." — but now the model IS gaining tables, and the guidance is to use raw ALTER.
- No `schema_version` table or migration tracking.

**How to avoid:**
1. **Manual migration script via Flask CLI**: Create a `flask migrate-orders` command that:
   - Checks `PRAGMA table_info(orders)` — if table exists, skip. If not, `CREATE TABLE orders (...)`.
   - Checks `PRAGMA table_info(products)` — if `cost_price` column missing, `ALTER TABLE products ADD COLUMN cost_price INTEGER DEFAULT 0`.
   - Idempotent — safe to run twice.
2. **Document the migration step**: In the deploy docs, add "After deploying v1.1, run `flask migrate-orders` before starting the app." Like the existing `init-db` step.
3. **Do NOT add flask-migrate / Alembic**: The project explicitly chose not to. Use raw SQL via `db.engine` for the two specific schema changes. This is consistent with the project's minimalist stack philosophy.

**Warning signs:**
- `flask init-db` does not create `orders` table (it only knows about Product/ProductImage/AdminUser from models.py at that point)
- New `Order` model in models.py but `db.create_all()` called before the model was defined — table never created
- Existing DB has `products` table without `cost_price` — app crashes on product create/edit

**Phase to address:** Phase (Order Placement) setup — must-fix. The migration command must run before any new feature is used.

---

### Pitfall 11: No Audit Trail on Order Status Changes — "Who shipped this?"

**What goes wrong:**
Admin A marks order #12 "shipped." Two days later the customer says "I never got it." Admin checks: order shows `shipped` but no record of when, by whom, or the tracking number. Did Admin A actually ship it? Did the carrier lose it? No paper trail.

**Why it happens:**
- `orders` table has only `status` and `updated_at` columns. No `status_history`, no `updated_by`, no `tracking_number`, no `note`.

**How to avoid:**
1. **Add `status_history` as a simple JSON field or separate table**: For MVP, add `tracking_number VARCHAR(100)` and `note TEXT` to the `orders` table. Do NOT over-engineer with a separate history table — the existing product model is flat and simple.
2. **Record `updated_by`** on the admin order-update form — even a single admin, log "by admin" for accountability.
3. **Do NOT** build a full audit log table. That's premature. A `note` field + `tracking_number` field on orders covers 90% of the need.

**Warning signs:**
- Order detail shows "shipped" but admin can't recall when or by whom
- No tracking number field in the order status update form
- Admin asks "was this order shipped or just marked shipped?"

**Phase to address:** Phase (Order Tracking) — tracking_number + note fields are must-fix. Full audit trail is nice-to-have for later.

---

### Pitfall 12: Stats Dashboard Slow Query — `SUM(price * quantity) JOIN` on Large Order Sets

**What goes wrong:**
With 5 tables (products, orders, order items), the stats query does a 4-way JOIN with `SUM` over 10,000+ rows. The page takes 3-5 seconds to load. Admin clicks "Thống kê" → waits → thinks the app crashed → refreshes → 5 more slow queries.

**Why it happens:**
- No pre-aggregation. Each dashboard load recalculates everything from raw rows.
- No indexes on `orders.status`, `orders.created_at`, `order_items.order_id`.
- JOIN on unindexed foreign keys.

**How to avoid:**
1. **Add indexes**: `CREATE INDEX idx_orders_status ON orders(status)`, `idx_orders_created ON orders(created_at)`, `idx_order_items_order_id ON order_items(order_id)`.
2. **Materialize daily summary**: For a solo seller, this is overkill. But a simple trick: cache the stats query result for 60 seconds using Flask's `cache` or even an in-memory `functools.lru_cache` with a timer. The admin doesn't need real-time stats — they need today's numbers, refreshed on each page visit.
3. **Paginate order list**: Don't load all 10,000 orders into the template. Use `Order.query.paginate()` — the existing `public.py` and `admin.py` product lists already paginate; follow the same pattern.

**Warning signs:**
- Stats dashboard takes >2 seconds to load with 1000+ orders
- Admin refreshes repeatedly, generating 5x load

**Phase to address:** Phase (Stats Dashboard) — indexes are must-fix; caching is nice-to-have for when orders > 1000.

---

## Minor Pitfalls

### Pitfall 13: Quantity Field Accepts 0 or Negative → Free Orders / Phantom Stock

**What goes wrong:**
Order form's `quantity` field accepts `0` (free order — admin ships nothing for nothing) or `-5` (admin stock increases by 5 on fulfillment). `Integer(min=1)` is forgotten; `IntegerField` without `NumberRange(min=1)` accepts any integer.

**How to avoid:** `IntegerField('Số lượng', validators=[NumberRange(min=1, max=999)])` — max prevents a bot submitting quantity=999999 to exhaust stock.

### Pitfall 14: Order Confirmation Email / SMS Not Sent — Admin Forgets Orders

**What goes wrong:**
No notification when an order is placed. Admin doesn't notice new orders for days. Customer calls angry.

**How to avoid:** For MVP, skip email/SMS. Add an admin notification badge on the dashboard: "Bạn có 3 đơn hàng mới." Use the existing `flash` or a `unread_orders` count. Phone/call is the existing fallback (Messenger link was the old flow).

### Pitfall 15: Order Detail Page Exposes Other Orders (IDOR)

**What goes wrong:**
Public order confirmation is at `/order/<id>` — but `id` is sequential. Customer A submits order #123, shares the link. Customer B guesses #124, #125 and sees other people's orders.

**How to prevent:** For MVP, do NOT have a public order lookup page. After order submission, show a thank-you page with `order_id` and `order_code` (a random token). If a public lookup is needed, require the phone number + order code to view. This is a future enhancement — document it as out of scope for MVP.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Must-Fix / Nice-to-Have | Mitigation |
|-------------|----------------|-------------------------|------------|
| Phase (Schema Migration) | `ALTER TABLE` + existing DB: cost_price NULL → profit math collapses | MUST-FIX | Add with `DEFAULT 0` + `COALESCE` in all profit queries |
| Phase (Order Placement) | Public form spam: no honeypot, no rate limit | MUST-FIX | Honeypot field + IP counter; reject silently |
| Phase (Order Placement) | Phone/address validation too loose/stricter | MUST-FIX | Strip + regex VN phone; Length cap on address |
| Phase (Order Placement) | Stock decrement on `pending`, not `shipped` | MUST-FIX | Document: decrement on `shipped` only; do not touch quantity on order create |
| Phase (Order Tracking) | Status dropdown allows invalid transitions (pending → delivered) | MUST-FIX | Model-level `VALID_TRANSITIONS` dict + form renders only valid next statuses |
| Phase (Order Tracking) | No `cancelled` status → deleted orders invisible in stats | MUST-FIX | Add `cancelled` as a status; exclude from revenue/profit/shipped counts |
| Phase (Order Tracking) | No tracking number / note / who-updated | NICE-TO-HAVE | Add `tracking_number` + `note` columns; `updated_by` logged |
| Phase (Stats Dashboard) | `SUM(price * quantity)` counts pending/cancelled as revenue | MUST-FIX | Filter WHERE `status IN ('shipped','delivered')` for revenue; show gross vs net |
| Phase (Stats Dashboard) | Profit SUM collapses on NULL cost_price | MUST-FIX | `COALESCE(cost_price, 0)` in every profit query |
| Phase (Stats Dashboard) | Slow query on 10k+ orders | NICE-TO-HAVE (at scale) | Index `status`, `created_at`; cache result 60s; paginate |
| Phase (Cost Price) | cost_price leaks to public template | MUST-FIX | Grep `cost_price` in `templates/public/` — must be zero matches |
| Phase (Cost Price) | cost_price stored as Float | MUST-FIX | Store as Integer; reuse `format_price` filter |
| Phase (Deployment) | SQLite busy_timeout mismatch (30s config vs 5s pragma) | MUST-FIX | Verify `PRAGMA busy_timeout` reads 30000 after app config change |
| Phase (Deployment) | No retry on `database is locked` | MUST-FIX | Wrap all order writes + status updates in retry(3, backoff=100ms) |

## Sources

- SQLite 3.43.1 verified in-environment: `PRAGMA journal_mode=WAL`, `PRAGMA busy_timeout=5000` (observed discrepancy with app config `timeout=30`) — WAL allows concurrent readers + 1 writer; writes still block.
- Flask 3.1.3 + Flask-SQLAlchemy 3.1.1: `db.create_all()` is DDL-only `CREATE TABLE IF NOT EXISTS` — does NOT alter existing tables or add columns. Verified against `__init__.py` and `db.py` in this codebase.
- wtforms 3.2.2 validators verified in-environment: `NumberRange(min=1, max=999)`, `Length(min=10, max=500)`, `Regexp` all available. `Optional()` validator exists for nullable fields.
- VN phone number format: ITU-T E.164 standard. Mobile prefixes: 03x (Viettel), 05x (Vietnamobile/Vinaphone), 07x (Gmobile/Mobifone), 08x (Zing/Vinaphone/Mobifone), 09x (legacy). Landline: 02x + 8-9 digits. With `+84` country code, leading `0` is dropped.
- Existing codebase verified: `CSRFProtect` is global in `create_app`, so public form POST without CSRF token returns 400 — public order form must include `{{ form.hidden_tag() }}`.
- Existing `__init__.py` sets `SQLALCHEMY_ENGINE_OPTIONS={'connect_args': {'timeout': 30}}` — this SHOULD yield 30000ms busy_timeout, but DB shows 5000ms. This is the discrepancy to investigate.
- Existing `models.py`: `price = db.Column(db.Integer)` — correct pattern for VND. `cost_price` must follow the same.
- Existing `public.py`: `product.status` is a `@property` computed from `discontinued` + `quantity > 0` — not a DB column. Order status should be a real DB column with a transition guard, not a computed property.
- VND has no subunit (zero dong coins were demonetized). Storing monetary values as Integer is correct — no Float/Numeric needed.
- Existing deploy docs (Linux.md, nginx.conf): nginx rate-limits `/admin/` and `/login` at `10r/m` per IP. The public product detail page is NOT rate-limited by design (browsing). Order submission on the same URL inherits no rate limit — must be handled in-app.

---

*Pitfalls research for: Adding order placement (public form), order status tracking (packed→shipped→delivered), optional cost price, and revenue/profit stats to existing Flask + SQLite storefront (StoreWeb v1.1 Buy System)*
*Researched: 2026-08-02*
