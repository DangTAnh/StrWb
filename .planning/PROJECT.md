# StoreWeb

## What This Is

Web bán hàng tiếng Việt để trưng bày và quản lý sản phẩm. Khách vào web xem danh sách hàng với chi tiết đầy đủ (ảnh, giá, thương hiệu, số đo, mô tả, trạng thái còn/hết hàng) rồi đặt hàng trực tiếp qua form (tên, SĐT, địa chỉ). Chủ web đăng nhập một tài khoản admin để thêm/sửa/xóa sản phẩm, theo dõi và cập nhật trạng thái đơn hàng, xem thống kê doanh thu. Backend Python Flask, tự host. **Đã shipped v1.0 (4 phase); đang xây milestone v1.1 Buy System.**

## Core Value

Khách xem được list hàng rõ ràng (ảnh + giá + trạng thái) và admin dễ dàng quản lý sản phẩm.

## Current Milestone: v1.1 Buy System

**Goal:** Thay luồng mua qua Messenger bằng hệ thống đặt hàng + theo dõi đơn + thống kê.

**Target features:**
- Bỏ nút "Mua qua Messenger", thay bằng form đặt hàng (giữ dải liên hệ Messenger)
- Form đặt hàng trên trang chi tiết: tên, SĐT, địa chỉ, số lượng, ghi chú — mỗi đơn = 1 sản phẩm
- Thêm trường giá nhập (tùy chọn, chỉ admin thấy) cho sản phẩm
- Admin panel mục mới: theo dõi đơn, cập nhật trạng thái (đã gói → đã gửi → đã nhận)
- Trang thống kê: doanh thu + lợi nhuận, số đơn + sản phẩm đã bán, số sản phẩm trong kho

## Requirements

### Validated

- ✓ Khách xem danh sách sản phẩm công khai, không cần tài khoản (CAT-01) — v1.0
- ✓ Khách xem chi tiết sản phẩm: ảnh, giá, thương hiệu, số đo, mô tả, trạng thái (CAT-02) — v1.0
- ✓ Giá + trạng thái còn/hết hiển thị rõ trên trang (CAT-03) — v1.0
- ✓ Sản phẩm hết hàng/ngừng bán hiển thị khác đi, không lấn át (CAT-04) — v1.0
- ✓ Trang chi tiết hiển thị gallery nhiều ảnh (CAT-05) — v1.0
- ✓ Giao diện responsive trên mobile (CAT-06) — v1.0
- ✓ Khách tìm kiếm sản phẩm theo tên/mô tả (SRCH-01) — v1.0
- ✓ Trang/dải liên hệ hiển thị link Messenger (CONT-01) — v1.0
- ✓ Link Messenger dễ thấy trên trang chủ và trang chi tiết (CONT-02) — v1.0
- ✓ Admin đăng nhập bằng tài khoản duy nhất, mật khẩu băm (AUTH-01) — v1.0
- ✓ Phiên đăng nhập admin duy trì qua nhiều request (AUTH-02) — v1.0
- ✓ Admin đăng xuất được (AUTH-03) — v1.0
- ✓ Mọi trang quản trị bị chặn nếu chưa đăng nhập (AUTH-04) — v1.0
- ✓ Admin tạo sản phẩm mới (PROD-01) — v1.0
- ✓ Admin sửa mọi thông tin sản phẩm (PROD-02) — v1.0
- ✓ Admin xóa sản phẩm an toàn CSRF (PROD-03) — v1.0
- ✓ Admin đặt trạng thái Còn hàng / Hết hàng / Ngừng bán (PROD-04) — v1.0
- ✓ Admin nhập tồn kho; tồn = 0 tự coi là hết hàng (PROD-05) — v1.0
- ✓ Giá lưu dạng số nguyên VND, không mất chính xác (PROD-06) — v1.0
- ✓ Form admin có CSRF + validate dữ liệu (PROD-07) — v1.0
- ✓ Admin upload ảnh, được validate (IMG-01) — v1.0
- ✓ Ảnh lưu filesystem, tên file UUID (IMG-02) — v1.0
- ✓ Mỗi sản phẩm hỗ trợ nhiều ảnh gallery (IMG-03) — v1.0
- ✓ Ảnh resize tạo thumbnail cho danh sách (IMG-04) — v1.0
- ✓ Giao diện toàn tiếng Việt, `lang="vi"` + utf-8 (PLAT-01) — v1.0
- ✓ SECRET_KEY từ môi trường, không debug trong production (PLAT-02) — v1.0
- ✓ SQLite WAL mode + busy_timeout (PLAT-03) — v1.0
- ✓ Script/CLI khởi tạo database + admin đầu tiên (PLAT-04) — v1.0

### Active

- [ ] Khách đặt hàng sản phẩm qua form (tên, SĐT, địa chỉ, số lượng) thay cho nút mua Messenger
- [ ] Admin xem và cập nhật trạng thái đơn hàng (đã gói, đã gửi, đã nhận)
- [ ] Admin nhập giá nhập cho sản phẩm (tùy chọn, chỉ admin thấy)
- [ ] Trang thống kê: doanh thu + lợi nhuận, số đơn + sản phẩm đã bán, số sản phẩm trong kho

### Out of Scope

- Giỏ hàng nhiều sản phẩm / thanh toán online — mỗi đơn = 1 sản phẩm, giao dịch khi giao hàng
- Tài khoản khách hàng — chỉ admin
- Phân loại / danh mục sản phẩm — danh sách phẳng
- OAuth, đăng ký admin mới — một tài khoản duy nhất

## Context

- **Đã shipped:** Milestone v1.0 hoàn tất — 4 phase, 12 plans, 38 tasks, 100% verified. Audit PASSED (28/28 reqs, 6/6 E2E flows). Code review + UI review cả 4 phase đều clean.
- **Đang xây:** Milestone v1.1 Buy System — thay luồng mua Messenger bằng form đặt hàng (tên/SĐT/địa chỉ), thêm giá nhập, admin theo dõi đơn + thống kê. Schema SQLite sẽ thêm cột `cost_price` + bảng `orders`/`order_items`.
- **Codebase:** Flask app tại `app/` — 3 blueprints (public/admin/auth), Flask-Login, Flask-WTF + CSRF, SQLite WAL + busy_timeout, image_utils (Pillow thumbnails), format_price. ~637 LOC Python + 589 templates + 425 CSS.
- **Deploy:** `docs/deploy/` — waitress (Windows), gunicorn/systemd (Linux), nginx HTTPS + admin rate-limit. `YOUR_DOMAIN` placeholder phải thay trước go-live (D-03).
- **Tech stack:** Flask 3.1.3, Flask-SQLAlchemy 3.1.1, Flask-Login 0.6.3, Flask-WTF 1.3.0, Pillow, waitress (pin trong requirements.txt).
- **UAT còn lại:** 6 visual items human UAT (Phase 2+3) + Phase 4 go-live checks — non-blocking, test qua `flask --app wsgi run --debug`.

## Constraints

- **Tech stack**: Python Flask — đã chốt bởi người dùng
- **Ngôn ngữ**: Tiếng Việt — giao diện duy nhất tiếng Việt
- **Deploy**: Tự host — cần cấu hình chạy trên máy riêng (ví dụ gunicorn + nginx hoặc tương đương)
- **Dữ liệu**: Cần lưu trữ sản phẩm + ảnh — SQLite là lựa chọn mặc định (nhẹ, tự host dễ)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Giao dịch qua Messenger, không tích hợp thanh toán | Người dùng yêu cầu | ✓ Validated — v1.0 (CONT-01/02) |
| Chỉ một tài khoản admin | Người dùng yêu cầu | ✓ Validated — v1.0 (AUTH-01..04) |
| Không phân loại sản phẩm | Người dùng yêu cầu, catalog phẳng | ✓ Validated — v1.0 |
| SQLite cho dữ liệu | Nhẹ, phù hợp tự host | ✓ Validated — v1.0 (PLAT-03, WAL) |
| Flask app factory + 3 blueprints (public/admin/auth) | Phân tách rõ ràng, chuẩn Flask | ✓ Good — v1.0 |
| Werkzeug generate/check_password_hash | Mật khẩu admin băm scrypt/pbkdf2 | ✓ Good — v1.0 |
| Search không dấu in-Python (NFD + strip Mn + casefold) | Không thêm cột/SQL LIKE, chính xác tiếng Việt | ✓ Good — v1.0 (decision 7 UI-SPEC) |
| Admin login chỉ app login + nginx rate-limit `/login` | Đủ cho 1 admin tự host, không basic auth/allowlist | ✓ Good — v1.0 (D-04) |
| Deploy: waitress (Windows) + gunicorn/systemd (Linux) + nginx HTTPS | gunicorn không chạy native Windows; waitress thay thế | ✓ Good — v1.0 |
| `YOUR_DOMAIN` placeholder trong nginx/Linux.md/README | Chưa có domain thật lúc execute | ⚠️ Revisit — thay trước go-live (D-03) |
| Thay nút "Mua qua Messenger" bằng form đặt hàng; giữ dải liên hệ Messenger | Người dùng chốt trong questioning v1.1 | — Pending — v1.1 |
| Mỗi đơn = 1 sản phẩm, khách chọn số lượng; không giỏ hàng | Người dùng chốt trong questioning v1.1; giỏ hàng vẫn out of scope | — Pending — v1.1 |
| Giá nhập tùy chọn, chỉ admin thấy; dùng tính lợi nhuận | Người dùng chốt trong questioning v1.1 | — Pending — v1.1 |
| Trạng thái đơn: đã gói → đã gửi → đã nhận | Người dùng yêu cầu | — Pending — v1.1 |

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
*Last updated: 2026-08-02 after starting milestone v1.1*
