---
phase: 01-scaffold-auth-data-model
reviewed: 2026-08-01T12:55:00Z
depth: deep
files_reviewed: 19
files_reviewed_list:
  - wsgi.py
  - app/__init__.py
  - app/db.py
  - app/models.py
  - app/forms.py
  - app/auth.py
  - app/admin.py
  - app/public.py
  - app/templates/base.html
  - app/templates/auth/login.html
  - app/templates/admin/dashboard.html
  - app/templates/public/index.html
  - app/templates/errors/404.html
  - app/templates/errors/500.html
  - app/static/css/style.css
  - .env.example
  - .flaskenv
  - requirements.txt
  - .gitignore
findings:
  blocker: 0
  high: 1
  medium: 2
  low: 6
  total: 9
status: issues_found
---

# Phase 1: Scaffold + Auth + Data Model — Code Review Report

**Reviewed:** 2026-08-01T12:55:00Z
**Depth:** deep (cross-file trace + empirical probes via Flask test client)
**Files Reviewed:** 19
**Status:** issues_found

## Summary

Phase 1 delivers a working Flask skeleton: app factory, SQLite WAL + busy_timeout, scrypt-hashed single-admin auth with CSRF-protected login/logout, Product/ProductImage/AdminUser data model, Vietnamese templates, and generic 404/500 handlers. All PLAT-01..04 and AUTH-01..04 requirements are functionally satisfied, and the CSRF enforcement, `next`-guard, WAL pragma, and SECRET_KEY fail-fast were empirically confirmed (see probes below).

However, review found **1 high, 2 medium, and 6 low** issues. The high-severity item breaks D-15 redirect-back (the login form drops the `next` parameter, so post-login return-to-original-page never works for any admin page other than the dashboard — currently masked because `/admin/` is the only admin route). Two medium items violate UI-SPEC/D-10: flash messages never render in their semantic colors, and the "30-day session" is not actually implemented (the session cookie is a browser-session cookie and the remember token lasts 365 days). No blocker-level defects (data loss, auth bypass, injection) were found.

**Verification method:** each finding was reproduced with a Flask test client against the real app (fresh `init-db`), not just read from source. Relevant probe output is cited per finding.

## High Issues

### CR-01: D-15 redirect-back is broken — login form drops the `next` parameter

**File:** `app/templates/auth/login.html:6` (root cause) + `app/auth.py:30` (reads `next` only from query string)

**Issue:** The `unauthorized_handler` correctly redirects unauthenticated admin access to `/login?next={request.path}` (`app/auth.py:20`), but the login form action is a bare `{{ url_for('auth.login') }}` — it renders as `action="/login"` with **no `next` preserved**. When the browser submits the form, it POSTs to `/login` with an empty query string, so `request.args.get('next')` at `app/auth.py:30` returns `None` and the code always falls back to `url_for('admin.dashboard')`. D-15 requires the admin to return to *the exact page originally requested*; the `next` value is silently discarded in the normal browser flow.

This is currently invisible because `/admin/` is the only admin route and the fallback happens to equal the requested target. It will silently break in Phase 2 the moment there is any second admin route (e.g. `/admin/products/1/edit`).

**Empirical proof (test client, fresh init-db):**
```
GET /admin/                    -> 302 Location: /login?next=/admin/
GET /login?next=/admin/        -> login form, <form action="/login"> (no next)
POST /login (as browser does)  -> 302 Location: /admin/            # fallback, next dropped
POST /login?next=/admin/products (manual, next in query) -> /admin/products  # code works only if next survives
```

**Fix:** preserve `next` across the POST. Two equivalent options (do one):

```html
<!-- app/templates/auth/login.html -->
<form method="post" action="{{ url_for('auth.login', next=request.args.get('next')) }}">
```

or add a hidden field inside the form:

```html
<input type="hidden" name="next" value="{{ request.args.get('next') }}">
```

and in `app/auth.py:30` read from both sources:

```python
next_url = request.values.get('next')
```

## Medium Issues

### WR-01: Flash messages never render in their semantic colors

**Files:** `app/templates/base.html:18` + `app/static/css/style.css:45-46`

**Issue:** The flash zone renders `<div class="flash {{ category }}">`, producing `class="flash error"` and `class="flash success"` (space-separated). The stylesheet only defines `.flash-error { color: var(--destructive) }` and `.flash-success { color: var(--success) }` (hyphenated single class names). These selectors do **not** match `class="flash error"`, so the destructive red (`#DC2626`) for "Sai tên đăng nhập hoặc mật khẩu" and green (`#059669`) for "Bạn đã đăng xuất thành công" are never applied — the single most important error-state cue on the login page renders in the default dark-gray body color, violating the UI-SPEC Interaction Contract.

**Empirical proof:** rendered login-failure HTML is `<div class="flash error">`; `style.css` contains `.flash-error` but not `.flash.error`.

**Fix:** align one side to the other. Either render the category with the `flash-` prefix in the template:

```html
<div class="flash-{{ category }}">{{ message }}</div>
```

or widen the CSS selectors:

```css
.flash-error, .flash.error { color: var(--destructive); }
.flash-success, .flash.success { color: var(--success); }
```

### WR-02: "30-day session" (D-10) is not implemented — session is a browser-session cookie + 365-day remember token

**Files:** `app/__init__.py:37` + `app/auth.py:29`

**Issue:** `PERMANENT_SESSION_LIFETIME = timedelta(days=30)` is configured, but nothing ever sets `session.permanent = True`, so Flask never attaches the 30-day expiry to the session cookie — it stays a browser-session cookie that dies on browser close. Independently, `login_user(user, remember=True)` sets a separate `remember_token` cookie whose lifetime defaults to `REMEMBER_COOKIE_DURATION` = **365 days** (Flask-Login config). The remember token re-authenticates the admin after every session-cookie loss, so the practical "stay logged in" duration is up to **one year**, not the 30 days D-10 specifies.

**Empirical proof:** after login, `Set-Cookie: session=...` carries `HttpOnly;Path;SameSite` with **no Expires/Max-Age**; `Set-Cookie: remember_token=...` carries `Expires=Sun, 01 Aug 2027` (365 days).

**Fix:** make the intended 30-day lifetime real and bound the remember token to it:

```python
# app/auth.py, after login_user(...):
from flask import session
session.permanent = True

# app/__init__.py, after login_manager.init_app(app):
from datetime import timedelta
login_manager.remember_cookie_duration = timedelta(days=30)
```

## Low Issues

### WR-03: `SESSION_COOKIE_SECURE` is effectively always False (deprecated `FLASK_ENV` mechanism)

**File:** `app/__init__.py:40`

**Issue:** `SESSION_COOKIE_SECURE=(os.environ.get('FLASK_ENV') == 'production')`. `FLASK_ENV` is the Flask 2.x signal, deprecated in 2.2 and removed in Flask 3.x; nothing in `.env.example`, `.flaskenv`, README, or the deployment path sets it, so this is `False` in every documented run mode. In a production deployment behind TLS the session cookie will still be sent over plain HTTP, weakening the auth cookie. Not a live defect in dev (HTTP is expected there), but the config silently can never do what its name promises.

**Empirical proof:** `SESSION_COOKIE_SECURE = False` with `FLASK_ENV` unset.

**Fix:** drive it from its own env var:

```python
SESSION_COOKIE_SECURE=os.environ.get('SESSION_COOKIE_SECURE', '').lower() in ('1', 'true', 'yes'),
```

and document it in `.env.example` / README (set to `true` when serving over HTTPS).

### WR-04: `init-db` accepts a whitespace-only or placeholder-variant password

**File:** `app/db.py:24-25`

**Issue:** D-03/D-04 guards check `== 'change-me'` and `len(...) < 8`. A password of 8 spaces (`"        "`) satisfies the length check and is accepted; so is `"change-me "` with trailing whitespace. These are trivially weak placeholders that defeat the intent of the fail-fast guards. `ADMIN_USERNAME` is also used unstripped.

**Empirical proof:** `init-db` with `ADMIN_PASSWORD="        "` exits 0 and upserts the admin.

**Fix:**

```python
if not admin_password.strip() or len(admin_password.strip()) < 8:
    raise click.ClickException('ADMIN_PASSWORD must be at least 8 non-whitespace characters.')
if admin_password.strip() == 'change-me':
    raise click.ClickException('ADMIN_PASSWORD is still "change-me". ...')
```

### WR-05: `login_manager.login_message` is dead configuration

**Files:** `app/__init__.py:55` + `app/auth.py:18-20`

**Issue:** `login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'` is configured, but a custom `@login_manager.unauthorized_handler` is registered, which takes precedence over Flask-Login's default unauthorized flow. The default flow is what flashes `login_message`; with the custom handler the message is never flashed (the flash zone also has no such message wired anywhere). The config line is misleading dead code.

**Fix:** remove the `login_message` / `login_message_category` lines, or have `unauthorized()` flash the message before redirecting (if the message is desired on the login page).

### WR-06: `next`-safety guard is fragile (defense-in-depth; not currently exploitable)

**File:** `app/auth.py:31`

**Issue:** The guard `not next_url.startswith('/') or next_url.startswith('//')` is the classic pattern that backslash variants (`/\evil.com`) can slip past. In this stack it is currently neutralized because Werkzeug's `redirect()` percent-encodes the backslash (`/\evil.com` → `Location: /%5Cevil.com`), which browsers resolve as a same-origin path, so no open redirect was reproduced. Still, the guard should not rely on an incidental encoding side effect.

**Empirical proof:** POST with `next=/\evil.com` → `Location: '/%5Cevil.com'` (same-origin, not exploitable).

**Fix (robustness):**

```python
from urllib.parse import urlsplit
if not next_url or urlsplit(next_url).netloc or not next_url.startswith('/'):
    next_url = url_for('admin.dashboard')
```

### WR-07: Dead CSS selector `.nav-group .logout-form`

**File:** `app/static/css/style.css:116`

**Issue:** The logout element is `<div class="nav-group logout-form">` — the `logout-form` class is on the same element as `nav-group`, so the descendant selector `.nav-group .logout-form` never matches. Harmless today (the element's own `.nav-group { margin-top: 16px }` rule applies the intended spacing), but it is dead code that misleads future edits.

**Fix:** change to `.nav-group.logout-form`, or drop the rule.

### WR-08: `datetime.utcnow` deprecated in Python 3.12+

**Files:** `app/models.py:14,32,50` + `app/__init__.py:62`

**Issue:** `datetime.utcnow()` is deprecated in Python 3.12 and will be removed in a future release; the project targets Python 3.10+ and the local env runs 3.11, so it works today but is a future breakage. It is also timezone-naive (stored as UTC), which is consistent across all columns so not a correctness bug now.

**Fix:** switch defaults to a timezone-aware UTC helper:

```python
from datetime import datetime, timezone
def utcnow():
    return datetime.now(timezone.utc)
```

and use `default=utcnow` (and `onupdate=utcnow`) in the model columns and the `current_year` context processor.

---

## Explicit "No Findings" Confirmation

- **Blocker / critical:** none found.
- **Security:** no auth bypass, no SQL/command/path injection, no XSS (Jinja autoescape on; `current_user.username` and flash text escaped), no open redirect reproduced (WR-06), CSRF enforced (verified POST without token → 400), password stored as scrypt hash, SECRET_KEY fail-fast verified. The D-12 no-lockout / no-rate-limit posture matches the decision.
- **Vietnamese copy:** all copy matches the UI-SPEC Copywriting Contract verbatim (coming-soon, login, dashboard, 404, 500, flash strings). No copy defects found.
- **CONTEXT.md / UI-SPEC deviations:** D-05..D-09, D-11, D-12, D-13, D-14 honored; deviations limited to CR-01 (D-15), WR-01 (UI-SPEC flash colors), WR-02 (D-10).

---

_Reviewed: 2026-08-01T12:55:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_

---

## Fix Applied

Fixed on 2026-08-01 by `gsd-code-review --fix` (worktree branch `gsd-reviewfix/01-1243`, merged to `master`).

| ID | Severity | Status | Commit |
|----|----------|--------|--------|
| CR-01 | High | Fixed — login form now carries `next` as a hidden input; `auth.py` reads it via `request.values.get('next')`, so D-15 redirect-back works for all admin routes | `a7a8d53` |
| WR-01 | Medium | Skipped — already resolved in Phase 2 (commit `0f43307` added `.flash-error, .flash.error` / `.flash-success, .flash.success` / `.flash-warning, .flash.warning`, matching `class="flash {{ category }}"` markup) | — |
| WR-02 | Medium | Fixed — `session.permanent = True` on login + `REMEMBER_COOKIE_DURATION=timedelta(days=30)` in config, so both the session cookie and the remember token now expire in 30 days (D-10) | `5b726a3` |
| WR-03 | Low | Fixed — `SESSION_COOKIE_SECURE` now driven by its own `SESSION_COOKIE_SECURE` env var (deprecated `FLASK_ENV` mechanism removed); documented in `.env.example` | `b8193a9` |
| WR-04 | Low | Fixed — `init-db` rejects whitespace-only / whitespace-padded `ADMIN_PASSWORD`; `ADMIN_USERNAME` stripped | `6668b8f` |
| WR-05 | Low | Fixed — removed dead `login_manager.login_message` / `login_message_category` (superseded by custom `unauthorized_handler`) | `b2869a0` |
| WR-06 | Low | Fixed — `next`-guard hardened with `urlsplit` (rejects scheme/host and `//` URLs) | `9fcc405` |
| WR-07 | Low | Fixed — `.nav-group .logout-form` (descendant, never matched) → `.nav-group.logout-form` (compound) | `56d7dad` |
| WR-08 | Low | Fixed — `datetime.utcnow` → tz-aware `utcnow()` helper in `app/models.py`; `current_year` uses `datetime.now(timezone.utc)` | `de89cd8` |

**Verification:** Flask test client after fixes — `GET /admin/` → `302 /login?next=/admin/`, login form contains hidden `next=/admin/`, browser-style POST returns `302 /admin/` (target preserved); `next` guard blocks `//evil.com` / `http://evil.com`; session + remember_token cookies both `Expires` ≈ 30 days; `init-db` rejects whitespace-only password; `SESSION_COOKIE_SECURE` env-driven. All checks passed.

**Note:** WR-08's `app/__init__.py` change (timezone import + `current_year`) landed inside the WR-05 commit `b2869a0` because both were uncommitted when WR-05 staged `app/__init__.py`. Final state is identical; only the commit boundary differs.
