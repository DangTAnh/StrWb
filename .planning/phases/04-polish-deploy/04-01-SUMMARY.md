---
phase: 04-polish-deploy
plan: 01
subsystem: ui
tags: [flask, jinja2, css, responsive, contrast, a11y, vietnamese]
requires:
  - phase: 03-public-catalog-search-contact
    provides: public catalog grid, detail gallery, search route, contact strip (frozen chain)
provides:
  - D-07 all 5 deferral fixes from Phase 3 (spec-sync comment, search out-of-range redirect, #B91C1C contrast, full-size gallery main image, ₫ glyph verdict)
  - D-05 CAT-04 de-emphasis verified HOLD (opacity 0.45 + badge overlay, no grayscale)
  - D-06 responsive audit at 480/768/1200 public + admin — all invariants hold, no fixes needed
affects: [Phase 4 plans 04-02/04-03, verifier]
tech-stack:
  added: []  # zero new packages (Registry Safety per 04-UI-SPEC)
  patterns: [search out-of-range redirect mirrors home() using raw page (manual pagination clamps), full-size filename served for gallery main image at 2x DPR]
key-files:
  created: []
  modified: [app/public.py, app/templates/public/product_detail.html, app/static/css/style.css]
key-decisions:
  - "D-07 #2 redirect compares the raw request page (page > pagination.pages) because _manual_pagination clamps page to [1, pages] — pagination.page > pagination.pages can never be true; mirrors home() behavior"
  - "D-07 #4 keeps url_for('static', ...) wrappers; only the asset name swaps to filename (main + data-src) while thumbnails keep thumb_filename"
  - "D-07 #3 contrast: #B91C1C measures 6.19:1 on #F9FAFB (plan estimate ~5.5:1) — passes AA with margin"
  - "D-07 #5 verdict: PASS — Noto Sans VN (leading fallback font) carries U+20AB (₫); no fallback font appended"
requirements-completed: [CAT-04, CAT-06]
duration: 20min
completed: 2026-08-02
---

# Phase 4 Plan 1: Polish UI Summary

Resolved all five Phase 3 deferral items (D-07), verified the CAT-04 out-of-stock de-emphasis holds unchanged (D-05), and audited public + admin responsiveness at 480/768/1200 (D-06) — no responsive violations found, so zero fixes were required. Phase 4 adds no pages, components, or libraries; every change is a CSS comment/color, a Jinja asset swap, or a route behavior mirror.

## Performance

- **Duration:** 20 min
- **Started:** 2026-08-01T17:42:09Z
- **Completed:** 2026-08-02T00:05:00Z
- **Tasks:** 5 completed (4 code, 1 verify-only)
- **Files modified:** 3

## Accomplishments
- **D-07 #1 (spec-sync):** `/* Declared spec addition (04-UI-SPEC D-07 #1): keeps the Messenger CTA a >=44px touch target... */` added directly above `.contact-strip .btn { min-width: 200px }`; rule value unchanged
- **D-07 #2 (search redirect):** `public.search` now mirrors `home()` — when `pagination.total and page > pagination.pages` it returns a 302 to the last valid page (keeping `q`), and `page < 1` redirects to `page=1`; no more silent clamp
- **D-07 #3 (contrast):** `.out-of-stock-note` darkened `#DC2626` → `#B91C1C` (red-700); measured **6.19:1** on `#F9FAFB` (≥4.5:1 AA). One token on the same red ramp; `--destructive` token and the "Sản phẩm hiện đang hết hàng." copy unchanged
- **D-07 #4 (2x DPR gallery):** detail main `<img>` + gallery swap `data-src` now serve `img.filename` (re-encoded JPEG q85, ≤2000px) instead of the 400px thumb, with `width/height=440` matching the desktop box; 72×72 thumbnails keep `thumb_filename`; swap JS unchanged
- **D-07 #5 (₫ glyph):** verdict **PASS** — `body` font-family leads with `'Noto Sans VN'`, which carries U+20AB (Dong sign); no fallback append needed
- **D-05 (CAT-04 HOLD):** `.is-unavailable .product-card-thumb img { opacity: 0.45 }` + `.badge-overlay` intact; `grayscale` absent from CSS; grid order unchanged (`sort_order ASC, id ASC`)
- **D-06 (responsive audit):** all invariants HOLD — grid `repeat(2/3/4, 1fr)` at 768/1200, search `max-width: 480px; margin-left: auto` on tablet, gallery `360px`/`440px`, container `max-width: 1200px`, `.contact-strip .btn { min-width: 200px }` fits in 288px at 320px viewport, admin table wrapped in `.table-scroll { overflow-x: auto }`, form inputs 44px, buttons unclipped
- CSS total **16.0KB** < 20KB budget

## Task Commits

1. **Task 1: D-07 #1 spec-sync comment + #5 ₫ glyph check** - `e4660bf` (style)
2. **Task 2: D-07 #2 search out-of-range redirect khớp home** - `63a2616` (feat)
3. **Task 3: D-07 #3 contrast `.out-of-stock-note` → `#B91C1C`** - `b7851c5` (style)
4. **Task 4: D-07 #4 gallery main image dùng bản gốc `filename`** - `4338f88` (feat)
5. **Task 5: D-05 verify CAT-04 + D-06 responsive audit** - no commit (verify-only; no code changes required)

## Files Created/Modified
- `app/public.py` - `search()` out-of-range redirect mirroring `home()` (D-07 #2)
- `app/templates/public/product_detail.html` - main img + `data-src` serve `filename` at 440px; thumbs keep `thumb_filename` (D-07 #4)
- `app/static/css/style.css` - spec-sync comment (D-07 #1), `#B91C1C` out-of-stock note (D-07 #3); 16.0KB total

## Decisions Made
- Redirect check uses the **raw** request `page` (`page > pagination.pages`) rather than `pagination.page` because `_manual_pagination` clamps; this is the only way to reproduce `home()`'s redirect semantics for `search`
- Keep the `url_for('static', filename='uploads/' + ...)` wrapper on every gallery reference; only the referenced asset property changes

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan Task 2 verify asserted `pagination.page > pagination.pages` and expected `page=2` — both impossible**
- **Found during:** 04-01 Task 2 verify
- **Issue:** (a) The plan's source assertion required the literal `pagination.page > pagination.pages`, but `_manual_pagination` clamps `page` to `[1, pages]`, so `pagination.page > pagination.pages` can never be true and the redirect would never fire. The functional intent (302 on out-of-range) requires comparing the raw request `page`. (b) The functional assertion expected `page=2` in the Location, but 30 seeded products at 12/page = 3 pages, so the last valid page is 3.
- **Fix:** Implemented `if pagination.total and page > pagination.pages: return redirect(url_for('public.search', q=q, page=pagination.pages))` (raw page). Verify harness asserted `page > pagination.pages` and `page=3`. Also verified `page=0` → 302 `page=1`.
- **Files modified:** `app/public.py` (production), harness assertion corrected
- **Verification:** TASK2_OK printed

**2. [Rule 1 - Bug] Plan Task 4 verify asserted bare `{{ img.filename }}` / `{{ img.thumb_filename }}` — ignores the `url_for` wrapper**
- **Found during:** 04-01 Task 4 verify
- **Issue:** The template correctly renders static URLs via `url_for('static', filename='uploads/' + img.xxx)`. The plan's literal-string assertions (`data-src="{{ img.filename }}"`, `src="{{ img.thumb_filename }}"`) would only match a bare, URL-broken reference.
- **Fix:** Kept the `url_for` wrapper (correct production behavior); harness asserted the wrapped form for both `data-src`→`filename` and thumb `src`→`thumb_filename`, plus main-img `filename` + `width/height=440`.
- **Files modified:** `app/templates/public/product_detail.html` (production, as planned), harness assertion corrected
- **Verification:** TASK4_OK printed

**3. [Rule 1 - Bug] Plan Task 5 verify asserted `/?page=2` → 200 and used `/auth/login`**
- **Found during:** 04-01 Task 5 verify
- **Issue:** (a) With the plan's 12 seeded products there is only 1 page, so `/?page=2` correctly 302-redirects to `/?page=1` (home's out-of-range behavior, `public.py:39-40`) — a 200 was impossible. (b) The auth blueprint registers `/login`, not `/auth/login` (same issue documented in Phase 3).
- **Fix:** Seeded 24 products so page 2 is real (`/?page=2` → 200) and additionally asserted `/?page=99` → 302. Used `/login` for the login render check.
- **Files modified:** none (test-harness invocation only)
- **Verification:** TASK5_OK printed

---

**Total deviations:** 3 auto-fixed (all plan-verify harness bugs; production code matches the plan's intent)
**Impact on plan:** Zero production-code scope creep — all fixes are correct implementations of the plan's stated intent.

## Issues Encountered
- All three deviations were self-contradictions in the plan's verify scripts (dead-code source assertion, literal-string template asserts ignoring `url_for`, page-count/routing mistakes), not product defects. Each was resolved by asserting the actual correct behavior.

## Next Phase Readiness
- Public chain fully polished: gallery serves sharp full-size images (2x DPR), search pagination redirects consistently, out-of-stock note meets AA, responsive invariants verified at all breakpoints
- 04-02 (deploy) and 04-03 (hardening + verify) can build on the frozen codebase; no further UI changes expected in this phase

---
*Phase: 04-polish-deploy*
*Completed: 2026-08-02*

## Self-Check: PASSED

All claims verified — SUMMARY file exists, all 4 task commits present (e4660bf, 63a2616, b7851c5, 4338f88), Task 5 verify-only (no diff), all task verifies green against isolated temp DBs, `data/app.db` unchanged (1 product "Áo sơ mi", 0 image rows).
