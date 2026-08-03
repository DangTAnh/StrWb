---
phase: 9
slug: polish-deploy
status: draft
shadcn_initialized: false
preset: none
created: 2026-08-03
---

# Phase 9 — UI Design Contract

> Visual and interaction contract for Phase 9 — Polish + Deploy (v1.1 close-out). Phase 9 is a **polish pass over the already-approved v1.1 surfaces**, not a new-feature phase. It introduces **no new design-system tokens, no new hex values, no new type roles, no new copy**. The contract locks: (1) the confirmed open UI-review findings to fix, (2) two locked reverted edits, (3) the 3-breakpoint responsive verification, and (4) the small cross-surface consistency gaps. All tokens, typography, spacing, and color roles are inherited unchanged from Phases 1/2/6/7/8.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none — Flask server-rendered Jinja2 templates with hand-written CSS |
| Preset | not applicable |
| Component library | none (hand-rolled tables, badges, stat cards, stepper — all inherited) |
| Icon library | none (text labels + CSS dots only) |
| Font | Noto Sans VN (Google Fonts), weights 400 + 600; fallback `Roboto, system-ui, -apple-system, sans-serif` — inherited Phase 1 |

**Design system source (inherited, unchanged):** Phase 1 baseline (`01-UI-SPEC.md`) — colors `#2563EB` / `#F9FAFB` / `#FFFFFF` / `#1F2937` / `#6B7280` / `#DC2626` / `#059669`; type scale 14/16/24/32 with weights 400 + 600; spacing multiples of 4 (4/8/16/24/32/48/64); breakpoints 480/768/1200. Phase 6 (`06-UI-SPEC.md`) — cart/checkout classes + `format_price`. Phase 7 (`07-UI-SPEC.md`) — admin order list/detail, `.badge-order-*`, `.order-progress` stepper. Phase 8 (`08-UI-SPEC.md`) — stats dashboard, `.stat-*`, `.status-breakdown`, `.badge-neutral`, the single new hex `#B45309`.

**shadcn gate:** Not applicable. Tech stack is Python Flask with Jinja2 + plain CSS. No `components.json` exists (verified: none in repo — same check passed in Phases 6/7/8); CLAUDE.md "What NOT to Use" bans Tailwind, Bootstrap, React/Vue, shadcn.

**Polish surface scope (locked by 09-CONTEXT.md):** Only the new v1.1 surfaces — public cart + checkout form, admin orders list/detail, admin stats. v1.0 surfaces (home, search, product_detail, admin product CRUD) are **not** touched except the two locked reverts (R-01, R-02). No redesign, no new components, no new features.

---

## Spacing Scale

Inherited unchanged from Phase 1 (`4 / 8 / 16 / 24 / 32 / 48 / 64`). Phase 9 introduces **no new spacing tokens**. The polish fixes reuse only existing values.

| Token | Value | Phase 9 Usage |
|-------|-------|---------------|
| xs | 4px | cart-badge margin-left (inherited, untouched) |
| sm | 8px | cart-thumb radius (4px radius is the inherited sm-radius, not a spacing token) |
| md | 16px | `.cart-actions` gap (inherited), `.checkout-form .btn` max-width 320px (a content width, not a token) |
| lg | 24px | unused — no section-padding changes |
| xl | 32px | unused |
| 2xl | 48px | unused |
| 3xl | 64px | unused |

**Exceptions (declared, justified sub-token values — not new spacing tokens):**
- `.cart-thumb` fixed `80px × 80px` — the cart thumbnail content size (already shipped inline; promoted to a class), not a spacing token.
- `.checkout-form .btn` `max-width: 320px` — a button content width matching the product-detail `.cart-cta` column (`max-width: 320px` on the add-to-cart form), not a spacing token.

---

## Typography

Roles inherited unchanged from Phase 1. Phase 9 makes **no changes to sizes, weights, or line-heights** (declared: 14, 16, 24, 32 px; weights 400 + 600; body 1.5, heading 1.2, display 1.1). Every element touched by a polish fix already maps to an inherited role.

| Role | Size | Weight | Line Height | Phase 9 Relevance |
|------|------|--------|-------------|-------------------|
| Body | 16px | 400 | 1.5 | Cart line-item name (accepted at 600 — see D-01), order-detail line totals (inherited) |
| Body (semibold variant) | 16px | 600 | 1.5 | `.data-table .line-total`, `.data-table .product-name` (inherited) |
| Label | 14px | 400 | 1.5 | `.unit-price`, `.cart-total-label`, `.help-text` (inherited) |
| Heading | 24px | 600 | 1.2 | Checkout heading (already fixed M1, `style.css:456`) |
| Display | 32px | 600 | 1.1 | Cart/order-detail total value (inherited) |

**Font stack (inherited):** `Noto Sans VN`, `Roboto`, `system-ui`, `-apple-system`, `sans-serif`

No type-usage-map changes: the polish fixes do not alter which role any element maps to. The only typography-adjacent change is F-03 (`.cart-badge` line-height `1.5` → `1`) — a rendering fix for a 20px pill that already ships 14px/600 Label text, not a role change.

---

## Color

Base palette inherited unchanged. Phase 9 adds **no new hex values** — every color used by a polish fix already exists in the stylesheet.

| Role | Value | Usage (inherited, unchanged) |
|------|-------|------------------------------|
| Dominant (60%) | #F9FAFB | Page background (inherited) |
| Secondary (30%) | #FFFFFF | Cards, nav header (inherited) |
| Accent (10%) | #2563EB | `.line-total` across cart + order-detail money tables (F-04 locks the shared treatment), `.cart-total-value`, `.btn-primary`, `.order-id`, focus rings, stepper current dot |
| Destructive | #DC2626 | `.link-danger`, cancel button, field errors (inherited — no new usage) |
| Success semantic | #059669 / #047857 | Badges (`#059669`) vs `.flash.success` text (`#047857`, AA 5.3:1 — already fixed M2) |
| Warning semantic | #B45309 | `.stat-note` only (Phase 8, AA 4.7:1) |
| Neutral semantic | #6B7280 | Labels, unit prices, hints, timestamps (inherited) |
| Border | #E5E7EB | Table cells, section dividers, stat-card border (inherited) |

**Accent reserved for (inherited list — unchanged by Phase 9):** primary buttons, price/total values (cart total, order total, line totals), order-id links, focus rings, stepper current dot. **F-04 does not add a new reservation** — it documents that the order-detail line total already inherits the Phase 6 `.line-total` accent rule and that this shared treatment is the intended contract.

**Contrast / accessibility re-check (A-01):** No new colors → no new contrast obligations. Re-verify on the touched surfaces that inherited AA tokens still hold: `.flash.success` `#047857` on `#F9FAFB` (≈5.3:1), `.stat-note` `#B45309` on `#F9FAFB` (≈4.7:1), `.badge-order-pending/shipped` `#1D4ED8` on `#DBEAFE` (≈4.6:1), `.out-of-stock-note` `#B91C1C` on `#F9FAFB` (≈6.19:1). No color is ever the sole status indicator (badge text always carries the label — inherited).

---

## Polish Contract (this phase's core)

Six confirmed findings / consistency fixes (F-01…F-06) + two locked reverts (R-01, R-02) + two verification-only items (V-01, V-02). **Every item is a small, token-bound change — no new classes beyond the two declared, no layout redesign.**

### F-01 — `.cart-actions` missing `flex-wrap` → 320px overflow (Phase 6 L2)

| | |
|---|---|
| **Evidence** | `app/static/css/style.css:453` — `.cart-actions { display: flex; gap: 16px; margin-top: 16px; }` (no wrap). Two buttons ("Tiếp tục mua sắm" + "Đặt hàng") ≈312px total; at a 320px viewport the 288px container overflows. |
| **Fix** | Add `flex-wrap: wrap;` to the base `.cart-actions` rule. Harmless at all widths; covers the 320px edge without a new media query. |
| **Contract** | `app/static/css/style.css` line 453 → `.cart-actions { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 16px; }` |

### F-02 — cart thumbnail inline style → class (Phase 6 L4)

| | |
|---|---|
| **Evidence** | `app/templates/public/cart.html:24` — `<img … style="object-fit: cover; border-radius: 4px; vertical-align: middle;">` inline. The codebase owns a `.thumb` class (`style.css:211`, 48px) but it is too small for the cart's 80px thumb. |
| **Fix** | Promote to a `.cart-thumb` class in the Phase 6 CSS section: `.cart-thumb { width: 80px; height: 80px; object-fit: cover; border-radius: 4px; vertical-align: middle; }`. Replace the inline style in `cart.html:24` with `class="cart-thumb"`. |
| **Contract** | One new CSS class `.cart-thumb`; inline style removed; `alt="{{ item.product.name }}"` preserved; `width="80" height="80"` attributes preserved. |

### F-03 — cart-badge digit clipping at 2-digit counts (Phase 6 I3)

| | |
|---|---|
| **Evidence** | `app/static/css/style.css:432-443` — `.cart-badge` `height: 20px` with `line-height: 1.5` (21px). At 2-digit counts the pill clips descenders. |
| **Fix** | Set `line-height: 1;` on `.cart-badge` so the 14px text vertically centers within the 20px pill at any digit count. |
| **Contract** | `style.css` `.cart-badge` block → `line-height: 1;` (replaces `1.5`). No other property changes. |

### F-04 — order-detail line-total color: lock the shared `.line-total` treatment (Phase 7 spec gap)

| | |
|---|---|
| **Evidence** | `app/templates/admin/orders/detail.html:32` renders order-item line totals with `class="line-total"`, which inherits the Phase 6 rule `style.css:452` → accent `#2563EB`/600. Phase 7 `07-UI-SPEC.md` declared this element `#1F2937`/600. Phase 7 had no UI review, so the gap was never reconciled. |
| **Decision** | **Keep the shared `.line-total` accent treatment** on both cart (public) and order-detail (admin) money tables. One rule, one look across v1.1 surfaces — accent emphasis on line totals matches the `.cart-total-value` and is within the accent budget on the small (1–3 row) item table. The Phase 7 per-element `#1F2937` declaration is superseded for this element; documented here, no code change. |
| **Contract** | No CSS/template change for F-04. Verify both `cart.html:38` and `detail.html:32` render `.line-total` identically (accent 600, tabular-nums). |

### F-05 — total-label punctuation consistency

| | |
|---|---|
| **Evidence** | `app/templates/public/cart.html:51` "Tổng cộng:" (trailing colon) vs `app/templates/admin/orders/detail.html:38` "Tổng cộng" (no colon). Both use `.cart-total-label`; the colon is redundant in the flex baseline layout. |
| **Fix** | Standardize on **"Tổng cộng"** (no colon) in `cart.html:51`, matching the order-detail total label. |
| **Contract** | One shared label string "Tổng cộng" on both v1.1 money totals. |

### F-06 — checkout submit button inline style → class

| | |
|---|---|
| **Evidence** | `app/templates/public/_checkout_form.html:22` — `<button … style="width: 100%; max-width: 320px;">Đặt hàng</button>` inline (same anti-pattern class F-02 fixes). The product-detail add-to-cart button already uses the `.cart-cta` class (`style.css:411`, `width: 100%`). |
| **Fix** | Remove the inline style; add `.checkout-form .btn { width: 100%; max-width: 320px; }` to the Phase 6 CSS section. |
| **Contract** | One new CSS class selector `.checkout-form .btn`; inline style removed; button label "Đặt hàng" unchanged. |

### R-01 — revert README heading (locked)

| | |
|---|---|
| **Evidence** | `README.md:1` — currently ` StoreWeb` (leading space, heading marker lost). `git diff` confirms the committed baseline was `# StoreWeb`. |
| **Fix** | Restore `# StoreWeb` as the H1. |
| **Contract** | `README.md` line 1 exactly `# StoreWeb`. (CONTEXT.md also adds a v1.1 description line — tracked by the deploy-docs plan, not the UI contract.) |

### R-02 — revert product-form help-text (locked)

| | |
|---|---|
| **Evidence** | `app/templates/admin/products/form.html` — the quantity field's `<p class="help-text">` is deleted in the working copy (stray uncommitted edit). The committed baseline had it. |
| **Fix** | Re-add after the quantity field-error loop: `<p class="help-text">Trạng thái tự động: Còn hàng khi tồn kho &gt; 0, Hết hàng khi tồn kho = 0. Bật “Ngừng bán” để ghi đè.</p>` |
| **Contract** | `form.html` quantity block matches the committed baseline verbatim (HTML entity `&gt;`, curly quotes `“…”`). |

### V-01 — verify-only: qty-0 cart row (Phase 6 L3)

No code change. The stale-item filter (`app/public.py` cart render) pops products whose status is no longer `available` — and a product whose stock hits 0 flips to `out_of_stock`, so a qty-0 row cannot persist for an available product; the MD-02 clamp (`public.py:127-131`) handles positive-stock drops. Add a `verify_11_full.py` assertion: seed a product at stock 1, add to cart, drop stock to 0 → cart render shows no qty-0 row for it (popped + info flash).

### V-02 — responsive verification at 3 breakpoints (locked)

Verify the five v1.1 surfaces render correctly at **375 (mobile) / 768 (tablet) / 1440 (desktop)** — the same viewport pattern as the existing `.planning/ui-reviews/` cart-empty evidence. Capture screenshots via Chrome headless against a **seeded temp DB** (reuse `verify_11_full.py` seed helpers) so populated states render without touching the real `data/app.db`. Evidence naming follows the existing pattern.

| Surface | 375 | 768 | 1440 | Pass condition |
|---------|-----|-----|------|----------------|
| Cart (populated, 2 items) | ✓ | ✓ | ✓ | `.table-scroll` horizontal scroll on mobile; `.cart-actions` wraps (F-01); thumbs render (F-02); no horizontal overflow |
| Cart (empty) | ✓ | ✓ | ✓ | `.empty-state` centered; reuse existing `cart-empty*` screenshots if unchanged |
| Checkout form section | ✓ | ✓ | ✓ | Fields full-width on mobile; no inline-style residue (F-06); phone help-text wraps cleanly |
| Admin orders list | ✓ | ✓ | ✓ | `.table-scroll` on mobile; filter stacks on mobile (`style.css:468`); pagination fits |
| Admin order detail | ✓ | ✓ | ✓ | stepper scrolls horizontally on mobile (`overflow-x: auto`); action-row buttons stack full-width |
| Admin stats | ✓ | ✓ | ✓ | `.stats-grid` 1→2→3 columns; stat cards fit; breakdown rows ≥44px |

**Evidence path:** `.planning/ui-reviews/` (git-ignored per `.planning/ui-reviews/.gitignore`), named `<surface>-<breakpoint>.png` (e.g. `orders-list-mobile.png`). Record the pass/fail matrix in `09-VERIFICATION.md`.

---

## Interaction Contracts

No new routes, no new interactions, no new state. The polish fixes touch **CSS + template markup only**:

| Item | Type | Surface |
|------|------|---------|
| F-01, F-03 | CSS-only | Public cart (CSS in `style.css`) |
| F-02, F-06 | Template + CSS | Public cart / checkout form |
| F-04, F-05 | Template-verify / one-label string | Cart + admin order detail |
| R-01, R-02 | Revert-to-baseline | Repo README + admin product form |
| V-01, V-02 | Verify harness + screenshots | All five v1.1 surfaces |

**Existing interactions confirmed untouched** (verified in code this session): cart add/update/remove POSTs with CSRF (`public.py:88-166`), checkout with honeypot silent-reject + CSRF + server re-validation (`public.py:171-233`), forward-only status transitions with server-side `TRANSITION_MAP` (`admin.py`), cancel `confirm()` dialog (`detail.html:77,89`). None are altered by this phase.

---

## Responsive Behavior

Breakpoints inherited (480/768/1200). The only responsive **change** is F-01 (`flex-wrap` on `.cart-actions`). V-02 is the verification of the existing responsive behavior at the three evidence viewports (375/768/1440), not new breakpoints.

| Breakpoint | Phase 9 Behavior |
|------------|------------------|
| Mobile ≤480px | Cart actions wrap (F-01); cart table scrolls (inherited `.table-scroll`); order filter stacks (inherited `style.css:468`); stepper scrolls horizontally (inherited `style.css:482`); stats grid 1-col (inherited `style.css:497`) |
| Tablet 768px | All five surfaces full-width without scroll; stats grid 2-col (inherited) |
| Desktop ≥1200px | Container max 1200px; stats grid 3-col (inherited); checkout button at max-width 320px (F-06) |

---

## Copywriting Contract

**Phase 9 introduces no new user-facing copy.** The polish fixes alter zero labels. The only copy-touching items are the two locked reverts, which restore committed baseline strings:

| Element | Copy | Status |
|---------|------|--------|
| Admin product-form help-text (restore) | `Trạng thái tự động: Còn hàng khi tồn kho > 0, Hết hàng khi tồn kho = 0. Bật “Ngừng bán” để ghi đè.` | R-02 — revert to baseline |
| Cart total label (consistency) | `Tổng cộng` (drop trailing colon in `cart.html:51`) | F-05 |
| All Phase 6/7/8 CTA, flash, empty-state, error strings | unchanged, verbatim | inherited — no edits |
| Primary CTA | none new — polish only; existing CTAs ("Thêm vào giỏ hàng", "Đặt hàng", "Chuyển sang: …", "Hủy đơn") unchanged | inherited |
| Empty / error / destructive-confirm states | unchanged from Phases 6/7/8 (empty-state headings, flash messages, `confirm('Hủy đơn #N? …')`) | inherited |

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not applicable — shadcn not used (Flask project, not React/Next/Vite) |
| Third-party | none | not applicable — no component registries declared |

**Note:** The shadcn initialization gate does not apply (Python Flask + Jinja2 + plain CSS; no `components.json`; CLAUDE.md bans Tailwind/Bootstrap/React/shadcn). No new dependencies, no new packages, no JS added or removed. The only changes are CSS rules and template markup in the existing files listed under each fix. `.cart-thumb` and `.checkout-form .btn` are literal CSS additions to `style.css`, not package additions.

---

## Open Questions / Decisions Made on Pattern

All design decisions are resolved from upstream artifacts (09-CONTEXT.md locked decisions + prior UI reviews + inherited tokens) — **no blocking questions remain, no user input required**:

1. **Cart product-name weight 600 vs declared 400 (Phase 6 L1)?** → **Accept 600.** `.data-table .product-name` is an inherited Phase 2 admin-table rule; the cart line name is each row's primary anchor and emphasis is defensible. Both are token weights. Documented, no change. (Contrasts with F-02/F-06, which kill *inline styles*; this is a class-based rule, not an inline style.)
2. **Order-detail line-total accent (F-04)?** → **Keep the shared `.line-total` accent treatment** across cart + order-detail. Supersedes the Phase 7 per-element `#1F2937` declaration. No code change.
3. **Shared admin nav (forward-referenced from Phase 7 to "Phase 9")?** → **Explicitly OUT OF SCOPE.** 09-CONTEXT.md locks the Phase 9 UI scope to the five new v1.1 surfaces + confirmed-finding fixes + 3-breakpoint responsive pass, and bans redesign. A shared admin nav would touch every admin template (a layout refactor, not a polish fix). It remains a backlog item for the next milestone.
4. **New screenshots for empty cart?** → **Reuse existing** `.planning/ui-reviews/cart-empty{,-tablet,-mobile}.png` if the cart markup change (F-02 thumb class, F-05 label) leaves the empty state unchanged — it does (empty state is a separate branch of `cart.html`). Re-capture only if a regression is suspected.
5. **Screenshot data source?** → **Seeded temp DB** via the `verify_11_full.py` seed helpers, never the real `data/app.db`. The real DB upgrade (`flask --app wsgi init-db`) stays an operator step in the Verify-production checklist (deploy-docs plan).

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS — no new user-facing copy; F-05 unifies "Tổng cộng"; R-02 restores a baseline admin string verbatim; all inherited CTA/empty/error strings untouched.
- [ ] Dimension 2 Visuals: PASS — six small token-bound fixes, no new components, no layout redesign; F-02/F-06 replace inline styles with classes (consistent with the codebase pattern); F-04 documents the shared `.line-total` treatment.
- [ ] Dimension 3 Color: PASS — zero new hex values; accent budget unchanged (F-04 clarifies an existing accent use, does not add one); A-01 re-verifies inherited AA tokens on touched surfaces.
- [ ] Dimension 4 Typography: PASS — no size/weight/line-height changes; F-03 is a pill line-height rendering fix for already-declared Label text.
- [ ] Dimension 5 Spacing: PASS — all values multiples of 4 from the inherited scale; `.cart-thumb` 80px and `.checkout-form .btn` 320px declared as justified content-width exceptions.
- [ ] Dimension 6 Registry Safety: PASS — no third-party registries, no shadcn, no new dependencies; two literal CSS additions only.

**Approval:** pending
