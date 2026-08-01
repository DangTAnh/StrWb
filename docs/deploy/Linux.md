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

Copy template site và sửa domain thật (thay mọi `YOUR_DOMAIN`):

```bash
sudo cp /srv/storewweb/docs/deploy/nginx.conf /etc/nginx/sites-available/storeweb
sudo nano /etc/nginx/sites-available/storeweb
sudo ln -s /etc/nginx/sites-available/storeweb /etc/nginx/sites-enabled/storeweb
sudo nginx -t && sudo systemctl reload nginx
```

Cấp chứng chỉ Let's Encrypt (certbot tự sửa nginx.conf để thêm SSL):

```bash
sudo certbot --nginx -d YOUR_DOMAIN
```

Auto-gia-hạn: certbot đã cài systemd timer khi cài package —

```bash
sudo systemctl status certbot.timer   # active; gia hạn tự động 2 lần/ngày
```

## 6. Backup SQLite

Sao lưu database hàng ngày (chạy khi app chạy vẫn an toàn nhờ WAL + `.backup`):

```bash
mkdir -p /srv/backups
sqlite3 /srv/storewweb/data/app.db ".backup '/srv/backups/app-$(date +%F).db'"
```

Cron hàng ngày:

```bash
sudo crontab -e
# 2:00 sáng mỗi ngày
0 2 * * * sqlite3 /srv/storewweb/data/app.db ".backup '/srv/backups/app-$(date +%F).db'" && find /srv/backups -name 'app-*.db' -mtime +14 -delete
```

Giữ backup 14 ngày. Nếu muốn backup thư mục upload, thêm `rsync -a /srv/storewweb/app/static/uploads /srv/backups/uploads/`.

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
