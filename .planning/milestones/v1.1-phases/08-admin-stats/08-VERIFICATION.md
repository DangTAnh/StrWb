---
phase: 08-admin-stats
verifier: gsd-verifier
status: verified
date: 2026-08-03
requirements_checked: [STAT-01, STAT-02, STAT-03, STAT-04]
---

# Phase 8 Verification — Admin Stats Dashboard

**Verifier:** gsd-verifier (goal-backward analysis)
**Date:** 2026-08-03
**Phase:** `08-admin-stats` — Stats dashboard: revenue + profit (NULL-safe), orders by status, units sold, inventory counts
**Script run:** `SECRET_KEY=test python .planning/tmp/verify_08_stats_full.py` → `TASK_OK`

---

## Requirement Traceability

| Requirement ID | Plan | Source of truth (CONTEXT.md) | Status |
|---|---|---|---|
| STAT-01 | `08-01-PLAN.md` | Revenue = `sum(product_price * quantity)` over orders `Đã gửi` + `Đã nhận` | **Verified** ✓ |
| STAT-02 | `08-01-PLAN.md` | Profit = revenue − cost, NULL-safe (`product_cost_price IS NULL` excluded) | **Verified** ✓ |
| STAT-03 | `08-02-PLAN.md` | Orders by status (5 statuses + total) + units sold | **Verified** ✓ |
| STAT-04 | `08-03-PLAN.md` | Inventory counts: tổng, còn hàng, hết hàng, ngừng bán | **Verified** ✓

**Coverage:** 4/4 STAT requirements — all verified against live codebase. Every requirement ID in `08-*-PLAN.md` frontmatter is accounted for and traced to `REQUIREMENTS.md`.

---

## Method (Goal-Backward Analysis)

Checked whether the implemented code delivers what the phase goal promised — not just that tasks completed. Approach:

1. **Read all plans** (`08-01-PLAN.md`, `08-02-PLAN.md`, `08-03-PLAN.md`) to extract `must_haves` truths and acceptance criteria.
2. **Read all summaries** to cross-reference claimed vs actual implementation.
3. **Read requirements traceability** in `REQUIREMENTS.md` — confirmed all 4 STAT IDs map to Phase 8.
4. **Read the actual code** (`app/admin.py`, `app/templates/admin/stats.html`, `app/__init__.py`, `app/models.py`) to ground-check queries and template rendering.
5. **Ran the verify script** against a temp DB — confirms aggregates, empty-state, and edge cases with real model execution on SQLite (SQLAlchemy 2.0.51).

---

## STAT-01 — Total revenue (Đã gửi + Đã nhận only)

**Requirement:** `REQUIREMENTS.md` — "Admin xem tổng doanh thu (chỉ tính đơn Đã gửi + Đã nhận)"

**Implementation ground-checked:**

- `/app/admin.py:14` — `REVENUE_STATUSES = ('Đã gửi', 'Đã nhận')` (tuple, not set — deterministic IN-clause order; research Pitfall 1).
- `/app/admin.py:155-163` — Q1 query:
  ```python
  revenue, units_sold = (
      db.session.query(
          db.func.coalesce(db.func.sum(OrderItem.product_price * OrderItem.quantity), 0),
          db.func.coalesce(db.func.sum(OrderItem.quantity), 0),
      )
      .join(Order, OrderItem.order_id == Order.id)
      .filter(Order.status.in_(REVENUE_STATUSES))
      .one()
  )
  ```
- **Filter is `Order.status.in_(REVENUE_STATUSES)` → revenue excludes `Chờ xác nhận`, `Đã gói`, `Đã hủy`.** ✓
- **Every `SUM` wrapped in `db.func.coalesce(..., 0)`** — empty qualifying set returns `0` (not `NULL`), so `format_price(int(value))` never crashes. ✓
- `/app/admin.py:203-208` — `render_template` passes `revenue` to template.
- `/app/templates/admin/stats.html:11` — `{{ revenue | format_price }}` renders VND. ✓
- `/app/__init__.py:64-66` — `format_price` filter: `f'{int(value):,}'.replace(',', '.') + '₫'` → `700.000₫`, `0₫`. ✓

**Verify script confirmed:** Full-seed revenue = `700.000₫` (a: 100000×2 + 200000×1; b: 300000×1). Empty-DB: `0₫`. ✓

---

## STAT-02 — Profit (revenue − cost, NULL-safe)

**Requirement:** `REQUIREMENTS.md` — "Admin xem lợi nhuận = doanh thú − giá nhập (đơn đã gửi/nhận, xử lý NULL)"

**Implementation ground-checked:**

- `/app/admin.py:167-175` — Q2 profit query:
  ```python
  profit, profit_items = (
      db.session.query(
          db.func.coalesce(db.func.sum((OrderItem.product_price - OrderItem.product_cost_price) * OrderItem.quantity), 0),
          db.func.count(OrderItem.id),
      )
      .join(Order, OrderItem.order_id == Order.id)
      .filter(Order.status.in_(REVENUE_STATUSES), OrderItem.product_cost_price.isnot(None))
      .one()
  )
  ```
- **`OrderItem.product_cost_price.isnot(None)` guard** — items with NULL cost_price are **excluded**, never treated as 0 (avoids overstating profit; CONTEXT.md locked decision). ✓
- Q3 (`total_qual_items`) counts all qualifying items; `profit_note` derives from `excluded = total_qual_items - profit_items > 0`. ✓
- `/app/admin.py:184-186` — `profit_note = f'Lợi nhuận tính trên {profit_items} sản phẩm có giá nhập.'` (only when exclusions exist).
- `/app/templates/admin/stats.html:16-18` — profit card renders `{{ profit | format_price }}` + conditional note `{% if profit_note %}`. ✓

**Verify script confirmed:** Full-seed profit = `180.000₫`. Note `"Lợi nhuận tính trên 2 sản phẩm có giá nhập."` present (2 cost-bearing items included, 1 NULL-cost item excluded). Empty-DB: `0₫`, note absent. ✓

**Review note (IN-05, 08-REVIEW.md):** `profit_items` counts line items, not distinct products — wording `"tính trên N sản phẩm có giá nhập"` is accepted per STAT-02 locked decision. Semantic mismatch only matters if spec changes to distinct-product counting in future.

---

## STAT-03 — Orders by status + units sold

**Requirement:** `REQUIREMENTS.md` — "Admin xem số đơn theo trạng thái + tổng sản phẩm đã bán"

**Implementation ground-checked:**

- `/app/admin.py:191-194` — Q4 reuse of Phase 7 `admin.orders()` pattern exactly:
  ```python
  status_counts = dict(
      db.session.query(Order.status, db.func.count(Order.id)).group_by(Order.status).all()
  )
  total_orders = sum(status_counts.values())
  ```
  - Same expression as `admin.py:136-138` (orders route). ✓
  - `total_orders` = sum of 5 status counts, includes `Đã hủy`. ✓
- `/app/admin.py:155-158` (Q1) — `units_sold` = `sum(quantity)` over same qualifying set as revenue (Đã gửi + Đã nhận). ✓
- `/app/templates/admin/stats.html:20-23` — units_sold card: `<p class="stat-value">{{ units_sold }}</p>` (integer, no format_price — correct per UI-SPEC; units is count not money). ✓
- `/app/templates/admin/stats.html:28-43` — "Đơn hàng" section:
  - `Tổng số đơn` = `{{ total_orders }}` with hint "Gồm cả đơn đã hủy." ✓
  - `ul.status-breakdown` — 6 list items: "Tất cả" + 5 statuses ✓
  - **"Tất cả"** → `url_for('admin.orders')` (no status param) + `.badge-neutral` ✓
  - **5 statuses** → `url_for('admin.orders', status='Đã gửi')` etc. + `order_badge_class('...')` ✓
  - **Every status uses `status_counts.get('Label', 0)`** — handles zero-count statuses (group_by omits them). ✓
  - `Đã gói` renders `0` when no orders in that status (verified: `status_counts` dict omits it, `.get` returns 0). ✓

**Verify script confirmed:** Full-seed: `Tổng số đơn = 4`, status breakdown all 5 present, `Đã gói = 0` badge, `badge-order-*` classes present. Empty-DB: `Tổng số đơn = 0`, all badges `0`. ✓

---

## STAT-04 — Inventory counts (tổng / còn hàng / hết hàng / ngừng bán)

**Requirement:** `REQUIREMENTS.md` — "Admin xem số sản phẩm trong kho (tổng, hết hàng, ngừng bán)"

**Implementation ground-checked:**

- `/app/admin.py:196-201` — Q5 inventory:
  ```python
  total_products = Product.query.count()
  in_stock = Product.query.filter(Product.quantity > 0, Product.discontinued.is_(False)).count()
  out_of_stock = Product.query.filter(Product.quantity == 0, Product.discontinued.is_(False)).count()
  discontinued = Product.query.filter(Product.discontinued.is_(True)).count()
  ```
  - `total_products` = count all products (incl discontinued). ✓
  - `in_stock` = `quantity > 0 AND discontinued.is_(False)` (SC extension — 3 disjoint buckets). ✓
  - `out_of_stock` = `quantity == 0 AND discontinued.is_(False)` — **disjoint from discontinued** (discontinued + qty=0 → only counts as Ngừng bán, not Hết hàng). ✓
  - `discontinued` = `discontinued.is_(True)`. ✓
  - Uses `Product.discontinued.is_(True)`/`.is_(False)` — correct SQLAlchemy boolean predicate on SQLite (anti-pattern `== True`/`== False` avoided). ✓

- `/app/templates/admin/stats.html:45-66` — "Kho" section:
  - "Tổng sản phẩm" = `{{ total_products }}` + hint "Gồm cả sản phẩm ngừng bán." ✓
  - "Còn hàng" = `{{ in_stock }}` ✓
  - "Hết hàng" = `{{ out_of_stock }}` ✓
  - "Ngừng bán" = `{{ discontinued }}` ✓
  - All 4 render as bare integers (counts, not money — correct). ✓

**Verify script confirmed:** Full-seed inventory: Tổng sản phẩm = 3, Còn hàng = 1, Hết hàng = 1, Ngừng bán = 1. ✓

**Critical edge case verified (from 08-REVIEW.md):** A discontinued product with `quantity == 0` counts only under "Ngừng bán" (discontinued filter), NOT "Hết hàng" (out_of_stock filters `discontinued.is_(False)`). The two buckets are disjoint — no double-count. ✓

---

## Format_Price Rendering & Empty-State Zero Display

- `/app/__init__.py:64-66`: `format_price` → `int(value)` cast is safe because every SUM is coalesced to `0` (never `NULL`/`None`).
- Revenue/profit: `{{ revenue | format_price }}` → `700.000₫`, `180.000₫`, `0₫` (empty). ✓
- Counts (units_sold, total_orders, inventory): bare `{{ value }}` integers, no format_price. ✓
- **Empty state:** No dimming, no placeholder component, no empty-state message — zeros render in normal `stat-value` styling (`0₫`, `0`, badge `0`). Confirmed by `_verify_empty()` in verify script: `0₫` found, all stats = `0`. ✓

---

## Security Verification

- `_protect_admin` before_request (`admin.py:45-49`) guards **every** admin route — `admin.stats()` inherits this; unauthenticated → 302 redirect to login. ✓
- Route is GET-only, reads **no** `request.args`/`request.form` — no injection surface. Statuses are hardcoded tuples (`REVENUE_STATUSES`). ✓
- `product_cost_price` never appears in any template output — only derived aggregates. Mirrors COST-02 (cost never shown to customers; admin-only here). ✓
- Breakdown links use `url_for('admin.orders', status='Đã gửi')` — hardcoded VN labels, not user input; Phase 7 `admin.orders()` whitelist-filters. ✓

---

## Verify Script Output

```
$ SECRET_KEY=test python .planning/tmp/verify_08_stats_full.py
Verify 1: Full-seed stats dashboard
  [full seed] revenue=700000, profit=180000, units=4, orders=4, inventory=3/1/1/1 ... OK
Verify 2: Empty DB renders zeros
  [empty DB] all zeros render (0 VND, 0 don, 0 inventory) ... OK
TASK_OK
```

Exit code 0. All assertions pass.

---

## Self-Assessment — must_haves vs Reality

| must_have (from 08-01/02/03-PLAN.md) | Actual code | Status |
|---|---|---|
| GET /admin/stats shows "Tổng doanh thu" via format_price (0₫ when no orders) — STAT-01 | `admin.py:150-208` (route), `stats.html:11` (template) | ✓ |
| Revenue only counts Đã gửi + Đã nhận; Đã hủy/Chờ xác nhận/Đã gói excluded — STAT-01 | `admin.py:14, 161` (`REVENUE_STATUSES` + `.in_()`) | ✓ |
| Profit = revenue − cost on IS NOT NULL items; NULL items excluded, not 0 — STAT-02 | `admin.py:167-175` (`isnot(None)` guard) | ✓ |
| Note "Lợi nhuận tính trên N sản phẩm có giá nhập." only when excluded > 0 — STAT-02 | `admin.py:184-186` + `stats.html:17` (`{% if profit_note %}`) | ✓ |
| Empty DB: GET /admin/stats returns 200 with 0₫, no 500 — STAT-01/02 | coalesce on every SUM (`admin.py:157, 169`); verify script `_verify_empty()` confirms 200 + `0₫` | ✓ |
| Nav "Thống kê" (no badge) → /admin/stats | `dashboard.html:15-16` | ✓ |
| Units sold card = sum(quantity) on Đã gửi+Đã nhận — STAT-03 | `admin.py:158` (Q1) + `stats.html:20-23` | ✓ |
| "Đơn hàng" section: Tổng số đơn + 5 status breakdown + "Tất cả" — STAT-03 | `stats.html:28-43` | ✓ |
| Breakdown rows → /admin/orders?status=<label>, "Tất cả" → /admin/orders — STAT-03 | `stats.html:35-40` (`url_for`) | ✓ |
| Zero-count status shows 0 via `.get(s, 0)`, no KeyError — STAT-03 | `stats.html:36-40` (`status_counts.get(...)`) | ✓ |
| Total orders includes Đã hủy — STAT-03 | `admin.py:194` (`sum(status_counts.values())`) | ✓ |
| "Kho" section: 4 cards Tổng/Còn hàng/Hết hàng/Ngừng bán — STAT-04 | `stats.html:45-66` | ✓ |
| Tổng sản phẩm = count all (incl discontinued) — STAT-04 | `admin.py:198` | ✓ |
| Hết hàng = qty==0 AND NOT discontinued; Ngừng bán = discontinued — STAT-04 | `admin.py:199-201` (disjoint) | ✓ |
| Còn hàng = qty>0 AND NOT discontinued — STAT-04 | `admin.py:199` | ✓ |
| Empty DB: 4 inventory cards render 0 — STAT-04 | verify script `_verify_empty()` confirms 0s | ✓ |

---

## Conclusion

**Phase 8 goal: ACHIEVED.** The `GET /admin/stats` dashboard delivers all four STAT requirements (STAT-01 through STAT-04) as locked in `08-CONTEXT.md`. The implementation is NULL-safe (coalesce on every SUM), disjoint-correct (inventory buckets cannot overlap), and empty-safe (temp-DB verify confirms `0₫` and zero counts with no 500s). The verify script `.planning/tmp/verify_08_stats_full.py` passes end-to-end (`TASK_OK`), asserting revenue=700000, profit=180000, profit_note present, units=4, total_orders=4, status breakdown with Đã gói=0, inventory 3/1/1/1, and full empty-DB zero rendering.

**No new dependencies added.** Reuses `format_price`, `order_badge_class`, `ORDER_STATUSES`, `.badge-order-*`, `.admin-card--wide`, and the Phase 7 `group_by` pattern. GET-only, no forms, no CSRF needed, admin-auth boundary inherited.

---

**Reviewed:** 2026-08-03
**Status:** verified
