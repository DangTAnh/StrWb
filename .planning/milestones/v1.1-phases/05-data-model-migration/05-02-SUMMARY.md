---
phase: 05-data-model-migration
plan: 02
subsystem: database
tags: [sqlite, migration, sqlalchemy, cli, idempotent]

# Dependency graph
requires:
  - phase: 05-01
    provides: Order model + Product.cost_price column on disk
provides:
  - init-db CLI now migrates v1.0 DBs safely: adds products.cost_price via PRAGMA-guarded ALTER and creates the orders table
affects: [06-order-management, 07-order-lifecycle]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "PRAGMA table_info(products) guard before ALTER TABLE ADD COLUMN — idempotent migration for existing SQLite DBs"
    - "engine.begin() transaction wrapper for DDL — commit on success / rollback on error"

key-files:
  created: []
  modified: [app/db.py]

key-decisions:
  - "Migrate existing v1.0 DBs by extending init-db (single code path) instead of a separate migration script — PRAGMA guard + ALTER covers old DBs, create_all covers fresh DBs"
  - "cost_price added as nullable INTEGER (D-05: money is Integer VND, never Float); ALTER adds no DEFAULT so existing rows are untouched"

patterns-established:
  - "Migration guard: run PRAGMA table_info, check column exists, ALTER only if missing — idempotent across repeated runs"

requirements-completed: [PLAT-05]

# Metrics
duration: 12min
completed: 2026-08-02
---

# Phase 5 Plan 2: Safe Idempotent init-db Migration Summary

**init-db CLI now migrates existing v1.0 SQLite DBs without data loss: PRAGMA-guarded `ALTER TABLE products ADD COLUMN cost_price INTEGER` plus `create_all` for the missing orders table, all in one code path.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-08-02T10:44:00Z
- **Completed:** 2026-08-02T10:56:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Added `from sqlalchemy import text` import to `app/db.py`
- Added PRAGMA guard + ALTER for `products.cost_price` directly after `db.create_all()` in `init_db_command`
- `db.create_all()` creates the missing `orders` table (IF NOT EXISTS semantics — never alters existing tables)
- Verified on a **copy of the real v1.0 `data/app.db`**: `orders` + `cost_price` appear, row counts of every pre-existing table unchanged (no data loss)
- Verified idempotency: running `init-db` a second time exits 0, no column duplication, no data change
- Verified fresh DB: `products` already has `cost_price` (from model), `orders` created empty

## Task Commits

Each task was committed atomically:

1. **Task 1: init-db idempotent — PRAGMA guard + ALTER cost_price** - `e65129d` (feat)

## Files Created/Modified
- `app/db.py` - init-db now runs a PRAGMA-guarded `ALTER TABLE products ADD COLUMN cost_price INTEGER` after `db.create_all()`; admin password checks and upsert unchanged

## Decisions Made
- Followed plan exactly — extended `init-db` (the existing CLI entry point) as the single migration path for both fresh and v1.0 DBs (PLAT-05)
- `cost_price` nullable INTEGER, no DEFAULT on ALTER — existing rows untouched, consistent with D-05 (money never Float)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required

**Operator note (required before Phase 6):** migrate the real `data/app.db` by running `flask --app app init-db` with a valid `ADMIN_PASSWORD` in the environment/.env. init-db also re-hashes the admin password from env, so a valid password is required.

## Next Phase Readiness
- Real DB migration is pending an operator-run `flask --app app init-db` (deliberately not run during execution to avoid touching the real DB)
- Phase 6 (order management) can rely on `orders` table + `products.cost_price` existing after that one command
- No blockers

---
*Phase: 05-data-model-migration*
*Completed: 2026-08-02*

## Self-Check: PASSED

- `app/db.py` exists with PRAGMA guard + ALTER (verified by execution test)
- `05-02-SUMMARY.md` exists in `.planning/phases/05-data-model-migration/`
- Commit `e65129d` present in git history
