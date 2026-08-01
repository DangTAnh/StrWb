---
phase: 02-admin-crud-images
verified: 2026-08-01T14:05:00Z
status: human_needed
score: 5/5 must-haves verified
overrides_applied: 0
overrides: []
gaps: []
human_verification:
  - test: "Exercise the gallery ↑/↓ reorder buttons and the 'Chọn ảnh' multi-file input in a real browser on the edit form: add several files, reorder existing images, check one 'Xóa' box, save."
    expected: "Previews render for new files (URL.createObjectURL), existing/new items reorder via ↑/↓, first gallery item carries the 'Ảnh chính' badge, checked images are removed on save, and the final gallery order is persisted (sort_order/is_primary updated)."
    why_human: "The gallery reorder/preview is client-side vanilla JS (form.html inline script). The Flask test client cannot execute browser JS, so DataTransfer file-order rebuild and DOM reorder behavior are only verifiable in a browser."
  - test: "Visually inspect the admin product list (table + status badges + thumbnails), create/edit form, gallery section, and delete-confirmation page against 02-UI-SPEC."
    expected: "Colors, spacing, 44px touch targets, status badge palette (Còn hàng/Hết hàng/Ngừng bán), 'Ảnh chính' badge, 48×48 thumbnails, and page copy match the UI-SPEC contract."
    why_human: "CSS appearance and layout are visual; grep confirms selectors exist but not that they render correctly."
  - test: "Resize the browser to mobile widths (≤768px, ≤480px) on the admin pages."
    expected: "2-col form rows collapse to 1 col, the product table scrolls horizontally (overflow-x), the header stacks, and the gallery wraps per UI-SPEC responsive behavior."
    why_human: "Responsive rendering is a visual/media-query behavior not verifiable via the test client."
---

# Phase 2: Admin CRUD + Images Verification Report

**Phase Goal:** Admin can fully manage product listings including images, stock, and pricing
**Verified:** 2026-08-01T14:05:00Z
**Status:** human_needed (all 5 programmatic truths VERIFIED; visual/JS-interaction layer requires human UAT)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Admin can create, edit, and delete products with all fields (name, price, brand, measurements, description, stock status, quantity) | VERIFIED | `app/admin.py:65-93` `new_product` creates with all 11 fields; `:97-119` `edit_product` uses `form.populate_obj`; `:122-147` `delete_product` GET renders confirm page, POST deletes. Independent test: create POST 302 + row persisted (all fields, `price=150000 brand=Coolmate sku=SKU-001`), edit POST 302 + every field updated + `status` flips to `discontinued` when `discontinued` set, delete POST 302 + row gone. quantity=0 (InputRequired fix, `app/forms.py:15,19`) accepted → status `out_of_stock`. |
| 2 | Admin can upload multiple images per product with server-side validation (file type via magic bytes, size limit, dimension checks) | VERIFIED | `app/image_utils.py:33-59` `validate_image_upload` (extension allowlist line 13, magic bytes 21-30, Pillow `verify()` 46-50, 2000×2000 cap 57-58); `app/admin.py:19-47` `_process_image_batch` validates the entire batch before saving. Independent byte-level tests: JPEG/PNG/WebP magic accepted, wrong extension/wrong-magic/corrupt/2500×2500 rejected with Vietnamese reasons, 2-file JPEG upload → 2 rows, PNG+WebP upload re-encoded. |
| 3 | Uploaded images are saved with UUID filenames and thumbnails are generated for listing views | VERIFIED | `app/image_utils.py:68` `uuid.uuid4().hex` filesystem name; `:76-81` full JPEG (q85) + 400×400 thumbnail (q82); `app/models.py:59-64` `thumb_filename`; `app/templates/admin/products/list.html:28-32` renders `primary_image.thumb_filename`. Independent tests: filename matches `^[0-9a-f]{32}\.jpg$`, full image ≤2000×2000 JPEG on disk, thumb ≤400×400 JPEG on disk, list page references the `_thumb.jpg` asset. |
| 4 | Price is stored as integer VND with no precision loss | VERIFIED | `app/models.py:22` `price = db.Column(db.Integer)`; `app/__init__.py:64-66` `format_price` filter `1.200.000₫`. Independent tests: sqlite `PRAGMA table_info(products)` → `price` column type `INTEGER`; round-trip of 999999999 exact; `format_price(1200000)` → `1.200.000₫`. |
| 5 | All admin forms have CSRF protection and validate submitted data | VERIFIED | `app/__init__.py:14,52` global `CSRFProtect`; `app/forms.py:13-24` `ProductForm` (InputRequired + NumberRange + Length); `app/templates/admin/products/form.html:7` `form.hidden_tag()`; `app/templates/admin/products/delete.html:14` hidden `csrf_token`. Independent tests: POST /new without token → 400; invalid create (empty name, negative price, negative quantity) re-renders 200 with all three field errors and nothing saved; create/edit/delete forms carry CSRF fields. |

**Score:** 5/5 truths verified

### Decision Spot-Checks (D-01..D-17)

| Decision | Status | Evidence |
|----------|--------|----------|
| D-01 table + thumbnail column | VERIFIED | list.html table with 7 columns incl. Ảnh; admin.py:56-62 |
| D-02 sort_order then id sort | VERIFIED | admin.py:59 `.order_by(Product.sort_order.asc(), Product.id.asc())` |
| D-03 20/page pagination | VERIFIED | admin.py:60 `per_page=20`; test: 26 products → page 1 shows 20 rows, page 2 shows 6, indicator `Trang 1 / 2` |
| D-04 delete confirmation shows name | VERIFIED | delete.html:6 + `Bạn có chắc muốn xóa sản phẩm “{tên}”?` |
| D-05 files removed with product | VERIFIED | admin.py:136-138 `delete_image_files` per image; test: delete product → 2 full + 2 thumb files gone from disk |
| D-06 DB first, files after | VERIFIED | admin.py:132-133 `db.session.delete; db.session.commit()` then file loop 134-138 |
| D-07 delete flash with count | VERIFIED | admin.py:140-142 `Đã xóa sản phẩm “{name}” và {N} ảnh đã xóa` |
| D-08 no undo / discontinued overrides | VERIFIED | delete.html:10 `Hành động này không thể hoàn tác.`; models.py:36-40 status logic (test: discontinued → `discontinued` despite qty=0) |
| D-09 cleanup failure non-blocking + warning | VERIFIED | admin.py:144-145 warning flash; test: forced OSError (file→dir) → delete still 302 + DB row gone + `Cảnh báo: sản phẩm đã xóa nhưng không xóa được…` rendered |
| D-10 inline upload in create/edit form | VERIFIED | form.html:78-102 gallery section in the same form |
| D-11 `<input type=file multiple>` | VERIFIED | form.html:100 `multiple accept=".jpg,.jpeg,.png,.webp"` |
| D-12 first image = primary | VERIFIED | admin.py:44-46 `sort_order=idx, is_primary=(idx==0)`; models.py:42-45 `primary_image`; tests: 2-image create → img0 primary; reorder via `image_order` → primary follows |
| D-13 reorder ↑/↓ | VERIFIED | form.html:90-93 buttons + inline JS; server-side test of reorder persistence |
| D-14 existing gallery in edit form + per-image delete | VERIFIED | form.html:84-97; admin.py:118-119 passes `existing_images` |
| D-15 checkbox delete on save | VERIFIED | form.html:94 checkbox + JS `syncDelete`; test: checked image row + file removed on save, kept image remains primary |
| D-16 validation contract (allowlist, magic, verify, 2000×2000, 16MB, UUID, re-encode, no secure_filename) | VERIFIED | image_utils.py:13,21-30,46-58,68,73; MAX_CONTENT_LENGTH 16MB in `__init__.py:36`; no `secure_filename` anywhere (grep) |
| D-17 reject whole batch | VERIFIED | admin.py:21-25 validate ALL before save; tests: valid+invalid batch → 200 with `Không thể lưu ảnh… bad.jpg…`, 0 new image rows; create with bad image → product NOT created |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `app/forms.py` | `ProductForm` with all fields + CSRF | VERIFIED | lines 13-24, 11 fields, InputRequired+NumberRange on price/quantity |
| `app/admin.py` | products/new/edit/delete routes + batch handling + delete cleanup | VERIFIED | lines 19-47 `_process_image_batch`, 56-62 list, 65-93 new, 97-119 edit, 122-147 delete |
| `app/image_utils.py` | allowlist, magic bytes, validate, UUID save, thumbnail, tolerant delete | VERIFIED | lines 13-105 |
| `app/models.py` | ProductImage.original_filename + sort_order + thumb_filename; Product.primary_image; delete-orphan cascade | VERIFIED | lines 33, 42-45, 48-64 |
| `app/templates/admin/products/list.html` | table + empty state + pagination + 48×48 thumb | VERIFIED | lines 9-77; thumb cell 28-32 |
| `app/templates/admin/products/form.html` | all fields + gallery section + inline JS | VERIFIED | lines 6-108 form, 78-102 gallery, 110-218 JS |
| `app/templates/admin/products/delete.html` | confirm page + POST form + csrf | VERIFIED | lines 6-15 |
| `app/__init__.py` | `format_price` filter + 413 handler | VERIFIED | lines 64-66, 84-87 |
| `app/static/css/style.css` | buttons, table, badges, pagination, gallery, responsive | VERIFIED | Phase 2 block lines 142-341; total 341 lines ~9.4KB < 15KB |
| `app/static/uploads/` + `.gitignore` | uploads dir tracked, images ignored | VERIFIED | `.gitkeep` present; `.gitignore` has `app/static/uploads/` |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | -- | ------ | ------- |
| `app/admin.py` | `app/image_utils.py` | `from .image_utils import delete_image_files, save_image_file, validate_image_upload` (line 6) | WIRED | batch validation/save/delete wired into routes |
| `app/admin.py` | `app/models.py` | `Product`, `ProductImage` queries; `img.product_id == product.id` guard | WIRED | line 7, 29, 36 |
| `app/templates/admin/products/form.html` | `app/admin.py` | hidden `image_order`/`delete_images` fields + `name="images"` files | WIRED | verified order/delete persisted server-side |
| `app/templates/admin/products/list.html` | `app/models.py` | `product.primary_image.thumb_filename` → `url_for('static', filename='uploads/'+…)` | WIRED | verified `_thumb.jpg` rendered |
| `app/templates/admin/products/delete.html` | `app/admin.py` delete POST | POST form + `csrf_token` → `delete_image_files` after DB delete | WIRED | verified delete flow + file cleanup |
| `app/admin.py` | CSRFProtect | `form.validate_on_submit()` + global CSRFProtect (`__init__.py:52`) | WIRED | POST without token → 400 |
| `app/image_utils.py` | Pillow | `Image.open/verify/convert/thumbnail/save` | WIRED | byte-level tests confirm real JPEG output |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| product list | `pagination.items` | `Product.query...paginate()` real sqlite rows | Yes | FLOWING |
| create form | product fields | `form.validate_on_submit()` → `db.session.add` → sqlite | Yes | FLOWING |
| image upload | uploaded bytes | `request.files.getlist('images')` → `validate_image_upload` → `save_image_file` writes real files | Yes | FLOWING |
| list thumbnail | `primary_image.thumb_filename` | real file in `app/static/uploads/<uuid>_thumb.jpg` | Yes | FLOWING |
| delete cleanup | image `filename`s | `delete_image_files` removes real files from disk (full + thumb) | Yes | FLOWING |
| price cell | `p.price` | integer column → `format_price` → `1.200.000₫` | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| CSRF POST without token | test client POST /admin/products/new | 400 | PASS |
| unauth /admin/products → login | GET unauth | 302 `/login?next=/admin/products` | PASS |
| create all fields | POST /new | 302; row persisted with all fields | PASS |
| edit all fields | POST /edit | 302; all fields updated; status discontinued | PASS |
| delete confirm + POST | GET then POST /delete | confirm shows name; 302; row gone | PASS |
| quantity=0 | POST /new qty=0 | 302; status out_of_stock | PASS |
| multi-image upload | POST /new 2×JPEG | 302; 2 rows; img0 primary | PASS |
| D-17 batch rejection | POST /edit good+bad | 200 + flash naming bad.jpg; no rows added | PASS |
| D-16 validation | image_utils byte-level | allowlist/magic/verify/2000×2000 all enforced | PASS |
| UUID + thumbnails | filesystem + Pillow | 32-hex .jpg; full ≤2000×2000; thumb ≤400×400 | PASS |
| reorder persists (D-13) | POST /edit image_order reversed | 302; primary follows new order | PASS |
| per-image delete (D-15) | POST /edit delete_images | row + file gone; kept image primary | PASS |
| product delete cleans files (D-05/06) | POST /delete with images | DB row + 4 files gone | PASS |
| D-09 warning on cleanup OSError | force file→dir, delete | 302; row gone; warning flash rendered | PASS |
| pagination 20/page (D-03) | seed 26, GET page 1/2 | 20 rows page 1, 6 rows page 2, `Trang 1 / 2` | PASS |
| price integer (SC4) | PRAGMA + round-trip | column INTEGER; 999999999 exact | PASS |
| format_price | filter call | 1200000 → `1.200.000₫` | PASS |
| form validation (SC5) | POST invalid data | 200 + field errors; nothing saved | PASS |
| empty state | GET with empty DB | `Chưa có sản phẩm nào` + CTA, no table | PASS |
| PNG/WebP re-encode | upload PNG+WebP | both stored as JPEG on disk | PASS |
| 413 oversized request | POST Content-Length 17MB | 302 redirect (handler) | PASS |
| delete success flash (D-07) | follow delete redirect | `Đã xóa sản phẩm “{name}” và 2 ảnh đã xóa` | PASS |

### Probe Execution

No `probe-*.sh` scripts exist in the repo and no probes were declared in any Phase 2 PLAN/SUMMARY. Step 7c: N/A.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| PROD-01 | 02-01 | create with name, price, brand, measurements, description | SATISFIED | forms.py:13-18; admin.py:65-93; tested |
| PROD-02 | 02-01 | edit every field | SATISFIED | admin.py:97-119 `populate_obj`; tested |
| PROD-03 | 02-01, 02-03 | delete via POST + CSRF | SATISFIED | admin.py:122-147; delete.html POST form; tested |
| PROD-04 | 02-01 | status Còn hàng/Hết hàng/Ngừng bán | SATISFIED | models.py:36-40; list.html badges; tested |
| PROD-05 | 02-01 | quantity ≥ 0; 0 → hết hàng | SATISFIED | forms.py:19; models.py:40; tested |
| PROD-06 | 02-01 | integer VND, no precision loss | SATISFIED | models.py:22; __init__.py:64-66; tested |
| PROD-07 | 02-01 | CSRF + validation on all admin forms | SATISFIED | forms.py:13-24; CSRFProtect; tested |
| IMG-01 | 02-02 | validated upload (magic bytes, size, dimension) | SATISFIED | image_utils.py:33-59; tested |
| IMG-02 | 02-02 | UUID filenames, no VN char loss | SATISFIED | image_utils.py:68; original_filename; tested |
| IMG-03 | 02-03 | multiple images per product (gallery) | SATISFIED | admin.py:19-47; form.html:78-102; tested |
| IMG-04 | 02-02 | resize → thumbnail for list | SATISFIED | image_utils.py:79-81; models.py:59-64; tested |

### Anti-Patterns Found

None. No TBD/FIXME/XXX/PLACEHOLDER markers, no `secure_filename`, no stub returns, no hardcoded empty data in the phase files. 2-01's `DataRequired`-rejects-zero bug was fixed with `InputRequired` (commit 458b4b7, documented in 02-01-SUMMARY) and independently verified (quantity=0 works).

### Human Verification Required

1. **Gallery reorder/preview JS interaction** — Exercise ↑/↓ reorder and the multi-file `Chọn ảnh` input in a real browser on the edit form. Expected: previews render for new files, items reorder, first item carries `Ảnh chính`, checked images delete on save, order persists. Why human: client-side vanilla JS not executable by the test client.
2. **Visual appearance vs 02-UI-SPEC** — Inspect admin list (table/badges/thumbnails), create/edit form, gallery, and delete-confirm page. Why human: CSS rendering is visual.
3. **Responsive behavior** — Resize to ≤768px / ≤480px on admin pages. Expected: 2-col rows collapse, table scrolls horizontally, header stacks, gallery wraps. Why human: media-query visual behavior.

### Gaps Summary

No functional gaps. All 5 roadmap success criteria verified against the actual code with independent execution (flask test client, Pillow byte-level, sqlite PRAGMA, filesystem checks): 75+15 programmatic checks, all passing. Two non-blocking observations:

1. **ROADMAP.md "Plans:" sub-lists** under Phase 2/3/4 list `01-01/01-02/01-03-PLAN.md` (copy-paste from Phase 1) instead of the phase's own plan files. Pre-existing docs defect, already tracked in `deferred-items.md`. Does not affect progress tracking (real plan files are 02-01/02-02/02-03-PLAN.md, all present).
2. **New-file ordering vs UI-SPEC wording** — New files always append *after* kept existing images on save (can't interleave a new file between existing ones), matching 02-03's persistence contract but slightly diverging from UI-SPEC's "gallery order (existing + new) is the order saved on submit". D-12 (first = primary) and D-13 (reorder existing / reorder new among themselves) still function. Non-blocking UX limitation.

The 3 human verification items above require browser/visual sign-off; all automated truths pass.

---

_Verified: 2026-08-01T14:05:00Z_
_Verifier: Claude (gsd-verifier)_
