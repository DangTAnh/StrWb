# Phase 1: Scaffold + Auth + Data Model — Context

**Gathered:** 2026-07-31
**Status:** Ready for planning

## Phase Boundary

Nền tảng của toàn bộ ứng dụng: Flask app skeleton (app factory + 3 blueprints: public, admin, auth), cấu hình an toàn (SECRET_KEY từ env, không debug trong production), đăng nhập admin (Flask-Login, đăng xuất, bảo vệ mọi route admin), giao diện tiếng Việt (`lang="vi"` + charset utf-8), SQLite WAL mode + busy_timeout, CLI tạo database + tài khoản admin đầu tiên, và **data model Product/AdminUser/ProductImage sẵn sàng cho Phase 2** (CRUD + ảnh).

Danh sách sản phẩm công khai (Phase 3) và CRUD admin (Phase 2) **không** nằm trong phase này — chỉ có khung sẵn.

## Implementation Decisions

### Admin Credentials (tài khoản admin)
- **D-01:** Tài khoản admin đầu tiên được tạo từ biến môi trường `ADMIN_USERNAME` / `ADMIN_PASSWORD` trong `.env`, qua lệnh CLI `flask init-db`. Mật khẩu băm bằng Werkzeug scrypt khi insert.
- **D-02:** Đổi mật khẩu = sửa `ADMIN_PASSWORD` trong `.env` rồi chạy lại `flask init-db` — CLI upsert tài khoản admin và đồng bộ hash từ `.env` vào DB (tạo mới nếu chưa có, cập nhật nếu đã đổi).
- **D-03:** Mật khẩu tối thiểu 8 ký tự — `init-db` từ chối nếu ngắn hơn (kèm cảnh báo rõ ràng).
- **D-04:** File `.env` mẫu chứa `ADMIN_PASSWORD=change-me`; `init-db` **từ chối chạy** nếu còn placeholder này (chống khởi chạy web với mật khẩu mặc định).

### Product Data Model
- **D-05:** Các trường bắt buộc: `name`, `price` (số nguyên VND, không float), `brand`, `measurements`, `description`, `quantity`, `discontinued` (cờ Ngừng bán), timestamps (`created_at` / `updated_at`).
- **D-06:** Trường phụ được duyệt: `sku` (mã sản phẩm), `sort_order` (thứ tự hiển thị), `admin_note` (ghi chú nội bộ — chỉ admin xem, không hiện công khai).
- **D-07:** `measurements` = **một ô văn bản tự do** (ví dụ "60×40×2cm" hoặc "M / L / XL"), không tách trường số.
- **D-08:** Trạng thái Còn/Hết hàng **tự suy từ `quantity`**: `quantity > 0` → Còn hàng, `quantity = 0` → Hết hàng. Riêng cờ boolean `discontinued` cho trạng thái Ngừng bán (admin bật, override).
- **D-09:** Bảng `ProductImage` (quan hệ một-nhiều với Product) **được tạo ngay ở Phase 1** để schema hoàn chỉnh; Phase 2 chỉ làm phần upload/validate/thumbnail. Ảnh chưa cần xử lý ở Phase 1.

### Session & Login
- **D-10:** Phiên đăng nhập kéo dài **30 ngày** (permanent session / remember-me).
- **D-11:** **Luôn nhớ** đăng nhập — không có ô checkbox "Ghi nhớ đăng nhập" trên form.
- **D-12:** Sai tên/mật khẩu → thông báo chung "Sai tên đăng nhập hoặc mật khẩu", không tiết lộ cái nào sai; **không khóa tài khoản**, không giới hạn số lần thử (khớp research: một admin, rủi ro thấp; rate-limit để dành cho deploy Phase 4).

### Phase 1 Pages
- **D-13:** Sau đăng nhập, admin thấy **trang quản trị tối giản**: lời chào + tên đăng nhập, khung nav đầy đủ (Trang chủ, Sản phẩm — hiện trạng thái trống/chưa có sản phẩm, Đăng xuất). Khung nav sẵn cho Phase 2 chỉ việc điền vào.
- **D-14:** Trang chủ công khai = **trang chờ** tiếng Việt "Cửa hàng đang chuẩn bị, xin quay lại sau" + nút liên hệ Messenger. Catalog thật là Phase 3.
- **D-15:** Khi truy cập route admin khi chưa đăng nhập → chuyển về trang đăng nhập, sau khi đăng nhập **quay về đúng trang định truy cập** (dùng `next`). Vào thẳng trang đăng nhập → về trang quản trị chính.

### Claude's Discretion
Không có vùng nào người dùng chọn "bạn quyết định". Các chi tiết kỹ thuật bàn giao cho planner/researcher: tên chính xác các route/blueprint, cấu trúc base template, cơ chế sinh/generate SECRET_KEY (32-byte từ env), cấu trúc thư mục `app/`, cách khai báo `db.create_all()` trong CLI.

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Definition & Requirements
- `.planning/ROADMAP.md` §"Phase 1: Scaffold + Auth + Data Model" — goal, 5 success criteria, mode mvp, requirement mapping
- `.planning/REQUIREMENTS.md` §"Quản trị (Admin Auth)" (AUTH-01..04) và §"Nền tảng & Ngôn ngữ" (PLAT-01..04) — yêu cầu v1 của phase này

### Architecture & Research
- `.planning/research/SUMMARY.md` — stack khuyến nghị + kiến trúc (app factory, 3 blueprints, Flask-Login, WAL, giá Integer) và 5 pitfalls chính
- `.planning/research/PITFALLS.md` — cách phòng tránh cụ thể: debug+RCE, SECRET_KEY thiếu, SQLite locked, VND float, image path traversal
- `CLAUDE.md` — tech stack đã chốt + phiên bản (Flask 3.1.3, Flask-SQLAlchemy 3.1.1, Flask-Login 0.6.3, Flask-WTF 1.3.0, Pillow, python-dotenv) + lưu ý platform (waitress cho Windows, không dùng gunicorn native)

### Project Constraints
- `.planning/PROJECT.md` — core value, constraints (Flask, tiếng Việt, tự host, SQLite), Key Decisions, Out of Scope

## Existing Code Insights

### Reusable Assets
- Không có — dự án greenfield, chưa có code.

### Established Patterns
- Chưa có pattern nào tồn tại. Phase này tạo lập các pattern đầu tiên (app factory, blueprint, CLI init-db) mà các phase sau theo.

### Integration Points
- N/A — dự án mới. Phase 1 dựng skeleton mà mọi thứ khác (CRUD, catalog) sẽ gắn vào: `app/__init__.py` (factory), `app/models.py`, `app/auth.py`, `app/admin.py`, `app/public.py`, `app/templates/base.html`.

## Specific Ideas

Không có yêu cầu cụ thể "làm giống X" từ thảo luận — mở cho cách tiếp cận chuẩn (standard approaches).

## Deferred Ideas

None — discussion stayed within phase scope.

---

*Phase: 1-Scaffold + Auth + Data Model*
*Context gathered: 2026-07-31*
