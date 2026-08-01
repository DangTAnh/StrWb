---
phase: 04-polish-deploy
plan: 03
subsystem: testing
tags: [flask, hardening, verification, nginx, https, error-pages, secret-key, debug]
requires:
  - phase: 04-polish-deploy
    plan: 01
    provides: CAT-04 de-emphasis + responsive invariants (SC-1/SC-2 sources)
  - phase: 04-polish-deploy
    plan: 02
    provides: waitress pin, docs/deploy/nginx.conf, Linux.md certbot, .env.example FLASK_DEBUG
provides:
  - Verified SECRET_KEY env + fail-fast + debug off (SC-4, PLAT-02)
  - Verified error pages 404/500 never leak stack traces (SC-5)
  - Verified nginx HTTPS + admin rate limiting + security headers + X-Forwarded-Proto (SC-3, D-04, D-02, WR-03)
  - docs/deploy/README.md "Verify production" post-go-live checklist
affects: [verifier, phase close]
tech-stack:
  added: []  # no new deps
  patterns: [verify-then-fix: source assertions + isolated temp-DB route rendering, boom-route registered before first request to satisfy Flask setup_finished guard]
key-files:
  created: []
  modified: [docs/deploy/README.md]
key-decisions:
  - "All success criteria (SC-1..SC-5) verified PASS — no production code changes required in this plan except the README verify checklist"
  - "D-04 verified at directive level: nginx.conf has no auth_basic and no allow directive (comment text mentioning the English phrase is documentation only)"
  - "Error-page leak test uses a boom route registered BEFORE the first request (Flask forbids route registration after app has handled a request)"
requirements-completed: [PLAT-02]
duration: 14min
completed: 2026-08-02
---

# Phase 4 Plan 3: Production Hardening + Verification Summary

Verified the entire Phase 4 success-criteria suite (SC-1..SC-5) end-to-end: SECRET_KEY loaded from env with fail-fast and debug off by default (SC-4/PLAT-02), 404/500 error pages render friendly Vietnamese copy with no stack trace (SC-5), nginx config carries HTTPS + Let's Encrypt cert path + admin rate limiting + all four security headers + `X-Forwarded-Proto $scheme` with no basic-auth/allowlist (SC-3/D-04/D-02), and the public back-link stays scheme-agnostic (WR-03). All verifications PASSED with zero production code changes — the only file edit was adding the post-go-live "Verify production" checklist to `docs/deploy/README.md`.

## Performance

- **Duration:** 14 min
- **Started:** 2026-08-02T00:44:00Z
- **Completed:** 2026-08-02T01:05:00Z
- **Tasks:** 4 completed (3 verify-only, 1 doc)
- **Files modified:** 1

## Accomplishments
- **SC-4 / PLAT-02 (Task 1):** `SECRET_KEY=os.environ.get('SECRET_KEY')` with `raise RuntimeError('SECRET_KEY must be set in environment variables...')` fail-fast, `DEBUG=(FLASK_DEBUG=='1')` default off, no hardcoded `debug=True`; `.env.example` documents `SECRET_KEY`, `FLASK_DEBUG=0`, `SESSION_COOKIE_SECURE`. With SECRET_KEY set + FLASK_DEBUG=0: `app.config['DEBUG'] is False`, SESSION_COOKIE_SECURE defaults False. PASS
- **SC-5 (Task 2):** `errors/404.html`/`500.html` reference no exception object (`traceback`, `{{ error }}`, `{{ e }}` absent); `/khong-ton-tai` → 404 "Trang không tìm thấy"; a forced-500 route → 500 "Đã có lỗi xảy ra" with the response body free of `Traceback` and the exception message. PASS
- **SC-3 / D-04 / D-02 / WR-03 (Task 3):** `nginx.conf` — `limit_req_zone zone=admin` + `limit_req zone=admin`, `ssl_certificate` at `/etc/letsencrypt/live/`, acme-challenge passthrough, listen 80+443, HSTS `max-age=31536000`, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, `X-Forwarded-Proto $scheme`; **no `auth_basic` and no `allow` directive** (verified at directive level). `Linux.md` has certbot `--nginx` + auto-renew. `public.py` back-link uses `request.host.split(':')[0]` (scheme-agnostic). PASS
- **E2E (Task 4):** source assertions for SC-1 (de-emphasis), SC-2 (grid 2/3/4 + gallery 440 + container 1200), SC-3 (waitress pin + nginx hardening); temp-DB route render: `/`, `/?page=2`, `/search`, `/search?q=ao`, `/products/1` all 200; `/admin/products` unauth → 302; `/login` → 200 with "Đăng nhập" copy. README "Verify production" checklist added. PASS
- **Phase smoke:** full end-to-end with 30 products + gallery images — all public routes 200 (except expected 404), detail page serves `filename` main image + `_thumb.jpg` thumbs at 440px, search `?q=san&page=99` → 302 `page=3`, out-of-stock note copy intact, error pages clean

## Task Commits

1. **Task 1: Verify SECRET_KEY env + debug off (PLAT-02, SC-4)** - no commit (verify-only, all correct)
2. **Task 2: Verify error pages không lộ stack trace (SC-5)** - no commit (verify-only, all correct)
3. **Task 3: Verify HTTPS + admin rate limiting + security headers + proxy headers** - no commit (verify-only, all correct)
4. **Task 4: E2E verification toàn bộ success criteria + README verify section** - `7ebc5d1` (docs)

## Files Created/Modified
- `docs/deploy/README.md` - added "Verify production" post-go-live checklist (HTTPS home, /admin login + rate limit, 404/500 no stack trace, no SECRET_KEY leak, nginx static serving)

## Decisions Made
- No production code changes required — the hardening work done in Phase 1 (SECRET_KEY fail-fast), Phase 3 (error templates WR-05), and 04-02 (nginx/Linux config) already satisfied every criterion; this plan's job was to prove it and document the verification procedure
- D-04 checked at the nginx directive level (`auth_basic`/`allow`) rather than by English word, because the config's Vietnamese comments legitimately mention "basic auth"/"allowlist" as documentation

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan Task 2 verify registered the boom route after the first request**
- **Found during:** 04-03 Task 2 verify (first run failed)
- **Issue:** Flask forbids `@app.route()` after the app has handled its first request (`AssertionError: The setup method 'route' can no longer be called...`). The plan's verify issued `GET /khong-ton-tai` before defining the forced-500 route.
- **Fix:** Registered the boom route immediately after `from wsgi import app`, before any test-client request. Re-ran → 404 and 500 both clean.
- **Files modified:** none (test-harness invocation only)
- **Verification:** TASK2_OK printed (server-side ERROR log is expected; response body has no traceback)

---

**Total deviations:** 1 auto-fixed (test-harness ordering)
**Impact on plan:** None — production behavior verified exactly as intended.

## Issues Encountered
- None in production code. All three verify-then-fix tasks concluded PASS without edits.

## Phase Close Readiness
- All Phase 4 success criteria SC-1..SC-5 verified: de-emphasis (SC-1), responsive (SC-2), production WSGI + reverse proxy + HTTPS (SC-3), SECRET_KEY env + debug off (SC-4), graceful error pages (SC-5)
- 04-01 (UI polish), 04-02 (deploy config), 04-03 (hardening + verify) all complete — phase ready for close

---
*Phase: 04-polish-deploy*
*Completed: 2026-08-02*

## Self-Check: PASSED

All claims verified — SUMMARY file exists, Task 4 commit 7ebc5d1 present, tasks 1-3 verify-only, all task verifies + PHASE4_SMOKE_OK green against isolated temp DBs, `data/app.db` unchanged (1 product "Áo sơ mi", 0 image rows).
