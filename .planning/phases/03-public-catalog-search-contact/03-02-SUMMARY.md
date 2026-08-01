---
phase: 03-public-catalog-search-contact
plan: 02
subsystem: ui
tags: [flask, jinja2, product-detail, gallery, messenger, vietnamese]
requires:
  - phase: 03-public-catalog-search-contact
    plan: 01
    provides: public/base.html layout chain, _nav.html header, product_detail route stub, Product.primary_image / ProductImage.thumb_filename, badge palette + .btn/.back-link CSS
provides:
  - full product detail route (404 on missing, images ordered by sort_order)
  - gallery-detail component: main image + 72px thumbnail strip + inline vanilla JS swap (D-06, CAT-05)
  - D-08 info order (name → price → status → CTA → brand → measurements → description)
  - Messenger CTA on all statuses + red out-of-stock note (D-07, D-13, CONT-02)
  - safe same-origin back link preserving search→detail context
affects: [Phase 3 wave 03-03, Phase 4]
tech-stack:
  added: []  # zero new packages; single ~10-line inline vanilla JS snippet (justified exception)
  patterns: [gallery thumbnail swap via data-src/data-alt + aria-current, conditional row omission for empty brand/measurements, same-origin referrer back-link]
key-files:
  created: []
  modified: [app/public.py, app/templates/public/product_detail.html, app/static/css/style.css]
key-decisions:
  - "Messenger CTA rendered for ALL statuses (out-of-stock, discontinued) — the sales channel isn't gated by stock (UI-SPEC flagged decision 6)"
  - "Main image reuses the 400px thumb asset (IMG-04) — no new full-size render; documented upgrade path (UI-SPEC flagged decision 4)"
  - "Back-link uses same-origin referrer (starts with request.host_url) else home — never a raw open redirect (T-03-05)"
  - "Detail goes 2-column at 768 not 1200; gallery column 360px → 440px at 1200 (UI-SPEC flagged decision 3)"
requirements-completed: [CAT-02, CAT-03, CAT-05, CONT-02]
duration: 4min
completed: 2026-08-01
---

# Phase 3 Plan 2: Product Detail Summary

Full product detail page: gallery with main image + clickable 72px thumbnail strip swapped by a ~10-line inline vanilla JS snippet, D-08-enforced info order (name → price → status → Messenger CTA → brand → measurements → description), Messenger button on every stock status with a red out-of-stock alert line, and a same-origin-safe back link that preserves search→detail context.

## Performance

- **Duration:** 4 min
- **Started:** 2026-08-01T14:05:30Z (approx)
- **Completed:** 2026-08-01T14:09:30Z (approx)
- **Tasks:** 2 completed
- **Files modified:** 3

## Accomplishments
- `product_detail` route returns the product + all `images` ordered by `ProductImage.sort_order` ASC; unknown id → `abort(404)` → generic errors/404.html (T-03-04); template renders only public fields — `admin_note` never leaks (asserted)
- Detail layout: `.product-detail` flex column below 768, row at ≥768 (image left, info right, D-05); gallery column 360px at ≥768, 440px at ≥1200; main image box neutral white with `object-fit: contain`
- Gallery (D-06/CAT-05): main image = first image (Phase 2 D-12); thumbnail strip only when `images|length > 1`; real `<button>` thumbs with `aria-label="Xem ảnh {n}"`, first active with `aria-current="true"`; inline vanilla JS swaps `#main-image` src/alt and toggles `.is-active`/`aria-current`; graceful when JS off
- Info order enforced by markup (D-08): h1 name → price (Display 32px accent tabular-nums) → status badge → Messenger CTA → out-of-stock red line → brand/measurements meta → description
- Messenger CTA on ALL statuses (D-07/D-13); red line "Sản phẩm hiện đang hết hàng." only when `out_of_stock`
- Empty brand/measurements rows and empty description section omitted entirely
- Back-link: same-origin referrer (`startswith(request.host_url)`) else home; cross-origin referrer rejected (T-03-05)
- CSS: total 15.5KB < 20KB

## Task Commits

1. **Task 1: Full product_detail route + page** — `dbe4c47` (feat: route), `c0b5a93` (feat: page)
2. **Task 2: Detail CSS** — `22a2316` (style)

## Files Created/Modified
- `app/public.py` - product_detail route: `images` ordered by sort_order passed to template
- `app/templates/public/product_detail.html` - full gallery + info page + inline JS swap (replaces stub)
- `app/static/css/style.css` - product-detail, gallery, meta, out-of-stock-note CSS (15.5KB total)

## Decisions Made
- Messenger CTA present for discontinued products too (UI-SPEC flagged decision 6): a customer may still ask about restock or a discontinued item
- Main image reuses the 400px thumbnail; no mid-size render in this phase — documented upgrade path if 2x DPR sharpness becomes an issue
- Back-link preserves search→detail context when arriving from `/search?q=...` (PITFALLS back-link pitfall)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Verify harness DB isolation ineffective (discovered in 03-03, affected all waves)**
- **Found during:** 03-03 Task 1 verify (root-caused during this phase)
- **Issue:** Flask-SQLAlchemy 3.1.1 creates engines eagerly in `init_app()`, so the plan's harness pattern of setting `app.config['SQLALCHEMY_DATABASE_URI']` after `create_app()` was silently ignored. This wave's verifies wrote seeded products into the gitignored `data/app.db` (later cleaned up); their assertions are product-specific within a single rendered detail page, so they still passed.
- **Fix:** Harness-only — dispose + rebuild the default engine after overriding the URI. Re-ran this plan's Task 1 verify against an isolated temp DB — green. Removed the polluted `data/app.db`.
- **Files modified:** none (test-harness invocation only); `data/app.db` deleted (gitignored runtime artifact)
- **Verification:** 03-02 TASK1 OK printed

---

**Total deviations:** 1 auto-fixed (cross-cutting test-harness DB isolation)
**Impact on plan:** None — production code matches the plan exactly; verify assertions confirmed green against an isolated DB.

## Issues Encountered
- None during implementation. Both task verify scripts passed; plan-level verification (including same-origin / cross-origin back-link behavior) green against an isolated DB.

## Next Phase Readiness
- Detail page fully wired for 03-03: the `_nav.html` search form and `_product_card.html` links already resolve
- Search results grid (03-03) reuses `_product_card.html` unchanged; cards already point to this detail route

---
*Phase: 03-public-catalog-search-contact*
*Completed: 2026-08-01*

## Self-Check: PASSED

All claims verified — SUMMARY file exists, all 3 task commits present (dbe4c47, c0b5a93, 22a2316), plan-level verification green.
