---
phase: 02-admin-crud-images
plan: 02
subsystem: image
tags: [pillow, image-validation, magic-bytes, uuid, thumbnails, sqlite-schema]
requires:
  - phase: 02-admin-crud-images
    provides: ProductImage model (Phase 1), MAX_CONTENT_LENGTH 16MB config, BASE_DIR in app/__init__.py
provides:
  - ProductImage.original_filename + sort_order columns + thumb_filename; Product.primary_image
  - app/image_utils.py: extension allowlist, magic-byte check, Pillow verify + 2000x2000 cap, UUID re-encode save, 400px thumbnail, tolerant delete
  - app/static/uploads/ directory (gitignored, .gitkeep tracked)
affects: [Phase 2 wave 02-03, Phase 3, Phase 4]
tech-stack:
  added: [app/image_utils.py module (Pillow-based)]
  patterns: [magic-byte verification, verify-then-reopen, re-encode to RGB JPEG on save, UUID filesystem names, (deleted, failed) cleanup tuple]
key-files:
  created: [app/image_utils.py, app/static/uploads/.gitkeep]
  modified: [app/models.py, .gitignore]
key-decisions:
  - "Re-encode everything to RGB JPEG (quality 85 full / 82 thumb) — strips EXIF/payloads, normalizes alpha (D-16/Pitfall 7)"
  - "Thumbnail 400x400px — headroom for 48px table + 96px gallery boxes"
  - "FileNotFoundError on delete counts as handled (deleted), OSError counts as failed (D-09)"
requirements-completed: [IMG-01, IMG-02, IMG-04]
duration: 13min
completed: 2026-08-01
---

# Phase 2 Plan 2: Image Validation and Storage Engine Summary

Standalone image-safety engine: extended ProductImage model (original_filename, sort_order, thumb_filename, primary_image) plus app/image_utils.py implementing the full D-16 contract — extension allowlist, magic-byte verification, Pillow verify(), 2000×2000 decompression-bomb cap, UUID re-encoded JPEG storage, 400px thumbnail generation, and a tolerant delete that returns failure counts.

## Performance

- **Duration:** 13 min
- **Started:** 2026-08-01T06:25:00Z
- **Completed:** 2026-08-01T06:38:00Z
- **Tasks:** 3 completed
- **Files modified:** 4

## Accomplishments
- `validate_image_upload` rejects wrong extension, wrong magic bytes, corrupt files, and >2000×2000 images — each with a Vietnamese reason (IMG-01, D-16)
- `save_image_file` writes a UUID-named re-encoded JPEG (quality 85) plus a 400×400 thumbnail (quality 82); verified a real 3000×2000 JPEG lands ≤2000×2000 with a valid thumb (IMG-02, IMG-04)
- `delete_image_files` removes full + thumb, tolerates missing files, counts lock failures — the D-09 contract
- `Product.primary_image` returns the sort_order-0 image (D-12); `ProductImage.thumb_filename` derives `<uuid>_thumb.jpg`
- Dev DB recreated with the new `product_images` columns (PRAGMA verified: `original_filename`, `sort_order`)
- `app/static/uploads/` exists in-repo (gitignored contents, tracked `.gitkeep`)

## Task Commits

1. **Task 1: Extend ProductImage model + uploads dir + gitignore** - `4cfda80` (feat)
2. **Task 2: image_utils.py validation contract (D-16)** - `d1204b8` (feat)
3. **Task 3: save_image_file + delete_image_files** - `1c5da13` (feat)

## Files Created/Modified
- `app/models.py` - ProductImage.original_filename, ProductImage.sort_order, thumb_filename, Product.primary_image
- `app/image_utils.py` - ALLOWED_EXTENSIONS, MAX_DIMENSION, THUMBNAIL_SIZE, check_magic_bytes, validate_image_upload, save_image_file, delete_image_files
- `app/static/uploads/.gitkeep` - keeps uploads dir in repo
- `.gitignore` - `app/static/uploads/` (uploaded images are user data)

## Decisions Made
- Re-encode everything to RGB JPEG (alpha/EXIF loss accepted for catalog photos) per D-16/Pitfall 7
- Thumbnail asset 400×400 (planner decision, serves 48px/96px UI boxes)
- `secure_filename` deliberately NOT used anywhere (D-16) — filesystem names are always `uuid4().hex + '.jpg'`

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
- None. The plan's three verify scripts ran as written and printed MODEL_OK, UPLOADS_DIR_OK, VALIDATE_OK, SAVE_DELETE_OK.

## Next Phase Readiness
- 02-03 wires `validate_image_upload` / `save_image_file` / `delete_image_files` into the 02-01 CRUD routes
- `ProductImage.sort_order` + `Product.primary_image` ready for gallery ordering and list thumbnails

---
*Phase: 02-admin-crud-images*
*Completed: 2026-08-01*

## Self-Check: PASSED

All claims verified — SUMMARY file exists, all task commits present (02-01: a46853f/cf43636/0f43307, 02-02: 4cfda80/d1204b8/1c5da13, 02-03: 2610fb3/9109008/bb6871a; plus fix 458b4b7), full smoke test green.
