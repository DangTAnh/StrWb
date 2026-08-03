---
phase: 08-admin-stats
plan: 01
subsystem: admin-stats
type: execute
tags: [admin, stats, revenue, profit, null-safe]
key-files:
  created:
    - app/templates/admin/stats.html
  modified:
    - app/admin.py
    - app/templates/admin/dashboard.html
    - app/static/css/style.css
metrics:
  commits: 3
  tasks: 3
  self-check: PASSED
---

# Plan 08-01 Summary — Revenue + profit (NULL-safe)

## What was built

`GET /admin/stats` route + first section of the stats page:

- `REVENUE_STATUSES = ('Đã gửi', 'Đã nhận')` — STAT-01 locked: only shipped + received orders count toward revenue (tuple keeps IN-clause order deterministic).
- `admin.stats()` route: 3 aggregate queries, all wrapped in `coalesce(..., 0)` so an empty qualifying set returns 0 (never `int(None)` → 500 crash):
  - Q1: revenue = `sum(product_price * quantity)` + units_sold (rendered in 08-02 per ROADMAP split).
  - Q2: profit = `sum((product_price - product_cost_price) * quantity)` on items with `product_cost_price IS NOT NULL` — NULL-cost items excluded, never treated as 0 (avoids overstating profit, STAT-02).
  - Q3: total qualifying items → derives the conditional note `"Lợi nhuận tính trên N sản phẩm có giá nhập."` shown only when some items were excluded.
- `admin/stats.html`: "Doanh thu & Lợi nhuận" section — revenue card (`.stat-value--accent` #2563EB) + profit card (`.stat-note` #B45309, AA 4.7:1), `format_price` for VND, hint "Chỉ tính đơn Đã gửi và Đã nhận."
- Dashboard nav: "Thống kê" group (no badge, pattern like "Đơn hàng").
- `style.css`: `.stats-group`, `.stats-grid` (1→2→3 col responsive), `.stat-card`, `.stat-label/.stat-value/.stat-value--display/.stat-value--accent`, `.stat-hint`, `.stat-note`.

## Verification

- Orchestrator verified full diff against CONTEXT decisions (STAT-01/02) after executor was interrupted by a provider 502 mid-run: statuses locked to Đã gửi + Đã nhận, `coalesce` on every SUM (empty-set safe), NULL-cost items excluded from profit, conditional note only when exclusions exist, accent class only on revenue. All match.
- Route registration + Jinja globals (`format_price`) consistent with existing admin patterns; `_protect_admin` before_request guards all admin routes.
- Runtime smoke test (full verify with temp DB) is scheduled in plan 08-03 (`verify_08_stats_full.py`) after all 3 sections exist.

## Commits

| # | Hash | Message |
|---|------|---------|
| 1 | `3524227` | feat(08-admin-stats-01): REVENUE_STATUSES + admin.stats() route with NULL-safe Q1-Q3 aggregates |
| 2 | `1bbfb24` | feat(08-admin-stats-01): admin/stats.html money section (revenue + profit + conditional note) |
| 3 | `2deded2` | feat(08-admin-stats-01): dashboard 'Thống kê' nav (no badge) + Phase 8 CSS stat classes |

## Deviations

None. (Executor committed all 3 tasks but was killed by provider 502 before writing this SUMMARY — closed out by orchestrator after diff verification; worktree merged.)

## Self-Check

**PASSED** — 3/3 tasks committed, diff matches all CONTEXT decisions (STAT-01, STAT-02) and research pitfalls (coalesce on empty set, NULL-cost exclusion).
