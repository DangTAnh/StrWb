---
phase: 9
verifier: gsd-verifier
status: verified
date: 2026-08-03
requirements_checked: [ORD-01, ORD-02, ORD-03, ORD-04, ORD-05, ORD-06, ORD-07, ORD-08, ORD-09, ORD-10, ORD-10a, ORD-10b, COST-01, COST-02, STAT-01, STAT-02, STAT-03, STAT-04, PLAT-05, V-01, V-02]
---

# Phase 9 Verification — Polish + Deploy v1.1 Close-out

**Verifier:** gsd-verifier (goal-backward analysis)
**Date:** 2026-08-03
**Phase:** `09-polish-deploy` — CSS/template polish (F-01…F-06), locked reverts (R-01, R-02), V-01 qty-0 edge case, V-02 3-breakpoint responsive verification, full v1.1 requirement self-check, and deploy-docs migration/PLAT-05 guard.
**Script run:** `SECRET_KEY=test python .planning/tmp/verify_11_full.py` → `TASK_OK`

---

## Requirement Traceability

| Requirement ID | Phase | Source of truth (CONTEXT.md) | Status |
|---|---|---|---|
| ORD-01 | PLAN-06 | Checkout creates Order + OrderItem snapshots with price/cost snapshot | **Verified** ✓ |
| ORD-02 | PLAN-06 | Qty > stock rejected; invalid phone rejected | **Verified** ✓ |
| ORD-03 | PLAN-06 | No qty form on out-of-stock / discontinued product detail | **Verified** ✓ |
| ORD-04 | PLAN-06 | OrderItem preserves ordered price after product price change | **Verified** ✓ |
| ORD-05 | PLAN-06 | Honeypot `website` field silent-rejects bot checkouts | **Verified** ✓ |
| ORD-06 | PLAN-07 | Admin orders list paginated (20/page); status filter | **Verified** ✓ |
| ORD-07 | PLAN-07 | Admin order detail shows customer info + items + timestamps | **Verified** ✓ |
| ORD-08 | PLAN-07 | Forward-only status transitions via TRANSITION_MAP | **Verified** ✓ |
| ORD-09 | PLAN-07 | Backward / terminal-status transitions rejected with error flash | **Verified** ✓ |
| ORD-10 | PLAN-06 | Cart add/update/remove replaces Messenger-only flow; nav cart-badge | **Verified** ✓ |
| ORD-10a | PLAN-06 | Cart cleared after successful checkout | **Verified** ✓ |
| ORD-10b | PLAN-06 | Product detail shows add-to-cart qty form when available | **Verified** ✓ |
| COST-01 | PLAN-05 | Admin product form has cost_price ("Giá nhập") field | **Verified** ✓ |
| COST-02 | PLAN-05 | Cost price never rendered on public pages | **Verified** ✓ |
| STAT-01 | PLAN-08 | Revenue = SUM(product_price × quantity) over Đã gửi + Đã nhận only | **Verified** ✓ (ported from 08-VERIFICATION) |
| STAT-02 | PLAN-08 | Profit = revenue − cost, NULL-cost items excluded | **Verified** ✓ (ported from 08-VERIFICATION) |
| STAT-03 | PLAN-08 | Orders by status (5 + total) + units sold | **Verified** ✓ (ported from 08-VERIFICATION) |
| STAT-04 | PLAN-08 | Inventory: tổng / còn hàng / hết hàng / ngừng bán | **Verified** ✓ (ported from 08-VERIFICATION) |
| PLAT-05 | deploy-docs | Idempotent init-db migration on v1.0-shaped DB; no-data-loss guard | **Verified** ✓ |
| V-01 | 09-UI-SPEC | qty-0 cart row cannot persist — stock-0 product popped + info flash | **Verified** ✓ |
| V-02 | 09-UI-SPEC | 5 v1.1 surfaces × 3 breakpoints render correctly | **Verified** ✓ |

**Coverage:** 21/21 requirement IDs — all verified against live codebase via `verify_11_full.py` against isolated temp DBs (never the real `data/app.db`).

---

## Method (Goal-Backward Analysis)

Checked whether the implemented code delivers what the phase goal promised — not just that tasks completed. Approach:

1. **Read all plans** (`09-02-PLAN.md`) to extract must_have truths and acceptance criteria (16 requirements + Phase 6 cart/checkout + V-01 + V-02).
2. **Read all summaries** to cross-reference claimed vs actual implementation.
3. **Read requirements traceability** in `REQUIREMENTS.md` — confirmed all IDs map to their phases.
4. **Read the actual code** (`app/admin.py`, `app/public.py`, `app/models.py`, `app/templates/public/cart.html`, `app/templates/public/_checkout_form.html`, `app/templates/admin/orders/detail.html`, `app/templates/admin/products/form.html`, `app/static/css/style.css`) to ground-check behavior and CSS/template fixes.
5. **Ran the verify script** against a temp DB — confirms all 21 requirement IDs with real model execution on SQLite (SQLAlchemy 2.0.51). Threat guard T-09-02 asserts the resolved DB path stays inside the temp dir; the real `data/app.db` is never touched.
6. **Captured V-02 responsive screenshots** via Chrome headless against a seeded temp DB server (`seed_serve_11.py`), verifying pass conditions for all 5 surfaces at 375/768/1440px.

---

## Requirement-by-Requirement Verification

### ORD-01 / ORD-10a — Checkout creates Order + OrderItem snapshots

**Requirement:** Checkout creates 1 Order + N OrderItem rows with price/cost snapshot; cart cleared after.

**Implementation ground-checked:**

- `app/public.py` checkout handler: creates `Order` with `customer_name/phone/address/note`, default status `Chờ xác nhận`; creates `OrderItem` rows snapshotting `product_name`, `product_price`, `product_cost_price`, `quantity` from the cart.
- `verify_11_full.py` `_verify_cart_checkout()`: asserts `new_order.items.count() == 1`, `it.product_price == 100000`, `it.product_cost_price == 60000`, `it.quantity == 2`, status `Chờ xác nhận`; asserts cart shows "Giỏ hàng trống" (empty state) after checkout.

**Verify script confirmed:** Order created with correct snapshot fields; cart cleared. ✓

### ORD-02 — Qty above stock / invalid phone rejected

**Requirement:** Adding qty > stock rejected with "Số lượng không hợp lệ"; checkout with non-digit phone rejected.

**Implementation ground-checked:**

- `app/public.py` cart-add: validates `quantity <= product.quantity` before adding to cart.
- `app/public.py` checkout: WTForms validators reject phone without digits.

**Verify script confirmed:** POST `/cart/add/{id}` with qty=999 → flash "Số lượng không hợp lệ", no cart change. Checkout with phone "abcdefg" → 0 new orders. ✓

### ORD-03 — No qty form on out-of-stock / discontinued

**Requirement:** Product detail hides add-to-cart form for `out_of_stock` or `discontinued` products.

**Implementation ground-checked:**

- `app/templates/public/product_detail.html`: conditional `{% if product.available %}` around the qty form.

**Verify script confirmed:** GET `/products/{p_stock0.id}` → no `name="quantity"` field. GET `/products/{p_disc.id}` → no qty field. GET `/products/{p_avail.id}` → qty field present. ✓

### ORD-04 — Price snapshot on OrderItem

**Requirement:** Changing product price after order creation does not alter the OrderItem's `product_price`.

**Implementation ground-checked:**

- Checkout copies `product.price` into `OrderItem.product_price` at creation time (not a FK relationship that cascades updates).

**Verify script confirmed:** After checkout, product price changed to 999999 → `OrderItem.product_price` still 100000. ✓

### ORD-05 — Honeypot + CSRF

**Requirement:** Checkout form has a hidden `website` field; filling it silently rejects (no order, redirect). CSRF enabled in production (WTF_CSRF_ENABLED=True).

**Implementation ground-checked:**

- `app/templates/public/_checkout_form.html`: `{{ wtf.hidden_field('website', class='hp-field') }}` (CSS-hidden field). `app/public.py` checkout: `if website: return redirect(...)` — silent reject.
- `_verify_ord05_csrf()` in verify script: separate app with `WTF_CSRF_ENABLED=True`, POST checkout without csrf_token → HTTP 400, 0 orders.

**Verify script confirmed:** Honeypot filled → 302 redirect, no order created. CSRF-less POST → 400, no order. ✓

### ORD-06 — Admin orders list pagination + status filter

**Requirement:** `/admin/orders` shows 20 per page with "Trang N/M" indicator; `?status=<label>` filters.

**Implementation ground-checked:**

- `app/admin.py` `orders()` route: `page = request.args.get('page', 1, type=int)`, `paginate()` at 20/page, `query_string({'status': ...})` dict-form (avoids double-encoding Vietnamese).

**Verify script confirmed:** 25 seeded orders → page 1 shows 20 rows + "Trang 1 / 2"; page 2 shows 5 rows + "Trang 2 / 2". Status filter `Đã gửi` shows exact count. ✓

### ORD-07 — Admin order detail

**Requirement:** Detail page shows customer info section, order items, order ID, timestamps.

**Implementation ground-checked:**

- `app/templates/admin/orders/detail.html: "Thông tin khách" section, order items table, `#{order.id}`, created_at.

**Verify script confirmed:** GET `/admin/orders/{id}` → 200, "Thông tin khách" present, `#{id}` present. ✓

### ORD-08 / ORD-09 — Forward-only status transitions

**Requirement:** Status transitions follow `TRANSITION_MAP` (Chờ xác nhận → Đã gói/Đã hủy; Đã gói → Đã gửi; Đã gửi → Đã nhận). Backward or terminal transitions rejected with "Không thể chuyển" flash.

**Implementation ground-checked:**

- `app/admin.py: TRANSITION_MAP` dict; `admin.order_status()` route checks `current_status in TRANSITION_MAP and next_status in TRANSITION_MAP[current_status]`.
- `app/templates/admin/orders/detail.html`: `confirm('Bạn có chắc chuyển sang "{{ next }}"?')`.

**Verify script confirmed:** Chờ xác nhận → Đã góp (200, status updated). Chờ xác nhận → Đã hủy (200, status updated). Đã gói → Chờ xác nhận (rejected, flash "Không thể chuyển", status unchanged). Terminal Đã hủy → Đã gói (rejected, unchanged). Terminal Đã nhận → Đã hủy (rejected, unchanged). ✓

### ORD-10 — Cart add/update/remove + nav badge

**Requirement:** Cart add replaces Messenger CTA; cart-badge appears when non-empty, hidden when empty; update replaces qty; remove clears line.

**Implementation ground-checked:**

- `app/public.py`: `/cart/add/{id}`, `/cart/update/{id}`, `/cart/remove/{id}` POST routes with CSRF.
- `app/templates/public/_navbar.html`: `{% if session.get('cart') and session['cart']|length > 0 %}` shows `.cart-badge`.

**Verify script confirmed:** Add 2× → home shows `.cart-badge`. Update to 1 → line total 100.000. Remove → cart-badge hidden. ✓

### ORD-10a — Cart cleared after checkout

**Requirement:** After successful checkout, session cart is emptied.

**Verify script confirmed:** POST checkout → GET `/cart` shows "Giỏ hàng trống". ✓

### ORD-10b — Add-to-cart form on available product detail

**Requirement:** Available product detail shows qty input + add-to-cart button.

**Verify script confirmed:** GET `/products/{p_avail.id}` → `name="quantity"` field present. ✓

### COST-01 — Admin form has Giá nhập field

**Requirement:** `app/templates/admin/products/form.html` renders `cost_price` field with label "Giá nhập".

**Implementation ground-checked:**

- `app/templates/admin/products/form.html`: `{{ wtf.hidden_field(csrf_token) }}` + `{{ wtf.form_field(form.cost_price, ...) }}` with label rendering.

**Verify script confirmed:** GET `/admin/products/new` → "Giá nhập" in response. ✓

### COST-02 — Cost price never on public pages

**Requirement:** "Giá nhập" label never appears on home, search, or product detail.

**Verify script confirmed:** GET `/`, `/search?q=Áo`, `/products/{id}` (authenticated + unauthenticated) → "Giá nhập" absent in all responses. ✓

### STAT-01 — Total revenue (Đã gửi + Đã nhận only)

**Requirement:** Revenue = `sum(product_price * quantity)` over orders with status `Đã gửi` or `Đã nhận`.

**Implementation ground-checked:**

- `app/admin.py:14` — `REVENUE_STATUSES = ('Đã gửi', 'Đã nhận')`.
- `app/admin.py:155-160` — query with `Order.status.in_(REVENUE_STATUSES)` + `coalesce(sum(...), 0)`.

**Verify script confirmed:** Full-seed revenue = 700.000₫ (100k×2 + 200k×1 + 300k×1). Empty-DB: 0₫. ✓

### STAT-02 — Profit (revenue − cost, NULL-safe)

**Requirement:** Profit = Σ((product_price − product_cost_price) × quantity) over revenue-status orders where cost_price IS NOT NULL.

**Implementation ground-checked:**

- `app/admin.py:167-176` — `sum((product_price - product_cost_price) * quantity)` with `.isnot(None)` guard.

**Verify script confirmed:** Full-seed profit = 180.000₫. Profit note "Lợi năng tính trên 2 sản phẩm có giá nhập." present (1 NULL-cost item excluded). Empty-DB: 0₫, note absent. ✓

### STAT-03 — Orders by status + units sold

**Requirement:** 5 statuses + total count; units sold = Σ quantity over revenue-status orders.

**Implementation ground-checked:**

- `app/admin.py:191-194` — `group_by(Order.status).count()`.
- `app/admin.py:158` — `units_sold` in the same revenue query.

**Verify script confirmed:** Full-seed: 25 seeded + 1 checkout = 26 orders. Status breakdown all 5 present. Units sold = 4. ✓

### STAT-04 — Inventory counts

**Requirement:** 4 cards: Tổng sản phẩm (all), Còn hàng (qty>0, not discontinued), Hết hàng (qty=0, not discontinued), Ngừng bán (discontinued).

**Implementation ground-checked:**

- `app/admin.py:196-201` — 4 separate queries with disjoint filters using `.is_(True)` / `.is_(False)`.

**Verify script confirmed:** Full-seed: Tổng=4, Còn hàng=2, Hết hàng=1, Ngừng bán=1. Discontinued product with qty=0 counted only under Ngừng bán (disjoint buckets). ✓

### PLAT-05 — Idempotent migration + no-data-loss guard

**Requirement:** `flask --app wsgi init-db` upgrades a v1.0-shaped DB (products w/o cost_price, legacy orders w/ product_name column) idempotently; aborts with "Manual migration required" if legacy orders table has rows.

**Implementation ground-checked:**

- `app/__init__.py` / `app/cli.py` `init_db` command: checks for existing tables; if `products` exists but lacks `cost_price` column → `ALTER TABLE products ADD COLUMN cost_price ...`; if `orders` has legacy `product_name` column and has rows → abort with "Manual migration required"; if no rows → drop and recreate with new schema; creates `order_items` table.
- Uses separate temp DB (`gsd_verify_plat05_` prefix) to avoid collision with main v1.1 seed DB.

**Verify script confirmed:** v1.0-shaped DB → init-db adds `cost_price`, removes legacy `product_name` from orders, creates `order_items`. Legacy orders w/ rows → exit code ≠ 0, "Manual migration required" in output. Idempotent re-run on clean DB → exit code 0. ✓

### V-01 — qty-0 cart row cannot persist

**Requirement:** When a product drops to stock 0 mid-session, it is popped from the cart with an info flash; no qty-0 row renders.

**Implementation ground-checked:**

- `app/public.py` cart render: filters cart items to `product.available` (qty > 0, not discontinued); sets info flash "Sản phẩm ... đã ngừng bán hoặc hết hàng".

**Verify script confirmed:** Product at qty 1 → added to cart → stock dropped to 0 → GET `/cart` → "đã ngừng bán hoặc hết hàng" flash present, "Giỏ hàng trống" empty state shown, no stale qty-0 row. ✓

### V-02 — Responsive verification (3 breakpoints × 5 surfaces)

**Requirement:** 5 v1.1 surfaces render correctly at 375/768/1440px.

**Method:** Seeded temp DB server (`seed_serve_11.py`, 127.0.0.1:8011) with `AdminAuthMiddleware`; Chrome headless screenshots at all 15 viewport/surface combinations.

**Pass matrix:**

| Surface | 375 (mobile) | 768 (tablet) | 1440 (desktop) | Pass condition | Status |
|---------|--------------|--------------|----------------|----------------|--------|
| Cart (populated, 2 items) | `populated-cart-mobile.png` | `populated-cart-tablet.png` | `populated-cart-desktop.png` | `.table-scroll` on mobile; `.cart-actions` wraps (F-01); `.cart-thumb` renders (F-02); no horizontal overflow | **PASS** ✓ |
| Checkout form section | `checkout-form-mobile.png` | `checkout-form-tablet.png` | `checkout-form-desktop.png` | Fields full-width on mobile; `.checkout-form .btn` class no inline style (F-06); phone help-text wraps | **PASS** ✓ |
| Admin orders list | `orders-list-mobile.png` | `orders-list-tablet.png` | `orders-list-desktop.png` | `.table-scroll` on mobile; filter stacks on mobile; pagination fits | **PASS** ✓ |
| Admin order detail | `orders-detail-mobile.png` | `orders-detail-tablet.png` | `orders-detail-desktop.png` | stepper scrolls horizontally on mobile; action-row buttons stack full-width | **PASS** ✓ |
| Admin stats | `stats-mobile.png` | `stats-tablet.png` | `stats-desktop.png` | `.stats-grid` 1→2→3 columns; stat cards fit; breakdown rows ≥44px | **PASS** ✓ |

**Fix verification (F-01…F-06):**

- **F-01** `.cart-actions { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 16px; }` — `flex-wrap: wrap` present, buttons wrap at 320px. ✓
- **F-02** `.cart-thumb { width: 80px; height: 80px; object-fit: cover; border-radius: 4px; vertical-align: middle; }` — class present on `<img>`, inline style removed. ✓
- **F-03** `.cart-badge { line-height: 1; }` — set to `1` (was `1.5`), 2-digit pills no longer clip. ✓
- **F-04** `.line-total` shared accent treatment on cart + order-detail — both render `.line-total` with accent `#2563EB`. ✓
- **F-05** "Tổng cộng" no colon on both `cart.html:51` and `detail.html:38` — both show `Tổng cộng`. ✓
- **F-06** `.checkout-form .btn { width: 100%; max-width: 320px; }` — class present, inline style removed from `_checkout_form.html`. ✓

**Reverts verified:**

- **R-01** `README.md:1` → `# StoreWeb` (leading-space heading marker restored). ✓
- **R-02** `form.html` quantity block → `<p class="help-text">Trạng thái tự động: Còn hàng khi tồn kho &gt; 0, Hết hàng khi tồn kho = 0. Bật "Ngừng bán" để ghi đè.</p>` restored. ✓

---

## Security Verification

- **Threat guard T-09-02:** `_setup_app()` in verify script asserts `resolved_db.startswith(os.path.abspath(tmpdir))` and `'app.db' in resolved_db` — temp DB never escapes tmpdir. ✓
- **CSRF:** ORD-05 CSRF facet tested with separate CSRF-enabled app instance → 400 on token-less POST. Production `WTF_CSRF_ENABLED` defaults True; verify harness only disables it for convenience. ✓
- **Honeypot:** `website` field CSS-hidden, silent-rejects bot checkouts without order creation. ✓
- **Admin auth:** All `/admin/*` routes protected by `_protect_admin` before_request (inherited from Phase 7); stats, orders, CRUD all 302-redirect to `/login` when unauthenticated. ✓
- **Cost never public:** COST-02 verified — "Giá nhập" label absent on all public pages (auth + unauth). ✓
- **No secrets in responses:** SECRET_KEY/test values only in temp DB; real `.env` values never loaded during verification. ✓

---

## Verify Script Output

```
$ SECRET_KEY=test python .planning/tmp/verify_11_full.py
Verify: Cart + Checkout (ORD-01/02/03/04/05, ORD-10/10a/10b)
  [cart/checkout] ORD-01/02/03/04/05, ORD-10/10a/10b, ORD-04 snapshot ... OK
Verify: Order tracking (ORD-06, ORD-07, ORD-08, ORD-09)
  [order tracking] ORD-06 (pagination+filter), ORD-07, ORD-08, ORD-09 ... OK
Verify: Cost price (COST-01, COST-02)
  [cost] COST-01 form field, COST-02 never public ... OK
Verify: Stats (STAT-01, STAT-02, STAT-03, STAT-04)
  [stats] STAT-01/02/03/04 ... OK
Verify: V-01 qty-0 edge (stock hit 0 mid-session)
  [V-01] stock-0 product popped + info flash + no qty-0 row ... OK
Verify: v1.0 regression smoke (catalog/search/contact/admin CRUD)
  [v1.0 smoke] catalog/detail/search/contact/admin CRUD ... OK
Verify: PLAT-05 migration (idempotent + no-data-loss guard)
  [PLAT-05] idempotent migration: cost_price added, orders rebuilt ... OK
  [PLAT-05 guard] legacy orders w/ rows aborts with 'Manual migration required' ... OK
Verify: v1.0 regression smoke (catalog/search/contact/admin CRUD)
  [v1.0 smoke] catalog/detail/search/contact/admin CRUD ... OK
Verify: ORD-05 CSRF facet (WTF_CSRF_ENABLED=True, token-less checkout)
  [ORD-05 CSRF] token-less checkout rejected 400, 0 orders ... OK
Verify: Empty-DB stats zeros (STAT-01..04)
  [empty stats] all zeros render ... OK
TASK_OK
```

Exit code 0. All assertions pass.

---

## Self-Assessment — must_haves vs Reality

| must_have (from 09-02-PLAN.md) | Actual code | Status |
|---|---|---|
| F-01: `.cart-actions` has `flex-wrap: wrap` | `style.css:454` | ✓ |
| F-02: `.cart-thumb` class, inline style removed | `style.css:446`, `cart.html:24` | ✓ |
| F-03: `.cart-badge` `line-height: 1` | `style.css:432-443` | ✓ |
| F-04: `.line-total` accent shared on cart + order-detail | `cart.html:38`, `detail.html:32` | ✓ |
| F-05: "Tổng cộng" no colon on both surfaces | `cart.html:51`, `detail.html:38` | ✓ |
| F-06: `.checkout-form .btn` class, inline style removed | `style.css:456`, `_checkout_form.html:22` | ✓ |
| R-01: README heading `# StoreWeb` | `README.md:1` | ✓ |
| R-02: product-form help-text restored | `form.html:68` | ✓ |
| V-01: qty-0 product popped + info flash | `public.py` cart render | ✓ |
| V-02: 15 screenshots pass (5 surfaces × 3 breakpoints) | `.planning/ui-reviews/` | ✓ |
| All 16 phase requirements (ORD-01..09, COST-01/02, STAT-01..04, PLAT-05) verified | `verify_11_full.py` | ✓ |
| Phase 6 cart/checkout reqs (ORD-10/10a/10b) verified | `verify_11_full.py` | ✓ |
| ORD-05 CSRF facet verified (400 on token-less) | `_verify_ord05_csrf()` | ✓ |
| v1.0 regression smoke (catalog/detail/search/contact/CRUD) | `_verify_v10_regression()` | ✓ |
| PLAT-05 idempotent migration + no-data-loss guard | `_verify_plat05()` | ✓ |
| Empty-DB stats render zeros (no 500) | `_verify_empty_stats()` | ✓ |
| Threat guard T-09-02: temp DB isolation | `_setup_app()` | ✓ |

---

## Conclusion

**Phase 9 goal: ACHIEVED.** All 21 requirement IDs (ORD-01..09, ORD-10/10a/10b, COST-01/02, STAT-01..04, PLAT-05, V-01, V-02) are verified against the live codebase via `verify_11_full.py` → `TASK_OK`. The six polish fixes (F-01…F-06) and two locked reverts (R-01, R-02) are in place and confirmed by both code inspection and responsive screenshots. V-01 (qty-0 cart edge case) is asserted by the verify harness. V-02 (3-breakpoint responsive) is confirmed by 15 screenshots in `.planning/ui-reviews/`, all passing the pass-condition matrix in 09-UI-SPEC.md.

**No new dependencies added.** Reuses `format_price`, `coalesce` on every SUM, `order_badge_class`, `order_badge_class`, and the Phase 7 `group_by` pattern. The verify harness runs entirely against temp DBs (threat guard T-09-02 enforced); the real `data/app.db` is never touched during verification.

**Non-blocking human UAT list (production deployment):**
1. Run `flask --app wsgi init-db` against the real DB to apply the PLAT-05 migration (idempotent; aborts safely if legacy orders have rows).
2. Verify `https://YOUR_DOMAIN/` returns 200 after nginx + HTTPS (Let's Encrypt).
3. Verify admin login + dashboard render in production with real `.env` SECRET_KEY.
4. Verify stats dashboard shows real revenue/profit/inventory numbers.
5. Spot-check V-02 surfaces in a real browser at 375/768/1440px.

---

**Reviewed:** 2026-08-03
**Status:** verified
