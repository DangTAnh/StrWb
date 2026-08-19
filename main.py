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


if __name__ == "__main__":
    main()
