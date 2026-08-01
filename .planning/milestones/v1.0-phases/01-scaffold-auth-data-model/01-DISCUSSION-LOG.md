# Phase 1: Scaffold + Auth + Data Model - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-31
**Phase:** 1-Scaffold + Auth + Data Model
**Areas discussed:** Tài khoản admin, Model Product, Phiên đăng nhập, Trang Phase 1

---

## Tài khoản admin

| Option | Description | Selected |
|--------|-------------|----------|
| CLI hỏi tương tác | CLI hỏi nhập username + password, không lộ ra lịch sử lệnh | |
| Từ biến .env | Đọc ADMIN_USERNAME / ADMIN_PASSWORD từ .env | ✓ |
| Tham số lệnh | `flask init-db --username X --password Y` | |

**User's choice:** Từ biến .env
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Sửa .env + chạy lại init-db | init-db đồng bộ hash từ .env vào DB | ✓ |
| Lệnh CLI riêng | `flask change-password` hỏi mật khẩu mới trực tiếp | |
| Để sau, qua trang admin | Trang đổi mật khẩu trong admin (Phase 2) | |

**User's choice:** Sửa .env + chạy lại init-db
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Tối thiểu 8 ký tự | init-db từ chối nếu ngắn hơn | ✓ |
| 8 ký tự + chữ/số | Thêm ràng buộc chữ và số | |
| Không kiểm tra | Admin tự chịu trách nhiệm | |

**User's choice:** Tối thiểu 8 ký tự
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Chặn placeholder change-me | .env mẫu chứa ADMIN_PASSWORD=change-me, init-db từ chối | ✓ |
| Báo lỗi khi thiếu biến | Thiếu biến thì init-db báo lỗi | |
| Không kiểm tra | Chấp nhận mọi giá trị | |

**User's choice:** Chặn placeholder change-me
**Notes:** —

---

## Model Product

| Option | Description | Selected |
|--------|-------------|----------|
| Mã sản phẩm (SKU) | Mã riêng từng sản phẩm để tra cứu nhanh | ✓ |
| Thứ tự hiển thị | Số sắp xếp ghim sản phẩm nổi bật lên đầu | ✓ |
| Ghi chú nội bộ | Chỉ admin xem, không hiện công khai | ✓ |

**User's choice:** Thêm cả 3 trường phụ (SKU, thứ tự hiển thị, ghi chú nội bộ)
**Notes:** Multi-select — user chọn tất cả 3.

| Option | Description | Selected |
|--------|-------------|----------|
| Ô văn bản tự do | Nhập tự do "60×40×2cm" hay "M / L / XL" | ✓ |
| Trường số tách riêng | Dài × Rộng × Cao (cm) | |
| Cả hai | Ô văn bản tự do + vài ô số riêng | |

**User's choice:** Ô văn bản tự do
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Tự suy từ tồn kho | quantity > 0 → Còn; = 0 → Hết; cờ riêng "Ngừng bán" | ✓ |
| Admin chọn thủ công | Bấm 1 trong 3 trạng thái | |
| Kết hợp, tự sửa | Admin chọn nhưng tồn = 0 thì ép về Hết | |

**User's choice:** Tự suy từ tồn kho
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Tạo ngay Phase 1 | Bảng ProductImage + quan hệ một-nhiều | ✓ |
| Để Phase 2 | Phase 1 chỉ có Product thuần | |

**User's choice:** Tạo ngay Phase 1
**Notes:** —

---

## Phiên đăng nhập

| Option | Description | Selected |
|--------|-------------|----------|
| 30 ngày | Cân bằng tiện lợi và an toàn | ✓ |
| 7 ngày | Nhắc đăng nhập lại hàng tuần | |
| 90 ngày | Nhớ gần như vĩnh viễn | |

**User's choice:** 30 ngày
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Luôn nhớ | Mặc định duy trì, không có ô tick | ✓ |
| Có ô checkbox, mặc định tick | Thêm tùy chọn "Ghi nhớ đăng nhập" | |
| Chỉ theo phiên trình duyệt | Đóng trình duyệt là hết phiên | |

**User's choice:** Luôn nhớ
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Báo lỗi chung, không khóa | "Sai tên đăng nhập hoặc mật khẩu", không giới hạn lần thử | ✓ |
| Khóa tạm sau 5 lần sai | Khóa 5 phút sau 5 lần sai liên tiếp | |
| Báo lỗi riêng từng loại | Nói rõ tên sai / mật khẩu sai | |

**User's choice:** Báo lỗi chung, không khóa
**Notes:** —

---

## Trang Phase 1

| Option | Description | Selected |
|--------|-------------|----------|
| Trang quản trị + nav sẵn | Lời chào + nav (Trang chủ, Sản phẩm trống, Đăng xuất) | ✓ |
| Trang chào tối thiểu | Chỉ "Xin chào" + nút Đăng xuất | |
| Không có trang admin riêng | Quay về trang chủ công khai | |

**User's choice:** Trang quản trị + nav sẵn
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Trang chờ sẵn sàng | "Cửa hàng đang chuẩn bị" + nút Messenger | ✓ |
| Chưa có trang công khai | Chỉ phục vụ đăng nhập admin | |
| Khung danh sách sản phẩm | Khung trang chủ danh sách trống | |

**User's choice:** Trang chờ sẵn sàng
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Quay về trang định truy cập | Dùng next param sau khi đăng nhập | ✓ |
| Luôn về trang quản trị chính | Bất kể trang trước đó | |

**User's choice:** Quay về trang định truy cập
**Notes:** —

---

## Claude's Discretion

Không có vùng nào user chọn "bạn quyết định". Các chi tiết kỹ thuật (tên route, cấu trúc template, cơ chế SECRET_KEY, cấu trúc thư mục, cách khai báo db.create_all) bàn giao cho planner/researcher.

## Deferred Ideas

None — discussion stayed within phase scope.
