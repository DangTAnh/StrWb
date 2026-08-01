# Phase 3: Public Catalog + Search + Contact — Context

**Gathered:** 2026-08-01
**Status:** Ready for UI-SPEC (frontend phase — UI hint: yes)

## Phase Boundary

Khách vào web không cần đăng nhập: xem danh sách sản phẩm (grid thẻ card, phân trang), xem trang chi tiết (ảnh gallery + giá + trạng thái + thương hiệu + số đo + mô tả), tìm kiếm theo tên/mô tả, và liên hệ mua qua Messenger. Thay trang "Cửa hàng đang chuẩn bị" (Phase 1) bằng catalog thật.

Phân trang admin, quản lý ảnh, CRUD (Phase 2), responsive hoàn thiện (CAT-06, Phase 4), hiển thị khác đi cho hết hàng/ngừng bán đầy đủ (CAT-04, Phase 4) **không** nằm trong phase này — chỉ có catalog công khai + tìm kiếm + liên hệ.

## Implementation Decisions

### Trang chủ / danh sách sản phẩm (Public Product List)
- **D-01:** Trang chủ hiển thị sản phẩm dạng **grid thẻ card** — mỗi thẻ: ảnh, tên, giá, trạng thái.
- **D-02:** Grid **responsive 2/3/4 cột** — mobile 2 cột, tablet 3 cột, desktop 4 cột (breakpoint theo design system 480/768/1200).
- **D-03:** **Phân trang 12 sản phẩm/trang** (sắp theo `sort_order` như admin, Phase 2 D-02).
- **D-04:** Sản phẩm hết hàng / ngừng bán trên grid: **ảnh mờ + nhãn** "Hết hàng" / "Ngừng bán" — khách nhìn rõ, không lấn át hàng còn. (Nền tảng cho CAT-04 Phase 4.)

### Trang chi tiết sản phẩm (Product Detail)
- **D-05:** Bố cục **ảnh trái - thông tin phải** (desktop); mobile stack ảnh trên, thông tin dưới.
- **D-06:** Gallery: **ảnh chính lớn + dãy thumbnail nhỏ**, click thumbnail để đổi ảnh chính. Ảnh đầu = ảnh chính (thừa kế Phase 2 D-12).
- **D-07:** Sản phẩm hết hàng trên detail: **vẫn hiện nút "Mua qua Messenger"** để khách hỏi, kèm **dòng "Hết hàng" đỏ rõ ràng**.
- **D-08:** Thứ tự thông tin: **tên → giá → trạng thái → thương hiệu → số đo → mô tả** (giá nổi bật ngay trên).

### Tìm kiếm (Search)
- **D-09:** Ô tìm kiếm đặt **trên header** trang chủ.
- **D-10:** Cơ chế **GET form submit → trang kết quả riêng** (không live search AJAX).
- **D-11:** **Tìm không dấu tiếng Việt** — chuẩn hóa bỏ dấu (NFD + strip combining marks + lowercase) khi so sánh tên/mô tả, nên "ao" tìm ra "áo".
- **D-12:** Kết quả **dùng chung grid** layout card + dòng "N sản phẩm cho '{từ khóa}'". Không có kết quả → thông báo "Không tìm thấy sản phẩm".

### Liên hệ Messenger (Contact)
- **D-13:** **Nút Messenger dễ thấy trên trang chủ + trang chi tiết** (CONT-01, CONT-02). Dùng `MESSENGER_URL` từ config Phase 1. Trang chủ giữ nút/liên kết Messenger; trang chi tiết có nút "Mua qua Messenger" gần giá/trạng thái (xem D-07).

### Claude's Discretion
Các chi tiết kỹ thuật bàn giao cho researcher/planner: số cột + breakpoint chính xác, kích thước ảnh hiển thị grid + detail (dùng thumbnail 400px có sẵn hay cần thêm), URL cấu trúc (`/products/<id>`, `/search?q=`), cơ chế chuẩn hóa tiếng Việt không dấu (Python `unicodedata` NFD + strip combining marks + lowercase, áp lên cả từ khóa và tên/mô tả), empty state tìm kiếm, cấu trúc template public (kế thừa `base.html`).

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Definition & Requirements
- `.planning/ROADMAP.md` §"Phase 3: Public Catalog + Search + Contact" — goal, 5 success criteria, mode mvp, requirement mapping
- `.planning/REQUIREMENTS.md` §"Catalog công khai" (CAT-01..03, 05) + §"Tìm kiếm" (SRCH-01) + §"Liên hệ" (CONT-01, 02)

### Prior Phase Decisions & Design System
- `.planning/phases/01-scaffold-auth-data-model/01-CONTEXT.md` — Product model (fields, status tự suy từ quantity + discontinued), MESSENGER_URL config, pattern Phase 1
- `.planning/phases/01-scaffold-auth-data-model/01-UI-SPEC.md` — design system baseline (màu #2563EB/#F9FAFB, type 14/16/24/32, spacing 4/8/16/24/32/48/64, breakpoint 480/768/1200)
- `.planning/phases/02-admin-crud-images/02-CONTEXT.md` — D-02 sort_order, D-12 ảnh đầu = ảnh chính, D-13 sắp xếp ảnh
- `.planning/phases/02-admin-crud-images/02-UI-SPEC.md` — extensions Phase 2 (badge, button, gallery pattern)
- `CLAUDE.md` — tech stack + What NOT to Use

### Research & Pitfalls
- `.planning/research/SUMMARY.md` + `.planning/research/PITFALLS.md` — kiến trúc 3 blueprint (public route), pattern hiển thị catalog, UX pitfalls (empty state, price format, placeholder ảnh)

## Existing Code Insights

### Reusable Assets
- `app/public.py` — blueprint public + route `/` (đang render coming-soon — sẽ thay bằng catalog)
- `app/templates/public/index.html` — coming-soon (thay bằng danh sách sản phẩm)
- `app/models.py` — Product + ProductImage đã có (fields, status, sort_order, images quan hệ)
- `app/image_utils.py` — thumbnail 400px đã sinh sẵn khi upload (dùng cho grid/detail)
- `app/templates/base.html` — nav + footer + flash zone (thêm ô tìm kiếm vào nav)
- config `MESSENGER_URL` — đã có từ Phase 1

### Established Patterns
- 3 blueprints (public/admin/auth), Flask-Login (public KHÔNG cần login), template kế thừa `base.html`, giao diện tiếng Việt `lang="vi"` + utf-8, design system Phase 1 + Phase 2 extensions.

### Integration Points
- `app/public.py` — thay route `/` (catalog list + phân trang) + thêm `/products/<id>` (detail) + `/search` (tìm kiếm)
- `app/templates/public/` — index.html (grid), product_detail.html (mới), search_results.html (mới hoặc chung)
- `app/templates/base.html` — thêm form tìm kiếm vào header/nav
- `app/static/css/style.css` — thêm style grid card, gallery detail, badge hết hàng, search

## Specific Ideas

Không có yêu cầu "làm giống X" từ thảo luận — mở cho cách tiếp cận chuẩn (standard approaches). User chọn "theo chuẩn e-commerce" cho gallery thumbnail (D-06) và "tìm không dấu" cho search (D-11).

## Deferred Ideas

- **Live search AJAX** — user chọn submit → trang kết quả (D-10). Không thêm vào Phase 3.
- **CAT-04** (hiển thị khác đi cho hết hàng/ngừng bán hoàn thiện) + **CAT-06** (responsive) — thuộc Phase 4 (Polish + Deploy). D-04 là nền tảng.

---

*Phase: 3-Public Catalog + Search + Contact*
*Context gathered: 2026-08-01*
