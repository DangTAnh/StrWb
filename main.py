import os
import secrets
from pathlib import Path

from app import create_app


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'
ENV_EXAMPLE_PATH = BASE_DIR / '.env.example'
DATABASE_PATH = BASE_DIR / 'data' / 'app.db'


def ensure_env_file():
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text(encoding='utf-8').splitlines()
    elif ENV_EXAMPLE_PATH.exists():
        lines = ENV_EXAMPLE_PATH.read_text(encoding='utf-8').splitlines()
    else:
        lines = []

    secret_key = os.environ.get('SECRET_KEY', '').strip() or secrets.token_hex(32)
    for index, line in enumerate(lines):
        if line.startswith('SECRET_KEY='):
            if not line.split('=', 1)[1].strip():
                lines[index] = f'SECRET_KEY={secret_key}'
            break
    else:
        lines.append(f'SECRET_KEY={secret_key}')

    if not ENV_PATH.exists() or lines != ENV_PATH.read_text(encoding='utf-8').splitlines():
        ENV_PATH.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')


def load_env_file(path):
    if not path.exists():
        return

    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


if not DATABASE_PATH.exists():
    ensure_env_file()

load_env_file(ENV_PATH)

app = create_app()


def initialize_database_if_needed():
    if DATABASE_PATH.exists():
        return

    from app.db import init_db_command

    result = app.test_cli_runner().invoke(init_db_command)
    if result.exit_code != 0:
        raise RuntimeError(result.output.strip() or 'Database initialization failed.')


if __name__ == '__main__':
    initialize_database_if_needed()
    app.run(host='0.0.0.0', port=int(__import__('os').environ.get('PORT', 10990)))


