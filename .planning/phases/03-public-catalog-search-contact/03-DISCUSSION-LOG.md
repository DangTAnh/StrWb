# Phase 3: Public Catalog + Search + Contact - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-01
**Phase:** 3-Public Catalog + Search + Contact
**Areas discussed:** Trang chủ / danh sách sản phẩm, Trang chi tiết sản phẩm, Tìm kiếm
*(Liên hệ Messenger không được user chọn để thảo luận — dùng mặc định từ Phase 1.)*

---

## Trang chủ / danh sách sản phẩm

| Option | Description | Selected |
|--------|-------------|----------|
| Grid thẻ card | Mỗi sản phẩm 1 thẻ: ảnh + tên + giá + trạng thái. Scan nhanh, đúng kiểu catalog | ✓ |
| Danh sách dạng dòng | Ảnh nhỏ trái, thông tin phải theo dòng. Ít dùng cho catalog công khai | |

**User's choice:** Grid thẻ card
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Responsive 2/3/4 cột | Điện thoại 2, tablet 3, desktop 4 — đa số khách VN dùng mobile | ✓ |
| Cố định 3 cột | Đơn giản nhưng desktop thưa, mobile chật | |

**User's choice:** Responsive 2/3/4 cột
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Phân trang 12/trang | Chia trang cố định, nhẹ, ổn định như admin | ✓ |
| Nút "Xem thêm" | Tải thêm từng đợt, hiện đại nhưng thêm JS | |
| Cuộn hết tất cả | Hiện toàn bộ một trang, đơn giản nhưng nặng | |

**User's choice:** Phân trang 12/trang
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Mờ + nhãn | Ảnh mờ + nhãn "Hết hàng"/"Ngừng bán" — khách nhìn rõ, không nhầm với hàng còn | ✓ |
| Nhãn thường | Chỉ thêm nhãn nhỏ, ảnh không đổi | |
| Ẩn ngừng bán | Không hiện sản phẩm ngừng bán trên danh sách | |

**User's choice:** Mờ + nhãn
**Notes:** CAT-04 (hiển thị khác đi không lấn át) thuộc Phase 4 — D-04 này là nền tảng cho nó.

---

## Trang chi tiết sản phẩm

| Option | Description | Selected |
|--------|-------------|----------|
| Ảnh trái - thông tin phải | Desktop: ảnh chính + thumbnail trái, thông tin phải. Mobile: stack | ✓ |
| Ảnh trên - thông tin dưới | Ảnh lớn trên cùng, thông tin dưới trên mọi màn hình | |

**User's choice:** Ảnh trái - thông tin phải
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Thumbnail đổi ảnh chính | Ảnh chính lớn + dãy thumbnail, bấm để đổi — chuẩn e-commerce | ✓ |
| Chỉ ảnh chính | Không có thumbnail chuyển đổi, dựa trên ảnh đầu = ảnh chính | |

**User's choice:** Thumbnail đổi ảnh chính
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Nút Messenger + nhãn hết hàng | Vẫn hiện "Mua qua Messenger" để khách hỏi + dòng "Hết hàng" đỏ rõ | ✓ |
| Ẩn nút, chỉ nhãn | Khách không bấm nhầm nhưng mất cơ hội hỏi | |

**User's choice:** Nút Messenger + nhãn hết hàng
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Giá nổi bật ngay | Tên → giá → trạng thái → thương hiệu → số đo → mô tả | ✓ |
| Giá để cuối | Tên → thương hiệu → số đo → mô tả → giá → trạng thái | |

**User's choice:** Giá nổi bật ngay
**Notes:** —

---

## Tìm kiếm

| Option | Description | Selected |
|--------|-------------|----------|
| Trên header | Ô tìm trong header trang chủ, luôn thấy khi vào web | ✓ |
| Trong trang chủ | Chỉ trên trang chủ, phía trên danh sách | |

**User's choice:** Trên header
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Submit → trang kết quả | GET form → trang kết quả riêng, dùng chung grid — đơn giản | ✓ |
| Live search (AJAX) | Gõ đến đâu hiện đến đó — nhanh hơn nhưng thêm JS | |

**User's choice:** Submit → trang kết quả
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Tìm không dấu | "ao" vẫn tìm ra "áo" (chuẩn hóa bỏ dấu khi so sánh) | ✓ |
| Khớp chính xác | Chỉ khớp đúng có dấu như nhập | |

**User's choice:** Tìm không dấu
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Dùng chung grid | Kết quả cùng layout grid card + dòng "N sản phẩm cho 'từ khóa'". Trống → báo không tìm thấy | ✓ |
| Layout riêng | Khác layout cho trang kết quả | |

**User's choice:** Dùng chung grid
**Notes:** —

---

## Liên hệ Messenger (không thảo luận — mặc định)

User không chọn vùng này. Dùng mặc định từ Phase 1 (config `MESSENGER_URL` đã có):
- Trang chủ: giữ nút/liên kết Messenger (đã có trong coming-soon, chuyển sang giao diện catalog).
- Trang chi tiết: nút "Mua qua Messenger" gần giá/trạng thái.
- Đáp ứng CONT-01, CONT-02.

---

## Claude's Discretion

Chi tiết kỹ thuật bàn giao cho researcher/planner: số cột + breakpoint chính xác (480/768/1200), kích thước ảnh hiển thị trên grid + detail, URL cấu trúc (`/products/<id>`, `/search?q=`), cơ chế chuẩn hóa tiếng Việt không dấu (unicodedata NFD + strip marks + lowercase), empty state tìm kiếm, cấu trúc template public (kế thừa base.html).

## Deferred Ideas

- **Live search AJAX** — user chọn submit → trang kết quả (D-10). Không thêm vào Phase 3.
- **CAT-04 / CAT-06** — thuộc Phase 4 (Polish + Deploy): hiển thị khác đi đầy đủ + responsive hoàn thiện.
