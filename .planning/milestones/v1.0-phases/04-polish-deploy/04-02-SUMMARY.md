---
phase: 04-polish-deploy
plan: 02
subsystem: infra
tags: [flask, wsgi, waitress, gunicorn, nginx, certbot, systemd, https, deploy]
requires:
  - phase: 01-scaffold-auth-data-model
    provides: app factory + wsgi.py entry point, SECRET_KEY env fail-fast, init-db CLI
provides:
  - docs/deploy/ full set: README index, Windows.md (waitress), Linux.md (gunicorn/systemd), nginx.conf (proxy/HTTPS/headers/rate-limit), storeweb.service
  - waitress==3.0.2 pinned in requirements.txt (Windows self-host WSGI server)
  - .env.example completed with FLASK_DEBUG + SESSION_COOKIE_SECURE guidance
affects: [04-03 hardening + verification, verifier]
tech-stack:
  added: [waitress==3.0.2]
  patterns: [Windows waitress-serve --listen=127.0.0.1:8000 wsgi:app, gunicorn 2*CPU+1 workers behind nginx, nginx limit_req_zone for /admin, HTTP 80 -> HTTPS 301 with acme-challenge passthrough]
key-files:
  created: [docs/deploy/README.md, docs/deploy/Windows.md, docs/deploy/Linux.md, docs/deploy/nginx.conf, docs/deploy/storeweb.service]
  modified: [requirements.txt, .env.example]
key-decisions:
  - "D-01 both paths: waitress (Windows, pinned) + gunicorn/systemd (Linux, documented only — NOT in requirements.txt because project is Windows-first)"
  - "D-02/D-03: nginx + certbot --nginx, YOUR_DOMAIN placeholder kept (no real domain available at exec time) with a bold comment that it MUST be replaced before go-live"
  - "D-04: /admin protected ONLY by app login + nginx limit_req_zone admin:10m rate=10r/m burst=5 — no basic auth, no IP allowlist (user's choice)"
  - "waitress smoke test: installed waitress 3.0.2, create_server on ephemeral port, GET / -> 200"
requirements-completed: [PLAT-02]
duration: 16min
completed: 2026-08-02
---

# Phase 4 Plan 2: Deployment Summary

Configured and documented production deployment for both target paths (D-01): Windows self-host via **waitress** (added to `requirements.txt`, smoke-tested 200) and VPS Linux via **gunicorn + systemd** (documented only, 2×CPU+1 workers, non-root user, EnvironmentFile), both behind an **nginx** reverse proxy with Let's Encrypt HTTPS, security headers, static-file serving, and admin rate limiting — no basic auth or IP allowlist (D-04). `docs/deploy/` is now the reproducible go-live reference.

## Performance

- **Duration:** 16 min
- **Started:** 2026-08-02T00:10:00Z
- **Completed:** 2026-08-02T00:26:00Z
- **Tasks:** 4 completed
- **Files modified:** 7 (5 created, 2 modified)

## Accomplishments
- **D-01 Windows:** `requirements.txt` pins `waitress==3.0.2`; `Windows.md` covers `.env` setup (SECRET_KEY via `secrets.token_hex`, ADMIN_PASSWORD, MESSENGER_URL, `SESSION_COOKIE_SECURE=true` behind HTTPS), `waitress-serve --listen=127.0.0.1:8000 wsgi:app`, Task Scheduler/NSSM background running, and the default 127.0.0.1 bind (explicit warning against exposing waitress directly without another HTTPS layer)
- **D-01 Linux:** `Linux.md` + `storeweb.service` — gunicorn workers `2×CPU+1` (`$((2*$(nproc)+1))`), bind `127.0.0.1:8000`, systemd unit with `[Unit]/[Service]/[Install]`, non-root `User=storeweb`, `EnvironmentFile` for SECRET_KEY, `Restart=always`, certbot `--nginx -d YOUR_DOMAIN` + `certbot.timer` auto-renew, daily SQLite `.backup` via cron (14-day retention), `rsync` upload sync, X-Forwarded-Proto note
- **D-02/D-03 nginx:** `nginx.conf` — `limit_req_zone $binary_remote_addr zone=admin:10m rate=10r/m` + `location /admin/ { limit_req zone=admin burst=5 nodelay; ... }`, HTTP 80 → HTTPS 301 with `/.well-known/acme-challenge/` passthrough, 443 SSL block pointing at `/etc/letsencrypt/live/YOUR_DOMAIN/`, `client_max_body_size 16M` matching MAX_CONTENT_LENGTH, security headers (HSTS `max-age=31536000; includeSubDomains`, X-Frame-Options, X-Content-Type-Options, Referrer-Policy), `location /static/ { alias ...; expires 7d }`, `X-Forwarded-Proto $scheme` proxy header
- **D-04:** admin protected only by app login + nginx rate limiting; no basic auth, no allowlist — matching the user's explicit choice
- **PLAT-02 / SC-4:** `.env.example` documents `FLASK_DEBUG=0` + `SESSION_COOKIE_SECURE`; `README.md` go-live checklist includes init-db (PLAT-04), domain swap, certbot, HTTPS + /admin verification
- **Waitress smoke test:** installed `waitress==3.0.2`, started `create_server(app, host='127.0.0.1', port=0)`, `GET /` returned HTTP 200

## Task Commits

1. **Task 1: waitress cho Windows self-host (D-01) + smoke test** - `cdd8e02` (feat)
2. **Task 2: gunicorn + systemd cho VPS Linux (D-01 Linux)** - `6a0cebf` (docs)
3. **Task 3: nginx reverse proxy + HTTPS + security headers + rate limiting admin (D-02, D-04)** - `94f54ba` (docs)
4. **Task 4: .env.example hoàn chỉnh + docs/deploy/README.md index** - `38c9f60` (docs)

## Files Created/Modified
- `docs/deploy/Windows.md` - waitress self-host guide (created)
- `docs/deploy/Linux.md` - gunicorn/systemd/certbot/backup/sync guide (created)
- `docs/deploy/nginx.conf` - reverse proxy + HTTPS + headers + admin rate limit template (created)
- `docs/deploy/storeweb.service` - systemd unit (created)
- `docs/deploy/README.md` - deploy index + go-live checklist (created)
- `requirements.txt` - `waitress==3.0.2` appended (modified)
- `.env.example` - `FLASK_DEBUG=0` + SESSION_COOKIE_SECURE guidance (modified)

## Decisions Made
- Keep `YOUR_DOMAIN` placeholder in nginx.conf/Linux.md (no real domain provided at execution time) but flag it prominently for go-live — per plan D-03 "config receives real domain, not placeholder" with the executor fallback explicitly allowed by the plan
- gunicorn NOT added to requirements.txt — Windows-first project, documented-only for Linux (plan and CLAUDE.md)
- Waitress installed in the runtime environment so the real smoke test runs (plan acceptance: "nếu chưa cài → executor chạy pip install -r requirements.txt rồi chạy lại verify")

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] waitress not installed at start → installed pinned version**
- **Found during:** 04-02 Task 1 smoke test
- **Issue:** `import waitress` raised ModuleNotFoundError; the plan's verify has an ImportError fallback but the acceptance criteria require installing and re-running the real smoke test.
- **Fix:** `python -m pip install waitress==3.0.2` (exactly the pinned version from the plan). Re-ran verify → `TASK1_OK waitress_smoke=200`.
- **Files modified:** none (environment install)
- **Verification:** TASK1_OK waitress_smoke=200 printed

---

**Total deviations:** 1 auto-fixed (environment package install per plan acceptance)
**Impact on plan:** None — required dependency installed; production code/config unchanged by the fix.

## Issues Encountered
- waitress 3.0.2's `server.effective_port` is a string, not int — harness formatting detail, no production impact.

## Next Phase Readiness
- `docs/deploy/` complete and self-consistent: README indexes both paths, nginx.conf references the exact service paths, storeweb.service matches Linux.md
- 04-03 (hardening + verify) can now verify the deployed config: SECRET_KEY env, debug off, error pages, HTTPS/rate-limit/headers, and the full SC-1..SC-5 success-criteria suite

---
*Phase: 04-polish-deploy*
*Completed: 2026-08-02*

## Self-Check: PASSED

All claims verified — SUMMARY file exists, all 4 task commits present (cdd8e02, 6a0cebf, 94f54ba, 38c9f60), all task verifies + plan-level verification green, `data/app.db` unchanged.
