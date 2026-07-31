---
phase: 01-scaffold-auth-data-model
plan: 02
subsystem: auth
tags: [flask-login, csrf, wtforms, scrypt, sqlalchemy]
requires:
  - phase: 01
    provides: app factory, db, AdminUser, init-db, blueprints
provides:
  - Full data model (AdminUser, Product, ProductImage) with status property
  - Working admin login/logout with 30-day session, CSRF, safe next redirect
  - @login_required gate on every admin route
affects: [03-ui, Phase 2 CRUD]
tech-stack:
  added: [Flask-WTF 1.3.0 CSRFProtect, Flask-Login 0.6.3 LoginManager, WTForms]
  patterns: [login_manager.user_loader, unauthorized_handler, before_request guard]
key-files:
  created: [app/forms.py]
  modified: [app/models.py, app/auth.py, app/__init__.py, app/admin.py, app/templates/auth/login.html, app/templates/base.html]
key-decisions:
  - "login_user(remember=True) + PERMANENT_SESSION_LIFETIME 30d (D-10/D-11)"
  - "Safe next redirect: path-only, reject // (D-15)"
  - "Generic login error, no lockout (D-12)"
  - "before_request @login_required guards all admin routes (AUTH-04)"
requirements-completed: [AUTH-01, AUTH-02, AUTH-03, AUTH-04]
duration: 15min
completed: 2026-08-01
---

# Phase 1 Plan 2: Data Model + Admin Auth Summary

Product/ProductImage models added and admin authentication is fully wired: scrypt-verified login, 30-day session, CSRF-protected login/logout, safe redirect-back, and every admin route gated by @login_required.

## Performance

- **Duration:** 15 min
- **Started:** 2026-08-01T03:15:00Z
- **Completed:** 2026-08-01T03:30:00Z
- **Tasks:** 3 completed
- **Files modified:** 6

## Accomplishments
- Product (Integer price, status property, images rel) + ProductImage models; init-db creates all 3 tables (verified MODELS_OK)
- Login POST validates scrypt hash, wrong password shows generic VN error, valid login 302 -> /admin/ (verified AUTH_OK)
- Logout POST clears session with success flash; admin blueprint protected via before_request (verified PROTECT_OK / REDIRECT_BACK_OK)

## Task Commits

1. **Task 1: Add Product and ProductImage models** - `b31d26b` (feat)
2. **Task 2: Flask-Login + CSRFProtect + LoginForm + login/logout** - `c34c939` (feat)
3. **Task 3: Protect every admin route with @login_required** - `ca8125a` (feat)

## Files Created/Modified
- `app/forms.py` - LoginForm (username/password/submit, VN labels, DataRequired)
- `app/models.py` - Product + ProductImage models with D-08 status property
- `app/auth.py` - user_loader, unauthorized_handler, login GET/POST, logout POST
- `app/__init__.py` - login_manager + csrf init, login_view, login_message
- `app/admin.py` - before_request @login_required guard
- `app/templates/auth/login.html` - Flask-WTF form with hidden_tag
- `app/templates/base.html` - flash zone added (required for D-12 error to render)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Flash zone needed in base.html for Plan 02 verify**
- **Found during:** Task 2
- **Issue:** The plan's own verify asserts `Sai tên đăng nhập hoặc mật khẩu` renders in the login page after a wrong password, but Plan 03 Task 2 is what officially adds the flash zone to base.html. Without it the flash never renders.
- **Fix:** Added the flash zone (get_flashed_messages with categories) to base.html now.
- **Files modified:** app/templates/base.html
- **Commit:** c34c939

### Verification Note

Plan 02 Task 3 verify expected the unauthenticated /admin/ Location to contain `next=%2Fadmin%2F` (URL-encoded). Werkzeug 3.1.8 renders the decoded `/login?next=/admin/`. Functionally identical — `next` carries only the path, the safe-redirect check (`startswith('/')`, rejects `//`) passes, and post-login redirect-back to /admin/ was confirmed (REDIRECT_BACK_OK).

## Verification
- Login flow: GET /login (200 + CSRF) -> POST valid (302 /admin/) -> GET /admin/ (200)
- Logout: POST /logout (302 /login), then /admin/ redirects to /login
- Error flow: wrong password 200 + generic VN flash
- Redirect-back: /admin/ unauth -> /login?next=/admin/ -> login -> /admin/
- Tables: admin_users, products, product_images all created by init-db
