---
phase: 07-admin-order-tracking
plan: 01
subsystem: admin-orders
type: execute
tags: [admin, orders, list, filter, pagination]
key-files:
  created:
    - app/templates/admin/orders/list.html
    - app/templates/admin/orders/detail.html
  modified:
    - app/admin.py
    - app/templates/admin/dashboard.html
    - app/static/css/style.css
metrics:
  commits: 2
  tasks: 3
  self-check: PASSED
---

# Plan 07-01 Summary — Order list + status filter

## What was built

Admin order list at `GET /admin/orders`:
- `ORDER_STATUSES` tuple (5 VN states) + `_order_total(order)` and `order_badge_class(status)` as Jinja template globals (`app_template_global`) — single source of truth reused by 07-02/07-03.
- `orders()` route: paginated (per_page=20, `error_out=False`), newest first (`created_at desc, id desc`), optional `?status=` whitelist filter, per-status counts for the filter dropdown.
- `admin/orders/list.html`: GET filter form (dropdown with per-status counts), 5-column data table (ID / customer / total via `_order_total` / status badge / created date), drill-in order-id link, pagination that preserves `?status=`, two empty states (no orders / no orders for filter).
- `admin/orders/detail.html` minimal stub so list drill-in links resolve (full UI is 07-02).
- Dashboard: "Đơn hàng" nav group with count badge (or "Chưa có đơn"), `orders_count` passed from `dashboard()`.
- `style.css`: `.badge-order-*` ×5 (pending/packed/shipped/delivered/cancelled), `.order-filter`, `.order-id`, mobile filter stacking.

## Verification

- 17-check self-test against a temp SQLite DB (BASE_DIR patched, `create_all` + seed, CSRF disabled): globals registered, `_order_total` math, badge mapping, paginated render, status filter, page 999 → 200, dashboard nav — **all OK (TASK_OK)**. Real `data/app.db` untouched.

## Commits

| # | Hash | Message |
|---|------|---------|
| 1 | `3beb4f5` | feat(07-01): order list route + _order_total/order_badge_class globals + list template |
| 2 | `74f2340` | feat(07-01): dashboard nav 'Đơn hàng' + CSS order badges/filter/id |

## Deviations

None. (Executor completed code commits but was interrupted before writing this SUMMARY — closed out by orchestrator after verification.)

## Self-Check

**PASSED** — all tasks complete, 17/17 verification checks pass.
