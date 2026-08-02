# Phase 5: Data Model + Migration - Context

**Gathered:** 2026-08-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Order model (snapshot price/cost/name) + `cost_price` column on Product + safe idempotent migration for existing SQLite DBs + cost price field on admin product form. Covers ORD-04, COST-01, COST-02, PLAT-05.
</domain>

<decisions>
## Implementation Decisions

### Order Model Shape
- Order giữ `product_id` FK nullable + snapshot đầy đủ (tên sản phẩm, giá bán, giá nhập, số lượng) tại thời điểm đặt — xóa sản phẩm không mất đơn, admin xem được sản phẩm gốc (ORD-04)
- Trạng thái đơn lưu String nhãn VN trực tiếp ("Chờ xác nhận" → "Đã gói" → "Đã gửi" → "Đã nhận" + "Đã hủy") — đơn giản, khớp UI
- Số hiệu đơn = ID tăng dần (không mã định dạng)

### Cost Price
- Cột `cost_price` Integer nullable, đơn vị VND (khớp quyết định D-05 không Float) (COST-01)
- Field giá nhập tùy chọn trên admin form, chỉ admin thấy (COST-02)

### Migration
- Mở rộng CLI `init-db`: guard `PRAGMA table_info` trước ALTER — idempotent, giữ pattern CLI hiện tại (PLAT-05)
- `create_all` tạo bảng mới (orders); ALTER thêm cột có guard — 1 đường code cho cả fresh DB và DB cũ

### Claude's Discretion
- Chi tiết validation field, thứ tự cột, index, backref naming do Claude tự chọn theo convention codebase hiện tại

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/models.py` — Product, ProductImage, AdminUser với pattern utcnow(), snake_case tablename
- `app/forms.py` — ProductForm: Optional IntegerField pattern (admin_note, sku)
- `app/db.py` — SQLAlchemy + init-db CLI command
- `app/admin.py` — admin product CRUD routes, ProductForm(obj=product)

### Established Patterns
- Integer VND cho tiền, không Float (D-05)
- Timestamps: created_at/updated_at dùng utcnow()
- SQLite WAL + busy_timeout qua event listener
- Flask-WTF + CSRF trên admin forms

### Integration Points
- `app/models.py` — thêm Order model + cost_price column
- `app/forms.py` — thêm cost_price field
- `app/admin.py` — product form nhận cost_price
- `app/db.py` — migration guard

</code_context>

<specifics>
## Specific Ideas

- Order là model mới độc lập (Phase 5 tạo bảng), route đặt hàng thuộc Phase 6
- Status forward-only enforcement thuộc Phase 7, Phase 5 chỉ định nghĩa column

</specifics>

<deferred>
## Deferred Ideas

- Giỏ hàng nhiều sản phẩm (ORD-10 → v2: refactor Order → Order + OrderItem)
- Tự động trừ tồn kho khi xác nhận (ORD-12 → v2)

</deferred>
