---
phase: 08
plan: 03
subsystem: admin-stats
type: execute
tags: [admin, stats, inventory, stat-04]
key-files:
  modified:
    - app/admin.py
    - app/templates/admin/stats.html
  created:
    - .planning/tmp/verify_08_stats_full.py
metrics:
  commits: 3
  tasks: 3
  self-check: PASSED
---

# Plan 08-03 Summary — Inventory counts dashboard

## What was built

Final plan of Phase 8 — completes the `GET /admin/stats` dashboard with the inventory (STAT-04) section. All three sections of the stats page are now present: "Doanh thu & Lợi nhuận", "Đơn hàng", "Kho".

- `app/admin.py` `stats()`: added Q5 inventory counts **after** Q4 (status_counts) and **before** `return render_template(...)`:
  - `total_products = Product.query.count()` — all products incl. discontinued
  - `in_stock = Product.query.filter(Product.quantity > 0, Product.discontinued.is_(False)).count()`
  - `out_of_stock = Product.query.filter(Product.quantity == 0, Product.discontinued.is_(False)).count()`
  - `discontinued = Product.query.filter(Product.discontinued.is_(True)).count()`
  - Added `total_products`, `in_stock`, `out_of_stock`, `discontinued` to `render_template()` — all 6 prior vars (revenue, profit, profit_note, units_sold, status_counts, total_orders) preserved.
- `app/templates/admin/stats.html`: added third `<section class="stats-group">` ("Kho") after the "Đơn hàng" section, inside the same `.admin-card--wide`. 4 `article.stat-card` tiles: "Tổng sản phẩm" (with hint "Gồm cả sản phẩm ngừng bán."), "Còn hàng", "Hết hàng", "Ngừng bán" — reuses `.stats-grid`/`.stat-card`/`.stat-label`/`.stat-value`/`.stat-hint` from plan 08-01. No new CSS required (already present from prior plans).
- `.planning/tmp/verify_08_stats_full.py`: standalone E2E self-check — seeds a temp DB (3 products incl. discontinued + NULL-cost + out-of-stock; 4 orders across all 5 statuses + Đã hủy; 5 order items incl. cancelled/pending excluded from revenue). Asserts revenue `700.000₫`, profit `180.000₫`, profit_note "Lợi nhuận tích trên 2 sản phẩm có giá nhập.", units=4, total_orders=4, all 5 status badges correct with Đã gói=0, inventory 3/1/1/1, plus an empty-DB case rendering `0₫` and zero counts.

## Verified pitfalls addressed

- **Research anti-pattern (Boolean predicates):** used `Product.discontinued.is_(False)` / `.is_(True)` — not `== False`/`== True`, which breaks on SQLite boolean columns (verified via research query against real models).
- **Separation of out_of_stock vs discontinued (STAT-04):** `out_of_stock` filters `quantity == 0 AND discontinued.is_(False)` — keeps the two disjoint. DISCONTINUED product with qty=0 still counts only under "Ngừng bán", not "Hết hàng".
- **Empty DB:** all aggregates use `coalesce(..., 0)` (inherited from 08-01) and `group_by`-derived `status_counts` uses `.get(s, 0)` (template). Verify script's empty-DB path confirms `0₫`, 0 orders, 0 inventory — no 500.

## Verification

- Task 1 verify: Q5 query predicates against temp DB with in-stock/out-of-stock/discontinued products → counts (3, 1, 1, 1) — `TASK_OK`
- Task 2 verify: GET /admin/stats → 200; "Kho" section renders 4 stat-cards 3/1/1/1 + hint; no error — `TASK_OK`
- Task 3 verify: `SECRET_KEY=test python .planning/tmp/verify_08_stats_full.py` → full-seed assertions + empty-DB zeros — `TASK_OK`

## Commits

| # | Hash | Message |
|---|------|---------|
| 1 | `3ec210a` | feat(08-admin-stats-03): Q5 inventory counts in admin.stats() |
| 2 | `6afd20a` | feat(08-admin-stats-03): stats.html Kho section 4 stat-card |
| 3 | `2a90f26` | test(08-admin-stats-03): full E2E self-check verify_08_stats_full.py |

## Deviations

None — plan executed exactly as written. No new dependencies; schema untouched; GET-only; `data/app.db` never touched by verify (temp BASE_DIR only).

## Self-Check

**PASSED** — 3/3 tasks committed, all verify commands exit 0 printing TASK_OK.

Full E2E verify (`.planning/tmp/verify_08_stats_full.py`):
- Revenue 700000, Profit 180000, profit_note present, units_sold 4, total_orders 4
- Status breakdown: 5 statuses rendered, Đã gói=0, Đã hủy=1, Chờ xác nhận=1, Đã gửi=1, Đã nhận=1
- Inventory: Tổng sản phẩm 3, Còn hàng 1, Hết hàng 1, Ngừng bán 1, hint present
- Empty DB: 0₫, 0 orders, 0 inventory, status badges 0

## Requirements

| Requirement | Status |
|-------------|--------|
| STAT-04 | Complete |

STAT-01, STAT-02, STAT-03 already complete via plans 08-01 + 08-02. Phase 8 STAT coverage: 4/4 (all verified).
