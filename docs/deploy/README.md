# Deploy StoreWeb — hướng dẫn triển khai production

Tài liệu deploy cho StoreWeb (Flask). Có **hai đường** tùy nền tảng:

| Đường | Nền tảng | WSGI server | Tài liệu |
|-------|----------|-------------|----------|
| **Windows self-host** | Windows | waitress | [`Windows.md`](./Windows.md) |
| **VPS Linux** | Ubuntu/Debian | gunicorn + systemd | [`Linux.md`](./Linux.md) |

Cả hai đường đều đứng sau **nginx** (reverse proxy + HTTPS Let's Encrypt qua certbot) —
xem template [`nginx.conf`](./nginx.conf). Admin chỉ bảo vệ bằng app login (Flask-Login)
+ nginx rate limiting (`limit_req`); **không** dùng basic auth nginx hay allowlist IP (D-04).

---

## Checklist go-live (chung cả hai đường)

1. **Tạo `.env`** từ `.env.example` với giá trị thật:
   - `SECRET_KEY` mạnh (`python -c "import secrets; print(secrets.token_hex(32))"`)
   - `ADMIN_PASSWORD` mạnh (≥8 ký tự, không để `change-me`)
   - `MESSENGER_URL` — link Messenger thật
   - `SESSION_COOKIE_SECURE=true` (khi đứng sau HTTPS)
   - `FLASK_DEBUG=0` — debug tắt production
2. **Cài dependencies:** `pip install -r requirements.txt` (đã gồm waitress; gunicorn cài
   riêng trên Linux — xem Linux.md).
3. **Khởi tạo database + admin:** `flask --app wsgi init-db` (tạo bảng + tài khoản admin
   đầu tiên từ `.env`, PLAT-04).
4. **nginx.conf:** thay mọi `YOUR_DOMAIN` bằng domain thật của bạn (D-03 — không deploy
   placeholder), rồi copy vào `/etc/nginx/sites-available/storeweb`.
5. **HTTPS:** `certbot --nginx -d YOUR_DOMAIN` — tự cấp + auto-gia-hạn (certbot.timer).
6. **Verify sau go-live:** mở `https://YOUR_DOMAIN/` (200, HTTPS), đăng nhập `/admin`
   bằng `ADMIN_PASSWORD`, gõ `/khong-ton-tai` → trang 404 tiếng Việt không lộ stack trace.

---

## Ghi chú bảo mật

- **Admin:** chỉ app login + nginx rate limiting (D-04). Không expose WSGI trực tiếp ra
  internet — waitress/gunicorn luôn bind `127.0.0.1:8000`, chỉ nginx gọi vào.
- **Secret:** `SECRET_KEY` chỉ nằm trong `.env`/systemd `EnvironmentFile`, không commit.
- **Debug:** `FLASK_DEBUG=0` production; error pages 404/500 không render traceback.
- **Backup:** sao lưu SQLite hàng ngày (xem Linux.md §6) + đồng bộ `app/static/uploads/`.

## File cấu hình

| File | Mục đích |
|------|----------|
| `Windows.md` | Hướng dẫn waitress trên Windows (Task Scheduler/NSSM) |
| `Linux.md` | Hướng dẫn gunicorn + systemd + nginx + certbot trên VPS |
| `nginx.conf` | Template site nginx (proxy, HTTPS, headers, rate limit admin) |
| `storeweb.service` | systemd unit cho gunicorn |
