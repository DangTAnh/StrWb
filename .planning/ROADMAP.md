# Roadmap: StoreWeb

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-08-01)
- ✅ **v1.1 Buy System** — Phases 5-9 (shipped 2026-08-03)

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

<details>
<summary>✅ v1.0 MVP (Phases 1-4) — SHIPPED 2026-08-01</summary>

- [x] **Phase 1: Scaffold + Auth + Data Model** - Foundation: app skeleton, secure config, admin login/logout, Vietnamese interface, SQLite WAL mode, DB init CLI (completed 2026-07-31)
- [x] **Phase 2: Admin CRUD + Images** - Admin creates/edits/deletes products with image upload, validation, UUID naming, thumbnails, and stock management (completed 2026-08-01)
- [x] **Phase 3: Public Catalog + Search + Contact** - Customers browse product listing and detail pages with gallery, search by name/description, and Messenger contact links (completed 2026-08-01)
- [x] **Phase 4: Polish + Deploy** - Responsive mobile layout, out-of-stock de-emphasis, production WSGI deployment with reverse proxy and hardened config (completed 2026-08-01)

</details>

<details>
<summary>✅ v1.1 Buy System (Phases 5-9) — SHIPPED 2026-08-03</summary>

- [x] **Phase 5: Data Model + Migration** — Order model (snapshot price/cost/name), `cost_price` column on Product, safe idempotent migration for existing SQLite DBs, cost price field on admin product form (ORD-04, COST-01, COST-02, PLAT-05) (completed 2026-08-02)
- [x] **Phase 6: Cart + Checkout (Public Order Form)** — Session cart + single-page cart+checkout; Order → Order + OrderItem refactor; add-to-cart replaces "Mua qua Messenger" CTA on detail; CSRF + honeypot (ORD-01, ORD-02, ORD-03, ORD-05, ORD-10, ORD-10a, ORD-10b) (completed 2026-08-02)
- [x] **Phase 7: Admin Order Tracking** — Order list (paginated, status filter) + detail view + status flow Chờ xác nhận → Đã gói → Đã gửi → Đã nhận (+ Đã hủy), forward-only (ORD-06, ORD-07, ORD-08, ORD-09) (completed 2026-08-02)
- [x] **Phase 8: Admin Stats** — Stats dashboard: revenue + profit (NULL-safe), orders by status, units sold, inventory counts (STAT-01, STAT-02, STAT-03, STAT-04) (completed 2026-08-02)
- [x] **Phase 9: Polish + Deploy** — UI polish, full v1.1 verification harness, no v1.0 regression, deploy docs update (all v1.1 reqs) (completed 2026-08-03)

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Scaffold + Auth + Data Model | v1.0 | 3/3 | Complete | 2026-07-31 |
| 2. Admin CRUD + Images | v1.0 | 3/3 | Complete | 2026-08-01 |
| 3. Public Catalog + Search + Contact | v1.0 | 3/3 | Complete | 2026-08-01 |
| 4. Polish + Deploy | v1.0 | 3/3 | Complete | 2026-08-01 |
| 5. Data Model + Migration | v1.1 | 3/3 | Complete    | 2026-08-02 |
| 6. Cart + Checkout (Public Order Form) | v1.1 | 3/3 | Complete | 2026-08-02 |
| 7. Admin Order Tracking | v1.1 | 3/3 | Complete    | 2026-08-02 |
| 8. Admin Stats | v1.1 | 3/3 | Complete    | 2026-08-02 |
| 9. Polish + Deploy | v1.1 | 3/3 | Complete    | 2026-08-03 |

---

*Full phase details archived in `.planning/milestones/v1.1-ROADMAP.md`*
