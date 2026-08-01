---
phase: 03-public-catalog-search-contact
plan: 03
subsystem: ui
tags: [flask, jinja2, search, diacritics, unicodedata, vietnamese]
requires:
  - phase: 03-public-catalog-search-contact
    plan: 01
    provides: public/base.html + _nav.html GET search form (pre-fill q), _product_card.html shared card, search route stub, pagination CSS
provides:
  - normalize_search_text: NFD → strip combining marks (Mn) → casefold (D-11)
  - _manual_pagination: SimpleNamespace mirroring Query.paginate template fields
  - full /search route: in-Python filter over name OR description, 12/page, clamps page bounds, preserves q
  - 3-state search results page (empty-query prompt / results / no-results) + .result-count CSS
affects: [Phase 4]
tech-stack:
  added: []  # unicodedata + types are stdlib; zero new packages (T-03-SC)
  patterns: [in-Python Unicode normalization for diacritic-insensitive search, manual pagination namespace for non-SQL filtering, shared-card results grid]
key-files:
  created: []
  modified: [app/public.py, app/templates/public/search.html, app/static/css/style.css]
key-decisions:
  - "In-Python filter over the whole catalog (UI-SPEC flagged decision 7) — no stored normalized column, no SQL LIKE; upgrade path documented (normalized column at write time when catalog grows)"
  - "Result count uses pagination.total (phase-wide total) so a multi-page result shows the true match count, consistent with the plan's Task 1 verify (13 matches → '13 sản phẩm')"
  - "Search page omits the contact strip (UI-SPEC flagged decision 8)"
requirements-completed: [SRCH-01]
duration: 12min
completed: 2026-08-01
---

# Phase 3 Plan 3: Search Summary

Diacritic-insensitive Vietnamese search (SRCH-01, D-11): `normalize_search_text` (NFD → strip combining marks → casefold) applied to both the keyword and each product's name/description, filtering in Python over the small catalog (no new DB column, no SQL LIKE), with a manual pagination namespace so the results page reuses the exact home-grid pagination markup, all three states (empty-query prompt / results / no-results), and pagination links that preserve `q`.

## Performance

- **Duration:** 12 min
- **Started:** 2026-08-01T14:10:30Z (approx)
- **Completed:** 2026-08-01T14:22:30Z (approx)
- **Tasks:** 2 completed
- **Files modified:** 3

## Accomplishments
- `normalize_search_text('áo') == 'ao'`, `normalize_search_text('Áo') == 'ao'`, `normalize_search_text('QUẦN') == 'quan'` — verified by unit assertions (D-11)
- `/search` route: strips `q`, normalizes it, filters `Product` (sorted sort_order ASC + id ASC) where the normalized name OR description contains the normalized keyword; `p.name or ''` / `p.description or ''` guard the nullable description (verified: product with `description=None` doesn't crash and still matches by name)
- `_manual_pagination(page, per_page, total)` returns a `SimpleNamespace` exposing the exact fields home uses (`page/pages/has_prev/has_next/prev_num/next_num`), so `search.html` reuses the same pagination markup; `pagination.items` assigned after construction
- Search page states: blank/whitespace `q` → "Tìm kiếm sản phẩm / Vui lòng nhập từ khóa để tìm kiếm." prompt; matches → `{total} sản phẩm cho “{q}”` + shared `_product_card` grid; zero matches → "Không tìm thấy sản phẩm" + CTA; both empty states link "Xem tất cả sản phẩm" → home
- Pagination links carry `q` (`url_for('public.search', q=q, page=N)`); nav input pre-fills the active query (D-09); no contact strip on the search page (flagged decision 8)
- CSS: `.result-count` 14px #6B7280 margin-bottom 48px; total style.css 15.6KB < 20KB
- Zero new dependencies; no schema change (T-03-SC)

## Task Commits

1. **Task 1: normalize + python filter + paginate** — `d38b76a` (feat)
2. **Task 2: search.html 3 states + result-count CSS** — `7e3df63` (feat: page), `b603c30` (style)

## Files Created/Modified
- `app/public.py` - `normalize_search_text`, `_manual_pagination`, full `/search` route
- `app/templates/public/search.html` - 3-state results page (replaces stub)
- `app/static/css/style.css` - `.result-count` (15.6KB total)

## Decisions Made
- In-Python filter over the whole catalog per UI-SPEC flagged decision 7 — single admin, low volume; documented upgrade path (store normalized columns at write time + SQL LIKE) if the catalog grows
- Result count renders `pagination.total` (phase-wide total) rather than `products|length` (current-page count): the plan explicitly permits either, but the plan's Task 1 verify asserts "13 sản phẩm" for 13 matches across 2 pages, which only `pagination.total` produces (page 1 would show 12 via `products|length`)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Verify harness DB isolation ineffective (Flask-SQLAlchemy eager engine creation)**
- **Found during:** 03-03 Task 1 verify (first run failed at result-count)
- **Issue:** The plan's verify scripts set `app.config['SQLALCHEMY_DATABASE_URI'] = sqlite:///<tempfile>` AFTER `create_app()` runs. Flask-SQLAlchemy 3.1.1 creates engines eagerly in `init_app()` ("Changes to application config after this call will not be reflected"), so the override was silently ignored and every verify hit the real `data/app.db`. My 03-03 runs then saw 43 accumulated test products instead of the 13 seeded, failing the result-count assertion. Earlier 03-01/03-02 verifies also wrote test data into `data/app.db` (their assertions were product-specific/data-independent so they still passed).
- **Fix:** Prepend a harness helper that overrides the URI AND disposes/rebuilds the default engine from current config (`db._app_engines[app]` dispose + `db._make_engine(None, {**SQLALCHEMY_ENGINE_OPTIONS, 'url': uri}, app)`). Production code unchanged. Re-ran ALL verifies (03-01 T2, 03-02 T1, 03-03 T1/T2) against isolated temp DBs — all green. Removed the polluted gitignored `data/app.db` (test junk; regenerated by `flask init-db`).
- **Files modified:** none (test-harness invocation only); `data/app.db` deleted (gitignored runtime artifact)
- **Verification:** TASK1_OK / TASK2_OK / 03-01 TASK2 OK / 03-02 TASK1 OK / PHASE3_SMOKE_OK printed

**2. [Rule 1 - Bug] Plan's Task 1 verify asserted the wrong item on search page 2**
- **Found during:** 03-03 Task 1 verify
- **Issue:** With 13 matches sorted by sort_order (1,4,5,…,15), page 1 holds items 1–12 and page 2 holds only the 13th, 'Áo lửng' (sort_order 15). The plan script asserted `'Áo măng tô' in h` for `?q=ao&page=2`, but 'Áo măng tô' (sort_order 13) is item 11 on page 1. The production route/pagination is correct.
- **Fix:** Corrected the harness assertion to `'Áo lửng' in h and 'Trang 2 / 2' in h`; also verified the pagination link carries `q` (`q=ao&page=1`). No production change.
- **Files modified:** none (test-harness invocation only)
- **Verification:** TASK1_OK printed

---

**Total deviations:** 2 auto-fixed (1 blocking test-harness DB isolation, 1 test-script expected-value bug)
**Impact on plan:** Both fixes were harness-side; production code matches the plan exactly. No scope creep, no plan redesign.

## Issues Encountered
- The plan's `search.html` contract note offered `products|length` OR `pagination.total` for the result count. The Task 1 verify's "13 sản phẩm" for a 2-page result requires `pagination.total`; `products|length` would render "12 sản phẩm" on page 1. Chose `pagination.total` — consistent with the plan's own verify.

## Next Phase Readiness
- Search (SRCH-01), catalog list (CAT-01/03), detail (CAT-02/03/05), and Messenger contact (CONT-01/02) all complete — Phase 3 is feature-complete
- Phase 4 (Polish + Deploy) can build on the now-frozen public chain: `public/base.html`, `_nav.html`, `_product_card.html`, detail gallery, and search results page

---
*Phase: 03-public-catalog-search-contact*
*Completed: 2026-08-01*

## Self-Check: PASSED

All claims verified — SUMMARY file exists, all 3 task commits present (d38b76a, 7e3df63, b603c30), all task verifies + full smoke test green against isolated DBs.
