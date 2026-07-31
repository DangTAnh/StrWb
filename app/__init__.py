import os
import sqlite3
from datetime import timedelta

from flask import Flask
from sqlalchemy import event
from sqlalchemy.engine import Engine

from .db import db, init_db_command

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@event.listens_for(Engine, 'connect')
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable WAL + busy_timeout for SQLite (PLAT-03)."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA busy_timeout=30000')
        cursor.close()


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(BASE_DIR, 'data', 'app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={'connect_args': {'timeout': 30}},
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        PERMANENT_SESSION_LIFETIME=timedelta(days=30),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=(os.environ.get('FLASK_ENV') == 'production'),
        DEBUG=(os.environ.get('FLASK_DEBUG', '0') == '1'),
        MESSENGER_URL=os.environ.get('MESSENGER_URL', 'https://m.me/yourpage'),
    )
    app.json.ensure_ascii = False

    if not app.config['SECRET_KEY']:
        raise RuntimeError('SECRET_KEY must be set in environment variables. See .env.example.')

    db.init_app(app)
    from . import models  # noqa: F401

    app.cli.add_command(init_db_command, name='init-db')

    from .public import public_bp
    from .auth import auth_bp
    from .admin import admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    return app
