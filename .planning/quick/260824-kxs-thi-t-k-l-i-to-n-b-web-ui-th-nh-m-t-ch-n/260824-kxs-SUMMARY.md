---
phase: quick-260824-kxs
plan: 01
subsystem: web-ui
tags: [ui, css, design-system, templates, tailwind-removal]
requires:
  - "app/templates/** (25 templates dùng utility Tailwind + 2 file CSS cũ)"
provides:
  - "app/static/css/style.css — design system thuần duy nhất (tokens + component class)"
  - "24 templates sạch utility, dùng class ngữ nghĩa"
affects:
  - "Mọi trang render của app (public, auth, admin, errors)"
tech-stack:
  added: []
  patterns:
    - "CSS token system (:root custom properties) + component class ngữ nghĩa, một file duy nhất"
    - "Checkbox-hack hamburger nav, Uiverse-style custom checkbox, custom-select dropdown — tất cả thuần CSS"
key-files:
  created: []
  modified:
    - app/static/css/style.css
    - app/templates/base.html
    - app/templates/public/_nav.html
    - app/templates/public/index.html
    - app/templates/public/search.html
    - app/templates/public/_product_card.html
    - app/templates/public/product_detail.html
    - app/templates/public/cart.html
    - app/templates/public/_checkout_form.html
    - app/templates/_admin_nav.html
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
  deleted:
    - app/static/css/input.css
decisions:
  - "Bộ nhận diện mới 'Đất nung': nền kem #f6f1e8, accent terracotta #b0512c, font Be Vietnam Pro 400/500/600/700"
  - "Class trạng thái JS toggle đổi sang ngữ nghĩa: is-disabled/is-dimmed/is-active/is-open thay opacity-50/bg-accent/hover:*"
  - "Style th/td của bảng qua context .data-table thay vì utility từng ô; căn lề cột giữ bằng 2 utilities .text-center/.text-right"
metrics:
  duration: ~40 min
  completed: 2026-08-24
  tasks: 3
  files_changed: 23 (+1 deleted)
---

# Quick Task 260824-kxs Summary

Thiết kế lại toàn bộ web UI thành một chỉnh thể: thay 2 file Tailwind (input.css 1082 dòng + style.css compiled 4321 dòng) bằng MỘT file CSS thuần tự viết (~1400 dòng, tokens + component class), và viết lại class attribute của 24/25 templates sang class ngữ nghĩa.

## Tasks Completed

| Task | Name | Commit | Files |
| ---- | ---- | ------ | ----- |
| 1 | Design system CSS mới + wire base.html + xóa input.css | 355ffb3 | style.css (viết mới), base.html, input.css (xóa) |
| 2 | Templates public + shared + auth + errors sang class ngữ nghĩa | 986e6d7 | 11 templates + style.css bổ sung rule contextual |
| 3 | Templates admin + full gates + smoke render | b5047c3 | 10 templates admin + style.css |

## Verification (5/5 gates pass)

1. Không còn variant syntax (`hover:`/`md:`...) trong toàn bộ app/templates/ — PASS
2. Không còn numeric-scale utility (`p-4`, `gap-4`, `w-full`...) — PASS
3. Không còn chữ "tailwind" trong app/templates/ và app/static/css/ — PASS
4. input.css đã bị xóa — PASS
5. Smoke render: `/`=302 (redirect /login — behavior internal-app có sẵn), `/login`=200, `/search?q=test`=200, `/cart`=200 — PASS

Bonus: parse toàn bộ 26 template bằng `app.jinja_env.parse()` — 0 lỗi cú pháp (phủ cả trang admin chưa đăng nhập được).

## JS Contracts giữ nguyên

- `search-ajax.js`: `.search-form`, `.product-grid`, `.search-results`, `.pagination` — còn nguyên ở DOM + có style
- `form-gallery.js`: `.gallery-item`, `.badge-primary`, `.reorder-btn`, `.delete-btn`, `.gallery-actions`, hiệu ứng `.paste-received` (animation flash 0.6s)
- Toast helper: `.toast(-success|-error|-info)` + `.show/.hide` + transition (force-reflow + transitionend hoạt động như cũ)
- Skip-link: ẩn off-screen, hiện khi `:focus`

## Deviations from Plan

**[Rule 1 - Bug] Class strings trong inline script phải sửa theo**
- **Found during:** Task 2
- **Issue:** Inline `<script>` trong `_product_card.html` và `cart.html` chứa chuỗi class Tailwind (`hover:bg-accent/90`, `focus:ring-accent`, `bg-gray-300`, `opacity-50`, `hover:bg-gray-50`...) — gate 1 chặn chính các chuỗi này, và CSS mới không định nghĩa chúng nên toggle state sẽ mất hiệu lực thị giác.
- **Fix:** Đổi sang class ngữ nghĩa tương đương 1:1 (`.add-cart.is-disabled`, `.product-card.is-dimmed`, `.btn.is-disabled`, `.suggestion-item/-name/-phone/-address`, badge không màu-utility). Toàn bộ logic JS (fetch, FormData, aria-disabled, hidden attr, event flow) giữ nguyên từng dòng.
- **Files modified:** `_product_card.html`, `cart.html`
- **Commit:** 986e6d7

**Files liệt kê kế hoạch nhưng không cần sửa:** `public/base.html`, `public/_search_results.html`, `_pagination.html` — không chứa utility Tailwind nào (chỉ có class ngữ nghĩa đã được định nghĩa lại trong CSS mới).

**Route smoke:** plan nêu `/gio-hang` nhưng route thật là `/cart` (đã check `public.py`) — dùng `/cart`. Chạy smoke bằng python toàn cục vì `.venv` hiện tại không có packages (flask/dotenv không cài trong venv).

## Deferred Issues (pre-existing, ngoài phạm vi)

- `admin/orders/list.html` script `loadFilteredOrders()` query `document.querySelector('.admin-card')` nhưng wrapper chỉ có class `admin-card--wide` → kết quả AJAX filter bị bỏ qua (container null). Lỗi có TRƯỚC task này (selector lệch với markup cũ), giữ nguyên 100% hành vi JS per yêu cầu plan. Nếu muốn bật tính năng lọc AJAX: thêm token `admin-card` vào wrapper hoặc đổi selector thành `[data-orders-container]`.
- Visual UAT các trang admin (đăng nhập thật) để người dùng kiểm tra trực quan.

## Self-Check: PASSED
