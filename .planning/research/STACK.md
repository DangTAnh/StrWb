# Stack Research — v1.1 Buy System (order placement + tracking + stats)

**Domain:** Extending existing Flask product catalog (single admin, SQLite, self-hosted, Vietnamese)
**Researched:** 2026-08-02
**Confidence:** HIGH

## Executive Summary

**Zero new dependencies.** The v1.1 buy-system features (public order form, cost price column, admin order tracking, revenue/profit stats) are fully covered by the existing stack: Flask + Flask-SQLAlchemy + Flask-WTF + SQLite. No payment gateway (transactions settle on delivery), no background queue, no charting library, no flask-migrate.

## Recommended Stack — What's Already There (REUSE, don't add)

| Capability | Existing Piece | Why It Suffices |
|------------|----------------|-----------------|
| Order model + queries | Flask-SQLAlchemy 3.1.1 + SQLAlchemy 2.x | New `Order` model, `cost_price` column, `SUM`/`COUNT` aggregates — plain ORM + SQL. |
| Public order form + CSRF | Flask-WTF 1.3.0 | `OrderForm` (name/phone/address/quantity/note) renders `hidden_tag()`; CSRFProtect is already global. |
| Admin status form | Flask-WTF SelectField | `OrderStatusForm` with integer-enum choices + `coerce=int`. |
| Status enum | stdlib `enum` (module-level constants) | Integer enum maps cleanly to SQLite, trivial `WHERE status >= N` queries. |
| Money (VND) | existing integer columns | `price` is already `Integer`; `cost_price` and snapshots follow the same integer-VND pattern — no Decimal/Float. |
| Order timestamps | existing `utcnow` helper in models.py | Reuse for `created_at`/`updated_at`. |
| Price formatting | existing `format_price` filter | Stats cards + order tables use it. |

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Payment gateway (Stripe/MoMo/VNPay) | Transactions settle on delivery, offline, by phone — no online payment required | Order form + status tracking only |
| flask-migrate / Alembic | Only one new column + two new tables; `db.create_all()` + idempotent `ALTER TABLE` in a CLI command covers existing DBs | Lightweight migration CLI (see ARCHITECTURE.md §Schema Migration) |
| Cart / OrderItem join table | Requirement is "each order = 1 product" — an `OrderItem` table adds a query + template layer for zero value | Flat `Order` model with `product_id`, `quantity`, `price_at_order` |
| Charting lib (Chart.js etc.) | Single admin, low volume — plain HTML stat cards suffice | Stat cards with `format_price` |
| Redis / Celery | No async work (no emails/SMS, no resize on order) | N/A |
| Customer accounts / auth | Order form is anonymous by design | Server-side validation only |

## Version Compatibility (unchanged from v1.0)

All stack versions verified in v1.0 remain pinned in requirements.txt (Flask 3.1.3, Flask-SQLAlchemy 3.1.1, Flask-Login 0.6.3, Flask-WTF 1.3.0, Pillow, waitress 3.0.2). No new pins introduced by v1.1.

## Sources
- Existing requirements.txt + installed-environment verification (v1.0 research, HIGH)
- SQLite ALTER TABLE ADD COLUMN semantics (SQLite docs, HIGH)
- ARCHITECTURE.md (v1.1) — integration analysis, HIGH

---
*Stack research for: StoreWeb v1.1 Buy System (order placement + tracking + stats)*
*Researched: 2026-08-02*
