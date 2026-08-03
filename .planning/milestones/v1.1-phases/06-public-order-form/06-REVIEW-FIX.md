---
phase: 06-public-order-form
fixed_at: 2026-08-02
review_path: .planning/phases/06-public-order-form/06-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 6: Code Review Fix Report

**Fixed at:** 2026-08-02
**Source review:** `.planning/phases/06-public-order-form/06-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 4 (2 MEDIUM + 2 LOW)
- Fixed: 4
- Skipped: 0

Scope theo hướng dẫn: MD-01, MD-02, LW-02, LW-05. Không sửa LW-01 (UX form reset — decision đã chốt), LW-03 (honeypot display:none — theo spec), LW-04 (GET mutate session — theo spec cart tự dọn stale), LW-06 (cosmetic), và các INFO.

## Fixed Issues

### MD-01: `cart_update` không upsert sản phẩm chưa có trong giỏ

**Files modified:** `app/public.py`
**Commit:** `00d6ee4`
**Applied fix:** Thêm guard `if str(product_id) not in cart:` trước khi ghi `cart[str(product_id)] = qty`. Nếu sản phẩm chưa có trong giỏ → flash error "Sản phẩm không có trong giỏ hàng." + redirect về `/cart`. Không thêm món mới qua route "update"; hành vi `cart_add` giữ nguyên.

### MD-02: Clamp qty xuống tồn kho hiện tại khi render cart

**Files modified:** `app/public.py`
**Commit:** `c03f232`
**Applied fix:** Trong `cart()` khi build items, clamp `qty = min(int(qty), product.quantity)` khi stock giảm sau khi add; **persist** qty đã clamp vào `session['cart']` để session khớp với đơn đặt được (không còn tổng tiền hiển thị mà checkout reject). `total += product.price * qty` dùng qty đã clamp. Template `cart.html` render `value`/`max` và "Thành tiền" từ qty đã clamp — không cần sửa template.

### LW-02: Guard `items_to_save` rỗng trước khi lấy `[0]`

**Files modified:** `app/public.py`
**Commit:** `8cbf5a7`
**Applied fix:** Sau vòng lặp re-validate, thêm guard `if not items_to_save:` → flash "Giỏ hàng của bạn đang trống." + redirect về `/cart`. Tránh `IndexError` 500 khi giỏ chỉ chứa key không phải số.

### LW-05: Bỏ `ignore missing` khỏi include `_checkout_form.html`

**Files modified:** `app/templates/public/cart.html`
**Commit:** `f1d122b`
**Applied fix:** `{% include "public/_checkout_form.html" %}` (bỏ `ignore missing`). File partial đã tồn tại; nếu sau này file mất sẽ fail loud thay vì form đặt hàng biến mất im lặng.

## Skipped Issues

Không có finding nào bị skip — cả 4 finding trong scope đều fixed.

## Smoke Test (temp DB, CSRF off, patch BASE_DIR)

Không đụng `data/app.db` thật (engine swap sang temp dir). `SECRET_KEY` set qua env, `WTF_CSRF_ENABLED=False`.

**18/18 checks pass** (main smoke test):
- A1-A2: `cart_add` ghi cart đúng (no regression)
- B1-B3: `cart_update` với product chưa có trong giỏ → không thêm (MD-01)
- C1-C2: `cart_update` với món đã có → cập nhật bình thường (no regression)
- D1-D5: clamp qty khi stock giảm 3→1; session qty=1; input `max="1" value="1"`; total 50.000₫ (MD-02); partial checkout form được render (LW-05)
- E1-E4: checkout happy path → tạo 1 order, 1 item qty=1, giỏ rỗng (no regression)
- F1-F2: checkout với giỏ chỉ chứa key không phải số → redirect, không 500, không tạo order (LW-02)

**4/4 checks pass** (06-02/06-03 regression):
- T1: tamper qty 99 > stock 5 → reject, không ghi (06-03)
- T2: checkout với qty hợp lệ → tạo order (06-03)
- T3: honeypot `website` điền → silent reject, không tạo order (06-02)
- T4: honeypot → giỏ không đổi (06-02)

**Kết luận:** 4 fix hoạt động đúng, không regress case chính 06-02/06-03.

---

_Fixed: 2026-08-02_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
