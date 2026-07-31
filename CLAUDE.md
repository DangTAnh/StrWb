<!-- GSD:project-start source:PROJECT.md -->
## Project

**StoreWeb**

Web bán hàng tiếng Việt để trưng bày và quản lý sản phẩm. Khách vào web xem danh sách hàng với chi tiết đầy đủ (ảnh, giá, thương hiệu, số đo, mô tả, trạng thái còn/hết hàng) rồi liên hệ mua qua Messenger. Chủ web đăng nhập một tài khoản admin để thêm/sửa/xóa sản phẩm, quản lý danh mục trạng thái và tồn kho. Backend Python Flask, tự host.

**Core Value:** Khách xem được list hàng rõ ràng (ảnh + giá + trạng thái) và admin dễ dàng quản lý sản phẩm.

### Constraints

- **Tech stack**: Python Flask — đã chốt bởi người dùng
- **Ngôn ngữ**: Tiếng Việt — giao diện duy nhất tiếng Việt
- **Deploy**: Tự host — cần cấu hình chạy trên máy riêng (ví dụ gunicorn + nginx hoặc tương đương)
- **Dữ liệu**: Cần lưu trữ sản phẩm + ảnh — SQLite là lựa chọn mặc định (nhẹ, tự host dễ)
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Technologies
| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Flask | 3.1.3 | Micro web framework (WSGI app) | Current latest; depends on Werkzeug 3.1.x, Jinja2 3.1.x, Click 8.x. Mature, minimal core. The standard entry point for any "Flask web" project. No heavier alternative is justified for a flat product catalog. |
| Flask-SQLAlchemy | 3.1.1 | SQLAlchemy ORM integration | Current latest; requires SQLAlchemy >= 2.0.16 / Flask >= 2.2.5. The de-facto Flask ORM adapter; integrates cleanly with Flask app/config context. Avoids raw SQLAlchemy boilerplate. |
| Flask-Login | 0.6.3 | Session-based admin auth (single user) | Current latest (maintenance mode since 2023-10, no actively maintained alternative that pairs with Flask's native session model). For a single admin account it is the correct, minimal abstraction over `session` — a custom cookie/session scheme would be reinventing exactly this. |
| Flask-WTF | 1.3.0 | Form rendering + CSRF + validation | Current latest; depends on WTForms. Gives server-side validation, CSRF protection, and Jinja macros (via `wtf`) out of the box. For product CRUD + admin login forms, hand-writing CSRF tokens and validators is unnecessary boilerplate. |
### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pillow | 12.3.0 | Image resize/validation for product uploads | Always here — product CRUD requires image upload. Resize on save to thumbnails. This is the standard Flask image-handling path (see "What NOT to use"). |
| Werkzeug | 3.1.8 | `generate_password_hash` / `check_password_hash` | Bundled with Flask 3.1; use `werkzeug.security` for admin password hashing (scrypt/pbkdf2). Do NOT reach for passlib unless you need exotic schemes. |
| python-dotenv | 1.2.2 | Load `.env` into Flask config | Always — keeps DB path, secret key, upload dir out of source. Reads `FLASK_APP`/`SECRET_KEY` style vars. |
| flask-migrate | 4.1.0 | Alembic migrations for SQLite schema changes | Use once the product model is in active flux (Phase 2). For Phase 1 (single `products` table, greenfield) `db.create_all()` is fine; add migrations when schema evolves. |
### Development Tools
| Tool | Purpose | Notes |
|------|---------|-------|
| Flask CLI (`flask run`) | Dev server with auto-reload | Use during development. Configure `flask --app app run --debug`. NOT for production. |
| venv / pip | Dependency isolation | Pin versions in `requirements.txt`. No Poetry needed at this size — adds ceremony, not value. |
## Installation
# Core
# Supporting
# Dev only (add once schema is non-trivial)
## Alternatives Considered
| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| gunicorn (Unix) | waitress | Use waitress on Windows hosts directly. gunicorn does not run natively on Windows (no `fork`); on Windows either use waitress as the WSGI server, or run gunicorn inside WSL. |
| plain CSS / minimal framework | Bootstrap 5 | Use Bootstrap only if you need a pre-built admin dashboard feel quickly. For a simple catalog, hand-written CSS (~200 LOC) is lighter and avoids Bootstrap's JS bundle entirely. |
| Pillow (manual resize) | Flask-Images | Flask-Images (3.0.2, 2019) is abandoned — no declared deps, no Python 3.10+ compatibility claims. Pillow's `Image.thumbnail()` is a 3-line replacement. |
| Flask-WTF | hand-rolled forms | If you need zero CSRF and zero validation, skip it. But CSRF on the admin forms is worth the one dependency. |
| Flask-Login | custom session code | Only if you want a stateless-token scheme. For a single shared admin over Flask sessions, Flask-Login is the minimal abstraction. |
## What NOT to Use
| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Flask-Images (3.0.2) | Abandoned since 2019; no deps declared; stale. | Pillow `Image.thumbnail()` inline — 3 lines, no dep risk. |
| gunicorn on Windows (natively) | gunicorn uses `os.fork`, unavailable on Windows. | waitress on Windows, or gunicorn inside WSL. |
| Redis / Celery | Single admin, SQLite, low volume — no background queue needed. | N/A — defer until async email/resize load appears. |
| Flask-Limiter / rate limiting | One admin IP logging in once per session; brute-force risk is low. | Add only if admin is ever internet-exposed without nginx allowlisting. |
| Flask-Admin | Overkill: full auto-generated admin UI for a flat product list. | Hand-rolled product routes with Flask-WTF — less surface, full control over VN labels. |
| passlib | Werkzeug's `generate_password_hash` covers scrypt/pbkdf2 out of the box. | `werkzeug.security` — one fewer dependency. |
| React / Vue / Svelte | Catalog is server-rendered HTML; no client interactivity beyond link nav. | Jinja2 templates only — zero JS bundle. |
| Tailwind / Bootstrap Vue / heavy CSS | Adds build step + bundle for utility classes a 200-line custom CSS file covers. | Plain responsive CSS (Flexbox/Grid), optional 5KB of custom CSS. |
## Stack Patterns by Variant
- Use `gunicorn` as the WSGI server (4-6 workers) behind `nginx` (static + reverse proxy).
- Use `waitress-serve --listen=127.0.0.1:8000 app:app` as the WSGI server (no `fork` needed). Optionally front with nginx on Windows for static files + TLS, or bind waitress directly.
- Skip `flask-migrate`; use `db.create_all()` in `app.cli` command. Add migrations only when the model gains columns/tables.
- Introduce `flask-migrate` + Alembic at that point (schema changes are a migration trigger, not a project-start ceremony).
## Version Compatibility
| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Flask 3.1.3 | Werkzeug >=3.1.0, Jinja2 >=3.1.2, Click >=8.1.3, itsdangerous >=2.2.0, blinker >=1.9.0, Python 3.10+ | Python 3.8 supported via `importlib-metadata` extra; project targets 3.10+. Verified: `pip install --dry-run` resolves Flask 3.1.3 with Werkzeug 3.1.8, blinker 1.9.0, itsdangerous 2.2.0 cleanly. |
| Flask-SQLAlchemy 3.1.1 | Flask >=2.2.5, SQLAlchemy >=2.0.16 | SQLAlchemy 2.0 line; tested with SQLAlchemy 2.0.51 (already installed, resolves fine). |
| Flask-WTF 1.3.0 | Flask >=2.0, WTForms >=3.1.1 | Uses WTForms 3.2.2 (already installed, compatible). |
| Flask-Login 0.6.3 | Flask >=2.0 (runtime: Flask >=1.0.2) | Compatible with Flask 3.x session API — no changes needed. |
| Pillow 12.3.0 | Python 3.10-3.14 | Standalone; no Flask coupling. |
## Sources
- PyPI `flask` metadata — verified Flask 3.1.3 latest, deps `werkzeug>=3.1.0`, `jinja2>=3.1.2`, `click>=8.1.3`, `itsdangerous>=2.2.0`, `blinker>=1.9.0` (HIGH confidence, current).
- PyPI `flask-sqlalchemy` metadata — verified Flask-SQLAlchemy 3.1.1 requires `sqlalchemy>=2.0.16` and `flask>=2.2.5` (HIGH).
- PyPI `flask-wtf` / `wtforms` metadata — verified Flask-WTF 1.3.0 / WTForms 3.2.2 (HIGH).
- PyPI `pillow`, `python-dotenv`, `flask-migrate`, `werkzeug`, `blinker` version history — verified via `pip index versions` (HIGH).
- PyPI `flask-images` (3.0.2, 2019-08) — last release 2019, no declared dependencies, no Python 3.10+ classifier — marked abandoned (MEDIUM).
- PyPI `gunicorn` + gunicorn official docs — gunicorn uses `os.fork`, unsupported on native Windows; `waitress` is the documented Windows alternative (HIGH).
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
