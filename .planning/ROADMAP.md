# Roadmap: StoreWeb

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-08-01)
- 🚧 **v1.1 Buy System** — Phases 5-9 (in progress)

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

<details open>
<summary>🚧 v1.1 Buy System (Phases 5-9) — PLANNED 2026-08-02</summary>

- [ ] **Phase 5: Data Model + Migration** — Order model (snapshot price/cost/name), `cost_price` column on Product, safe idempotent migration for existing SQLite DBs, cost price field on admin product form (ORD-04, COST-01, COST-02, PLAT-05)
- [ ] **Phase 6: Public Order Form** — Order placement form on product detail (name/phone/address/quantity/note) replacing the "Mua qua Messenger" CTA; validation + CSRF + success feedback (ORD-01, ORD-02, ORD-03, ORD-05)
- [ ] **Phase 7: Admin Order Tracking** — Order list (paginated, status filter) + detail view + status flow Chờ xác nhận → Đã gói → Đã gửi → Đã nhận (+ Đã hủy), forward-only (ORD-06, ORD-07, ORD-08, ORD-09)
- [ ] **Phase 8: Admin Stats** — Stats dashboard: revenue + profit (NULL-safe), orders by status, units sold, inventory counts (STAT-01, STAT-02, STAT-03, STAT-04)
- [ ] **Phase 9: Polish + Deploy** — UI polish, full v1.1 verification harness, no v1.0 regression, deploy docs update (all v1.1 reqs)

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Scaffold + Auth + Data Model | v1.0 | 3/3 | Complete | 2026-07-31 |
| 2. Admin CRUD + Images | v1.0 | 3/3 | Complete | 2026-08-01 |
| 3. Public Catalog + Search + Contact | v1.0 | 3/3 | Complete | 2026-08-01 |
| 4. Polish + Deploy | v1.0 | 3/3 | Complete | 2026-08-01 |
| 5. Data Model + Migration | v1.1 | 0/3 | Planned | — |
| 6. Public Order Form | v1.1 | 0/3 | Planned | — |
| 7. Admin Order Tracking | v1.1 | 0/3 | Planned | — |
| 8. Admin Stats | v1.1 | 0/3 | Planned | — |
| 9. Polish + Deploy | v1.1 | 0/3 | Planned | — |

---

*Full phase details archived in `.planning/milestones/v1.0-ROADMAP.md`*
