# Phase 6: Cart + Checkout (Public Order Form) - Context

**Gathered:** 2026-08-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Giỏ hàng nhiều sản phẩm (session-based) + checkout tạo đơn nhiều sản phẩm. Refactor `Order` → `Order` + `OrderItem` (ORD-10a) — thay thế form đặt hàng 1 sản phẩm và nút "Mua qua Messenger" trên trang chi tiết. Dải liên hệ Messenger giữ nguyên ở trang chủ/footer. Covers ORD-01, ORD-02, ORD-03, ORD-05, ORD-10, ORD-10a, ORD-10b.

**Scope change note:** User chốt cart đầy đủ 2026-08-02 (đảo ngược decision cũ "mỗi đơn = 1 sản phẩm"). ORD-10 từ v2 deferred chuyển active v1.1. `data/app.db` thật CHƯA migrate (Phase 5 chỉ test trên temp copy) → refactor schema trước go-live an toàn, không mất dữ liệu.

</domain>

<decisions>
## Implementation Decisions

### Order + OrderItem Refactor (ORD-10a)
- `orders`: id, customer_name, customer_phone, customer_address, customer_note, status (String VN, default 'Chờ xác nhận'), created_at, updated_at — KHÔNG còn snapshot fields trực tiếp
- `order_items`: id, order_id (FK `orders.id`, ondelete='CASCADE'), product_id (FK nullable, ondelete='SET NULL'), product_name/product_price/product_cost_price (snapshot tại thời điểm đặt, Integer VND D-05), quantity (Integer ≥ 1), created_at
- Migration idempotent: guard `PRAGMA table_info(orders)` — orders bảng cũ (nếu có) cần xử lý cột thừa + tạo `order_items` qua create_all; không mất dữ liệu (thực tế orders chưa có data live)
- OrderItem có CheckConstraint `quantity >= 1` (IN-03 Phase 5 review — rẻ khi bảng mới)

### Cart (ORD-10)
- Session-based: giỏ lưu trong Flask `session` dạng `{product_id: quantity}`, không cần bảng DB (khách ẩn danh, không tài khoản — giữ scope)
- Thêm/sửa số lượng/xóa món; hiện tổng tiền (sum price × qty); giỏ trống → trang giỏ hàng trống có CTA về trang chủ
- Server-side validate lại mọi thứ ở checkout (số lượng ≤ tồn kho, sản phẩm còn tồn, không ngừng bán) — không tin client

### Detail Page (ORD-10b)
- Thay nút "Mua qua Messenger" bằng block "Thêm vào giỏ hàng": số lượng (1 ≤ qty ≤ tồn kho) + nút thêm
- Ẩn block khi sản phẩm hết hàng/ngừng bán (hiện note "Sản phẩm hiện đang hết hàng." như hiện tại)
- Nút/badge "Xem giỏ" hiển thị số món đang có (dễ thấy, có thể đặt trong nav)

### Checkout + Validation (ORD-01/02/03/05)
- Form: Tên (bắt buộc), SĐT (bắt buộc), Địa chỉ (bắt buộc), Ghi chú (tùy chọn)
- SĐT: bắt buộc, chỉ chữ số (cho phép space/`-`/`+` prefix), dài 8-11 chữ số — không chặt format VN chuẩn (user chốt)
- Quantity: server-side validate ≥ 1 và ≤ tồn kho (cả khi tamper)
- CSRF: Flask-WTF (sẵn toàn app) + honeypot field ẩn "website" — bot điền bị reject im lặng (không flash, không lưu)
- Success: redirect về trang chi tiết (hoặc trang xác nhận) kèm flash xanh "Đặt hàng thành công! Chúng tôi sẽ liên hệ xác nhận qua SĐT."; xóa giỏ sau khi đặt thành công
- Không giảm tồn kho khi đặt (ORD-12 → v2)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/templates/base.html` — flash-zone sẵn (get_flashed_messages) dùng cho success message
- `app/forms.py` — FlaskForm pattern; WTForms validators: DataRequired, InputRequired, Optional, Length, NumberRange
- `app/public.py` — public_bp; `product_detail(product_id)` GET route; home/search có sẵn
- `app/models.py` — Order model (Phase 5) cần refactor; Product có price/cost_price/quantity/status
- CSRFProtect bật toàn app (`app/__init__.py`)
- `_set_sqlite_pragma` đã bật `PRAGMA foreign_keys=ON` (fix Phase 5) → FK SET NULL/CASCADE hoạt động

### Established Patterns
- Flask-WTF forms validators tiếng Việt (`message='...'`)
- SQLAlchemy ORM, `db.session.add/commit`
- Flash messages với categories (success/error/warning) render trong base.html
- Status qua `product.status` property (available/out_of_stock/discontinued)
- Session usage: Flask session (login/CSRF) — có thể dùng cho cart

### Integration Points
- `app/public.py` — thêm routes: add-to-cart POST, cart page GET, checkout GET/POST
- `app/forms.py` — thêm CartForm (quantity) + CheckoutForm (name/phone/address/note)
- `app/templates/public/product_detail.html` — thay CTA bằng add-to-cart block
- `app/templates/public/` — thêm `cart.html` (giỏ + checkout hoặc tách riêng)
- `app/models.py` — refactor Order + thêm OrderItem
- `app/db.py` — migration: guard orders + create order_items

</code_context>

<specifics>
## Specific Ideas

- Tổng tiền hiển thị format_price (sẵn có)
- Giỏ hiển thị từng món: ảnh thumb + tên + đơn giá + số lượng + thành tiền
- Checkout form có thể nằm ngay trên trang giỏ hàng (1 trang) hoặc trang riêng — để planner chọn, nghiêng về 1 trang giỏ + checkout liền
- Snapshot price/cost_price lấy từ product tại thời điểm thêm vào giỏ hay tại checkout? → Tại checkout (thời điểm đặt, ORD-04) — nhưng cost/price có thể thay đổi giữa add & checkout; quyết định: snapshot tại checkout từ product hiện tại

</specifics>

<deferred>
## Deferred Ideas

- Thông báo đơn mới cho admin (ORD-11 → v2)
- Tự động trừ tồn kho khi xác nhận (ORD-12 → v2)
- SMS/email xác nhận cho khách — ngoài scope, admin liên hệ qua SĐT
- Lưu giỏ DB cho khách đăng nhập — không có tài khoản khách, session đủ
</deferred>
