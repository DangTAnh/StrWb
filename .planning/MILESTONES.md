# Milestones

## v1.0 MVP (Shipped: 2026-08-01)

**Phases completed:** 4 phases, 12 plans, 38 tasks

**Key accomplishments:**

1. **Phase 1 — Scaffold + Auth + Data Model:** Flask app factory + 3 blueprints (public/admin/auth), Flask-Login admin login/logout + protection, SQLite WAL + busy_timeout, `flask init-db` CLI (rejects placeholder/short passwords), full VN UI chrome (`lang="vi"`).
2. **Phase 2 — Admin CRUD + Images:** Full product CRUD with Flask-WTF validation + CSRF, multi-image galleries (UUID filenames, thumbnails, delete-orphan cascade, batch-aware uploads), `1.200.000₫` price formatting, status badges (Còn hàng / Hết hàng / Ngừng bán) + stock tracking.
3. **Phase 3 — Public Catalog + Search + Contact:** Responsive grid 2/3/4 cột, detail page + gallery, search không dấu (NFD + casefold) over name/description, Messenger contact strip/CTA mọi trạng thái, pagination 12/trang.
4. **Phase 4 — Polish + Deploy:** Cả 5 deferral UI Phase 3 fixed (contrast #B91C1C 6.19:1 AA, 2x-DPR gallery, search out-of-range redirect, ₫ glyph PASS, spec-sync) + responsive audit 480/768/1200 clean; deploy waitress (Windows) + gunicorn/systemd (Linux) + nginx HTTPS + admin rate-limit; hardening verified SC-1..SC-5 (40+ checks, temp-DB isolated).
5. **Milestone audit PASSED** — 28/28 requirements, 4/4 phases, 6/6 E2E flows (`398d437`).
6. **Zero open review findings** — code review + UI review cả 4 phase đều fixed (Phase 4 UI 24/24, 0 findings).

**Known deferred items at close:** 1 (see STATE.md Deferred Items)

---
