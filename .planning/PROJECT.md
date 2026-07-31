# StoreWeb

## What This Is

Web bán hàng tiếng Việt để trưng bày và quản lý sản phẩm. Khách vào web xem danh sách hàng với chi tiết đầy đủ (ảnh, giá, thương hiệu, số đo, mô tả, trạng thái còn/hết hàng) rồi liên hệ mua qua Messenger. Chủ web đăng nhập một tài khoản admin để thêm/sửa/xóa sản phẩm, quản lý danh mục trạng thái và tồn kho. Backend Python Flask, tự host.

## Core Value

Khách xem được list hàng rõ ràng (ảnh + giá + trạng thái) và admin dễ dàng quản lý sản phẩm.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Khách xem danh sách sản phẩm công khai, không cần tài khoản
- [ ] Khách xem chi tiết sản phẩm: ảnh, giá, thương hiệu, số đo, mô tả, trạng thái
- [ ] Trang liên hệ chung với link Messenger để khách đặt mua
- [ ] Admin đăng nhập bằng tài khoản duy nhất (mật khẩu)
- [ ] Admin thêm/sửa/xóa sản phẩm kèm ảnh
- [ ] Admin đánh dấu trạng thái Còn hàng / Hết hàng / Ngừng bán
- [ ] Admin theo dõi số lượng tồn kho, tự ẩn khi hết
- [ ] Giao diện tiếng Việt

### Out of Scope

- Giỏ hàng / thanh toán online — giao dịch qua Messenger
- Tài khoản khách hàng — chỉ admin
- Phân loại / danh mục sản phẩm — danh sách phẳng
- OAuth, đăng ký admin mới — một tài khoản duy nhất

## Context

- Người dùng muốn tự host web (deploy lên VPS/máy riêng), không dùng dịch vụ PaaS sẵn có.
- Backend cố định: Python Flask.
- Giao dịch không nằm trong web — chỉ là kênh giới thiệu sản phẩm + liên hệ.
- Chưa có code hiện có (greenfield, thư mục D:\Python\storewweb trống).

## Constraints

- **Tech stack**: Python Flask — đã chốt bởi người dùng
- **Ngôn ngữ**: Tiếng Việt — giao diện duy nhất tiếng Việt
- **Deploy**: Tự host — cần cấu hình chạy trên máy riêng (ví dụ gunicorn + nginx hoặc tương đương)
- **Dữ liệu**: Cần lưu trữ sản phẩm + ảnh — SQLite là lựa chọn mặc định (nhẹ, tự host dễ)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Giao dịch qua Messenger, không tích hợp thanh toán | Người dùng yêu cầu | — Pending |
| Chỉ một tài khoản admin | Người dùng yêu cầu | — Pending |
| Không phân loại sản phẩm | Người dùng yêu cầu | — Pending |
| SQLite cho dữ liệu | Nhẹ, phù hợp tự host | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-07-31 after initialization*
