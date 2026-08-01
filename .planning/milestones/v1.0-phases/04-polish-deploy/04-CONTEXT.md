# Phase 4: Polish + Deploy — Context

**Gathered:** 2026-08-01
**Status:** Ready for UI-SPEC/planning

## Phase Boundary

Hoàn thiện giao diện cho production (de-emphasis hết hàng/ngừng bán CAT-04, responsive mobile CAT-06, fix deferral UI còn treo từ Phase 3) và cấu hình deploy production: WSGI server (waitress cho Windows, gunicorn cho Linux), reverse proxy nginx + HTTPS Let's Encrypt, hardening config (SECRET_KEY từ env, tắt debug, error pages không lộ stack trace).

Phần tính năng mới (giỏ hàng, phân loại, đăng ký khách...) **không** nằm trong phase này.

## Implementation Decisions

### Deploy target & server stack
- **D-01:** Deploy **cả hai đường** — cấu hình sẵn để chạy trên Windows self-host (waitress) **và** tài liệu/bộ cấu hình gunicorn + systemd cho VPS Linux khi lên sau. WSGI server theo CLAUDE.md: Windows → `waitress` (gunicorn không chạy native), Linux → `gunicorn`.

### Reverse proxy & HTTPS
- **D-02:** Reverse proxy + HTTPS dùng **nginx + Let's Encrypt** (certbot, auto-gia-hạn).
- **D-03:** **Có domain sẵn** — config nginx/certbot dùng domain thật, không dùng placeholder.
- **D-04:** Bảo vệ trang admin (`/admin`) khi deploy công khai: **chỉ app login** (Flask-Login đã có) + mật khẩu mạnh; nginx thêm chặn brute-force cơ bản (rate limiting). **Không** dùng allowlist IP, **không** basic auth nginx — user chọn đơn giản.

### Polish UI
- **D-05:** **CAT-04 giữ như hiện tại** — nền tảng D-04 Phase 3 (ảnh mờ opacity 0.45 + nhãn "Hết hàng"/"Ngừng bán") đã đạt success criterion. Chỉ verify, **không** thêm grayscale, **không** đổi thứ tự sản phẩm.
- **D-06:** **CAT-06 audit responsive toàn bộ public + admin** ở mọi breakpoint 480/768/1200, fix mọi chỗ vỡ. Ưu tiên public (đa số khách VN dùng mobile), admin cũng phải dùng được trên điện thoại.
- **D-07:** **Fix hết 5 deferral UI từ Phase 3** (ghi trong `03-UI-REVIEW.md`): (1) spec-sync `.contact-strip .btn { min-width: 200px }`, (2) cho nhất quán search-clamp-vs-home-redirect (cosmetic), (3) nâng contrast dòng "Sản phẩm hiện đang hết hàng." từ ~4.3:1 lên ≥4.5:1 (AA), (4) ảnh chính gallery dùng bản rõ nét hơn (thay 400px thumb khi màn hình 2x DPR — bản gốc đã lưu đủ lớn), (5) kiểm tra render ký tự `₫`.

### Claude's Discretion
- Error pages graceful (404/500 đã có template — verify không lộ stack trace trong production).
- Hardened config: SECRET_KEY từ env (đã có từ Phase 1, verify trong production), `debug=False`, nginx security headers (HSTS, X-Frame-Options...), serve static qua nginx.
- Chi tiết deploy Linux: số gunicorn workers (công thức 2×CPU+1), systemd unit file, backup SQLite, đồng bộ ảnh upload lên VPS, proxy headers (X-Forwarded-Proto cho WR-03 back-link đã fix scheme-agnostic).
- Mức rate limiting nginx chặn brute-force admin.

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Definition & Requirements
- `.planning/ROADMAP.md` §"Phase 4: Polish + Deploy" — goal, 5 success criteria, mode mvp
- `.planning/REQUIREMENTS.md` §"Catalog công khai" (CAT-04, CAT-06) + §"Nền tảng" (PLAT-01..04)

### Prior Phase Decisions & Design System
- `.planning/phases/01-scaffold-auth-data-model/01-CONTEXT.md` — config pattern (SECRET_KEY env fail-fast), design system baseline
- `.planning/phases/01-scaffold-auth-data-model/01-UI-SPEC.md` — design system baseline (màu #2563EB/#F9FAFB, type 14/16/24/32, spacing 4/8/16/24/32/48/64, breakpoint 480/768/1200)
- `.planning/phases/02-admin-crud-images/02-UI-SPEC.md` — extensions Phase 2 (badge, button, gallery pattern)
- `.planning/phases/03-public-catalog-search-contact/03-CONTEXT.md` — D-04 foundation (ảnh mờ + badge), D-11 search normalization
- `.planning/phases/03-public-catalog-search-contact/03-UI-REVIEW.md` — 5 deferral items (fix trong Phase 4 per D-07)
- `CLAUDE.md` — tech stack, waitress vs gunicorn (Windows), What NOT to Use (rate limiting chỉ khi internet-exposed)

### Existing Code Insights
- `wsgi.py` — entry point WSGI app (dùng cho waitress/gunicorn)
- `app/config.py` — SECRET_KEY từ env, SQLALCHEMY_DATABASE_URI, upload dir
- `app/public.py` — catalog routes (home pagination đã clamp redirect, search clamp)
- `app/templates/errors/404.html`, `500.html` — dynamic extends (public chrome vs admin) từ Phase 3 WR-05 fix
- `app/static/css/style.css` — grid, card, badge, contact-strip, detail gallery

## Existing Code Insights

### Reusable Assets
- `wsgi.py` — WSGI entry (production server mount point)
- `app/__init__.py` — app factory `create_app()`
- Error templates 404/500 — dynamic extends theo request (public/admin)
- `app/image_utils.py` — thumbnail 400px + bản gốc (ảnh chính gallery dùng bản gốc cho 2x DPR)
- Config `SECRET_KEY`/`MESSENGER_URL` từ `.env` — đã sẵn pattern

### Established Patterns
- 3 blueprints (public/admin/auth), Flask-Login, template kế thừa, design system tokens, plain CSS <20KB không framework.
- Verify-harness: Flask-SQLAlchemy 3.1.1 tạo engine eager trong `init_app` → cô lập temp DB bằng dispose+rebuild `db._app_engines[app][None]`.

### Integration Points
- `requirements.txt` — thêm `waitress` (dev Windows); tài liệu thêm `gunicorn` cho Linux (không thêm vào requirements nếu chỉ Windows)
- Cấu hình deploy: nginx config file + certbot instructions + systemd unit (docs/deploy/)
- CSS: fix contrast, spec-sync, gallery image source, ₫ glyph

## Specific Ideas

Không có yêu cầu "làm giống X" — user chọn theo chuẩn production thông dụng: nginx + Let's Encrypt, waitress (Windows) / gunicorn (Linux), admin chỉ app login. User có domain sẵn.

## Deferred Ideas

- **Allowlist IP / basic auth nginx cho /admin** — user chọn "chỉ app login" (D-04). Có thể thêm sau nếu cần thêm lớp bảo vệ.
- **Thêm grayscale + xếp hàng hết cuối** — user chọn giữ D-04 hiện tại (D-05).
- **Live search AJAX / giỏ hàng / phân loại sản phẩm** — ngoài scope roadmap (đã ghi deferred từ Phase 3).

---

*Phase: 4-Polish + Deploy*
*Context gathered: 2026-08-01*
