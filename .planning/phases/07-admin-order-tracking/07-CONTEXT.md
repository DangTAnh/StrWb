# Phase 7: Admin Order Tracking - Context

**Gathered:** 2026-08-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Admin quản lý đơn hàng: danh sách đơn (phân trang, lọc theo trạng thái) + chi tiết đơn (thông tin khách, sản phẩm snapshot, số lượng, giá, ghi chú, thời gian) + chuyển trạng thái forward-only Chờ xác nhận → Đã gói → Đã gửi → Đã nhận (+ Đã hủy, admin only). Covers ORD-06, ORD-07, ORD-08, ORD-09.

**Depends on:** Phase 6 (Order + OrderItem model đã refactor xong — orders giữ customer+status, order_items snapshot từng sản phẩm).

</domain>

<decisions>
## Implementation Decisions

### Status Flow (ORD-08, ORD-09)
- 5 trạng thái tiếng Việt (decision đã lock từ Phase 6 model): `Chờ xác nhận` (default) → `Đã gói` → `Đã gửi` → `Đã nhận`; + `Đã hủy` (admin only, không phải bước trong chuỗi tiến)
- **Forward-only, không lùi** (ORD-09): chuyển từ trạng thái hiện tại chỉ được tới trạng thái kế tiếp trong chuỗi. `Đã nhận` là cuối — không chuyển tiếp được. `Đã hủy` là trạng thái hấp thụ — hủy rồi thì hết, không chuyển đâu khác.
- **Ai được hủy?** Chỉ admin (mọi route admin đã `@login_required` qua `_protect_admin`) — ORD-08.
- **Hủy được từ đâu?** Từ `Chờ xác nhận` hoặc `Đã gói` (trước khi gửi). `Đã gửi`/`Đã nhận` là tiến không thể lùi — không cho hủy (forward-only, giữ nguyên tắc không lùi). Server-side enforce: từ `Đã gửi`/`Đã nhận` không có transition hợp lệ nào ngoài rỗng.
- **Transition map** (server-side duy nhất, không tin client):
  ```
  'Chờ xác nhận': {'Đã gói', 'Đã hủy'}
  'Đã gói':       {'Đã gửi', 'Đã hủy'}
  'Đã gửi':       {'Đã nhận'}
  'Đã nhận':      set()   # terminal — hết chuỗi
  'Đã hủy':       set()   # terminal — hấp thụ
  ```
- **Invalid transition → flash error + redirect, không 500, không thay đổi DB.**

### Order List (ORD-06)
- Route: `GET /admin/orders` → `admin.orders()` — pattern y hệt `admin.products()` (paginate per_page=20, error_out=False, page từ `request.args`).
- Sắp xếp: `created_at desc, id desc` (đơn mới nhất trước).
- Lọc theo status: query param `?status=<label tiếng Việt>` hoặc `?status=` (trống = tất cả). Dropdown filter trong template. Nếu status param không hợp lệ (không nằm trong 5) → bỏ qua filter (hoặc flash), không 500.
- Mỗi dòng hiện: **ID đơn, tên khách, tổng tiền (sum order_items), trạng thái, ngày tạo** + link vào chi tiết. Tổng tiền tính từ items (KHÔNG cột total — sum là nguồn truth).
- **Tổng tiền đơn** = `sum(item.product_price * item.quantity for item in order.items)` — hàm helper `_order_total(order)` trong admin.py.
- Count theo status hiển thị bên cạnh filter (như pattern product dashboard) — optional, nếu rẻ thì làm.
- Vùng admin đã bảo vệ `@login_required` — không cần làm lại.

### Order Detail (ORD-07)
- Route: `GET /admin/orders/<int:order_id>` → `admin.order_detail(order_id)`. Order không tồn tại → flash 'Không tìm thấy đơn.' + redirect về `/admin/orders`.
- Hiện: customer_name/phone/address/note, status, created_at/updated_at, từng OrderItem (product_name, quantity, product_price, thành tiền = price*qty), tổng tiền.
- `product_id` có thể NULL (product bị xóa — SET NULL) → hiện snapshot `product_name` là đủ, không cần link product (nếu product còn, optional link vào admin product edit).
- **Không hiện `product_cost_price` ở đây** (nhạy cảm, Phase 7 chỉ cần giá bán; cost_price dùng cho Phase 8 stats — IN-02 code review đã ghi chú giữ trong vùng `@login_required`; chi tiết đơn admin có quyền thấy nhưng KHÔNG cần hiện — defer, giữ tối giản).
- Timestamps: hiển thị định dạng tiếng Việt dễ đọc (vd `%d/%m/%Y %H:%M`).

### Status Transition UI + Route (ORD-08)
- Route: `POST /admin/orders/<int:order_id>/status` → `admin.update_order_status(order_id)`. CSRF (Flask-WTF toàn app) — dùng form nhỏ hoặc hidden `next_status` field + CSRF token.
- Cách hiển thị: trên trang chi tiết đơn, hiện nút "Chuyển sang: <trạng thái kế tiếp>" (hoặc dropdown các trạng thái hợp lệ theo transition map). Mỗi nút là form POST riêng (CSRF-safe). UI-SPEC sẽ chốt visual.
- Server validate: `next_status` phải nằm trong transition map của status hiện tại → hợp lệ thì set `order.status = next_status` + commit + flash success + redirect về detail; không hợp lệ → flash error + redirect, không đổi DB.
- Có thể dùng form: `OrderStatusForm` (SelectField hoặc 1 nút submit) — để UI-phase/planner chốt.

### UI-SPEC
- Phase 7 có UI hint: yes → phải có `07-UI-SPEC.md` trước khi plan (gate).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/admin.py` — admin_bp (`/admin`), `_protect_admin` `@login_required` trước mọi route, `admin.products()` pattern pagination (`paginate(page=page, per_page=20, error_out=False)`), flash patterns tiếng Việt, `db.session.get(Model, id)` lookup pattern
- `app/models.py` — `Order` (id, customer_name/phone/address/note, status default 'Chờ xác nhận', created_at/updated_at utcnow, `items` relationship lazy='dynamic'), `OrderItem` (order_id FK CASCADE, product_id FK SET NULL nullable, product_name/product_price snapshot, product_cost_price nullable, quantity CheckConstraint ≥1, product relationship)
- `app/templates/admin/` — dashboard.html + products/list.html + form.html + delete.html — KHÔNG có base admin layout riêng (dùng chung base.html)
- `app/templates/base.html` — flash-zone, nav chung (xem nav hiện có để thêm link "Đơn hàng")
- Pagination render: xem `admin/products/list.html` cách render `pagination.items` + page links
- Flask-WTF CSRF toàn app (mọi POST cần token)
- `format_price` — helper public (dùng lại cho tổng tiền)
- `app/public.py` checkout đã tạo Order + OrderItem với status mặc định — data thật sẽ vào DB sau operator `flask --app app init-db` (hiện data/app.db vẫn v1.0, chưa có bảng)

### Established Patterns
- Route admin: `@admin_bp.route(...)` + `@login_required` (qua before_request), `db.session.get`, flash + redirect
- Pagination: `Model.query.order_by(...).paginate(page=page, per_page=N, error_out=False)`
- Form: FlaskForm + validators tiếng Việt; CSRF bật
- Timestamps: `created_at`/`updated_at` datetime

### Integration Points
- `app/admin.py` — thêm 3 routes: orders (GET list), order_detail (GET detail), update_order_status (POST status)
- `app/forms.py` — OrderStatusForm (nếu cần)
- `app/templates/admin/orders/list.html` + `detail.html` — 2 template mới
- `app/templates/base.html` hoặc `_nav.html` — thêm link "Đơn hàng" vào nav admin (kiểm tra cách nav admin render hiện tại)
- `app/static/css/style.css` — CSS cho order list/detail (admin style sẵn có)

</code_context>

<specifics>
## Specific Ideas

- Tổng tiền đơn dùng `format_price` (đã có) — hiển thị VND.
- Detail page hiện status hiện tại rõ ràng + nút transition hợp lệ theo map.
- Forward-only có thể hiện bằng progress indicator (Chờ xác nhận → Đã gói → Đã gửi → Đã nhận) với trạng thái hiện tại được highlight — UI-SPEC sẽ quyết.
- Nếu rẻ: count badge mỗi status trên list (optional, không bắt buộc).

</specifics>

<deferred>
## Deferred Ideas

- Thông báo đơn mới cho admin (ORD-11 → v2)
- Tự động trừ tồn kho khi xác nhận (ORD-12 → v2)
- Thêm cột total vào orders (không cần — sum items là nguồn truth)
- Export đơn CSV
- Chuyển trạng thái hàng loạt (bulk) — chưa cần
- Hiện cost_price trên detail admin (defer — chỉ Phase 8 stats cần; nếu planner thấy rẻ và giữ trong vùng login thì có thể thêm nhưng mặc định KHÔNG)

</deferred>
