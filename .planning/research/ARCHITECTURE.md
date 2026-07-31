# Architecture Research

**Domain:** Product catalog web app (Flask, single admin, SQLite, self-hosted, Vietnamese)
**Researched:** 2026-07-31
**Confidence:** HIGH

## System Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                             Internet / Client                                │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                          Nginx (port 80/443)                          │  │
│  │  - Serves /static and /uploads directly (files, no Python overhead)   │  │
│  │  - Proxies all other requests to gunicorn via 127.0.0.1:8000          │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                    Gunicorn (WSGI server, sync workers)                │  │
│  │  - Imports `wsgi:app` entry point                                    │  │
│  │  - Runs the Flask application factory → returns app object           │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────────┤
│  │                        Flask Application (app/)                        │  │
│  │                                                                        │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────────────┐  │  │
│  │  │   public_bp     │  │   admin_bp      │  │        auth.py         │  │  │
│  │  │ (Blueprint)     │  │ (Blueprint)     │  │  Flask-Login manager   │  │  │
│  │  │                 │  │                 │  │  login/logout routes   │  │  │
│  │  │ - /              │  │ - /admin/      │  │  login_required        │  │  │
│  │  │ - /product/<id>  │  │ - /admin/products/                           │  │  │
│  │  │ - /contact       │  │ - /admin/products/new                       │  │  │
│  │  │                   │  │ - /admin/products/<id>/edit                │  │  │
│  │  └────────┬─────────┘  │ - /admin/products/<id>/delete                │  │  │
│  │           │             │                                           │  │  │
│  │           │             └────────┬─────────┘                        │  │
│  │           │                      │                                   │  │
│  │           ├──────────────────────┤                                   │  │
│  │           │                      │                                   │  │
│  │  ┌────────┴──────────────────────┴────┐   ┌──────────────────────┐ │  │
│  │  │              models.py             │   │        db.py        │ │  │
│  │  │  (SQLAlchemy models)               │   │  (db object + init)  │ │  │
│  │  │                                     │   │                      │ │  │
│  │  │  Product(id, name, price, brand,    │   │  db = SQLAlchemy()   │ │  │
│  │  │    measurements, description,       │   │  init_db command    │ │  │
│  │  │    status, stock, image_path)       │   │                     │ │  │
│  │  │  Admin(id, username, password_hash) │   │                      │ │  │
│  │  └──────────────────────────────────────┘   └──────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                       SQLite Database (data/app.db)                   │  │
│  │  Tables: products, admin_users, (schema.sql for init)                 │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │        Filesystem: app/static/uploads/ (product images)               │  │
│  │  Served by nginx at /uploads/<filename>                                │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|---------------|----------------|
| `app/__init__.py` | Application factory, extension registration, blueprint registration | `create_app(config)` function |
| `app/models.py` | SQLAlchemy models (Product, AdminUser) | Declarative model classes on shared `db` |
| `app/db.py` | Database object + CLI init command | `db = SQLAlchemy()`, `init_db` click command |
| `app/public.py` (blueprint) | Public-facing routes: catalog list, product detail, contact | `@bp.route` decorators, `render_template` |
| `app/admin.py` (blueprint) | Admin CRUD routes: product list, create, edit, delete | `@bp.route` + `@login_required` |
| `app/auth.py` (blueprint) | Login form, session management, logout | Flask-Login `login_user`/`logout_user` |
| `app/templates/` | Jinja2 templates (base + public + admin partials) | Inherited via `{% extends %}` |
| `app/static/` | CSS, JS, uploaded images | Served by Flask in dev / nginx in prod |
| `wsgi.py` | WSGI entry point for gunicorn | `from app import create_app; app = create_app()` |
| `data/app.db` | SQLite database file | Initialized via `flask init-db` |

## Recommended Project Structure

```
storewweb/
├── app/
│   ├── __init__.py          # create_app() factory, init extensions, register blueprints
│   ├── db.py                 # db = SQLAlchemy(), init_db() CLI command, schema.sql loader
│   ├── models.py             # Product, AdminUser SQLAlchemy models
│   ├── auth.py               # auth_bp: login, logout routes + Flask-Login setup
│   ├── public.py             # public_bp: / , /product/<id>, /contact
│   ├── admin.py              # admin_bp: /admin/ CRUD for products
│   ├── templates/
│   │   ├── base.html         # shared layout: navbar, flash messages, {% block content %}
│   │   ├── public/
│   │   │   ├── index.html    # product list with thumbnails
│   │   │   ├── product.html  # single product detail
│   │   │   └── contact.html  # contact + Messenger link
│   │   └── admin/
│   │       ├── login.html    # login form
│   │       ├── products.html # product list + links to create/edit
│   │       ├── product_form.html # create/edit form
│   │       └── layout.html   # minimal admin wrapper (or extend base.html)
│   └── static/
│       ├── css/style.css     # single stylesheet for public + admin
│       └── uploads/          # product images (gitignored)
├── data/
│   └── app.db               # SQLite (production), or .gitkeep
├── wsgi.py                  # gunicorn entry point: `app = create_app()`
├── requirements.txt
└── .flaskenv               # FLASK_APP=app FLASK_DEBUG=1 (dev only)
```

### Structure Rationale

- **`app/` package with factory pattern** — Required because the user self-hosts with gunicorn (needs `wsgi:app` importable). The factory pattern (`create_app()`) lets you load config from environment variables or instance files without circular imports. This is the official Flask-recommended structure for any app deployed beyond `flask run` in development.
- **Blueprints split public vs admin vs auth** — Even with ~8 screens, blueprints keep route definitions in focused files. Public routes get no auth; admin routes get `@login_required`; auth routes handle session lifecycle. Each blueprint's routes live in one file (~150-200 lines max).
- **No Flask-Admin** — The admin interface is only ~5 screens (login, product list, create, edit, delete) and the user wants simple CRUD with a single admin account. Flask-Admin adds a heavy dependency, a full Bootstrap theme, and a non-Vietnamese-first admin UI. Custom blueprints with hand-written forms are ~200 fewer lines of dependency and give full control over the Vietnamese labels.
- **Templates in subfolders matching blueprints** — `templates/public/`, `templates/admin/` keeps them organized. A single `base.html` at the root provides the shared layout.
- **`data/` folder for SQLite** — Separates the database file from source code, makes backup/cleaner gitignore trivial.

## Architectural Patterns

### Pattern 1: Application Factory (Flask standard)

**What:** A `create_app(config_name)` function in `app/__init__.py` that creates the Flask instance, loads config, initializes extensions, registers blueprints, and returns the app.

**When to use:** Always for self-hosted deployment (gunicorn/uwsgi import the app object). Standard Flask pattern since 2.0.

**Trade-offs:** Slight indirection vs single-file `app = Flask(__name__)`, but zero downside for any deployment beyond `flask run`.

**Example:**
```python
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-insecure-change-me'),
        SQLALCHEMY_DATABASE_URI='sqlite:///app.db',
        UPLOAD_FOLDER='app/static/uploads',
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB upload cap
    )
    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    return app
```

### Pattern 2: Blueprint-based route isolation

**What:** Each functional area (public catalog, admin CRUD, auth) is a `Blueprint` registered in the factory. Routes are defined with `@bp.route(...)` inside each blueprint module.

**When to use:** Any Flask app with more than 3 routes. Even for ~8 screens, blueprints prevent a 300-line `app.py`.

**Trade-offs:** One extra layer (`.py` file per blueprint), but route logic stays isolated and testable.

**Example:**
```python
from flask import Blueprint, render_template
from .models import Product

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/products')
@login_required
def product_list():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)
```

### Pattern 3: SQLAlchemy models with Flask-Login UserMixin

**What:** Database models are plain SQLAlchemy declarative classes. The admin user model inherits `UserMixin` from Flask-Login to satisfy `is_authenticated`, `is_active`, `get_id`.

**When to use:** Always for session-based auth in Flask. Flask-Login is the de-facto standard.

**Trade-offs:** Adds one dependency, but provides `login_required`, session management, and `current_user` for free.

**Example:**
```python
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))
```

### Pattern 4: Filesystem image storage with path in DB

**What:** Uploaded product images are saved to `app/static/uploads/` with `werkzeug.utils.secure_filename`. The `image_path` column on `Product` stores the filename (e.g. `abc123.jpg`). Public templates render `<img src="/static/uploads/{{ product.image_path }}">`.

**When to use:** Always for self-hosted apps without a blob store. Filesystem is simpler than blob storage and works with nginx static serving.

**Trade-offs:** File lifecycle (deletion on product removal) must be handled manually. Scaling to multiple servers requires shared storage, but that is not a concern here.

**Example:**
```python
import os, uuid
from werkzeug.utils import secure_filename

def save_product_image(file):
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in {'png', 'jpg', 'jpeg', 'gif'}:
        raise ValueError('Invalid file type')
    filename = f'{uuid.uuid4().hex}.{ext}'
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return filename
```

## Data Flow

### Public Catalog Request Flow

```
Browser → nginx (static) or Flask (dynamic) → public_bp route → models.py query → templates/public/*.html → Browser
```

1. User navigates to `/`
2. Nginx proxies to gunicorn → `public_bp.index()`
3. Route calls `Product.query.filter_by(status='available').all()`
4. `index.html` template loops over products, renders `<img src="/static/uploads/{{ p.image_path }}">`
5. Browser requests image file directly from nginx (no Python overhead)

### Admin CRUD Flow

```
Browser → nginx → gunicorn → admin_bp route → models.py → db.session commit → SQLite → redirect → public_bp route → template → Browser
```

1. Admin logs in via `auth_bp.login()` → Flask-Login `login_user()` → session cookie set
2. Admin navigates to `/admin/products` → `admin_bp.product_list()` → `@login_required` check → `Product.query.all()` → `products.html` renders
3. Admin clicks "Edit" → `admin_bp.product_edit(id)` → form pre-filled → POST updates `Product` via `db.session.commit()`
4. Image upload: `request.files['image']` → `save_product_image()` → filename stored in `product.image_path` → `db.session.commit()`
5. After save → redirect to `/admin/products` → list shows updated row

### Authentication Flow

```
Browser → nginx → gunicorn → auth_bp.login() → Flask-Login → session cookie → Browser (cookie on all subsequent requests)
```

1. POST `/login` with username/password → `check_password_hash` → `login_user(admin)` → Flask-Login sets `session["_user_id"]` (signed cookie)
2. Browser sends cookie on next request → Flask-Login `user_loader` callback → `load_user(user_id)` → `AdminUser.query.get(id)` → `current_user` populated
3. `@login_required` decorator checks `current_user.is_authenticated`; if False, redirects to `login_manager.login_view`
4. Logout → `logout_user()` → session cleared

### Key Data Flows

1. **Product image upload:** Browser POST → nginx → Flask `request.files` → `secure_filename` + `uuid` → `file.save()` to filesystem → filename stored in `product.image_path` → SQLite commit → redirect.
2. **Product creation/edit:** Form POST → `admin_bp` route → `form.populate_obj(product)` or manual field assignment → `db.session.add()` + `commit()` → redirect to list.
3. **Public rendering:** `Product.query` → Jinja2 `for product in products` → `<img src="/static/uploads/..." >` → browser fetches image from nginx.

## Component Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `public_bp` ↔ `models.py` | Direct import (`from .models import Product`) | Public routes read products only; no writes. |
| `admin_bp` ↔ `models.py` | Direct import (`from .models import Product`) | Admin routes do full CRUD; `@login_required` enforced per route. |
| `auth.py` ↔ `models.py` | Direct import (`from .models import AdminUser`) | Auth loads user via `user_loader` callback using the model. |
| `admin_bp` ↔ `auth` | Flask-Login `login_required` decorator + `current_user` | Admin blueprint does not import auth routes; relies on decorator + session cookie. |
| Flask app ↔ SQLite | SQLAlchemy ORM | All DB access goes through `db.session`; no raw SQL except `init_db` schema loading. |
| Flask app ↔ filesystem | `file.save()` / `os.path` | Image uploads go to `UPLOAD_FOLDER`; deletions require manual `os.remove()`. |
| Nginx ↔ Flask | HTTP reverse proxy | Nginx forwards all non-static requests to gunicorn at `127.0.0.1:8000`. |
| Nginx ↔ filesystem | Direct file serving | `/static/` and `/uploads/` served by nginx, bypassing Python entirely. |

## Build Order (Dependencies)

The following sequence minimizes blocking and ensures each phase builds on verified foundations:

```
1. Project skeleton → 2. DB + models → 3. Auth → 4. Admin CRUD → 5. Public catalog → 6. Image upload → 7. Styling → 8. Deployment
```

| Step | Component | Depends On | Output |
|------|-----------|-----------|--------|
| 1 | `app/__init__.py`, `requirements.txt`, `wsgi.py` | Flask installed | `create_app()` returns empty Flask app, server starts |
| 2 | `models.py`, `db.py` + `schema.sql` | Step 1 | `flask init-db` creates SQLite tables; `db` object importable |
| 3 | `auth.py` (login route, `login_manager`, `user_loader`) | Steps 1-2 | Single admin can log in via Flask-Login session |
| 4 | `admin.py` (product list/edit/delete) | Steps 1-3 | Admin sees empty product list, can navigate but CRUD needs models wired |
| 5 | `public.py` (catalog list, product detail, contact) | Steps 1-4 | Public sees product list (empty initially) |
| 6 | Image upload field in admin form | Steps 2-5 | Admin can upload product image → saved to filesystem → displayed in catalog |
| 7 | Templates + CSS (Vietnamese labels, responsive layout) | Steps 1-6 | Full UI polished; all screens styled |
| 8 | Nginx config + gunicorn setup | Steps 1-7 | Production-ready self-hosted deployment |

**Rationale:** DB and models must exist before any CRUD. Auth must exist before admin routes can be protected. Public catalog can be built in parallel with admin CRUD since they both only depend on models existing — but admin CRUD is the "data entry" path, so it should come first to unblock seeding real data. Image upload is a refinement of the admin create/edit flow, so it comes after basic CRUD works. Deployment is last since it's config, not code.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-100 products | Current architecture is optimal. SQLite handles low concurrency fine. Single admin means no auth contention. |
| 100-1000 products | Add product search via `ilike` queries. Consider paginating the product list (Flask-SQLAlchemy `paginate`). Add `created_at` and `updated_at` columns for sort/filter. |
| 1000+ products | Migrate to PostgreSQL. Add full-text search or SQLite FTS. Consider caching product list pages. Add product categories/tags. |
| 10k+ daily visitors | Deploy with more gunicorn workers. Add Redis cache layer for product list. Offload image serving to CDN. Consider read replicas for SQLite→PostgreSQL migration. |

### Scaling Priorities

1. **First bottleneck:** Product list query grows linearly — paginate at 50-100 items. Use `paginate(page, per_page=50)`.
2. **Second bottleneck:** Image storage grows — move uploads to a dedicated directory outside the app repo, or to S3-compatible storage if budget allows.

## Anti-Patterns

### Anti-Pattern 1: Single-file app.py with everything inline

**What people do:** Put all routes, models, and config in one `app.py` because the tutorial shows `flask run` works.

**Why it's wrong:** Breaks gunicorn deployment (needs `wsgi:app`), config can't be environment-driven, no separation of public/admin/auth concerns, impossible to test individual components without the full app context.

**Do this instead:** Use the app factory pattern with `app/__init__.py` and blueprints. The extra files cost zero runtime overhead and prevent a painful refactor later.

### Anti-Pattern 2: Storing images in SQLite as BLOB

**What people do:** `db.Column(LargeBinary)` for product images, base64-decode in templates.

**Why it's wrong:** SQLite bloats to 3x file size for BLOBs. Backups become huge. Nginx can't serve images without Python round-trips. No browser caching.

**Do this instead:** Filesystem storage with `secure_filename` + UUID. Nginx serves images directly. One column (`image_path`) stores the filename.

### Anti-Pattern 3: Custom auth instead of Flask-Login

**What people do:** Hand-roll session management with `session['user_id']` and a custom decorator.

**Why it's wrong:** Miss edge cases (session fixation, freshness, remember-me). Flask-Login's `user_loader`, `login_required`, and `current_user` solve this in 10 lines of setup.

**Do this instead:** `flask_login.LoginManager`, `UserMixin` on the model, `@login_required` on admin routes, `@login_manager.user_loader` callback.

### Anti-Pattern 4: Raw SQL strings instead of SQLAlchemy ORM

**What people do:** `db.execute('SELECT * FROM products WHERE id = ?', (id,))` with manual row-to-dict conversion.

**Why it's wrong:** More code, no model reuse, harder to test, must handle connection lifecycle manually. ORM handles session management, lazy/eager loading, and gives you objects with methods.

**Do this instead:** SQLAlchemy models. `Product.query.get(id)` returns an object or None. `product.name`, `product.price` work naturally in templates.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Nginx | Reverse proxy + static file serving | Configure `proxy_pass http://127.0.0.1:8000`; serve `/static/uploads/` directly. |
| Gunicorn | WSGI server running `wsgi:app` | Install `gunicorn` in requirements; run `gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app`. |
| Filesystem | `app/static/uploads/` directory | Add to `.gitignore`; create at deploy time with correct permissions. |
| SQLite | SQLAlchemy `sqlite:///app.db` | No external service; file-based; backup via `cp data/app.db`. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `app/__init__.py` ↔ `db.py` | `db.init_app(app)` | Factory calls init for each extension. |
| `app/__init__.py` ↔ blueprints | `app.register_blueprint(bp)` | One line per blueprint; order doesn't matter for Flask. |
| `app/__init__.py` ↔ `auth.py` | `login_manager.init_app(app)` | Flask-Login manager initialized in factory, routes defined in blueprint. |
| `auth.py` ↔ `models.py` | `from .models import AdminUser` | User loader callback references the model. |
| `public_bp` ↔ `admin_bp` | None (shared templates only) | No cross-imports. Admin and public are fully isolated. |
| Templates ↔ `static/` | `url_for('static', filename=...)` | Jinja `url_for` generates correct paths; works in dev and prod. |

## Sources

- Flask Application Factory pattern: https://flask.palletsprojects.com/en/stable/patterns/appfactories/
- Flask Blueprints documentation: https://flask.palletsprojects.com/en/stable/blueprints/
- Flask-Login documentation: https://flask-login.readthedocs.io/en/latest/
- Flask-Admin (not recommended for this use case): https://flask-admin.readthedocs.io/en/latest/
- Flask File Uploads: https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
- Flask SQLite3 pattern: https://flask.palletsprojects.com/en/stable/patterns/sqlite3/
- Flask-Nginx deployment: https://flask.palletsprojects.com/en/stable/deploying/nginx/
- Flask-Gunicorn deployment: https://flask.palletsprojects.com/en/stable/deploying/gunicorn/
- Context7 documentation: Flask (/pallets/flask), Flask-Login (/maxcountryman/flask-login), Flask-Admin (/pallets-eco/flask-admin)

---
*Architecture research for: Flask product catalog web app (self-hosted, single admin, SQLite, Vietnamese)*
*Researched: 2026-07-31*
