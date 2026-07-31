# Phase 2: Admin CRUD + Images — Context

**Gathered:** 2026-08-01
**Status:** Ready for planning

## Phase Boundary

Admin có thể quản lý trọn đời sản phẩm: danh sách sản phẩm (bảng + thumbnail), tạo/sửa/xóa sản phẩm với đầy đủ trường (PROD-01..07), và upload nhiều ảnh mỗi sản phẩm có validate (magic bytes, kích thước, giới hạn dung lượng) + sinh thumbnail (IMG-01..04). Xóa sản phẩm qua POST + CSRF.

Danh sách/catalog công khai (Phase 3), tìm kiếm (Phase 3), polish hiển thị công khai (Phase 4) **không** nằm trong phase này — chỉ có admin CRUD + ảnh.

## Implementation Decisions

### Danh sách sản phẩm (Admin Product List)
- **D-01:** Danh sách admin hiển thị dạng **bảng + thumbnail ảnh** (không phải thẻ card). Cột gồm: ảnh nhỏ, tên, SKU, giá, tồn kho, trạng thái, hành động Sửa/Xóa. Thumbnail lấy từ ảnh chính (xem D-12).
- **D-02:** Sắp xếp mặc định theo trường `sort_order` (đã có từ Phase 1, D-06) — thứ tự trong admin khớp thứ tự hiển thị công khai, sản phẩm nổi bật lên đầu.
- **D-03:** Có **phân trang**, mỗi trang **20 sản phẩm**.

### Xóa sản phẩm (Product Delete)
- **D-04:** Có **hộp xác nhận trước khi xóa** (hiện tên sản phẩm để admin chắc chắn).
- **D-05:** Xóa **file ảnh trên đĩa theo** cùng lúc xóa sản phẩm — không để ảnh mồ côi.
- **D-06:** Thứ tự xử lý: **xóa dòng DB trước, dọn file ảnh sau** (chống lỗi nửa chừng).
- **D-07:** Flash message chi tiết sau khi xóa: "Đã xóa sản phẩm [tên]" + số ảnh đã xóa (nếu có).
- **D-08:** **Không hoàn tác / không thùng rác** — xóa là thao tác cuối, không soft-delete.
- **D-09:** Lỗi dọn ảnh trên đĩa (file không tồn tại, bị khóa) chỉ **ghi cảnh báo trong flash**, không chặn luồng xóa.

### Upload ảnh gallery (Image Gallery Upload)
- **D-10:** Upload ảnh **ngay trong form tạo/sửa sản phẩm** — không có màn hình quản lý ảnh riêng. Luồng nhập liệu gọn, tạo xong là có ảnh.
- **D-11:** Cơ chế chọn file dùng `<input type="file" multiple>` — **chọn nhiều file một lần**.
- **D-12:** **Ảnh đầu tiên trong gallery là ảnh chính** — dùng làm thumbnail trong danh sách. Đổi ảnh chính = sắp lại thứ tự.
- **D-13:** **Thứ tự ảnh sắp xếp lại được** (nút lên/xuống, hoặc kéo thả nếu đơn giản) — thay vì cố định theo lúc upload.

### Sửa ảnh riêng lẻ (Per-Image Management)
- **D-14:** Quản lý ảnh **ngay trong form sửa sản phẩm**: gallery hiện ảnh hiện có kèm khả năng xóa từng ảnh + thêm ảnh mới.
- **D-15:** Xóa 1 ảnh bằng cách **tick chọn trong form rồi lưu** (submit POST + CSRF) — không xóa tức thì qua request riêng.
- **D-16:** Validate ảnh **theo chuẩn research** (PITFALLS.md): kiểm tra extension theo allowlist `{.jpg,.jpeg,.png,.webp}`, **magic bytes** (JPEG `FF D8 FF`, PNG `89 50 4E 47 0D 0A 1A 0A`, WebP `RIFF..WEBP`), Pillow `verify()` + kiểm tra kích thước pixel (max 2000×2000 chống decompression bomb), `MAX_CONTENT_LENGTH = 16MB`, re-encode khi lưu, **tên file UUID** (giữ tên gốc tiếng Việt ở DB nếu cần, không dùng `secure_filename` làm tên hiển thị). Số cụ thể (thumb size) do planner quyết.
- **D-17:** Khi chọn nhiều file mà có **1 file không hợp lệ** → **chặn toàn bộ bộ ảnh**, báo rõ tên file + lý do trong flash; không lưu ảnh hỏng, không bỏ qua âm thầm.

### Claude's Discretion
Các chi tiết kỹ thuật bàn giao cho planner/researcher: kích thước thumbnail chính xác (px) cho danh sách + gallery, tổ chức route CRUD (tên route, blueprint admin), các class form Flask-WTF, cấu trúc template admin (kế thừa `base.html` từ Phase 1), cơ chế sắp xếp thứ tự ảnh (nút lên/xuống hay kéo thả), lưu thumbnail riêng hay ghi đè, cách hiển thị giá VND trong bảng (e.g. `1.200.000₫`).

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Definition & Requirements
- `.planning/ROADMAP.md` §"Phase 2: Admin CRUD + Images" — goal, 5 success criteria, mode mvp, requirement mapping
- `.planning/REQUIREMENTS.md` §"Quản lý sản phẩm (Admin CRUD)" (PROD-01..07) + §"Ảnh sản phẩm" (IMG-01..04) — yêu cầu v1 của phase này

### Prior Phase Decisions & Design System
- `.planning/phases/01-scaffold-auth-data-model/01-CONTEXT.md` — model Product (D-05..09: fields, measurements tự do, trạng thái tự suy từ quantity + cờ discontinued, ProductImage một-nhiều) + các pattern Phase 1
- `.planning/phases/01-scaffold-auth-data-model/01-UI-SPEC.md` — design system baseline (spacing 4/8/16/24/32/48/64, màu 60/30/10 #F9FAFB/#FFFFFF/#2563EB, typography 14/16/24/32, copy tiếng Việt chuẩn) — Phase 2 bám theo
- `CLAUDE.md` — tech stack đã chốt + phiên bản (Flask 3.1.3, Flask-SQLAlchemy 3.1.1, Flask-WTF 1.3.0, Pillow 12.3.0, python-dotenv) + What NOT to use (Flask-Admin, Flask-Images, passlib)

### Research & Pitfalls
- `.planning/research/SUMMARY.md` — kiến trúc (app factory, 3 blueprints, admin.py CRUD), pattern upload ảnh (Pillow magic bytes + verify, UUID filename, thumbnail), pitfalls chính
- `.planning/research/PITFALLS.md` — chi tiết phòng tránh: **Pitfall 3** (image path traversal: extension allowlist, magic bytes, verify, 2000×2000, 16MB, send_from_directory), **Pitfall 7** (decompression bomb: MAX_CONTENT_LENGTH + dimension check + re-encode), UX pitfalls (empty state, price format, POST delete), "Looks Done But Isn't" checklist

## Existing Code Insights

### Reusable Assets
- Chưa có code Phase 2 — Phase 1 (scaffold + auth + model) đang được plan/execute. Phase 2 dựng trên: `app/admin.py` (blueprint admin + routes CRUD), `app/models.py` (Product + ProductImage đã khai báo từ Phase 1), `app/templates/admin/` (kế thừa `base.html`).

### Established Patterns
- App factory + 3 blueprints (public/admin/auth), Flask-Login bảo vệ mọi route admin (`@login_required`), form Flask-WTF + CSRF, giao diện tiếng Việt `lang="vi"` + utf-8 — các pattern Phase 1 mà Phase 2 phải theo.

### Integration Points
- `app/admin.py` — thêm các route CRUD product (list/create/edit/delete) + xử lý upload ảnh.
- `app/models.py` — ProductImage đã tồn tại từ Phase 1, Phase 2 dùng nó cho upload/gallery/thumbnail.
- `app/templates/admin/products/` — template list + form (kế thừa `base.html`).
- `app/static/uploads/` — thư mục lưu ảnh (đã định hình từ research; UUID filenames).

## Specific Ideas

Không có yêu cầu "làm giống X" từ thảo luận — mở cho cách tiếp cận chuẩn (standard approaches). Người dùng chọn "theo chuẩn research" cho giới hạn validate ảnh (D-16).

## Deferred Ideas

- **Toggle tồn kho nhanh ngay trên danh sách admin** — đã nằm trong REQUIREMENTS v2 (PRODV-01). Không thêm vào Phase 2; thuộc bản phát hành sau.
- **Màn hình quản lý ảnh riêng** (tách khỏi form sản phẩm) — user chọn quản lý ảnh ngay trong form sửa (D-10, D-14), không cần màn hình riêng trong v1.

---

*Phase: 2-Admin CRUD + Images*
*Context gathered: 2026-08-01*
