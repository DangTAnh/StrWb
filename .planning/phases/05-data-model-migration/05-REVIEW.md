---
phase: 05-data-model-migration
reviewed: 2026-08-02T12:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - app/models.py
  - app/db.py
  - app/forms.py
  - app/admin.py
  - app/templates/admin/products/form.html
findings:
  critical: 0
  warning: 2
  info: 3
  total: 5
status: resolved
---

# Phase 5: Code Review Report — Data Model Migration

**Reviewed:** 2026-08-02T12:00:00Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** resolved (2 warnings fixed in commit `f97784d`)

## Summary

Reviewed the Phase 5 (data-model-migration) changes across plans 05-01, 05-02, 05-03:

- **`app/models.py`** — added `Product.cost_price` (Integer, nullable, VND, D-05-compliant) and the new `Order` model with 13 columns, snapshot pricing (ORD-04), nullable `product_id` FK with `ondelete='SET NULL'`, and `passive_deletes=True` backref.
- **`app/db.py`** — `init_db_command` extended with an idempotent migration: `db.create_all()` then a `PRAGMA table_info(products)` guard before `ALTER TABLE ... ADD COLUMN cost_price` inside `engine.begin()`.
- **`app/forms.py`** — `cost_price = IntegerField('Giá nhập (VND)', [Optional(), NumberRange(min=0)])`.
- **`app/admin.py`** — `new_product()` persists `cost_price`; `edit_product()` gained a `sort_order = 0` guard after `populate_obj`.
- **`app/templates/admin/products/form.html`** — full-width `.form-field` block for cost_price.

The two documented deviations are both sound: the `sort_order = 0` guard correctly prevents the pre-existing `populate_obj`-writes-`None`-into-NOT-NULL IntegrityError (only `sort_order` is nullable-optional among NOT NULL columns; `name`/`price`/`quantity` are `InputRequired`/`DataRequired`, `discontinued` is a BooleanField), and the hand-written `<label for="cost_price">` matches WTForms' generated `id="cost_price"` so the label binding works. The pre-existing uncommitted deletion of the quantity help-text in `form.html` was noted and excluded per instructions.

COST-02 is satisfied: `cost_price` appears only in the admin form template; public templates (`public/index.html`, `public/product_detail.html`, `public/search.html`) never reference it, and no JSON/serialization endpoint dumps model columns.

The migration is idempotent and correct for both fresh and v1.0 databases (verified: `create_all` uses `checkfirst=True`; the PRAGMA guard prevents duplicate-column ALTERs; `ALTER` runs in a transaction). CSRF is preserved on all admin POSTs (`form.hidden_tag()` in the product form, manual `csrf_token()` in delete.html, global `CSRFProtect`). No SQL injection vectors found — all queries are ORM, the migration uses literal identifiers only.

No Critical findings. Two Warnings and three Info items are documented below.

## Resolution Log

- **WR-01** — FIXED in `f97784d`: added `PRAGMA foreign_keys=ON` to the SQLite connect listener (`app/__init__.py:26`). Verified: deleting a product with orders sets `orders.product_id` to NULL via `ON DELETE SET NULL`; image cascade (`cascade='all, delete-orphan'`) still works with FK on; `delete_product` succeeds.
- **WR-02** — FIXED in `f97784d`: `cost_price=form.cost_price.data` (dropped `or None`). Verified: cost_price `0` now persists as `0` (not NULL); empty input still NULL via `Optional()`.
- **IN-01 / IN-02 / IN-03** — Deferred. IN-01 is cosmetic (hand-written label renders identically to `{{ form.cost_price.label }}`; binding verified). IN-02 is a process note (flask-migrate adoption deferred to a future schema-change phase). IN-03 (`orders.quantity >= 1` CHECK) is enforced at the Phase 6 order form (ORD-02) and adding a DB CHECK now would drift from already-migrated DBs — deferred.

## Warnings

### WR-01: SQLite FK enforcement is OFF — `ondelete='SET NULL'` never fires, orders keep dangling `product_id`

**File:** `app/models.py:77` (FK declaration) and `app/models.py:90` (`passive_deletes=True`); root cause in `app/__init__.py:19-26`

**Issue:** The new `Order.product_id` FK declares `ondelete='SET NULL'` and the backref uses `passive_deletes=True`, which explicitly tells SQLAlchemy to skip loading/null-ing child rows and rely on the database. But the SQLite connect listener in `app/__init__.py:19-26` sets only `journal_mode=WAL` and `busy_timeout` — it never issues `PRAGMA foreign_keys=ON`. SQLite defaults FK enforcement to OFF, and this was confirmed at runtime (`PRAGMA foreign_keys = 0`). Consequently, deleting a Product that has orders leaves every `orders.product_id` pointing at a now-deleted product id instead of being SET NULL. The FK is also inert for insert validation (an Order can reference a nonexistent product). The snapshot columns keep the order data self-contained, so there is no data loss today, but the documented SET NULL semantics are silently not honored — a correctness gap introduced by this phase's new FK dependency.

**Fix:** Enable FK enforcement in the existing connect listener:
```python
@event.listens_for(Engine, 'connect')
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')  # enables ON DELETE SET NULL for orders.product_id
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA busy_timeout=30000')
        cursor.close()
```
(If enforcement is enabled, verify `delete_product` in `app/admin.py:171-172` still succeeds — with `passive_deletes=True` the ORM does not load orders, so the DB-level SET NULL handles them and the commit will not raise.)

### WR-02: `cost_price=form.cost_price.data or None` coerces a legitimate cost of 0 VND to NULL

**File:** `app/admin.py:110`

**Issue:** The form validator is `NumberRange(min=0)`, which explicitly accepts 0 as a valid cost (free/zero-cost stock is meaningful for retail). But `form.cost_price.data or None` converts `0` to `None` due to Python truthiness. The result is asymmetric with `price`: a sale price of 0 is persisted, but an entered cost of 0 is silently dropped to "not entered" (NULL), and the Order snapshot `product_cost_price` records the same loss. This is a data-fidelity bug in a money field.

**Fix:** The `Optional()` validator already yields `None` for empty input, so the `or None` is both redundant and harmful:
```python
cost_price=form.cost_price.data,  # Optional() yields None on empty; preserves 0
```

## Info

### IN-01: Hand-written cost_price label duplicates field label text (drift risk)

**File:** `app/templates/admin/products/form.html:32`

**Issue:** The label is hard-coded as `<label for="cost_price">Giá nhập (VND)</label>`, duplicating the label text defined on the form field (`app/forms.py:16`). The `for`/`id` binding is correct (WTForms renders `id="cost_price"`), so there is no functional defect, but the sibling optional fields use `{{ form.field.label }}`; a future label-text change in `forms.py` will silently leave this template stale.

**Fix:** Use the WTForms-generated label for consistency, keeping the help-text:
```html
{{ form.cost_price.label }}
{{ form.cost_price(class="input", min="0", step="1") }}
<p class="help-text">Chỉ quản trị viên xem được</p>
{% for error in form.cost_price.errors %}<span class="field-error">{{ error }}</span>{% endfor %}
```

### IN-02: Migration is a one-off hand-rolled guard; project guidance now points to flask-migrate

**File:** `app/db.py:32-38`

**Issue:** The guard is idempotent and correct for `cost_price`, but it only checks column *existence* (not type), and it is a bespoke one-off that must be duplicated by hand for every future schema change. `CLAUDE.md` ("flask-migrate", "When to Use", "What NOT to Use") states migrations should be introduced once the model gains columns/tables — this phase is exactly that trigger (new `cost_price` column + new `orders` table), yet the phase hand-rolled the ALTER instead of adopting Alembic.

**Fix:** Adopt `flask-migrate` (Alembic) now that the schema is in flux, or at minimum have the guard verify the column type (`PRAGMA table_info` returns the type in `row[2]`) so a mismatched pre-existing column is not silently accepted.

### IN-03: `Order.quantity` has no DB-level CHECK constraint (>= 1)

**File:** `app/models.py:81`

**Issue:** The model comment defers quantity validation to the Phase 6 form, and no Order rows can be created yet, so there is no live path to a 0/negative quantity. But SQLite will accept any integer, and adding a `CheckConstraint` now is free while the `orders` table is brand new — adding it later requires a table rebuild (SQLite cannot add CHECK constraints via `ALTER TABLE`).

**Fix:** Add a check constraint to the model now:
```python
__table_args__ = (db.CheckConstraint('quantity >= 1', name='ck_orders_quantity_positive'),)
```

---

_Reviewed: 2026-08-02T12:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
