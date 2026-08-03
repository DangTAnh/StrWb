# StoreWeb

## What This Is

Web bán hàng tiếng Việt để trưng bày và quản lý sản phẩm. Khách vào web xem danh sách hàng với chi tiết đầy đủ (ảnh, giá, thương hiệu, số đo, mô tả, trạng thái còn/hết hàng), thêm vào giỏ hàng nhiều sản phẩm rồi đặt hàng qua form (tên, SĐT, địa chỉ). Chủ web đăng nhập một tài khoản admin để thêm/sửa/xóa sản phẩm, theo dõi và cập nhật trạng thái đơn hàng, xem thống kê doanh thu/lợi nhuận. Backend Python Flask, tự host. **Đã shipped v1.0 (4 phase) và v1.1 Buy System (5 phase).**

## Core Value

Khách xem được list hàng rõ ràng (ảnh + giá + trạng thái) và admin dễ dàng quản lý sản phẩm.

## Current Milestone: v1.2 Đợt bán (Sale Batches)

**Goal:** Chia catalog thành các đợt bán — admin tạo đợt, gán sản phẩm (nhiều đợt được), ẩn/hiện từng đợt sau khi đã chuẩn bị xong sản phẩm; public chỉ thấy các đợt đang hiện.

**Target features:**
- Admin tạo/sửa/xóa đợt bán (chỉ tên + thứ tự + cờ ẩn/hiện)
- Admin gán sản phẩm vào nhiều đợt (many-to-many)
- Admin ẩn/hiện từng đợt bán (toggle)
- Trang chủ hiển thị từng section theo đợt đang hiện, theo thứ tự sắp xếp
- Sản phẩm chưa gán vào đợt nào = ẩn khỏi public (search, chi tiết, giỏ hàng cũng không thấy)
- Admin vẫn thấy toàn bộ sản phẩm trong quản trị

## Current State

**Đã shipped v1.1 Buy System (2026-08-03):** hệ thống đặt hàng nhiều sản phẩm (session cart + checkout với CSRF/honeypot), Order + OrderItem snapshot, theo dõi đơn admin (forward-only status), thống kê doanh thu/lợi nhuận NULL-safe, migration SQLite idempotent. Audit PASSED 19/19 reqs, 5/5 phases.

**Next:** Milestone v1.2 Đợt bán đang planning (requirements → roadmap). Sau roadmap: `/gsd:plan-phase [N]`.

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

### Validated (v1.1)

- ✓ Khách đặt hàng nhiều sản phẩm qua giỏ hàng + checkout form (ORD-01/02/03/05, ORD-10/10a/10b) — v1.1
- ✓ Admin xem và cập nhật trạng thái đơn hàng forward-only (ORD-06/07/08/09) — v1.1
- ✓ Admin nhập giá nhập tùy chọn, không hiện công khai (COST-01/02) — v1.1
- ✓ Trang thống kê: doanh thu + lợi nhuận NULL-safe, số đơn theo trạng thái, sản phẩm đã bán, tồn kho (STAT-01..04) — v1.1
- ✓ Migration SQLite idempotent, không mất dữ liệu (PLAT-05) — v1.1

### Active

- [ ] Admin tạo/sửa/xóa đợt bán (BATCH-01/02/03) — v1.2
- [ ] Admin gán sản phẩm vào nhiều đợt (BATCH-04) — v1.2
- [ ] Admin ẩn/hiện từng đợt bán (BATCH-05) — v1.2
- [ ] Trang chủ hiển thị section theo từng đợt đang hiện, đúng thứ tự (BATCH-06/07) — v1.2
- [ ] Sản phẩm chưa gán đợt = ẩn khỏi public (search, chi tiết, giỏ hàng) (BATCH-08) — v1.2

### Out of Scope

- Thanh toán online (MoMo/VNPay/card) — giao dịch khi giao hàng, ngoài luồng web
- Tài khoản khách hàng — đặt hàng ẩn danh đủ cho quy mô hiện tại
- Phân loại / danh mục sản phẩm — catalog phẳng
- OAuth, đăng ký admin mới — một tài khoản duy nhất
- Thông báo đơn mới cho admin (ORD-11), tự trừ tồn kho (ORD-12), stats theo ngày/export/CSV (STAT-05..07) — deferred v2

## Context

- **Đã shipped:** v1.0 (2026-08-01, 4 phase, 12 plans, audit PASSED 28/28) và v1.1 Buy System (2026-08-03, 5 phase, 15 plans, audit PASSED 19/19, integration clean).
- **Codebase:** Flask app tại `app/` — 3 blueprints (public/admin/auth), Flask-Login, Flask-WTF + CSRF, SQLite WAL + busy_timeout, image_utils (Pillow thumbnails), format_price. Thêm `Order`/`OrderItem` models, cart/checkout routes, admin order tracking + stats.
- **Deploy:** `docs/deploy/` — waitress (Windows), gunicorn/systemd (Linux), nginx HTTPS + admin rate-limit. `YOUR_DOMAIN` placeholder phải thay trước go-live (D-03).
- **Tech stack:** Flask 3.1.3, Flask-SQLAlchemy 3.1.1, Flask-Login 0.6.3, Flask-WTF 1.3.0, Pillow, waitress (pin trong requirements.txt).
- **UAT còn lại (non-blocking):** 6 visual items human UAT v1.1 (Phase 5+6) + v1.0 Phase 2-4 items + admin nav subpage + image-upload E2E harness gap (xem STATE.md Deferred Items).
- **Go-live v1.1:** chạy `flask --app wsgi init-db` trên DB thật để áp migration PLAT-05 (idempotent, an toàn nếu legacy orders có hàng thì báo `Manual migration required`).

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
| Không phân loại sản phẩm | Người dùng yêu cầu, catalog phẳng | ⚠️ Revisit — v1.2 thêm "đợt bán" (grouping theo đợt bán, không phải danh mục thông thường) |
| SQLite cho dữ liệu | Nhẹ, phù hợp tự host | ✓ Validated — v1.0 (PLAT-03, WAL) |
| Flask app factory + 3 blueprints (public/admin/auth) | Phân tách rõ ràng, chuẩn Flask | ✓ Good — v1.0 |
| Werkzeug generate/check_password_hash | Mật khẩu admin băm scrypt/pbkdf2 | ✓ Good — v1.0 |
| Search không dấu in-Python (NFD + strip Mn + casefold) | Không thêm cột/SQL LIKE, chính xác tiếng Việt | ✓ Good — v1.0 (decision 7 UI-SPEC) |
| Admin login chỉ app login + nginx rate-limit `/login` | Đủ cho 1 admin tự host, không basic auth/allowlist | ✓ Good — v1.0 (D-04) |
| Deploy: waitress (Windows) + gunicorn/systemd (Linux) + nginx HTTPS | gunicorn không chạy native Windows; waitress thay thế | ✓ Good — v1.0 |
| `YOUR_DOMAIN` placeholder trong nginx/Linux.md/README | Chưa có domain thật lúc execute | ⚠️ Revisit — thay trước go-live (D-03) |
| Thay nút "Mua qua Messenger" bằng add-to-cart; giữ dải liên hệ Messenger ở trang chủ | Người dùng chốt trong questioning v1.1 | ✓ Validated — v1.1 (ORD-10b) |
| Giỏ hàng nhiều sản phẩm (session) + checkout tạo Order + OrderItem snapshot | Người dùng mở rộng phạm vi trong questioning; mỗi đơn nhiều sản phẩm | ✓ Validated — v1.1 (ORD-10/10a) |
| Giá nhập tùy chọn, chỉ admin thấy; dùng tính lợi nhuận | Người dùng chốt trong questioning v1.1 | ✓ Validated — v1.1 (COST-01/02) |
| Trạng thái đơn: Chờ xác nhận → Đã gói → Đã gửi → Đã nhận (+ Đã hủy), forward-only | Người dùng yêu cầu | ✓ Validated — v1.1 (ORD-08/09) |
| Tồn kho không tự giảm khi đặt hàng (ORD-12 deferred v2) | Đơn giản hóa v1.1, tránh race | ⚠️ Revisit — deferred v2 |
| Đợt bán chỉ giữ tên + thứ tự + cờ ẩn/hiện (không mô tả/ảnh bìa) | Người dùng chọn trong questioning v1.2 | ✓ Pending — v1.2 |
| Sản phẩm ↔ đợt bán many-to-many (1 sản phẩm nhiều đợt) | Người dùng chọn trong questioning v1.2 | ✓ Pending — v1.2 |
| Public hiển thị từng section theo thứ tự trên trang chủ (không thêm route riêng) | Người dùng chọn trong questioning v1.2 | ✓ Pending — v1.2 |
| Sản phẩm chưa gán đợt = ẩn khỏi public (search/chi tiết/giỏ hàng) | Người dùng chọn trong questioning v1.2 | ✓ Pending — v1.2 |

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
*Last updated: 2026-08-03 after v1.2 milestone start*
