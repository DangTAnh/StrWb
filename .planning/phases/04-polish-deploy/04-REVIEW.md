---
phase: 04-polish-deploy
reviewed: 2026-08-02T01:13:09+07:00
depth: standard
files_reviewed: 10
files_reviewed_list:
  - app/public.py
  - app/static/css/style.css
  - app/templates/public/product_detail.html
  - requirements.txt
  - .env.example
  - docs/deploy/Windows.md
  - docs/deploy/Linux.md
  - docs/deploy/nginx.conf
  - docs/deploy/storeweb.service
  - docs/deploy/README.md
findings:
  critical: 1
  warning: 4
  info: 2
  total: 7
status: issues_found
---

# Phase 4: Code Review Report

**Reviewed:** 2026-08-02T01:13:09+07:00
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Phase 4 (Polish + Deploy) reviewed: the D-07 UI deferral fixes (`public.py` search
out-of-range redirect, `style.css` out-of-stock-note contrast, `product_detail.html`
full-size gallery main image), the waitress/Windows + gunicorn/systemd/nginx Linux
deploy docs, nginx template, systemd unit, `.env.example`, and `requirements.txt`.

The application-code changes are correct and clean:
- `public.py` search redirect handles all edge cases (page=0, negative, huge, total=0)
  correctly and mirrors `home()`; the redirect preserves the `q` query string.
- `product_detail.html` full-size image change is safe (filename is server-generated
  UUID + `.jpg` from `image_utils.py`; no path-traversal surface) and consistent with
  the thumb swap logic.
- `style.css` `#B91C1C` is an isolated token change (6.19:1 on white, passes AA) that
  does not touch `--destructive` or `.btn-danger`.
- `requirements.txt` `waitress==3.0.2` is a real pinned release.

The deploy hardening (nginx.conf, Linux.md, README) has one security defect and several
flow/correctness defects: the nginx admin rate limit misses the actual login endpoint,
the nginx template breaks `nginx -t` on Ubuntu/Debian (nginx < 1.25.1 and pre-certbot
cert paths), Linux.md never initializes the database, and the documented cron backup
line is syntactically broken. These must be fixed before the go-live path can work.

## Critical Issues

### CR-01: nginx admin rate limit does not cover the `/login` brute-force target

**File:** `docs/deploy/nginx.conf:50-58` (also `docs/deploy/README.md:42-43`)

**Issue:** D-04's stated brute-force protection (`limit_req zone=admin`) is applied only
in `location /admin/`. The login endpoint is `/login` (`app/auth.py:25` — the `auth`
blueprint has no `url_prefix`), which matches `location /` and is **not** rate-limited.
No app-level throttle exists (no attempt counter, no Flask-Limiter). An attacker can POST
to `/login` without any request limit — the exact attack D-04 was meant to stop is
unthrottled. The README go-live verify step ("đăng nhập sai vài lần → nginx `limit_req`
chặn brute-force (429 nếu vượt 10 req/phút/IP)") is therefore false on two counts: the
login POST is not limited at all, and even where `limit_req` fires nginx returns **503**
by default (`limit_req_status` default), not 429.

**Fix:**
```nginx
limit_req_zone $binary_remote_addr zone=admin:10m rate=10r/m;
limit_req_status 429;

server {
    ...
    # login is the actual brute-force target — must be rate-limited too
    location = /login {
        limit_req zone=admin burst=5 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin/ {
        limit_req zone=admin burst=5 nodelay;
        ...
    }
}
```
Also update `README.md:42-43` to state that the limit returns 429 only after adding
`limit_req_status 429;`.

## Warnings

### WR-01: `http2 on;` directive requires nginx >= 1.25.1 — breaks `nginx -t` on Ubuntu/Debian

**File:** `docs/deploy/nginx.conf:29`

**Issue:** The `http2` directive was introduced in nginx 1.25.1 (2023-05). Ubuntu 22.04
ships 1.18.0, Ubuntu 24.04 ships 1.24.0, Debian 12 ships 1.22.1 — all report `unknown
directive "http2"`, so `nginx -t` at `Linux.md:86` fails on every distro Linux.md names.

**Fix:** Use the universally supported form:
```nginx
listen 443 ssl http2;
```
(accepted on all nginx versions; on >= 1.25.1 it logs a deprecation notice only).

### WR-02: nginx.conf references Let's Encrypt certs before they exist — documented Linux flow cannot complete

**File:** `docs/deploy/nginx.conf:32-33` + `docs/deploy/Linux.md:80-92`

**Issue:** The template hardcodes `ssl_certificate`/`ssl_certificate_key` to
`/etc/letsencrypt/live/YOUR_DOMAIN/*.pem`. Linux.md instructs copy → edit → symlink →
`nginx -t && systemctl reload nginx` → `certbot --nginx`. But before certbot runs, no
cert exists, so `nginx -t` fails with `[emerg] cannot load certificate ... No such file
or directory`. certbot --nginx also requires nginx running with a valid config, so the
whole sequence deadlocks.

**Fix:** Document a working order in Linux.md — e.g. comment out the `ssl_certificate`
/ `ssl_certificate_key` lines (or the whole 443 server block) before the first
`nginx -t`, then run `certbot --nginx -d YOUR_DOMAIN`, which writes the real cert paths
into the SSL server automatically. Re-run `nginx -t` afterward.

### WR-03: Linux.md never runs `init-db` — a fresh VPS deploy serves 500s on every page

**File:** `docs/deploy/Linux.md` (walkthrough steps 1-8)

**Issue:** Tables are created only by the `flask init-db` CLI command
(`app/__init__.py:57`, `app/db.py:11`); `create_app()` never calls `db.create_all()`.
Windows.md (step 3) and README.md (checklist item 3) run `init-db`, but Linux.md's
walkthrough omits it entirely. Following Linux.md sequentially yields a gunicorn service
whose every query fails with `no such table: products` (500 on home, search, and admin).
Additionally, if run by a non-`storeweb` user the SQLite file becomes root-owned and the
service cannot write it.

**Fix:** Add an init step after `.env` setup (Linux.md step 2) and before starting the
service, run as the service user:
```bash
sudo -u storeweb /srv/storewweb/venv/bin/flask --app wsgi init-db
```

### WR-04: cron backup line is broken — `%F` unescaped, daily SQLite backup silently never runs

**File:** `docs/deploy/Linux.md:115`

**Issue:** In crontab, an unescaped `%` is replaced by a newline and everything after the
first `%` is sent to the command's stdin. `$(date +%F)` becomes an unterminated command
substitution (`$(date +` + newline + `F)`), so the job errors out every night. This is the
**only** backup mechanism documented for the SQLite DB — a silent daily failure is a
data-loss risk (backup not being taken is only discovered at restore time).

**Fix:** Escape the percent:
```cron
0 2 * * * sqlite3 /srv/storewweb/data/app.db ".backup '/srv/backups/app-$(date +\%F).db'" && find /srv/backups -name 'app-*.db' -mtime +14 -delete
```

## Info

### IN-01: `location /static/` drops the server-level security headers

**File:** `docs/deploy/nginx.conf:44-48`

**Issue:** nginx `add_header` inheritance rule: a location that defines any `add_header`
inherits **none** from the enclosing server. `/static/` defines
`add_header Cache-Control "public"`, so static responses (images, CSS) are served without
HSTS, `X-Frame-Options`, `X-Content-Type-Options`, or `Referrer-Policy` even though the
server block sets them.

**Fix:** Re-declare the security headers inside `location /static/` (or serve static from
the proxied app path if the extra cache-control is not worth the header loss).

### IN-02: `.well-known/acme-challenge` webroot location is vestigial and assumes a dir that is never created

**File:** `docs/deploy/nginx.conf:17-19`

**Issue:** `root /var/www/html` is only used by `certbot certonly --webroot`; the
documented flow uses `certbot --nginx`, which injects its own challenge location. The
`/var/www/html` directory is not created anywhere in the docs, so if anyone does switch
to webroot mode this silently 404s. Harmless for the documented flow, but misleading.

**Fix:** Either drop the location, or create the dir and note it is only for
`--webroot` issuance.

---

_Reviewed: 2026-08-02T01:13:09+07:00_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

---

## Fix Applied

| Finding | Severity | Commit | Status |
|---------|----------|--------|--------|
| CR-01 — nginx rate limit misses `/login`; 429 claim wrong | Critical | `a676902` | fixed |
| WR-01 — `http2 on;` breaks `nginx -t` on nginx < 1.25.1 | Warning | `e71882b` | fixed |
| WR-02 — cert referenced before it exists; flow deadlocks | Warning | `f385d2e` | fixed |
| WR-03 — Linux.md omits `init-db`; fresh deploy 500s | Warning | `3557be9` | fixed |
| WR-04 — cron backup `%F` unescaped, silently never runs | Warning | `a914577` | fixed |
| IN-01 — `/static/` drops server security headers | Info | `c40d66e` | fixed |
| IN-02 — vestigial `.well-known/acme-challenge` webroot | Info | `c40d66e` | fixed |

All 7 findings fixed (4 in-scope Warning/Critical + both Info, the latter judged trivially
fixable in the same nginx.conf file). No findings skipped.

_Fixed: 2026-08-02_
_Fixer: Claude (gsd-code-fixer)_
