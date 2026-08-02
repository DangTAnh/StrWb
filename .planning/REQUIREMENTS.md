# Requirements: StoreWeb

**Defined:** 2026-08-02
**Core Value:** Khách xem được list hàng rõ ràng (ảnh + giá + trạng thái) và admin dễ dàng quản lý sản phẩm.

## v1.1 Requirements

Requirements for milestone v1.1 Buy System. Each maps to roadmap phases.

### Đặt hàng

- [ ] **ORD-01**: Khách đặt hàng qua form trên trang chi tiết (tên, SĐT, địa chỉ, số lượng, ghi chú) — thay nút "Mua qua Messenger"
- [ ] **ORD-02**: Form yêu cầu bắt buộc tên, SĐT, địa chỉ; số lượng ≥ 1 và ≤ tồn kho
- [ ] **ORD-03**: Khách thấy thông báo thành công sau khi đặt; form không hiện khi sản phẩm hết hàng/ngừng bán
- [ ] **ORD-04**: Mỗi đơn = 1 sản phẩm, lưu snapshot tên sản phẩm + giá bán + giá nhập tại thời điểm đặt
- [ ] **ORD-05**: Form công khai có CSRF + chống spam cơ bản

### Theo dõi đơn — Admin

- [ ] **ORD-06**: Admin xem danh sách đơn (phân trang, lọc theo trạng thái)
- [ ] **ORD-07**: Admin xem chi tiết đơn (thông tin khách, sản phẩm, số lượng, giá, ghi chú, thời gian)
- [ ] **ORD-08**: Admin cập nhật trạng thái đơn: Chờ xác nhận → Đã gói → Đã gửi → Đã nhận (+ Đã hủy, chỉ admin)
- [ ] **ORD-09**: Trạng thái đơn chỉ tiến về trước, không cho lùi

### Giá nhập

- [ ] **COST-01**: Admin nhập giá nhập tùy chọn (chỉ admin thấy) cho sản phẩm
- [ ] **COST-02**: Giá nhập không bao giờ hiển thị cho khách

### Thống kê

- [ ] **STAT-01**: Admin xem tổng doanh thu (chỉ tính đơn Đã gửi + Đã nhận)
- [ ] **STAT-02**: Admin xem lợi nhuận = doanh thu − giá nhập (đơn đã gửi/nhận, xử lý NULL)
- [ ] **STAT-03**: Admin xem số đơn theo trạng thái + tổng sản phẩm đã bán
- [ ] **STAT-04**: Admin xem số sản phẩm trong kho (tổng, hết hàng, ngừng bán)

### Nền tảng

- [ ] **PLAT-05**: Migration an toàn cho DB cũ — thêm cột `cost_price` + bảng `orders` (idempotent, không mất dữ liệu)

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Đặt hàng nâng cao

- **ORD-10**: Giỏ hàng nhiều sản phẩm trong một đơn (refactor Order → Order + OrderItem)
- **ORD-11**: Thông báo đơn mới cho admin (in-app / email)
- **ORD-12**: Tự động trừ tồn kho khi đơn được xác nhận

### Thống kê nâng cao

- **STAT-05**: Lọc thống kê theo khoảng ngày
- **STAT-06**: Export báo cáo CSV
- **STAT-07**: Bảng lợi nhuận theo từng sản phẩm

## Out of Scope

| Feature | Reason |
|---------|--------|
| Thanh toán online (MoMo/VNPay/card) | Giao dịch thanh toán khi giao hàng, ngoài luồng web |
| Tài khoản khách hàng | Đặt hàng ẩn danh đủ cho quy mô hiện tại |
| Phân loại / danh mục sản phẩm | Catalog phẳng (giữ nguyên v1.0) |
| Đăng ký admin / OAuth / multi-role | Một tài khoản admin duy nhất |
| SMS/email xác nhận đơn cho khách | Không hạ tầng; admin liên hệ qua SĐT |
| Xóa đơn (hard delete) | Stats cộng dồn — chỉ chuyển trạng thái "Đã hủy" |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ORD-01 | 6 | Pending |
| ORD-02 | 6 | Pending |
| ORD-03 | 6 | Pending |
| ORD-04 | 5 | Pending |
| ORD-05 | 6 | Pending |
| ORD-06 | 7 | Pending |
| ORD-07 | 7 | Pending |
| ORD-08 | 7 | Pending |
| ORD-09 | 7 | Pending |
| COST-01 | 5 | Pending |
| COST-02 | 5 | Pending |
| STAT-01 | 8 | Pending |
| STAT-02 | 8 | Pending |
| STAT-03 | 8 | Pending |
| STAT-04 | 8 | Pending |
| PLAT-05 | 5 | Pending |

**Coverage:**
- v1.1 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0 ✓

---
*Requirements defined: 2026-08-02*
*Last updated: 2026-08-02 after initial definition*
