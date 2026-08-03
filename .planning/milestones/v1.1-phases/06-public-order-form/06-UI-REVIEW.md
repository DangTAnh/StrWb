# Phase 6 — UI Review (Cart + Checkout)

**Audited:** 2026-08-02
**Baseline:** `06-UI-SPEC.md` (design contract, 6/6 PASS at creation)
**Screenshots:** partial — empty-cart captured at 1440/768/375 via Chrome headless (`app/static` + templates code-audited for populated states). Product detail + populated cart could NOT be rendered: local DB is at v1.0, missing `products.cost_price` (operator `flask --app app init-db` deferred post-Phase-6 per 06-03-SUMMARY). All populated-state verdicts are code-based.
**Registry audit:** N/A — Flask project, no `components.json`, no shadcn, no third-party registries.
**Fix status (2026-08-02):** H1, M1, M2 FIXED in commit `f8f799d`. Verdict upgraded CONDITIONAL → APPROVED.

---

## Pillar Scores

| # | Pillar | Score | Key Finding |
|---|--------|-------|-------------|
| 1 | Copywriting | 95/100 | Every declared CTA/flash/field-error string matches contract verbatim; Vietnamese throughout. |
| 2 | Visuals | 78/100 | Cart price column deviates from spec: line total missing accent + 600, unit price not muted 14px. |
| 3 | Color | 82/100 | Tokens clean, no new hex; but line-total accent reservation unmet and success flash fails AA contrast. |
| 4 | Typography | 78/100 | Checkout h2 "Thông tin đặt hàng" unstyled (UA 700 faux-bold, not token 24px/600); cart product name 600 vs declared 400. |
| 5 | Spacing | 90/100 | All spacing multiples-of-4, tokens honored; minor cart-actions overflow risk at 320px. |
| 6 | Experience Design | 85/100 | Full state coverage (empty/error/success/honeypot/CSRF); qty-0 edge when stock depletes to 0 while in cart. |

**Overall: 508/600 (≈85/100)** — pre-fix audit snapshot; the Visuals/Color/Typography gaps this score reflects (H1/M1/M2) are fixed as of 2026-08-02 (commit `f8f799d`).

---

## Verdict: APPROVED

Faithful implementation — 4 of 6 pillars ≥85, all copy verbatim, state machine complete, no blockers. The three declared contract items (cart table price-column styling ×2, checkout heading typography) and the accessibility contrast failure were fixed in commit `f8f799d` (findings H1, M1, M2). Code re-audit of the three findings: PASS. Verdict upgraded CONDITIONAL → APPROVED.

---

## Findings Summary

| Severity | Count |
|----------|-------|
| HIGH | 1 |
| MEDIUM | 2 |
| LOW | 4 |
| INFO | 4 |

---

## Detailed Findings

### HIGH

**H1 — Cart table price column not styled per spec (design deviation).** **[FIXED — commit `f8f799d`]**
- `app/templates/public/cart.html:30` — unit price `<td>{{ item.product.price | format_price }}</td>` has no class → renders default Body 16px/400 `#1F2937`. UI-SPEC Type Usage Map declares **unit price = Label 14px/400 #6B7280**.
- `app/templates/public/cart.html:38` — line total `<td>{{ (item.product.price * item.quantity) | format_price }}</td>` has no class → renders default 16px/400 `#1F2937`. UI-SPEC declares **line total = Body 16px/600 #2563EB**, and Color section explicitly reserves accent for "cart line total".
- Net effect: the entire price column of the cart table loses its intended visual hierarchy (muted unit price, accent emphasis on line total). The `.data-table .price-cell` class already exists (`style.css:195`) with `tabular-nums` and Phase 2 `badge-primary`/accent patterns are available.
- **Fix:** add a price-cell class for the unit price (`color: var(--text-secondary)`/`#6B7280; font-size: 14px`) and a line-total class (`color: var(--accent); font-weight: 600; font-variant-numeric: tabular-nums`), mirroring the `.cart-total-value` treatment.

### MEDIUM

**M1 — Checkout section heading "Thông tin đặt hàng" unstyled (design deviation / typography).** **[FIXED — commit `f8f799d`]**
- `app/templates/public/cart.html:59` `<h2>Thông tin đặt hàng</h2>` — `style.css:451` only sets `margin-bottom`; there is **no global `h2` rule** in the stylesheet (verified). The heading therefore falls back to the UA default `1.5em / font-weight: bold(700)`.
- UI-SPEC declares checkout heading = **Heading 24px/600**, and the Google Fonts load (`base.html:9`) only ships weights 400+600 — so the 700 is browser-synthesized faux-bold, inconsistent with every other heading in the app (all tied to the 24px/600 `h1` or 16px/600 `h2` tokens).
- **Fix:** add a declared role, e.g. `.checkout-section h2 { font-size: 24px; font-weight: 600; line-height: 1.2; }` (or a shared `.section-heading` class).

**M2 — Success flash "Đặt hàng thành công..." fails WCAG AA contrast (accessibility).** **[FIXED — commit `f8f799d`]**
- `style.css:47` `.flash.success { color: var(--success) }` → `#059669`. Measured contrast on page bg `#F9FAFB`: **3.61:1**, below the 4.5:1 AA threshold for 14px normal text (the flash renders at default body 16px — still below AA).
- Token is inherited from Phase 1, but the copy is new in Phase 6, so it carries a new-contrast obligation. The `.badge-available` pairing (`#059669` on `#ECFDF5`) shows the token works at display size; it fails at small body text.
- **Fix (lazy):** darken the success flash text only — `#047857` (emerald-700, ~5.3:1) for `.flash.success`, leaving the `--success` token untouched for badges/icons. Or bump the flash to 600 weight.

### LOW

**L1 — Cart product name weight 600 vs declared Body 400 (design deviation, inherited).**
- `style.css:194` `.data-table .product-name { font-weight: 600 }` (Phase 2 admin rule) is applied to the cart line name at `cart.html:28`. UI-SPEC maps the name to Body 400. Reads fine, but deviates from the declared role. Either accept (name emphasis is defensible) or add a cart-specific override to 400.

**L2 — `.cart-actions` no flex-wrap — overflow risk at 320px (cosmetic/mobile).**
- `style.css:449` `.cart-actions { display: flex; gap: 16px; }` has no `flex-wrap`. Two buttons ("Tiếp tục mua sắm" + "Đặt hàng") total ~312px; at the 480px breakpoint container is 448px (fits), but at 320px viewport container is 288px → overflow. Add `flex-wrap: wrap` for <480px.

**L3 — qty-0 row when stock depletes to 0 while in cart (edge case).**
- `app/public.py:130` clamps `qty = min(int(qty), product.quantity)`. If an available product's stock reaches exactly 0 after being added, the row persists with quantity `0` (`cart.html:34` renders `value=0`, violating the `min="1"` client hint); checkout then rejects it via the "Một số sản phẩm không còn khả dụng" flash. Not a crash, but a visibly invalid 0-qty row. Prefer popping items clamped to 0 (mirroring the stale-item filter) instead of retaining them.

**L4 — Cart thumb uses inline style instead of a class (cosmetic).**
- `cart.html:24` `style="object-fit: cover; border-radius: 4px; vertical-align: middle;"` inline. Works, but the codebase already owns a `.thumb` class (`style.css:210`) and a `.thumb-placeholder` (used at `cart.html:26`). Promote the image to a `.thumb`-style class for consistency.

### INFO

**I1 — "Tổng cộng:" vs spec "Tổng công:".** UI-SPEC Copywriting table lists "Tổng công:" (a typo — the Cart Page Layout section and Cart total label row both say "Tổng cộng:"). Implementation `cart.html:51` uses **"Tổng cộng:"**, the correct Vietnamese. No change needed.

**I2 — Spec "Giá" column-header accent reservation not implemented.** Color section reserves accent for a "Giá" column header, but the Copywriting contract names the column "Đơn giá" and `.data-table thead th` is uniformly `#6B7280` (`style.css:190`). Uniform muted headers are the right call; the reservation row is a spec-internal inconsistency.

**I3 — cart-badge height 20px vs line-height 21px.** `.cart-badge` (`style.css:431-442`) `height: 20px` with `line-height: 1.5` (21px) can clip 1px off the digit descender; this is verbatim the spec's own CSS example (`06-UI-SPEC.md` §2), so it is contract-conformant. Watch it once item count reaches 2 digits.

**I4 — Audit limitation (not a defect).** Local `data/app.db` is still v1.0 (`products` lacks `cost_price`) so `/` and `/products/<id>` return 500; `/cart` (empty) renders. Operator action `flask --app app init-db` is required post-Phase-6 — already flagged in 06-03-SUMMARY. Re-run this audit visually after the DB migration to confirm the populated cart table + add-to-cart block.

---

## Registry Safety

No `components.json`, no shadcn, no third-party registries. All Phase 6 CSS/templates hand-rolled (Flask/Jinja2 + plain CSS per CLAUDE.md). `.messenger-cta` fully removed (0 references). No new dependencies. Clean.

---

## Deviation Classification

**Design deviations vs UI-SPEC (must-fix to match contract):** H1 (price column styling), M1 (checkout heading role) — **both FIXED** in `f8f799d`.
**Quality gaps (fix recommended, not contract-mandated):** M2 (flash contrast) — **FIXED** in `f8f799d`; L1 (product-name weight), L3 (qty-0 edge) — still open (out of scope).
**Cosmetic / optional:** L2 (cart-actions wrap), L4 (thumb inline style), I1-I3.

---

## Files Audited

- `app/templates/public/cart.html`
- `app/templates/public/_checkout_form.html`
- `app/templates/public/product_detail.html`
- `app/templates/public/_nav.html`
- `app/templates/public/base.html`
- `app/templates/public/index.html`
- `app/templates/base.html`
- `app/static/css/style.css`
- `app/public.py` (routes + flash copy)
- `app/forms.py` (CartForm + CheckoutForm + messages)
- `.planning/phases/06-public-order-form/06-UI-SPEC.md` (contract)
- `.planning/phases/06-public-order-form/06-{01,02,03}-SUMMARY.md`
- Screenshots: `.planning/ui-reviews/cart-empty.png` (1440), `cart-empty-tablet.png` (768), `cart-empty-mobile.png` (375) — git-ignored.
