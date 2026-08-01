---
phase: 02-admin-crud-images
plan: 03
subsystem: admin
tags: [flask, gallery, javascript, image-upload, csrf, delete-cascade]
requires:
  - phase: 02-admin-crud-images
    provides: 02-01 CRUD routes + form/list/delete templates; 02-02 image_utils + ProductImage columns
provides:
  - Inline gallery upload in create/edit form (multiple files, batch validation D-17, primary D-12, reorder D-13, per-image delete D-15)
  - Batch-aware new/edit POST handlers via _process_image_batch
  - Full product delete with on-disk file cleanup (DB-first D-06, count flash D-07, non-blocking warning D-09)
  - 48x48 primary thumbnail in the admin list (IMG-04)
  - 413 error handler for oversized uploads
affects: [Phase 3, Phase 4]
tech-stack:
  added: [inline vanilla JS for gallery preview/reorder (~2KB, no libraries)]
  patterns: [validate-entire-batch-before-write (D-17), hidden image_order/delete_images fields, DataTransfer rebuild for file order, delete-orphan cascade]
key-files:
  created: []
  modified: [app/admin.py, app/__init__.py, app/models.py, app/templates/admin/products/form.html, app/templates/admin/products/list.html, app/static/css/style.css]
key-decisions:
  - "Delete-orphan cascade on Product.images so product delete removes image rows (root-cause fix for NOT NULL product_id failure)"
  - "New files always append after kept existing images on save (per 02-03 persistence contract); JS reorders new files among themselves"
  - "Gallery changes persist only on Save (POST + CSRF, D-15) — no immediate-delete request"
requirements-completed: [PROD-03, IMG-01, IMG-02, IMG-03, IMG-04]
duration: 24min
completed: 2026-08-01
---

# Phase 2 Plan 3: Gallery Wiring + Delete Cleanup Summary

Completed the Phase 2 vertical slice: inline multi-image gallery in the create/edit form with batch validation (D-17), primary-image selection (D-12), ↑/↓ reorder (D-13), per-image checkbox delete on Save (D-15), 48×48 list thumbnails (IMG-04), and full product delete that removes DB row first then on-disk files with a count flash and non-blocking cleanup warnings (D-05/D-06/D-07/D-09).

## Performance

- **Duration:** 24 min
- **Started:** 2026-08-01T06:38:00Z
- **Completed:** 2026-08-01T07:02:00Z
- **Tasks:** 3 completed
- **Files modified:** 6

## Accomplishments
- `_process_image_batch` validates the ENTIRE batch before saving any file — one invalid file rejects all with a flash naming file + reason, nothing saved (D-17)
- Create/edit POST now parses `image_order`/`delete_images` hidden fields and `images` file list; assigns `sort_order = index` and `is_primary = (idx == 0)` (D-12/D-13/D-15)
- Gallery UI: existing images with Ảnh chính badge, ↑/↓ reorder buttons (44px touch), ☐ Xóa checkbox, `Chọn ảnh` file input (`multiple accept=".jpg,.jpeg,.png,.webp"`)
- Inline vanilla JS (~2KB): new-file previews via `URL.createObjectURL`, `DataTransfer` rebuild so final new-file order reaches the server, `image_order`/`delete_images` hidden-field sync
- Delete flow: DB row first, then `delete_image_files` for every image; success flash `Đã xóa sản phẩm “{tên}” và {N} ảnh đã xóa`; cleanup failures surface a warning flash but never block (D-09)
- 413 handler flashes `Tập tin quá lớn. Tối đa 16MB cho mỗi lần tải ảnh.` and redirects back
- List Ảnh column renders the 48×48 primary thumbnail, placeholder otherwise

## Task Commits

1. **Task 1: Batch-aware image handling in new/edit routes (D-17)** - `2610fb3` (feat)
2. **Task 2: Gallery section in form + JS reorder + list thumbnails** - `9109008` (feat)
3. **Task 3: Full delete with file cleanup + 413 handler** - `bb6871a` (feat)

## Files Created/Modified
- `app/admin.py` - `_process_image_batch`, batch-aware new/edit POST, delete file cleanup, existing_images passed to form
- `app/__init__.py` - 413 error handler + flask imports
- `app/models.py` - `Product.images` cascade `all, delete-orphan` (Rule 1 fix)
- `app/templates/admin/products/form.html` - gallery section + inline JS
- `app/templates/admin/products/list.html` - primary thumb cell
- `app/static/css/style.css` - gallery grid, badge-primary, reorder-btn, img-delete, thumb

## Decisions Made
- Per-image delete and reorder are persisted only on the CSRF-protected form Save (D-15); no immediate delete request
- New files are appended after kept existing images on save (the plan's persistence contract), so primary always comes from the displayed gallery order
- Flash copy uses curly Vietnamese quotes per UI-SPEC (`Đã xóa sản phẩm “{tên}”`)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Deleting a product with images failed with NOT NULL constraint**
- **Found during:** Task 3 (full delete verify)
- **Issue:** `Product.images` had no cascade, so `db.session.delete(product)` emitted `UPDATE product_images SET product_id=NULL` — violating `product_id NOT NULL` → 500. Latent since Phase 1 (no images existed), surfaced by the new delete-with-images flow
- **Fix:** Added `cascade='all, delete-orphan'` to `Product.images` so deleting a product deletes its image rows (root cause fix)
- **Files modified:** app/models.py
- **Verification:** DELETE413_OK — DB row gone, ProductImage rows gone, 4 files removed from disk
- **Committed in:** bb6871a (Task 3 commit)

**2. [Rule 3 - Blocking] Task 1 verify reused a closed BytesIO**
- **Found during:** Task 1 (batch verify)
- **Issue:** The plan's script passed the same `BytesIO` to two POSTs; Werkzeug's test client closes file streams after the first request → `ValueError: I/O operation on closed file`
- **Fix:** Used a fresh image stream for the second POST (test-harness invocation only)
- **Files modified:** none
- **Verification:** BATCH_OK printed

---

**Total deviations:** 2 auto-fixed (1 real bug, 1 test-harness)
**Impact on plan:** The cascade fix was essential — product delete would 500 on any product with images. No scope creep.

## Issues Encountered
- The delete-orphan cascade was discovered only when the delete-with-images verify ran; the model change is minimal and standard ORM practice.

## Next Phase Readiness
- Phase 2 vertical slice complete: admin can create/edit/delete products with validated multi-image galleries end to end
- Public catalog (Phase 3) can consume `Product.primary_image`/`ProductImage.filename` for display

---
*Phase: 02-admin-crud-images*
*Completed: 2026-08-01*

## Self-Check: PASSED

All claims verified — SUMMARY file exists, all task commits present (02-01: a46853f/cf43636/0f43307, 02-02: 4cfda80/d1204b8/1c5da13, 02-03: 2610fb3/9109008/bb6871a; plus fix 458b4b7), full smoke test green.
