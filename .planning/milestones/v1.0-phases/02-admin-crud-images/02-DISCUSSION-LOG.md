# Phase 2: Admin CRUD + Images - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-01
**Phase:** 2-Admin CRUD + Images
**Areas discussed:** Danh sách sản phẩm, Xóa sản phẩm, Upload ảnh gallery, Sửa ảnh riêng lẻ

---

## Danh sách sản phẩm

| Option | Description | Selected |
|--------|-------------|----------|
| Bảng + thumbnail | Bảng với cột: ảnh nhỏ, tên, SKU, giá, tồn kho, trạng thái, hành động Sửa/Xóa. Scan nhanh, phù hợp quản lý nhiều sản phẩm | ✓ |
| Thẻ card | Giống view công khai, ít thông tin hơn, khó scan khi nhiều sản phẩm | |

**User's choice:** Bảng + thumbnail
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Theo sort_order | Thứ tự admin khớp thứ tự hiển thị công khai, sản phẩm nổi bật lên đầu | ✓ |
| Mới nhất trước | Sản phẩm mới tạo hiện đầu danh sách | |
| Theo tên A-Z | Sắp theo bảng chữ cái tên sản phẩm | |

**User's choice:** Theo sort_order
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Có phân trang | Chia trang, mỗi trang cố định số sản phẩm, tránh trang nặng | ✓ |
| Cuộn dài tất cả | Hiện toàn bộ sản phẩm một trang, đơn giản | |

**User's choice:** Có phân trang
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| 20/trang | Cân bằng mật độ thông tin và tốc độ tải | ✓ |
| 10/trang | Trang nhẹ hơn | |
| 50/trang | Xem được nhiều hơn một lần | |

**User's choice:** 20/trang
**Notes:** —

---

## Xóa sản phẩm

| Option | Description | Selected |
|--------|-------------|----------|
| Có xác nhận | Hộp xác nhận hiện tên sản phẩm, chống bấm nhầm | ✓ |
| Xóa ngay, không xác nhận | Nhanh hơn nhưng dễ bấm nhầm | |

**User's choice:** Có xác nhận
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Xóa ảnh theo | Xóa file ảnh cùng lúc xóa sản phẩm, không để rác ảnh mồ côi | ✓ |
| Giữ ảnh trên đĩa | An toàn nếu cần phục hồi nhưng tốn dung lượng | |

**User's choice:** Xóa ảnh theo
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Xóa DB trước, dọn ảnh sau | Chống lỗi nửa chừng | ✓ |
| Chỉ xóa DB, quét ảnh sau | Để quét dọn ảnh cho CLI riêng | |

**User's choice:** Xóa DB trước, dọn ảnh sau
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Flash chi tiết tên SP | "Đã xóa sản phẩm [tên]" + ảnh đã xóa (nếu có) | ✓ |
| Flash chung ngắn | "Đã xóa sản phẩm" gọn | |

**User's choice:** Flash chi tiết tên SP
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Không cần hoàn tác | Xóa là thao tác cuối, có chủ ý | ✓ |
| Có thùng rác khôi phục | Soft delete, phức tạp hơn, lệch thiết kế đơn giản | |

**User's choice:** Không cần hoàn tác
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Cảnh báo, không chặn | Ghi cảnh báo vào flash, không chặn luồng xóa | ✓ |
| Rollback nếu dọn ảnh lỗi | Coi thao tác thất bại, phức tạp, hiếm khi cần | |

**User's choice:** Cảnh báo, không chặn
**Notes:** —

---

## Upload ảnh gallery

| Option | Description | Selected |
|--------|-------------|----------|
| Upload ngay trong form | Trong form tạo/sửa sản phẩm, chọn nhiều file một lúc, tạo xong là có ảnh | ✓ |
| Màn hình ảnh riêng | Tạo sản phẩm trước, sau vào màn hình quản lý ảnh riêng | |

**User's choice:** Upload ngay trong form
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Chọn nhiều file 1 lần | `<input type=file multiple>`, chọn cả bộ ảnh một lần | ✓ |
| Thêm từng ảnh | Kiểm soát từng ảnh nhưng thao tác nhiều lần | |

**User's choice:** Chọn nhiều file 1 lần
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Ảnh đầu tiên là ảnh chính | Dùng làm thumbnail danh sách; đổi ảnh chính bằng cách sắp lại thứ tự | ✓ |
| Tick chọn ảnh chính riêng | Tường minh nhưng thêm bước | |
| Không có ảnh chính | Danh sách hiện ảnh bất kỳ | |

**User's choice:** Ảnh đầu tiên là ảnh chính
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Sắp xếp thứ tự được | Nút lên/xuống hoặc kéo thả | ✓ |
| Cố định theo lúc upload | Thứ tự cố định theo thời điểm thêm | |

**User's choice:** Sắp xếp thứ tự được
**Notes:** —

---

## Sửa ảnh riêng lẻ

| Option | Description | Selected |
|--------|-------------|----------|
| Quản lý trong form sửa | Gallery hiện kèm nút xóa từng ảnh + thêm ảnh mới, một luồng duy nhất | ✓ |
| Màn hình ảnh riêng | Nút 'Ảnh' mở màn hình quản lý riêng của sản phẩm | |

**User's choice:** Quản lý trong form sửa
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Tick chọn rồi lưu | Tick ảnh cần xóa trong form rồi lưu, POST + CSRF | ✓ |
| Xóa tức thì từng ảnh | Bấm nút xóa ngay, request riêng, nhanh nhưng thêm endpoint | |

**User's choice:** Tick chọn rồi lưu
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Theo chuẩn research | Magic bytes, Pillow verify, giới hạn dung lượng, UUID; JPEG/PNG/WebP | ✓ |
| Tự đặt số cụ thể | Người dùng tự cho con số (5MB, 3000x3000...) | |

**User's choice:** Theo chuẩn research
**Notes:** Con số cụ thể do planner quyết, neo theo research (16MB, 2000×2000).

| Option | Description | Selected |
|--------|-------------|----------|
| Chặn cả bộ, báo rõ | Chặn lưu, báo tên file + lý do, không tạo ảnh hỏng | ✓ |
| Bỏ qua ảnh lỗi | Giữ ảnh hợp lệ còn lại, chấp nhận mất ảnh lỗi im lặng | |

**User's choice:** Chặn cả bộ, báo rõ
**Notes:** —

---

## Claude's Discretion

Người dùng không chọn "bạn quyết định" ở vùng nào. Các chi tiết kỹ thuật bàn giao cho planner/researcher: kích thước thumbnail (px), tổ chức route CRUD + form classes, cấu trúc template admin, cơ chế sắp xếp thứ tự ảnh (nút lên/xuống hay kéo thả), hiển thị giá VND trong bảng.

## Deferred Ideas

- **Toggle tồn kho nhanh ngay trên danh sách admin** — v2 (PRODV-01), không thêm vào Phase 2.
- **Màn hình quản lý ảnh riêng** — user chọn quản lý ảnh trong form sửa (D-10, D-14), không cần màn hình riêng trong v1.
