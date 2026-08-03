---
phase: 06-public-order-form
verified: 2026-08-02T10:08:31Z
status: human_needed
score: 5/5 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Mở trang chi tiết sản phẩm còn hàng — kiểm tra block 'Thêm vào giỏ hàng' (input số lượng min=1 max=tồn kho + nút primary) hiển thị đúng, không còn nút 'Mua qua Messenger'; sản phẩm hết hàng hiện note đỏ, ngừng bán không hiện block nào"
    expected: "Add-to-cart form hiển thị đẹp (input 44px, nút full-width max 320px); Messenger CTA chỉ còn trên trang chủ/footer; out-of-stock note + discontinued badge như spec"
    why_human: "Render thực tế của CSS/typography (phông chữ, layout, spacing) không verify được bằng grep/test HTTP"
  - test: "Thêm 2-3 sản phẩm vào giỏ, mở /cart — kiểm tra bảng line-item (thumb + tên + đơn giá + số lượng + thành tiền), tổng tiền format đúng, nút Cập nhật/Xóa hoạt động, section 'Thông tin đặt hàng' nằm dưới bảng"
    expected: "Bảng giỏ hàng đúng spec (5 cột, caption ẩn, hover row); tổng tiền in đậm accent; responsive mobile bảng cuộn ngang không tràn"
    why_human: "Responsive 480/768/1200 + table scroll + visual spacing chỉ xác nhận được bằng trình duyệt thực"
  - test: "Kiểm tra nav header có link 'Giỏ hàng' + badge số món khi giỏ không trống; badge biến mất khi giỏ trống; ở mobile nav xếp chồng đúng"
    expected: "Badge pill accent trắng hiển thị số sản phẩm; link+badge touch target ≥44px; stacking mobile đúng spec"
    why_human: "Vị trí badge trong nav, kích thước touch target, hành vi responsive cần xác nhận mắt thường"
  - test: "Trên /cart điền form đặt hàng (tên/SĐT/địa chỉ/ghi chú) — kiểm tra required asterisk, help-text SĐT, placeholder ghi chú, nút 'Đặt hàng'; điền SĐT sai 7 chữ số xem lỗi"
    expected: "Form 4 field đúng nhãn tiếng Việt + honeypot ẩn hoàn toàn (không focus được); nút primary full-width max 320px; lỗi SĐT hiển thị thông báo tiếng Việt"
    why_human: "Hiển thị field-error, honeypot ẩn bằng display:none, layout form cần trình duyệt thực để xác nhận"
  - test: "Đặt hàng thành công — kiểm tra flash xanh 'Đặt hàng thành công! Chúng tôi sẽ liên hệ xác nhận qua SĐT.' xuất hiện trên trang chi tiết, giỏ đã trống"
    expected: "Flash success màu #059669 hiển thị trong flash-zone, redirect về trang chi tiết sản phẩm đầu tiên, badge giỏ biến mất"
    why_human: "Màu flash, vị trí flash-zone, redirect visual cần xác nhận mắt thường"
---

# Phase 6: Cart + Checkout (Public Order Form) Verification Report

**Phase Goal:** Giỏ hàng nhiều sản phẩm (lưu session) + checkout tạo đơn nhiều sản phẩm (Order + OrderItem) thay form đặt hàng 1 sản phẩm; bỏ nút "Mua qua Messenger" trên trang chi tiết, giữ dải liên hệ Messenger
**Verified:** 2026-08-02T10:08:31Z
**Status:** human_needed (all 5 success criteria VERIFIED programmatically; 5 non-blocking visual UAT items require human confirmation)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | **SC1** Order model refactored: `orders` giữ khách + status; `order_items` snapshot từng SP + FK `order_id`; migration idempotent không mất dữ liệu | ✓ VERIFIED | `app/models.py:73-101` (Order 8 cột customer+status; OrderItem snapshot + FK CASCADE/SET NULL + CheckConstraint quantity>=1); `app/db.py:43-54` (PRAGMA table_info(orders) guard, DROP only when 0 rows, ClickException on legacy data); live test: orders cols customer-only, order_items snapshot cols present, init-db ×2 idempotent, legacy-with-data → ClickException + data preserved, legacy-empty → DROP + rebuild |
| 2 | **SC2** Trang chi tiết có "Thêm vào giỏ hàng" (1 ≤ qty ≤ tồn kho); bỏ "Mua qua Messenger" trên detail; giữ dải Messenger nơi khác | ✓ VERIFIED | `product_detail.html:34-48` (status-gated add-to-cart form: qty min=1 max=stock, POST cart_add có CSRF); grep: "Mua qua Messenger" chỉ còn ở `index.html:28` (contact-strip); `_nav.html:9-15` (Giỏ hàng + badge); test: detail has add-to-cart max="5", NO Messenger, out-of-stock note, discontinued neither, home strip kept |
| 3 | **SC3** Trang giỏ hàng liệt kê SP, sửa số lượng/xóa, hiện tổng tiền; hidden khi hết hàng/ngừng bán | ✓ VERIFIED | `app/public.py:111-167` (cart route lọc stale + clamp qty MD-02; cart_update no-upsert MD-01; cart_remove); `cart.html` (5-cột table, total format_price, empty state); test: list/line-total/grand-total/update/remove/out-of-stock-hidden/empty-state all pass |
| 4 | **SC4** Checkout bắt buộc tên/SĐT/địa chỉ; tạo 1 Order + nhiều OrderItem snapshot; CSRF + honeypot | ✓ VERIFIED | `app/forms.py:32-44` (CheckoutForm DataRequired name/phone/address, validate_customer_phone 8-11 digits); `app/public.py:171-233` (checkout 6 bước: honeypot→empty→validate→re-validate từng món→1 Order + N OrderItem 1 commit→xóa giỏ+flash+redirect); test: e2e tạo 1 order/2 items snapshot đúng, tamper qty>stock/ngừng bán/hết hàng reject (0 order), CSRF thiếu token→400, honeypot silent reject |
| 5 | **SC5** Khách thấy thông báo thành công; tồn kho KHÔNG giảm (ORD-12 deferred v2) | ✓ VERIFIED | `app/public.py:230-233` (xóa giỏ + flash success 'Đặt hàng thành công!…', không giảm product.quantity); test: p1/p2 quantity vẫn 5/3 sau đặt; success flash xuất hiện trên trang chi tiết sau redirect |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `app/models.py` | Order (customer+status) + OrderItem (snapshot, FK CASCADE/SET NULL, CheckConstraint) | ✓ VERIFIED | `models.py:73-101`; live schema inspect confirmed |
| `app/db.py` | init-db idempotent orders guard + tạo order_items | ✓ VERIFIED | `db.py:43-57`; idempotency + legacy data-preservation tested live |
| `app/forms.py` | CartForm + CheckoutForm (name/phone/address required, honeypot) | ✓ VERIFIED | `forms.py:13-14, 32-44`; phone digit-count validation tested |
| `app/public.py` | cart_add / cart / cart_update / cart_remove / checkout routes | ✓ VERIFIED | `public.py:88-233`; all routes exercised by test |
| `app/templates/public/cart.html` | Cart page (table + total + checkout include + empty state) | ✓ VERIFIED | Rendered and content-verified (names, totals, update/remove forms, empty state) |
| `app/templates/public/product_detail.html` | Add-to-cart block replacing Messenger CTA | ✓ VERIFIED | Status-gated form; no Messenger string |
| `app/templates/public/_nav.html` | Cart link + badge | ✓ VERIFIED | Badge count = len(session['cart']), hidden when empty |
| `app/templates/public/_checkout_form.html` | Checkout partial (CSRF + honeypot + 4 fields) | ✓ VERIFIED | Rendered in non-empty cart (honeypot name=website + 4 fields + csrf) |
| `app/static/css/style.css` | Phase 6 cart/checkout CSS | ✓ VERIFIED | `.cart-link`, `.cart-badge`, `.honeypot`, `.cart-total`, `.cart-cta`, `button.link-danger` present; no `.messenger-cta` |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| detail add-to-cart form | `cart_add` route → session cart | POST + CSRF token | ✓ WIRED | Live: add qty 2 → session cart `{'1':2}` |
| `cart_update` form | session cart | POST + server validate qty | ✓ WIRED | Live: update qty works; product-not-in-cart not upserted (MD-01) |
| `cart_remove` form | session cart | POST | ✓ WIRED | Live: item removed |
| checkout form | `checkout` route → Order + OrderItem | POST + CSRF + honeypot | ✓ WIRED | Live: 1 Order + 2 OrderItems snapshot in 1 commit |
| `OrderItem.order_id` | `orders.id` | FK ondelete='CASCADE' + ORM cascade | ✓ WIRED | Live: delete order → items CASCADE |
| `OrderItem.product_id` | `products.id` | FK ondelete='SET NULL' nullable + passive_deletes | ✓ WIRED | Live: delete product → product_id NULL, snapshot preserved |
| nav badge | session cart | `len(session['cart'])` | ✓ WIRED | Template `_nav.html:10-13` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| cart.html items/total | `items` / `total` | session cart → Product DB query (fresh price/stock/status) | Yes | ✓ FLOWING |
| Order creation | `Order` / `OrderItem` | CheckoutForm input + current Product snapshot | Yes (real DB rows, verified) | ✓ FLOWING |
| nav badge | `cart_count` | session cart length | Yes | ✓ FLOWING |
| cart page stale cleanup | flash info | unavailable product filtered at render | Yes (verified out-of-stock hidden) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| E2E add→cart→checkout → 1 Order + 2 OrderItems snapshot | temp DB test client | 1 order, 2 items, snapshot correct, stock unchanged | ✓ PASS |
| qty tamper (99>stock) / ngừng bán / hết hàng checkout | direct POST no GET /cart | 0 orders created | ✓ PASS |
| CSRF missing token → 400 | POST /cart/add, /cart/checkout | status 400 | ✓ PASS |
| CSRF-protected happy path (real tokens) | token from rendered form → add + checkout | order created | ✓ PASS |
| Honeypot `website` filled | POST checkout | silent reject, 0 orders, cart unchanged | ✓ PASS |
| Phone 7/11 digits | checkout POST | 7→reject, 11→accept | ✓ PASS |
| Migration idempotent | init-db ×2 on temp DB | both exit 0 | ✓ PASS |
| Migration legacy-with-data | init-db on legacy DB | ClickException 'Manual migration required', data preserved | ✓ PASS |
| Migration legacy-empty rebuild | init-db on legacy DB | DROP + recreate customer-only schema, product data preserved | ✓ PASS |
| Grep gate cost_price/Giá nhập in public templates | grep scan | 0 hits | ✓ PASS |
| No v1.0 regression | home/search/detail/admin | all 200, 404 for missing, admin redirects to login | ✓ PASS |
| Admin login + product CRUD | login + create product | login ok, product created | ✓ PASS |

### Probe Execution

Step 7c: SKIPPED — no probe scripts exist for this phase (`.planning/phases/06-public-order-form/` has no `probe-*.sh`; plans declare no probes). Verification used a purpose-built test harness on temp DBs.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| ORD-01 | 06-03 | Khách đặt hàng qua form (tên/SĐT/địa chỉ/số lượng/ghi chú) — thay Messenger CTA | ✓ SATISFIED | `_checkout_form.html` on cart page; detail no longer has Messenger CTA. Note: form lives on the cart page (single-page cart+checkout, UI-SPEC decision), detail page provides add-to-cart — satisfies ORD-01's intent |
| ORD-02 | 06-03 | Form bắt buộc tên/SĐT/địa chỉ; qty ≥1 ≤ tồn kho | ✓ SATISFIED | `forms.py:33-35` DataRequired; `public.py:197` re-validate `1 <= qty <= product.quantity` |
| ORD-03 | 06-02, 06-03 | Thông báo thành công; form không hiện khi hết hàng/ngừng bán | ✓ SATISFIED | flash success + status-gated add-to-cart block; tested |
| ORD-05 | 06-03 | CSRF + chống spam | ✓ SATISFIED | CSRFProtect app-wide → 400; honeypot silent reject; tested |
| ORD-10 | 06-02 | Giỏ hàng nhiều SP (session) — thêm/sửa/xóa/tổng tiền | ✓ SATISFIED | 4 cart routes + cart.html; tested |
| ORD-10a | 06-01, 06-03 | Checkout tạo 1 đơn nhiều SP (Order + OrderItem snapshot) | ✓ SATISFIED | models refactor + checkout single commit; tested |
| ORD-10b | 06-02 | Detail có "Thêm vào giỏ hàng"; bỏ form 1 SP; giữ dải Messenger | ✓ SATISFIED | detail add-to-cart; Messenger only in index.html contact-strip; tested |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | No TBD/FIXME/XXX/HACK markers in any Phase 6 file | 🛑 none | — |
| — | — | No stub (empty return, hardcoded empty data, console.log-only) in Phase 6 code | ⚠️ none | — |

Documented, non-blocking acceptances (from 06-REVIEW / 06-REVIEW-FIX, all with recorded decisions):
- **LW-01** form reset on checkout validation fail → redirect /cart loses user input. Accepted per UI-SPEC (flash summary only); not fixed by design. Non-blocking UX note.
- **LW-03** honeypot `display:none` may be ignored by some bots. Accepted per UI-SPEC ("never focusable"). Non-blocking defense-depth note.
- **LW-04** GET /cart mutates session (stale cleanup). Accepted per spec (self-cleaning cart). Non-blocking.
- **LW-06** flash "Đã thêm {qty}" wording on qty replace. Cosmetic; not fixed.
- **IN-01** phone regexp `\d` matches Unicode digits / `\s` includes newline. Data-quality only; not a security issue.
- **IN-02** `product_cost_price` snapshot stored on OrderItem. Phase 7 must keep it behind `@login_required`; verified 0 public renders in Phase 6.

### Human Verification Required

All 5 automated success-criteria checks pass. The following are non-blocking visual checks requiring a browser (see frontmatter for full detail):

1. **Detail page add-to-cart block** — visual rendering of qty input + button; out-of-stock note; discontinued badge; no Messenger CTA.
2. **Cart page layout + responsive** — 5-column table, total, update/remove, checkout section below; mobile scroll at 480/768/1200.
3. **Nav cart-link badge** — badge shows item count, hidden when empty, ≥44px touch target, mobile stacking.
4. **Checkout form visual** — 4 fields + required asterisks + phone help-text + hidden honeypot + submit button.
5. **Success flash** — green success message renders in flash-zone after order.

### Gaps Summary

**No blocking gaps.** All 5 success criteria verified programmatically (72/72 harness checks + CSRF-protected happy path + honeypot render + admin regression). 7/7 Phase 6 requirements satisfied. No v1.0 regression (home/search/detail/admin tested). Grep gate `cost_price`/`Giá nhập` in `app/templates/public/` = 0 hits.

**Deployment note (not a phase gap):** real `data/app.db` is still v1.0 (no `cost_price`, no `orders`/`order_items`). Migration is a deferred operator action — run `flask --app app init-db` after Phase 6 with valid `ADMIN_PASSWORD`. Migration verified idempotent and data-preserving on temp DBs.

---

_Verified: 2026-08-02T10:08:31Z_
_Verifier: Claude (gsd-verifier)_
