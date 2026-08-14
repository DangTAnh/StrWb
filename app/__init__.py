import os
import sqlite3
from datetime import datetime, timedelta, timezone

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine

from .db import db, init_db_command

login_manager = LoginManager()
csrf = CSRFProtect()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@event.listens_for(Engine, 'connect')
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable WAL + busy_timeout for SQLite (PLAT-03)."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA busy_timeout=30000')
        cursor.execute('PRAGMA foreign_keys=ON')  # enforce FK (ON DELETE SET NULL on orders.product_id)
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
        REMEMBER_COOKIE_DURATION=timedelta(days=30),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.environ.get('SESSION_COOKIE_SECURE', '').lower() in ('1', 'true', 'yes'),
        DEBUG=(os.environ.get('FLASK_DEBUG', '0') == '1'),
        MESSENGER_URL=os.environ.get('MESSENGER_URL', 'https://m.me/yourpage'),
    )
    app.json.ensure_ascii = False

    if not app.config['SECRET_KEY']:
        raise RuntimeError('SECRET_KEY must be set in environment variables. See .env.example.')

    db.init_app(app)
    from . import models  # noqa: F401

    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    app.cli.add_command(init_db_command, name='init-db')

    @app.context_processor
    def inject_year():
        cart = session.get('cart', {})
        total_qty = 0
        for qty in cart.values():
            try:
                total_qty += int(qty)
            except (TypeError, ValueError):
                pass
        return {
            'current_year': datetime.now(timezone.utc).year,
            'cart_total_quantity': total_qty,
            'cart_quantities': cart
        }

    @app.template_filter('format_price')
    def format_price(value):
        return f'{int(value):,}'.replace(',', '.') + '₫'

    @app.template_filter('strftime')
    def strftime(value, fmt):
        if value is None:
            return ''
        return value.strftime(fmt)

    from .public import public_bp
    from .auth import auth_bp
    from .admin import admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def too_large(e):
        flash('Tập tin quá lớn. Tối đa 16MB cho mỗi lần tải ảnh.', 'error')
        return redirect(request.referrer or url_for('admin.products'))

    @app.after_request
    def _cache_product_images(response):
        # IMG-CACHE: product uploads use UUID filenames — immutable, safe to cache forever.
        # Scoped to /static/uploads/ so CSS/JS (unversioned) keep their default short cache.
        # ponytail: 1y + immutable; if a UUID collision were ever to happen, bust via URL change.
        if request.path.startswith('/static/uploads/'):
            response.cache_control.public = True
            response.cache_control.max_age = 31536000
            response.cache_control.immutable = True
        return response

    return app
