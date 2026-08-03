---
phase: 07-admin-order-tracking
plan: 02
subsystem: admin-orders
type: execute
tags: [admin, orders, detail, ord-07]
key-files:
  created:
    - app/templates/admin/orders/detail.html
  modified:
    - app/__init__.py
metrics:
  commits: 3
  tasks: 3
  files: 3
  self-check: PASSED
---

# Plan 07-02 Summary — Order detail view (ORD-07)

## What was built

Order detail page at `GET /admin/orders/<int:order_id>`:

- **`strftime` Jinja filter** in `app/__init__.py` — None-safe, renders `%d/%m/%Y %H:%M` for created_at/updated_at. Owned by this plan (07-01 used `.strftime()` method call directly).
- **`order_detail` route** in `app/admin.py` — `db.session.get(Order, order_id)`; missing order flashes `'Không tìm thấu đơn.'` (error) + redirects to `admin.orders` (no 404/500). Route stub created by 07-01; this plan owns the full detail UI that renders through it.
- **`admin/orders/detail.html`** — full template: back-link, header (`Đơn #{{ order.id}}` + status badge via `order_badge_class`), three `.order-section` blocks (Thông tin khách / Sản phẩm / Thời gian).
  - Customer info via `dl.order-meta` (Họ và tên, Số điện thoại, Địa chỉ, optional Ghi chú)
  - Items table (`.data-table`): product_name as plain-text snapshot (no product link — product_id may be NULL), quantity, unit price, line total
  - `.cart-total` reuses Phase 6 `.cart-total-value`/`.cart-total-label`; grand total via `_order_total(order)` (single source of truth from 07-01)
  - Timestamps via `| strftime('%d/%m/%Y %H:%M')`
  - **Does NOT** render `product_cost_price` (COST-02 — cost price reserved for Phase 8 stats)
- **`style.css`** — appended `.order-detail` (padding 24px), `.order-section` (border-top + padding/margin 24px + h2 16px/600), `.order-meta dt/dd`, `.data-table .unit-price`. Reuses `.cart-total-value` from Phase 6 unchanged.

No new dependencies. Real `data/app.db` untouched — all verification runs against temp patched `BASE_DIR` + `db.create_all()`.

## Reused from 07-01 (not redefined)

- `_order_total(order)` Jinja global — grand total
- `order_badge_class(status)` Jinja global — badge CSS class mapping
- `ORDER_STATUSES` tuple
- `admin.orders` endpoint + list template
- `.badge-order-*` CSS classes, `.order-filter`, `.order-id`

## Verification

- **Task 1 verify** — `strftime` filter in `jinja_env.filters`, None-safe, renders `'02/08/2026 09:30'` for `%d/%m/%Y %H:%M`; `admin.order_detail` view registered. **TASK_OK**
- **Task 2 verify** — temp DB: login → GET `/admin/orders/{id}` renders header badge (`badge-order-pending`), customer info, both items, line total `200.000₫`, grand total `400.000₫`, timestamps matching `\d{2}/\d{2}/\d{4} \d{2}:\d{2}`, back-link present, no `product_cost_price`; missing order → redirect + flash `'Không tìm thấy đơn.'` no 500. **TASK_OK**
- **Task 3 verify** — `.order-detail`/`.order-section`/`.order-meta`/`.data-table .unit-price` present in CSS; `.cart-total-value` (Phase 6) intact. **TASK_OK**
- **Full E2E** — all assertions pass. **ALL_TASKS_OK**

## Deviations

None. Plan executed as written. The `order_detail` route body (lines 138-144 in admin.py) was created as a minimal stub by 07-01 — this plan reuses it unchanged and owns only the `strftime` filter and the template that renders through it.

## Self-Check

**PASSED** — all 3 tasks complete, all verification scripts exit 0 printing TASK_OK, full E2E passes, real DB untouched.
