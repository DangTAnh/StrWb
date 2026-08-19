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
PORT = int(os.environ.get("FLASK_PORT", "5000"))
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
    if not os.path.isdir(git_dir):
        print(f"[CLONE] {REPO_URL} → {dest}")
        r = run(["git", "clone", REPO_URL, dest])
        print(r.stdout)
        if r.returncode != 0:
            print(r.stderr)
            sys.exit(f"[FAIL] clone thất bại (exit {r.returncode}).")
    else:
        print(f"[PULL] lấy bản latest trong {dest}")
        r = run(["git", "pull", "--ff-only"], cwd=dest)
        print(r.stdout)
        if r.returncode != 0:
            print(r.stderr)
            sys.exit(f"[FAIL] pull thất bại (exit {r.returncode}). Có commit local? Thử stash/push.")

    print("--- kiểm tra thư mục dữ liệu ---")
    for d in DATA_DIRS:
        full = os.path.join(dest, d) if dest != os.getcwd() else d
        ensure_dir(full)
    print("[DONE] tất cả thư mục đã sẵn sàng.")


def load_env(dest):
    """Nạp .env (nếu có) vào os.environ — SECRET_KEY bắt buộc để create_app chạy."""
    env_path = os.path.join(dest, ".env")
    if not os.path.isfile(env_path):
        sys.exit(f"[FAIL] không tìm thấy {env_path}. Tạo từ .env.example rồi điền SECRET_KEY/ADMIN_PASSWORD.")
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

    print(f"[RUN] http://127.0.0.1:{PORT}/  (debug={DEBUG})")
    # ponytail: use_reloader=False để tránh spawn 2 tiến trình + đụng WAL. Bật reloader
    # riêng qua FLASK_DEBUG=1 nếu cần auto-reload khi sửa code.
    app.run(host="127.0.0.1", port=PORT, debug=DEBUG, use_reloader=DEBUG)


if __name__ == "__main__":
    main()
    dest = sys.argv[1] if len(sys.argv) > 1 else "."
    run_web(dest)
