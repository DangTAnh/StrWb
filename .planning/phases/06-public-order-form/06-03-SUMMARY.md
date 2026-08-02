---
phase: 06-public-order-form
plan: 03
subsystem: api
tags: [flask, wtforms, csrf, honeypot, order, orderitem, jinja2]

# Dependency graph
requires:
  - phase: 06-public-order-form 06-01
    provides: Order (customer-only 8 cột) + OrderItem snapshot (FK order_id CASCADE, product_id nullable SET NULL, CheckConstraint quantity >= 1)
  - phase: 06-public-order-form 06-02
    provides: Session cart `{product_id(str): quantity}` + cart routes + cart.html include `_checkout_form.html` (placeholder)
provides:
  - CheckoutForm (customer_name/phone/address bắt buộc, note optional, website honeypot; SĐT 8-11 chữ số qua Regexp + digit-count)
  - POST /cart/checkout route: honeypot silent reject -> empty-cart guard -> form.validate -> server re-validate từng món -> tạo 1 Order + nhiều OrderItem snapshot trong 1 commit -> xóa giỏ + flash success + redirect chi tiết
  - `_checkout_form.html` partial (CSRF + honeypot + 4 field) được cart.html include — single-page cart+checkout trên /cart
affects: [07-admin-order-tracking, 09-polish-deploy]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Honeypot silent reject: field 'website' truthy -> redirect /cart trước mọi logic (không flash, không ghi DB, không đụng giỏ)"
    - "Optional field edge case: WTForms 3.2.2 Optional không set field.data; field vắng mặt khỏi POST -> data=None -> luôn guard `(data or '').strip() or None`"
    - "Snapshot tại checkout: OrderItem product_name/price/cost_price từ product hiện tại, không từ session (giá có thể đổi giữa add & checkout)"
    - "Single-commit order: db.session.add(order) -> flush() lấy order.id -> add từng OrderItem -> commit()"

key-files:
  created:
    - app/templates/public/_checkout_form.html
  modified:
    - app/forms.py
    - app/public.py

key-decisions:
  - "Thứ tự route checkout: honeypot -> empty-cart guard -> form.validate -> re-validate cart -> tạo đơn -> xóa giỏ + flash + redirect. Honeypot chạy TRƯỚC CSRF-check? Không — CSRFProtect app-level chặn 400 trước khi route chạy; honeypot check là check đầu trong route."
  - "Optional note guard: `(form.customer_note.data or '').strip() or None` — plan ghi `data.strip() or None` nhưng crash khi field vắng mặt (data=None) — sửa Rule 1"
  - "Redirect về trang chi tiết sản phẩm ĐẦU TIÊN trong giỏ (items_to_save[0]) — theo 06-UI-SPEC step 9"
  - "Không giảm tồn kho khi đặt (ORD-12 deferred v2); không cài admin notification (ORD-11 deferred)"

patterns-established:
  - "Pattern: validate_customer_phone (field-level WTForms validator) là check chính — Regexp chỉ lọc charset + độ dài thô"
  - "Pattern: template partial không extends base.html, render trong include của trang public; `{% include ... ignore missing %}` cho phép triển khai theo wave"
  - "Pattern: mọi POST form public mang csrf_token() (CSRFProtect app-wide) — POST thiếu token -> 400"

requirements-completed: [ORD-01, ORD-02, ORD-03, ORD-05]

# Metrics
duration: 10min
completed: 2026-08-02
---

# Phase 6 Plan 3: CheckoutForm + Checkout Route + Checkout Form Partial Summary

**Checkout đặt hàng nhiều sản phẩm (ORD-01/02/03/05, ORD-10a): CheckoutForm (tên/SĐT/địa chỉ bắt buộc, ghi chú tùy chọn, SĐT 8-11 chữ số qua Regexp + digit-count, honeypot 'website') + route POST /cart/checkout (honeypot silent reject → empty-cart guard → form.validate → server re-validate từng món available + 1≤qty≤tồn kho → tạo 1 Order + nhiều OrderItem snapshot trong 1 commit → xóa giỏ + flash success + redirect về trang chi tiết) + partial `_checkout_form.html` (CSRF + honeypot + 4 field) được cart.html include — zero new dependencies, tồn kho KHÔNG giảm (ORD-12 → v2)**

## Performance

- **Duration:** 10 min
- **Started:** 2026-08-02T15:41:00Z (≈)
- **Completed:** 2026-08-02T15:50:38Z
- **Tasks:** 2
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments
- `CheckoutForm` trong `app/forms.py`: customer_name (DataRequired + Length max 100), customer_phone (DataRequired + Regexp `^\+?[\d\s-]{8,15}$` + `validate_customer_phone` đếm 8–11 chữ số), customer_address (DataRequired + Length max 500), customer_note (Optional + Length max 1000), website (honeypot), submit; imports `Regexp` + `ValidationError`
- Route `checkout()` trong `app/public.py`: 6 bước theo plan — honeypot silent reject (không flash/không đơn/không đụng giỏ) → empty-cart guard → form.validate → server re-validate TỪNG món (product tồn tại + status 'available' + `1 <= qty <= product.quantity`; sai → flash lỗi, KHÔNG tạo đơn) → tạo 1 Order + nhiều OrderItem snapshot (product_name/price/cost_price/quantity tại thời điểm đặt) trong 1 commit → `session['cart'] = {}` + flash success xanh + redirect về trang chi tiết sản phẩm đầu tiên trong giỏ
- `_checkout_form.html` (new): partial KHÔNG extends base.html — form POST `/cart/checkout` + csrf_token() + honeypot `website` (`.honeypot` display:none) + 4 field (name max 100, phone type=tel + help-text "8–11 chữ số...", address textarea max 500, note textarea max 1000 + placeholder) + submit `.btn.btn-primary` — markup theo 06-UI-SPEC verbatim; được cart.html include hiển thị trong `.checkout-section` trên trang giỏ
- Verify Task 1 (9 cases) + Task 2 (partial render + integration GET /cart) + grep gate (`cost_price|Giá nhập` trong `app/templates/public/` = 0 hits) đều pass

## Task Commits

Each task was committed atomically:

1. **Task 1: CheckoutForm + route checkout POST /cart/checkout** - `01caee7` (feat)
2. **Task 2: _checkout_form.html (CSRF + honeypot + 4 field)** - `367b723` (feat)

**Plan metadata:** SUMMARY + STATE/ROADMAP committed với plan completion

**Auto-fix bổ sung sau Task 2** (Rule 1 bug, smoke test bắt được):

3. **Fix: guard customer_note None khi field vắng mặt** - `5c92fb3` (fix)

## Files Created/Modified
- `app/forms.py` - Added `CheckoutForm` (name/phone/address bắt buộc, note optional, website honeypot, validate_customer_phone digit-count); imports `Regexp` + `ValidationError`
- `app/public.py` - Imports `CheckoutForm`, `Order`, `OrderItem`; added `checkout()` route POST /cart/checkout (6 bước); fix `(customer_note.data or '').strip() or None`
- `app/templates/public/_checkout_form.html` - NEW: checkout form partial (CSRF + honeypot + 4 field + submit) — include điểm của cart.html

## Decisions Made
- Followed plan as specified, gồm 2 điều chỉnh: (1) Rule 1 fix optional-note guard; (2) verify-harness Task 2 cần request context cho `url_for()`.
- Redirect về trang chi tiết sản phẩm ĐẦU TIÊN trong giỏ theo 06-UI-SPEC step 9 (`items_to_save[0][0].id`).
- Advisory plan-checker về UX form reset khi validation fail (redirect `/cart` làm mất input): chấp nhận đúng spec — UI-SPEC Checkout Flow dùng flash summary, không yêu cầu giữ input. Ghi nhận, không sửa.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Optional note field vắng mặt trong POST → crash `customer_note.data.strip()`**
- **Found during:** Smoke test sau Task 2 (không nằm trong verify script của plan)
- **Issue:** Plan ghi `customer_note=form.customer_note.data.strip() or None`. WTForms 3.2.2 `Optional` validator không set `field.data`; khi `customer_note` không có trong POST, `form.customer_note.data` là `None` → `AttributeError: 'NoneType' object has no attribute 'strip'` (500). Verify script của plan không bắt được vì các case reject (thiếu field bắt buộc/honeypot/giỏ trống/tamper) xảy ra trước BƯỚC 5, và happy path luôn gửi note.
- **Fix:** `customer_note=(form.customer_note.data or '').strip() or None` — guard None → `''` → None khi vắng mặt/whitespace.
- **Files modified:** app/public.py
- **Verification:** Smoke test end-to-end pass: note vắng mặt + note whitespace → order tạo với `customer_note is None`; Task 1 verify (9 cases) vẫn pass.
- **Committed in:** 5c92fb3 (fix commit riêng sau Task 2)

---

**Total deviations:** 1 auto-fixed (1 Rule 1 bug)
**Impact on plan:** Fix cần thiết cho correctness — form hợp lệ (không ghi chú) trước đó crash 500. Không scope creep.

## Issues Encountered

- **Task 2 verify-harness cần request context cho `url_for()` (không phải bug app):** Plan verify render partial standalone trong `app.app_context()`, nhưng `url_for('public.checkout')` cần request context khi không cấu hình `SERVER_NAME` → `RuntimeError: Unable to build URLs outside an active request`. Không đổi template; wrapper harness bằng `app.test_request_context('/cart')` quanh lệnh render. Integration check (GET /cart qua test client) vốn có request context nên pass nguyên vẹn.

## Stub Tracking
- `app/templates/public/cart.html` include `{% include "public/_checkout_form.html" ignore missing %}` — **đã resolved**: file `_checkout_form.html` tồn tại từ Task 2, form render trong `.checkout-section`. Không còn stub.
- `OrderItem.product_cost_price` nullable Integer = lựa chọn data-model thật (NULL = sản phẩm không nhập cost), không phải stub.

## Threat Flags
No new security surface beyond the plan's threat model:
- T-06-01 honeypot: field 'website' truthy → silent reject (verified: redirect /cart, không flash, không đơn, giỏ nguyên)
- T-06-02 CSRF: POST thiếu token → 400 (verified trên instance CSRF-enabled; `csrf_token()` trong form)
- T-06-03 tamper/hết hàng/ngừng bán: server re-validate từng món → không tạo đơn (verified: qty 99 > tồn kho 5, product discontinued)
- T-06-05 cost_price: grep gate `cost_price|Giá nhập` trong `app/templates/public/` = 0 hits; route chỉ GHI cost_price vào OrderItem, không render public
- T-06-07 oversell (không trừ tồn kho): accept theo ORD-12 deferred v2 — ghi nhận ở SUMMARY này

## User Setup Required
None - không có cấu hình external service. (Operator action deferred từ Phase 5/6: chạy `flask --app app init-db` trên `data/app.db` thật sau Phase 6.)

## Next Phase Readiness
- Checkout luồng hoàn chỉnh: khách thêm giỏ → trang /cart hiện form → đặt hàng → Order + OrderItem trong DB + flash success. Sẵn sàng cho Phase 7 (admin order tracking): `Order` + `OrderItem` có đủ dữ liệu (customer + snapshot items) để admin xem/xử lý đơn sau `@login_required`.
- Blockers: none. `app/templates/admin/products/form.html` uncommitted của user được giữ nguyên xuyên suốt (không stage, không revert, không commit).

## Self-Check: PASSED
- FOUND: app/forms.py (class CheckoutForm; imports Regexp + ValidationError; validate_customer_phone 8-11 digits)
- FOUND: app/public.py (def checkout(); route /cart/checkout POST; honeypot -> empty cart -> form.validate -> re-validate -> Order + OrderItem -> xóa giỏ + flash success + redirect detail)
- FOUND: app/templates/public/_checkout_form.html (action url_for('public.checkout'), csrf_token, website.honeypot, 4 field, submit btn-primary)
- FOUND: commit 01caee7 (Task 1)
- FOUND: commit 367b723 (Task 2)
- FOUND: commit 5c92fb3 (fix customer_note None)

---
*Phase: 06-public-order-form*
*Completed: 2026-08-02*
