# Phase 8: Admin Stats — Research

**Researched:** 2026-08-03
**Domain:** SQLAlchemy 2.0 aggregation over Order/OrderItem/Product; Jinja server-rendered stats dashboard
**Confidence:** HIGH

## Summary

Phase 8 adds a single read-only admin route `GET /admin/stats` (`admin.stats()`) that computes revenue + profit (NULL-safe), units sold, orders-by-status counts, and inventory counts, rendered into one new template `admin/stats.html`. **No new dependencies** — every aggregate is a standard SQLAlchemy 2.0 legacy-Query expression over the existing `Order` / `OrderItem` / `Product` models, money uses the existing `format_price` Jinja filter, statuses use the existing `ORDER_STATUSES` / `order_badge_class` globals, and the page reuses the `.admin-card--wide` + `.badge-order-*` CSS system.

The critical design facts verified by executing the exact query patterns against a temp SQLite DB with the real models (SQLAlchemy 2.0.51): (1) `SUM()` over an empty qualifying set returns SQLite `NULL`, so **`db.func.coalesce(..., 0)` is load-bearing** — without it the empty-DB page crashes rendering `None | format_price`; (2) the Phase 7 `group_by(Order.status)` pattern **omits statuses with zero orders** (e.g. `Đã gói` absent when no such orders exist), so the template must use `status_counts.get(status, 0)` — the UI-SPEC already does this; (3) `profit` must be a separate query with `OrderItem.product_cost_price.isnot(None)` and a companion `count()` to drive the conditional NULL-safe note. All three are verified working in the throwaway script `.planning/tmp/verify_08_stats_queries.py`.

**Primary recommendation:** Implement `admin.stats()` as 6 simple, separate aggregate queries (no combined mega-join, no `select()` rewrite) — the dataset is single-admin / SQLite / low-volume, and matching the codebase's established `db.session.query(...)` style keeps the diff minimal and consistent with Phase 7.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Doanh thu & Lợi nhuận (STAT-01, STAT-02)
- **Trạng thái tính doanh thu**: chỉ đơn `Đã gửi` + `Đã nhận` (đã lock từ SC — không bao gồm Chờ xác nhận/Đã gói/Đã hủy).
- **Revenue** = `sum(order_items.product_price * quantity)` trên các OrderItem của đơn có status ∈ {Đã gửi, Đã nhận}.
- **Profit NULL-safe**: loại item có `product_cost_price IS NULL` khỏi lợi nhuận (không coi là 0 — tránh overstate). Hiện note: "Lợi nhuận tính trên N sản phẩm có giá nhập" khi có item bị loại. Profit = `sum((product_price - product_cost_price) * quantity)` trên items còn lại.
- **Phạm vi thời gian**: toàn thời gian (STAT-05 lọc theo ngày → v2 deferred).
- **"Đã hủy" không tính vào doanh thu/lợi nhuận** — chỉ hiện trong breakdown trạng thái.
- **Units sold** (sản phẩm đã bán) = `sum(quantity)` trên items của đơn Đã gửi + Đã nhận — nhất quán với revenue.

#### Đơn hàng theo trạng thái (STAT-03)
- Breakdown cả **5 trạng thái** (Chờ xác nhận, Đã gói, Đã gửi, Đã nhận, Đã hủy) + tổng số đơn (gồm cả Đã hủy).
- Mỗi status **click được** → link sang `/admin/orders?status=<label>` (filter pattern đã có sẵn Phase 7).
- Tổng đơn = đếm tất cả order (mọi trạng thái).

#### Tồn kho (STAT-04)
- **Tổng sản phẩm** = đếm tất cả Product (kể cả discontinued).
- **Hết hàng** = `quantity = 0` VÀ không discontinued (tách riêng khỏi ngừng bán).
- **Ngừng bán** = `discontinued = True`.
- **Còn hàng** = `quantity > 0` VÀ không discontinued (thêm ngoài SC — đủ 3 phân khúc rõ ràng).

#### UI & Vị trí
- Route mới `GET /admin/stats` → `admin.stats()` — KHÔNG nhúng vào dashboard.
- Nav admin (dashboard.html): thêm mục **"Thống kê"** (pattern giống mục "Đơn hàng").
- **Server-rendered tĩnh khi load** — không JS polling, 0 dependency mới.
- Layout: grid thẻ số liệu theo nhóm (Doanh thu/Lợi nhuận, Đơn hàng, Kho) — tái dùng `admin-card` CSS sẵn có.
- **Empty state**: hiện số 0 rõ ràng (₫0, 0 đơn) + label, không để trống, không báo lỗi.
- Định dạng tiền: dùng `format_price` helper đã có (hiển thị VND).

### Claude's Discretion
Không có — user đã chốt đủ 4 area.

### Deferred Ideas (OUT OF SCOPE)
- Lọc theo khoảng ngày (STAT-05 → v2)
- Export CSV (STAT-06 → v2)
- Bảng lợi nhuận theo từng sản phẩm (STAT-07 → v2)
- Auto-refresh dữ liệu (không cần — server-rendered tĩnh)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| STAT-01 | Admin xem tổng doanh thu (chỉ tính đơn Đã gửi + Đã nhận) | Revenue = `coalesce(sum(product_price * quantity), 0)` over `OrderItem ⋈ Order` filtered `Order.status.in_(('Đã gửi','Đã nhận'))` — **verified** by execution. Coalesce is required (empty set → NULL → crash in `format_price`). |
| STAT-02 | Admin xem lợi nhuận = doanh thu − giá nhập (đơn đã gửi/nhận, xử lý NULL) | Profit = separate query adding `OrderItem.product_cost_price.isnot(None)`; companion `count(OrderItem.id)` drives the conditional note `"Lợi nhuận tính trên {N} sản phẩm có giá nhập."` when `total_qualifying_items - profit_items > 0` — **verified**. |
| STAT-03 | Admin xem số đơn theo trạng thái + tổng sản phẩm đã bán | Reuse Phase 7 `dict(db.session.query(Order.status, count(Order.id)).group_by(Order.status).all())`; `total_orders = sum(values)`. Units sold rides the same revenue query (`sum(quantity)`). **verified** that zero-count statuses are omitted → template must `.get(s, 0)`. |
| STAT-04 | Admin xem số sản phẩm trong kho (tổng, hết hàng, ngừng bán) | `Product.query.count()` (all); `in_stock = filter(quantity > 0, discontinued.is_(False))`; `out_of_stock = filter(quantity == 0, discontinued.is_(False))`; `discontinued = filter(discontinued.is_(True))` — **verified**. |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

Directives that constrain the Phase 8 plan (from `./CLAUDE.md`):

- **Tech stack is locked**: Python Flask; server-rendered Jinja2; SQLite. No new frameworks.
- **Language**: Vietnamese-only UI (`lang="vi"`, all copy VN — PLAT-01).
- **Money = Integer VND only** (D-05, never Float) — all aggregates stay int; `format_price` renders `1.200.000₫`.
- **No heavy deps**: "What NOT to Use" bans Tailwind/Bootstrap/React/Vue/shadcn/Flask-Admin/passlib/Redis/Celery. Phase 8 adds **no dependencies** — aggregation via SQLAlchemy, plain CSS.
- **No JS**: catalog is server-rendered HTML; Phase 8 is GET-only, zero JS, zero polling.
- **Self-hosted deploy**: no new runtime/services introduced.
- **GSD workflow**: file edits flow through `/gsd-execute-phase`; research/plans live in `.planning/phases/08-admin-stats/`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Revenue / profit / units aggregation | API / Backend | Database | SQL aggregates over `OrderItem ⋈ Order` — server computes from stored snapshots; SQLite owns the data |
| Orders-by-status counts | API / Backend | — | `GROUP BY Order.status` — identical to the Phase 7 `admin.orders()` pattern |
| Inventory counts | API / Backend | — | `COUNT` predicates over `Product.quantity` / `Product.discontinued` |
| Stats page rendering (SSR) | API / Backend (Jinja) | — | `admin.stats()` renders `stats.html` server-side; no client data fetching |
| Stat-card grid / breakdown styling | Browser (CSS) | — | New `.stats-group` / `.stat-card` / `.status-breakdown` classes in `style.css` |
| "Thống kê" nav link | Browser (HTML) | — | One `.nav-group` block added to dashboard nav-list; reuses existing `.nav-group` |
| Drill-down to filtered orders | API / Backend | Browser | Breakdown rows link `url_for('admin.orders', status=<label>)` — Phase 7 route already handles the param |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| SQLAlchemy 2.0 (via Flask-SQLAlchemy 3.1.1) | 2.0.51 | Aggregate queries (`db.session.query`, `db.func.sum/count/coalesce`, `.join`, `.in_`, `.scalar/.one`) | Already installed (verified `sqlalchemy 2.0.51`); legacy Query API is the codebase's established style (`admin.py:134`, `public.py`) |
| Flask | 3.1.3 | Route `admin.stats()` on existing `admin_bp` | Already installed; `@admin_bp.before_request @login_required _protect_admin` already protects every admin route |
| Jinja2 (bundled) | 3.1.x | `stats.html` extends `base.html`; `format_price` filter + `order_badge_class` global | Already installed; both helpers already registered app-wide (`__init__.py:64`, `admin.py:31`) |
| Plain CSS | — | `.stats-group`, `.stat-card`, `.status-breakdown`, `.badge-neutral` | Project explicitly bans CSS frameworks; ~70–90 new lines in `style.css` (UI-SPEC) |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `db.func.coalesce` | (SQLAlchemy) | Wrap every `SUM` so empty qualifying set returns `0` not `NULL` | **Always** — this is the empty-state correctness guarantee (verified: empty set → `0`, else `None` → template crash) |
| `db.func.count` | (SQLAlchemy) | `profit_items` count (drives NULL-safe note) and status `group_by` | Always for the note + status breakdown |
| `_order_total` / `order_badge_class` / `ORDER_STATUSES` | (existing, `app/admin.py`) | Status badge class + status constant reuse | Template uses `order_badge_class(...)` directly (it is a Jinja global); `ORDER_STATUSES` not needed in template (5 rows hardcoded per UI-SPEC) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| 6 separate simple queries | One combined `JOIN` + `CASE WHEN` mega-query | Separate queries are readable, match codebase style, and SQLite + single-admin dataset make the perf difference nil; combined query is fragile to extend |
| Legacy `db.session.query(...)` | SQLAlchemy 2.0 `select()` core API | Codebase uses legacy Query API everywhere (`admin.py:134`); switching styles mid-project adds churn with zero benefit at this size |
| Compute profit in Python (iterate `order.items`) | SQL aggregate | Python iteration would N+1 the lazy `Order.items` and drift from the snapshot-consistent SQL aggregate; SQL is the single source of truth |

**Installation:** None. Zero new packages in this phase (UI-SPEC "Registry Safety" and CLAUDE.md constraints).

**Version verification (verified this session):** Flask 3.1.3, Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.0.51, Python 3.11.8 (`pip` import check), waitress 3.0.2. All already in `requirements.txt`.

## Package Legitimacy Audit

No external packages are installed in this phase — aggregation uses the already-installed SQLAlchemy/Flask, money uses the existing `format_price` filter, styling is hand-written CSS, and one literal hex value (`#B45309`) is added to `style.css`. The Package Legitimacy Gate is **not applicable** (no installs; slopcheck N/A).

| Package | Registry | Disposition |
|---------|----------|-------------|
| (none) | — | No installs in Phase 8 |

## Architecture Patterns

### System Architecture Diagram

```
GET /admin/stats  (admin_bp, @before_request → @login_required via _protect_admin)
   │
   ▼
admin.stats()  ──┬── Q1: revenue + units_sold ── db.func.sum(product_price*quantity), sum(quantity)
                 │         JOIN order_items ⋈ orders ON order_id, FILTER orders.status IN ('Đã gửi','Đã nhận')
                 ├── Q2: profit + profit_items ── sum((price-cost)*qty), count(id)
                 │         same JOIN/FILTER AND order_items.product_cost_price IS NOT NULL
                 ├── Q3: total_qualifying_items ── count(id), same JOIN/FILTER  → profit_note = (Q3 − Q2_count > 0)
                 ├── Q4: status_counts ── SELECT orders.status, count(id) GROUP BY status   (Phase 7 pattern)
                 │         total_orders = sum(status_counts.values())
                 └── Q5: inventory ── total_products | in_stock(qty>0, ¬disc) | out_of_stock(qty=0, ¬disc) | discontinued(disc=TRUE)
   │
   ▼
context dict → render_template('admin/stats.html')
   │
   ▼
[.admin-page] > [.admin-header h1 "Thống kê"]
  [.admin-card.admin-card--wide]
    ├ [section.stats-group] Doanh thu & Lợi nhuận  → 3 .stat-card (revenue | format_price, profit, units_sold)
    ├ [section.stats-group] Đơn hàng               → .stat-card "Tổng số đơn" + ul.status-breakdown (6 links)
    └ [section.stats-group] Kho                    → 4 .stat-card (tổng, còn hàng, hết hàng, ngừng bán)
   │
   ▼ (breakdown row click)
/admin/orders?status=<VN label>  → Phase 7 admin.orders() applies existing whitelist filter
```

**Data-flow trace (primary use case):** admin clicks "Thống kê" nav → `admin.stats()` runs 6 aggregate queries against `app.db` → server builds the context dict → `stats.html` renders VN stat cards → admin clicks a status row → `url_for('admin.orders', status='Đã gửi')` → Phase 7 filter page. No client JS, no POST, no CSRF involved.

### Recommended Project Structure (files touched)

```
app/
├── admin.py                              # + REVENUE_STATUSES const + admin.stats() route
├── templates/admin/stats.html            # NEW — 3 stats-group sections
├── templates/admin/dashboard.html        # + "Thống kê" nav-group (no badge)
└── static/css/style.css                  # + .stats-group/.stats-group-title/.stats-grid/.stat-card/
                                          #   .stat-label/.stat-value/.stat-value--display/.stat-hint/
                                          #   .stat-note/.status-breakdown/.badge-neutral (~70–90 lines)
```

### Pattern 1: NULL-safe aggregate with `coalesce` (the load-bearing detail)

**What:** Every `SUM` over a filtered join must be wrapped in `db.func.coalesce(..., 0)`.
**Why verified:** Executed against a temp DB — a qualifying set with zero rows returns SQLite `NULL`, and the template's `{{ revenue | format_price }}` calls `int(value)` in the filter (`__init__.py:66`), which would raise `TypeError` on `None`. `coalesce` turns the empty-DB page into a clean `0₫`.
**Example (verified):** see Code Examples below.

### Pattern 2: Orders-by-status — reuse the Phase 7 group_by exactly

**What:** `dict(db.session.query(Order.status, db.func.count(Order.id)).group_by(Order.status).all())` — the same expression already in `admin.orders()` (`admin.py:133-135`). `total_orders = sum(status_counts.values())`.
**Verified caveat:** statuses with zero orders are **absent** from the dict (my temp-DB run produced `{'Chờ xác nhận':1,'Đã gửi':1,'Đã hủy':1,'Đã nhận':1}` with `Đã gói` missing). The template MUST read `status_counts.get(status, 0)` — the UI-SPEC markup already does exactly this.

### Pattern 3: NULL-safe profit note is derived, not stored

**What:** Profit query returns `(profit, profit_items)` where `profit_items = count(id)` over cost-bearing items. A third scalar query counts total qualifying items. `excluded = total_qualifying_items - profit_items`. Note renders **only** when `excluded > 0`, copy `"Lợi nhuận tính trên {profit_items} sản phẩm có giá nhập."` (UI-SPEC copy contract). When zero qualifying orders exist, `excluded == 0` → note absent (matches "never shows in zero case").

### Anti-Patterns to Avoid

- **Omitting `coalesce` on a `SUM`**: empty DB → `None` → `format_price` raises `TypeError` → 500. Every `SUM` gets `coalesce(..., 0)`.
- **Reading zero-count statuses with `status_counts['Đã gói']`**: KeyError on real data. Always `.get(s, 0)`.
- **Iterating `order.items` in Python to total revenue**: N+1 over `lazy='dynamic'`; SQL aggregate is the snapshot-consistent single source of truth (same decision as `_order_total`).
- **Filtering booleans with `== True` / `== False`**: use `Product.discontinued.is_(True)` / `.is_(False)` — the explicit SQLAlchemy boolean predicate (verified on SQLite).
- **Adding JS/polling or a chart library**: locked out — server-rendered static page, zero JS (CONTEXT.md + UI-SPEC).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Total revenue/profit/units | Python loops over `Order.items` (N+1 on `lazy='dynamic'`) | `db.func.sum`/`count`/`coalesce` + `join` | SQL aggregate over snapshot columns is exact and one round-trip; matches `_order_total` philosophy |
| Orders-by-status counts | A second filter query per status | `GROUP BY Order.status` (existing Phase 7 expression) | One query returns all five statuses; template fills gaps with `.get(..., 0)` |
| VND formatting of aggregates | New money formatter | Existing `format_price` Jinja filter | Already registered app-wide; handles zero (`0₫`) and negative (`-200.000₫`) |
| Status badge classes on breakdown rows | New badge logic | Existing `order_badge_class` Jinja global + `.badge-order-*` CSS | Already registered and verified in Phase 7 |
| Card/breakdown layout | A component library / shadcn / Tailwind | Hand-written CSS (~70–90 lines) reusing `.admin-card--wide`, `.badge`, `.product-grid` breakpoints | CLAUDE.md bans CSS/component frameworks; project is server-rendered Jinja |

**Key insight:** This phase is pure read-only aggregation over data the app already owns. Every building block (`format_price`, `order_badge_class`, `ORDER_STATUSES`, `db.func.*`, the group-by pattern) already exists and is verified — the plan is composition, not construction.

## Common Pitfalls

### Pitfall 1: Empty-DB 500 from `SUM` → `None` → `format_price`
**What goes wrong:** With zero qualifying orders, `SUM(...)` is SQLite `NULL`; `{{ revenue | format_price }}` calls `int(None)` → `TypeError` → 500 on a fresh install.
**Why it happens:** The `format_price` filter (`__init__.py:66`) casts `int(value)` with no None guard, and `SUM` over an empty set is NULL.
**How to avoid:** Wrap every aggregate in `db.func.coalesce(expr, 0)`. Verified: empty qualifying set → `0`.
**Warning signs:** The page works on populated data but 500s after `flask init-db` with zero orders.

### Pitfall 2: KeyError on a zero-count status
**What goes wrong:** `status_counts['Đã gói']` raises `KeyError` when no order is in that status — the `GROUP BY` output has no row for it.
**Why it happens:** SQL `GROUP BY` returns rows only for values that exist; missing statuses are legitimate.
**How to avoid:** Template always `status_counts.get(status, 0)` (UI-SPEC already writes this). Same convention as Phase 7 `list.html:10`.
**Warning signs:** Any direct `status_counts['...']` subscript in the template.

### Pitfall 3: NULL cost items counted as `0` profit
**What goes wrong:** If the profit query omits the `IS NOT NULL` guard, `(price - NULL) * qty` evaluates to `NULL`, silently dropping the line (or worse, being treated as 0 → overstated profit).
**Why it happens:** SQL NULL arithmetic propagates to NULL; without an explicit predicate the SUM ignores those rows ambiguously.
**How to avoid:** Profit query explicitly filters `OrderItem.product_cost_price.isnot(None)` (locked decision — NULL items excluded, never 0) and derives `profit_note` from the companion `count`.
**Warning signs:** Profit unexpectedly equals revenue, or the note logic uses an absolute threshold instead of `excluded > 0`.

### Pitfall 4: Splitting the same route across plans into a broken intermediate page
**What goes wrong:** ROADMAP splits Phase 8 into 08-01 (revenue+profit), 08-02 (orders+units), 08-03 (inventory). If each plan re-renders `stats.html` with only its section, the page is fine, but if a plan renders a template that references context vars the route doesn't yet pass, Jinja raises `UndefinedError` → 500.
**Why it happens:** One route + one template built incrementally across three plans.
**How to avoid:** Each plan keeps `admin.stats()` + `stats.html` self-consistent (every context var the template uses must be passed). 08-01 passes the full revenue/profit/units set it renders; 08-02/08-03 extend both route and template together. Do not render the full three-section template until all its vars exist.
**Warning signs:** `jinja2.exceptions.UndefinedError` on `/admin/stats` between plans.

## Code Examples

All query patterns below were **executed and verified** against a temp SQLite DB using the real `Order`/`OrderItem`/`Product` models (SQLAlchemy 2.0.51, Flask-SQLAlchemy 3.1.1). Evidence: `.planning/tmp/verify_08_stats_queries.py` → `700000 4`, `180000 2`, `3`, status dict, `3 1 1 1`, empty-set `0`.

### `admin.stats()` route (in `app/admin.py`)
```python
# Module level, next to ORDER_STATUSES:
REVENUE_STATUSES = ('Đã gửi', 'Đã nhận')   # STAT-01 locked; not a set — tuple keeps order deterministic


@admin_bp.route('/stats', methods=['GET'])
def stats():
    # Q1 — revenue + units_sold (same join+filter, one tuple row). Verified: empty set -> (0, 0)
    revenue, units_sold = (
        db.session.query(
            db.func.coalesce(db.func.sum(OrderItem.product_price * OrderItem.quantity), 0),
            db.func.coalesce(db.func.sum(OrderItem.quantity), 0),
        )
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status.in_(REVENUE_STATUSES))
        .one()
    )

    # Q2 — profit, NULL-safe: cost-bearing items only. Returns (sum, count_of_items_included)
    profit, profit_items = (
        db.session.query(
            db.func.coalesce(db.func.sum((OrderItem.product_price - OrderItem.product_cost_price) * OrderItem.quantity), 0),
            db.func.count(OrderItem.id),
        )
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status.in_(REVENUE_STATUSES), OrderItem.product_cost_price.isnot(None))
        .one()
    )

    # Q3 — total qualifying items -> derive the conditional note
    total_qual_items = (
        db.session.query(db.func.count(OrderItem.id))
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status.in_(REVENUE_STATUSES))
        .scalar()
    )
    profit_note = None
    if total_qual_items - profit_items > 0:
        profit_note = f'Lợi nhuận tính trên {profit_items} sản phẩm có giá nhập.'

    # Q4 — orders by status (exact Phase 7 expression, admin.py:133-135)
    status_counts = dict(
        db.session.query(Order.status, db.func.count(Order.id)).group_by(Order.status).all()
    )
    total_orders = sum(status_counts.values())

    # Q5 — inventory
    total_products = Product.query.count()                                   # incl. discontinued
    in_stock = Product.query.filter(Product.quantity > 0, Product.discontinued.is_(False)).count()
    out_of_stock = Product.query.filter(Product.quantity == 0, Product.discontinued.is_(False)).count()
    discontinued = Product.query.filter(Product.discontinued.is_(True)).count()

    return render_template(
        'admin/stats.html',
        revenue=revenue, profit=profit, profit_note=profit_note, units_sold=units_sold,
        status_counts=status_counts, total_orders=total_orders,
        total_products=total_products, in_stock=in_stock, out_of_stock=out_of_stock,
        discontinued=discontinued,
    )
```
*Source: pattern assembled from existing `app/admin.py` (`orders()` at line 125, `db.func.count` at 134) and verified by execution; SQLAlchemy Query API reference: docs.sqlalchemy.org/en/20/orm/query.html, SQL functions: docs.sqlalchemy.org/en/20/core/functions.html.*

### `stats.html` (key snippets — reuse of `format_price` + `order_badge_class`)
```html
{% extends "base.html" %}
{% block content %}
<div class="admin-page">
  <div class="admin-header"><h1>Thống kê</h1></div>
  <div class="admin-card admin-card--wide">
    <section class="stats-group">
      <h2 class="stats-group-title">Doanh thu &amp; Lợi nhuận</h2>
      <div class="stats-grid">
        <article class="stat-card">
          <p class="stat-label">Tổng doanh thu</p>
          <p class="stat-value stat-value--display stat-value--accent">{{ revenue | format_price }}</p>
          <p class="stat-hint">Chỉ tính đơn Đã gửi và Đã nhận.</p>
        </article>
        <article class="stat-card">
          <p class="stat-label">Lợi nhuận</p>
          <p class="stat-value stat-value--display">{{ profit | format_price }}</p>
          {% if profit_note %}<p class="stat-note">{{ profit_note }}</p>{% endif %}
          <p class="stat-hint">Doanh thu trừ giá nhập.</p>
        </article>
        <article class="stat-card">
          <p class="stat-label">Sản phẩm đã bán</p>
          <p class="stat-value">{{ units_sold }}</p>
          <p class="stat-hint">Từ các đơn Đã gửi và Đã nhận.</p>
        </article>
      </div>
    </section>
    <!-- Đơn hàng section: breakdown rows reuse order_badge_class (Jinja global) -->
    <section class="stats-group">
      <h2 class="stats-group-title">Đơn hàng</h2>
      <div class="stat-card">
        <p class="stat-label">Tổng số đơn</p>
        <p class="stat-value">{{ total_orders }}</p>
        <p class="stat-hint">Gồm cả đơn đã hủy.</p>
        <ul class="status-breakdown">
          <li><a href="{{ url_for('admin.orders') }}">Tất cả <span class="badge badge-neutral">{{ total_orders }}</span></a></li>
          <li><a href="{{ url_for('admin.orders', status='Chờ xác nhận') }}">Chờ xác nhận <span class="badge {{ order_badge_class('Chờ xác nhận') }}">{{ status_counts.get('Chờ xác nhận', 0) }}</span></a></li>
          <li><a href="{{ url_for('admin.orders', status='Đã gói') }}">Đã gói <span class="badge {{ order_badge_class('Đã gói') }}">{{ status_counts.get('Đã gói', 0) }}</span></a></li>
          <li><a href="{{ url_for('admin.orders', status='Đã gửi') }}">Đã gửi <span class="badge {{ order_badge_class('Đã gửi') }}">{{ status_counts.get('Đã gửi', 0) }}</span></a></li>
          <li><a href="{{ url_for('admin.orders', status='Đã nhận') }}">Đã nhận <span class="badge {{ order_badge_class('Đã nhận') }}">{{ status_counts.get('Đã nhận', 0) }}</span></a></li>
          <li><a href="{{ url_for('admin.orders', status='Đã hủy') }}">Đã hủy <span class="badge {{ order_badge_class('Đã hủy') }}">{{ status_counts.get('Đã hủy', 0) }}</span></a></li>
        </ul>
      </div>
    </section>
  </div>
</div>
{% endblock %}
```
*Note: `stat-value--accent` is the one addition beyond the UI-SPEC class list — see Open Question 1. `format_price` (`__init__.py:64`) and `order_badge_class` (`admin.py:31`) are both app-wide registered (verified in Phase 7: both in `app.jinja_env.globals`).*

### New CSS (in `app/static/css/style.css`, appended under a Phase 8 banner)
```css
/* ============ Phase 8: Admin stats ============ */
.stats-group { padding: 24px; }
.stats-group + .stats-group { border-top: 1px solid #E5E7EB; }   /* first section: no border */
.stats-group-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; }  /* matches .order-section h2 */
.stats-grid { display: grid; grid-template-columns: 1fr; gap: 16px; }
@media (min-width: 768px)  { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1200px) { .stats-grid { grid-template-columns: repeat(3, 1fr); } }  /* mirrors .product-grid */
.stat-card { background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 16px; }  /* same gray as .data-table thead */
.stat-label { font-size: 14px; color: #6B7280; }
.stat-value { font-size: 24px; font-weight: 600; line-height: 1.2; color: #1F2937; font-variant-numeric: tabular-nums; margin-top: 4px; }
.stat-value--display { font-size: 32px; line-height: 1.1; }     /* money role (h1.display) */
.stat-value--accent { color: #2563EB; }                          /* revenue only; see Open Question 1 */
.stat-hint { font-size: 14px; color: #6B7280; margin-top: 8px; }
.stat-note { font-size: 14px; color: #B45309; margin-top: 8px; } /* NEW hex, AA 4.7:1 on #F9FAFB (UI-SPEC) */
.status-breakdown { list-style: none; margin: 16px 0 0; padding: 0; }
.status-breakdown li + li { border-top: 1px solid #E5E7EB; }
.status-breakdown a { display: flex; align-items: center; justify-content: space-between; gap: 8px; min-height: 44px; padding: 12px 8px; color: #1F2937; }
.status-breakdown a:hover { background: #F9FAFB; text-decoration: none; }
.badge-neutral { color: #6B7280; background: #F3F4F6; border-color: #E5E7EB; }  /* same trio as .badge-discontinued */
@media (max-width: 480px) { .stats-group { padding: 16px; } }
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual `sum()` over Python `order.items` | SQL `SUM`/`COUNT` aggregates with `JOIN` + `coalesce` | Phase 8 (this phase) | Exact snapshot math in one round-trip; NULL-safe by construction |
| (none — stats page did not exist) | Read-only server-rendered stats dashboard | Phase 8 | Zero new deps; reuses `format_price` + `order_badge_class` + `.badge-order-*` |

**Deprecated/outdated:** None relevant. The project already avoids `passlib` (uses `werkzeug.security`), `Flask-Images` (uses Pillow), and `gunicorn`-on-Windows (uses waitress) — none of this changes in Phase 8. SQLAlchemy legacy `Query` API is not deprecated in 2.0 (still fully supported and the codebase's established style).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `db.session.query(...)` legacy Query API is preferred over `select()` for consistency | Standard Stack | LOW risk — both work; `select()` is the "modern" API but the entire codebase uses `session.query`. If the project later standardizes on `select()`, Phase 8 becomes a small mechanical refactor. |
| A2 | The ROADMAP 3-plan split (08-01 revenue+profit, 08-02 orders+units, 08-03 inventory) maps cleanly onto one route + one template built incrementally | Architecture Patterns | Planner must keep each intermediate state self-consistent (Pitfall 4); otherwise a template referencing a not-yet-passed context var 500s |
| A3 | `#B45309` on `#F9FAFB` ≈ 4.7:1 (AA at 14px) is accepted | Common Pitfalls / CSS | Taken from UI-SPEC (which mirrors the accepted D-07 darkening precedent); if a stricter contrast pass later disagrees, only the `.stat-note` color changes |

*All aggregation query patterns, the `coalesce` behavior, the group-by omission of zero-count statuses, and the inventory predicates are `[VERIFIED]` by direct execution — not assumptions.*

## Open Questions

1. **How is the accent color applied to revenue only?**
   - What we know: UI-SPEC mandates revenue `#2563EB`, profit `#1F2937` (accent would misread a negative profit), and its markup gives revenue and profit identical classes (`stat-value stat-value--display`). The spec's "New CSS classes" list has no revenue-color modifier.
   - What's unclear: The mechanical way to color revenue differently from profit with that markup.
   - Recommendation: Add one line `.stat-value--accent { color: #2563EB; }` (beyond the spec's class list) and apply it only on the revenue card: `<p class="stat-value stat-value--display stat-value--accent">`. Minimal, honors the 4-item accent budget, matches the `.product-price`/`.cart-total-value` accent-money precedent. Flag as a 1-line spec micro-deviation in the plan.

2. **`total_orders` derivation: `sum(status_counts.values())` vs `Order.query.count()`.**
   - What we know: Both equal the true order count (group_by only emits existing statuses; all 5 are in `ORDER_STATUSES`, and any order's status is one of the 5). UI-SPEC says "sum of the five counts."
   - What's unclear: None functionally — they're identical.
   - Recommendation: Use `sum(status_counts.values())` (UI-SPEC wording, one fewer query).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | Runtime | ✓ | 3.11.8 | — |
| Flask | Framework | ✓ | 3.1.3 | — |
| Flask-SQLAlchemy | ORM integration | ✓ | 3.1.1 | — |
| SQLAlchemy | Aggregation queries | ✓ | 2.0.51 | — |
| SQLite | Data store | ✓ | (stdlib) | — |
| Jinja2 | Templates | ✓ | (bundled) | — |

**Missing dependencies with no fallback:** None. This phase adds no external tools, services, or packages — pure code/CSS changes. (Step 2.6: no external runtime dependencies beyond the already-installed stack.)

## Validation Architecture

Skipped per `.planning/config.json` — `workflow.nyquist_validation` is explicitly `false`.

**Project convention note for the planner:** although nyquist validation is off, this project verifies every phase with temp-DB self-check scripts in `.planning/tmp/verify_XXXX.py` (see `07-VERIFICATION.md`, e.g. `verify_0701.py`, run via `python .planning/tmp/verify_0701.py` with `SECRET_KEY` set). Phase 8's plan should include a self-check that seeds products/orders/items (incl. a NULL-cost item, a `Đã hủy` order, a zero-stock and a discontinued product) and asserts the exact aggregates (revenue 700000, profit 180000, note text, status dict, inventory 3/1/1/1, empty-set 0). The throwaway `.planning/tmp/verify_08_stats_queries.py` from this research is a working starting point.

## Security Domain

`security_enforcement` is absent from `.planning/config.json` → treated as enabled. Phase 8 is a **GET-only, read-only admin page with no forms, no POST, and no user-supplied request parameters** — the attack surface is minimal, but the admin-auth boundary applies.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes (inherited) | `Flask-Login` — every admin route protected by `@admin_bp.before_request @login_required _protect_admin` (`admin.py:42-46`); `admin.stats()` gets this automatically |
| V3 Session Management | yes (inherited) | Flask signed session + `SESSION_COOKIE_HTTPONLY`/`SAMEsITE='Lax'` (`__init__.py:40-41`) — unchanged |
| V4 Access Control | yes | `admin.stats()` is a blueprint route under `/admin`, so `_protect_admin` gates it; no unauthenticated exposure |
| V5 Input Validation | no new input | The route reads **no** query/form params (statuses are hardcoded tuples `REVENUE_STATUSES`; template rows are static). No injection surface introduced |
| V6 Cryptography | no new crypto | No secrets handled; money is Integer VND (D-05), not floats |

### Known Threat Patterns for {Flask + SQLite admin}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unauthenticated access to stats | Spoofing / Info disclosure | Inherited `_protect_admin` `@login_required`; stats reveals revenue/profit → must stay admin-only (never register the route outside `admin_bp`) |
| SQL injection via status label | Tampering | Not applicable — status filter uses `Order.status.in_(REVENUE_STATUSES)` (a Python tuple, parameterized by SQLAlchemy), never a request-derived string; breakdown links use `url_for('admin.orders', status=<hardcoded label>)` |
| Sensitive cost data leak to customers | Info disclosure | Stats page is admin-only; `product_cost_price` never appears in any template output (only derived aggregates) — mirrors COST-02 |
| CSRF | — | Not applicable — no POST forms in this phase; no `csrf_token()` needed (the dashboard nav logout form already carries one, unchanged) |

## Sources

### Primary (HIGH confidence)
- **Verified by direct execution this session**: `.planning/tmp/verify_08_stats_queries.py` against a temp SQLite DB using the real models — proves `coalesce` empty-set → `0`, the `join`/`in_`/`isnot(None)` patterns, group-by omission of zero-count statuses, and all inventory predicates on SQLAlchemy 2.0.51 / Flask-SQLAlchemy 3.1.1.
- **Codebase inspection (authoritative for this project)**: `app/admin.py` (`orders()` line 125, `db.func.count` line 134, `ORDER_STATUSES`, `_order_total`, `order_badge_class`, `_protect_admin`), `app/models.py` (`Order.items` lazy='dynamic', `OrderItem.product_price/product_cost_price/quantity`, `Product.quantity/discontinued`), `app/__init__.py` (`format_price` filter line 64-66), `app/templates/admin/dashboard.html`, `app/templates/admin/orders/list.html`, `app/static/css/style.css`.
- **Phase 7 artifacts**: `.planning/phases/07-admin-order-tracking/07-VERIFICATION.md` and `07-01-PLAN.md` — established temp-DB self-check pattern and `group_by` status-count expression.
- **Locked design contracts**: `.planning/phases/08-admin-stats/08-CONTEXT.md` (all 4 areas locked), `08-UI-SPEC.md` (data contract, copy contract, new CSS class list, `#B45309` contrast).

### Secondary (MEDIUM confidence)
- SQLAlchemy 2.0 documentation: [Query API](https://docs.sqlalchemy.org/en/20/orm/query.html) and [SQL functions](https://docs.sqlalchemy.org/en/20/core/functions.html) — the legacy Query API and `func`/`coalesce` reference (patterns already proven by execution; docs cited for API shape).

### Tertiary (LOW confidence)
- None — no WebSearch-only claims were required for this phase; everything is verified by codebase evidence or direct execution.

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** — zero new deps; every reused helper verified registered app-wide; versions verified via pip.
- Architecture: **HIGH** — query patterns executed and proven against real models; plan split mirrors ROADMAP.
- Pitfalls: **HIGH** — the two crash-class bugs (empty-DB `coalesce`, `.get` vs subscript) are directly observed from execution results.

**Research date:** 2026-08-03
**Valid until:** 2026-09-02 (stable stack — Flask 3.1.x / SQLAlchemy 2.0.x; 30-day horizon).
