# Roadmap: StoreWeb

## Overview

Vietnamese product catalog web (Flask, single admin, SQLite, self-hosted). Customers browse products (image, price, brand, measurements, status) and contact seller via Messenger. Phases deliver end-to-end capability: admin auth, admin product management with images, public catalog with search and contact, and production polish + deployment.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Scaffold + Auth + Data Model** - Foundation: app skeleton, secure config, admin login/logout, Vietnamese interface, SQLite WAL mode, DB init CLI
- [ ] **Phase 2: Admin CRUD + Images** - Admin creates/edits/deletes products with image upload, validation, UUID naming, thumbnails, and stock management
- [ ] **Phase 3: Public Catalog + Search + Contact** - Customers browse product listing and detail pages with gallery, search by name/description, and Messenger contact links
- [ ] **Phase 4: Polish + Deploy** - Responsive mobile layout, out-of-stock de-emphasis, production WSGI deployment with reverse proxy and hardened config

## Phase Details

### Phase 1: Scaffold + Auth + Data Model
**Goal**: Admin can securely access the application and the data model is ready for product management
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, PLAT-01, PLAT-02, PLAT-03, PLAT-04
**Success Criteria** (what must be TRUE):
  1. Admin can log in with username/password and stay logged in across browser sessions
  2. Admin can log out from any admin page
  3. All admin routes redirect to login page when accessed without authentication
  4. Application renders with Vietnamese interface (lang="vi", charset utf-8)
  5. Database initializes via CLI script and creates the first admin account
**Plans**: 3 plans
**UI hint**: yes

Plans:
- [ ] 01-01-PLAN.md — Walking Skeleton: scaffold, config, WAL, init-db, 3 blueprints, Vietnamese base template
- [ ] 01-02-PLAN.md — Data model + admin auth: Product/ProductImage, Flask-Login, login/logout, admin protection
- [ ] 01-03-PLAN.md — Admin UI + Vietnamese polish: dashboard, login, coming-soon, error pages

### Phase 2: Admin CRUD + Images
**Goal**: Admin can fully manage product listings including images, stock, and pricing
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: PROD-01, PROD-02, PROD-03, PROD-04, PROD-05, PROD-06, PROD-07, IMG-01, IMG-02, IMG-03, IMG-04
**Success Criteria** (what must be TRUE):
  1. Admin can create, edit, and delete products with all fields (name, price, brand, measurements, description, stock status, quantity)
  2. Admin can upload multiple images per product with server-side validation (file type via magic bytes, size limit, dimension checks)
  3. Uploaded images are saved with UUID filenames and thumbnails are generated for listing views
  4. Price is stored as integer VND with no precision loss
  5. All admin forms have CSRF protection and validate submitted data
**Plans**: 3 plans
**UI hint**: yes

Plans:
- [ ] 01-01-PLAN.md — Walking Skeleton: scaffold, config, WAL, init-db, 3 blueprints, Vietnamese base template
- [ ] 01-02-PLAN.md — Data model + admin auth: Product/ProductImage, Flask-Login, login/logout, admin protection
- [ ] 01-03-PLAN.md — Admin UI + Vietnamese polish: dashboard, login, coming-soon, error pages

### Phase 3: Public Catalog + Search + Contact
**Goal**: Customers can browse products, search, and contact the seller via Messenger
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: CAT-01, CAT-02, CAT-03, CAT-05, SRCH-01, CONT-01, CONT-02
**Success Criteria** (what must be TRUE):
  1. Customers can view a public product listing grid without logging in
  2. Customers can view product detail pages showing images, price, brand, measurements, description, and stock status
  3. Customers can search products by name or description and see matching results
  4. Customers see a visible Messenger contact link on both the homepage and product detail pages
  5. Product detail page displays an image gallery with all product images
**Plans**: 3 plans
**UI hint**: yes

Plans:
- [ ] 01-01-PLAN.md — Walking Skeleton: scaffold, config, WAL, init-db, 3 blueprints, Vietnamese base template
- [ ] 01-02-PLAN.md — Data model + admin auth: Product/ProductImage, Flask-Login, login/logout, admin protection
- [ ] 01-03-PLAN.md — Admin UI + Vietnamese polish: dashboard, login, coming-soon, error pages

### Phase 4: Polish + Deploy
**Goal**: Application is production-ready with polished UX and secure deployment
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: CAT-04, CAT-06
**Success Criteria** (what must be TRUE):
  1. Out-of-stock and discontinued products are visually de-emphasized in the listing without overwhelming in-stock items
  2. Application layout is fully responsive on mobile devices
  3. Application is deployed with a production WSGI server behind a reverse proxy with HTTPS
  4. SECRET_KEY is loaded from environment variable and debug mode is disabled in production
  5. Error pages display gracefully without exposing stack traces
**Plans**: 3 plans
**UI hint**: yes

Plans:
- [ ] 01-01-PLAN.md — Walking Skeleton: scaffold, config, WAL, init-db, 3 blueprints, Vietnamese base template
- [ ] 01-02-PLAN.md — Data model + admin auth: Product/ProductImage, Flask-Login, login/logout, admin protection
- [ ] 01-03-PLAN.md — Admin UI + Vietnamese polish: dashboard, login, coming-soon, error pages

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Scaffold + Auth + Data Model | 0/3 | Not started | - |
| 2. Admin CRUD + Images | 0/3 | Not started | - |
| 3. Public Catalog + Search + Contact | 0/3 | Not started | - |
| 4. Polish + Deploy | 0/2 | Not started | - |
