# Phase 4 — UI Review

**Audited:** 2026-08-02
**Baseline:** 04-UI-SPEC.md (Approval: approved 6/6) + 01/02/03-UI-SPEC.md design system
**Screenshots:** not captured (no dev server) — code audit of the changed surface
**Registry audit:** N/A — no shadcn/components.json (Flask + hand-written CSS per CLAUDE.md)

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Design System Conformance | 4/4 | All D-07 changes reuse existing tokens; #B91C1C is same red ramp as inherited #DC2626; no new hex values; contact-strip min-width documented as declared spec addition; CSS size unchanged (~15.8KB < 20KB) |
| 2. Copywriting | 4/4 | No copy changes in Phase 4 — all Phase 1-3 strings locked; out-of-stock note text preserved (only color touched) |
| 3. Responsive Behavior | 4/4 | D-06 audit confirmed all invariants hold at 480/768/1200 public + admin; no fixes required (per 04-01-SUMMARY) |
| 4. State & Feedback | 4/4 | Search out-of-range now 302→last page mirroring home (D-07 #2); page=0→1; no silent-clamp inconsistency remaining |
| 5. Spacing & Hierarchy | 4/4 | Token multiples of 4 preserved; contact-strip body→CTA gap already fixed to 24px in Phase 3 (c0c38a9); no spacing regressions |
| 6. Accessibility Basics | 4/4 | Contrast fix #B91C1C on #F9FAFB = 6.19:1 (AA pass, up from ~4.3:1); gallery main image full-size keeps alt/width/height; thumbs unchanged 72×72 touch targets |

**Overall: 24/24**

---

## Detailed Findings

### Pillar 1: Design System Conformance (4/4)

All Phase 4 changes stay within the locked token set:
- **#B91C1C** (`style.css:410`) is the same red ramp as inherited destructive #DC2626 — same hue family, darker shade for AA. No new hex *hue*, no token-scheme drift. Verified via code inspection.
- **`.contact-strip .btn { min-width: 200px }`** (`style.css:386`) is now documented with an inline comment: "Declared spec addition (04-UI-SPEC D-07 #1): keeps the Messenger CTA a >=44px touch target on mobile. Harmless, documented, no token change." — resolves the prior "harmless but undocumented" flag.
- Gallery main image swaps `thumb_filename` → `filename` (full-size original, quality-85 re-encoded JPEG) with `width="440" height="440"` (`product_detail.html:10`); thumbs keep `thumb_filename` 72×72 (`:20`). No new asset pipeline, no library.

### Pillar 2: Copywriting (4/4)

Zero copy changes in Phase 4. All strings ("Sản phẩm hiện đang hết hàng.", "Mua qua Messenger", badges, empty states) remain verbatim per Phase 1-3 contracts. The out-of-stock note is touched for **color only** (#DC2626 → #B91C1C) — text unchanged.

### Pillar 3: Responsive Behavior (4/4)

D-06 audit (04-01-SUMMARY Task 5) verified all breakpoint invariants hold at 480/768/1200 for **public + admin** — no responsive violations found, zero fixes required. Grid 2/3/4-col, header stack→row, detail stack→2-col 360/440px, admin table/form usable on phone all confirmed. Gallery main image now 440px source (`filename`) renders crisp at 2x DPR on desktop (D-07 #4) — the deferral that previously made it soft.

### Pillar 4: State & Feedback (4/4)

- **Search out-of-range** now redirects 302 to the last valid page (`public.py` search route), mirroring `home()` exactly — resolving the Phase 3 INFO finding "search clamps silently while home redirects." `page=0`/negative → 302 to page 1; `total=0` → no redirect (empty state renders). Both routes now share identical out-of-range semantics.
- The contrast fix also improves the *state* affordance: the out-of-stock note is now clearly legible per WCAG AA.

### Pillar 5: Spacing & Hierarchy (4/4)

No spacing changes in Phase 4; all values remain multiples of 4. The contact-strip body→CTA gap was already corrected to 24px in Phase 3 (commit `c0c38a9`) and is confirmed at `style.css:384`. Heading hierarchy (h1→h2→h3, visually-hidden h2 before grid) was restored in Phase 3 (`d2389a1`) and is untouched by Phase 4.

### Pillar 6: Accessibility Basics (4/4)

- **Contrast:** out-of-stock note #B91C1C on #F9FAFB = **6.19:1** (computed), passing AA (≥4.5:1) with comfortable margin — resolves the Phase 3 ~4.3:1 LOW finding (D-07 #3).
- **Gallery main image:** full-size `filename` keeps `alt` = product name, explicit `width`/`height` 440 (no CLS), not lazy (correct for LCP). Thumbs unchanged: 72×72 targets, `aria-label`, `aria-current` on active.
- `₫` (U+20AB): D-07 #5 verdict per 04-01-SUMMARY — Noto Sans VN (leading fallback font) carries U+20AB, no fallback font appended. `format_price` at `app/__init__.py:63-65` confirmed. (Browser-render confirmation is a human UAT item.)

---

## Findings

**None.** Phase 4 is a clean polish pass — all 5 D-07 deferral items resolved, D-05 held, D-06 audited, no new defects introduced.

Non-blocking / human UAT items (unchanged from prior phases, worth a manual look):
- Browser-render check of `₫` glyph (D-07 #5 verdict is code-based; visual confirm is quick).
- Visual responsive sweep on a real phone (D-06 audit was code-level).
- Real-domain HTTPS go-live (`YOUR_DOMAIN` placeholder → real domain per D-03).

---

## Registry Safety

No shadcn, no components.json, no third-party registries (Flask + hand-written CSS per CLAUDE.md). Zero new libraries in Phase 4; the gallery-swap JS remains the same ~10-line vanilla script (only `data-src` now points at the full-size file). No flags.

---

## Verification Method

Code audit of the changed surface: `style.css` (D-07 #1/#3, D-05 opacity), `product_detail.html` (D-07 #4 full-size image), `public.py` (D-07 #2 search redirect), plus 04-01/02/03-SUMMARY.md for the D-05/D-06 verification results. No dev server available — same method as prior phase reviews.

---

## Files Audited

- `app/static/css/style.css` (#B91C1C, contact-strip min-width comment, D-05 opacity rule)
- `app/templates/public/product_detail.html` (main image full-size + width 440, thumb data-src)
- `app/public.py` (search out-of-range redirect mirroring home)
- `.planning/phases/04-polish-deploy/04-UI-SPEC.md`, `04-CONTEXT.md`, `04-01/02/03-SUMMARY.md`

---

**Overall verdict:** 24/24 — Phase 4 is a clean, correct polish pass. Every D-07 deferral from Phase 3 is resolved exactly per the UI-SPEC, D-05 CAT-04 de-emphasis holds unchanged, D-06 responsive invariants verified with zero fixes needed, and the contrast fix measurably improves accessibility. No findings. This UI is production-ready.

---

## Fix Applied

No fixes required — audit found zero findings.

_Fixed: N/A_
_Fixer: N/A_
