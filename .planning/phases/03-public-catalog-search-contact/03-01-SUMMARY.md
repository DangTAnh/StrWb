---
phase: 03-public-catalog-search-contact
plan: 01
subsystem: ui
tags: [flask, jinja2, public-catalog, product-grid, pagination, vietnamese]
requires:
  - phase: 01-scaffold-auth-data-model
    provides: Flask app factory, public blueprint, Product model, base template, CSS token set
  - phase: 02-admin-crud-images
    provides: Product.primary_image + ProductImage.thumb_filename (400px asset), status badge palette, .btn/.pagination/.empty-state CSS, format_price filter
provides:
  - public layout chain: base.html {% block header %}, public/base.html, public/_nav.html (sticky header + GET search form)
  - home catalog grid route: 12/page, sort_order ASC + id ASC, paginate(error_out=False)
  - shared product card include (_product_card.html) reused by home + search grids (D-12)
  - out-of-stock/discontinued dimmed image + overlay badge (D-04)
  - homepage contact strip with Messenger CTA (CONT-01/02, D-13)
  - stub product_detail + search routes so url_for never raises BuildError
affects: [Phase 3 waves 03-02/03-03, Phase 4]
tech-stack:
  added: []  # zero new packages
  patterns: [public/base.html inheritance chain, shared _product_card include, sticky header with GET search form, 2/3/4 responsive grid, 12/page pagination]
key-files:
  created: [app/templates/public/base.html, app/templates/public/_nav.html, app/templates/public/_product_card.html, app/templates/public/product_detail.html, app/templates/public/search.html]
  modified: [app/templates/base.html, app/public.py, app/templates/public/index.html, app/static/css/style.css]
key-decisions:
  - "Header block {% block header %} inserted between skip-link and flash zone so admin/auth pages render no header (D-09, UI-SPEC Decision Flagged 1)"
  - "Card-name clamp line-height 1.4 documented as a CSS exception (UI-SPEC Dimension-4 flag, non-blocking) — not a new type role"
requirements-completed: [CAT-01, CAT-03, CONT-01, CONT-02]
duration: 5min
completed: 2026-08-01
---

# Phase 3 Plan 1: Public foundation + home catalog grid Summary

Replaced the Phase 1 coming-soon page with a real public catalog: shared public layout chain (base header block + public/base.html + sticky header with GET search form), responsive 2/3/4-column product grid (12/page, sort_order-then-id), shared product-card include with dimmed-image + overlay badges for out-of-stock/discontinued, homepage Messenger contact strip that renders even on an empty store, and stub product_detail/search routes so all `url_for` calls resolve mid-phase.

## Performance

- **Duration:** 5 min
- **Started:** 2026-08-01T14:00:42Z
- **Completed:** 2026-08-01T14:05:26Z
- **Tasks:** 3 completed
- **Files modified:** 8

## Accomplishments
- Public chrome: `base.html` gains `{% block header %}`; `public/base.html` extends base and includes `public/_nav.html`; admin/auth templates don't override the block → they render no header (D-09, UI-SPEC flagged decision 1)
- Header nav: brand link "Cửa hàng" → home + GET search form (`role="search"`, input `name="q"`, submit "Tìm") that pre-fills `q` from `request.args` (D-10)
- Home route: `Product.query.order_by(sort_order, id).paginate(per_page=12, error_out=False)` — same sort as admin Phase 2 D-02 (D-03)
- Product card include shared by home + search grids: whole-card `<a>`, 1:1 thumb (or "—" placeholder), price `format_price`, out-of-stock/discontinued get `.is-unavailable` + overlay badge (D-04); in-stock cards have no overlay
- Homepage: `h1 Sản phẩm`, grid, centered pagination (Trước/Trang X/Y/Sau) only when pages>1, contact strip always visible including empty store (CONT-01/02)
- Stub routes for `/products/<int:id>` (404 on missing) and `/search` (empty-query prompt) so card/nav `url_for` never raises BuildError
- CSS: sticky `.site-header`, 44px search input (12px padding declared exception), `.product-grid` 2/3/4 columns at 768/1200, card hover accent border + soft shadow, 44px pagination touch targets, `.contact-strip` 64px top margin; total CSS 13.5KB < 20KB

## Task Commits

1. **Task 1: Public layout chain + header/search form + search route stub** — `4c3f978` (feat: header + search form layout chain), `ffa1253` (feat: search route stub + empty-query prompt), `71c4e55` (style: header + search css)
2. **Task 2: Home route + product card + index rewrite + detail stub** — `506881c` (feat)
3. **Task 3: CSS grid/card/badge-overlay/contact-strip/pagination** — `957edeb` (style)

## Files Created/Modified
- `app/templates/base.html` - added `{% block header %}` between skip-link and flash zone
- `app/templates/public/base.html` - public base extending base + including nav
- `app/templates/public/_nav.html` - sticky header with brand + GET search form
- `app/templates/public/_product_card.html` - shared product card component (thumb, name, price, status overlay)
- `app/templates/public/index.html` - rewritten: grid/empty-state + pagination + contact strip
- `app/templates/public/product_detail.html` - minimal stub (03-02 replaces)
- `app/templates/public/search.html` - empty-query prompt stub (03-03 replaces)
- `app/public.py` - home route (12/page), product_detail + search stubs
- `app/static/css/style.css` - header/search + grid/card/badge/contact-strip CSS (13.5KB total)

## Decisions Made
- Header block approach per UI-SPEC flagged decision 1: search lives only in the public chain; admin pages render no header
- Card-name 2-line clamp uses `line-height: 1.4` as a documented non-token exception (forces the clamp closed without clipping descenders)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Plan-level verify used a wrong auth route path**
- **Found during:** Plan 03-01 overall verification (after Task 3)
- **Issue:** My own verification harness asserted `GET /auth/login` → 200, but the auth blueprint registers `/login` (not `/auth/login`); the assertion failed on a URL I invented, not on plan code
- **Fix:** Corrected the harness to `GET /login`; re-ran the same assertions (home 200 no-redirect, /products/99999 404, /search 200, /admin/ redirects to /login, header form on all public pages)
- **Files modified:** none (test-harness invocation only)
- **Verification:** PLAN01_VERIFY_OK printed

**2. [Rule 3 - Blocking] Verify harness DB isolation ineffective (discovered in 03-03, affected all waves)**
- **Found during:** 03-03 Task 1 verify (root-caused during this phase)
- **Issue:** Flask-SQLAlchemy 3.1.1 creates engines eagerly in `init_app()`, so the plan's harness pattern of setting `app.config['SQLALCHEMY_DATABASE_URI']` after `create_app()` was silently ignored. This wave's verifies wrote seeded products into the gitignored `data/app.db` (later cleaned up); their assertions were data-independent/product-specific so they still passed.
- **Fix:** Harness-only — dispose + rebuild the default engine after overriding the URI (`db._app_engines[app]` + `db._make_engine`). Re-ran this plan's Task 2 verify against an isolated temp DB — green. Removed the polluted `data/app.db`.
- **Files modified:** none (test-harness invocation only); `data/app.db` deleted (gitignored runtime artifact)
- **Verification:** 03-01 TASK2 OK printed

---

**Total deviations:** 2 auto-fixed (1 test-harness path correction, 1 cross-cutting test-harness DB isolation)
**Impact on plan:** None — all plan code verified green; no scope creep, no plan redesign.

## Issues Encountered
- None during implementation. All task verify scripts passed first run.

## Next Phase Readiness
- `public/base.html` + `_nav.html` + `_product_card.html` ready to be extended by 03-02 (detail) and 03-03 (search results) without restructuring
- `product_detail.html` stub in place — 03-02 replaces with full gallery/info layout
- `search.html` stub in place — 03-03 replaces with 3-state results page

---
*Phase: 03-public-catalog-search-contact*
*Completed: 2026-08-01*

## Self-Check: PASSED

All claims verified — SUMMARY file exists, all 5 task commits present (4c3f978, ffa1253, 71c4e55, 506881c, 957edeb), plan-level verification green.
