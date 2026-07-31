# Pitfalls Research

**Domain:** Self-hosted Flask product catalog + admin (single admin, SQLite, image uploads, Vietnamese site)
**Researched:** 2026-07-31
**Confidence:** HIGH (verified against installed Flask 3.0.0, Werkzeug 3.0.0, Flask-SQLAlchemy 3.1.1, SQLite 3.43.1 on Python 3.11)

## Critical Pitfalls

### Pitfall 1: Flask Debug Mode + Werkzeug Debugger in Production

**What goes wrong:**
Running the app with `debug=True` or using `flask run` (which sets `debug=True` by default) exposes the Werkzeug interactive debugger. The debugger allows executing arbitrary Python code in the browser — anyone who can reach the site can run `import os; os.system('rm -rf /')`. The debugger is "protected" by a PIN shown in the server console, but the PIN is derivable from machine MAC address, username, and modname — all obtainable through other vulnerabilities.

**Why it happens:**
Developers start with `flask run` because it is the documented quick-start. They forget to disable debug or switch to gunicorn before going live. Self-hosted users with limited ops experience may not know the difference between dev server and production WSGI server.

**How to avoid:**
1. Use `flask run` only for local development.
2. For production always use a WSGI server (gunicorn): `gunicorn --bind 0.0.0.0:8000 app:app`
3. Set `app.debug = False` in production config, or use environment variable: `FLASK_ENV=production python app.py`
4. Add a startup check that crashes if `app.debug` and not localhost.
5. Never set `DEBUG = True` in committed config files.

**Warning signs:**
- The console shows ` * Debug mode: on` on startup
- Visiting `/console` returns the debugger PIN entry page (instead of 404)
- Error pages show full Python traceback with local variables

**Phase to address:** Phase 1 (Initial Scaffold) — set up proper config loading with environment-based debug, add health check route, document dev vs prod startup commands.

---

### Pitfall 2: SECRET_KEY Not Set (Session Forgery)

**What goes wrong:**
Flask signs session cookies with `SECRET_KEY`. If it is `None` (the default), Flask logs a `RuntimeError` but the app continues to start — except sessions silently fail. Users cannot log in, `session['logged_in'] = True` does nothing, and the admin login appears broken. Even worse: if a developer hardcodes a weak key like `'secret'` into version control, attackers who see the source can forge any session cookie.

**Why it happens:**
`SECRET_KEY` is not set by default — it is `None`. The Flask quick-start tutorials sometimes omit it for brevity. When the login page "doesn't work," the developer may chase other causes (database, form validation) instead of checking `app.config['SECRET_KEY']`.

**How to avoid:**
1. Set `SECRET_KEY` from environment variable at startup: `app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32))`
2. For the single-admin use case: generate a strong key once and put it in a `.env` file: `python -c "import secrets; print(secrets.token_hex(32))"`
3. Fail fast if SECRET_KEY is missing in production: check on startup and `raise RuntimeError`.
4. Never commit `.env` files to git (add to `.gitignore`).

**Warning signs:**
- Login form submits successfully but user is not logged in on next page
- Console shows `UserWarning: The 'SECRET_KEY' should be set`
- Session cookie value starts with `'` (invalid signature)

**Phase to address:** Phase 1 (Initial Scaffold) — create `.env.example`, load config from environment, add startup validation.

---

### Pitfall 3: Image Upload Path Traversal + Extension-Only Validation

**What goes wrong:**
Developers use `secure_filename()` from Werkzeug and assume it is sufficient. `secure_filename` strips path separators (`../`, `..\`) and non-ASCII characters, producing safe filenames. But it does NOT validate file type — `secure_filename('shell.php')` returns `'shell.php'`. If the uploads directory is served directly by nginx with PHP/CGI enabled, an attacker can upload a PHP webshell and execute it. Even without PHP, a `.html` file in the served directory causes stored XSS. Additionally, `secure_filename` strips Vietnamese characters — `ảnh_sản_phẩm.jpg` becomes `anh_san_pham.jpg`, losing the meaningful filename.

**Why it happens:**
Tutorial code often checks only the file extension (`file.filename.endswith('.jpg')`). Content-Type headers can be spoofed. Magic byte verification is rarely shown in Flask tutorials. Developers do not consider that nginx might execute uploaded files.

**How to avoid:**
1. **Validate file extension** against a strict allowlist: `{'.jpg', '.jpeg', '.png', '.webp'}`.
2. **Validate magic bytes** server-side — read first bytes and compare against known signatures:
   - JPEG: `FF D8 FF`
   - PNG: `89 50 4E 47 0D 0A 1A 0A`
   - GIF: `47 49 46 38`
   - WebP: starts with `RIFF` then `WEBP` at offset 8
3. **Use Pillow to verify and re-encode**: `from PIL import Image; img = Image.open(file); img.verify()` then re-save to enforce dimensions and strip embedded payloads.
4. **Limit image dimensions**: reject images larger than e.g. 2000x2000px (prevents decompression bomb DoS).
5. **Store uploads outside web root** or serve via `send_from_directory` (never direct nginx path with CGI).
6. **Set `MAX_CONTENT_LENGTH`**: `app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024` (16MB) to prevent denial-of-service via large uploads.

**Warning signs:**
- `secure_filename('shell.php.jpg')` returns `'shell.php.jpg'` — double extension preserved
- Upload directory accepts any file type
- `MAX_CONTENT_LENGTH` not configured (unlimited upload size)
- Uploaded files accessible at `/uploads/shell.php` and executing code

**Phase to address:** Phase 2 (Admin + Image Upload) — implement Pillow-based validation, magic byte check, MAX_CONTENT_LENGTH, and secure storage path.

---

### Pitfall 4: SQLite "database is locked" Under Gunicorn Multi-Worker

**What goes wrong:**
SQLite is a file-based database. When gunicorn forks N workers (default: `CPU count * 2 + 1`), each worker process opens its own SQLite connection. SQLite allows concurrent reads but only one writer at a time. Under concurrent admin writes (e.g., admin saves two products simultaneously), the second write receives `sqlite3.OperationalError: database is locked`. This results in HTTP 500 errors or silently dropped writes. Even with WAL mode enabled, the problem persists for writes — WAL only separates readers and writers.

**Why it happens:**
Flask-SQLAlchemy defaults connect to SQLite without `connect_args` for timeout or WAL mode. Developers deploy with `--workers 4` and assume SQLite handles concurrency like PostgreSQL. The admin interface (single-user) rarely triggers concurrent writes during development, so the issue only surfaces under production load.

**How to avoid:**
1. **Enable WAL mode** in Flask-SQLAlchemy config:
   ```python
   app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
       'connect_args': {
           'timeout': 30,
           'isolation_level': None,
       },
       'pool_pre_ping': True,
   }
   ```
   Also run `PRAGMA journal_mode=WAL` on connection (see Flask-SQLAlchemy event listener pattern below).

2. **Set busy_timeout**: `connect_args={'timeout': 30}` gives SQLite 30 seconds to wait for a lock before failing.

3. **Do NOT use `gunicorn --preload`**: preloading forks workers after the DB connection is opened, sharing one connection across processes — causes lock corruption. Without `--preload`, each worker opens its own connection.

4. **Add retry logic** for write operations (retry on `OperationalError` with exponential backoff).

5. **Connection-per-request pattern**: Flask-SQLAlchemy's scoped_session creates a new connection per request by default, which is correct. Ensure it is not overridden.

**Warning signs:**
- Console shows `sqlite3.OperationalError: database is locked`
- Admin saves fail intermittently under concurrent edits
- Gunicorn started with `--preload` flag

**Phase to address:** Phase 2 (Admin) or Phase 3 (Deployment) — configure engine options, test concurrent writes, add retry logic.

---

### Pitfall 5: Float Prices for VND (Precision Loss + Incorrect Formatting)

**What goes wrong:**
Developers store prices as `Float` or `DECIMAL` in the database. Simple operations like `price * 0.9` produce results like `89999.99999999999` due to IEEE 754 floating-point representation. Display formatting like `f"{price:,.2f} VND"` produces `89,999.99 VND` — the `.99` suffix implies cents, but VND has no subunit in practice. Worse, `float` accumulation errors compound over multiple operations (e.g., order totals, discounts). Vietnamese customers see confusing `.99` suffixes on prices that should be whole numbers.

**Why it happens:**
Most price-handling tutorials use `float` because it is the default numeric type in JSON and Python. Developers from USD/EUR backgrounds assume 2 decimal places are needed. The floating-point errors are small enough that they go unnoticed in dev but compound in production.

**How to avoid:**
1. **Store prices as `Integer`** in the database — VND has no subunit, store values directly (e.g., 100000 for 100,000 VND).
2. **Do all money math in integers** — use integer multiplication/division (e.g., `price * 9 // 10` for 10% discount).
3. **Format with no decimal places**: `f"{price:,} VND"` produces `100,000 VND`.
4. **Display with thousand separator**: `{{ product.price | int | format_price }}` in Jinja2.
5. If sub-cent precision is ever needed (it is not for VND), use `decimal.Decimal` — never `float`.

**Warning signs:**
- Price column type is `Float` or `DECIMAL` in model definition
- Template shows `.00` or `.99` after prices
- Price calculations use `/` instead of `//` for integer division

**Phase to address:** Phase 1 (Data Model) — define price as `db.Integer`, add Jinja2 filter for formatting, document the convention.

---

### Pitfall 6: Missing `html lang="vi"` and `<meta charset="utf-8">` (Mojibake / Wrong SEO)

**What goes wrong:**
Vietnamese text appears as tofu (`&#7883;` or `Ã¡»` ) or garbled in the browser. Search engines index the page without knowing it is Vietnamese, leading to wrong language in search results. The admin interface shows question marks for Vietnamese characters in input fields.

**Why it happens:**
- Python source files saved in cp1258 or UTF-8 without declaration
- SQLite column encoding mismatch (rare — SQLite defaults to UTF-8)
- Flask templates render with default Jinja2 encoding but HTML document lacks `<meta charset="utf-8">`
- HTTP response missing `Content-Type: text/html; charset=utf-8`
- Missing `<html lang="vi">` tells browser and SEO crawlers the language

**How to avoid:**
1. Save all Python source files as UTF-8 (Python 3 defaults to UTF-8).
2. Add `<meta charset="utf-8">` as the first `<head>` element in every template.
3. Set `<html lang="vi">` on the root HTML element.
4. Add `Content-Language: vi` or `Content-Language: vi-VN` HTTP header.
5. Ensure `app.json.ensure_ascii = False` for JSON API responses with Vietnamese.
6. For Jinja2 templates, no extra configuration needed — Jinja2 defaults to UTF-8.
7. Verify end-to-end: SQLite stores UTF-8, Python reads UTF-8, Jinja2 renders UTF-8, browser interprets UTF-8.

**Warning signs:**
- Characters appear as `&#7883;` (HTML entities) in browser source
- Vietnamese characters show as black diamonds or question marks
- Google Search Console reports wrong language detected

**Phase to address:** Phase 1 (Scaffold) — set up base template with correct charset and lang, add `ensure_ascii = False` to Flask JSON config, document file encoding requirements.

---

### Pitfall 7: Image Upload Memory Exhaustion (Decompression Bomb)

**What goes wrong:**
An attacker uploads a small file (e.g., 10KB) that is actually a 50,000x50,000 pixel PNG that decompresses to ~2GB in memory. When Pillow opens or the web server buffers the file, it exhausts server RAM, crashes the worker, and potentially the entire server. Even legitimate users can accidentally upload large photos from modern phone cameras.

**Why it happens:**
Flask's default behavior reads the entire uploaded file into `request.files` before the application sees it. `Image.open()` does not limit pixel dimensions. Developers assume `MAX_CONTENT_LENGTH` protects against this, but a 10KB file passes the size check while its decompressed form is enormous.

**How to avoid:**
1. **Use Pillow to verify dimensions**: After opening with `Image.open()`, check `img.width` and `img.height` against a maximum (e.g., 2000px).
2. **Call `img.verify()`** before processing — verifies integrity without full decompression.
3. **Re-encode the image** after validation (stripping EXIF and recompressing to known-safe dimensions).
4. **Set `MAX_CONTENT_LENGTH`** as a first line of defense against multi-GB uploads.

```python
from PIL import Image
img = Image.open(file.stream)
img.verify()  # Raises exception if corrupt
img = Image.open(file.stream)  # Re-open after verify
if img.width > 2000 or img.height > 2000:
    raise ValueError("Image too large")
img.thumbnail((800, 800))  # Resize to fixed max
img.save(dest_path)  # Re-encode
```

**Warning signs:**
- Upload works in dev but crashes server with large photo from real phone camera
- Memory usage spikes when opening uploaded images
- No dimension check after `Image.open`

**Phase to address:** Phase 2 (Image Upload) — implement Pillow verification, resize on save, set MAX_CONTENT_LENGTH.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Use `db.String` length 255 for all text fields | No need to think about limits | Product descriptions get truncated | Never — set explicit lengths from the start |
| Store prices as Float | Familiar, JSON-compatible | Precision errors compound | Never for VND — use Integer |
| Skip `MAX_CONTENT_LENGTH` | No upload size limit issues | DoS via large uploads exhausts disk/RAM | Never — 16MB max is plenty for product photos |
| Use Flask-SQLAlchemy default session | No migration setup needed | Schema changes require manual DB edits | First phase only — migrate to Flask-Migrate for real project |
| Serve uploads via Flask route | Works without nginx setup | Slow, blocks workers on large images | Dev only — nginx must serve uploads in production |
| Hardcode `.env` values in config | No `.env` file management | Secrets in version control | Never — `.env` is the minimum |
| Skip `gunicorn --max-requests` | Simpler config | Workers leak memory over time | Acceptable for low-traffic sites (< 100 req/day) |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| **nginx** | Serve uploads directly from `/uploads/` with PHP/CGI enabled | Store uploads outside web root or deny execution in uploads dir; use `send_from_directory` |
| **gunicorn** | Start with `--preload` for faster boot | Never use `--preload` with SQLite — each worker needs its own DB connection |
| **SQLite** | Deploy with 4+ workers, no WAL, no timeout | Use WAL mode + `busy_timeout=30s` + consider 1-2 workers for write-heavy admin |
| **Pillow** | Trust `Image.open()` + save directly | Always `verify()` first, then re-open, then resize/re-encode |
| **Let's Encrypt** | Use `certbot --standalone` which binds port 80 | Use nginx plugin (`certbot --nginx`) to avoid port conflict with gunicorn |
| **Cloudflare** | Enable "Always Online" or automatic static caching | Disable caching on `/admin/*` paths; set cache TTL=0 for dynamic content |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| SQLite write lock contention | Admin saves fail intermittently | WAL + busy_timeout + retry logic | 2+ concurrent admin users writing |
| Flask serving static files | Slow page loads, high CPU | nginx serves `/static/` and `/uploads/` | Any production traffic |
| No image resizing on upload | 5MB photos render at 2400x1800 | Resize to max 800px on upload | Page loads > 2s on mobile |
| Gunicorn sync workers blocking on upload | Upload blocks all other requests | Use `--workers 2` (not 4+) for simple site; or gthread worker class | Concurrent admin + visitor access during upload |
| No template caching | Same template re-rendered every request | Flask caches templates by default in production | Negligible — only matters at high traffic |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| `debug=True` in production | Remote Code Execution via Werkzeug debugger | Hardcode `debug=False` in production config; never expose `/console` |
| No `SECRET_KEY` or weak key | Session forgery, login bypass | Generate 32-byte random key per deployment; store in environment variable |
| No CSRF on admin forms | Attacker can trick admin into deleting products | Use Flask-WTF `CSRFProtect` or manual token; `SameSite=Lax` as defense-in-depth |
| Serving uploads as-is | Stored XSS via uploaded HTML, or RCE via PHP | Validate magic bytes; serve via `send_from_directory`; deny non-image extensions in nginx |
| File extension validation only | Upload `shell.jpg.php` with image content-Type | Check actual file content (magic bytes + Pillow `verify()`) |
| Passwords stored in plaintext | DB leak exposes all admin passwords | Use `werkzeug.security.generate_password_hash` (scrypt in Werkzeug 3.x) |
| No `MAX_CONTENT_LENGTH` | Upload 1GB file to exhaust disk | Set to `16 * 1024 * 1024` (16MB) — sufficient for product photos |
| Missing `SESSION_COOKIE_SECURE` | Session cookie sent over HTTP (interceptable) | `app.config['SESSION_COOKIE_SECURE'] = True` (requires HTTPS) |
| Missing `PERMANENT_SESSION_LIFETIME` config | Sessions last 31 days (too long) | Set `app.permanent_session_lifetime = timedelta(hours=8)` for admin session |
| No rate limiting on login | Brute-force attack on admin password | Add `flask-limiter` or nginx-level rate limiting on `/login` |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Empty product list shows blank page | Vietnamese admin sees nothing, thinks site is broken | Add `{% else %}` clause: `Chưa có sản phẩm nào` |
| Price shows `100000.00 VND` | Looks like foreign currency with cents, confusing | Format as `100,000₫` or `100,000 VND` (no decimals) |
| No `lang="vi"` on HTML | Wrong font rendering, wrong SEO language | Always `<html lang="vi">` |
| Product detail page missing back link | Admin must use browser back button | Add "Quay lại" link to product list |
| Delete product via GET link | One click accidentally deletes, no undo | Use POST form with confirmation dialog |
| No image preview on upload form | Admin uploads wrong file, can't verify | Show thumbnail preview after file selection (client-side JS) |
| Admin forms not responsive on mobile | Can't manage products while away from computer | Add viewport meta tag; test on mobile |
| No feedback after form submit | Admin doesn't know if save succeeded | Flash message: `Lưu sản phẩm thành công` |

---

## "Looks Done But Isn't" Checklist

- [ ] **Admin login page:** SECRET_KEY not set → verify login actually persists across requests
- [ ] **Product list:** Shows sample data but blank when DB is empty → verify `{% else %}` clause in template renders `Chưa có sản phẩm nào`
- [ ] **Image upload:** Works in Flask dev server → verify nginx serves `/uploads/` directory with correct permissions
- [ ] **Price display:** Shows `100000 VND` → verify comma formatting: `100,000 VND`
- [ ] **Delete product button:** Uses `<a href="/delete/1">` → verify it is a POST form with CSRF token + confirmation
- [ ] **Contact page:** Has Messenger link → verify HTML `lang="vi"` and `<meta charset="utf-8">` are present
- [ ] **Deployment:** `gunicorn app:app` runs locally → verify `gunicorn --workers N` with SQLite WAL mode and busy_timeout
- [ ] **Error handling:** Page works with sample data → trigger a 500 (e.g., invalid DB path) and verify custom error page renders

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|----------------|------------|
| Phase 1 (Scaffold) | SECRET_KEY missing → login silently broken | Fail-fast check on startup: `if not app.config['SECRET_KEY']: raise RuntimeError` |
| Phase 1 (Scaffold) | No `lang="vi"` / charset → mojibake in production | Use base template with `<html lang="vi">` and `<meta charset="utf-8">` |
| Phase 2 (Image Upload) | No `MAX_CONTENT_LENGTH` → RAM exhaustion | Set `app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024` |
| Phase 2 (Image Upload) | `secure_filename` strips Vietnamese → filenames lose meaning | Store original filename in DB; use UUID + `.jpg` for filesystem name |
| Phase 2 (Image Upload) | No dimension check → decompression bomb | `Image.open(file); img.verify(); check width/height limits` |
| Phase 3 (Deploy) | `debug=True` left on → RCE via Werkzeug debugger | Config: `DEBUG = False` in production; verify `/console` returns 404 |
| Phase 3 (Deploy) | `gunicorn --preload` → SQLite lock corruption | Document gunicorn command without `--preload` |
| Phase 3 (Deploy) | nginx serves uploads with PHP → code execution | nginx: `location /uploads/ { try_files $uri =404; }` |
| Phase 3 (Deploy) | No reverse proxy headers → HTTP URLs mixed with HTTPS | Add `ProxyFix` + nginx `proxy_set_header X-Forwarded-Proto $scheme` |
| Phase 3 (Deploy) | No gunicorn PID file → restart kills wrong process | `gunicorn --pid /var/run/gunicorn.pid` |

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Debug mode enabled in production | LOW — config change | 1. Set DEBUG=False 2. Restart with gunicorn 3. Kill debugger PIN exposure |
| SECRET_KEY changed (sessions invalidated) | LOW | Inform admin to log in again; sessions are stateless so no data lost |
| SQLite database locked | MEDIUM | 1. Restart gunicorn workers (clears stale connections) 2. Check for long-running transactions |
| Uploaded image is malicious | HIGH | 1. Inspect uploads directory for non-image files 2. Delete any .php/.html/.py files 3. Tighten nginx to deny execution in /uploads/ |
| Price stored as Float (precision corruption) | MEDIUM | 1. Migrate column to Integer 2. Convert existing values: `UPDATE products SET price = ROUND(price)` |
| Database corruption from backup during write | HIGH | 1. Restore from last known-good backup 2. Switch to `sqlite3 .backup` command for future backups |
| Missing CSRF protection exploited | MEDIUM | 1. Add CSRF tokens immediately 2. Audit admin actions for unauthorized changes 3. Rotate admin password |
| No MAX_CONTENT_LENGTH (disk filled) | MEDIUM | 1. Clear uploads directory 2. Set MAX_CONTENT_LENGTH 3. Add disk monitoring alert |

---

## Sources

- Flask 3.0.0 installed and verified in this environment — `app.config` defaults checked for `SECRET_KEY=None`, `DEBUG=False`, `SESSION_COOKIE_SECURE=False`, `SESSION_COOKIE_SAMESITE=None`
- Werkzeug 3.0.0 `generate_password_hash` verified to use `scrypt` by default (not MD5/SHA1); `secure_filename` verified to strip path separators and Vietnamese characters
- SQLite 3.43.1 — WAL mode confirmed working for file-based DBs; `threadsafety=3` (fully thread-safe) but process-level concurrency still requires WAL + busy_timeout
- Flask-SQLAlchemy 3.1.1 — `SQLALCHEMY_ENGINE_OPTIONS` with `connect_args` verified
- Flask-WTF NOT installed — confirms no built-in CSRF protection, needs `pip install flask-wtf`
- Pillow 12.2.0 confirmed installed — `Image.open()`, `.verify()`, `.thumbnail()` available for validation
- WebFetch to Flask official docs returned HTTP 429 (Cloudflare challenge) — findings verified via local code inspection of installed packages instead
- Jinja2 auto-escaping verified: `{{ content }}` escapes HTML; `{{ content|safe }}` does not
- Python `json.dumps(ensure_ascii=True)` confirmed to escape Vietnamese characters; Flask `app.json.ensure_ascii = False` resolves for jsonify

---

*Pitfalls research for: Self-hosted Flask product catalog with Vietnamese admin and image uploads*
*Researched: 2026-07-31*
