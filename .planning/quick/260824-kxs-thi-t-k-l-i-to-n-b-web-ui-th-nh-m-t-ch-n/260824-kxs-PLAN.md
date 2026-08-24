---
phase: quick-260824-kxs
plan: 01
type: execute
wave: 1
depends_on: []
autonomous: true
requirements: [D-01-FULL-REDESIGN, D-02-REMOVE-TAILWIND, D-03-KEEP-WIP]
user_setup: []
files_modified:
  - app/static/css/style.css
  - app/static/css/input.css
  - app/templates/base.html
  - app/templates/public/base.html
  - app/templates/public/index.html
  - app/templates/public/product_detail.html
  - app/templates/public/cart.html
  - app/templates/public/search.html
  - app/templates/public/_nav.html
  - app/templates/public/_product_card.html
  - app/templates/public/_checkout_form.html
  - app/templates/public/_search_results.html
  - app/templates/_admin_nav.html
  - app/templates/_pagination.html
  - app/templates/auth/login.html
  - app/templates/errors/404.html
  - app/templates/errors/500.html
  - app/templates/admin/base.html
  - app/templates/admin/stats.html
  - app/templates/admin/categories/list.html
  - app/templates/admin/products/list.html
  - app/templates/admin/products/form.html
  - app/templates/admin/products/delete.html
  - app/templates/admin/orders/list.html
  - app/templates/admin/orders/detail.html
  - app/templates/admin/orders/_content.html
  - app/templates/admin/orders/delete.html
must_haves:
  truths:
    - "Không còn bất kỳ utility/class Tailwind nào trong toàn bộ app/templates/ và app/static/css/"
    - "Toàn bộ giao diện được định nghĩa bởi MỘT file CSS thuần tự viết theo hệ thống token + component class ngữ nghĩa"
    - "Bộ màu + font + spacing là thiết kế MỚI, khác rõ rệt bản cũ; font Google hỗ trợ tiếng Việt đầy đủ"
    - "Mọi trang render không lỗi: public (trang chủ, chi tiết, giỏ, tìm kiếm), auth, admin, trang lỗi"
    - "Hành vi JS giữ nguyên 100%: toast, skip-link, tìm kiếm AJAX, gallery ảnh form sản phẩm, collapse form"
  artifacts:
    - path: "app/static/css/style.css"
      provides: "Design system thuần: tokens (:root) + reset + component classes"
      min_lines: 400
    - path: "app/static/css/input.css"
      provides: "DELETED — không tồn tại sau khi hoàn thành"
    - path: "app/templates/**"
      provides: "25 templates dùng duy nhất class ngữ nghĩa, không còn utility Tailwind"
  key_links:
    - from: "app/templates/base.html"
      to: "css/style.css"
      via: "url_for('static', filename='css/style.css') — điểm wire CSS DUY NHẤT của app"
      pattern: "css/style\\.css"
    - from: "app/templates/*"
      to: "component classes trong style.css"
      via: "class attribute"
      pattern: "class=\"(btn|card|table|input|badge|toast|nav|pagination)"
    - from: "app/static/js/search-ajax.js"
      to: "DOM templates"
      via: "querySelector('.search-form' | '.product-grid' | '.search-results' | '.pagination')"
      pattern: "\\.(search-form|product-grid|search-results|pagination)"
    - from: "app/static/js/form-gallery.js"
      to: "DOM templates + CSS"
      via: "className gán trực tiếp 'gallery-item', 'badge-primary', 'reorder-btn', 'delete-btn', 'gallery-actions', 'paste-received'"
      pattern: "(gallery-item|badge-primary|reorder-btn|delete-btn|paste-received)"
    - from: "base.html window.showToast()"
      to: "style.css"
      via: "class toast/toast-success/toast-error/toast-info/show/hide"
      pattern: "\\.toast(-success|-error|-info)?(\\.|\\s|,|\\{)"
---

<objective>
Thiết kế lại toàn bộ web UI thành một chỉnh thể thống nhất: thay 2 file Tailwind (input.css 27KB + style.css compiled 79KB) bằng MỘT file CSS thuần tự viết theo hệ thống token + component class, và viết lại class attribute của cả 25 templates từ utility Tailwind sang class ngữ nghĩa.

Purpose: Loại bỏ phụ thuộc Tailwind triệt để (per D-02), có bộ nhận diện mới hoàn toàn phù hợp web bán hàng thời trang tiếng Việt (per D-01), làm việc trên trạng thái WIP hiện tại không stash/revert (per D-03).
Output: `app/static/css/style.css` (mới, thuần), 25 templates sạch Tailwind, `app/static/css/input.css` bị xóa. JS KHÔNG phải sửa — đã grep xác minh cả 3 file JS chỉ dùng class ngữ nghĩa (.search-form, .product-grid, .gallery-item...) nên CSS mới BẮT BUỘC định nghĩa style cho các class này.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md

Codebase facts (đã verify khi lập plan):
- CSS được load tại ĐÚNG MỘT chỗ: `app/templates/base.html` dòng 10 qua `url_for('static', filename='css/style.css')`. Giữ tên file `style.css` => không phải sửa link. `admin/base.html`, `public/base.html` không tự load CSS riêng.
- Font hiện tại: Noto Sans VN (base.html dòng 9). Đổi thành Be Vietnam Pro (weights 400;500;600;700) hoặc font Google tương đương hỗ trợ tiếng Việt đầy đủ.
- JS contracts (tên class PHẢI còn tồn tại ở DOM và có style):
  - `search-ajax.js`: `.search-form`, `.product-grid`, `.search-results`, `.pagination`, `input[name="q"]`
  - `form-gallery.js`: gán trực tiếp className `gallery-item`, `badge-primary`, `reorder-btn`, `delete-btn`, `gallery-actions`; toggle `paste-received` (hiệu ứng flash khi paste ảnh — cần animation/transition)
  - `base.html` toast helper (giữ nguyên JS): `toast`, `toast-success`, `toast-error`, `toast-info`, `show`, `hide` + transition trên `#toast-container`
  - `skip-link`: cần trạng thái focus hiển thị (thay thế utility `absolute left-[-9999px] focus:left-0`)
- Route/render Python KHÔNG chứa class CSS — chỉ templates + static.
- Working tree đang có WIP người dùng (app/admin.py, db.py, forms.py, models.py, xlsx files, admin/orders/list.html, detail.html). Per D-03: KHÔNG stash, KHÔNG revert — làm đè lên, commit trộn WIP trong 2 file orders trùng là chấp nhận được. KHÔNG đụng vào các file WIP ngoài phạm vi UI (admin.py, db.py, forms.py, models.py, *.xlsx).
</context>

<tasks>

<task type="auto">
  <name>Task 1: Viết design system CSS mới + wire base.html + xóa Tailwind assets</name>
  <files>app/static/css/style.css, app/templates/base.html, app/static/css/input.css (xóa)</files>
  <action>
XÓA `app/static/css/input.css`. GHI ĐÈ `app/static/css/style.css` bằng CSS thuần tự viết hoàn toàn (không @tailwind, không @theme, không build step). LƯU Ý: chữ "tailwind" không được xuất hiện trong file CSS hay template nào (gate verify grep case-insensitive).

Cấu trúc file CSS:
1. Header comment ngắn mô tả design system (không nhắc tên Tailwind).
2. Tokens `:root`: bảng màu trung tính ấm + 1 accent (chọn giá trị cụ thể, khác hẳn palette cũ) — `--color-bg`, `--color-surface`, `--color-text`, `--color-text-muted`, `--color-border`, `--color-accent`, `--color-accent-hover`, `--color-danger`, `--color-success`; spacing scale `--space-1..8` (base 4px); type scale `--text-xs..2xl`; `--font-sans`; `--radius-sm/md/lg`; `--shadow-sm/md`.
3. Reset/base tối giản: box-sizing, margin 0, font-family body, img max-width.
4. Layout: `.container` (max-width + padding ngang responsive), header/nav `.site-header`, `.site-nav`, footer.
5. Components (bắt buộc đủ theo inventory dưới): `.btn` + `.btn-primary/.btn-secondary/.btn-danger` (+ size nhỏ nếu cần), `.card`, `.table` (kèm wrapper/table-responsive nếu cart/admin table cần cuộn ngang mobile), `.form-group`, `.label`, `.input`, `.select`, `.textarea`, `.badge` + `.badge-primary` (JS contract) + badge trạng thái còn/hết hàng (vd `.badge-in-stock`, `.badge-out-of-stock` — đặt tên rồi dùng nhất quán ở Task 2/3), `.alert` + `.alert-success/.alert-error`, `.toast` + `.toast-success/.toast-error/.toast-info` + state `.show/.hide` với transition (giữ cơ chế force-reflow + transitionend của toast helper), `.pagination`, `.product-grid` (grid responsive: 2 cột mobile -> 4 cột desktop), `.search-form`, `.search-results`, `.skip-link` (ẩn off-screen, hiện khi :focus), gallery form sản phẩm: `.gallery-item`, `.gallery-actions`, `.reorder-btn`, `.delete-btn`, hiệu ứng `.paste-received` (outline/flash ngắn), `.modal` CHỈ nếu grep thấy markup modal sẵn trong templates (nếu không có thì bỏ qua, đừng viết cho có).
6. Utilities cục bộ tối đa ~5 cái thực sự lặp lại nhiều nơi (vd `.text-center`) — đây KHÔNG phải tái tạo Tailwind, chỉ những gì templates đang cần sau khi viết lại.

Sửa `app/templates/base.html`: đổi Google Fonts link sang Be Vietnam Pro `family=Be+Vietnam+Pro:wght@400;500;600;700` (giữ preconnect); đổi `body class="font-sans text-text bg-bg"` thành class ngữ nghĩa mới (hoặc bỏ hẳn nếu body style qua element selector); đổi footer/utility classes (`container mx-auto px-4 py-8 text-center text-sm text-text-muted`) thành class ngữ nghĩa; GIỮ NGUYÊN toàn bộ script toast + flashed-toasts + aria-live container.

Đây là "contract" cho Task 2/3: nếu trong lúc viết templates cần thêm component/biến thể, QUAY LẠI bổ sung vào style.css (một file duy nhất, không tạo file CSS thứ hai).
  </action>
  <verify>
    <automated>test ! -f app/static/css/input.css && ! grep -riE "tailwind|@tailwind|@theme" app/static/css/ && wc -l app/static/css/style.css | awk '$1 >= 400 {exit 0} {exit 1}' && grep -cE "\.(btn|card|table|input|badge|toast|pagination|product-grid|skip-link)" app/static/css/style.css</automated>
  </verify>
  <done>
input.css đã xóa; style.css thuần ≥400 dòng, chứa tokens + đủ component inventory; base.html nạp font mới + link style.css duy nhất; toast/skip-link contracts được định nghĩa.
  </done>
</task>

<task type="auto">
  <name>Task 2: Viết lại templates public + shared + auth + errors sang class ngữ nghĩa</name>
  <files>app/templates/public/base.html, app/templates/public/index.html, app/templates/public/product_detail.html, app/templates/public/cart.html, app/templates/public/search.html, app/templates/public/_nav.html, app/templates/public/_product_card.html, app/templates/public/_checkout_form.html, app/templates/public/_search_results.html, app/templates/_admin_nav.html, app/templates/_pagination.html, app/templates/auth/login.html, app/templates/errors/404.html, app/templates/errors/500.html</files>
  <action>
Với TỪNG file: đọc file, thay toàn bộ utility Tailwind trong attribute class bằng component class đã định nghĩa ở Task 1 (vd `bg-white rounded shadow p-4` -> `card`; `grid gap-4` trên lưới sản phẩm -> `product-grid`; `px-4 py-2 bg-blue text-white rounded` -> `btn btn-primary`). Cho phép thêm/bớt wrapper div khi component cần, nhưng tuân thủ tuyệt đối các guardrail sau:

- KHÔNG đổi bất kỳ biểu thức Jinja nào: `{% %}`, `{{ }}`, biến, filter (`format_price`, `strftime`...), điều kiện, vòng lặp.
- KHÔNG đổi field name, `id`, `name`, `data-*` (data-dir, name="q"...), `aria-*`, `href`, route/url_for, method form.
- Giữ nguyên `form.hidden_tag()` / csrf token rendering trong mọi form (CSRF là trust boundary — mất hidden_tag là vỡ bảo mật submit form).
- Giữ chính xác các class mà JS query/gán: `search-form`, `product-grid`, `search-results`, `pagination`, `gallery-item`, `badge-primary`, `reorder-btn`, `delete-btn`, `gallery-actions`, `paste-received`, `toast*`.
- Badge trạng thái còn/hết hàng dùng đúng cặp class đã chốt ở Task 1.
- Chỉ đụng attribute class + cấu trúc DOM tối thiểu phục vụ styling. Nếu gặp inline `style="..."` thì chuyển sang class nếu trivial, còn không thì giữ nguyên.

Riêng `_pagination.html`: giữ cấu trúc phân trang + class `pagination` (search-ajax.js querySelector nó).
Riêng `errors/*.html` + `auth/login.html`: chúng ít utility, chỉ thay class cho đồng bộ hệ mới.
  </action>
  <verify>
    <automated>! grep -rEn "(hover|focus|sm|md|lg|xl):[a-z]" app/templates/public/ app/templates/auth/ app/templates/errors/ app/templates/_admin_nav.html app/templates/_pagination.html && ! grep -rEn "\"[^\"]*\b(bg|text|border|p|px|py|pt|pb|pl|pr|m|mx|my|mt|mb|ml|mr|gap|w|h|min-w|min-h|max-w|max-h)-[0-9]" app/templates/public/ app/templates/auth/ app/templates/errors/ app/templates/_admin_nav.html app/templates/_pagination.html && grep -c "hidden_tag\|csrf_token" app/templates/public/_checkout_form.html app/templates/auth/login.html</automated>
  </verify>
  <done>
14 file public/shared/auth/errors không còn utility Tailwind (cả variant syntax `hover:`/`md:` lẫn numeric scale `p-4`/`gap-4`); CSRF token vẫn render trong các form; các class JS-contract còn nguyên.
  </done>
</task>

<task type="auto">
  <name>Task 3: Viết lại templates admin + chạy full gates + smoke render</name>
  <files>app/templates/admin/base.html, app/templates/admin/stats.html, app/templates/admin/categories/list.html, app/templates/admin/products/list.html, app/templates/admin/products/form.html, app/templates/admin/products/delete.html, app/templates/admin/orders/list.html, app/templates/admin/orders/detail.html, app/templates/admin/orders/_content.html, app/templates/admin/orders/delete.html</files>
  <action>
Áp dụng cùng guardrail Task 2 cho 10 file admin (đọc từng file, thay utility -> component class, không đụng Jinja logic/field name/data-*/aria-*/hidden_tag). Lưu ý riêng:
- `products/form.html` (90 chỗ class) và `orders/detail.html` (114 chỗ class) là 2 file nặng nhất — làm theo block (form group, table, badge, button group) chứ không sửa lẻ từng attribute.
- `orders/list.html` và `orders/detail.html` đang là WIP của người dùng — per D-03 cứ viết lại class trực tiếp, chấp nhận commit trộn.
- `_admin_nav.html` (shared, đã làm ở Task 2) được include bởi các trang admin: kiểm tra nav hiển thị đúng trong layout admin, không nhân đôi style.
- Bảng dữ liệu admin (orders list/detail, stats) dùng `.table` + wrapper responsive; badge trạng thái đơn/nhập kho dùng cùng hệ `.badge-*`.

Sau khi xong 10 file, chạy FULL GATES toàn repo (mục Verification) và smoke render:
`.venv/Scripts/python.exe -c "from dotenv import load_dotenv; load_dotenv(); from app import create_app; c=create_app().test_client(); rs=[c.get(p) for p in ('/', '/login', '/search?q=test', '/gio-hang')]; print([r.status_code for r in rs]); assert all(r.status_code < 500 for r in rs)"`
(Đường dẫn `/gio-hang` — kiểm tra route thật trong app/public.py trước khi chạy; nếu tên route khác thì thay bằng route public thật. Trang admin cần đăng nhập nên không đưa vào smoke; chúng được phủ bởi gate grep + render sẽ được người dùng kiểm tra trực quan.)
Nếu smoke lỗi do template -> sửa rồi chạy lại đến khi pass.
  </action>
  <verify>
    <automated>.venv/Scripts/python.exe -c "from dotenv import load_dotenv; load_dotenv(); from app import create_app; c=create_app().test_client(); rs=[c.get(p) for p in ('/', '/login', '/search?q=test')]; print([r.status_code for r in rs]); assert all(r.status_code < 500 for r in rs)"</automated>
  </verify>
  <done>
10 file admin sạch Tailwind; toàn repo pass hết gates (xem Verification); smoke render `/`, `/login`, `/search` đều < 500; không file Python/xlsx WIP nào ngoài phạm vi bị thay đổi.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

Không tạo trust boundary mới — thay đổi thuần presentation (HTML class + CSS). Các trust boundary hiện hữu (form POST qua Flask-WTF CSRF, session cookie, upload ảnh) KHÔNG bị động chạm vào logic.

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-QK-01 | Tampering | Form templates (_checkout_form, login, products/form, orders) | mitigate | Guardrail bắt buộc trong Task 2/3: giữ nguyên `form.hidden_tag()`/csrf token + field name khi viết lại class; verify grep đếm hidden_tag/csrf_token vẫn present |
| T-QK-02 | Denial of Service | Templates render (Jinja logic bị phá khi edit class) | mitigate | Smoke render test_client ở Task 3 chặn lỗi 500 trước khi commit |
| T-QK-03 | Information Disclosure | skip-link, aria-live toast container, label form | mitigate | Giữ nguyên mọi aria-*/label/skip-link (a11y cơ bản không được đơn giản hóa); CSS mới phải có trạng thái :focus cho .skip-link |
| T-QK-SC | Tampering | Package installs | N/A | Không cài package nào trong quick task này — không cần legitimacy checkpoint |
</threat_model>

<verification>
Chạy TẤT CẢ các gate sau khi hoàn thành (toàn repo, từ root):

```bash
# 1. Không só variant syntax Tailwind (hover:/focus:/md:/lg:)
! grep -rEn "(hover|focus|sm|md|lg|xl):[a-z]" app/templates/

# 2. Không só numeric-scale utility (p-4, gap-4, w-full...)
! grep -rEn "\"[^\"]*\b(bg|text|border|p|px|py|pt|pb|pl|pr|m|mx|my|mt|mb|ml|mr|gap|w|h|min-w|min-h|max-w|max-h)-[0-9]" app/templates/

# 3. Không còn chữ tailwind ở đâu cả
! grep -ri "tailwind" app/templates/ app/static/css/

# 4. input.css đã bị xóa
test ! -f app/static/css/input.css

# 5. Smoke render các route public
.venv/Scripts/python.exe -c "from dotenv import load_dotenv; load_dotenv(); from app import create_app; c=create_app().test_client(); rs=[c.get(p) for p in ('/', '/login', '/search?q=test')]; print([r.status_code for r in rs]); assert all(r.status_code < 500 for r in rs)"
```

Lưu ý gate 2: pattern `\b(text|border)-[0-9]` có thể dính false-positive với class ngữ nghĩa chứa số — nếu báo match, kiểm tra tay: chỉ sửa nếu đúng là utility Tailwind còn sót, không phải đổi tên component hợp lệ.
</verification>

<success_criteria>
- Cả 5 gates trong mục Verification pass.
- `app/static/css/style.css` là nguồn duy nhất của toàn bộ giao diện, viết theo token + component class, mobile-first responsive.
- Bộ màu/font/spacing mới khác biệt rõ so với bản cũ; font Google hỗ trợ tiếng Việt đầy đủ (Be Vietnam Pro hoặc tương đương).
- Không file nào ngoài danh sách files_modified bị thay đổi (trừ các file WIP người dùng — không đụng, git status xác nhận chúng giữ trạng thái như đầu phiên).
- Commit theo từng task: `feat(ui): design system css moi thay the tailwind` / `feat(ui): templates public sang class ngu nghia` / `feat(ui): templates admin + gates` (commit trộn WIP trong orders templates được người dùng chấp thuận — D-03).
</success_criteria>

<output>
Tạo SUMMARY tại: `.planning/quick/260824-kxs-thi-t-k-l-i-to-n-b-web-ui-th-nh-m-t-ch-n/260824-kxs-SUMMARY.md`
</output>
