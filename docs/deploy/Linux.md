# Deploy StoreWeb trên VPS Linux (gunicorn + systemd + nginx + certbot)

Hướng dẫn chạy StoreWeb production trên VPS Ubuntu/Debian. Dùng **gunicorn** làm WSGI
server sau **nginx** (reverse proxy + HTTPS Let's Encrypt qua certbot). Lệnh production
giữ bind loopback `127.0.0.1:8000` — chỉ nginx gọi vào.

## Yêu cầu

- VPS Ubuntu/Debian, Python 3.11+
- Domain trỏ về IP của VPS (bản ghi A)
- Quyền root hoặc sudo

## 1. Cài đặt project + môi trường

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip nginx certbot python3-certbot-nginx sqlite3
cd /srv
sudo git clone https://github.com/YOU/storewweb.git   # hoặc rsync từ máy phát triển
cd storewweb
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
# gunicorn KHÔNG nằm trong requirements.txt (project Windows-first) — cài riêng:
sudo venv/bin/pip install gunicorn
```

Tạo user chạy app (không dùng root):

```bash
sudo useradd -r -s /usr/sbin/nologin storeweb
sudo mkdir -p /srv/storewweb/data /srv/storewweb/app/static/uploads
sudo chown -R storeweb:storeweb /srv/storewweb
```

## 2. File .env

```bash
sudo cp /srv/storewweb/.env.example /srv/storewweb/.env
sudo nano /srv/storewweb/.env
```

Điền giá trị thật: `SECRET_KEY` (sinh bằng `python -c "import secrets; print(secrets.token_hex(32))"`),
`ADMIN_PASSWORD` mạnh, `MESSENGER_URL`, và `SESSION_COOKIE_SECURE=true` (vì sau HTTPS).
`FLASK_DEBUG=0` — production không bật debug.

Phân quyền: `sudo chown storeweb:storeweb /srv/storewweb/.env && sudo chmod 600 /srv/storewweb/.env`.

Khởi tạo database + tài khoản admin **trước khi chạy app** (WR-03 — thiếu bước này thì mọi
truy vấn 500 vì chưa có bảng `products`):

```bash
cd /srv/storewweb && sudo -u storeweb venv/bin/flask --app wsgi init-db
```

Chạy bằng user `storeweb` (user của systemd service) để `data/app.db` do `storeweb` sở hữu —
không bị root sở hữu khiến service không ghi được. Lệnh tạo bảng + upsert admin từ `.env`
(`ADMIN_PASSWORD` phải đặt trước — xem bước `.env` ở trên).

> **Nâng cấp v1.0 → v1.1:** trên một cài đặt v1.0 hiện có, lệnh `flask init-db` ở trên cũng
> thực hiện migration v1.1 một cách idempotent — thêm cột `products.cost_price` nếu chưa có,
> và rebuild lại bảng `orders` legacy chỉ khi bảng rỗng (không bao giờ xóa dữ liệu; nếu có
> hàng sẽ báo `Manual migration required`). **Sao lưu `data/app.db` trước khi chạy** (xem
> §6).

## 3. Gunicorn workers

Công thức **2×CPU+1** dựa trên `nproc`:

```bash
nproc                                   # ví dụ 2
# -> workers = 2*2+1 = 5
```

Kiểm tra bằng một lệnh trước khi chạy service:

```bash
cd /srv/storewweb && venv/bin/gunicorn --workers $((2*$(nproc)+1)) --bind 127.0.0.1:8000 wsgi:app
```

Nếu mọi thứ đúng, dừng lại (Ctrl+C) và chuyển sang systemd bên dưới.

## 4. systemd unit

File `storeweb.service` trong thư mục này — copy vào systemd:

```bash
sudo cp /srv/storewweb/docs/deploy/storeweb.service /etc/systemd/system/storeweb.service
sudo nano /etc/systemd/system/storeweb.service   # sửa WorkingDirectory/EnvironmentFile/ExecStart nếu đường dẫn khác
sudo systemctl daemon-reload
sudo systemctl enable --now storeweb
sudo systemctl status storeweb
```

Sửa số workers trong `ExecStart` thành `2×CPU+1` thực tế nếu khác mặc định `5`.

## 5. nginx + HTTPS (certbot)

> **Thứ tự quan trọng (WR-02):** template `nginx.conf` tham chiếu
> `/etc/letsencrypt/live/YOUR_DOMAIN/{fullchain.pem,privkey.pem}`. Chứng chỉ PHẢI được cấp
> **trước** khi chạy `nginx -t` — nếu không nginx báo `[emerg] cannot load certificate`.
> Vì vậy cấp cert bằng `certbot certonly --standalone` trước, cài config sau.

Cấp chứng chỉ trước (cần port 80 trống — `--pre-hook` tự tạm dừng nginx nếu đang chạy):

```bash
sudo certbot certonly --standalone -d YOUR_DOMAIN --pre-hook "systemctl stop nginx" --post-hook "systemctl start nginx"
```

(certbot hỏi email + đồng ý điều khoản lần đầu.) Chứng chỉ lưu tại
`/etc/letsencrypt/live/YOUR_DOMAIN/` — đúng đường dẫn `nginx.conf` tham chiếu. Các hook
`--pre-hook/--post-hook` được certbot ghi vào renewal config để tự tạm dừng/khởi động nginx
quanh lúc gia hạn.

Copy template site và sửa domain thật (thay mọi `YOUR_DOMAIN`):

```bash
sudo cp /srv/storewweb/docs/deploy/nginx.conf /etc/nginx/sites-available/storeweb
sudo nano /etc/nginx/sites-available/storeweb
sudo ln -s /etc/nginx/sites-available/storeweb /etc/nginx/sites-enabled/storeweb
sudo nginx -t && sudo systemctl reload nginx
```

Auto-gia-hạn: certbot đã cài systemd timer khi cài package —

```bash
sudo systemctl status certbot.timer   # active; gia hạn tự động 2 lần/ngày
```

## 6. Backup SQLite

Sao lưu database hàng ngày (chạy khi app chạy vẫn an toàn nhờ WAL + `.backup`). Lệnh
`sqlite3 .backup` là WAL-safe — không cần dừng app, và copy nhất quát được cả `app.db-wal`/`-shm`.

```bash
mkdir -p /srv/backups
sqlite3 /srv/storewweb/data/app.db ".backup '/srv/backups/app-$(date +%F).db'"
```

Cron hàng ngày (bao gồm cả uploads trong routine):

```bash
sudo crontab -e
# 2:00 sáng mỗi ngày
# LƯU Ý (WR-04): trong crontab, % bị thay bằng newline — phải escape thành %% để `date +%%F`
# ra đúng ngày. Dòng dưới đã escape; đừng sửa thành %F kẻo backup âm thầm không chạy.
0 2 * * * sqlite3 /srv/storewweb/data/app.db ".backup '/srv/backups/app-$(date +%%F).db'" && rsync -a /srv/storewweb/app/static/uploads /srv/backups/uploads/ && find /srv/backups -name 'app-*.db' -mtime +14 -delete
```

Giữ backup 14 ngày. `rsync` đồng bộ `uploads` cùng lúc — phần nằm trong routine hàng ngày.

## 7. Đồng bộ ảnh upload lên VPS

Ảnh sản phẩm nằm ở `app/static/uploads/` — đồng bộ từ máy phát triển:

```bash
rsync -av app/static/uploads/ user@vps:/srv/storewweb/app/static/uploads/
```

(Đảm bảo thư mục đích thuộc quyền `storeweb`.)

## 8. Proxy headers (X-Forwarded-Proto)

`nginx.conf` (Task 5) đặt `proxy_set_header X-Forwarded-Proto $scheme;` — gunicorn nhận
header qua proxy. Back-link trong `public.py` dùng `request.host.split(':')[0]`
(scheme-agnostic), nên không cần đổi code (WR-03).

## Cập nhật phiên bản mới

```bash
cd /srv/storewweb && sudo git pull && sudo venv/bin/pip install -r requirements.txt
sudo systemctl restart storeweb
```

---

*Xem `README.md` trong thư mục này để chọn đường deploy (Windows hay Linux) + checklist go-live.*
