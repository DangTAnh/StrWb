# Phase 8 — UI Review (Admin Stats Dashboard)

**Audited:** 2026-08-03
**Baseline:** `08-UI-SPEC.md` (design contract — 6/6 PASS at creation)
**Coverage:** Full code audit of all 4 implementation files + CSS, grounded against `08-CONTEXT.md` decisions and Phase 7 patterns. Render verification via `.planning/tmp/verify_08_stats_full.py` (confirms empty-state zeros render, status breakdown correct).
**Registry audit:** N/A — Flask project, no `components.json`, no shadcn, no third-party registries. All Phase 8 CSS/templates hand-rolled (Jinja2 + plain CSS per CLAUDE.md). No new dependencies.

---

## Pillar Scores

| # | Pillar | Score (1-4) | Key Finding |
|---|--------|-------------|-------------|
| 1 | Copywriting | 4 | Every declared string matches `08-UI-SPEC.md` Copywriting Contract verbatim; Vietnamese throughout; no primary CTA (read-only dashboard); zero-data renders explicit `0₫`/`0` with labels; no error/empty-state component. |
| 2 | Visuals | 4 | Reuses `.admin-card--wide` + `.admin-page`/`.admin-header`; `.order-section` divider pattern mirrored via `.stats-group` border-top; `.badge-order-*` + new `.badge-neutral` match gray-trio; gray stat tiles (`#F9FAFB`) match `.data-table thead`. |
| 3 | Color | 4 | Single new hex `#B45309` scoped to `.stat-note` only (AA 4.7:1 on `#F9FAFB`); accent `#2563EB` reserved for revenue value only (`stat-value--accent`); profit + all counts `#1F2937` (not accent) — respects 60/30/10. |
| 4 | Typography | 4 | All new elements mapped to 4 inherited roles (14/16/24/32 · weights 400/600); no new sizes or weights; `tabular-nums` on money (`stat-value--display`) and counts (`stat-value`); line-heights 1.1/1.2 per role. |
| 5 | Spacing | 4 | All values multiples of 4 from inherited scale (4/8/16/24); 44px breakdown-row touch target per spec exception (`min-height:44px` + `padding:12px 8px`); `border-top:1px #E5E7EB` divider between `.stats-group` sections. |
| 6 | Experience Design | 4 | Server-rendered GET-only (no JS, no polling, no forms, no CSRF); nav "Thống kê" has no misleading count badge; breakdown rows are real `<a>` links (6 total: Tất cả + 5 statuses); zero-count statuses render via `.get(s, 0)` (no KeyError); heading hierarchy h1→h2→p.label; page works with scripting disabled. |

**Overall: 24/24 (4.0/4 average) — APPROVED**

---

## Verdict: APPROVED

Faithful, complete implementation of `08-UI-SPEC.md`. All 6 pillars pass; every locked CONTEXT.md decision is honored; the single new CSS hex (`#B45309`) is justified as an AA contrast fix over the inherited `#D97706`. No design deviations, no accessibility gaps, no state-machine holes. Verification script confirms both populated and empty-DB rendering.

---

## Findings Summary

| Severity | Count |
|----------|-------|
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 2 |
| INFO | 0 |

---

## Detailed Findings

### LOW

**L1 — Profit note wording counts line-items, not distinct products (semantic edge case, spec-locked).**
- `app/admin.py:186` — `profit_note = f'Lợi nhuận tính trên {profit_items} sản phẩm có giá nhập.'` where `profit_items` = `db.func.count(OrderItem.id)` (one row per order-item line, not DISTINCT product).
- If two line items of the same product appear in different orders (or the same order), the note reads "2 sản phẩm" while only 1 distinct product has a cost price. This is a semantic mismatch only.
- **Status per spec:** `08-CONTEXT.md` STAT-02 locked decision states the note wording verbatim and `08-UI-SPEC.md` Dimension 4 notes line-items are accepted. The `08-REVIEW.md` (code review) also flags this as IN-05 and accepts it as spec-compliant.
- **Recommendation:** No change unless future spec wants distinct-product counting. Documented, not a defect.

**L2 — Redundant Q3 query for `total_qual_items` (minor perf, not a UI deviation).**
- `app/admin.py:178-183` runs a 3rd `db.session.query` over `order_items JOIN orders` with the same `REVENUE_STATUSES` filter already used by Q1 (`admin.py:155-163`).
- This is a code-quality/perf observation (flagged as IN-03 in `08-REVIEW.md`), not a visual/UI-spec deviation. The Phase 8 UI-REVIEW scope covers visual compliance, so this is noted for completeness only — no visual impact.
- **Recommendation:** Could merge `count(OrderItem.id)` into Q1's SELECT; deferred (no user-visible effect).

---

## Spec Compliance Checklist

Verified against `.planning/phases/08-admin-stats/08-UI-SPEC.md`:

| Spec Item | Status | Evidence |
|-----------|--------|----------|
| Nav "Thống kê" after "Đơn hàng", no badge | PASS | `dashboard.html:15-16` — `.nav-group` with plain `<a>`, no `.badge` |
| Route `GET /admin/stats`, `@login_required` | PASS | `admin.py:150-151` — inherits `before_request` |
| Template extends `base.html` | PASS | `stats.html:1` — `{% extends "base.html" %}` |
| `.admin-card.admin-card--wide` container | PASS | `stats.html:5` |
| 3 groups: Doanh thu/Lợi nhuận / Đơn hàng / Kho | PASS | `stats.html:6, 28, 45` |
| Revenue = accent `#2563EB` only | PASS | `stats.html:11` `stat-value--accent`; `style.css:504` |
| Profit = `#1F2937` (not accent) | PASS | `stats.html:16` |
| Profit note `#B45309`, conditional | PASS | `stats.html:17` (`{% if profit_note %}`) + `style.css:506` |
| Counts = `#1F2937` (not accent) | PASS | `stats.html:22,32,50,55,59,63` |
| `format_price` on money, bare int on counts | PASS | `stats.html:11,16` (pipe filter); `22,32,50,55,59,63` (bare) |
| Empty state: `0₫` / `0` / badge `0` normal style | PASS | `08-VERIFICATION.md:167`; verify script `_verify_empty()` |
| Breakdown rows: links to `/admin/orders?status=` | PASS | `stats.html:35-40` — `url_for('admin.orders', status='...')` |
| "Tất cả" row: `/admin/orders` + `.badge-neutral` | PASS | `stats.html:35` + `style.css:514` |
| 5 status badges via `order_badge_class` | PASS | `stats.html:36-40` |
| `status_counts.get(s, 0)` — zero-safe | PASS | `stats.html:36-40` |
| `.stat-note` AA contrast (4.7:1) | PASS | `style.css:506` — `#B45309` on `#F9FAFB` |
| 44px touch targets on breakdown rows | PASS | `style.css:512` — `min-height:44px` |
| Responsive grid 1→2→3 cols | PASS | `style.css:497-499` — `1fr` / `repeat(2,1fr)` @768 / `repeat(3,1fr)` @1200 |
| Tabular nums on money + counts | PASS | `style.css:502` (`stat-value`), `style.css:503` (`stat-value--display`) |
| 11 new CSS classes per spec | PASS | `style.css:494-514` — `.stats-group`, `.stats-group-title`, `.stats-grid`, `.stat-card`, `.stat-label`, `.stat-value`, `.stat-value--display`, `.stat-hint`, `.stat-note`, `.status-breakdown`, `.badge-neutral` |
| No new dependencies | PASS | Reuses `format_price`, `order_badge_class`, `ORDER_STATUSES`, `.badge-order-*`, `.admin-card--wide` |

---

## Registry Safety

No `components.json`, no shadcn, no third-party registries, no Tailwind/Bootstrap/React (per CLAUDE.md "What NOT to Use"). All Phase 8 additions are hand-rolled CSS classes in `app/static/css/style.css` (lines 493-514) and native Jinja2 in `app/templates/admin/stats.html`. No new dependencies. Clean.

---

## Deviation Classification

**Design deviations vs UI-SPEC (must-fix):** None — implementation is faithful to all locked decisions in `08-CONTEXT.md` and the component contract in `08-UI-SPEC.md`.

**Quality gaps (fix recommended, not contract-mandated):** L1 (profit-note line-item count semantics — spec-locked, no change), L2 (redundant Q3 query — code-level, no UI impact).

**Cosmetic / optional:** None identified.

---

## Files Audited

- `app/templates/admin/stats.html` — PRIMARY (3-group stat dashboard)
- `app/templates/admin/dashboard.html` — nav addition ("Thống kê")
- `app/static/css/style.css` — Phase 8 section (lines 493-514)
- `app/admin.py` — `stats()` route (lines 150-208)
- `app/__init__.py` — `format_price` filter (lines 64-66)
- `.planning/phases/08-admin-stats/08-UI-SPEC.md` — design contract (primary reference)
- `.planning/phases/08-admin-stats/08-CONTEXT.md` — locked decisions
- `.planning/phases/08-admin-stats/08-REVIEW.md` — prior code review (IN-01 through IN-06)
- `.planning/phases/08-admin-stats/08-VERIFICATION.md` — verify script ground-truth