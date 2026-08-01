# Phase 2 — UI Review

**Audited:** 2026-08-01
**Baseline:** 02-UI-SPEC.md (Approval: flagged) + 01-UI-SPEC.md baseline design system
**Screenshots:** not captured (no dev server at 3000/5173/8080/5000/8000) — code-only audit
**Registry audit:** N/A — no shadcn/components.json (Flask + hand-written CSS per CLAUDE.md)

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Visual Hierarchy | 3/4 | Clear primary-CTA focus, but "Ảnh chính" badge goes stale during reorder and input focus ring is sub-spec |
| 2. Color | 3/4 | 60/30/10 split and status palette exact; accent bleeds onto pagination links outside the 5-element reservation |
| 3. Typography | 3/4 | 4-size/2-weight scale honored for Phase 2 text; reorder arrows at 18px and dashboard badge at 12px off-scale |
| 4. Spacing | 4/4 | Fully token-adherent; documented exceptions (badge 2px, input 12px) applied correctly |
| 5. Alignment & Consistency | 3/4 | Hành động column left-aligned (spec: right); gallery preview order ≠ persisted order for mixed existing+new reorders |
| 6. Responsive & Accessibility | 3/4 | 480/768 breakpoints correct, table a11y solid; focus-visible ring missing on links/checkbox/reorder; price/qty missing step/min |

**Overall: 19/24**

---

## Top 3 Priority Fixes

1. **Gallery reorder does not persist the displayed order in edit mode (D-12 gap, HIGH)** — In `admin.py:38-42` new files are appended *after* all existing images, so a newly uploaded image can never become the primary image on an existing product. Worse, `moveExisting` in `form.html:188-196` lets the user visually interleave a new preview above an existing image, but `syncOrder` (`form.html:119-125`) only captures `data-id` items, so the on-screen order and the saved order diverge. Fix: build one ordered list of existing-image ids *and* new-file keys in the JS, submit it, and have `_process_image_batch` assemble the final gallery from that single ordered sequence.
2. **"Ảnh chính" badge does not re-render on reorder (MEDIUM)** — The badge is server-rendered on `loop.first` of existing images (`form.html:89`) and travels with its item's DOM node. Moving the original first item down leaves the badge visually on position 2, while the position-1 item shows no badge — the editor preview contradicts the saved result. Move badge assignment into JS so it always marks the first displayed item.
3. **Focus-visible ring missing on most interactive elements (MEDIUM, a11y contract)** — Spec requires "2px #2563EB ring on all interactive elements." Only `.btn` has it (`style.css:181`). Links (`Sửa`/`Xóa`/`Quay lại`/pagination), reorder buttons, and the gallery checkbox fall back to the browser default; the input focus state is a 20%-alpha shadow (`style.css:276-280`) instead of a solid accent border + 2px ring.

---

## Detailed Findings

### Pillar 1: Visual Hierarchy (3/4)

The primary CTA is the sole filled-accent element on the list page (`list.html:6`) and the form (`form.html:105`) — the accent-reservation hierarchy holds. Heading (24px/600) vs table header (14px/600 gray) separation is correct.

- **MEDIUM** — Stale "Ảnh chính" badge misrepresents primary-image hierarchy during editing. Badge is rendered server-side on the first existing item (`form.html:89`) and stays glued to that DOM node through JS reorders (`form.html:188-196`); a reordered gallery can show the badge on the 2nd position while position 1 is unbranded.
- **LOW** — Input focus affordance is weak: `box-shadow: 0 0 0 2px rgba(37,99,235,0.2)` (`style.css:276-280`) is a 20%-alpha tint, visually much softer than the spec'd solid 2px accent ring; also `outline: none` at `style.css:277` removes the default focus indicator entirely on browsers without good `:focus-visible` fallback.
- **LOW** — Gallery reorder affordance relies on unicode arrows with a hover color change only (`style.css:323`); no border/background in idle state makes the control visually quiet in an already-dense card. Acceptable per spec (icons = unicode arrows only), but worth a Phase 4 affordance pass.

### Pillar 2: Color (3/4)

60/30/10 split is correct: dominant #F9FAFB on page/table-header/hover (`style.css:2,193-195,200`), secondary #FFFFFF on cards (`style.css:3,98`), accent #2563EB reserved for the 5 declared elements. Status badge palette matches spec exactly (`style.css:228-230`): available `#059669/#ECFDF5/#A7F3D0`, out-of-stock `#D97706/#FFFBEB/#FDE68A`, discontinued `#6B7280/#F3F4F6/#E5E7EB`. Flash warning `#D97706` (`style.css:47`), destructive/back-link and `.link-danger` scoped correctly.

- **LOW** — Accent over-reach: `.pagination a { color: var(--accent); }` (`style.css:242`) colors the "Trước"/"Sau" controls accent, but pagination is not among the 5 accent-reserved elements in the spec (§Color). The indicator is correctly #6B7280 (`style.css:240`); only the controls deviate. Same structural risk from the global `a { color: var(--accent) }` (`style.css:22`) — every future link inherits accent automatically.
- **INFO** — `#1d4ed8` lowercase at `style.css:94` is the same value as `#1D4ED8` elsewhere (cosmetic, no behavior difference).

### Pillar 3: Typography (3/4)

Phase 2 text respects the 4-size (14/16/24/32) / 2-weight (400/600) scale: buttons 14/600 (`style.css:173-175`), table headers 14/600 (`style.css:195-198`), product name 14/600 (`style.css:201`), body cells 14/400, inputs 16/400 (`style.css:270`), page headings 24/600 (`style.css:38`). Body line-height 1.5.

- **LOW** — Reorder arrows render at 18px (`style.css:318`), a 5th size outside the declared scale. Mitigation: they are icon glyphs, not copy — but the spec's type contract says "no new sizes."
- **LOW** — Dashboard product-count badge at 12px (`style.css:111`) — pre-existing Phase 1 off-scale size (5th size), not introduced by Phase 2.
- **INFO** — Login submit (`style.css:92`) and logout button (`style.css:125`) render at 16px vs the Label 14px role — pre-existing Phase 1 deviation, outside Phase 2 scope.

### Pillar 4: Spacing (4/4)

All Phase 2 spacing maps to the 4/8/16/24/32/48/64 token set: table cells 8/16 (`style.css:192`), button padding 0/24 (`style.css:170`), empty state 32/16 (`style.css:250-251`), form field margin 16 (`style.css:259`), row gap 16 (`style.css:260`), action row margin 24 (`style.css:286`), gallery gap 24/margin 16 (`style.css:297`), badge 2/8 (`style.css:222`), reorder actions 4/4 (`style.css:311`). Documented exceptions applied exactly: badge vertical 2px, input/textarea horizontal 12px (`style.css:267,275`). No arbitrary spacing values found.

- **INFO** — Checkbox control is 18×18 (`style.css:285,326`) and thumbnail 96px gallery box / 48px table box match the declared dimensions.

### Pillar 5: Alignment & Consistency (3/4)

Buttons, cards, table cells, and form rows are consistently token-aligned across all three new pages; flash zone and page wrapper share the 1200px container (`style.css:43,157`). Empty-state, pagination, and delete-card match their layout contracts.

- **MEDIUM** — Hành động column is left-aligned: `.data-table .actions-cell { white-space: nowrap; }` (`style.css:204`) has no `text-align: right`, but the spec table contract explicitly requires "Hành động | right-aligned, nowrap."
- **MEDIUM** — Gallery preview order and persisted order diverge for mixed existing+new reorders (see Top Fix 1). `moveExisting` reorders the full DOM (`form.html:188-196`) but `syncOrder` only serializes `data-id` items (`form.html:119-125`) and new files are appended last on save (`admin.py:38-42`). Result: the editor can display a new preview in position 1 that is actually saved last.
- **LOW** — Button disabled states are absent: spec button matrix defines primary `bg #93C5FD`, destructive `bg #FCA5A5`, secondary `text #9CA3AF`, but no `.btn:disabled`/`.btn[disabled]` rule exists (`style.css:165-187`). Unexercised today (no button is ever disabled) but an incomplete contract.
- **LOW** — `.admin-card--wide` (`style.css:160`) lacks the spec'd `overflow: hidden`, so the table/pagination do not clip to the card's `border-radius: 8px` corners (the header row's square corners can poke past the rounded card edge).

### Pillar 6: Responsive & Accessibility (3/4)

Breakpoints are correct: table in `overflow-x: auto` scroll wrapper (`style.css:190`, `list.html:10`), form 2-col rows collapse at 768px (`style.css:333`), header stacks at 768px (`style.css:334`), pagination left-aligns at 768px (`style.css:335`), 480px page padding retained (`style.css:340`). Table semantics are solid: `<table>` + `<th scope="col">` + visually-hidden caption (`list.html:12`). Reorder buttons and delete checkbox carry Vietnamese `aria-label`s (`form.html:91-92,94`). Delete is a real POST+CSRF confirmation page, no JS `confirm()`. Empty state, error summary, and warning flash all render.

- **MEDIUM** — Focus-visible coverage incomplete (see Top Fix 3). Links, reorder buttons, and the gallery checkbox have no custom `:focus-visible`; input focus is a 20%-alpha shadow.
- **LOW** — Price and quantity inputs lack HTML-level `min`/`step`: spec requires price `type="number" step="1" min="0"` and quantity `type="number" min="0"`. The template passes only `class`/`required`/`aria_required` (`form.html:21,59`); WTForms `NumberInput` will default `step` to `any`, and `min="0"` is not rendered at all. Server-side `NumberRange` still validates, so this is a UI-enforcement gap, not a data-safety one.
- **INFO** — 400px thumbnail assets (`image_utils.py:15`) are served into 48px/96px boxes; correct output, but oversized for the display size (bandwidth/perf nit).

### Copywriting cross-check (spec checker flags verified)

Both checker nits from the spec sign-off are fixed in the implementation: the "Hủy to" typo is rendered simply as "Hủy" (`form.html:106`), and the flash reads "Chưa có ảnh nào được lưu" (`admin.py:89,112`), matching the recommended wording. All copy-inventory strings match the contract verbatim (list heading/headers, empty state, form labels/placeholders, derived-status hint, gallery help, delete confirmation, flash messages, price format `1.200.000₫` via `format_price` at `app/__init__.py:64-66`). Vietnamese curly quotes used consistently in templates. No orthography issues found.

- **LOW (pre-existing, Phase 1)** — 500 page repeats "Đã có lỗi xảy ra" in both heading and body (`errors/500.html:4-5`).

---

## Deferred to Phase 4 (Polish)

- Downscale thumbnail generation for the 48px table cell (400px is ~8× oversize) — `image_utils.py:15`.
- Normalize off-scale sizes: reorder arrows 18px (`style.css:318`) and dashboard badge 12px (`style.css:111`); align Phase 1 login/logout button size to Label 14px.
- Add `.btn:disabled` styles from the spec button matrix (only needed once any button becomes conditionally disabled).
- Add `overflow: hidden` to `.admin-card--wide` for corner clipping.
- Verify `₫` (U+20AB) renders under the Noto Sans VN fallback chain.
- Gallery affordance polish (idle-state borders/bg on reorder buttons) and richer empty-gallery hint.

---

## Registry Safety

No shadcn, no components.json, no third-party registries (Flask + hand-written CSS). All components are hand-rolled per CLAUDE.md "What NOT to Use." No flags.

---

## Files Audited

- `app/templates/base.html`
- `app/templates/admin/dashboard.html`
- `app/templates/admin/products/list.html`
- `app/templates/admin/products/form.html`
- `app/templates/admin/products/delete.html`
- `app/static/css/style.css`
- `app/image_utils.py` (thumbnail pipeline)
- `app/admin.py`, `app/forms.py`, `app/models.py`, `app/__init__.py` (format_price, flash copy, status/primary derivation)
- `app/templates/auth/login.html`, `app/templates/errors/404.html`, `app/templates/errors/500.html`

---

**Overall verdict:** Structurally sound and highly spec-faithful (19/24) — the outstanding issues are concentrated in one functional gap (gallery order persistence on mixed existing+new reorders) and a scattered focus-state accessibility shortfall, neither of which blocks the Phase 2 feature set but both of which should be fixed before this UI is inherited by Phase 3.

---

## Fix Applied

Fixed on 2026-08-01 by `gsd-code-review --fix` (worktree branch `gsd-reviewfix/02-1756`, merged to `master`).

| Finding | Severity | Status | Commit |
|---------|----------|--------|--------|
| Gallery reorder does not persist displayed order (Top Fix 1, D-12/D-13) | HIGH | Fixed — `syncOrder` now serializes the full on-screen gallery (existing ids + `new:<i>` tokens for uploads); `_process_image_batch` parses that stream, re-sorts existing images by their submitted id and inserts new uploads at their displayed position, so a newly uploaded image can become primary on an existing product by moving it up | `12c9729` |
| "Ảnh chính" badge stale on reorder (Top Fix 2) | MEDIUM | Fixed — `updatePrimaryBadge()` removes and re-renders the badge on the first displayed item after every reorder (`moveExisting`/`moveNew`/file add); server-side `loop.first` remains the initial state | `12161a1` |
| Focus-visible ring missing on links/reorder/checkbox; input focus is a 20%-alpha shadow (Top Fix 3) | MEDIUM | Fixed — added `a:focus-visible`, `.reorder-btn:focus-visible`, checkbox `:focus-visible` (2px accent ring, matches `.btn:focus-visible`); input focus now a solid 2px accent outline + accent border, dropping the `outline: none` that suppressed the default indicator | `b763980` |
| Hành động column left-aligned (Pillar 5) | MEDIUM | Fixed — `.actions-cell` now `text-align: right` | `fde188c` |
| Accent bleeds onto pagination links (Pillar 2) | LOW | Fixed — `.pagination a` uses neutral `#6B7280`; accent stays reserved for the 5 declared elements | `fde188c` |
| Price/quantity number inputs missing `min`/`step` (Pillar 6) | LOW | Fixed — price `min="0" step="1"`, quantity `min="0" step="1"` | `fde188c` |
| Reorder arrows at 18px, a 5th size off the scale (Pillar 3) | LOW | Fixed — 18px → 16px (token scale) | `fde188c` |
| `.btn:disabled` states absent (Pillar 5) | LOW | Fixed — spec matrix applied: primary `#93C5FD`, destructive `#FCA5A5`, secondary `#9CA3AF`, plus `cursor: not-allowed` | `fde188c` |
| `.admin-card--wide` missing `overflow: hidden` (Pillar 5) | LOW | Fixed — added `overflow: hidden` so the table/pagination clip to the card's 8px radius | `fde188c` |
| Thumbnail asset downsizing (400px into 48px/96px boxes) | LOW | Deferred to Phase 4 — not touched | — |
| ₫ (U+20AB) glyph verification | LOW | Deferred to Phase 4 — not touched | — |
| Gallery idle-state affordance polish | LOW | Deferred to Phase 4 — not touched | — |

**Verification:** Flask test client (no production server started). Created a product with 2 uploaded images (first = primary, `sort_order` [0,1]); edited it with a reorder + 1 new upload so the new image sat first → it became primary and existing A/B followed in order; reordered to [B,C,A] (persisted, B primary); deleted A → [B,C] kept, B primary. Edit page GET renders the initial `image_order` stream and exactly one Ảnh chính badge. Unauth `GET /admin/` still → `302 /login?next=/admin/`. All checks passed.
