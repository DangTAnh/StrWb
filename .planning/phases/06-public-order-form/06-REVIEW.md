---
phase: 06-public-order-form
reviewed: 2026-08-02
depth: standard
files_reviewed: 9
files_reviewed_list:
  - app/models.py
  - app/db.py
  - app/forms.py
  - app/public.py
  - app/templates/public/product_detail.html
  - app/templates/public/_nav.html
  - app/templates/public/cart.html
  - app/templates/public/_checkout_form.html
  - app/static/css/style.css
findings:
  high: 0
  medium: 2
  low: 6
  info: 3
  total: 11
status: issues_found
---

# Phase 6: Code Review Report (Cart + Checkout)

**Reviewed:** 2026-08-02
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Đã review toàn bộ Phase 6 (session cart + checkout) ở mức standard, đọc 3 SUMMARY + CONTEXT + UI-SPEC trước, sau đó đọc từng file code và chạy smoke test thực tế trên temp DB (CSRF, honeypot, tamper qty, deleted-product, atomic order, SET NULL/CASCADE, migration legacy).

**Tổng thể: implementation chắc chắn về security.** Các điểm security chính đều được verify bằng test thực tế:
- **CSRF**: CSRFProtect app-wide, mọi POST thiếu token → 400 (verified).
- **Honeypot 'website'**: silent reject — không flash, không tạo đơn, giỏ không đổi (verified: orders vẫn 0).
- **SĐT validation**: 8–11 chữ số, cho phép space/`-`/`+` prefix; 10/10 test case pass.
- **Quantity tamper**: server re-validate `1 <= qty <= product.quantity` + status `available` ở cả add/update/checkout (verified: qty 99 > stock 5 bị reject; checkout với product bị xóa → không tạo đơn).
- **Không lộ `cost_price`/`Giá nhập`**: grep gate 0 hits trong `app/templates/public/`; route chỉ GHI snapshot vào OrderItem, không render public.
- **XSS**: user data (name/address/note) và flash message render qua Jinja2 autoescape (mặc định).
- **FK**: delete product → `order_items.product_id` SET NULL giữ snapshot (verified); delete order → CASCADE xóa items (verified).
- **Atomic**: 1 Order + nhiều OrderItem trong 1 `commit()` (verified: 1 order / 2 items).
- **Migration**: legacy orders rỗng → DROP + recreate OK; legacy orders có data → guard raise, data giữ nguyên (verified).

Không tìm thấy HIGH. Các finding tập trung vào 2 lỗi logic mức MEDIUM (cart_update upsert, cart page hiển thị qty/total quá tồn kho) và một số LOW/INFO về UX và phòng thủ.

---

## HIGH Issues

Không có finding HIGH. Vùng security (CSRF, honeypot, tamper, XSS, cost-price gate) đã được xác nhận hoạt động đúng bằng test.

---

## MEDIUM Issues

### MD-01: `cart_update` tự thêm sản phẩm KHÔNG có trong giỏ (upsert) — sai ngữ nghĩa route "update"

**File:** `app/public.py:146-148`

**Issue:** Route `cart_update` không kiểm tra sản phẩm đã tồn tại trong giỏ trước khi ghi `cart[str(product_id)] = qty`. Kết quả là POST tới `/cart/update/<id>` với một sản phẩm chưa có trong giỏ sẽ *thêm mới* sản phẩm đó (chỉ cần available + qty ≤ tồn kho — giống hệt `cart_add`). Khác với advisory plan-checker #2 (đã sửa để `cart_update` check status cho nhất quán với `cart_add`), nhưng check "đã trong giỏ chưa" thì chưa có.

**Failure scenario:** Người dùng mở 2 tab: tab A xóa sản phẩm X khỏi giỏ; tab B vẫn còn form "Cập nhật" của X (render trước khi xóa) → bấm Cập nhật → X bị thêm lại vào giỏ mà người dùng không mong muốn. Ngoài ra, một request được craft (kèm CSRF token hợp lệ của chính session) có thể nhồi bất kỳ sản phẩm available nào vào giỏ qua route update.

**Fix:**
```python
cart = session.get('cart', {})
if str(product_id) not in cart:
    # Không phải món trong giỏ — redirect về /cart, không thêm
    flash('Sản phẩm không có trong giỏ hàng.', 'error')
    return redirect(url_for('public.cart'))
cart[str(product_id)] = qty
```

---

### MD-02: Cart page hiển thị qty/total vượt tồn kho hiện tại — tổng tiền sai so với đơn có thể đặt

**File:** `app/public.py:127-128`, `app/templates/public/cart.html:34,38`

**Issue:** `cart()` chỉ lọc sản phẩm có `status != 'available'` (đã hết hẳn/ngừng bán), nhưng KHÔNG clamp `qty` xuống `product.quantity` khi tồn kho giảm sau khi thêm vào giỏ. Cart page render `value={{ item.quantity }}` và `total += product.price * qty` với qty cũ, dù `max="{{ item.product.quantity }}"` đã giảm.

**Failure scenario:** Khách thêm 3 sản phẩm (tồn kho 3). Admin giảm tồn kho còn 1. Khách mở /cart thấy "Số lượng: 3" và "Tổng cộng: 150.000₫" — nhưng khi bấm Đặt hàng thì checkout reject ("Một số sản phẩm không còn khả dụng"). Khách thấy tổng tiền không thể thanh toán. Ngoài ra, native constraint `max=1` trên input number chặn submit form "Cập nhật" trừ khi khách tự sửa số về ≤ 1 — thêm một bước bí hiểm.

**Fix:** Clamp qty khi render trong `cart()`:
```python
qty = min(int(qty), product.quantity)
items.append(SimpleNamespace(product=product, quantity=qty))
total += product.price * qty
```

---

## LOW Issues

### LW-01: Checkout validation fail làm mất toàn bộ input người dùng; field-error không được render

**File:** `app/public.py:177-179`, `app/templates/public/_checkout_form.html:1-24`

**Issue:** Khi `form.validate()` fail, route flash một message tổng hợp rồi `redirect` về `/cart` — form render lại trống, mất hết tên/SĐT/địa chỉ khách vừa nhập. `_checkout_form.html` cũng không render `{{ form.customer_name.errors }}` / `.field-error` theo UI-SPEC mục 4.

**Failure scenario:** Khách nhập đủ field nhưng SĐT sai (7 chữ số) → bấm Đặt hàng → redirect /cart, mất hết dữ liệu đã gõ, phải nhập lại từ đầu.

**Ghi chú:** Đây là quyết định đã ghi nhận trong SUMMARY 06-03 (advisory plan-checker về UX form reset — chấp nhận theo spec). Vẫn nên cân nhắc sửa vì ảnh hưởng trực tiếp tỉ lệ hoàn tất đơn.

**Fix:** Thay redirect bằng render lại trang giỏ kèm form đã giữ input (hoặc truyền `form` vào template, render lỗi field-level trong partial).

---

### LW-02: `items_to_save[0]` có thể IndexError 500 nếu giỏ chỉ chứa key không phải số

**File:** `app/public.py:219`

**Issue:** Vòng lặp checkout `continue` (bỏ qua) các key không phải số (dòng 186), nhưng cuối route truy cập thẳng `items_to_save[0][0].id`. Nếu toàn bộ key trong giỏ đều không phải số → `items_to_save` rỗng → `IndexError` → 500. Không thể reach qua luồng app bình thường (mọi route chỉ ghi key `str(product_id)` là chuỗi số), nhưng đây là lỗ hổng phòng thủ: code đã cố xử lý key lạ nhưng không hoàn tất.

**Fix:** Sau vòng lặp, thêm guard:
```python
if not items_to_save:
    flash('Giỏ hàng của bạn đang trống.', 'error')
    return redirect(url_for('public.cart'))
```

---

### LW-03: Honeypot `display:none` — nhiều bot spam bỏ qua field ẩn kiểu này

**File:** `app/templates/public/_checkout_form.html:3`, `app/static/css/style.css:445`

**Issue:** Honeypot dùng `display: none`. Nhiều spam bot có heuristic "bỏ qua field ẩn bằng display:none", nên sẽ không bao giờ điền `website` → honeypot không bắt được. Kỹ thuật hiệu quả hơn là off-screen (`position:absolute; left:-9999px`) — bot vẫn thấy field và điền, người dùng không thấy.

**Ghi chú:** Đây là lựa chọn có chủ đích trong UI-SPEC ("true display:none so it is never focusable"). Không phải bug, nhưng giảm hiệu quả trap.

---

### LW-04: `cart()` (GET) có side-effect thay đổi session

**File:** `app/public.py:111-130`

**Issue:** Route GET `/cart` pop các món stale và ghi `session['cart'] = cart`. GET được coi là an toàn/idempotent; việc mutate session trong GET vi phạm tinh thần đó và có thể gây nhầm lẫn khi debug/log (một request GET làm thay đổi trạng thái người dùng). Hành vi cleanup là đúng và cần thiết, nhưng nên chuyển thành POST hoặc tách cleanup riêng nếu muốn nghiêm ngặt.

---

### LW-05: `{% include "public/_checkout_form.html" ignore missing %}` giờ đã có file — nên bỏ `ignore missing`

**File:** `app/templates/public/cart.html:60`

**Issue:** `ignore missing` từng cần thiết khi 06-02 ship trước 06-03. Nay file đã tồn tại. Nếu sau này file bị đổi tên/xóa, `ignore missing` khiến form đặt hàng biến mất im lặng (nút "Đặt hàng" scroll xuống section trống) thay vì fail rõ ràng.

**Fix:**
```jinja
{% include "public/_checkout_form.html" %}
```

---

### LW-06: Flash "Đã thêm {qty} sản phẩm vào giỏ" có thể gây hiểu nhầm khi thay thế qty cũ

**File:** `app/public.py:107`

**Issue:** Cart dùng cơ chế replace-not-increment (đúng UI-SPEC). Nhưng flash dùng `qty` = số lượng MỚI trong giỏ, không phải số lượng vừa thêm. Nếu giỏ đang có 1, khách thêm 2 → cart thành 2, flash "Đã thêm 2 sản phẩm vào giỏ" (thực tế chỉ +1 net).

**Fix:** Dùng qty chênh lệch hoặc đổi lời: `Đã cập nhật giỏ hàng: {qty} sản phẩm.`

---

## INFO Issues

### IN-01: Regexp SĐT chấp nhận chữ số Unicode và `\s` bao gồm newline

**File:** `app/forms.py:34,40-44`

**Issue:** `\d` trong Python regexp khớp cả chữ số Unicode (ví dụ ٠١٢٣٤٥٦٧٨), và `[\d\s-]` cho phép `\n`/`\r`. Một SĐT như `0912\n345678` hoặc bằng chữ số Ả-Rập vượt qua validation; giá trị lưu là chuỗi raw (chỉ `.strip()`). Khi admin gọi lại sẽ khó/dial sai. Không phải lỗi bảo mật, chỉ data-quality. Nếu muốn chặt: giới hạn `[0-9\s-]` và thay `.isdigit()` bằng đếm `[0-9]`.

### IN-02: OrderItem snapshot chứa `product_cost_price` — dữ liệu nhạy cảm về giá vốn

**File:** `app/models.py:97`, `app/public.py:210`

**Issue:** Giá vốn được snapshot vào OrderItem (đúng thiết kế ORD-10a). Đã verify Phase 6 không render `cost_price` ở public (grep 0 hits). Lưu ý cho Phase 7: trang admin xem đơn phải giữ `cost_price` trong vùng `@login_required`, không được lộ ra public templates.

### IN-03: Oversell risk — tồn kho không giảm khi đặt (ORD-12 deferred v2)

**File:** `app/public.py:217`

**Issue:** Checkout không trừ `product.quantity`, nên 2 khách có thể đặt cùng lúc sản phẩm cuối cùng (cùng 1 tồn kho 1). Đây là quyết định deferred theo ORD-12 → v2. Ghi nhận rủi ro: với đơn hàng chờ admin xác nhận qua SĐT, oversell chỉ gây khó chịu (admin từ chối đơn), không phải lỗi tiền. Cân nhắc trừ tồn kho ở Phase 7 khi admin xác nhận đơn.

---

## Phương pháp xác minh (đã chạy)

Smoke test trên temp SQLite (engine swap, không đụng `data/app.db` thật — đã cleanup bảng test tạo nhầm):
- CSRF: POST thiếu token → 400
- Honeypot: không tạo order, giỏ nguyên
- Tamper: qty 99 > stock 5 reject; discontinued/out-of-stock reject
- Atomic: 1 order + 2 items trong 1 commit
- SET NULL: xóa product → order_items.product_id = NULL, snapshot giữ nguyên
- CASCADE: xóa order → items bị xóa
- Deleted-product checkout: re-validation reject, không tạo order
- Migration legacy rỗng: DROP + recreate OK; legacy có data: guard raise, data giữ nguyên

---

_Reviewed: 2026-08-02_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
