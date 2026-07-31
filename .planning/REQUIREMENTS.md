# Requirements: StoreWeb

**Defined:** 2026-07-31
**Core Value:** Khách xem được list hàng rõ ràng (ảnh + giá + trạng thái) và admin dễ dàng quản lý sản phẩm.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Quản trị (Admin Auth)

- [ ] **AUTH-01**: Admin đăng nhập bằng tài khoản duy nhất (username + mật khẩu đã băm)
- [ ] **AUTH-02**: Phiên đăng nhập admin duy trì qua nhiều request (Flask-Login)
- [ ] **AUTH-03**: Admin đăng xuất được
- [ ] **AUTH-04**: Mọi trang quản trị bị chặn nếu chưa đăng nhập

### Quản lý sản phẩm (Admin CRUD)

- [ ] **PROD-01**: Admin tạo sản phẩm mới với tên, giá, thương hiệu, số đo, mô tả
- [ ] **PROD-02**: Admin sửa mọi thông tin sản phẩm
- [ ] **PROD-03**: Admin xóa sản phẩm (qua POST để an toàn CSRF)
- [ ] **PROD-04**: Admin đặt trạng thái Còn hàng / Hết hàng / Ngừng bán
- [ ] **PROD-05**: Admin nhập số lượng tồn kho; sản phẩm tồn = 0 tự xem là hết hàng
- [ ] **PROD-06**: Giá lưu dạng số nguyên (VND), không mất chính xác
- [ ] **PROD-07**: Form admin có CSRF protection và validate dữ liệu

### Ảnh sản phẩm

- [ ] **IMG-01**: Admin upload ảnh sản phẩm, được validate (magic bytes, kích thước, giới hạn dung lượng)
- [ ] **IMG-02**: Ảnh lưu trên filesystem với tên file UUID (không mất ký tự tiếng Việt)
- [ ] **IMG-03**: Mỗi sản phẩm hỗ trợ nhiều ảnh (gallery)
- [ ] **IMG-04**: Ảnh được resize tạo thumbnail cho danh sách

### Catalog công khai

- [ ] **CAT-01**: Khách xem danh sách sản phẩm công khai, không cần đăng nhập
- [ ] **CAT-02**: Khách xem trang chi tiết sản phẩm: ảnh, giá, thương hiệu, số đo, mô tả, trạng thái
- [ ] **CAT-03**: Giá + trạng thái còn/hết hiển thị rõ trên trang
- [ ] **CAT-04**: Sản phẩm hết hàng hoặc ngừng bán được hiển thị khác đi (không lấn át hàng còn)
- [ ] **CAT-05**: Trang chi tiết hiển thị gallery nhiều ảnh của sản phẩm
- [ ] **CAT-06**: Giao diện responsive trên mobile (đa số khách VN dùng điện thoại)

### Tìm kiếm

- [ ] **SRCH-01**: Khách tìm kiếm sản phẩm theo tên/mô tả

### Liên hệ

- [ ] **CONT-01**: Trang/dải liên hệ hiển thị link Messenger của người bán
- [ ] **CONT-02**: Link Messenger dễ thấy trên trang chủ và trang chi tiết

### Nền tảng & Ngôn ngữ

- [ ] **PLAT-01**: Giao diện toàn tiếng Việt, `lang="vi"` + charset utf-8
- [ ] **PLAT-02**: SECRET_KEY từ môi trường (không hardcode, không debug=True trong production)
- [ ] **PLAT-03**: SQLite dùng WAL mode + busy_timeout tránh lỗi database locked
- [ ] **PLAT-04**: Có script/CLI khởi tạo database và tạo tài khoản admin đầu tiên

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Catalog nâng cao

- **CATV-01**: Lọc/sort theo giá, thương hiệu, trạng thái
- **CATV-02**: Sitemap.xml cho SEO
- **CATV-03**: Chế độ tối (dark mode)

### Quản trị nâng cao

- **PRODV-01**: Toggle tồn kho nhanh ngay trên danh sách
- **PRODV-02**: Đếm lượt xem/lượt bán (social proof)
- **PRODV-03**: Link WhatsApp bên cạnh Messenger

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Giỏ hàng | Giao dịch qua Messenger, không có cart |
| Thanh toán online | Giao dịch qua Messenger, tránh PCI scope |
| Tài khoản khách hàng | Chỉ admin; khách không cần đăng nhập |
| Phân loại / danh mục sản phẩm | Người dùng yêu cầu không cần |
| OAuth / đăng ký admin mới | Một tài khoản duy nhất |
| Multi-vendor / multi-store | Một người bán duy nhất |
| Đánh giá / bình luận (UGC) | Chưa cần cho v1 |
| Wishlist / yêu thích | Ngoài phạm vi |
| Tự trừ tồn kho khi bán | Giao dịch ngoài web, admin tự quản lý |
| Notifications thời gian thực | Ngoài phạm vi |
| Đa ngôn ngữ | Chỉ tiếng Việt |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 |  | Pending |
| AUTH-02 |  | Pending |
| AUTH-03 |  | Pending |
| AUTH-04 |  | Pending |
| PROD-01 |  | Pending |
| PROD-02 |  | Pending |
| PROD-03 |  | Pending |
| PROD-04 |  | Pending |
| PROD-05 |  | Pending |
| PROD-06 |  | Pending |
| PROD-07 |  | Pending |
| IMG-01 |  | Pending |
| IMG-02 |  | Pending |
| IMG-03 |  | Pending |
| IMG-04 |  | Pending |
| CAT-01 |  | Pending |
| CAT-02 |  | Pending |
| CAT-03 |  | Pending |
| CAT-04 |  | Pending |
| CAT-05 |  | Pending |
| CAT-06 |  | Pending |
| SRCH-01 |  | Pending |
| CONT-01 |  | Pending |
| CONT-02 |  | Pending |
| PLAT-01 |  | Pending |
| PLAT-02 |  | Pending |
| PLAT-03 |  | Pending |
| PLAT-04 |  | Pending |

**Coverage:**
- v1 requirements: 28 total
- Mapped to phases: 0
- Unmapped: 28 ⚠️

---
*Requirements defined: 2026-07-31*
*Last updated: 2026-07-31 after initial definition*
