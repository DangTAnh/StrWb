---
phase: 04-polish-deploy
verified: 2026-08-02T01:10:00Z
status: passed
score: 5/5 success criteria verified
overrides_applied: 0
overrides: []
gaps: []
human_verification:
  - test: "Open a product detail page with ≥2 images on a 2x-DPR (Retina/High-DPI) screen and click each 72px thumbnail."
    expected: "The main image is sharp (served from the full-size `filename`, not the 400px thumb) at width 440, and the click swaps the main image to the clicked thumbnail's data-src (full-size). Thumbnails themselves stay 72x72."
    why_human: "2x-DPR sharpness is visual; the Flask test client confirms the asset names in HTML but not pixel rendering."
  - test: "Visually audit the public site and admin at browser widths ≤480, 768, and ≥1200."
    expected: "No horizontal scroll; home grid 2/3/4 columns; header stacks on mobile and becomes a single row with the search box right-aligned (max-width 480px) at ≥768; detail page stacks below 768 and is 2-column (gallery 360px, then 440px at ≥1200) above; contact-strip CTA (min-width 200px) fits at 320px viewport; admin product table scrolls horizontally inside its card rather than breaking the page; form inputs ≥44px touch."
    why_human: "Media-query reflow and touch-target sizing are visual/behavioral and not verifiable via the test client."
  - test: "Confirm the ₫ (U+20AB Dong sign) glyph renders in the price on a browser running the Noto Sans VN fallback chain."
    expected: "Prices render as e.g. '150.000₫' with the ₫ glyph visible (not a tofu box). If a glyph is missing on some OS, document a fallback font carrying U+20AB per 04-UI-SPEC D-07 #5."
    why_human: "Font glyph coverage is OS/browser-dependent; the code-level verdict is PASS (Noto Sans VN carries U+20AB) but visual confirmation needs a browser."
  - test: "Run the real production deploy against a real domain."
    expected: "certbot --nginx -d <real-domain> issues an HTTPS cert, nginx serves the site over 443, /admin login works behind rate limiting, and the Verify production checklist in docs/deploy/README.md passes."
    why_human: "D-02/D-03 requires a real domain and a live VPS/Windows host; nginx.conf currently carries the YOUR_DOMAIN placeholder that must be replaced before go-live."
---

# Phase 4: Polish + Deploy Verification Report

**Phase Goal (MVP user story):** The store owner runs StoreWeb in production (Windows self-host or VPS Linux) behind a reverse proxy with HTTPS, admin protected; customers get a polished, mobile-responsive catalog with clear out-of-stock de-emphasis
**Verified:** 2026-08-02T01:10:00Z
**Status:** passed (all 5 roadmap success criteria VERIFIED programmatically; 4 non-blocking human UAT items listed)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Out-of-stock and discontinued products are visually de-emphasized without overwhelming in-stock items (SC-1, CAT-04, D-05) | VERIFIED | `style.css:371` `.is-unavailable .product-card-thumb img { opacity: 0.45 }` + `:372` `.badge-overlay` (Hết hàng / Ngừng bán); `grayscale` absent from CSS; grid order unchanged (`sort_order ASC, id ASC`, `public.py:36`). Test: seeded out-of-stock product renders `.is-unavailable` card; `TASK5_OK`/`TASK4_OK` (04-03). |
| 2 | Application layout is fully responsive on mobile (SC-2, CAT-06, D-06) | VERIFIED | `style.css`: grid `repeat(2,1fr)` (362) / 3-col ≥768 (363) / 4-col ≥1200 (364), search `max-width:480px; margin-left:auto` ≥768 (358), gallery `360px` ≥768 (419) / `440px` ≥1200 (421), container `max-width:1200px` (36), `.table-scroll { overflow-x:auto }` (183) wraps admin table, `.contact-strip .btn { min-width:200px }` (385) fits 288px at 320px viewport, `.form-field input` 44px height (259). Test: all invariants asserted (`TASK5_OK` 04-01; `TASK4_OK` 04-03). |
| 3 | Application is deployed with a production WSGI server behind a reverse proxy with HTTPS (SC-3, D-01/D-02/D-03) | VERIFIED (config) | `requirements.txt` pins `waitress==3.0.2`; waitress smoke test GET / → 200 (`TASK1_OK` 04-02). `docs/deploy/Linux.md` + `storeweb.service` gunicorn/systemd. `nginx.conf`: listen 80→443 redirect, acme-challenge, ssl_certificate `/etc/letsencrypt/live/YOUR_DOMAIN/`, `proxy_pass http://127.0.0.1:8000`, `X-Forwarded-Proto $scheme`, static alias. Certbot `--nginx` documented. Human UAT: real-domain HTTPS go-live (domain not available at exec time). |
| 4 | SECRET_KEY loaded from environment variable and debug mode disabled in production (SC-4, PLAT-02) | VERIFIED | `app/__init__.py:32` `SECRET_KEY=os.environ.get('SECRET_KEY')` + `:47-48` fail-fast RuntimeError; `:42` `DEBUG=(FLASK_DEBUG=='1')` default off; no hardcoded `debug=True`. `.env.example` documents `SECRET_KEY`, `FLASK_DEBUG=0`, `SESSION_COOKIE_SECURE`. Test: with SECRET_KEY set + FLASK_DEBUG=0 → `app.config['DEBUG'] is False`, SESSION_COOKIE_SECURE False (`TASK1_OK` 04-03). |
| 5 | Error pages display gracefully without exposing stack traces (SC-5) | VERIFIED | `errors/404.html`/`500.html` render only Vietnamese copy + home link; no `traceback`/`{{ error }}`/`{{ e }}`; `app/__init__.py:78-81` 500 handler rolls back + renders 500 page; no PROPAGATE_EXCEPTIONS. Test: `/khong-ton-tai` → 404 "Trang không tìm thấy"; forced-500 route → 500 "Đã có lỗi xảy ra" with no Traceback/exception marker in body (`TASK2_OK` 04-03). |

**Score:** 5/5 truths verified

### Decision Spot-Checks (D-01..D-07 + PLAT)

| Decision | Status | Evidence |
|----------|--------|----------|
| D-01 deploy cả hai đường (waitress Windows + gunicorn/systemd Linux) | VERIFIED | `requirements.txt` + `docs/deploy/Windows.md`; `docs/deploy/Linux.md` + `storeweb.service`; waitress smoke 200 |
| D-02 reverse proxy + HTTPS nginx + Let's Encrypt | VERIFIED (config) | `nginx.conf` 80→443, ssl_certificate, acme-challenge; Linux.md certbot `--nginx` + auto-renew |
| D-03 config nhận domain thật | PARTIAL (human) | `YOUR_DOMAIN` placeholder kept + bold go-live comment; no real domain at exec time — must replace before deploy |
| D-04 admin chỉ app login + rate limiting, không basic auth/allowlist | VERIFIED | `nginx.conf` `limit_req_zone zone=admin rate=10r/m` + `location /admin/ { limit_req zone=admin burst=5 nodelay }`; no `auth_basic`, no `allow` directive (04-03 TASK3_OK) |
| D-05 CAT-04 giữ nguyên hiện trạng | VERIFIED | opacity 0.45 + badge overlay intact; no grayscale; no reorder |
| D-06 responsive audit 480/768/1200 | VERIFIED | all invariants HOLD; no fixes required (04-01 Task 5) |
| D-07 #1 spec-sync `.contact-strip .btn` | VERIFIED | comment above rule `style.css:385` (`Declared spec addition`); rule value unchanged |
| D-07 #2 search out-of-range redirect khớp home | VERIFIED | `public.py` `if pagination.total and page > pagination.pages: redirect(url_for('public.search', q=q, page=pagination.pages))`; `page<1` → page=1. Test `?q=san&page=99` → 302 `page=3`; `page=0` → 302 `page=1` |
| D-07 #3 contrast `.out-of-stock-note` | VERIFIED | `color: #B91C1C`; measured **6.19:1** on `#F9FAFB` (≥4.5:1 AA); `--destructive` token unchanged |
| D-07 #4 gallery main image bản gốc (2x DPR) | VERIFIED (code) | `product_detail.html` main img + `data-src` use `img.filename`, `width/height=440`; thumbs keep `thumb_filename`; human UAT for pixel sharpness |
| D-07 #5 `₫` glyph render | VERIFIED (code) | Noto Sans VN leads font stack and carries U+20AB → verdict PASS; human UAT for OS/browser confirmation |
| PLAT-02 SECRET_KEY env + debug off | VERIFIED | 04-03 Task 1 |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `app/public.py` | search out-of-range redirect mirroring home | VERIFIED | `if pagination.total and page > pagination.pages: return redirect(url_for('public.search', q=q, page=pagination.pages))` + `page<1` guard; `_manual_pagination` unchanged |
| `app/templates/public/product_detail.html` | main image + swap data-src serve `filename` at 440px; 72px thumbs keep `thumb_filename` | VERIFIED | main `src`/`data-src` → `uploads/<uuid>.jpg`, `width="440" height="440"`; thumb `src` → `<uuid>_thumb.jpg`; swap JS unchanged |
| `app/static/css/style.css` | spec-sync comment, `#B91C1C` out-of-stock note, responsive invariants intact, <20KB | VERIFIED | 16,033 bytes (16.0KB); all breakpoint/grid/CAT-04 assertions pass |
| `requirements.txt` | `waitress==3.0.2` appended; no gunicorn/Redis/Celery/Flask-Limiter | VERIFIED | 7 lines; waitress smoke test 200 |
| `.env.example` | SECRET_KEY, ADMIN_USERNAME/PASSWORD, MESSENGER_URL, SESSION_COOKIE_SECURE guidance, FLASK_DEBUG=0 | VERIFIED | all present |
| `docs/deploy/Windows.md` | waitress guide: .env, waitress-serve 127.0.0.1:8000 wsgi:app, background run | VERIFIED | created |
| `docs/deploy/Linux.md` | gunicorn 2*CPU+1, systemd, certbot --nginx, SQLite backup, rsync uploads | VERIFIED | created |
| `docs/deploy/nginx.conf` | rate limit /admin, HTTPS, security headers, static alias, X-Forwarded-Proto | VERIFIED | created |
| `docs/deploy/storeweb.service` | systemd unit, non-root User, EnvironmentFile, Restart=always | VERIFIED | created |
| `docs/deploy/README.md` | index both paths + go-live checklist + Verify production section | VERIFIED | created |
| `docs/deploy/README.md` | "Verify production" post-go-live checklist | VERIFIED | added (04-03 Task 4, commit `7ebc5d1`) |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | -- | ------ | ------- |
| `public.py` search | `url_for('public.search')` | redirect last valid page (out-of-range) | WIRED | 302 `page=3` test; `q` preserved |
| `product_detail.html` main img | `ProductImage.filename` | full-size asset for 440px box | WIRED | `uploads/<uuid>.jpg` rendered; no `thumb_filename` in main img |
| `product_detail.html` thumb | `ProductImage.thumb_filename` | 72×72 thumbnail asset | WIRED | `<uuid>_thumb.jpg` rendered |
| `wsgi.py` app object | `waitress-serve ... wsgi:app` | Windows WSGI entry | WIRED | smoke test GET / → 200 |
| `app/__init__.py` | systemd `EnvironmentFile` | SECRET_KEY env fail-fast | WIRED | `storeweb.service` EnvironmentFile; fail-fast verified |
| `app/static/uploads/` | `nginx.conf location /static/` | nginx serves static + uploads | WIRED | `alias` + `expires 7d` |
| `public.py` back-link | `request.host.split(':')[0]` | scheme-agnostic behind proxy | WIRED | `app/public.py:53` (WR-03) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| search out-of-range redirect | `GET /search?q=san&page=99` (30 items) | 302 → `page=3` | PASS |
| search negative page | `GET /search?q=san&page=0` | 302 → `page=1` | PASS |
| home out-of-range redirect | `GET /?page=99` (24 items) | 302 → last page | PASS |
| detail gallery full-size | `GET /products/3` (2 images) | main `uploads/img-a.jpg` + swap `img-b.jpg` + `_thumb.jpg` thumbs + `width="440"` | PASS |
| out-of-stock note | `GET /products/3` | "Sản phẩm hiện đang hết hàng." copy intact | PASS |
| 404 error page | `GET /khong-ton-tai` | 404 "Trang không tìm thấy", no traceback | PASS |
| 500 error page | forced-500 route | 500 "Đã có lỗi xảy ra", no Traceback/marker | PASS |
| admin unauth redirect | `GET /admin/products` | 302 → /login | PASS |
| login render | `GET /login` | 200 "Đăng nhập" | PASS |
| waitress WSGI smoke | waitress create_server + GET / | HTTP 200 | PASS |
| all public routes | `/`, `/?page=2`, `/search`, `/search?q=ao`, `/products/1` | 200 | PASS |
| CSS budget | style.css bytes | 16,033 < 20,000 | PASS |

### Probe Execution

No `probe-*.sh` scripts exist in the repo and no probes were declared in any Phase 4 PLAN/SUMMARY. Step 7c: N/A.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| CAT-04 | 04-01 | hết hàng/ngừng bán hiển thị khác đi | SATISFIED | `style.css:371-372` opacity 0.45 + badge overlay (D-05 HOLD) |
| CAT-06 | 04-01 | responsive mobile | SATISFIED | grid 2/3/4, gallery 360/440, header stack, admin `.table-scroll` |
| PLAT-02 | 04-02/04-03 | SECRET_KEY env + debug off production | SATISFIED | `app/__init__.py:32,42,47-48`; `.env.example`; verified |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `docs/deploy/nginx.conf` | all | `YOUR_DOMAIN` placeholder (no real domain at exec time) | Info (go-live requirement) | Deploy must replace before going live (D-03); bold comment added |
| `app/static/css/style.css` | 50-51 | orphaned `.coming-soon` rule (inherited from Phase 1) | Info (non-blocking) | dead CSS ~few lines; out of phase-4 scope |

No TBD/FIXME/XXX/TODO/HACK markers in phase code; no stub templates; no leaked SECRET_KEY/admin_note; all 11 task commits exist.

### Human Verification Required (non-blocking)

1. **2x-DPR gallery sharpness + swap** — See frontmatter `human_verification[0]`.
2. **Responsive visual audit** — See frontmatter `human_verification[1]`.
3. **₫ glyph browser confirmation** — See frontmatter `human_verification[2]`.
4. **Real-domain HTTPS go-live** — See frontmatter `human_verification[3]`.

### Gaps Summary

No functional gaps. All 5 roadmap success criteria verified against the actual code with independent execution (Flask test client against isolated temp DBs, waitress smoke test, source/HTML/CSS assertions): 40+ programmatic checks passing across the three plans. Non-blocking notes:

1. **`YOUR_DOMAIN` placeholder** — nginx.conf/Linux.md/README keep the token because no real domain was available at execution time. It is flagged prominently (D-03) and must be replaced before go-live; certbot issuance requires a real domain + VPS.
2. **Verify-only tasks carried no commits** — 04-01 Task 5 and 04-03 Tasks 1-3 were verify-then-fix with zero changes needed; intentionally no per-task commit (no diff). Documented in each SUMMARY.
3. **Pre-existing `Đ/đ` not folded to `d`** (Phase 3 note) and orphaned `.coming-soon` CSS remain out of Phase 4 scope.

The 4 human UAT items require browser/VPS sign-off; all automated truths pass, so status is `passed` per the orchestrator's instruction.

---

_Verified: 2026-08-02T01:10:00Z_
_Verifier: Claude (gsd-execute-phase)_
