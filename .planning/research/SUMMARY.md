# Project Research Summary

**Project:** StoreWeb — Vietnamese product catalog web
**Domain:** Self-hosted Flask product catalog (single admin, SQLite, Vietnamese UI, Messenger contact, no cart/payments)
**Researched:** 2026-07-31
**Confidence:** HIGH

## Executive Summary

StoreWeb is a Vietnamese-language product catalog built on Python Flask with a single admin account, SQLite database, and filesystem image storage. The product serves as a self-hosted alternative to complex e-commerce platforms that browse products and contact the seller via Messenger to negotiate and complete transactions manually. The recommended approach uses the Flask application factory pattern with three isolated blueprints (public, admin, auth), SQLAlchemy ORM over SQLite, Flask-Login for session management, and Flask-WTF for CSRF-protected forms. Image uploads are validated server-side via Pillow (magic bytes + dimension checks) and stored with UUID filenames outside any executable web path.

The architecture is deliberately minimal: no shopping cart, no payments, no customer accounts, no product categories. These are not missing features but explicitly scoped out as anti-features that would add complexity (PCI scope, order management, fraud risk, permission models) without value for a single-admin, Messenger-negotiated sales model. The product differentiation comes from execution quality (Vietnamese-specific UX, mobile-first CSS, Messenger-native contact flow) rather than feature breadth.

The highest risks are operational rather than architectural: (1) debug mode left on in production exposes the Werkzeug debugger enabling remote code execution, (2) SQLite database is locked errors under multi-worker gunicorn deployments, (3) image upload vulnerabilities (decompression bombs, path traversal, non-image files served as executable), (4) SECRET_KEY not set causing silent session failure, and (5) VND prices stored as Float causing precision errors. All five are well-documented in PITFALLS.md with concrete prevention strategies that should be implemented at the scaffold phase, not as afterthoughts.

## Key Findings

### Recommended Stack

Flask 3.1.3 is the core web framework, paired with Flask-SQLAlchemy 3.1.1 (SQLAlchemy 2.0 ORM), Flask-Login 0.6.3 (session-based auth), Flask-WTF 1.3.0 (form validation + CSRF), Pillow 12.3.0 (image validation), and python-dotenv 1.2.2 (config from environment). Werkzeug 3.1.8 provides generate_password_hash/check_password_hash (scrypt). For production, use waitress on Windows hosts or gunicorn+nginx on Linux. Flask-Migrate is deferred to when the schema grows beyond a single flat products table.

**Core technologies:**
- Flask 3.1.3: micro web framework, WSGI-compatible, current latest
- Flask-SQLAlchemy 3.1.1: SQLAlchemy 2.0 ORM integration
- Flask-Login 0.6.3: minimal session-based auth for single admin
- Flask-WTF 1.3.0: server-side form validation, CSRF protection
- Pillow 12.3.0: image resize/validation on upload, decompression bomb protection
- python-dotenv 1.2.2: load SECRET_KEY, DB path, upload dir from environment
- gunicorn (Linux) / waitress (Windows): production WSGI servers
- nginx: reverse proxy, static + upload file serving

**Explicitly avoided:** Flask-Admin (overkill), Flask-Images (abandoned), passlib (Werkzeug covers), Redis/Celery (not needed), React/Vue (server-rendered only).

### Expected Features

**Must have (table stakes) — 9 core features for v1:**
- Public product listing page (flat grid, server-rendered, no auth wall)
- Product detail page (image, price, brand, measurements, description, stock status)
- Product images with thumbnail resize (Vietnamese shoppers are image-heavy)
- Price + stock status prominently displayed
- Contact link/button to Messenger (de-facto sales channel in Vietnam)
- Admin login (single shared account with password hash)
- Admin product CRUD (create/edit/delete with image upload)
- Stock/status tracking (in stock, out of stock, discontinued)
- Responsive mobile layout (CSS Flexbox/Grid only)

**Should have (competitive differentiators) — defer to v1.x:**
- Image gallery per product (multiple images, thumbnail strip)
- Search by name/description (essential past 30 products)
- Filter/sort by price, brand, stock status
- Admin inline stock toggle (bulk edit for speed)
- Quick contact WhatsApp link alongside Messenger
- Product view/sold count (low-key social proof)

**Defer (v2+):** Product categories, reviews/ratings, sitemap.xml, dark mode.

**Anti-features (explicitly excluded):** Shopping cart, payments, customer accounts, multi-vendor, UGC, wishlist, inventory auto-reduce, real-time notifications, multi-language SEO.

### Architecture Approach

Flask application factory pattern with three blueprints: public_bp (catalog, detail, contact), admin_bp (CRUD behind @login_required), auth_bp (login/logout). Single base.html with Vietnamese labels. Filesystem image storage with UUID filenames served by nginx. SQLite database, no background queues. Hand-rolled admin CRUD with Flask-WTF forms — no Flask-Admin.

**Major components:**
1. app/__init__.py — Application factory
2. app/models.py — Product (Integer price) and AdminUser (UserMixin)
3. app/db.py — SQLAlchemy db object + init-db CLI
4. app/auth.py — Login/logout routes + Flask-Login
5. app/admin.py — CRUD routes behind @login_required
6. app/public.py — Public routes: listing, detail, contact
7. app/templates/ — base.html + public/ and admin/ subfolders
8. app/static/uploads/ — Product images (gitignored)

### Critical Pitfalls

1. Debug mode + Werkzeug debugger in production (RCE) — never commit DEBUG=True. Phase: Scaffold.
2. SECRET_KEY not set (session forgery) — generate 32-byte key, load from env. Phase: Scaffold.
3. Image upload path traversal (RCE) — validate magic bytes, Pillow verify(), dimension check, 16MB limit, UUID filenames. Phase: Admin + Image Upload.
4. SQLite database is locked (multi-worker gunicorn) — WAL mode, busy_timeout=30s, no --preload, retry logic. Phase: Admin or Deployment.
5. VND prices as Float (precision loss) — store as Integer, no decimals. Phase: Data Model.

## Implications for Roadmap

Based on research, suggested 5-phase structure:

### Phase 1: Scaffold + Data Model + Auth
**Rationale:** Foundation must exist before any CRUD. Config, SECRET_KEY, Vietnamese charset must be baked in from the start.
**Delivers:** create_app() factory, SQLite DB, admin login works, base template with lang=vi + charset=utf-8, Integer price column.
**Addresses:** Admin login, stock/status tracking (model), responsive base layout.
**Avoids:** SECRET_KEY missing, debug=True, VND as Float, missing lang/charset.
**Research flag:** NONE — Flask factory pattern is official documentation.

### Phase 2: Admin CRUD + Image Upload
**Rationale:** Data entry is the critical path; image validation must be baked in before any file touches the filesystem.
**Delivers:** Admin creates/edits/deletes products with validated image upload.
**Addresses:** Admin product CRUD, product images, stock/status admin interface.
**Avoids:** Path traversal, decompression bomb, SQLite locked (WAL mode).
**Research flag:** NONE — standard Flask file upload patterns.

### Phase 3: Public Catalog
**Rationale:** Public catalog depends on models (Phase 1) and seeded data (Phase 2).
**Delivers:** Public listing (flat grid), detail page, /contact with Messenger link.
**Addresses:** Public listing, detail page, price+status display, Messenger contact.
**Avoids:** Blank empty page, price decimals, no back link.
**Research flag:** NONE — standard server-rendered catalog patterns.

### Phase 4: Polish + Validation
**Rationale:** UX refinements depend on stable CRUD flow. Vietnamese market requires careful formatting.
**Delivers:** Out-of-stock de-emphasis, flash messages, POST delete with CSRF, image preview, responsive forms.
**Avoids:** Price with .00 VND, GET delete link, no submit feedback.
**Research flag:** NONE — standard Flask-WTF + CSS patterns.

### Phase 5: Production Deployment
**Rationale:** Deployment is configuration, not code — all app functionality must be complete.
**Delivers:** gunicorn/waitress WSGI server, nginx reverse proxy, HTTPS, ProxyFix, custom error pages.
**Avoids:** debug=True, gunicorn --preload with SQLite, nginx executing uploads.
**Research flag:** Platform-specific if using Hetzner/DigitalOcean.

### Phase Ordering Rationale
- DB + models first: all subsequent phases depend on Product and AdminUser models.
- Auth second: admin routes must be protected before CRUD endpoints.
- Admin CRUD third: data entry path; public catalog is useless without products.
- Public catalog fourth: depends on models and seeded data.
- Polish fifth: refinements depend on stable CRUD.
- Deployment sixth: configuration, not code.

### Research Flags

Phases likely needing deeper research during planning:
- Phase 5 (Deployment): Platform-specific if using Hetzner/DigitalOcean.

Phases with standard patterns (skip research):
- Phase 1 (Scaffold): Flask factory is official docs.
- Phase 2 (CRUD): Flask-WTF + SQLAlchemy CRUD is textbook.
- Phase 3 (Public catalog): Server-rendered templates.
- Phase 4 (Polish): Flash messages + CSS.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versions verified via PyPI metadata and pip resolution. |
| Features | HIGH | Table stakes verified against Vietnamese mobile behavior + PROJECT.md. |
| Architecture | HIGH | App factory + blueprints is official Flask pattern. |
| Pitfalls | HIGH | Verified against installed Flask 3.0.0/Werkzeug 3.0.0. |

**Overall confidence:** HIGH

### Gaps to Address
- Vietnamese font rendering (Roboto, Noto Sans VN) — test on Android Chrome during Phase 4.
- Messenger link URL format depends on admin Facebook Page config — verify in Phase 3.
- nginx upload filesystem permissions — audit in Phase 5.
- SQLite backup strategy (concurrent writes) — use sqlite3 .backup in Phase 5.

## Sources

### Primary (HIGH confidence)
- PyPI flask 3.1.3, flask-sqlalchemy 3.1.1, flask-wtf 1.3.0, flask-login 0.6.3, pillow 12.3.0, werkzeug 3.1.8, python-dotenv 1.2.2
- Flask 3.0.0 installed locally — config defaults verified
- Werkzeug 3.0.0 installed locally — password hashing + secure_filename verified
- SQLite 3.43.1 — WAL mode, busy_timeout verified
- Flask official docs (app factory, blueprints, file uploads, deployment)
- Flask-Login official docs
- PROJECT.md — project source of truth

### Secondary (MEDIUM confidence)
- PyPI flask-images 3.0.2 — abandoned since 2019
- GitHub: Vietnamese web ban hang Flask projects — confirming PROJECT.md scope as deliberate

### Tertiary (LOW confidence)
- WebFetch to Flask docs returned HTTP 429 — verified locally instead

---
*Research completed: 2026-07-31*
*Ready for roadmap: yes*