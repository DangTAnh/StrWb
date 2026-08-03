---
phase: 06-public-order-form
plan: 02
subsystem: ui
tags: [flask, session, jinja2, cart, csrf]

# Dependency graph
requires:
  - phase: 06-public-order-form 06-01
    provides: Order + OrderItem refactor, Product.status property, Product.primary_image / ProductImage.thumb_filename, PRAGMA foreign_keys=ON
provides:
  - Session cart `{product_id(str): quantity(int)}` + 4 public routes (cart_add / cart / cart_update / cart_remove) + CartForm
  - cart.html single-page cart (line-item table + total + empty state + checkout placeholder include)
  - Nav cart-link with badge (len(session['cart']), hidden when empty)
  - Status-gated add-to-cart block replacing the detail-page Messenger CTA; stale-item filtering with flash info
affects: [06-03 checkout, 07-admin-order-tracking]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Session cart mutation gotcha: always reassign whole dict `session['cart'] = cart` (never mutate child dict) so Flask marks session modified"
    - "Status-gated render: `{% if product.status == 'available' %} add-to-cart {% elif out_of_stock %} note {% endif %}` (discontinued renders neither)"
    - "Stale-item filter at render: skip non-digit keys (T-06-02), deleted product -> silent pop (no flash, avoids leaking id), unavailable -> pop + flash info"
    - "Every POST cart form carries csrf_token() + CSRFProtect app-wide (POST without token -> 400)"

key-files:
  created:
    - app/templates/public/cart.html
  modified:
    - app/forms.py
    - app/public.py
    - app/templates/public/product_detail.html
    - app/templates/public/_nav.html
    - app/static/css/style.css

key-decisions:
  - "Plan-checker advisory 1 (flash stale-item mâu thuẫn nội tại): resolved per the inline comment — deleted product (product is None) is silently removed (no flash, avoids leaking id); flash info only when product exists but is out_of_stock/discontinued"
  - "Plan-checker advisory 2: cart_update now checks product.status == 'available' (not just qty range) for consistency with cart_add"
  - "Plan-checker advisory 3: cart.html thumb URL written fully: url_for('static', filename='uploads/' + item.product.primary_image.thumb_filename) — mirrors product_detail.html pattern"
  - "Add-to-cart replaces qty (not increments) per UI-SPEC; server re-validates 1 <= qty <= product.quantity; min/max attributes are client hints only"

patterns-established:
  - "Pattern: Flask session cookie is untrusted state -> every cart read re-validates product existence/status/stock server-side (T-06-01/02)"
  - "Pattern: template include placeholder `{% include \"public/_checkout_form.html\" ignore missing %}` lets cart page render before 06-03 ships the checkout form"
  - "Pattern: CSS `.link-danger` used as `<button type=\"submit\">` needs `button.link-danger` reset (background:none/border:none) — done"

requirements-completed: [ORD-10, ORD-10b, ORD-03]

# Metrics
duration: 7min
completed: 2026-08-02
---

# Phase 6 Plan 2: Session Cart + Cart Routes + Cart Page Summary

**Session cart (ORD-10): CartForm + 4 public routes (add/update/remove/view) with server-side qty validation, cart.html line-item table with format_price totals and empty state, nav cart-badge (len session cart), and a status-gated add-to-cart block replacing the detail-page Messenger CTA (ORD-10b) with stale-item filtering + flash info (ORD-03) — zero new dependencies**

## Performance

- **Duration:** 7 min
- **Started:** 2026-08-02T08:22:33Z
- **Completed:** 2026-08-02T08:29:56Z
- **Tasks:** 2
- **Files modified:** 6 (1 created, 5 modified)

## Accomplishments
- `CartForm` (quantity IntegerField, InputRequired + NumberRange min=1) in `app/forms.py`
- 4 public routes in `app/public.py`: `cart_add` (POST /cart/add/<id>), `cart` (GET /cart), `cart_update` (POST /cart/update/<id>), `cart_remove` (POST /cart/remove/<id>) — all session writes reassign the full dict to mark modified
- `cart` route filters stale items at render: non-digit keys skipped, deleted products silently removed, out-of-stock/discontinued removed with a Vietnamese `info` flash
- `cart.html` (new): 5-column `.data-table` (thumb + name, unit price, qty update form, line total, remove form), cart-total via `format_price`, cart-actions, checkout section with `{% include "public/_checkout_form.html" ignore missing %}` (placeholder for 06-03), and an empty-state with CTA
- `product_detail.html`: Messenger CTA replaced by status-gated add-to-cart block (csrf, qty min=1 max=stock, help-text "Còn N sản phẩm trong kho"); out-of-stock note preserved in elif branch; homepage `.contact-strip` Messenger CTA untouched
- `_nav.html`: cart-link "Giỏ hàng" + cart-badge showing `len(session['cart'])`, hidden entirely when cart is empty
- `style.css`: added `.cart-link`, `.cart-badge`, `.add-to-cart-form`, `.cart-cta`, `.cart-qty-form`, `.cart-qty-input`, `.honeypot`, `.cart-total*`, `.cart-actions`, `.checkout-section`, `button.link-danger` reset; removed unused `.messenger-cta`

## Task Commits

Each task was committed atomically:

1. **Task 1: CartForm + routes cart_add / cart / cart_update / cart_remove** - `c3ae1eb` (feat)
2. **Task 2: Trang chi tiết add-to-cart + nav badge + cart.html + CSS** - `28eea4c` (feat)

**Plan metadata:** `docs(06-02): complete plan — cart session + routes + cart page` (final commit after SUMMARY/STATE/ROADMAP)

## Files Created/Modified
- `app/forms.py` - Added `CartForm(FlaskForm)` with quantity IntegerField (InputRequired + NumberRange min=1)
- `app/public.py` - Imports `flash`, `session`, `CartForm`; added 4 cart routes; kept home/product_detail/search unchanged
- `app/templates/public/product_detail.html` - Messenger CTA replaced by status-gated add-to-cart block; out-of-stock note in elif branch
- `app/templates/public/_nav.html` - Added cart-link with conditional cart-badge
- `app/templates/public/cart.html` - NEW: cart table + total + actions + checkout placeholder + empty state
- `app/static/css/style.css` - Added Phase 6 cart CSS block; removed `.messenger-cta`

## Decisions Made
- Followed plan as specified, including the three plan-checker advisories (flash stale-item resolution per comment, cart_update status check, full thumb URL expression in cart.html).
- Add-to-cart replaces quantity rather than incrementing (UI-SPEC "replace, not increment").

## Deviations from Plan

### Advisory Applications (plan-checker — applied during execution, not Rule 1-3 auto-fixes)

**1. [Advisory] Resolved flash stale-item contradiction in `cart()`**
- **Found during:** Task 1 (cart route)
- **Issue:** Plan action text flashed a message using `pid_str` when `product is None`, while its own comment said "(Chỉ flash khi product còn tồn tại — tránh lộ thông tin id.)"
- **Fix:** Implemented per the comment: `product is None` → silent `cart.pop` (no flash); only products that exist but are unavailable get the `info` flash with their real name.
- **Files modified:** app/public.py
- **Verification:** Task 1/2 verifies + smoke test pass; session cleaned, flash contains real product name for unavailable items.
- **Committed in:** c3ae1eb

**2. [Advisory] cart_update now checks `product.status == 'available'`**
- **Found during:** Task 1 (cart_update route)
- **Issue:** cart_update validated only `1 <= qty <= product.quantity`, inconsistent with cart_add's status gate.
- **Fix:** Added `product.status != 'available'` to the invalid branch (flash error + redirect /cart).
- **Files modified:** app/public.py
- **Committed in:** c3ae1eb

**3. [Advisory] cart.html thumb URL written fully**
- **Found during:** Task 2 (cart.html)
- **Issue:** Plan elided the thumbnail URL expression.
- **Fix:** Wrote `url_for('static', filename='uploads/' + item.product.primary_image.thumb_filename)` mirroring product_detail.html.
- **Files modified:** app/templates/public/cart.html
- **Committed in:** 28eea4c

---

**Total deviations:** 0 auto-fixed (Rule 1-3); 3 advisory applications implemented
**Impact on plan:** Advisories were correctness/consistency requirements; no scope creep.

## Issues Encountered
- None blocking. Both task verify scripts passed first run, printing `TASK_OK`. During an additional regression smoke test, two initial assertions failed due to test-harness mistakes (not app bugs): (1) asserting the stale-item flash verbatim ignored Jinja2 HTML autoescaping (`'` renders as `&#39;`); (2) asserting the stale product name is absent from the page while the flash legitimately contains it. Corrected assertions; app behavior confirmed correct. This is expected/desired autoescaping, not a defect.

## Stub Tracking
- `app/templates/public/cart.html` includes `{% include "public/_checkout_form.html" ignore missing %}` — `_checkout_form.html` does not exist yet. **Intentional**: the checkout form ships in 06-03; `ignore missing` lets the cart page render before that file exists. Resolved by 06-03.

## Threat Flags
No new security surface beyond the plan's threat model. All POST cart routes are CSRF-protected app-wide (POST without token → 400, verified). No `cost_price` / `Giá nhập` in `app/templates/public/` (grep gate 0 hits). Non-digit session keys and deleted/unavailable products are filtered at render (T-06-02). Quantity tampering re-validated server-side (T-06-01).

## Next Phase Readiness
- Ready for 06-03 (checkout): `CartForm` + 4 cart routes + cart page in place; `public._checkout_form.html` include is the single insertion point for the checkout form. `cart()` already passes filtered `items` + `total` to the template for checkout re-validation.
- Blockers: none. Real `data/app.db` still v1.0; operator will run `flask --app app init-db` post-Phase-6 (unchanged from 06-01 note).

## Self-Check: PASSED
- FOUND: app/forms.py (CartForm with quantity IntegerField + NumberRange(min=1))
- FOUND: app/public.py (cart_add / cart / cart_update / cart_remove; imports flash, session, CartForm)
- FOUND: app/templates/public/cart.html (data-table, caption.visually-hidden, 5 th scope=col, qty POST form, remove POST form, checkout include ignore missing, empty state)
- FOUND: app/templates/public/product_detail.html (cart_add form, csrf_token(), name="quantity", max="{{ product.quantity }}", no "Mua qua Messenger")
- FOUND: app/templates/public/_nav.html (a.cart-link → public.cart, span.cart-badge when cart_count > 0)
- FOUND: app/static/css/style.css (.cart-badge, .cart-link, .cart-qty-form, .cart-qty-input, .honeypot, .cart-total, .cart-cta, button.link-danger; no .messenger-cta)
- FOUND: commit c3ae1eb (Task 1)
- FOUND: commit 28eea4c (Task 2)

---
*Phase: 06-public-order-form*
*Completed: 2026-08-02*
