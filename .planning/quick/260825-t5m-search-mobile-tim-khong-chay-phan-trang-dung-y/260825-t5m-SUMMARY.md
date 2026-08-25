# Quick Task 260825-t5m — Tóm tắt

**Commit:** eb5ccaa | **Files:** 3 changed (+21 / -16)

## Thay đổi theo file

- **`app/static/js/search-ajax.js`** — comment đầu file ghi GET + XHR;
  `runSearch()`: bỏ FormData/fetch POST → `URLSearchParams({q, page,
  ajax:'1'})` + GET fetch với header XHR (giữ nguyên loading opacity và
  `.then()`); fallback `.catch`: `form.submit()` → `window.location.href =
  url` (giữ q+page).
- **`app/templates/_pagination.html`** — auto-call `pagination_nav(...)` sau
  `{% endmacro %}` với guard `{% if pagination is defined and endpoint is
  defined %}`; 5 nơi import macro bằng `{% from %}` (không context) bị skip.
- **`app/public.py`** (route `search`) — `is_ajax` nhận thêm
  `request.args.get('ajax') == '1'`; ép int an toàn:
  `cat_id = args.get('category', type=int) or form.get('category', type=int)`,
  `page = ... or ... or 1`.

## Lệch (Lỗi chặn — Rule 3)

`render_template('public/_pagination.html', ...)` →
`render_template('_pagination.html', ...)` tại dòng render AJAX trong
`public.py`. Plan root-cause #2 giả định route nhận chuỗi rỗng; thực tế
`app/templates/public/_pagination.html` **không tồn tại** (blueprint không có
`template_folder`, loader chỉ đọc `app/templates/`) → AJAX nào qua được CSRF
sẽ dính TemplateNotFound → 500. Verify bước 1 của plan (`pagination_html`
non-empty) bắt buộc sửa path; chỉnh 1 string, giữ đúng phạm vi 3 file.

## Xác minh (test_client, system python, PYTHONIOENCODING=utf-8, load_dotenv('.env'))

| # | Request | Kết quả |
|---|---------|---------|
| 1 | GET `/search?q=ao&page=2&ajax=1` + XHR | 200 JSON; html 47794 chars; pagination_html 650 chars, chứa `page-num` + link page 3 |
| 2 | POST `/search` `{q:'ao',page:'2',ajax:'1'}` + XHR, CSRF off | 200 JSON, pagination_html 650 chars — ép int hết TypeError |
| 2b | POST tương tự, CSRF bật | 400 (đúng CSRFProtect — lý do JS chuyển GET) |
| 3 | GET `/search?q=ao&page=2` full HTML | 200, có `.pagination`; đúng **1** `<nav class="pagination">` — guard không render trùng |
| 4 | GET `/search` không q | 200 |
| 5 | POST `page='999'` + XHR, CSRF off | 200 (clamp out-of-range nguyên vẹn) |

Home `/`: 0 nav (pages <= 1 → macro ẩn, hành vi sẵn có).

## Root cause tóm tắt

1. search-ajax.js fetch POST → CSRFProtect global chặn 400 (không csrf_token)
   → catch → form.submit() mất page → luôn về trang 1.
2. Route AJAX render nhầm path `public/_pagination.html` (file nằm ở root
   templates/) → TemplateNotFound; và bản thân template chỉ chứa macro
   definition → render trực tiếp ra chuỗi rỗng.
3. public.py get(key, default-from-form, type=int) trả string khi key chỉ ở
   form → min(str, int) TypeError.
