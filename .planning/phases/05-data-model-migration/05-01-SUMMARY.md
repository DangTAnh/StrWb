---
phase: 05-data-model-migration
plan: 01
subsystem: database
tags: [sqlalchemy, sqlite, orders, cost-price, snapshot]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: Product/ProductImage models, utcnow() helper, Integer VND pattern (D-05)
provides:
  - Product.cost_price column (Integer nullable VND)
  - Order model with snapshot pricing (name/sale/cost/qty) + customer info + VN status + timestamps
affects: [05-02, 05-03, phase-06-order-form, phase-07-admin-tracking, phase-08-stats]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Snapshot columns on Order (product_name/product_price/product_cost_price/quantity) so deleting a product never loses an order (ORD-04)"
    - "FK ondelete='SET NULL' + passive_deletes=True backref for delete-surviving orders"

key-files:
  created: []
  modified: [app/models.py]

key-decisions:
  - "Order keeps product_id FK nullable + full snapshot at order time; deleting a product nulls the FK, order survives (ORD-04)"
  - "Order status stored as VN label String, default 'Chờ xác nhận' (forward-only transitions enforced in Phase 7)"
  - "Order number = incrementing id, no formatted code"
  - "cost_price Integer nullable VND (D-05: never Float; COST-01: NULL = not entered)"

patterns-established:
  - "Order timestamps reuse utcnow() default/onupdate, matching Product"

requirements-completed: [ORD-04, COST-01]

# Metrics
duration: 5min
completed: 2026-08-02
---

# Phase 05: Data Model + Migration Plan 01 Summary

**Product.cost_price column (Integer nullable VND) + Order model with full snapshot pricing (name/sale/cost/qty), customer PII, VN status label, and a delete-surviving FK — the data-model foundation for the v1.1 Buy System**

## Performance

- **Duration:** 5 min
- **Started:** 2026-08-02T03:37:00Z
- **Completed:** 2026-08-02T03:42:06Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Added `Product.cost_price` — Integer nullable VND column right after `price`, matching the codebase money pattern (D-05 never Float), NULL = not entered (COST-01)
- Added `Order` model (`orders` table) with all 13 columns: id, product_id FK, snapshot columns (product_name, product_price, product_cost_price, quantity), customer PII (name, phone, address, note), status (VN label default 'Chờ xác nhận'), created_at/updated_at (utcnow)
- FK `product_id → products.id` with `ondelete='SET NULL'` and `passive_deletes=True` backref — deleting a product nulls the FK, the order and its snapshot survive (ORD-04)
- `db.create_all()` on a fresh DB builds the `orders` table exactly per the model definition (PLAT-05 half), verified via SQLAlchemy inspect

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Product.cost_price + Order model (snapshot pricing)** - `955b5ed` (feat)

**Plan metadata:** SUMMARY.md committed with plan completion

## Files Created/Modified
- `app/models.py` - Added `Product.cost_price` column and `Order` class (21 insertions, no deletions)

## Decisions Made
- None beyond plan spec — executed exactly as written

## Deviations from Plan

None - plan executed exactly as written.

**Total deviations:** 0
**Impact on plan:** None

## Issues Encountered
None — verify script exited 0 printing `TASK_OK` on first run.

## User Setup Required

None - no external service configuration required. This is a model-only slice; the schema change is exercised against a fresh in-memory DB.

## Next Phase Readiness
- `Product.cost_price` exists for 05-03 (admin form field, COST-02) and Phase 8 profit stats
- `Order` model ready for Phase 6 order form to write snapshots, Phase 7 admin tracking to read status + snapshot
- `orders` table is created automatically by the existing `db.create_all()` path — no manual migration needed for fresh DBs
- ORD-10 (cart) and ORD-12 (stock auto-decrement) remain deferred to v2 as planned

---
*Phase: 05-data-model-migration*
*Completed: 2026-08-02*

## Self-Check: PASSED
- Created file `.planning/phases/05-data-model-migration/05-01-SUMMARY.md` — FOUND
- Task commit `955b5ed` — FOUND
