# Deploy StoreWeb trên Windows (self-host với waitress)

Hướng dẫn chạy StoreWeb production trên máy Windows tự host. Dùng **waitress** làm WSGI
server (gunicorn không chạy native trên Windows — không có `os.fork`). Cấu hình mặc định
bind `127.0.0.1:8000` và đứng sau nginx (hoặc tầng proxy/HTTPS khác) — xem `nginx.conf`.

## Yêu cầu

- Python 3.11+ (64-bit)
- pip + `venv` (khuyên dùng)
- `git` (để clone project) hoặc copy thư mục project lên máy

## 1. Cài đặt

```bat
cd C:\path\to\storewweb
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` đã gồm `waitress==3.0.2` — không cần cài riêng.

## 2. Tạo file .env

```bat
copy .env.example .env
```

Rồi mở `.env` bằng Notepad và điền giá trị thật:

- `SECRET_KEY` — sinh ngẫu nhiên:
  ```bat
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- `ADMIN_PASSWORD` — mật khẩu admin mạnh (≥8 ký tự; không để `change-me`).
- `MESSENGER_URL` — link Messenger thật của người bán.
- `SESSION_COOKIE_SECURE=true` — đặt `true` khi đứng sau HTTPS (nginx). Khi chỉ chạy
  HTTP cục bộ, để `false` để session vẫn hoạt động.

## 3. Khởi tạo database + tài khoản admin đầu tiên

```bat
set FLASK_APP=wsgi
flask init-db
```

Lệnh này tạo bảng và tạo/cập nhật tài khoản admin trong `.env`.

## 4. Chạy production (waitress)

```bat
venv\Scripts\waitress-serve --listen=127.0.0.1:8000 wsgi:app
```

Kiểm tra nhanh: mở `http://127.0.0.1:8000/` — phải trả trang chủ (HTTP 200).

> Entry point là object `app` trong `wsgi.py` (`load_dotenv()` + `create_app()`), nên
> lệnh là `wsgi:app`.

### Bind 127.0.0.1 (mặc định — khuyên dùng)

Waitress chỉ nghe trên loopback; nginx (hoặc reverse proxy khác) đứng trước, chuyển
request công khai vào. Không expose waitress thẳng ra internet.

### Nếu KHÔNG có nginx phía trước

Muốn expose thẳng, đổi `--listen=0.0.0.0:8000` **VÀ** bắt buộc phải có lớp HTTPS khác
phía trước (ví dụ Cloudflare / HAProxy có TLS). **Không khuyến khích** — mặc định hãy
chạy `127.0.0.1` sau nginx.

## 5. Chạy nền trên Windows

Hai cách phổ biến:

- **Task Scheduler**: Tạo task chạy lúc boot, action = lệnh
  `C:\path\to\storewweb\venv\Scripts\waitress-serve.exe --listen=127.0.0.1:8000 wsgi:app`,
  "Start in" = `C:\path\to\storewweb`. Chọn *Run whether user is logged on or not* để chạy
  ngay cả khi không đăng nhập.
- **NSSM** (Non-Sucking Service Manager): gói waitress thành Windows service:
  ```bat
  nssm install StoreWeb "C:\path\to\storewweb\venv\Scripts\waitress-serve.exe" "--listen=127.0.0.1:8000 wsgi:app"
  nssm set StoreWeb AppDirectory C:\path\to\storewweb
  nssm start StoreWeb
  ```

## 6. Nginx Windows (tùy chọn, khuyên dùng)

Khi có nginx Windows làm reverse proxy + HTTPS:

- Tham chiếu template `nginx.conf` trong thư mục này (sửa đường dẫn + domain thật).
- Cấu hình `proxy_pass http://127.0.0.1:8000` trỏ đúng waitress.

---

*Xem `README.md` trong thư mục này để chọn đường deploy (Windows hay Linux) + checklist go-live.*
