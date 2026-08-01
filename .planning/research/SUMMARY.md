# Project Research Summary — v1.1 Buy System

**Project:** StoreWeb — Vietnamese product catalog web
**Domain:** Extending v1.0 (Flask, single admin, SQLite, Vietnamese UI, Messenger contact) with order placement + order tracking + cost price + stats
**Researched:** 2026-08-02
**Confidence:** HIGH (ARCHITECTURE + PITFALLS grounded in codebase inspection; STACK/FEATURES synthesized inline after background agents hit provider 500s)

## Executive Summary

v1.1 replaces the "buy via Messenger" flow with a real order system, but stays deliberately minimal: **zero new dependencies**. Flask-SQLAlchemy + Flask-WTF + SQLite already cover the entire feature set. The core design moves are (1) a flat `Order` model (one product per order, no `OrderItem` join table, no cart) with **price/cost/name snapshots** so later product edits never corrupt historical revenue; (2) an integer status enum `Chờ xác nhận → Đã gói → Đã gửi → Đã nhận` (+ admin-only `Đã hủy`, no hard deletes); (3) a nullable admin-only `cost_price` on `Product`; (4) stats computed live via SQL aggregates (no cache table). Existing SQLite DBs need a lightweight idempotent migration (add column + create tables) — `db.create_all()` alone won't add columns.

## Stack additions
- **None.** All existing deps reused (Flask 3.1.3, Flask-SQLAlchemy 3.1.1, Flask-WTF 1.3.0, SQLite). Explicitly NOT added: payment gateway, flask-migrate (lightweight ALTER CLI instead), cart/OrderItem, charting lib, Redis/Celery, customer accounts.

## Feature table stakes
- **Order placement:** form on product detail (tên, SĐT, địa chỉ, số lượng, ghi chú), quantity ≥1 and ≤ stock, clear success feedback, form hidden when product unavailable, CSRF on public form. Keep Messenger strip as "hỏi thêm" (not "Mua").
- **Admin tracking:** paginated order list + status filter, order detail, status advance (đã gói → đã gửi → đã nhận) + cancelled bucket, status badges, reject backward transitions.
- **Cost price:** optional integer field, admin-only, never public.
- **Stats:** revenue (shipped+delivered only), profit = revenue − cost (NULL-safe), order counts by status, units sold, inventory counts. Stat cards with `format_price`.

## Watch Out For (top pitfalls)
1. **Migration on existing DBs** — `ALTER TABLE ADD COLUMN cost_price` leaves NULLs; profit math must COALESCE or it silently returns NULL. Migration CLI must be idempotent (guard with `PRAGMA table_info`).
2. **Public form spam** — CSRF + honeypot/min-length + server-side validation; no auth to lean on.
3. **Money math** — integer VND everywhere; never Float; NULL cost → treat as 0 for profit.
4. **SQLite write locks** — WAL + busy_timeout already in place; keep order commit short, avoid write-in-read.
5. **VN phone/address validation** — loose enough (10–11 digits, 0x/84x) to not reject real customers.
6. **Status integrity** — forward-only transitions; `Đã hủy` admin-only; never delete orders.
7. **Stats accuracy** — only shipped+delivered count as revenue/units sold; exclude cancelled.
8. **Cost price visibility** — never render to public templates.

## Suggested build order (from ARCHITECTURE.md)
Phase A: data model + migration → B: public order form → C: admin order list/detail/status → D: admin stats → E: polish.

---
*Research completed: 2026-08-02*
*Ready for roadmap: yes*
