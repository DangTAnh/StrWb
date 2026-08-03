---
phase: 08-admin-stats
plan: 02
subsystem: admin-stats
type: execute
tags: [admin, stats, orders, units-sold]
key-files:
  modified:
    - app/admin.py
    - app/templates/admin/stats.html
    - app/static/css/style.css
metrics:
  commits: 3
  tasks: 3
  self-check: PASSED
---

# Plan 08-02 Summary — Orders by status + units sold

## What was built

EXTEND `GET /admin/stats` — second section of the stats dashboard:

- **Q4** in `admin.stats()`: `status_counts = dict(db.session.query(Order.status, db.func.count(Order.id)).group_by(Order.status).all())` — exact copy of Phase 7 `admin.orders()` pattern (line 133-135). `total_orders = sum(status_counts.values())` (includes cancelled, matches `Order.query.count()`).
- `admin/stats.html`:
  - Added 3rd card in "Doanh thu & Lợi nhuận" grid: **"Sản phẩm đã bán"** (`{{ units_sold }}` integer, from Q1 in 08-01) + hint "Từ các đơn Đã gửi và Đã nhận."
  - New **"Đơn hàng"** section after money section (within same `.admin-card--wide`): `stat-card` with "Tổng số đơn" + breakdown `ul.status-breakdown` (6 links: "Tất cả" → `/admin/orders` no filter + `.badge-neutral`; 5 statuses → `/admin/orders?status=<VN label>` + `.badge {{ order_badge_class(...) }}`). Every status uses `status_counts.get('<label>', 0)` — handles zero-count statuses safely.
- `style.css`: `.status-breakdown` (list-style none, li border-top, a flex with min-height 44px touch target, hover #F9FAFB) + `.badge-neutral` (gray trio #6B7280/#F3F4F6/#E5E7EB, matching `.badge-discontinued`).

## Verified pitfalls addressed

- **Pitfall 2 (KeyError → 500):** `group_by` omits statuses with zero orders. Template uses `status_counts.get('Đã gói', 0)` — verified `'Đã gói' not in status_counts` returns 0, not KeyError. No new dependency; DB untouched; GET-only.

## Verification

- Task 1 verify: Q4 `status_counts` omit zero-count (Đã gói absent), `total_orders=4` sum correct — `TASK_OK`
- Task 2 verify: GET /admin/stats → 200; units_sold=3 (2+1 from Đã nhận+Đã gửi); breakdown 6 links; Đã gói renders 0; badge-order-* present; no 08-03 vars (`total_products`/`in_stock`) — `TASK_OK`
- Task 3 verify: CSS contains `.status-breakdown` + `.badge-neutral` with correct hex values — `TASK_OK`

## Commits

| # | Hash | Message |
|---|------|---------|
| 1 | `076e0f7` | feat(08-admin-stats-02): Q4 status_counts + total_orders in admin.stats() |
| 2 | `6af1d75` | feat(08-admin-stats-02): stats.html units_sold card + Đơn hàng breakdown section |
| 3 | `48d50f2` | feat(08-admin-stats-02): CSS .status-breakdown + .badge-neutral |

## Deviations

None.

## Self-Check

**PASSED** — 3/3 tasks committed, all verify scripts exit 0 printing TASK_OK.
