# Walking Skeleton — StoreWeb

**Phase:** 1
**Generated:** 2026-07-31

## Capability Proven End-to-End

An administrator can run `flask init-db` to create their hashed account in SQLite, then run the Flask dev server and open a Vietnamese page (`lang="vi"`, charset utf-8) that renders the public coming-soon page and the admin login form.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Framework | Flask 3.1.3 application factory (`create_app()` in `app/__init__.py`) | Official Flask pattern; enables `wsgi:app` import for waitress/gunicorn, env-driven config, extension init in one place. Pinned per CLAUDE.md. |
| Data layer | Flask-SQLAlchemy 3.1.1 + SQLite (`data/app.db`), WAL mode + busy_timeout=30000 via SQLAlchemy `Engine` event listener | SQLite is the user-locked default (self-host, low volume). WAL + busy_timeout prevents `database is locked` under WSGI workers (PITFALLS Pitfall 4). |
| Auth | Flask-Login 0.6.3 + Flask-WTF 1.3.0 (CSRFProtect) + Werkzeug scrypt hashing | Minimal session abstraction for a single admin. `login_user(remember=True)`, 30-day permanent session, `login_view='auth.login'`, custom `unauthorized_handler` passing `next=request.path` for safe redirect-back (D-15). |
| Routing | Three blueprints: `public_bp` (`/`), `auth_bp` (`/login`, `/logout`), `admin_bp` (`/admin/`, url_prefix `/admin`) | Isolates public / auth / admin surfaces so `@login_required` can be applied once to the whole admin blueprint via `before_request`. |
| Config | python-dotenv: `.env` loaded in `wsgi.py`; `SECRET_KEY` required (fail-fast `RuntimeError` if missing); `DEBUG` from `FLASK_DEBUG` env, defaults off; `SESSION_COOKIE_HTTPONLY=True`, `SAMEsITE=Lax`, `SECURE` only when `FLASK_ENV=production` | PLAT-02: secrets never in source; debug never on by default. |
| Templates | Jinja2 server-rendered, `app/templates/` with `base.html` (`lang="vi"`, `charset="utf-8"`), subfolders `auth/`, `admin/`, `public/`, `errors/` | PLAT-01; zero JS bundle per CLAUDE.md "What NOT to Use". |
| CSS | Hand-written `app/static/css/style.css` (~5KB), Noto Sans VN + system fallback, Flexbox/Grid, accent `#2563EB` | UI-SPEC design system; no Bootstrap/Tailwind. |
| Deployment (dev) | `flask --app wsgi run`; production entry `wsgi.py` exposing `app = create_app()`; waitress for Windows, gunicorn on Linux (Phase 4) | CLAUDE.md platform note: gunicorn has no `fork` on Windows. |
| Data model | `AdminUser` (UserMixin), `Product`, `ProductImage` (one-to-many) | Product/ProductImage created in Phase 1 so the schema is complete for Phase 2 CRUD + uploads (D-05..D-09). |
| CLI | `flask init-db` registered via `app.cli.add_command`; reads `ADMIN_USERNAME`/`ADMIN_PASSWORD` from env; rejects `change-me` placeholder and <8-char passwords; upserts hash | PLAT-04 + D-01..D-04. |

## Stack Touched in Phase 1

- [x] Project scaffold (`requirements.txt`, `.flaskenv`, `.env.example`, `.gitignore`, `wsgi.py`, `README.md`)
- [x] Routing — 3 blueprints with real routes (`/`, `/login`, `/admin/`)
- [x] Database — real write (`flask init-db` creates AdminUser row) and real read (init-db upsert query; login `AdminUser.query.filter_by`)
- [x] UI — interactive login form wired to POST `/login` with CSRF + session
- [x] Deployment — documented local full-stack run command in `README.md` (`flask --app wsgi init-db` + `flask --app wsgi run`)

## Out of Scope (Deferred to Later Slices)

- Product CRUD, image upload/validation, thumbnails (Phase 2)
- Public catalog listing/detail, search, Messenger contact page (Phase 3)
- Responsive polish, production WSGI deploy, hardening (Phase 4)
- Rate limiting / account lockout (D-12 defers by design; re-evaluate Phase 4)
- Flask-Migrate/Alembic (add when schema gains columns/tables)
- Multi-admin, OAuth, password reset (single admin, out of scope per PROJECT.md)

## Subsequent Slice Plan

Each later phase adds one vertical slice on top of this skeleton without altering its architectural decisions:

- Phase 2: Admin can create/edit/delete products with validated image uploads and stock tracking
- Phase 3: Customers can browse the public catalog, view detail pages, search, and contact via Messenger
- Phase 4: Production deployment (waitress/gunicorn + reverse proxy), responsive mobile polish, hardened config
