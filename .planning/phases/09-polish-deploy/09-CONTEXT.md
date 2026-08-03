# Phase 9: Polish + Deploy - Context

**Gathered:** 2026-08-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Close-out phase của milestone v1.1 Buy System: polish UI các bề mặt mới v1.1 (cart/checkout, admin orders, stats), xây verification harness toàn diện (16 req v1.1 + không regression v1.0), cập nhật deploy docs (migration/backup v1.1). Không thêm tính năng mới — chỉ đóng gói, xác minh, đánh bóng.

</domain>

<decisions>
## Implementation Decisions

### UI Polish Scope
- Chỉ polish các bề mặt mới v1.1: cart, checkout form, admin orders list/detail, admin stats. Trang v1.0 (home/search/product_detail) đã review + UI review approved — không đụng.
- Độ sâu: chỉ sửa lỗi đã xác nhận từ các UI review trước + 1 responsive pass 3 breakpoints (mobile/tablet/desktop). Không redesign layout.
- Xác nhận polish bằng screenshot 3 breakpoints (pattern `.planning/ui-reviews/` — cart-empty evidence đã có sẵn).
- Hoàn nguyên 2 edit lạc đang uncommitted: README.md mất heading `# StoreWeb`, `app/templates/admin/products/form.html` mất `<p class="help-text">` hướng dẫn trạng thái tự động.

### Verification Harness
- Một script `.planning/tmp/verify_11_full.py` — temp DB + seed, assert toàn bộ 16 req v1.1 (ORD-01..09, COST-01/02, STAT-01..04, PLAT-05), theo pattern `verify_08_stats_full.py` đã dùng (không thêm pytest).
- v1.0 regression: scripted smoke — catalog list/detail, search không dấu, contact strip Messenger, admin login + CRUD sản phẩm (create/update/delete).
- Kết quả ghi `09-VERIFICATION.md` với bảng traceability đầy đủ 16 req + v1.0 smoke, như phase 8.
- Human UAT (visual items deferred từ phases trước) giữ non-blocking — liệt kê trong VERIFICATION, không chặn close.

### Deploy Docs Update
- Thêm mục migration v1.1 vào deploy docs: backup `data/app.db` trước, rồi `flask --app wsgi init-db` (idempotent — nâng cấp schema v1.0 → v1.1 an toàn, PLAT-05). Không viết migration script riêng.
- Backup guidance cụ thể: SQLite (`.db` + `-wal`) + `app/static/uploads/`, cả Windows (Task Scheduler) + Linux (cron).
- Sửa `docs/deploy/README.md` (checklist chung + Verify production) + cập nhật `Windows.md`/`Linux.md` phần backup.
- Sửa README.md repo root: khôi phục heading + thêm dòng mô tả v1.1 (đặt hàng qua giỏ + theo dõi đơn + thống kê).

### Claude's Discretion
- Chi tiết polish cụ thể (màu, spacing, responsive breakpoint) theo findings UI review có sẵn — tự quyết dựa trên design tokens hiện có.
- Cấu trúc script verify (helpers, seed data) tự quyết miễn assert đủ 16 req.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.planning/tmp/verify_08_stats_full.py` — pattern verify harness (temp DB, seed, assert, TASK_OK) dùng lại cho verify_11_full.py
- `format_price` filter, `order_badge_class`, `ORDER_STATUSES`, `.badge-order-*`, `.admin-card--wide`, `.data-table` — dùng lại khi polish admin orders/stats
- `.planning/ui-reviews/` — screenshot evidence cart-empty (mobile/tablet) từ UI review gần đây
- `docs/deploy/` — README.md, Windows.md, Linux.md, nginx.conf, storeweb.service (cấu trúc docs hiện có)

### Established Patterns
- UI: plain CSS hand-rolled trong `app/static/css/style.css` (514 dòng, sections theo phase), Jinja2 templates, toàn tiếng Việt
- Verify: script đơn file chạy `SECRET_KEY=test python .planning/tmp/verify_XX.py`, temp DB isolate (Flask-SQLAlchemy dispose+rebuild engine), assert + `TASK_OK`
- Deploy docs: bảng checklist go-live + mục Verify production, hai đường Windows/Linux

### Integration Points
- Templates polish: `app/templates/public/cart.html`, `_checkout_form.html`, `product_detail.html`, `app/templates/admin/orders/list.html`, `detail.html`, `stats.html`
- CSS: thêm section mới cuối `style.css` (pattern các phase trước)
- Deploy docs: `docs/deploy/README.md` checklist + Windows.md/Linux.md backup sections

</code_context>

<specifics>
## Specific Ideas

- Khôi phục heading README repo (`# StoreWeb`) — bị lạc mất khi chỉnh sửa trước đó.
- Hoàn nguyên help-text form.html — thông tin "Trạng thái tự động: Còn hàng khi tồn kho > 0..." có ích cho admin, không nên bỏ.
- Harness verify phải chạy trên temp DB (không đụng `data/app.db` thật) — pattern đã xác lập từ phase 6/8.

</specifics>

<deferred>
## Deferred Ideas

- Human UAT visual items (từ Phase 2/3/6 còn lại) — non-blocking, liệt kê trong VERIFICATION cho operator tự kiểm.
- Re-audit cart populated sau operator chạy `init-db` trên DB thật — nằm trong Verify production checklist.

</deferred>
