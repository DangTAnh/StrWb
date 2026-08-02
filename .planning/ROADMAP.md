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

## Phase Details

### Phase 5: Data Model + Migration

**Goal**: Order model with snapshot pricing and Product cost_price column, safe idempotent migration for existing SQLite DBs, cost price field on admin product form
**Depends on**: Phase 4
**Requirements**: ORD-04, COST-01, COST-02, PLAT-05
**Success Criteria** (what must be TRUE):

  1. Order model exists storing customer info (name, phone, address, quantity, note) plus snapshot of product name, sale price, and cost price at order time
  2. Product model has a nullable `cost_price` column
  3. Migration is idempotent — adding the `cost_price` column and `orders` table runs safely on existing v1.0 SQLite DBs without data loss
  4. Admin product create/edit form includes an optional cost price field
  5. Cost price never appears on any public-facing page

**Plans**: 3 plans
**UI hint**: yes

Plans:

**Wave 1**

- [x] 05-01-PLAN.md — Order + Product cost data model

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 05-02-PLAN.md — Idempotent SQLite migration
- [x] 05-03-PLAN.md — Cost price on admin product form

### Phase 6: Cart + Checkout (Public Order Form)

**Goal**: Giỏ hàng nhiều sản phẩm (lưu session) + checkout tạo đơn nhiều sản phẩm (Order + OrderItem) thay form đặt hàng 1 sản phẩm; bỏ nút "Mua qua Messenger" trên trang chi tiết, giữ dải liên hệ Messenger
**Depends on**: Phase 5 (Order model refactor → Order + OrderItem)
**Requirements**: ORD-01, ORD-02, ORD-03, ORD-05, ORD-10, ORD-10a, ORD-10b
**Success Criteria** (what must be TRUE):

  1. Order model refactored: `orders` giữ thông tin khách + status; `order_items` lưu snapshot từng sản phẩm (name/price/cost_price/quantity) + FK `order_id`; migration idempotent không mất dữ liệu
  2. Trang chi tiết có "Thêm vào giỏ hàng" (chọn số lượng, 1 ≤ qty ≤ tồn kho); không còn nút "Mua qua Messenger" trên trang chi tiết; dải Messenger ở nơi khác giữ nguyên
  3. Trang giỏ hàng liệt kê sản phẩm, cho sửa số lượng/xóa, hiện tổng tiền; hidden khi hết hàng/ngừng bán
  4. Checkout bắt buộc tên/SĐT/địa chỉ; tạo 1 Order + nhiều OrderItem snapshot; CSRF + honeypot chống spam
  5. Khách thấy thông báo thành công sau khi đặt hàng; tồn kho không giảm (ORD-12 deferred v2)

**Plans**: 3 plans
**UI hint**: yes

Plans:

- [x] 06-01-PLAN.md — Order → Order + OrderItem refactor + migration
- [ ] 06-02-PLAN.md — Cart (session) + add/update/remove + total
- [ ] 06-03-PLAN.md — Checkout form + submit route + CSRF/honeypot + success

### Phase 7: Admin Order Tracking

**Goal**: Order list (paginated, status filter) + detail view + forward-only status flow Chờ xác nhận → Đã gói → Đã gửi → Đã nhận (+ Đã hủy)
**Depends on**: Phase 6
**Requirements**: ORD-06, ORD-07, ORD-08, ORD-09
**Success Criteria** (what must be TRUE):

  1. Admin sees a paginated order list filterable by status
  2. Admin sees an order detail view with customer info, product snapshot, quantity, price, note, and timestamps
  3. Admin can advance order status Chờ xác nhận → Đã gói → Đã gửi → Đã nhận
  4. Admin can cancel an order (Đã hủy) — admin only
  5. Status only moves forward — cannot revert

**Plans**: 3 plans
**UI hint**: yes

Plans:

- [ ] 07-01-PLAN.md — Order list + status filter
- [ ] 07-02-PLAN.md — Order detail view
- [ ] 07-03-PLAN.md — Forward-only status transitions

### Phase 8: Admin Stats

**Goal**: Stats dashboard — revenue + profit (NULL-safe), orders by status, units sold, inventory counts
**Depends on**: Phase 7
**Requirements**: STAT-01, STAT-02, STAT-03, STAT-04
**Success Criteria** (what must be TRUE):

  1. Admin sees total revenue (only orders with status Đã gửi + Đã nhận)
  2. Admin sees profit = revenue − cost price (NULL-safe)
  3. Admin sees order counts by status and total units sold
  4. Admin sees inventory counts (total, out of stock, discontinued)

**Plans**: 3 plans
**UI hint**: yes

Plans:

- [ ] 08-01-PLAN.md — Revenue + profit stats
- [ ] 08-02-PLAN.md — Orders-by-status + units sold
- [ ] 08-03-PLAN.md — Inventory counts dashboard

### Phase 9: Polish + Deploy

**Goal**: UI polish, full v1.1 verification harness, no v1.0 regression, deploy docs update
**Depends on**: Phase 8
**Requirements**: ORD-01, ORD-02, ORD-03, ORD-04, ORD-05, ORD-06, ORD-07, ORD-08, ORD-09, COST-01, COST-02, STAT-01, STAT-02, STAT-03, STAT-04, PLAT-05
**Success Criteria** (what must be TRUE):

  1. All 16 v1.1 requirements verified
  2. No v1.0 regression (catalog, search, contact, admin CRUD all working)
  3. Deploy docs updated with v1.1 migration/backup instructions
  4. New order form + admin order views polished and responsive

**Plans**: 3 plans
**UI hint**: yes

Plans:

- [ ] 09-01-PLAN.md — UI polish pass
- [ ] 09-02-PLAN.md — v1.1 verification harness
- [ ] 09-03-PLAN.md — Deploy docs update

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Scaffold + Auth + Data Model | v1.0 | 3/3 | Complete | 2026-07-31 |
| 2. Admin CRUD + Images | v1.0 | 3/3 | Complete | 2026-08-01 |
| 3. Public Catalog + Search + Contact | v1.0 | 3/3 | Complete | 2026-08-01 |
| 4. Polish + Deploy | v1.0 | 3/3 | Complete | 2026-08-01 |
| 5. Data Model + Migration | v1.1 | 3/3 | Complete    | 2026-08-02 |
| 6. Public Order Form | v1.1 | 1/3 | In Progress | — |
| 7. Admin Order Tracking | v1.1 | 0/3 | Planned | — |
| 8. Admin Stats | v1.1 | 0/3 | Planned | — |
| 9. Polish + Deploy | v1.1 | 0/3 | Planned | — |

---

*Full phase details archived in `.planning/milestones/v1.0-ROADMAP.md`*
