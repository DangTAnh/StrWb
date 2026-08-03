# Phase 8: Admin Stats - Context

**Gathered:** 2026-08-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Trang thống kê admin: doanh thu + lợi nhuận (NULL-safe), số đơn theo trạng thái, tổng sản phẩm đã bán, số sản phẩm trong kho. Covers STAT-01, STAT-02, STAT-03, STAT-04.

**Depends on:** Phase 7 (Order + OrderItem snapshot đã có `product_cost_price` nullable; admin orders list/detail + transition đã xong). Route mới `GET /admin/stats` — tách riêng khỏi dashboard.

</domain>

<decisions>
## Implementation Decisions

### Doanh thu & Lợi nhuận (STAT-01, STAT-02)
- **Trạng thái tính doanh thu**: chỉ đơn `Đã gửi` + `Đã nhận` (đã lock từ SC — không bao gồm Chờ xác nhận/Đã gói/Đã hủy).
- **Revenue** = `sum(order_items.product_price * quantity)` trên các OrderItem của đơn có status ∈ {Đã gửi, Đã nhận}.
- **Profit NULL-safe**: loại item có `product_cost_price IS NULL` khỏi lợi nhuận (không coi là 0 — tránh overstate). Hiện note: "Lợi nhuận tính trên N sản phẩm có giá nhập" khi có item bị loại. Profit = `sum((product_price - product_cost_price) * quantity)` trên items còn lại.
- **Phạm vi thời gian**: toàn thời gian (STAT-05 lọc theo ngày → v2 deferred).
- **"Đã hủy" không tính vào doanh thu/lợi nhuận** — chỉ hiện trong breakdown trạng thái.
- **Units sold** (sản phẩm đã bán) = `sum(quantity)` trên items của đơn Đã gửi + Đã nhận — nhất quán với revenue.

### Đơn hàng theo trạng thái (STAT-03)
- Breakdown cả **5 trạng thái** (Chờ xác nhận, Đã gói, Đã gửi, Đã nhận, Đã hủy) + tổng số đơn (gồm cả Đã hủy).
- Mỗi status **click được** → link sang `/admin/orders?status=<label>` (filter pattern đã có sẵn Phase 7).
- Tổng đơn = đếm tất cả order (mọi trạng thái).

### Tồn kho (STAT-04)
- **Tổng sản phẩm** = đếm tất cả Product (kể cả discontinued).
- **Hết hàng** = `quantity = 0` VÀ không discontinued (tách riêng khỏi ngừng bán).
- **Ngừng bán** = `discontinued = True`.
- **Còn hàng** = `quantity > 0` VÀ không discontinued (thêm ngoài SC — đủ 3 phân khúc rõ ràng).

### UI & Vị trí
- Route mới `GET /admin/stats` → `admin.stats()` — KHÔNG nhúng vào dashboard.
- Nav admin (dashboard.html): thêm mục **"Thống kê"** (pattern giống mục "Đơn hàng").
- **Server-rendered tĩnh khi load** — không JS polling, 0 dependency mới.
- Layout: grid thẻ số liệu theo nhóm (Doanh thu/Lợi nhuận, Đơn hàng, Kho) — tái dùng `admin-card` CSS sẵn có.
- **Empty state**: hiện số 0 rõ ràng (₫0, 0 đơn) + label, không để trống, không báo lỗi.
- Định dạng tiền: dùng `format_price` helper đã có (hiển thị VND).

### Claude's Discretion
Không có — user đã chốt đủ 4 area.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/admin.py` — admin_bp, `_protect_admin` @login_required (mọi route tự bảo vệ), `_order_total(order)` helper, `ORDER_STATUSES` + `order_badge_class` Jinja globals, `format_price` helper
- `app/models.py` — `Order.status` (VN label), `Order.items` relationship `lazy='dynamic'`, `OrderItem.product_price`/`product_cost_price`/`quantity`, `Product.quantity`/`discontinued`
- `app/templates/admin/dashboard.html` — nav-list pattern + badge counts (products_count, orders_count)
- `app/templates/admin/orders/list.html` — pagination render + status filter pattern (Phase 7)
- `app/static/css/style.css` — `.admin-card`, badge-order-* classes
- Flask-WTF CSRF toàn app — mọi POST cần token (stats là GET thuần, không cần form)

### Established Patterns
- Route admin: `@admin_bp.route(...)` + `@login_required` (qua before_request), query + render_template, flash + redirect
- Nav: `.nav-list` trong dashboard.html với `.nav-group` + badge count
- Query: SQLAlchemy 2.0 style (`db.session.query(...).filter(...)`)
- Tổng tiền: `_order_total(order)` sum từ items (không có cột total)

### Integration Points
- `app/admin.py` — thêm 1 route: `admin.stats()` (GET /admin/stats)
- `app/templates/admin/stats.html` — 1 template mới
- `app/templates/admin/dashboard.html` — thêm nav item "Thống kê"
- `app/static/css/style.css` — CSS cho stats cards (nếu cần thêm class mới)

</code_context>

<specifics>
## Specific Ideas

- Stats page nhóm thành 3 cụm thẻ: **Doanh thu & Lợi nhuận** (revenue, profit, units sold), **Đơn hàng** (tổng + 5 status breakdown, clickable), **Kho** (tổng, còn hàng, hết hàng, ngừng bán).
- Note NULL-safe profit chỉ hiện khi có item thiếu cost — không hiện vĩnh viễn.
- Mỗi status trong breakdown là link `<a href="/admin/orders?status=...">`.

</specifics>

<deferred>
## Deferred Ideas

- Lọc theo khoảng ngày (STAT-05 → v2)
- Export CSV (STAT-06 → v2)
- Bảng lợi nhuận theo từng sản phẩm (STAT-07 → v2)
- Auto-refresh dữ liệu (không cần — server-rendered tĩnh)
</deferred>
