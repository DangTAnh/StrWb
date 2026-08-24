---
phase: quick-260824-wx4
plan: 01
subsystem: public-ui
tags: [bugfix, css, js, navbar, search, mobile]
requires: []
provides: [mobile-search-one-row-header]
affects: [public-layout]
tech-stack:
  added: []
  patterns: [click-outside-close, absolute-overlay-search-form]
key-files:
  created: []
  modified:
    - app/templates/public/_nav.html
    - app/static/css/style.css
decisions:
  - "Bỏ input blur handler (nguyên nhân bug submit); thay bằng document click-outside chỉ chạy <768px"
  - "Form tìm kiếm mobile absolute top:100% neo vào .site-header sticky → không đẩy layout trang"
metrics:
  duration: ~5 min
  completed_date: 2026-08-24
---

# Quick Task 260824-wx4: Sửa nav bar tìm kiếm bản mobile Summary

**Một dòng:** Nút tìm kiếm mobile thành icon SVG 1 hàng trong header + sửa bug bấm nút Tìm không submit (bỏ blur handler), form trượt absolute dưới header.

## Những gì đã làm

### Task 1 — `_nav.html`
- Nút toggle: bỏ `btn btn-primary` + text "Tìm kiếm" → SVG magnifier inline 20px (stroke currentColor), giữ class `search-toggle`, `aria-label="Mở tìm kiếm"`.
- JS: **xóa** `input.addEventListener('blur', ...)` (blur do touchstart ăn mất click submit). Thêm `document.addEventListener('click', ...)` đóng khi bấm ra ngoài shell trên mobile (<768px); tap nút "Tìm" nằm trong shell nên vẫn submit, handler `submit → closeSearch()` sẵn có tự đóng.
- `aria-label` đổi theo state: mở → "Đóng tìm kiếm", đóng → "Mở tìm kiếm".

### Task 2 — `style.css` (block max-width 767px)
- Header mobile 1 hàng: `.site-header__inner` row/space-between; shell `flex: 0 0 auto`.
- `.search-toggle`: icon button 40×40, border, hover accent.
- `.search-form` mobile: `display:none`, khi mở là `position:absolute; top:100%` full-width ngay dưới header sticky (background surface + shadow) — bỏ rule cũ `flex: 1 0 100%` từng đẩy cả trang.
- Desktop block min-768 giữ nguyên.

## Verify (đã chạy)

Flask test_client, session admin #1 (`_user_id='1'`), load .env trước `create_app()`:

| Check | Kết quả |
|-------|---------|
| GET `/` | 200 |
| Nút `.search-toggle` chứa `<svg` | True |
| Script nav KHÔNG còn "blur" | True |
| Có `document.addEventListener('click'` | True |
| CSS max-767 có `.search-form` absolute top:100% | True |
| Rule cũ `flex: 1 0 100%` đã biến mất | True |
| Desktop min-768 nguyên vẹn (ẩn toggle + desktop-header-actions) | True |

## Deviations from Plan

None - plan executed exactly as written.

## Ghi chú môi trường

- `venv/Scripts/python.exe` không tồn tại; dùng system `python`. `.venv` có sẵn nhưng thiếu flask — phải dùng system python.
- `SECRET_KEY` bắt buộc từ env → cần `load_dotenv()` trước `create_app()` khi verify.

## Commits

- `99c89eb` fix(ui): nav tim kiem mobile - icon gon 1 hang + nut Tim submit dung (2 files: _nav.html, style.css)

## Self-Check: PASSED

- FOUND: app/templates/public/_nav.html (modified, committed)
- FOUND: app/static/css/style.css (modified, committed)
- FOUND: commit 99c89eb trong git log
