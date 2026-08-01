import os

import click
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create tables and upsert the admin account (PLAT-04, D-01..D-04)."""
    from .models import AdminUser

    admin_password = os.environ.get('ADMIN_PASSWORD', '')
    if not admin_password.strip():
        raise click.ClickException('ADMIN_PASSWORD must be set in environment variables.')
    if admin_password.strip() == 'change-me':
        raise click.ClickException(
            'ADMIN_PASSWORD is still "change-me". Update .env with a real password before running init-db.'
        )
    if len(admin_password.strip()) < 8:
        raise click.ClickException('ADMIN_PASSWORD must be at least 8 non-whitespace characters.')

    admin_username = os.environ.get('ADMIN_USERNAME', 'admin').strip()

    db.create_all()

    user = AdminUser.query.filter_by(username=admin_username).first()
    if user:
        user.password_hash = generate_password_hash(admin_password)
        click.echo(f'Updated password for admin "{admin_username}".')
    else:
        db.session.add(AdminUser(username=admin_username, password_hash=generate_password_hash(admin_password)))
        click.echo(f'Created admin "{admin_username}".')
    db.session.commit()
