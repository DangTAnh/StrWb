---
phase: 05-data-model-migration
verified: 2026-08-02T13:30:00Z
status: human_needed
score: 5/5 must-haves verified
overrides_applied: 0
re_verification: false
human_verification:
  - test: "Open the admin product create/edit form in a browser and confirm the 'Giá nhập (VND)' field renders as a full-width .form-field directly below the 'Giá (VND) | Thương hiệu' row, with the help-text 'Chỉ quản trị viên xem được' and no required asterisk."
    expected: "Field renders cleanly with label binding, integer input (min=0 step=1), and help-text. No layout break in the existing form."
    why_human: "HTML presence and round-trip persistence are verified programmatically, but the visual layout of the new field inside the existing admin form can only be confirmed in a browser."
---

# Phase 5: Data Model + Migration Verification Report

**Phase Goal:** Order model with snapshot pricing and Product cost_price column, safe idempotent migration for existing SQLite DBs, cost price field on admin product form
**Verified:** 2026-08-02T13:30:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Success Criteria Verification

| # | Success Criterion | Status | Evidence |
|---|-------------------|--------|----------|
| 1 | Order model exists storing customer info (name, phone, address, quantity, note) plus snapshot of product name, sale price, and cost price at order time | ✓ VERIFIED | `app/models.py:73-90` — `Order` model with all 13 columns. Live DB inspection (`PRAGMA table_info(orders)`) confirmed: `product_name` (NOT NULL), `product_price` (Integer NOT NULL), `product_cost_price` (Integer nullable), `quantity` (NOT NULL), `customer_name/phone/address` (NOT NULL), `customer_note` (nullable), `status` (NOT NULL, default 'Chờ xác nhận'), timestamps. Snapshot values are stored columns — not live references to `Product.price`. FK `product_id → products.id` nullable with `ondelete='SET NULL'` (confirmed via `PRAGMA foreign_key_list(orders)` → `SET NULL`). |
| 2 | Product model has a nullable `cost_price` column | ✓ VERIFIED | `app/models.py:28` — `cost_price = db.Column(db.Integer, nullable=True)`. Column created via migration as `INTEGER` nullable, no default (confirmed in migration test). Integer only, D-05 compliant (no Float). |
| 3 | Migration is idempotent — adding `cost_price` and `orders` table runs safely on existing v1.0 SQLite DBs without data loss | ✓ VERIFIED | Ran `init-db` twice against a COPY of the real v1.0 `data/app.db` (patched `app.BASE_DIR` to temp dir before `create_app`, SECRET_KEY/ADMIN_PASSWORD set). Run 1: exit 0, `Migrated: added products.cost_price (v1.0 -> v1.1)`, orders table created, data preserved (products 1→1, admin_users 1→1). Run 2: exit 0, `cost_price` appears exactly once (no dup), data unchanged. `app/db.py:34-38` — `PRAGMA table_info(products)` guard before `ALTER TABLE products ADD COLUMN cost_price INTEGER` inside `engine.begin()`. Real `data/app.db` confirmed untouched after tests. |
| 4 | Admin product create/edit form includes an optional cost price field | ✓ VERIFIED | `app/forms.py:16` — `cost_price = IntegerField('Giá nhập (VND)', [Optional(), NumberRange(min=0, message='Giá nhập không được âm')])`. `app/templates/admin/products/form.html:31-36` — full-width `.form-field` after price/brand row with help-text 'Chỉ quản trị viên xem được', no required asterisk. Round-trip via test client: create 150000 persists; edit 0 preserved as 0; edit empty → NULL; edit negative → rejected ('Giá nhập không được âm'), value unchanged; edit 200000 persists. |
| 5 | Cost price never appears on any public-facing page | ✓ VERIFIED | Grep across `app/templates/public/**` for `cost_price|Giá nhập` — no matches. Rendered GET responses for `/`, `/search`, `/products/{id}` contain no `cost_price` or `Giá nhập`. `cost_price` appears only in `app/models.py`, `app/db.py`, `app/forms.py`, `app/admin.py`, and `app/templates/admin/products/form.html`. No JSON/serialization endpoint dumps model columns (only docstring match for `jsonify`/`serialize`). |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `app/models.py` | Product.cost_price Integer nullable + Order model 13 cols + snapshot | ✓ VERIFIED | cost_price Integer nullable (line 28); Order with snapshot columns, customer PII, VN status, utcnow timestamps |
| `app/db.py` | init-db idempotent: create_all + PRAGMA guard + ALTER | ✓ VERIFIED | PRAGMA table_info guard, ALTER inside engine.begin(); ran twice on v1.0 DB copy |
| `app/forms.py` | ProductForm.cost_price IntegerField Optional + NumberRange(min=0) | ✓ VERIFIED | `IntegerField('Giá nhập (VND)', [Optional(), NumberRange(min=0)])` |
| `app/admin.py` | new_product persists cost_price; edit via populate_obj + sort_order guard | ✓ VERIFIED | `cost_price=form.cost_price.data` (line 110); `sort_order = 0` guard after populate_obj (line 144-145) |
| `app/templates/admin/products/form.html` | cost_price field after Giá/Thương hiệu row | ✓ VERIFIED | Rendered in admin create and edit forms (test client) |
| `app/__init__.py` | SQLite `PRAGMA foreign_keys=ON` listener (review fix WR-01) | ✓ VERIFIED | Line 26 — FK enforcement enabled; orders.product_id SET NULL semantics now honored |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `Order.product_id` | `products.id` | `ForeignKey(..., ondelete='SET NULL')` + `passive_deletes=True` + `PRAGMA foreign_keys=ON` listener | ✓ WIRED | FK present in model; `PRAGMA foreign_key_list(orders)` shows `SET NULL`; enforcement enabled in `app/__init__.py:26` |
| `Order.product_name/price/cost_price` | order-time snapshot | stored columns, not live `Product` refs | ✓ WIRED | Snapshot columns are plain Integer/String columns; no relationship reads live product price |
| `init_db_command` | products table | PRAGMA table_info guard before ALTER | ✓ WIRED | Verified idempotent on v1.0 DB copy |
| `init_db_command` | orders table | `db.create_all()` (checkfirst) after `from . import models` | ✓ WIRED | orders created on fresh and v1.0 DBs |
| `form.cost_price` | `app/forms.py` ProductForm | `{{ form.cost_price(...) }}` render | ✓ WIRED | Rendered in admin create/edit forms |
| `new_product` | ProductForm.cost_price | `cost_price=form.cost_price.data` | ✓ WIRED | Round-trip persisted 150000/0/200000; NULL on empty |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| Order snapshot cols | product_name/price/cost_price | populated at order time (Phase 6 write path) | N/A this phase — data model only, no write route yet | ✓ FLOWING (columns exist; write route is Phase 6) |
| cost_price on admin form | `form.cost_price.data` → `Product.cost_price` | WTForms field → admin.py constructor/populate_obj → DB | ✓ Real data flows (round-trip tested: 150000/0/NULL/200000 persisted correctly) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Migration on v1.0 DB copy | `init-db` run 1 (temp copy of real data/app.db) | exit 0, cost_price added, orders created, data preserved | ✓ PASS |
| Migration idempotency | `init-db` run 2 | exit 0, cost_price once, data unchanged | ✓ PASS |
| Create persists cost_price | POST `/admin/products/new` cost_price=150000 | persisted 150000 | ✓ PASS |
| Zero cost preserved | POST edit cost_price=0 | persisted 0 (not NULL) | ✓ PASS |
| Empty cost → NULL | POST edit cost_price='' | persisted NULL | ✓ PASS |
| Negative cost rejected | POST create/edit cost_price=-5/-99 | re-rendered with 'Giá nhập không được âm', no write | ✓ PASS |
| Edit update | POST edit cost_price=200000 | persisted 200000 | ✓ PASS |
| Public leak check | GET `/`, `/search`, `/products/{id}` | no cost_price / 'Giá nhập' in rendered HTML | ✓ PASS |
| Admin list leak | GET `/admin/products` | no cost_price / 'Giá nhập' | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| ORD-04 | 05-01 | Each order stores snapshot of product name + sale price + cost price at order time | ✓ SATISFIED | Order model snapshot columns (product_name, product_price, product_cost_price, quantity) confirmed in live schema |
| COST-01 | 05-01, 05-03 | Admin enters optional cost price (admin-only) for products | ✓ SATISFIED | Form field + create/edit persistence round-trip verified |
| COST-02 | 05-03 | Cost price never shown to customers | ✓ SATISFIED | No public template/render leak; cost_price only in admin files |
| PLAT-05 | 05-02 | Safe migration for old DB — add cost_price + orders table (idempotent, no data loss) | ✓ SATISFIED | Idempotency test on real v1.0 DB copy: 2 runs, no data loss, no dup column |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | TBD/FIXME/XXX debt markers | None found | — |
| — | — | Stub/placeholder implementations | None found | — |
| — | — | Hardcoded empty data reaching render | None found | — |

All `placeholder` grep hits are legitimate CSS/HTML input-placeholder attributes — not debt markers.

### Human Verification Required

1. **Admin form field visual layout**
   - **Test:** Open the admin product create/edit form in a browser; confirm the 'Giá nhập (VND)' field renders as a full-width `.form-field` directly below the 'Giá (VND) | Thương hiệu' row, with help-text 'Chỉ quản trị viên xem được' and no required asterisk.
   - **Expected:** Field renders cleanly with label binding, integer input (min=0 step=1), and help-text. No layout break in the existing form.
   - **Why human:** HTML presence and round-trip persistence are verified programmatically, but the visual layout of the new field inside the existing admin form can only be confirmed in a browser.

### Operational Note (not a gap)

The real `data/app.db` is still v1.0 schema (no `cost_price`, no `orders` table). Phase 6 requires an operator to run `flask --app app init-db` with a valid `ADMIN_PASSWORD` before order routes can write. The migration command is proven correct against a copy of this exact DB (both runs exit 0, no data loss).

### Gaps Summary

No gaps found. All 5 roadmap success criteria are met with code-level and behavioral evidence. The single human-verification item is a lightweight visual confirmation of the new admin form field; all functional behavior is verified programmatically.

---

_Verified: 2026-08-02T13:30:00Z_
_Verifier: Claude (gsd-verifier)_
