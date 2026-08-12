**# StoreWeb

Web bán hàng tiếng Việt để trưng bày và quản lý sản phẩm. Backend Python Flask, tự host.
Đặt hàng qua giỏ hàng, theo dõi đơn và thống kê (v1.1).

## Cài đặt

1. Cài dependencies:
   ```
   python -m pip install -r requirements.txt
   ```

2. Tạo file `.env` từ `.env.example`:
   ```
   cp .env.example .env
   ```

3. Sinh `SECRET_KEY` và dán vào `.env`:
   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

4. Đặt `ADMIN_PASSWORD` trong `.env` (tối thiểu 8 ký tự, không phải `change-me`).

5. Khởi tạo cơ sở dữ liệu (tạo tài khoản admin):
   ```
   flask --app wsgi init-db
   ```

6. Chạy ứng dụng:
   ```
   flask --app wsgi run
   ```

Mở trình duyệt tại `http://127.0.0.1:5000` để xem trang chủ và `/login` để đăng nhập quản trị.
