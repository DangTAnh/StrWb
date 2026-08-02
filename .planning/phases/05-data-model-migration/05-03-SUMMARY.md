---
phase: 05-data-model-migration
plan: 03
subsystem: ui
tags: [flask, wtforms, jinja2, admin, cost-price]

# Dependency graph
requires:
  - phase: 05-01
    provides: Product.cost_price nullable Integer column (models.py, on disk)
provides:
  - "Admin product create/edit form optional 'Giá nhập (VND)' field (COST-01)"
  - "create + edit persistence of cost_price (Integer VND, NULL when empty)"
  - "Negative cost_price rejected with 'Giá nhập không được âm' (NumberRange min=0)"
  - "COST-02 enforced: no public template leaks cost_price / 'Giá nhập'"
affects: [phase 8 profit calculation, admin-product-form, cost-price]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Optional() + NumberRange(min=0) optional integer field (matches sku/sort_order/admin_note)"
    - "explicit-kwargs Product() constructor in new_product passes cost_price"

key-files:
  created: []
  modified:
    - app/forms.py
    - app/admin.py
    - app/templates/admin/products/form.html

key-decisions:
  - "Rendered literal <label for=\"cost_price\">Giá nhập (VND)</label> instead of {{ form.cost_price.label }} to satisfy the plan's Task-2 verify gate, which greps the raw template for the literal label text (rendered HTML is byte-identical to WTForms default label)"
  - "Auto-fixed pre-existing edit_product bug: empty Optional() sort_order was written as NULL via populate_obj into a NOT NULL column, crashing edit; coerced to 0 to mirror new_product's `or 0`"

patterns-established:
  - "Optional numeric fields on ProductForm use Optional() + NumberRange(min=0, message=...) with a Vietnamese exact-match error message"

requirements-completed: [COST-01, COST-02]

# Metrics
duration: 7min
completed: 2026-08-02
---

# Phase 5 Plan 3: Cost-price field on admin product form Summary

**Optional 'Giá nhập (VND)' IntegerField on the admin product create/edit form with create+edit persistence, negative rejection ('Giá nhập không được âm'), NULL-when-empty, and a COST-02 guard keeping cost price off every public template**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-08-02T04:37:09Z
- **Completed:** 2026-08-02T04:43:58Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- `ProductForm.cost_price` IntegerField 'Giá nhập (VND)' with `Optional()` + `NumberRange(min=0, message='Giá nhập không được âm')` placed immediately after `price` in `app/forms.py` (no new imports needed — IntegerField/Optional/NumberRange already imported).
- `new_product()` explicit-kwargs constructor now passes `cost_price=form.cost_price.data or None` so create persists the value (edit already bound it via `form.populate_obj`).
- Admin form template renders the new full-width `.form-field` right after the "Giá (VND) | Thương hiệu" row: label, `<input class="input" min="0" step="1">` (integer VND, D-05), help-text "Chỉ quản trị viên xem được", and error loop. No `required`/`aria-required`, no new CSS/tokens/media queries.
- Behavioral verify confirmed: create persists cost_price=150000, edit updates to 200000, cost_price=-5 re-renders with "Giá nhập không được âm", empty submits NULL. COST-02 grep over `app/templates/public/**/*.html` finds no `cost_price` or `Giá nhập`.

## Task Commits

Each task was committed atomically:

1. **Task 1: ProductForm.cost_price + new_product persistence** - `24c4ef2` (feat)
2. **Task 2: cost_price field markup form.html + COST-02 public guard** - `97d540e` (feat)

**Plan metadata:** (committed by orchestrator)

## Files Created/Modified
- `app/forms.py` - Added `cost_price = IntegerField('Giá nhập (VND)', validators=[Optional(), NumberRange(min=0, message='Giá nhập không được âm')])` to ProductForm, after `price`.
- `app/admin.py` - `new_product()` passes `cost_price=form.cost_price.data or None`; `edit_product()` coerces empty `sort_order` to 0 after `populate_obj` (Rule 3 fix).
- `app/templates/admin/products/form.html` - Added cost_price `.form-field` block after the price/brand `form-row-2`. The pre-existing unrelated deletion (quantity help-text line) was left untouched and remains uncommitted in the working tree.

## Decisions Made
- **Literal label vs `{{ form.cost_price.label }}`:** The plan's UI-SPEC markup says `{{ form.cost_price.label }}`, but the Task-2 verify script greps the *raw* template file for the literal string `Giá nhập (VND)`. WTForms' `label` renderer produces exactly `<label for="cost_price">Giá nhập (VND)</label>`, so a hand-written literal `<label for="cost_price">` yields byte-identical rendered HTML while satisfying the verify gate and preserving the `for` accessibility association.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] edit_product crashed on empty optional sort_order (NOT NULL violation)**
- **Found during:** Task 1 (verify script, edit-persistence step)
- **Issue:** `edit_product()` uses `form.populate_obj(product)` (plan explicitly said "no change needed"). When the admin submits an empty optional `sort_order` (the verify script submits `sort_order: ''`), WTForms `Optional()` yields `None`, and `populate_obj` writes `None` into the `sort_order` column which is `nullable=False` → `sqlite3.IntegrityError: NOT NULL constraint failed: products.sort_order`. This is a pre-existing bug independent of the cost_price feature — `new_product()` avoids it via `sort_order=form.sort_order.data or 0`.
- **Fix:** After `form.populate_obj(product)`, added `if product.sort_order is None: product.sort_order = 0` — mirrors `new_product`'s `or 0` behavior. Root-cause fix in the shared path; minimal, no behavior change for non-empty values.
- **Files modified:** `app/admin.py` (edit_product)
- **Verification:** Task-1 verify now passes (edit returns 302 and persists cost_price).
- **Committed in:** `24c4ef2` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary for the plan's own verify gate to pass; corrects a genuine pre-existing crash in the edit route. No scope creep — change is one guard in the exact file the plan modifies.

## Issues Encountered
- Plan-internal inconsistency between UI-SPEC markup (`{{ form.cost_price.label }}`) and the Task-2 verify gate (grep for literal `Giá nhập (VND)` in raw template). Resolved via literal label that renders identically — see Decisions Made.
- Plan-internal ordering dependency: Task 1's verify asserts the negative-error message renders in the body, which requires Task 2's template markup to already exist. Implemented both code changes before running Task 1's verify, then committed them as two atomic task commits.

## User Setup Required

None - no external service configuration required. Field is admin-only; no new env vars, deps, or infra.

## Next Phase Readiness
- Admin can now record cost price alongside sale price; Phase 8 profit (revenue − cost) has its data source.
- `app/models.py` `Order.product_cost_price` (added in 05-02) already snapshots cost at order time; `Product.cost_price` is readable for profit reporting.
- No public surface changed; no migrations needed beyond 05-02's idempotent `init-db`.

## Self-Check: PASSED

- `app/forms.py`, `app/admin.py`, `app/templates/admin/products/form.html`, `05-03-SUMMARY.md` — all found.
- Commits `24c4ef2` and `97d540e` — both found in git history.
- `cost_price = IntegerField('Giá nhập (VND)', ...)` present in forms.py (line 16).
- `cost_price=form.cost_price.data or None` present in admin.py new_product (line 110).

---
*Phase: 05-data-model-migration*
*Completed: 2026-08-02*
