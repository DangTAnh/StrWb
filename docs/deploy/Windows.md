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
if not exist data mkdir data
pip install -r requirements.txt
```

`requirements.txt` đã gồm `waitress==3.0.2` — không cần cài riêng. Thư mục `data\`
chứa SQLite DB (`data\app.db`) — phải tồn tại trước khi chạy `flask init-db` (bước 3).

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

> **Nâng cấp v1.0 → v1.1:** trên một cài đặt v1.0 hiện có, lệnh `flask init-db` trên đây
> cũng thực hiện migration v1.1 một cách idempotent — thêm cột `products.cost_price` nếu
> chưa có, và rebuild lại bảng `orders` legacy chỉ khi bảng rỗng (không bao giờ xóa dữ liệu;
> nếu có hàng sẽ báo `Manual migration required`). **Sao lưu `data\app.db` trước khi chạy.**

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

## Sao lưu (Backup)

SQLite chạy ở WAL mode — bản sao an toàn cần có `app.db` + `app.db-wal` (cùng `app.db-shm`)
cùng lúc, hoặc dùng `sqlite3.exe ".backup"` (WAL-safe). Luôn sao lưu cả thư mục `uploads`.

**Phương pháp 1 — sqlite3 .backup (khuyến nghị):**

```bat
if not exist C:\backups mkdir C:\backups
sqlite3.exe "C:\path\to\storewweb\data\app.db" ".backup C:\backups\app-%date:~-4,4%%date:~-10,2%%date:~-7,2%.db"
```

> Tên file dùng chuỗi `%date%` theo định dạng locale en-US (`YYYYMMDD`). Máy dùng
> ngôn ngữ/locale khác có thể cho tên sai định dạng — khi đó hãy đặt tên file cố định
> (ví dụ `app.db.bak`) hoặc điều chỉnh chuỗi cắt theo locale của bạn.

**Phương pháp 2 — copy file (dừng app trước):** dừng waitress, copy `app.db` + `app.db-wal`
+ `app.db-shm` cùng lúc, rồi mở app lại.

**Uploads:**

```bat
robocopy app\static\uploads C:\backups\uploads /MIR
```

**Lên lịch tự động với Task Scheduler:** tạo task chạy hàng ngày (ví dụ 2:00 sáng), action =
lệnh batch sao lưu trên, "Start in" = `C:\path\to\storewweb`. Chọn *Run whether user is logged
on or not*. Thêm bước **Delete files older than 14 days** ở tab Settings để giữ chỉ N bản
sao. (Xem Linux.md §6 để cấu hình tương đương trên cron.)
