---
phase: 06-public-order-form
plan: 01
subsystem: database
tags: [flask, sqlalchemy, sqlite, migration, order, orderitem]

# Dependency graph
requires:
  - phase: 05-data-model-migration
    provides: Order model (snapshot schema), Product.cost_price, PRAGMA foreign_keys=ON (WR-01)
provides:
  - Order refactored to customer-only schema (id, customer_name, customer_phone, customer_address, customer_note, status, created_at, updated_at)
  - OrderItem model + table (snapshot product_name/price/cost_price/quantity, FK order_id CASCADE, FK product_id nullable SET NULL, CheckConstraint quantity >= 1)
  - init-db idempotent orders guard (PRAGMA table_info + DROP only when 0 rows, ClickException on legacy data)
affects: [06-02 cart session, 06-03 checkout, 07-admin-order-tracking]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Idempotent SQLite migration: PRAGMA table_info guard inside engine.begin() transaction, DROP only when COUNT(*) == 0, second create_all() to recreate new schema"
    - "Snapshot pattern: order_items stores product_name/price/cost_price at order time; product deletion SET NULLs product_id but keeps snapshot (no data loss)"

key-files:
  created: []
  modified:
    - app/models.py
    - app/db.py

key-decisions:
  - "orders giữ customer + status (8 cột), bỏ snapshot trực tiếp; order_items chứa snapshot từng sản phẩm (ORD-10a)"
  - "order_id FK ondelete='CASCADE' + ORM cascade all, delete-orphan; product_id FK ondelete='SET NULL' nullable + passive_deletes — xóa sản phẩm giữ snapshot đơn"
  - "CheckConstraint quantity >= 1 trên order_items (IN-03 Phase 5 deferred) — rẻ vì bảng mới"
  - "Migration: DROP orders legacy chỉ khi 0 rows; nếu có dữ liệu raise ClickException 'Manual migration' — không bao giờ tự DROP dữ liệu"

patterns-established:
  - "Pattern migration idempotent PLAT-05: create_all (tạo bảng thiếu) + PRAGMA guard + engine.begin() transaction + create_all lại sau rebuild"
  - "Verify chỉ trên temp DB (patch app_module.BASE_DIR), không bao giờ chạm data/app.db thật"

requirements-completed: [ORD-10a]

# Metrics
duration: 6min
completed: 2026-08-02
---

# Phase 6 Plan 1: Order + OrderItem Refactor Summary

**Refactor Order → Order + OrderItem (ORD-10a): orders chỉ giữ thông tin khách + status; order_items lưu snapshot từng sản phẩm với FK order_id CASCADE + product_id nullable SET NULL + CheckConstraint quantity >= 1; init-db migration idempotent rebuild orders legacy (guard PRAGMA table_info, DROP chỉ khi 0 rows) mà không mất dữ liệu**

## Performance

- **Duration:** 6 min
- **Started:** 2026-08-02T08:03:44Z
- **Completed:** 2026-08-02T08:09:30Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `Order` reduced to 8 customer+status columns; snapshot columns + `product` relationship removed
- New `OrderItem` model: 8 columns, FK `order_id` → `orders.id` CASCADE, FK `product_id` → `products.id` nullable SET NULL, `CheckConstraint('quantity >= 1')` (IN-03)
- `init-db` idempotent orders guard: rebuilds legacy Phase 5 `orders` (snapshot schema) into customer-only schema; only DROPs when `COUNT(*) == 0`; raises `ClickException('Manual migration...')` when legacy data present — never destroys data
- Verified on temp copies only (5 cases A–E pass); real `data/app.db` untouched (still v1.0, no orders/order_items)

## Task Commits

Each task was committed atomically:

1. **Task 1: Refactor Order model + thêm OrderItem model** - `b93a0ee` (feat)
2. **Task 2: init-db idempotent — orders legacy guard + tạo order_items** - `70fa7d1` (feat)

**Plan metadata:** SUMMARY.md committed with plan completion

## Files Created/Modified
- `app/models.py` - Order refactored (customer+status only) + OrderItem added (snapshot + FK CASCADE/SET NULL + CheckConstraint)
- `app/db.py` - `init_db_command` extended: orders guard (PRAGMA table_info + DROP when 0 rows + ClickException on data) + second `db.create_all()` to recreate new orders schema

## Decisions Made
- Followed plan as specified. Snapshot taken at order time per product (ORD-10a); quantity >= 1 enforced at DB level (IN-03).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Verify scripts used deprecated SQLAlchemy 1.x `engine.execute()` API**
- **Found during:** Task 1 verify
- **Issue:** Plan's verify script called `db.engine.execute(text(...))`, removed in SQLAlchemy 2.0 (`AttributeError: 'Engine' object has no attribute 'execute'`)
- **Fix:** Adapted the verify invocation to SQLAlchemy 2.0 `with db.engine.connect() as conn: conn.execute(...)`. App code (`app/models.py`, `app/db.py`) unchanged.
- **Files modified:** none (verify script invocation only, not committed app code)
- **Verification:** Task 1 verify passes printing `TASK_OK`
- **Committed in:** n/a (part of task 1 verification; app code committed in `b93a0ee`)

---

**Total deviations:** 1 auto-fixed (1 bug in plan's verify script)
**Impact on plan:** All auto-fixes were in the verification harness (SQLAlchemy 2.0 API compatibility), not app code. No scope creep.

## Issues Encountered
- None. Both task verifies passed on first run after the SQLAlchemy 2.0 API adaptation.

## Stub Tracking
None — no stubs introduced. `OrderItem.product_cost_price` is nullable Integer but that is a real data-model choice (NULL = product has no cost), not a stub.

## Threat Flags
No new security surface beyond the plan's threat model. `OrderItem.product_cost_price` (T-06-03) is an Integer nullable VND snapshot; no public route/template renders it in Phase 6.

## Next Phase Readiness
- Ready for 06-02 (cart session) and 06-03 (checkout): `Order` + `OrderItem` models in place, `init-db` will create `order_items` on the real DB when the operator runs it post-Phase-6.
- Blockers: none. Operator action deferred to after Phase 6: run `flask --app app init-db` on real `data/app.db` (still v1.0) with valid `ADMIN_PASSWORD` in `.env`.

## Self-Check: PASSED
- FOUND: app/models.py (OrderItem class, CheckConstraint, FK CASCADE/SET NULL)
- FOUND: app/db.py (PRAGMA table_info(orders) guard, DROP TABLE orders, Manual migration, second create_all)
- FOUND: .planning/phases/06-public-order-form/06-01-SUMMARY.md
- FOUND: commit b93a0ee (Task 1)
- FOUND: commit 70fa7d1 (Task 2)

---
*Phase: 06-public-order-form*
*Completed: 2026-08-02*
