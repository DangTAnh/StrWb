#!/usr/bin/env python3
"""Kiểm tra thư mục data/uploads tồn tại; clone bản latest từ GitHub nếu thiếu.

Chạy:  python main.py [thư_mục_đích_mặc_định_.]

- Nếu thư mục đích chưa có `.git` → clone https://github.com/DangTAnh/StrWb vào đó.
- Nếu đã có → pull --ff-only để lấy bản latest (không rebase/merge phức tạp).
- Kiểm tra data/ và uploads/ tồn tại sau khi clone, tạo nếu thiếu.
"""
import os
import subprocess
import sys

REPO_URL = "https://github.com/DangTAnh/StrWb.git"
# ponytail: uploads thực nằm ở app/static/uploads (xem cấu trúc dự án). data/ ở root.
DATA_DIRS = ("data", "app/static/uploads")
# port + debug mặc định; ghi đè qua env FLASK_PORT / FLASK_DEBUG.
PORT = int(os.environ.get("FLASK_PORT", "10990"))
DEBUG = os.environ.get("FLASK_DEBUG", "0") in ("1", "true", "yes")


def run(cmd, cwd=None):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def ensure_dir(path):
    if os.path.isdir(path):
        print(f"[OK] tồn tại: {path}")
        return True
    os.makedirs(path, exist_ok=True)
    print(f"[CREATED] {path}")
    return False


def main():
    # Windows console mặc định cp1252 — ép stdout utf-8 để in được tiếng Việt.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass  # Python < 3.7 không có reconfigure; chấp nhận constraints.
    dest = sys.argv[1] if len(sys.argv) > 1 else "."
    dest = os.path.abspath(dest)

    if not os.path.isdir(dest):
        os.makedirs(dest, exist_ok=True)
        print(f"[CREATED] thư mục đích: {dest}")

    git_dir = os.path.join(dest, ".git")
    # ponytail: nếu dest đã có app package đầy đủ → chỉ pull. Nếu thiếu (panel upload
    # mỗi main.py/.env) → clone sparse vào temp (bỏ node_modules + ảnh uploads cho
    # nhẹ) rồi merge sang dest, giữ .env/data/uploads.
    app_init = os.path.join(dest, "app", "__init__.py")
    if os.path.isdir(git_dir):
        print(f"[PULL] lấy bản latest trong {dest}")
        r = run(["git", "pull", "--ff-only"], cwd=dest)
        print(r.stdout)
        if r.returncode != 0:
            print(r.stderr)
            sys.exit(f"[FAIL] pull thất bại (exit {r.returncode}). Có commit local? Thử stash/push.")
    elif os.path.isfile(app_init):
        # ponytail: code đầy đủ nhưng không phải git repo (deploy thủ công) — giữ nguyên.
        print(f"[SKIP] {dest} đã có code app/ — bỏ qua clone, giữ code hiện có.")
    else:
        # clone repo vào dest. dest có sẵn main.py/.env → git clone sẽ fail.
        # ponytail: repo upstream lỡ commit node_modules + ảnh uploads (2858 files).
        # Dùng sparse-checkout bỏ 2 thư mục đó (nhẹ + ít lỗi hơn). Clone tạm vào
        # dest/.strwb_clone (KHÔNG vào /tmp — /tmp trên panel có thể noexec/hạn chế ghi).
        import shutil
        print(f"[CLONE] {REPO_URL} → dest/.strwb_clone (sparse, merge)")
        tmp = os.path.join(dest, ".strwb_clone")
        shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp, exist_ok=True)
        r = run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", REPO_URL, tmp])
        print(r.stdout)
        if r.returncode != 0:
            print(r.stderr)
            shutil.rmtree(tmp, ignore_errors=True)
            sys.exit(f"[FAIL] clone thất bại (exit {r.returncode}).")
        # exclude node_modules + ảnh sản phẩm uploads (giữ app/static/uploads/ trỗng).
        r2 = run(["git", "sparse-checkout", "set", "--no-cone",
                  "/*", "!/node_modules", "!/app/static/uploads"], cwd=tmp)
        if r2.returncode != 0:
            print(r2.stderr)
            shutil.rmtree(tmp, ignore_errors=True)
            sys.exit(f"[FAIL] sparse-checkout thất bại (exit {r2.returncode}).")
        # giữ lại các file deploy-specific của dest trước khi đè.
        keep = {".env": None, "data": None, "app/static/uploads": None}
        for name in list(keep):
            p = os.path.join(dest, name)
            if os.path.exists(p):
                bak = os.path.join(dest, ".strwb_keep_" + name.replace("/", "_"))
                shutil.rmtree(bak, ignore_errors=True)
                os.makedirs(bak, exist_ok=True)
                shutil.move(p, os.path.join(bak, name))
                keep[name] = bak
        # đè toàn bộ nội dung repo (đã sparse) vào dest (trừ .git).
        for entry in os.listdir(tmp):
            if entry == ".git":
                continue
            src = os.path.join(tmp, entry)
            dst = os.path.join(dest, entry)
            if os.path.isdir(src):
                shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        # hồi sinh file đã giữ.
        for name, bak in keep.items():
            if bak:
                os.makedirs(os.path.dirname(os.path.join(dest, name)), exist_ok=True)
                shutil.move(os.path.join(bak, name), os.path.join(dest, name))
                shutil.rmtree(bak, ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)
        # ponytail: cũng xóa các bak dir đã tạo trong dest.
        for bak in keep.values():
            if bak:
                shutil.rmtree(bak, ignore_errors=True)
        print(f"[OK] merge repo vào {dest} (đã giữ .env/data/uploads, bỏ node_modules/ảnh).")
    print("--- kiểm tra thư mục dữ liệu ---")
    for d in DATA_DIRS:
        full = os.path.join(dest, d) if dest != os.getcwd() else d
        ensure_dir(full)
    print("[DONE] tất cả thư mục đã sẵn sàng.")


def _seed_env(dest):
    """Tạo .env default an toàn nếu thiếu (deploy web panel không kèm .env).

    Secrets sinh random một lần và ghi cố định — không regenerate mỗi restart,
    иначе session invalid liên tục + admin không biết mật khẩu.
    Admin đổi ADMIN_PASSWORD sau khi đăng nhập lần đầu.
    """
    import secrets
    env_path = os.path.join(dest, ".env")
    if os.path.isfile(env_path):
        return env_path
    secret = secrets.token_hex(32)
    # ponytail: default password cố định + cảnh báo rõ ranh giới bảo mật — không generate
    # random vì admin cần biết để đăng nhập lần đầu. Bắt buộc đổi sau.
    default_pw = "change-me-now"
    content = (
        "# Tự sinh bởi main.py khi deploy thiếu .env. Đổi giá trị rồi restart.\n"
        f"SECRET_KEY={secret}\n"
        "ADMIN_USERNAME=admin\n"
        f"ADMIN_PASSWORD={default_pw}\n"
        "MESSENGER_URL=https://m.me/yourpage\n"
        "SESSION_COOKIE_SECURE=false\n"
        "FLASK_DEBUG=0\n"
    )
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[CREATED] {env_path} — SECRET_KEY random, ADMIN_PASSWORD='{default_pw}' (ĐỔI NGAY sau đăng nhập).")
    return env_path


def load_env(dest):
    """Nạp .env vào os.environ — SECRET_KEY bắt buộc để create_app chạy."""
    env_path = os.path.join(dest, ".env")
    if not os.path.isfile(env_path):
        env_path = _seed_env(dest)
    for line in open(env_path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip()
        # ponytail: không ghi đè env đã set sẵn (qua shell) — ưu tiên ngoài cao hơn .env.
        if key and key not in os.environ:
            os.environ[key] = val
    print(f"[OK] nạp .env: {env_path}")


def run_web(dest):
    """Khởi động Flask dev server (tạo app + init-db nếu DB thiếu, rồi app.run)."""
    # cd vào dest để import app + .env đúng đường dẫn.
    os.chdir(dest)
    sys.path.insert(0, dest)
    if "PYTHONPATH" in os.environ:
        # đã trong path
        pass
    load_env(dest)

    from app import create_app
    app = create_app()

    # init-db tự động nếu data/app.db thiếu (tạo bảng + admin).
    db_path = os.path.join(dest, "data", "app.db")
    if not os.path.isfile(db_path):
        print(f"[INIT-DB] {db_path} chưa có — chạy init-db...")
        from app.db import init_db_command
        # ponytail: gọi click command trực tiếp không cần CLI runner phức tạp.
        try:
            from click.testing import CliRunner
            r = CliRunner().invoke(init_db_command, catch_exceptions=False)
            print(r.output)
            if r.exit_code != 0:
                sys.exit(f"[FAIL] init-db exit {r.exit_code}.")
        except SystemExit as e:
            print(e)
            sys.exit(1)
    else:
        print(f"[OK] DB tồn tại: {db_path}")

    print(f"[RUN] http://0.0.0.0:{PORT}/  (debug={DEBUG})")
    # ponytail: use_reloader=False để tránh spawn 2 tiến trình + đụng WAL. Bật reloader
    # riêng qua FLASK_DEBUG=1 nếu cần auto-reload khi sửa code.
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG, use_reloader=DEBUG)


if __name__ == "__main__":
    main()
    dest = sys.argv[1] if len(sys.argv) > 1 else "."
    run_web(dest)
