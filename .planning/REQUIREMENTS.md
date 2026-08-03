# Requirements: StoreWeb

**Defined:** 2026-08-03
**Core Value:** Khách xem được list hàng rõ ràng (ảnh + giá + trạng thái) và admin dễ dàng quản lý sản phẩm.

## v1.2 Requirements

Requirements for milestone v1.2 "Đợt bán (Sale Batches)". Mỗi requirement map vào đúng 1 phase trong roadmap.

### Đợt bán (Admin)

- [ ] **BATCH-01**: Admin tạo đợt bán mới với tên và thứ tự hiển thị
- [ ] **BATCH-02**: Admin sửa tên/thứ tự của đợt bán
- [ ] **BATCH-03**: Admin xóa đợt bán mà không làm mất sản phẩm (chỉ gỡ quan hệ gán)
- [ ] **BATCH-04**: Admin gán sản phẩm vào một hoặc nhiều đợt bán (many-to-many)
- [ ] **BATCH-05**: Admin ẩn/hiện từng đợt bán chỉ với 1 thao tác

### Hiển thị public

- [ ] **BATCH-06**: Trang chủ hiển thị section tương ứng từng đợt bán đang hiện, theo thứ tự sắp xếp
- [ ] **BATCH-07**: Sản phẩm không thuộc ít nhất một đợt đang hiện bị ẩn khỏi public ở mọi đường (trang chủ, tìm kiếm, URL chi tiết, giỏ hàng)

### Hạ tầng

- [ ] **BATCH-08**: Migration thêm bảng đợt bán + bảng gán sản phẩm–đợt, không sửa bảng products, idempotent, không mất dữ liệu

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Đợt bán nâng cao

- **BATCH-09**: Đợt bán có mô tả / ảnh bìa / ngày bắt đầu–kết thúc (drop release đầy đủ)
- **BATCH-10**: Mỗi đợt bán có URL riêng (VD `/dot-ban/<slug>`)
- **BATCH-11**: Hoàn lại tồn kho khi hủy đơn sau khi đã xác nhận (liên quan ORD-12)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Danh mục/phân loại sản phẩm thuần túy (hierarchical category) | User chọn "đợt bán" — grouping phẳng theo đợt + toggle, không phải cây danh mục; v1.0 từng exclude |
| Ảnh bìa / mô tả / thời gian đợt bán | User chọn "chỉ tên đợt" trong questioning v1.2 → deferred BATCH-09 |
| Hiển thị đợt ẩn cho khách dưới dạng preview/draft | Đợt ẩn = không tồn tại với public, không có chế độ xem thử |
| Giao diện khách tự lọc theo đợt (tab/filter) | User chọn hiển thị từng section theo thứ tự, không thêm route/interaction mới |

## Traceability

Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| BATCH-01 | Phase 10 | Pending |
| BATCH-02 | Phase 10 | Pending |
| BATCH-03 | Phase 10 | Pending |
| BATCH-04 | Phase 11 | Pending |
| BATCH-05 | Phase 10 | Pending |
| BATCH-06 | Phase 12 | Pending |
| BATCH-07 | Phase 12 | Pending |
| BATCH-08 | Phase 10 | Pending |

**Coverage:**
- v1.2 requirements: 8 total
- Mapped to phases: 8 ✓
- Unmapped: 0

---
*Requirements defined: 2026-08-03*
*Last updated: 2026-08-03 after roadmap creation*
