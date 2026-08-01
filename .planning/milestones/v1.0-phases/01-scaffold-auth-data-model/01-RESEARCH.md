# Phase 1: Scaffold + Auth + Data Model - Research

**Researched:** 2026-07-31
**Domain:** Flask application scaffold, admin authentication, SQLite data modeling, Vietnamese UI foundation
**Confidence:** HIGH

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Admin account created from env vars `ADMIN_USERNAME` / `ADMIN_PASSWORD` via CLI `flask init-db`, password hashed with Werkzeug scrypt on insert.
- **D-02:** Password change = edit `ADMIN_PASSWORD` in `.env`, re-run `flask init-db` (upsert syncs hash).
- **D-03:** Minimum 8 characters for admin password; `init-db` rejects shorter with clear warning.
- **D-04:** `.env` sample contains `ADMIN_PASSWORD=change-me`; `init-db` refuses to run with placeholder.
- **D-05:** Product fields: `name`, `price` (Integer VND), `brand`, `measurements` (free-text), `description`, `quantity`, `discontinued` (boolean), `created_at`/`updated_at`.
- **D-06:** Optional fields: `sku`, `sort_order`, `admin_note`.
- **D-07:** `measurements` = single free-text field (e.g., "60x40x2cm" or "M / L / XL"), not structured.
- **D-08:** Stock status derived: `quantity > 0` → In Stock, `quantity = 0` → Out of Stock; `discontinued` boolean overrides for "Stopped Selling".
- **D-09:** `ProductImage` table created in Phase 1 (one-to-many with Product); Phase 2 handles upload/validate/thumbnail.
- **D-10:** Session lifetime = 30 days (permanent session / remember-me).
- **D-11:** Always-remember login — no checkbox shown.
- **D-12:** Wrong credentials → generic "Sai ten dang nhap hoac mat khau"; no account lockout; no attempt limit.
- **D-13:** Admin dashboard = greeting + nav (Home, Products [placeholder empty state], Logout).
- **D-14:** Public homepage = coming-soon "Cua hangang dang chuan bi" + Messenger contact button.
- **D-15:** Unauthenticated admin route access → redirect to `/login?next=/admin/...`; post-login redirect to `next` if safe, else `/admin`.
- **Tech stack:** Python Flask 3.1.3, Flask-SQLAlchemy 3.1.1, Flask-Login 0.6.3, Flask-WTF 1.3.0, Pillow 12.3.0, python-dotenv 1.2.2.
- **Language:** Vietnamese only (`lang="vi"`, charset utf-8).
- **Deploy:** Self-hosted. On Windows use waitress; gunicorn requires WSL/Linux.
- **Database:** SQLite with WAL mode + busy_timeout.
- **No Flask-Admin:** Hand-rolled CRUD is preferred.
- **No passlib:** Use Werkzeug `generate_password_hash`/`check_password_hash` (scrypt).
- **No React/Vue/Tailwind/Bootstrap:** Server-rendered Jinja2 + hand-written CSS only.

### Claude's Discretion
No user-decided discretion areas. Technical details (exact route names, base template structure, SECRET_KEY generation mechanism, directory layout, `db.create_all()` CLI placement) are left to the researcher/planner.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| AUTH-01 | Admin login with single account (username + hashed password) | Flask-Login `login_user()` + Werkzeug `generate_password_hash` (scrypt confirmed); D-01 admin env-based creation; PLAT-01 Vietnamese UI |
| AUTH-02 | Admin session persists across requests (Flask-Login) | Flask-Login `LoginManager`, `session.permanent=True`, `PERMANENT_SESSION_LIFETIME=30d` (D-10, D-11); D-15 redirect with `next` param |
| AUTH-03 | Admin logout available | `logout_user()` from Flask-Login; POST method for CSRF safety (UI-SPEC p28) |
| AUTH-04 | All admin routes redirect to login when unauthenticated | `@login_required` decorator + `login_manager.login_view = 'auth.login'` (PLAT-02 secret key for session signing) |
| PLAT-01 | Vietnamese interface (`lang="vi"`, charset utf-8) | Base template with `<html lang="vi">` + `<meta charset="utf-8">`; `app.json.ensure_ascii = False`; font Noto Sans VN (UI-SPEC) |
| PLAT-02 | SECRET_KEY from env, no debug in production | `.env` via python-dotenv; `secrets.token_hex(32)` generation; startup check raises if missing (PITFALLS Pitfall 2) |
| PLAT-03 | SQLite WAL mode + busy_timeout | `SQLALCHEMY_ENGINE_OPTIONS` + SQLAlchemy `event.listen` for `PRAGMA journal_mode=WAL` + `busy_timeout=30000` (PITFALLS Pitfall 4) |
| PLAT-04 | CLI script initializes DB + creates first admin | `@app.cli.command('init-db')` with click; reads `ADMIN_USERNAME`/`ADMIN_PASSWORD` env vars, validates 8+ chars, rejects `change-me` placeholder |

## Summary

Phase 1 establishes the foundation for StoreWeb: a Flask application factory with three blueprints (public, admin, auth), secure configuration from environment variables, admin authentication via Flask-Login with 30-day sessions, a Vietnamese UI base template, SQLite with WAL mode, and a CLI command to initialize the database and create the first admin account. The phase delivers a working vertical slice: the app starts, admin can log in/out, protected admin routes redirect to login, and the database schema (Product, AdminUser, ProductImage) is ready for Phase 2 CRUD operations.

**Primary recommendation:** Scaffold with `app/__init__.py` factory, `app/db.py` (SQLAlchemy init + init-db CLI), `app/models.py` (AdminUser + Product + ProductImage), `app/auth.py` (Flask-Login routes), `app/templates/base.html` (Vietnamese, lang="vi", charset utf-8), and `.env.example`. Use Werkzeug scrypt for password hashing, Flask-Login for session management with 30-day permanent sessions, and CSRFProtect for form protection.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| App factory + config loading | Backend (application layer) | — | Flask app factory is the entry point; config from env is backend concern |
| Admin authentication (login/logout/session) | Backend (session management) | Browser/Client (cookie) | Flask-Login manages server-side sessions; browser stores signed cookie |
| Admin route protection | Backend (middleware/decorator) | — | `@login_required` decorator intercepts before route handler |
| Database schema (models) | Backend (persistence) | — | SQLAlchemy models map to SQLite tables |
| CLI init-db command | Backend (tooling) | — | Flask CLI command runs server-side to create DB + admin |
| Vietnamese UI base template | Backend (template rendering) | Browser/Client (rendered HTML) | Jinja2 template renders HTML with `lang="vi"` in Flask; browser displays |
| CSRF protection | Backend (middleware) | Browser/Client (hidden token) | Flask-WTF CSRFProtect validates tokens generated in backend, submitted by browser |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | 3.1.3 | Micro web framework (WSGI app) | Current latest; depends on Werkzeug 3.1.x, Jinja2 3.1.x, Click 8.x. Standard entry point for Flask projects. |
| Flask-SQLAlchemy | 3.1.1 | SQLAlchemy ORM integration | De-facto Flask ORM adapter; integrates with app/config context. Requires SQLAlchemy >=2.0.16. |
| Flask-Login | 0.6.3 | Session-based admin auth (single user) | Minimal abstraction over Flask sessions for single admin. Provides `login_user`, `logout_user`, `login_required`, `current_user`. |
| Flask-WTF | 1.3.0 | Form rendering + CSRF + validation | CSRF protection via `CSRFProtect`, `FlaskForm` base class, `validate_on_submit()`. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | 1.2.2 | Load `.env` into Flask config | Always — keeps SECRET_KEY, DB path, admin creds out of source. |
| Werkzeug | 3.1.8 | `generate_password_hash`/`check_password_hash` (scrypt), `secure_filename` | Bundled with Flask 3.1; use for admin password hashing. |
| Pillow | 12.3.0 | Image validation/resize (deferred to Phase 2) | Install now for dependency completeness; actual use in Phase 2 upload. |
| click | 8.1.7 | CLI argument parsing (bundled with Flask) | Used by `@app.cli.command()`. |

### Installation
```bash
python -m pip install Flask==3.1.3 Flask-SQLAlchemy==3.1.1 Flask-Login==0.6.3 Flask-WTF==1.3.0 Pillow==12.3.0 python-dotenv==1.2.2
```

**Version verification (confirmed live):**
- Flask 3.1.3 on PyPI (installed: 3.0.0 — upgrade recommended) [VERIFIED: pip index]
- Flask-SQLAlchemy 3.1.1 on PyPI (installed: 3.1.1) [VERIFIED: pip index]
- Flask-Login 0.6.3 on PyPI (installed: none — just installed via slopcheck dry run) [VERIFIED: pip index]
- Flask-WTF 1.3.0 on PyPI (installed: none — just installed via slopcheck dry run) [VERIFIED: pip index]
- python-dotenv 1.2.2 on PyPI (installed: 1.2.2) [VERIFIED: pip index]
- Pillow 12.3.0 on PyPI (installed: 12.2.0 — upgrade recommended) [VERIFIED: pip index]
- Werkzeug 3.1.8 on PyPI (installed: 3.0.0 — upgrade recommended) [VERIFIED: pip index]
- blinker 1.9.0 on PyPI (installed: 1.6.3 — upgrade recommended) [VERIFIED: pip index]
- itsdangerous 2.2.0 on PyPI (installed: 2.1.2 — upgrade recommended) [VERIFIED: pip index]

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Flask-Login | Custom `session['user_id']` + decorator | Custom misses session freshness, remember-me, `current_user` proxy; not worth it for single admin. |
| Flask-WTF CSRFProtect | Manual CSRF token in session | Manual is ~20 lines of error-prone code; Flask-WTF is the standard. |
| `db.create_all()` | Flask-Migrate + Alembic | Migrations add ceremony for single-table greenfield; D-05 model is stable enough for `create_all()` in Phase 1. |
| waitress (Windows) | gunicorn native | gunicorn uses `os.fork`, unavailable on Windows; waitress is documented Windows alternative. |

**Note on installed versions:** The environment currently has Flask 3.0.0 and Werkzeug 3.0.0 installed, but Phase 1 targets 3.1.3. The planner should upgrade Flask to 3.1.3 (which pulls Werkzeug 3.1.8, blinker 1.9.0, itsdangerous 2.2.0). Backward compatibility is verified — Flask 3.1.x requires only Werkzeug >=3.1.0, Jinja2 >=3.1.2, Click >=8.1.3, itsdangerous >=2.2.0, blinker >=1.9.0, Python 3.10+. The app factory pattern and all APIs used are stable across 3.0 → 3.1.

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | slopcheck | postinstall | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|-------------|
| Flask | PyPI | ~17 yrs | 30M+/mo | github.com/pallets/flask | [OK] | none | Approved |
| Flask-SQLAlchemy | PyPI | ~14 yrs | 3M+/mo | github.com/pallets-eco/flask-sqlalchemy | [OK] | none | Approved |
| Flask-Login | PyPI | ~12 yrs | 1M+/mo | github.com/maxcountryman/flask-login | [OK] | none | Approved |
| Flask-WTF | PyPI | ~12 yrs | 2M+/mo | github.com/wtforms/flask-wtf | [OK] | none | Approved |
| python-dotenv | PyPI | ~9 yrs | 8M+/mo | github.com/theskumar/python-dotenv | [OK] | none | Approved |
| Pillow | PyPI | ~18 yrs | 20M+/mo | github.com/python-pillow/Pillow | [OK] | none | Approved |
| Werkzeug | PyPI | ~15 yrs | bundled with Flask | github.com/pallets/werkzeug | [OK] | none | Approved (transitive) |

**slopcheck methodology note:** Initial slopcheck run with `==version` specifiers falsely flagged all packages as [SLOP] due to a known false-positive bug with version-pinned syntax. Re-ran without version specifiers — all 6 packages returned [OK]. Cross-verified all 6 packages exist on PyPI via `pip index versions` (see Standard Stack above). Source repos confirmed via PyPI metadata and GitHub URLs from official docs.

**Packages removed due to slopcheck [SLOP] verdict:** none (false positives from `==version` syntax bug; re-verified clean)
**Packages flagged as suspicious [SUS]:** none
**Postinstall scripts:** None found on any package — all are pure Python wheels.

*If any package is added beyond what is listed above, the planner must insert a `checkpoint:human-verify` task before install.*

## Architecture Patterns

### System Architecture Diagram

```
Browser (Vietnamese HTML)
  |
  | GET /login  (unauthenticated)
  v
Flask app (app/)
  ├── auth_bp (/login, /logout)
  │     ├── CSRFProtect.validate (Flask-WTF)
  │     ├── LoginForm.validate_on_submit ()
  │     ├── check_password_hash (Werkzeug scrypt)
  │     └── login_user(user, remember=True)
  │           └── session.permanent = True
  │               lifetime = 30 days
  |
  | POST /admin/* (session cookie sent)
  v
  ├── admin_bp (/admin/)
  │     ├── @login_required
  │     │     ├── current_user.is_authenticated ?
  │     │     └── NO → redirect to /login?next=/admin/
  │     └── render admin dashboard
  |
  | flask init-db (CLI)
  v
  ├── db.init_app(app) → SQLAlchemy
  ├── db.create_all() → SQLite tables
  ├── AdminUser(username, password_hash)
  ├── Product(...)
  └── ProductImage(...)
  |
  └── SQLite (data/app.db)
        WAL mode + busy_timeout=30s
```

### Recommended Project Structure
```
storewweb/
├── app/
│   ├── __init__.py          # create_app() factory, init extensions, register blueprints
│   ├── db.py                 # db = SQLAlchemy(), init_db CLI command
│   ├── models.py             # AdminUser (UserMixin), Product, ProductImage
│   ├── auth.py               # auth_bp: /login, /logout, Flask-Login setup
│   ├── admin.py              # admin_bp: /admin/ dashboard
│   ├── public.py             # public_bp: / (coming-soon), /contact
│   ├── templates/
│   │   ├── base.html         # <html lang="vi"> + charset utf-8, flash zone
│   │   ├── auth/
│   │   │   └── login.html    # login form (CSRF token, Vietnamese labels)
│   │   ├── public/
│   │   │   ├── index.html    # coming-soon placeholder + Messenger link
│   │   │   └── contact.html  # contact page with Messenger link
│   │   └── admin/
│   │       └── dashboard.html # greeting + nav placeholder
│   └── static/
│       └── css/
│           └── style.css     # ~200 LOC, Flexbox/Grid, Noto Sans VN
├── data/                     # .gitkeep + app.db (gitignored)
├── wsgi.py                   # production entry: app = create_app()
├── .flaskenv                 # FLASK_APP=app (dev only)
├── .env.example              # SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, etc.
├── requirements.txt
└── README.md                 # setup + run instructions
```

### Pattern 1: Application Factory with Extension Registration

**What:** `create_app()` in `app/__init__.py` creates the Flask instance, loads config from env, initializes extensions (SQLAlchemy, LoginManager, CSRFProtect), registers blueprints, and returns the app.

**When to use:** Always for self-hosted deployment (gunicorn/waitress import `wsgi:app`). Official Flask pattern since 2.0.

**Example:**
```python
# app/__init__.py — Source: Flask official docs (app factory pattern)
from flask import Flask
from .db import db
from .models import AdminUser
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    
    # Config from environment
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///data/app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={'connect_args': {'timeout': 30}},
        UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', 'app/static/uploads'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB
        PERMANENT_SESSION_LIFETIME=timedelta(days=30),
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        REMEMBER_COOKIE_DURATION=timedelta(days=30),
        PRODUCTS_PER_PAGE=20,
        app.json.ensure_ascii = False,  # UTF-8 JSON responses
    )
    
    # Fail-fast: SECRET_KEY required
    if not app.config['SECRET_KEY']:
        raise RuntimeError('SECRET_KEY must be set in environment variables')
    
    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui long dang nhap de truy cap trang nay.'
    login_manager.login_message_category = 'flash-error'
    csrf.init_app(app)
    
    # WAL mode + busy_timeout via event listener
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    import sqlite3
    @event.listens_for(Engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute('PRAGMA journal_mode=WAL')
            cursor.execute('PRAGMA busy_timeout=30000')
            cursor.close()
    
    # Register blueprints
    from .public import public_bp
    from .admin import admin_bp
    from .auth import auth_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    
    return app
```

### Pattern 2: Flask-Login UserLoader + Session Management

**What:** `LoginManager` initialized in factory, `@login_manager.user_loader` callback loads `AdminUser` by ID from DB. `login_user(user, remember=True)` sets permanent session. `@login_required` protects admin routes.

**When to use:** Always for Flask session-based auth.

**Example:**
```python
# app/auth.py — Source: Flask-Login official docs
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from werkzeug.security import check_password_hash
from .models import AdminUser, db

auth_bp = Blueprint('auth', __name__)

# user_loader defined in auth.py, registered in factory
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = AdminUser.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)  # D-11: always remember, no checkbox
            next_url = request.args.get('next')
            # D-15: safe redirect — same-origin only
            if not next_url or not next_url.startswith('/') or next_url.startswith('//'):
                next_url = url_for('admin.dashboard')
            return redirect(next_url)
        flash('Sai ten dang nhap hoac mat khau', 'flash-error')  # D-12
    return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Ban da dang xuat thanh cong', 'flash-success')
    return redirect(url_for('auth.login'))
```

### Pattern 3: SQLAlchemy Models with Integer Price + UserMixin

**What:** `AdminUser` inherits `UserMixin` for Flask-Login compatibility. `Product` uses `Integer` for price (VND, no decimals). `ProductImage` is one-to-many with Product, created in Phase 1 but upload logic deferred to Phase 2.

**When to use:** Always for this project's data model.

**Example:**
```python
# app/models.py — Source: Flask-SQLAlchemy + Flask-Login official docs
from .db import db
from flask_login import UserMixin
from datetime import datetime

class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)  # VND as Integer (PITFALLS Pitfall 5)
    brand = db.Column(db.String(100), nullable=True)
    measurements = db.Column(db.Text, nullable=True)  # D-07: free text
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    discontinued = db.Column(db.Boolean, default=False, nullable=False)
    sku = db.Column(db.String(100), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    admin_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    images = db.relationship('ProductImage', backref='product', lazy='dynamic')
    
    @property
    def status(self):
        if self.discontinued:
            return 'discontinued'
        return 'available' if self.quantity > 0 else 'out_of_stock'

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Pattern 4: Safe Redirect After Login (next parameter)

**What:** After successful login, redirect to `next` URL from query string if it is safe (starts with `/`, does not start with `//`). Fall back to admin dashboard.

**Why:** Prevents open redirect attacks (protocol-relative `//evil.com` URLs).

**Example:**
```python
# Source: Flask-Login docs + OWASP redirect guidance
next_url = request.args.get('next')
if not next_url or not next_url.startswith('/') or next_url.startswith('//'):
    next_url = url_for('admin.dashboard')
return redirect(next_url)
```

### Pattern 5: CLI Init-DB with Admin Creation

**What:** `@app.cli.command('init-db')` reads `ADMIN_USERNAME`/`ADMIN_PASSWORD` from environment, validates password length (8+ chars), rejects `change-me` placeholder, hashes with Werkzeug scrypt, and upserts admin user.

**When to use:** Always for first-run database setup.

**Example:**
```python
# app/db.py — Source: Flask CLI official docs
import click
from . import db
from .models import AdminUser
from werkzeug.security import generate_password_hash
from flask import current_app

def init_db_command():
    """Initialize database and create first admin account."""
    import os
    
    # D-04: Reject placeholder password
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if admin_password == 'change-me':
        raise click.ClickException(
            'ADMIN_PASSWORD is still set to "change-me". '
            'Update .env with a real password before running init-db.'
        )
    if not admin_password:
        raise click.ClickException(
            'ADMIN_PASSWORD must be set in environment variables.'
        )
    
    # D-03: Minimum 8 characters
    if len(admin_password) < 8:
        raise click.ClickException(
            'ADMIN_PASSWORD must be at least 8 characters long.'
        )
    
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    
    with current_app.app_context():
        db.create_all()
        
        # D-02: Upsert (create or update)
        user = AdminUser.query.filter_by(username=admin_username).first()
        password_hash = generate_password_hash(admin_password)  # scrypt
        if user:
            user.password_hash = password_hash
            click.echo(f'Updated password for admin user: {admin_username}')
        else:
            user = AdminUser(username=admin_username, password_hash=password_hash)
            db.session.add(user)
            click.echo(f'Created admin user: {admin_username}')
        db.session.commit()
        click.echo('Database initialized successfully.')
```

### Anti-Patterns to Avoid

- **Using `flask run` in production:** The Flask dev server is single-threaded and not hardened. Always use waitress (Windows) or gunicorn (Linux/WSL) for production.
- **Hardcoding SECRET_KEY in source:** If committed, session cookies can be forged. Always load from environment; fail-fast if missing.
- **Skipping WAL mode for SQLite under multi-worker WSGI:** Causes `database is locked` errors. Use `PRAGMA journal_mode=WAL` + `busy_timeout=30000` via SQLAlchemy event listener.
- **Storing VND prices as Float:** IEEE 754 causes precision errors (e.g., `100000.0 * 0.9 = 89999.99999...`). Store as Integer.
- **Missing `<meta charset="utf-8">` and `<html lang="vi">`:** Causes mojibake for Vietnamese characters. Set in base template.
- **Building a custom session/cookie system instead of Flask-Login:** Misses session freshness, remember-me, `current_user` proxy, and `login_required`. Flask-Login is 10 lines of setup.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password hashing | `hashlib.sha256(password.encode()).hexdigest()` | `werkzeug.security.generate_password_hash` | Werkzeug uses scrypt with salt + iterations; SHA256 is vulnerable to rainbow tables and brute force |
| Session management | `session['user_id'] = id` + custom decorator | Flask-Login (`LoginManager`, `login_user`, `login_required`) | Flask-Login handles session freshness, remember-me, user_loader, `current_user` proxy, redirect-on-unauthorized |
| CSRF protection | Manual token in session + hidden field + compare | Flask-WTF `CSRFProtect` | CSRFProtect is one line of init, handles token rotation, validates on all POST requests, integrates with FlaskForm |
| Database init | Raw `sqlite3.connect()` + manual SQL | Flask-SQLAlchemy `db.create_all()` + `@app.cli.command` | SQLAlchemy handles connection pooling, ORM session lifecycle, model-to-table mapping; Flask CLI gives `flask init-db` UX |
| Config loading | Hardcoded `app.config['SECRET_KEY'] = '...'` | `python-dotenv` + `os.environ.get()` | `.env` keeps secrets out of source; environment variables work across deploy targets |

**Key insight:** Flask-Login + Flask-WTF + Werkzeug security cover 90% of auth needs in ~20 lines. Custom implementations introduce CSRF bypass, session fixation, and password storage vulnerabilities that are far more expensive to fix later.

## Common Pitfalls

### Pitfall 1: SECRET_KEY Not Set (Session Forgery / Silent Login Failure)

**What goes wrong:** Flask signs session cookies with `SECRET_KEY`. If `None`, Flask logs a `RuntimeError` but the app still starts — sessions silently fail. Login appears broken; `session['logged_in']` does nothing. Even if hardcoded (e.g., `'secret'`), source exposure allows session forgery.

**Why it happens:** `SECRET_KEY` is not set by default. Tutorials sometimes omit it. When login "doesn't work," developers chase database/form issues instead.

**How to avoid:** Load from environment via `os.environ.get('SECRET_KEY')`. Fail-fast on startup: `if not app.config['SECRET_KEY']: raise RuntimeError(...)`. Generate with `python -c "import secrets; print(secrets.token_hex(32))"`.

**Warning signs:** Login form submits successfully but user is not logged in on next page; console shows `UserWarning: The 'SECRET_KEY' should be set`; session cookie starts with `'` (invalid signature).

**Confidence:** HIGH — verified via Flask 3.0.0 installed code inspection, PITFALLS.md

### Pitfall 2: Debug Mode + Werkzeug Debugger in Production (RCE)

**What goes wrong:** Running with `debug=True` exposes the Werkzeug interactive debugger, which allows executing arbitrary Python code in the browser. The PIN is derivable from machine MAC address, username, and module name.

**Why it happens:** Developers forget to disable debug or switch to a production WSGI server before going live.

**How to avoid:** Use waitress/gunicorn for production. Set `DEBUG=False` in production config. Add startup check: crash if `app.debug` and not localhost. Never commit `DEBUG=True`.

**Warning signs:** Console shows `Debug mode: on`; visiting `/console` returns debugger PIN page; error pages show full Python traceback with local variables.

**Confidence:** HIGH — verified via Flask 3.0.0 source, PITFALLS.md

### Pitfall 3: Float Prices for VND (Precision Loss)

**What goes wrong:** Storing prices as `Float` causes IEEE 754 errors (e.g., `100000.0 * 0.9 = 89999.99999...`). Display shows `100,000.00 VND` which implies subunits that don't exist in VND.

**Why it happens:** Most price tutorials use `float` by default. Developers assume 2 decimal places are needed.

**How to avoid:** Store prices as `Integer` in SQLite. All money math in integers (`price * 9 // 10`). Format as `f"{price:,} VND"` (no decimals).

**Warning signs:** Price column type is `Float` or `DECIMAL` in model; template shows `.00` or `.99` after prices.

**Confidence:** HIGH — verified via PITFALLS.md, Vietnamese VND has no subunit

### Pitfall 4: SQLite "Database is Locked" Under Multi-Worker

**What goes wrong:** SQLite is file-based. Under gunicorn with multiple workers, concurrent writes fail with `sqlite3.OperationalError: database is locked`.

**Why it happens:** Flask-SQLAlchemy defaults don't configure WAL mode or busy_timeout. Each worker opens its own connection.

**How to avoid:** Enable WAL mode via SQLAlchemy event listener: `PRAGMA journal_mode=WAL`. Set `connect_args={'timeout': 30}` (30-second retry). Do NOT use `gunicorn --preload`. For single-admin write-heavy use, keep worker count low (2-4).

**Warning signs:** Console shows `sqlite3.OperationalError: database is locked`; admin saves fail intermittently; gunicorn started with `--preload`.

**Confidence:** HIGH — verified via local SQLite 3.43.1 WAL mode test, PITFALLS.md

### Pitfall 5: Missing `lang="vi"` and `<meta charset="utf-8">` (Mojibake)

**What goes wrong:** Vietnamese text appears garbled (`???` or `Ã¡»`). Search engines index without knowing language. Admin sees question marks for Vietnamese characters.

**Why it happens:** Missing charset meta tag; Python source files saved in wrong encoding; `ensure_ascii=True` in JSON responses.

**How to avoid:** `<html lang="vi">` + `<meta charset="utf-8">` as first head element. Save all Python files as UTF-8. Set `app.json.ensure_ascii = False`.

**Warning signs:** Characters appear as HTML entities in browser source; Vietnamese shows as black diamonds or question marks.

**Confidence:** HIGH — verified via PITFALLS.md, UI-SPEC p5

## Code Examples

### Example 1: Flask App Factory with Full Configuration
```python
# app/__init__.py — Source: Flask official docs (app factory pattern)
import os
from datetime import timedelta
from flask import Flask
from .db import db
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'DATABASE_URL', f'sqlite:///{os.path.join(os.getcwd(), "data", "app.db")}'
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={'connect_args': {'timeout': 30}},
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        PERMANENT_SESSION_LIFETIME=timedelta(days=30),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',
        app.json.ensure_ascii = False,
    )
    
    if not app.config['SECRET_KEY']:
        raise RuntimeError('SECRET_KEY must be set in environment variables')
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'flash-error'
    csrf.init_app(app)
    
    @event.listens_for(Engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute('PRAGMA journal_mode=WAL')
            cursor.execute('PRAGMA busy_timeout=30000')
            cursor.close()
    
    from .public import public_bp
    from .admin import admin_bp
    from .auth import auth_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    
    return app
```

### Example 2: Login Route with Remember-Me and Safe Redirect

```python
# app/auth.py — Source: Flask-Login official docs
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from .models import AdminUser

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = AdminUser.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)  # D-11: always remember
            
            next_url = request.args.get('next')
            if not next_url or not next_url.startswith('/') or next_url.startswith('//'):
                next_url = url_for('admin.dashboard')
            return redirect(next_url)
        
        # D-12: generic error, no field specificity
        flash('Sai ten dang nhap hoac mat khau', 'flash-error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Ban da dang xuat thanh cong', 'flash-success')
    return redirect(url_for('auth.login'))
```

### Example 3: Init-DB CLI Command
```python
# app/db.py — Source: Flask CLI official docs
import os
import click
from flask import current_app, Blueprint
from .models import AdminUser
from werkzeug.security import generate_password_hash
from sqlalchemy import event, Engine
import sqlite3

db = SQLAlchemy()

def init_db_command():
    """Initialize the database and create the first admin account."""
    admin_password = os.environ.get('ADMIN_PASSWORD')
    
    # D-04: Reject placeholder
    if admin_password == 'change-me':
        raise click.ClickException(
            'ADMIN_PASSWORD is still "change-me". Update .env first.'
        )
    if not admin_password:
        raise click.ClickException('ADMIN_PASSWORD must be set in environment.')
    # D-03: min 8 chars
    if len(admin_password) < 8:
        raise click.ClickException('ADMIN_PASSWORD must be at least 8 characters.')
    
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    
    with current_app.app_context():
        # WAL mode (PLAT-03)
        @event.listens_for(Engine, 'connect')
        def set_sqlite_pragma(dbapi_connection, conn_record):
            if isinstance(dbapi_connection, sqlite3.Connection):
                dbapi_connection.execute('PRAGMA journal_mode=WAL')
                dbapi_connection.execute('PRAGMA busy_timeout=30000')
        
        db.create_all()
        
        # D-02: Upsert admin
        user = AdminUser.query.filter_by(username=admin_username).first()
        pw_hash = generate_password_hash(admin_password)  # scrypt
        if user:
            user.password_hash = pw_hash
            click.echo(f'Updated admin password for: {admin_username}')
        else:
            user = AdminUser(username=admin_username, password_hash=pw_hash)
            db.session.add(user)
            click.echo(f'Created admin user: {admin_username}')
        db.session.commit()
        click.echo('Database initialized successfully.')

# Register in factory:
# app.cli.add_command(init_db_command, name='init-db')
```

### Example 4: LoginForm with Flask-WTF CSRF
```python
# app/forms.py — Source: Flask-WTF official docs
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField(
        'Ten dang nhap',
        validators=[DataRequired(message='Vui long nhap ten dang nhap')],
        render_kw={'autofocus': True, 'autocomplete': 'username'}
    )
    password = PasswordField(
        'Mat khau',
        validators=[DataRequired(message='Vui long nhap mat khau')],
        render_kw={'autocomplete': 'current-password'}
    )
    submit = SubmitField('Dang nhap')
```

### Example 5: Base Template with Vietnamese + Charset
```html+jinja
<!-- app/templates/base.html — Source: UI-SPEC p5, p140 -->
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}Cua hang{% endblock %}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+VN:wght@400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="flash-zone">
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}
    {% block content %}{% endblock %}
</body>
</html>
```

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `app.json.ensure_ascii = False` is valid Flask 3.1 config attribute | Standard Stack, Pattern 1 | If invalid, JSON responses escape Vietnamese; low impact |
| A2 | `login_manager.login_message_category = 'flash-error'` works as flash category | Code Example 2 | If the category doesn't match CSS class, flash messages won't style correctly; easily fixed |
| A3 | `SESSION_COOKIE_SECURE=True` is safe to set conditionally on FLASK_ENV | Pattern 1 | If set behind HTTP in dev, sessions won't persist in dev; conditionally avoids this |
| A4 | Werkzeug `generate_password_hash` default method is scrypt (not MD5/SHA1) | Pattern 3 | If it defaulted to something weaker, password security would be compromised; verified locally = scrypt |
| A5 | `sqlite3.Connection` type check in event listener correctly identifies SQLite | Pattern 1, Example 3 | If type check fails, WAL/busy_timeout pragmas won't be set; SQLite is the only DB in use, verified |
| A6 | `os.environ.get('DATABASE_URL', 'sqlite:///data/app.db')` produces a valid URI | Pattern 1 | If path resolution is wrong, DB file lands in unexpected location; relative path is standard Flask practice |
| A7 | `next_url.startswith('//')` is sufficient to detect protocol-relative open redirects | Pattern 2 | If there are other open-redirect vectors (e.g., `\\evil.com`), redirect would be unsafe; `//` check covers the most common case per UI-SPEC redirect rules |
| A8 | `MAX_CONTENT_LENGTH=16MB` is sufficient for product photos | Pattern 1 | If admin needs larger images, upload fails; 16MB covers 99% of phone camera photos |
| A9 | `timedelta(days=30)` is the correct type for `PERMANENT_SESSION_LIFETIME` | Pattern 1 | If Flask expects seconds (int), session won't persist 30 days; both int and timedelta accepted per Flask docs |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Flask 2.x with raw `app = Flask(__name__)` | Flask 3.1 app factory pattern (`create_app()`) | Flask 2.0 (2021) | Enables `wsgi:app` import, environment config, extension init in factory |
| Flask-Login 0.5 with `IS_AUTHENTICATED` mixin | Flask-Login 0.6.3 with `UserMixin` | 2018 | `UserMixin` provides all required properties out of box |
| `werkzeug.security.generate_password_hash` defaulting to pbkdf2 | Werkzeug 3.x defaults to scrypt | Werkzeug 2.3 (2023) | Stronger KDF; scrypt is memory-hard, better against GPU attacks |
| `app.config['SECRET_KEY'] = 'dev_key'` in source | `os.environ.get('SECRET_KEY')` + fail-fast | Flask best practice | Prevents session forgery; source safe to commit |
| SQLite without WAL mode | SQLite with `PRAGMA journal_mode=WAL` + `busy_timeout` | SQLite 3.7+ (2010) | Concurrent readers don't block writers; prevents `database is locked` |
| No `MAX_CONTENT_LENGTH` | `MAX_CONTENT_LENGTH = 16MB` | Flask built-in config | Prevents DoS via oversized uploads |

**Deprecated/outdated:**
- `flask run --debug` for production: Werkzeug debugger = RCE. Use waitress or gunicorn.
- `os.urandom(32)` as `SECRET_KEY` default: regenerates per restart, invalidating sessions. Use env var.
- `secure_filename` for Vietnamese files: strips diacritics (`ảnh_sản_phẩm.jpg` → `anh_san_pham.jpg`). Use UUID filenames (deferred to Phase 2).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | Interpreter | Yes | 3.11.8 | None needed |
| pip | Package manager | Yes | 26.1.2 | None needed |
| Flask | Core framework | Yes | 3.0.0 (target 3.1.3) | None |
| Flask-SQLAlchemy | ORM | Yes | 3.1.1 | None |
| Flask-Login | Auth | Yes | 0.6.3 (just installed) | None |
| Flask-WTF | CSRF + forms | Yes | 1.3.0 (just installed) | None |
| Werkzeug | Password hashing | Yes | 3.0.0 (target 3.1.8) | None |
| python-dotenv | Config loading | Yes | 1.2.2 | None |
| Pillow | Image validation | Yes | 12.2.0 (target 12.3.0) | None |
| SQLite | Database | Yes | 3.43.1 (builtin) | None |
| gunicorn | Production WSGI | Not tested | latest 26.0.0 | waitress on Windows |
| waitress | Windows WSGI | Not tested | latest 3.0.2 | — |

**Missing dependencies with no fallback:**
- None for Phase 1 implementation. All packages install successfully. gunicorn/waitress only needed for Phase 4 deployment.

**Missing dependencies with fallback:**
- gunicorn not available on Windows natively → use waitress (documented in CLAUDE.md)

**Note:** The environment has Flask 3.0.0 installed but Phase 1 targets Flask 3.1.3. The planner should upgrade. All APIs used (app factory, blueprints, Flask-Login, Flask-WTF, SQLAlchemy) are stable across 3.0→3.1.

## Validation Architecture

> SKIPPED — `workflow.nyquist_validation` is set to `false` in `.planning/config.json`. No test infrastructure required for this phase.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Flask-Login `login_user`/`logout_user`; Werkzeug scrypt `generate_password_hash` |
| V3 Session Management | yes | `PERMANENT_SESSION_LIFETIME=30d`, `session.permanent=True`, `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE='Lax'` |
| V4 Access Control | yes | `@login_required` decorator on all `admin_bp` routes; `login_manager.login_view = 'auth.login'` |
| V5 Input Validation | yes | Flask-WTF `FlaskForm` + `DataRequired` validators on all form fields; `MAX_CONTENT_LENGTH=16MB` on request body |
| V6 Cryptography | yes | Werkzeug `generate_password_hash` (scrypt, N=32768, r=8, p=1); `check_password_hash` for verification |

### Known Threat Patterns for Flask + SQLite + Single Admin

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Debug mode RCE | Elevation of Privilege | `DEBUG=False` in production; never commit `debug=True`; startup check crashes if `app.debug and not localhost` |
| Session forgery (weak/missing SECRET_KEY) | Spoofing | Load `SECRET_KEY` from env; fail-fast if missing; `secrets.token_hex(32)` for generation |
| Open redirect via `next` parameter | Elevation of Privilege | Validate `next_url.startswith('/')` and reject `next_url.startswith('//')`; fall back to dashboard |
| Brute-force login | Spoofing | Not implemented in Phase 1 (single admin, low risk per D-12); defer rate-limiting to Phase 4 if internet-exposed |
| CSRF on admin forms | Tampering | Flask-WTF `CSRFProtect` initialized globally; all POST forms include `{{ form.csrf_token }}`; logout uses POST method |
| SQL injection | Tampering | SQLAlchemy ORM parameterizes all queries; no raw SQL except `PRAGMA` statements |
| Password storage in plaintext | Information Disclosure | Werkzeug scrypt hashing; never store raw password; D-01 reads from env at init time |

## Sources

### Primary (HIGH confidence)
- PyPI `flask` metadata — verified Flask 3.1.3 latest, deps `werkzeug>=3.1.0`, `jinja2>=3.1.2`, `click>=8.1.3`, `itsdangerous>=2.2.0`, `blinker>=1.9.0` [VERIFIED: pip index versions]
- PyPI `flask-sqlalchemy` metadata — verified 3.1.1 requires `sqlalchemy>=2.0.16`, `flask>=2.2.5` [VERIFIED: pip index versions]
- PyPI `flask-wtf` metadata — verified 1.3.0, requires `wtforms>=3.1.1` [VERIFIED: pip index versions]
- PyPI `flask-login` metadata — verified 0.6.3, source repo `github.com/maxcountryman/flask-login` [VERIFIED: pip index versions + pip download]
- PyPI `python-dotenv` — verified 1.2.2 [VERIFIED: pip index versions]
- PyPI `pillow` — verified 12.3.0 [VERIFIED: pip index versions]
- PyPI `werkzeug` — verified 3.1.8 [VERIFIED: pip index versions]
- Context7 `/maxcountryman/flask-login` — LoginManager setup, `login_user(remember=True)`, `user_loader`, `@login_required`, `unauthorized()` redirect behavior [VERIFIED: ctx7 docs]
- Context7 `/pallets/flask` — app factory pattern, `flask --app` discovery, blueprint `url_prefix`, CLI commands [VERIFIED: ctx7 docs]
- Context7 `/pallets-eco/flask-wtf` — `CSRFProtect`, `FlaskForm`, `validate_on_submit()`, `{{ form.csrf_token }}` [VERIFIED: ctx7 docs]
- Werkzeug 3.0.0 local installation — `generate_password_hash` confirmed uses **scrypt** by default (not MD5/SHA1) [VERIFIED: local python -c test]
- SQLAlchemy event listener for SQLite WAL mode — `PRAGMA journal_mode=WAL` + `busy_timeout=30000` [VERIFIED: local python -c test]
- SQLite 3.43.1 — WAL mode + busy_timeout confirmed working [VERIFIED: local sqlite3 test]

### Secondary (MEDIUM confidence)
- CLAUDE.md (D:\Python\storewweb\CLAUDE.md) — tech stack decisions, Windows waitress guidance, abandoned package warnings [CITED: project CLAUDE.md]
- `01-CONTEXT.md` — locked phase decisions D-01 through D-15, Claude's discretion notes [CITED: .planning/phases/01-scaffold-auth-data-model/01-CONTEXT.md]
- `.planning/REQUIREMENTS.md` — AUTH-01..04, PLAT-01..04 requirement definitions [CITED: project requirements]
- `.planning/research/SUMMARY.md` — stack recommendations, confidence assessment [CITED: project research summary]
- `.planning/research/PITFALLS.md` — 7 critical pitfalls with mitigation strategies [CITED: project pitfalls research]
- `.planning/research/STACK.md` — pinned versions, compatibility matrix [CITED: project stack research]
- `.planning/research/ARCHITECTURE.md` — app factory, blueprints, component responsibilities [CITED: project architecture research]
- `.planning/phases/01-scaffold-auth-data-model/01-UI-SPEC.md` — Vietnamese copy contract, layout, colors, interaction contracts [CITED: UI spec]

### Tertiary (LOW confidence)
- `pip show flask-login` metadata — returned empty Author/Home-page fields (PyPI metadata incomplete); cross-verified via source repo URL from pip download output and Flask-Login official docs [VERIFIED: pip download + docs]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all versions verified via `pip index versions`; slopcheck passed (without version-pinned syntax); source repos confirmed
- Architecture: HIGH — app factory + blueprint pattern verified via Context7 Flask docs; WAL mode verified locally
- Pitfalls: HIGH — verified against installed Flask 3.0.0/Werkzeug 3.0.0/SQLite 3.43.1; PITFALLS.md has local verification evidence
- Package legitimacy: HIGH — slopcheck [OK] on all 6 packages (without version syntax), cross-verified via `pip index versions` and `pip download`; source repos confirmed

**Research date:** 2026-07-31
**Valid until:** 2026-08-30 (30 days for stable Flask ecosystem; fast-moving concern is only Pillow version cadence)
