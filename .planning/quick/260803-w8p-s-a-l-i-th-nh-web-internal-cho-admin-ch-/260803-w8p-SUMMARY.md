---
quick_id: 260803-w8p
status: complete
---

# Summary — Quick Task 260803-w8p

## Chuyển StoreWeb thành web internal quản lí hàng

### Trạng thái
- [x] Task 1: Đổi nhãn "Cửa hàng" → "Quản lý hàng" trong toàn bộ templates
- [x] Task 2: Root `/` redirect tới admin login + reframe contact strip

### Task 1 — Đổi nhãn (9 template files)
Commit: `8879a20` feat(quick-260803-w8p): rename 'Cửa hàng' → 'Quản lý hàng' in all templates
- `app/templates/public/_nav.html`: brand link "Cửa hàng" → "Quản lý hàng"
- `app/templates/public/base.html`: title "Cửa hàng" → "Quản lý hàng"; footer "© {{ current_year }} Cửa hàng" → "© {{ current_year }} Quản lý hàng"
- `app/templates/public/index.html`: title "Sản phẩm — Cửa hàng" → "Sản phẩm — Quản lý hàng"; empty-state "Cửa hàng đang cập nhật..." → "Quản lý hàng đang cập nhật..."
- `app/templates/public/search.html`: title "Tìm kiếm — Cửa hàng" → "Tìm kiếm — Quản lý hàng"
- `app/templates/public/product_detail.html`: title "… — Cửa hàng" → "… — Quản lý hàng"
- `app/templates/public/cart.html`: title "Giỏ hàng — Cửa hàng" → "Giỏ hàng — Quản lý hàng"
- `app/templates/_checkout_form.html`, `errors/404.html`, `errors/500.html`: scan xác nhận không chứa "Cửa hàng"
- **Grep gate:** 0 kết quả "Cửa hàng" trong `app/templates/`

### Task 2 — Root redirect + reframe contact strip
Commit: `e982481` feat(quick-260803-w8p): root redirect to admin login + reframe contact strip

**`app/public.py`:**
- Thêm import: `from flask_login import current_user`
- `home()`: kiểm tra `current_user.is_authenticated`; nếu chưa đăng nhập → `redirect(url_for('auth.login'))`. Nếu đăng nhập → render danh sách sản phẩm bình thường.
- Quy trình mới: khách hàng gửi đơn qua Messenger (bên ngoài web); admin đăng nhập vào web internal để quản lí/đặt hàng.

**`app/templates/public/index.html`:**
- Contact strip heading: "Liên hệ mua hàng" → "Nhận đơn qua Messenger"
- Button: "Mua qua Messenger" → "Mở Messenger để nhận đơn" (href vẫn `{{ config['MESSENGER_URL'] }}`)

### Verification
1. `grep -rn "Cửa hàng" app/templates/` → 0 match ✓
2. `grep -n "current_user" app/public.py` → import + dùng trong `home()` ✓
3. `grep -n "auth.login" app/public.py` → redirect khi unauthenticated ✓
4. `grep -n "Mở Messenger\|Nhận đơn qua Messenger" index.html` → cập nhật ✓
5. Test client: `GET /` → 302 redirect tới `/login` ✓

### Notes
- Task 2 được thực hiện trực tiếp (inline) do provider OPENCODE gặp lỗi rate-limit (HTTP 429) trên agent executor; các lần retry đều fail. Work được thực hiện đúng plan, commit nguyên tử, verify đầy đủ.
- Không phải cửa hàng công khai nữa — toàn bộ giao diện và luồng truy cập chuyển thành công cụ internal cho admin.
