# Roadmap: StoreWeb

## Milestones

- [x] **v1.0 MVP** — Phases 1-4 (shipped 2026-08-01)
- [x] **v1.1 Buy System** — Phases 5-9 (shipped 2026-08-03)
- [ ] **v1.2 Đợt bán (Sale Batches)** — Phases 10-12 (in progress)

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

<details>
<summary>v1.0 MVP (Phases 1-4) — SHIPPED 2026-08-01</summary>

- [x] **Phase 1: Scaffold + Auth + Data Model** - Foundation: app skeleton, secure config, admin login/logout, Vietnamese interface, SQLite WAL, DB init CLI (completed 2026-07-31)
- [x] **Phase 2: Admin CRUD + Images** - Admin creates/edits/deletes products with image upload, validation, UUID naming, thumbnails, and stock management (completed 2026-08-01)
- [x] **Phase 3: Public Catalog + Search + Contact** - Customers browse product listing and detail pages with gallery, search by name/description, and Messenger contact links (completed 2026-08-01)
- [x] **Phase 4: Polish + Deploy** - Responsive mobile layout, out-of-stock de-emphasis, production WSGI deployment with reverse proxy and hardened config (completed 2026-08-01)

</details>

<details>
<summary>v1.1 Buy System (Phases 5-9) — SHIPPED 2026-08-03</summary>

- [x] **Phase 5: Data Model + Migration** — Order model (snapshot price/cost/name), `cost_price` column on Product, safe idempotent migration for existing SQLite DBs, cost price field on admin product form (ORD-04, COST-01, COST-02, PLAT-05) (completed 2026-08-02)
- [x] **Phase 6: Cart + Checkout (Public Order Form)** — Session cart + single-page cart+checkout; Order → Order + OrderItem refactor; add-to-cart replaces "Mua qua Messenger" CTA on detail; CSRF + honeypot (ORD-01, ORD-02, ORD-03, ORD-05, ORD-10, ORD-10a, ORD-10b) (completed 2026-08-02)
- [x] **Phase 7: Admin Order Tracking** — Order list (paginated, status filter) + detail view + status flow Chờ xác nhận → Đã gói → Đã gửi → Đã nhận (+ Đã hủy), forward-only (ORD-06, ORD-07, ORD-08, ORD-09) (completed 2026-08-02)
- [x] **Phase 8: Admin Stats** — Stats dashboard: revenue + profit (NULL-safe), orders by status, units sold, inventory counts (STAT-01, STAT-02, STAT-03, STAT-04) (completed 2026-08-02)
- [x] **Phase 9: Polish + Deploy** — UI polish, full v1.1 verification harness, no v1.0 regression, deploy docs update (all v1.1 reqs) (completed 2026-08-03)

</details>

<details>
<summary>v1.2 Đợt bán (Sale Batches) (Phases 10-12) — IN PROGRESS</summary>

- [ ] **Phase 10: Data Model + Migration + Admin Batch CRUD + Toggle** - Batch model (name, sort_order, visible), product_batches junction table, idempotent migration via init-db, admin create/edit/delete batch + visibility toggle (BATCH-01, BATCH-02, BATCH-03, BATCH-05, BATCH-08)
- [ ] **Phase 11: Product-Batch Assignment** - Admin assigns products to one or more batches via many-to-many UI on product edit page (BATCH-04)
- [ ] **Phase 12: Public Rendering + Visibility Gating** - Homepage renders a section per visible batch in sort order; products not in any visible batch hidden from public everywhere (home, search, detail, cart) (BATCH-06, BATCH-07)

</details>

## Phase Details

### Phase 10: Data Model + Migration + Admin Batch CRUD + Toggle
**Goal**: Admin can fully manage sale batches (create/edit/delete/toggle visibility) and the database schema supports many-to-many product-batch relationships without touching the products table.
**Depends on**: Phase 9
**Requirements**: BATCH-01, BATCH-02, BATCH-03, BATCH-05, BATCH-08
**Success Criteria** (what must be TRUE):
  1. Admin can create a new batch with a name and sort order, saved to the database
  2. Admin can edit an existing batch's name and sort order and see the updated values persist
  3. Admin can delete a batch without losing any products (the product-batch relationships are removed, products remain)
  4. Admin can toggle a batch's visibility with a single action and the visible flag updates immediately
  5. Running the init-db CLI on an existing database adds the batches and product_batches tables without modifying the products table or losing any existing data
**Plans**: TBD
**UI hint**: yes

### Phase 11: Product-Batch Assignment
**Goal**: Admin can assign any product to one or more sale batches through the product edit interface.
**Depends on**: Phase 10
**Requirements**: BATCH-04
**Success Criteria** (what must be TRUE):
  1. Admin can assign a product to one or more batches from the product edit form
  2. Admin can remove a product from a batch; the association is removed while the product and batch both persist
  3. Admin can save a product with multiple batches selected and the assignments are persisted correctly
**Plans**: TBD
**UI hint**: yes

### Phase 12: Public Rendering + Visibility Gating
**Goal**: The public catalog only shows products belonging to visible batches, organized into sections on the homepage in sort order; products in no visible batch are invisible everywhere public.
**Depends on**: Phase 11
**Requirements**: BATCH-06, BATCH-07
**Success Criteria** (what must be TRUE):
  1. Homepage renders one section per visible batch, each section listing its products, in sort_order sequence
  2. A product not assigned to any visible batch does not appear in the homepage listing
  3. A product not assigned to any visible batch is excluded from search results
  4. Navigating directly to a product detail URL for a product not in any visible batch shows a 404 (or otherwise does not reveal the product)
  5. A product not assigned to any visible batch does not appear in the cart add flow or cart contents
**Plans**: TBD
**UI hint**: yes

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 10. Data Model + Migration + Admin Batch CRUD + Toggle | v1.2 | 0/4 | Not started | - |
| 11. Product-Batch Assignment | v1.2 | 0/1 | Not started | - |
| 12. Public Rendering + Visibility Gating | v1.2 | 0/2 | Not started | - |

---

*Full phase details archived in `.planning/milestones/v1.1-ROADMAP.md`*
