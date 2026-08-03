# Milestones

## v1.1 Buy System (Shipped: 2026-08-03)

**Phases completed:** 5 phases, 15 plans, 22 tasks

**Key accomplishments:**

- init-db CLI now migrates existing v1.0 SQLite DBs without data loss: PRAGMA-guarded `ALTER TABLE products ADD COLUMN cost_price INTEGER` plus `create_all` for the missing orders table, all in one code path.
- Optional 'Giá nhập (VND)' IntegerField on the admin product create/edit form with create+edit persistence, negative rejection ('Giá nhập không được âm'), NULL-when-empty, and a COST-02 guard keeping cost price off every public template
- Refactor Order → Order + OrderItem (ORD-10a): orders chỉ giữ thông tin khách + status; order_items lưu snapshot từng sản phẩm với FK order_id CASCADE + product_id nullable SET NULL + CheckConstraint quantity >= 1; init-db migration idempotent rebuild orders legacy (guard PRAGMA table_info, DROP chỉ khi 0 rows) mà không mất dữ liệu
- Session cart (ORD-10): CartForm + 4 public routes (add/update/remove/view) with server-side qty validation, cart.html line-item table with format_price totals and empty state, nav cart-badge (len session cart), and a status-gated add-to-cart block replacing the detail-page Messenger CTA (ORD-10b) with stale-item filtering + flash info (ORD-03) — zero new dependencies
- Checkout đặt hàng nhiều sản phẩm (ORD-01/02/03/05, ORD-10a): CheckoutForm (tên/SĐT/địa chỉ bắt buộc, ghi chú tùy chọn, SĐT 8-11 chữ số qua Regexp + digit-count, honeypot 'website') + route POST /cart/checkout (honeypot silent reject → empty-cart guard → form.validate → server re-validate từng món available + 1≤qty≤tồn kho → tạo 1 Order + nhiều OrderItem snapshot trong 1 commit → xóa giỏ + flash success + redirect về trang chi tiết) + partial `_checkout_form.html` (CSRF + honeypot + 4 field) được cart.html include — zero new dependencies, tồn kho KHÔNG giảm (ORD-12 → v2)
- Admin order tracking (ORD-06/07/08/09): paginated order list with status filter + detail view (customer info, item snapshots, timestamps) + forward-only status flow Chờ xác nhận → Đã gói → Đã gửi → Đã nhận (+ Đã hủy) — server-side TRANSITION_MAP + stepper UI, zero new dependencies
- Admin stats (STAT-01..04): NULL-safe revenue + profit (đơn Đã gửi + Đã nhận), orders-by-status breakdown, units sold, inventory counts — all re-queried per GET, no cache drift
- v1.1 polish + verification: F-01..F-06 + R-01/R-02 UI fixes, full 16-req verification harness (TASK_OK, isolated temp DBs, v1.0 regression smoke), 15/15 responsive screenshots, deploy docs with v1.1 migration + backup
- Milestone audit PASSED — 19/19 requirements, 5/5 phases, integration clean (all WIRED)

**Known deferred items at close:** 2 (see STATE.md Deferred Items)

---

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
