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
5. **HTTPS:** cấp chứng chỉ **trước khi** `nginx -t`:
   `sudo certbot certonly --standalone -d YOUR_DOMAIN` (cần port 80 trống; tự gia-hạn qua
   certbot.timer — xem Linux.md §5).
6. **Verify sau go-live:** xem mục "Verify production" bên dưới.

---

## Verify production (checklist sau go-live)

Chạy các kiểm tra sau sau khi deploy lên production:

1. **HTTPS + trang chủ:** mở `https://YOUR_DOMAIN/` → HTTP 200, trình duyệt không cảnh
   báo HSTS/SSL, khóa ổ khóa xuất hiện (HTTPS hoạt động).
2. **Admin login:** vào `https://YOUR_DOMAIN/admin` → bị redirect sang `/login`; đăng nhập
   bằng `ADMIN_PASSWORD` trong `.env` → vào được dashboard. Thử đăng nhập sai vài lần —
   nginx `limit_req` chặn brute-force: `/login` và `/admin/` giới hạn 10 req/phút/IP, trả
   **429** khi vượt (nhờ `limit_req_status 429;` trong nginx.conf).
3. **Error page 404:** gõ `https://YOUR_DOMAIN/khong-ton-tai` → trang 404 tiếng Việt
   ("Trang không tìm thấy") **không kèm stack trace**.
4. **Error page 500:** tạm kích hoạt lỗi server (nếu cần) → trang 500 "Đã có lỗi xảy ra",
   body không chứa `Traceback` / exception message.
5. **Không lộ secret:** kiểm tra nginx error log / response body không chứa `SECRET_KEY`
   hoặc giá trị `.env`; `.env` có quyền `600` (Linux) và không bị commit.
6. **Static + uploads:** `https://YOUR_DOMAIN/static/...` trả ảnh/asset trực tiếp từ nginx
   (không đi qua WSGI), HTTP 200 + header `Cache-Control`.

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
