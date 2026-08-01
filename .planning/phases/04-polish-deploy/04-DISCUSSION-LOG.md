# Phase 4: Polish + Deploy - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-01
**Phase:** 4-Polish + Deploy
**Areas discussed:** Deploy target & server stack, HTTPS & reverse proxy, Polish scope

---

## Deploy target & server stack

| Option | Description | Selected |
|--------|-------------|----------|
| Windows self-host (máy hiện tại) | waitress-serve bind 127.0.0.1, front bằng nginx/Caddy tùy chọn. Không phí, đơn giản. | |
| VPS Linux | Vultr/DigitalOcean/OVH, gunicorn + nginx + Let's Encrypt. Chuẩn production 24/7, tốn ~5-10$/tháng + domain. | |
| Cả hai (dev Windows + sẵn cấu hình VPS) | waitress chạy thử trên Windows + tài liệu/bộ cấu hình gunicorn-nginx cho khi lên VPS sau | ✓ |

**User's choice:** Cả hai (dev Windows + sẵn cấu hình VPS)
**Notes:** User muốn sẵn sàng cả 2 đường — dev trên máy hiện tại, config VPS để sau lên khi cần.

---

## HTTPS & reverse proxy

| Option | Description | Selected |
|--------|-------------|----------|
| nginx + Let's Encrypt | Phổ biến nhất, đúng CLAUDE.md, certbot auto-gia-hạn | ✓ |
| Caddy (tự động HTTPS) | Caddyfile ~5 dòng, zero bảo trì cert | |
| Cloudflare | Free plan, proxy HTTPS edge, không quản lý cert server | |
| Chưa cần (LAN trước) | Chỉ chạy LAN/ngrok khi cần test | |

**User's choice:** nginx + Let's Encrypt
**Notes:** Nhất quán với CLAUDE.md ("gunicorn + nginx").

| Option | Description | Selected |
|--------|-------------|----------|
| Có domain | Đã có domain, trỏ về server khi lên VPS | ✓ |
| Chưa có (placeholder) | Config nginx/certbot với domain placeholder | |
| Chỉ IP, không domain | Let's Encrypt không cấp cert cho IP trần | |

**User's choice:** Có domain
**Notes:** Config dùng domain thật.

| Option | Description | Selected |
|--------|-------------|----------|
| Chỉ app login | Flask-Login + mật khẩu mạnh, nginx chặn brute-force cơ bản | ✓ |
| nginx allowlist IP | Chỉ IP nhà/văn phòng vào được /admin | |
| Allowlist IP + basic auth | An toàn nhất nhưng 2 lớp nhớ | |

**User's choice:** Chỉ app login
**Notes:** User chọn đơn giản nhất — đúng gợi ý "rate limiting chỉ khi internet-exposed" trong CLAUDE.md.

---

## Polish scope

| Option | Description | Selected |
|--------|-------------|----------|
| Giữ như hiện tại | D-04 (ảnh mờ + badge) đã đạt CAT-04, chỉ verify | ✓ |
| Nâng: grayscale + xếp cuối | Thêm grayscale + hàng hết xếp cuối danh sách (đổi hành vi phân trang) | |
| Nâng nhẹ: grayscale | Chỉ grayscale ảnh, giữ thứ tự sort_order | |

**User's choice:** Giữ như hiện tại
**Notes:** Minimal — D-04 Phase 3 đã đạt success criterion.

| Option | Description | Selected |
|--------|-------------|----------|
| Toàn bộ public + admin | Rà cả public + admin ở breakpoint 480/768/1200, fix mọi chỗ vỡ | ✓ |
| Chỉ public | Khách xem mobile, admin dùng máy tính | |
| Chỉ chỗ bị flag | Sửa gallery reorder, badge, grid — không audit toàn diện | |

**User's choice:** Toàn bộ public + admin
**Notes:** Ưu tiên public (đa số khách VN mobile), admin cũng dùng được trên điện thoại.

| Option | Description | Selected |
|--------|-------------|----------|
| Fix hết 5 mục | spec-sync min-width, search-clamp vs redirect, contrast 4.3→4.5:1, ảnh chính gallery 2x DPR, ký tự ₫ | ✓ |
| Chỉ 2 mục ảnh hưởng | contrast + chất lượng ảnh chính gallery | |
| Bỏ qua (chỉ verify) | Đều cosmetic, giữ code hiện tại | |

**User's choice:** Fix hết 5 mục
**Notes:** Tất cả đều nhỏ, đáng làm cho chất lượng production.

---

## Claude's Discretion

- Error pages graceful (404/500 đã có template — verify không lộ stack trace).
- Hardened config: SECRET_KEY env (đã có Phase 1), `debug=False`, nginx security headers, serve static qua nginx.
- Chi tiết deploy Linux: gunicorn workers, systemd unit, backup SQLite, sync ảnh upload, proxy headers.
- Mức rate limiting nginx chặn brute-force admin.

## Deferred Ideas

- **Allowlist IP / basic auth nginx cho /admin** — user chọn "chỉ app login"; thêm sau nếu cần lớp bảo vệ.
- **Grayscale + xếp hàng hết cuối** — user giữ D-04 hiện tại.
- **Live search AJAX / giỏ hàng / phân loại** — ngoài roadmap (deferred từ Phase 3).
