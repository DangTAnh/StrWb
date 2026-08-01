# Phase 3 — UI Review

**Audited:** 2026-08-01
**Baseline:** 03-UI-SPEC.md (Approval: flagged) + 01-UI-SPEC.md baseline design system + 02-UI-SPEC.md extensions
**Screenshots:** not captured (no dev server at 3000/5173/8080/5000/8000) — code audit + Flask test-client render verification
**Registry audit:** N/A — no shadcn/components.json (Flask + hand-written CSS per CLAUDE.md)

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Design System Conformance | 3/4 | Tokens/type/color exact — no new hex, accent reservations honored, CSS 15.8KB < 20KB; search-input placeholder color left at browser default (spec pins #6B7280) |
| 2. Copywriting | 4/4 | All contract strings verbatim Vietnamese; no generic labels; orthography correct; empty/error states carry actionable copy |
| 3. Responsive Behavior | 4/4 | Grid 2/3/4 at 480/768/1200, header stack→row, detail stack→2-col 360/440px — all exact |
| 4. State & Feedback | 3/4 | Empty/disabled/error/hover/focus states complete; prompt-state page heading misrepresents ("Kết quả tìm kiếm" renders when no query was run) |
| 5. Spacing & Hierarchy | 3/4 | Token-adherent except contact-strip body→CTA gap is 16px vs declared 24px; heading-order regression h1→h3→h2 on home |
| 6. Accessibility Basics | 3/4 | alt/labels/focus-visible/touch-targets/contrast solid; placeholder color drift and marginal red-line contrast; heading levels skip |

**Overall: 20/24**

---

## Top 3 Priority Fixes

1. **Search prompt-state heading misrepresents the state (MEDIUM)** — `search.html:5,7-11`. When `q` is empty the page renders h1 "Kết quả tìm kiếm" *above* the empty-state h2 "Tìm kiếm sản phẩm" — the page heading claims results exist when no search ran. Fix: make the h1 conditional — render "Tìm kiếm sản phẩm" as the h1 for the prompt state and keep "Kết quả tìm kiếm" only when a query was submitted (drop the duplicated empty-state h2). Verified: `/search` (no q) renders both headings.
2. **Search-input placeholder color not set to the declared token (MEDIUM)** — `style.css:348-352`. Spec type map pins placeholder #6B7280; no `::placeholder` rule exists, so the browser default gray renders (Chrome ≈ #757575 at 54% opacity) — a token drift against the declared muted-gray system and an uncontrolled contrast value. Fix: `.search-form input::placeholder { color: #6B7280; opacity: 1; }`.
3. **Heading-order regression h1→h3→h2 on the public grid (LOW, a11y)** — `_product_card.html:16`, `index.html:25`. Sequence is h1 "Sản phẩm" → h3 product names → h2 "Liên hệ mua hàng": levels skip h2 and then regress. Spec declared card names as `h3`, so this is spec-faithful but imperfect. Fix: insert a `visually-hidden` h2 "Danh sách sản phẩm" before the grid on `index.html` (and `search.html`), restoring h1→h2→h3→h2 with zero visual change.

---

## Detailed Findings

### Pillar 1: Design System Conformance (3/4)

System extension is exact: no new hex values (all Phase 3 colors reuse the Phase 1+2 token set), Noto Sans VN stack unchanged, type scale 14/16/24/32 + weights 400/600 respected (Phase 3 additions use only these), accent reserved for the declared elements (price `style.css:378,405`, Messenger CTA + search submit `.btn-primary`, active gallery-thumb border `style.css:401`, card hover border `style.css:365`, back link, brand hover `style.css:346`, focus ring), plain CSS 15.8KB under the 20KB target, zero JS libraries (one ~10-line inline swap script). Card-name clamp line-height 1.4 exception documented inline (`style.css:375`).

- **MEDIUM** — Search-input placeholder color unset (`style.css:348-352`): spec §Typography pins "placeholder #6B7280"; no `::placeholder` rule anywhere in the file (grep confirms). Browser default gray renders instead. (See Top Fix 2.)
- **LOW** — `.contact-strip .btn { min-width: 200px }` (`style.css:384`) is an undeclared addition to the spec's component contract. Harmless (button stays 44px touch, centered), but undocumented.
- **INFO** — 400px thumb asset served into a 440px gallery box at 2x DPR is soft on desktop retina — spec Decision #4, already deferred to a later phase. Not a defect.

### Pillar 2: Copywriting (4/4)

Every contract string is verbatim and idiomatic Vietnamese: "Mua qua Messenger", "Tìm" (aria-label "Tìm kiếm"), "Sản phẩm", "Liên hệ mua hàng", "Đặt câu hỏi hoặc đặt mua trực tiếp qua Messenger.", "Chưa có sản phẩm nào", "Cửa hàng đang cập nhật sản phẩm mới. Vui lòng quay lại sau.", "Không tìm thấy sản phẩm", "Không có kết quả cho “{q}”. Kiểm tra lại từ khóa hoặc duyệt tất cả sản phẩm.", "Vui lòng nhập từ khóa để tìm kiếm.", "Xem tất cả sản phẩm", "Sản phẩm hiện đang hết hàng.", "Quay lại", "Tìm kiếm sản phẩm", "Kết quả tìm kiếm", result count "N sản phẩm cho “q”" (`search.html:13`), thumbnail aria-label "Xem ảnh {n}" (`product_detail.html:18`). Titles exact: "{name} — Cửa hàng", "Tìm kiếm — Cửa hàng". Price format `150.000₫` via `format_price` (`app/__init__.py:63-65`) confirmed. Vietnamese curly quotes consistent. No generic/placeholder copy anywhere. The heading-redundancy issue is a state-structure matter, not copy — scored under Pillar 4.

### Pillar 3: Responsive Behavior (4/4)

All breakpoint behavior exact per spec §Responsive:
- **Mobile (<768):** grid 2-col gap 16 (`style.css:361`), header column-stacked with full-width search (`style.css:344,347`), detail stacked (`style.css:387`), page padding 16 (`style.css:36`), price Display 32 (`style.css:405`).
- **Tablet (≥768):** grid 3-col gap 24 (`style.css:362`), header single row with search `max-width: 480px; margin-left: auto` (`style.css:356-358`), detail 2-col with 360px gallery (`style.css:416-419`), contact-strip padding 32 (`style.css:381`).
- **Desktop (≥1200):** grid 4-col (`style.css:363`), gallery 440px (`style.css:420`), container max 1200 (`style.css:36`).

Grid/header/detail were the three spec'd layout behaviors; all verified by code inspection. No overflow risk at 320px (2-col cards, price fits; CTA min-width 200px still < 288px available).

### Pillar 4: State & Feedback (3/4)

State coverage is otherwise complete: hover states (card border+shadow `style.css:365`, brand `style.css:346`, buttons, pagination underline via global `a:hover`), `:focus-visible` rings on every new interactive element following the Phase 2 `b763980` pattern (card `style.css:366`, thumb `style.css:402`, search input `style.css:352`, buttons `style.css:170`, links + back-link inherit global `a:focus-visible` `style.css:24`), empty states for all three grid conditions (home no-products `index.html:18-23`, search no-results `search.html:27-31`, search prompt `search.html:7-11`), pagination disabled spans with `aria-disabled="true"` (`index.html:12,15`, `search.html:20,23`), and 404/500 error templates render correct chrome per route (verified via test client: public 404/500 include the search header, admin/auth 404/500 do not — WR-05).

- **MEDIUM** — Prompt-state misrepresentation: with no query, h1 still reads "Kết quả tìm kiếm" (`search.html:5`) above the "Tìm kiếm sản phẩm" prompt (`search.html:7-11`). The page presents results-state chrome for a state where no results exist. (See Top Fix 1.)
- **INFO** — Search out-of-range page clamps silently (`public.py:75` `_manual_pagination` clamps `page` to `pages`) while home redirects to the last page (`public.py:39-40`). Both render a valid page; purely an internal inconsistency.

### Pillar 5: Spacing & Hierarchy (3/4)

Phase 3 spacing is token-adherent (all multiples of 4; the single 12px non-token search-input padding is declared as a spec exception `style.css:349`). Verified values: header inner gap 8 (`style.css:344`), grid gap 16/24 (`style.css:361-362`), card body 16 (`style.css:372`), price→name 4 (`style.css:378`), badge overlay inset 8 (`style.css:371`), thumbs gap 8 (`style.css:395`), detail gap 32 (`style.css:387,417`), contact-strip margin-top 64 (`style.css:381`) + padding 32, result-count → grid 48 (`style.css:423`), meta rows 4-gap (`style.css:410`), description section 24 (`style.css:413`).

- **LOW** — Contact-strip body→CTA gap is 16px, spec declares 24px: `.contact-strip p { margin-bottom: 16px }` (`style.css:383`) vs spec §Spacing "lg | 24px | … contact-strip button margin-bottom". Fix: `margin-bottom: 24px`.
- **LOW** — Heading hierarchy regression (see Top Fix 3): h3 card names precede the h2 "Liên hệ mua hàng" on home and the h2 "Mô tả" on detail; h2 is skipped between h1 and h3.

### Pillar 6: Accessibility Basics (3/4)

Solid baseline: `lang="vi"` + `charset` + skip link (`base.html:2,4,13`), single-focus-target product card `<a>` with visible 2px accent focus (`style.css:366`), visually-hidden `<label>` + `type="search"` + `role="search"` (`_nav.html:4-7`), gallery thumbnails are real `<button>`s with `aria-label="Xem ảnh {n}"` and `aria-current` on the active (`product_detail.html:18-19`, JS swap at `product_detail.html:53-70`), touch targets ≥44px (search input 44, `.btn` 44, pagination links `min-height: 44px` `style.css:380`, thumbs 72×72), image `alt` = product name throughout, `width/height` + `loading="lazy"` on cards/thumbs (main detail image intentionally not lazy — correct for LCP), badge palette and #6B7280 muted text verified AA (≈4.6:1).

- **MEDIUM** — Placeholder color drift (see Top Fix 2): the spec's chosen #6B7280 (≈4.6:1) is not applied; the browser default is an uncontrolled gray.
- **LOW** — Out-of-stock red line #DC2626 on #F9FAFB ≈ 4.3:1 (`style.css:408`), marginally below AA for 14px normal text. Inherited destructive token, deliberately pinned by spec Decision #5 — noted, not a Phase 3 regression.
- **INFO** — Thumbnail `alt` repeats the product name for every thumb (spec Decision: "all carry product name for simplicity") — screen readers announce duplicate text per image; spec chose this deliberately, so no action.

---

## Deferred to Phase 4 (Polish)

- Normalize the search-input placeholder to #6B7280 (or accept browser default and document it) — one-line CSS.
- Document or drop `.contact-strip .btn { min-width: 200px }` (`style.css:384`) in the spec.
- Strip `q` in the nav input (`_nav.html:6`) to match the handler's `.strip()` (`public.py:63`) — currently a query typed with surrounding spaces shows raw in the input but stripped in the result count.
- Align search out-of-range page handling with home's redirect (`public.py:75` vs `:39-40`) — cosmetic consistency.
- Consider a mid-size image render (~880px) for the 440px detail gallery at 2x DPR — spec Decision #4 upgrade path.
- Confirm `₫` (U+20AB) renders in the Noto Sans VN fallback chain.

---

## Registry Safety

No shadcn, no components.json, no third-party registries (Flask + hand-written CSS per CLAUDE.md). All Phase 3 components (site header + search, product card, badge overlay, gallery-detail, contact strip, Messenger button) are hand-rolled; the single inline gallery-swap JS is hand-written vanilla (~10 lines), no library. No flags.

---

## Verification Method

Code-only audit (no dev server at 3000/5173/8080/5000/8000) plus a Flask test-client render pass over every Phase 3 route/state (in-memory app; real `data/app.db` was temporarily seeded during the pass and restored to its pre-audit single-product state afterward). Confirmed rendered correctly: home grid + contact strip + pagination hidden at 1 page; home `?page=2` → 302 last page (WR-01); detail D-08 order, Messenger CTA, out-of-stock red line only for `out_of_stock`, empty brand/measurements/description rows omitted; back link same-origin/fallback (WR-03); search diacritic/casefold/description match, prompt + no-results + result-count states (WR-02), `q` preserved in nav input and pagination; gallery thumbs only when >1 image with `is-active` + `aria-current`; 404/500 dynamic `{% extends %}` (WR-05) — public chrome on public routes, no header on admin/auth routes, no stack trace exposed.

---

## Files Audited

- `app/templates/base.html` (header block + flash + footer)
- `app/templates/public/base.html`, `public/_nav.html`, `public/_product_card.html`
- `app/templates/public/index.html`, `public/product_detail.html`, `public/search.html`
- `app/templates/errors/404.html`, `errors/500.html` (WR-05 dynamic extends)
- `app/static/css/style.css` (Phase 3 additions at `style.css:342-423`)
- `app/public.py` (search normalization, pagination, back_url)
- `app/__init__.py` (`format_price`, `current_year`, error handlers)
- `app/models.py` (`status`, `primary_image`, `thumb_filename`)
- `app/image_utils.py` (thumbnail pipeline — confirms all uploads re-encoded to `.jpg`, so `thumb_filename` never returns None for a stored image)

---

**Overall verdict:** Highly spec-faithful and functionally verified (20/24) — the Phase 3 frontend renders exactly to contract across all four routes, all three responsive tiers, and all grid/search/error states. No HIGH or blocking findings; the outstanding items are one genuine state-presentation flaw (prompt heading), one design-token miss (placeholder color), and a small cluster of spacing/a11y polish. All non-blocking; this UI is safe to inherit by Phase 4.

---

## Fix Applied

All 5 in-scope findings fixed; each verified with a Flask test_client render probe against an isolated temp DB (real `data/app.db` untouched). Deferred Phase 4 items unchanged.

| Finding | Commit | Status |
|---------|--------|--------|
| UI-01 | `5304eb6` | fixed — search h1 is conditional: "Tìm kiếm sản phẩm" for the prompt state, "Kết quả tìm kiếm" only after a query runs; duplicate empty-state h2 dropped |
| UI-02 | `3904490` | fixed — `.search-form input::placeholder { color: #6B7280; opacity: 1; }` pins the spec token |
| UI-03 | `c0c38a9` | fixed — `.contact-strip p` margin-bottom 16px → 24px per spec §Spacing |
| UI-04 | `d2389a1` | fixed — visually-hidden h2 "Danh sách sản phẩm" before the grid on `index.html` and `search.html` restores h1→h2→h3 |
| UI-05 | `d02c4ba` | fixed — nav search input uses the route-stripped `q` (single source); raw `request.args` fallback only when `q` is undefined |

_Fixed: 2026-08-01T15:26:28Z_
_Fixer: Claude (gsd-code-fixer)_
