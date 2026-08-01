---
phase: 02-admin-crud-images
plan: 01
subsystem: admin
tags: [flask, wtforms, jinja2, admin-crud, pagination, vietnamese]
requires:
  - phase: 01-scaffold-auth-data-model
    provides: Flask app factory, admin blueprint with @login_required guard, Product model, base template, CSS vars
provides:
  - ProductForm (Flask-WTF) with all PROD-01..07 fields + CSRF
  - products list route (sort_order ASC, id ASC, 20/page) with table + empty state + pagination
  - create/edit/delete routes behind @login_required, delete via POST + CSRF confirm page
  - format_price Jinja filter (integer VND -> 1.200.000₫)
  - admin component CSS (buttons, table, badges, pagination, form fields, flash-warning)
affects: [Phase 2 waves 02-02/02-03, Phase 3, Phase 4]
tech-stack:
  added: [format_price template filter]
  patterns: [Flask-WTF ProductForm, paginate() with error_out=False, server-rendered delete confirm, status badge via Jinja if/elif]
key-files:
  created: [app/templates/admin/products/list.html, app/templates/admin/products/form.html, app/templates/admin/products/delete.html]
  modified: [app/forms.py, app/admin.py, app/__init__.py, app/static/css/style.css, app/templates/admin/dashboard.html]
key-decisions:
  - "format_price via f-string int formatting (1.200.000₫), never :,.2f (PROD-06)"
  - "Delete is a two-step server-rendered confirm (GET) + POST form with csrf_token (PROD-03/D-04/D-08)"
  - "Flash message copy uses curly Vietnamese quotes per UI-SPEC ('Đã cập nhật sản phẩm “{tên}”')"
requirements-completed: [PROD-01, PROD-02, PROD-03, PROD-04, PROD-05, PROD-06, PROD-07]
duration: 22min
completed: 2026-08-01
---

# Phase 2 Plan 1: Admin Product CRUD Core Summary

Admin product CRUD vertical slice: ProductForm (Flask-WTF) with all product fields, sorted + paginated product list table with status badges and empty state, create/edit/delete routes behind @login_required, POST+CSRF delete confirmation page, integer-VND price formatting, and the admin component CSS base.

## Performance

- **Duration:** 22 min
- **Started:** 2026-08-01T06:03:00Z
- **Completed:** 2026-08-01T06:25:00Z
- **Tasks:** 3 completed
- **Files modified:** 8

## Accomplishments
- `ProductForm` with all 11 fields (name, price, brand, measurements, description, quantity, discontinued, sku, sort_order, admin_note, submit) + CSRF via `hidden_tag()` (PROD-01..07)
- Product list: `sort_order ASC` then `id ASC`, 20/page via `paginate(error_out=False)`, table with 7 columns, status badges (Còn hàng/Hết hàng/Ngừng bán), `{% else %}` empty state, `Trang X / Y` pagination (D-01/D-02/D-03)
- Delete flow: GET renders confirmation page showing product name + irreversible warning + image-count note; POST (with csrf_token) performs the delete (D-04/D-08, PROD-03)
- `format_price` filter renders `1200000` -> `1.200.000₫` (PROD-06)
- Dashboard `Sản phẩm` nav now targets `admin.products` with a live count badge
- All routes verified registered: `admin.products`, `admin.new_product`, `admin.edit_product`, `admin.delete_product`

## Task Commits

1. **Task 1: ProductForm + format_price filter** - `a46853f` (feat)
2. **Task 2: Product list route + table + pagination + dashboard nav** - `cf43636` (feat)
3. **Task 3: Create/edit/delete routes + form/delete templates + admin CSS** - `0f43307` (feat)

## Files Created/Modified
- `app/forms.py` - added `ProductForm` (LoginForm unchanged)
- `app/admin.py` - dashboard count, products list, new/edit/delete routes
- `app/__init__.py` - `format_price` Jinja filter
- `app/templates/admin/products/list.html` - table + empty state + pagination
- `app/templates/admin/products/form.html` - create/edit form, all fields
- `app/templates/admin/products/delete.html` - delete confirmation page
- `app/templates/admin/dashboard.html` - nav rewire + count badge
- `app/static/css/style.css` - buttons, table, badges, pagination, form, flash-warning

## Decisions Made
- Flash message copy uses curly Vietnamese quotes per UI-SPEC copy contract (e.g. `Đã cập nhật sản phẩm “{tên}”`), matching the delete-confirm body `Bạn có chắc muốn xóa sản phẩm “{tên}”?`
- Empty-state and derived-status hint copy taken verbatim from UI-SPEC (curly quotes preserved)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Verify scripts needed request context for Flask-WTF forms**
- **Found during:** Task 1 (ProductForm + format_price verify)
- **Issue:** The plan's verify script instantiated `ProductForm()` outside an app/request context; Flask-WTF raises `Working outside of request context` when generating the CSRF token
- **Fix:** Ran the verify inside `app.test_request_context()`; no production code change
- **Files modified:** none (test-harness invocation only)
- **Verification:** FORM_FILTER_OK printed

**2. [Rule 3 - Blocking] Task 2 verify referenced a route that only lands in Task 3**
- **Found during:** Task 2 (list route verify)
- **Issue:** `list.html` calls `url_for('admin.new_product'/'edit_product'/'delete_product')`; those routes are added in Task 3, so GET /admin/products raised `BuildError` -> 500
- **Fix:** Implemented Task 2 + Task 3 code together (admin.py carries both list and CRUD routes), then ran both verifications; committed in the plan's task order
- **Files modified:** app/admin.py, list.html, dashboard.html, form.html, delete.html, style.css
- **Verification:** LIST_OK then CRUD_OK; all four routes registered

**3. [Rule 1 - Bug] Plan verify script asserted a price that no seeded product has**
- **Found during:** Task 2 verify
- **Issue:** The plan's script asserted `'1.200.000₫' in body` but seeded products were priced 100000 and 200000 (the plan's own inline comment acknowledges this)
- **Fix:** Dropped the impossible assertion; kept `'200.000₫' and '100.000₫'` checks which match the seeded data
- **Files modified:** none (test-harness invocation only)
- **Verification:** LIST_OK printed

**4. [Rule 2 - Missing Critical] Flash color selectors did not match rendered classes**
- **Found during:** Task 3 (CSS)
- **Issue:** `base.html` renders `class="flash {{ category }}"` (e.g. `flash warning`), but Phase 1 CSS only defined `.flash-error`/`.flash-success` (element class `flash-error` never appears), so Phase 2's success/warning flashes would render uncolored
- **Fix:** Added `.flash.success`, `.flash.error`, `.flash.warning` selectors alongside the plan-specified `.flash-warning`; success #059669, error #DC2626, warning #D97706
- **Files modified:** app/static/css/style.css
- **Verification:** Flash zone renders semantic colors for all three categories

**5. [Rule 1 - Bug] Creating a product with quantity=0 failed validation (DataRequired rejects 0)**
- **Found during:** Phase 2 full smoke test (create with `quantity=0`)
- **Issue:** `price` and `quantity` used WTForms `DataRequired`, which checks truthiness and therefore rejects the integer `0`. A product with `quantity=0` (Hết hàng) or `price=0` re-rendered the form with validation errors (HTTP 200) instead of saving — an out-of-stock product could never be created
- **Fix:** Switched `price` and `quantity` to `InputRequired` (checks input presence only), keeping `NumberRange(min=0)` as the actual value bound
- **Files modified:** app/forms.py
- **Verification:** Smoke test — create with `quantity=0` returns 302 and the product's `status` is `out_of_stock`
- **Committed in:** 458b4b7 (fix)

---

**Total deviations:** 5 auto-fixed (2 blocking test-harness, 1 test-script bug, 1 missing critical CSS, 1 real validation bug)
**Impact on plan:** All fixes necessary for the CRUD slice to render and verify; no scope creep, no plan redesign.

## Issues Encountered
- Task 2's list template could not be verified in isolation from Task 3's routes (plan sequencing dependency); resolved by implementing and verifying both together before committing.

## Next Phase Readiness
- Routes and templates ready for 02-02 (image engine) and 02-03 (gallery wiring) to extend without restructuring
- Form already declares `enctype="multipart/form-data"` so the 02-03 file input works unchanged

---
*Phase: 02-admin-crud-images*
*Completed: 2026-08-01*

## Self-Check: PASSED

All claims verified — SUMMARY file exists, all task commits present (02-01: a46853f/cf43636/0f43307, 02-02: 4cfda80/d1204b8/1c5da13, 02-03: 2610fb3/9109008/bb6871a; plus fix 458b4b7), full smoke test green.
