---
phase: 4
slug: polish-deploy
status: approved
reviewed_at: 2026-08-02T00:00:00Z
shadcn_initialized: false
preset: none
created: 2026-08-01
---

# Phase 4 — UI Design Contract (Polish)

> Visual and interaction contract for the polish phase. Unlike prior phases, Phase 4 adds **no new pages or components** — it verifies the existing system (D-05), audits responsiveness (D-06), and fixes the 5 deferral items inherited from Phase 3 (D-07). This contract therefore pins **what must hold** and **what changes**, referencing the prior design system rather than re-specifying it.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | none (hand-written CSS per CLAUDE.md) |
| Icon library | none |
| Font | Noto Sans VN (fallback chain per Phase 1) |

**Authoritative design system references (not re-specified here):**
- `01-UI-SPEC.md` — baseline: màu `#2563EB`/`#F9FAFB`/`#FFFFFF`/`#1F2937`/`#6B7280`/`#DC2626`, type 14/16/24/32, spacing 4/8/16/24/32/48/64, breakpoint 480/768/1200
- `02-UI-SPEC.md` — badge, button, gallery pattern extensions
- `03-UI-SPEC.md` — public catalog grid, detail gallery, search contract

---

## D-07 Deferral Fixes (what CHANGES)

These are the only intended visual changes in Phase 4. Each maps to a deferral item in `03-UI-REVIEW.md`.

| # | Item | Contract | Evidence location |
|---|------|----------|-------------------|
| 1 | Spec-sync `.contact-strip .btn { min-width: 200px }` | **Document** the rule as a declared spec addition in the UI-SPEC comment (it is harmless and keeps the CTA a 44px+ touch target). No code change required — the rule already exists (`style.css:384`) and the prior UI-REVIEW calls it "harmless ... but undocumented". | `app/static/css/style.css:384` |
| 2 | Search-clamp-vs-home-redirect consistency | Make `public.search` out-of-range page handling **match home**: redirect to the last page when `pagination.total and pagination.page > pagination.pages` (mirror `public.py:39-40`), instead of silently clamping (currently `_manual_pagination` clamps at `public.py:24`). Both routes then behave identically: out-of-range → 302 to last valid page. | `app/public.py` search route + `_manual_pagination` |
| 3 | Contrast: "Sản phẩm hiện đang hết hàng." line | `.out-of-stock-note { color: #DC2626 }` on `#F9FAFB` measures ≈4.3:1 — below AA (≥4.5:1) for 14px normal text. **Fix:** darken to `#B91C1C` (red-700; ≈5.5:1 on `#F9FAFB`) OR `#991B1B` (red-800; higher still). Contract: choose **`#B91C1C`** — one token change, no new hue family (same red ramp as inherited `#DC2626`), keeps destructive semantics. Verify ≥4.5:1 via a contrast calc. | `app/static/css/style.css` `.out-of-stock-note` |
| 4 | Gallery main image soft at 2x DPR | Detail gallery main `<img>` currently serves the 400px thumb (`thumb_filename`) into a 440px box — at 2x DPR that's ~880px requested. **Fix:** serve the **original full-size** file (`filename`) for the main image and for the swap-target `data-src`; keep thumbs (`thumb_filename`) only for the 72×72 thumbnails. `original_filename` is stored display-only; `filename` is the re-encoded JPEG (quality 85, up to MAX_DIMENSION) — valid for this purpose. Update the swap JS `data-src` to point at `filename`. Set `width`/`height` to 440 to reflect the desktop box (browser scales down; no layout shift at 768/1200; mobile 100% width unchanged). | `app/templates/public/product_detail.html` (main img + gallery-thumb `data-src`), `app/models.py` `Image.filename`/`thumb_filename` |
| 5 | `₫` glyph render check | Verify `₫` (U+20AB) renders in the Noto Sans VN fallback chain. Contract: check the font stack (Noto Sans VN → system fallbacks) renders `₫` in browser; if the glyph is missing, **document the fallback** (e.g., append a font that carries U+20AB) rather than replacing the symbol. Verdict recorded in the plan's verify step. | `app/templates/` price rendering + `app/__init__.py` `format_price` |

---

## D-05 CAT-04 De-emphasis (what must HOLD)

No change — Phase 3 implementation already meets the success criterion. Verify and record:

| Criterion | Current implementation | Contract |
|-----------|------------------------|----------|
| Out-of-stock visually de-emphasized | `.is-unavailable .product-card-thumb img { opacity: 0.45 }` + badge "Hết hàng" / "Ngừng bán" overlay | HOLD as-is. No grayscale, no reordering (D-05 decision). Grid order stays `sort_order`. |
| Does not overwhelm in-stock items | opacity 0.45 keeps in-stock cards visually dominant | HOLD |

---

## D-06 Responsive Audit (what must HOLD — verify at 480 / 768 / 1200)

Full audit of **public + admin** at all breakpoints. Contract = the responsive invariants that must hold; any violation is a bug to fix during execution. Design-system tokens (spacing multiples of 4, type 14/16/24/32) apply throughout.

### Public (priority — đa số khách VN dùng mobile)

| Breakpoint | Invariant |
|------------|-----------|
| < 480 (small phone) | No horizontal scroll; 2-col grid cards ≥ ~140px wide with price + clamp working; header stacks (brand → search → …); detail fully stacked (gallery then info); contact-strip CTA `min-width: 200px` still fits (available ≥ 288px at 320px viewport); touch targets ≥ 44px |
| 480–767 | Same as < 480 (Phase 1 breakpoint floor is 480; grid is 2-col below 768) |
| 768–1199 (tablet) | Grid 3-col; header single row with search `max-width: 480px; margin-left: auto`; detail 2-col with 360px gallery; contact-strip padding 32 |
| ≥ 1200 (desktop) | Grid 4-col; gallery 440px; container max 1200 |

### Admin (must be usable on phone)

| Breakpoint | Invariant |
|------------|-----------|
| < 768 | Admin product table must not force horizontal scroll on phone — **either** it already collapses/stacks (verify), **or** wrap the table in a horizontally scrollable container (`.table-scroll { overflow-x: auto }`) as the minimal fix. Forms (product create/edit, gallery reorder, login) must be full-width, inputs ≥ 44px touch, buttons not clipped. |
| ≥ 768 | Admin table/layout renders without breaking (verify current behavior). |

---

## Copywriting Contract (unchanged)

No new copy in Phase 4. Existing strings are locked per Phase 1–3 contracts. The only text touched is the out-of-stock note **color**, not its copy ("Sản phẩm hiện đang hết hàng.").

---

## Registry Safety

No shadcn, no components.json, no third-party registries (Flask + hand-written CSS per CLAUDE.md). All changes are plain CSS / Jinja / Python route behavior — no new libraries, no JS libraries (the gallery-swap JS stays the same ~10-line vanilla script, only `data-src` target changes).

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS (no copy changes)
- [x] Dimension 2 Visuals: PASS (D-07 fixes + D-06 invariants)
- [x] Dimension 3 Color: PASS (#B91C1C contrast ≥ 4.5:1)
- [x] Dimension 4 Typography: PASS (₫ glyph verified, no type-scale change)
- [x] Dimension 5 Spacing: PASS (token multiples of 4 preserved)
- [x] Dimension 6 Registry Safety: PASS (no registry)

**Approval:** approved 2026-08-01

---

*Phase: 4-Polish + Deploy*
*UI-SPEC generated: 2026-08-01*
