---
phase: quick-260804-3ow
plan: 1
type: execute
status: complete
---

# Quick 260804-3ow: xóa ảnh trực tiếp + tên SP tự động theo STT

## Done
- `app/forms.py`: `name` field dropped `DataRequired` → `Optional()` so it can be blank.
- `app/admin.py` `new_product()`: if name blank, generate `Sản phẩm {001}` using `max(Product.id)+1` (deletion-safe, no collision).
- `app/templates/admin/products/form.html`: existing-image checkbox replaced with a ✕ `delete-btn` (data-id).
- `app/static/js/form-gallery.js`: refactored to direct-delete — `removeNewItem` (unsaved upload), `markExistingDeleted` (appends to `delete_images`). Removed checkbox `syncDelete`. Paste handler preserved.
- `app/static/css/style.css`: `.delete-btn` styles; removed `.img-delete` checkbox rules.

## Verification
- `app/forms.py` + `app/admin.py` syntax ok.
- name validators = [Optional, Length]; empty name passes validation.
- form.html render: with 1 existing image, `delete-btn` present, `img-delete-cb` absent; `js/form-gallery.js` linked; no inline script.
- JS file: `paste` handled, `delete-btn`/`removeNewItem`/`markExistingDeleted` present, `img-delete-cb` removed.
- CSS: `.delete-btn` present, `.img-delete` removed.

## Manual (pending)
- /products/new: leave name blank + add images + submit → product named `Sản phẩm 00X`.
- Gallery: click ✕ on an existing image → item removed, id queued in delete_images (server deletes on submit).
- Gallery: upload new image then ✕ → immediate removal from file list.

## Commit
`6728c51` — feat: direct-delete gallery buttons + auto-generated product name by STT

## Self-Check: PASSED
