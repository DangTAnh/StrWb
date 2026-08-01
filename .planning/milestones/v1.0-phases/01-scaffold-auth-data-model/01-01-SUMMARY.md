---
phase: 01-scaffold-auth-data-model
plan: 01
subsystem: scaffold
tags: [flask, sqlite, wal, factory, blueprint, jinja2]
requires: []
provides:
  - Runnable Flask app factory with SECRET_KEY fail-fast and WAL+busy_timeout SQLite
  - init-db CLI that creates/upserts the admin account (rejects change-me and <8-char passwords)
  - Three blueprints (public /, auth /login, admin /admin/) with Vietnamese Jinja2 templates
affects: [02-auth, 03-ui, Phase 2, Phase 3, Phase 4]
tech-stack:
  added: [Flask 3.1.3, Flask-Login 0.6.3, Flask-SQLAlchemy 3.1.1, Flask-WTF 1.3.0, Pillow 12.3.0, python-dotenv 1.2.2]
  patterns: [application factory, WAL via Engine connect listener, blueprint per surface]
key-files:
  created: [wsgi.py, app/__init__.py, app/db.py, app/models.py, app/public.py, app/auth.py, app/admin.py, app/templates/base.html, app/templates/public/index.html, app/templates/auth/login.html, app/templates/admin/dashboard.html, app/static/css/style.css, requirements.txt, .flaskenv, .env.example, .gitignore, README.md]
  modified: [SKELETON.md pre-existing in phase dir]
key-decisions:
  - "SECRET_KEY missing -> RuntimeError fail-fast at startup (PLAT-02)"
  - "SQLite WAL + busy_timeout=30000 via SQLAlchemy Engine connect event listener (PLAT-03)"
  - "init-db CLI uses Werkzeug scrypt hashing and upserts by username (D-01/D-02)"
  - "Blueprint-per-surface routing so @login_required can gate the whole admin blueprint later"
requirements-completed: [PLAT-01, PLAT-02, PLAT-03, PLAT-04]
duration: 20min
completed: 2026-08-01
---

# Phase 1 Plan 1: Walking Skeleton Summary

Flask app factory boots with env-driven config, SQLite WAL + busy_timeout, `flask init-db` writes a scrypt-hashed AdminUser row, and three blueprints serve the Vietnamese coming-soon page and login form.

## Performance

- **Duration:** 20 min
- **Started:** 2026-08-01T02:55:00Z
- **Completed:** 2026-08-01T03:15:00Z
- **Tasks:** 3 completed
- **Files modified:** 17

## Accomplishments
- App boots via `wsgi:app`; `flask --app wsgi routes` lists public.home (/), auth.login (/login), admin.dashboard (/admin/)
- `flask init-db` creates/upserts admin account, rejecting placeholder and short passwords (verified: INIT_DB_OK, REJECTS_PLACEHOLDER_OK, REJECTS_SHORT_OK)
- All pages render `<html lang="vi">` + `<meta charset="utf-8">` (verified: PAGES_OK)
- Requirements pinned and installed (Flask 3.1.3 resolved cleanly)

## Task Commits

1. **Task 1: Scaffold dependencies and config files** - `fb48f62` (chore)
2. **Task 2: App factory, SQLAlchemy db, AdminUser model, init-db CLI** - `3c97768` (feat)
3. **Task 3: Blueprints, Vietnamese templates, minimal CSS, SKELETON.md** - `3cf9986` (feat)

## Files Created/Modified
- `wsgi.py` - load_dotenv before create_app, exposes `app`
- `app/__init__.py` - create_app, env config, WAL listener, blueprint registration, init-db command
- `app/db.py` - SQLAlchemy instance + init_db_command (scrypt hash, upsert, guards)
- `app/models.py` - AdminUser (UserMixin) model
- `app/public.py`, `app/auth.py`, `app/admin.py` - three blueprints
- `app/templates/base.html` - lang=vi base layout with Noto Sans VN
- `app/templates/public/index.html` - coming-soon page with Messenger link
- `app/templates/auth/login.html` - login form (plain, CSRF in Plan 02)
- `app/templates/admin/dashboard.html` - dashboard stub
- `app/static/css/style.css` - minimal placeholder stylesheet
- `requirements.txt`, `.flaskenv`, `.env.example`, `.gitignore`, `data/.gitkeep`, `README.md` - scaffold

## Deviations from Plan
None - plan executed exactly as written.

## Verification
- `flask --app wsgi routes` succeeds with 3 endpoints
- `pip install -r requirements.txt` exits 0
- Task 2 verify prints INIT_DB_OK, REJECTS_PLACEHOLDER_OK, REJECTS_SHORT_OK
- Task 3 verify prints PAGES_OK

## Self-Check: PASSED
