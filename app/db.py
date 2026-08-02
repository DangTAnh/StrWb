import os

import click
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
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

    # Migration guard (PLAT-05): create_all never ALTERs an existing table, so add
    # cost_price to v1.0 DBs manually. PRAGMA check makes this idempotent.
    with db.engine.begin() as conn:
        rows = conn.execute(text('PRAGMA table_info(products)')).fetchall()
        if not any(row[1] == 'cost_price' for row in rows):
            conn.execute(text('ALTER TABLE products ADD COLUMN cost_price INTEGER'))
            click.echo('Migrated: added products.cost_price (v1.0 -> v1.1).')

        # Orders guard (06-01 / ORD-10a): rebuild the legacy Phase 5 orders table
        # (snapshot columns on orders) into the customer-only schema. Only DROP when
        # the legacy table is empty — never destroy data.
        orders_exist = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")).fetchone()
        if orders_exist:
            ocols = [row[1] for row in conn.execute(text('PRAGMA table_info(orders)'))]
            if 'product_name' in ocols:
                order_count = conn.execute(text('SELECT COUNT(*) FROM orders')).scalar()
                if order_count > 0:
                    raise click.ClickException(
                        'Manual migration required: orders has legacy snapshot schema with data. '
                        'Migrate the data manually before running init-db.'
                    )
                conn.execute(text('DROP TABLE orders'))
                click.echo('Migrated: rebuilt orders table (legacy snapshot schema -> customer-only schema).')

    # Recreate the orders table (new schema) after the legacy DROP; no-op otherwise.
    db.create_all()

    user = AdminUser.query.filter_by(username=admin_username).first()
    if user:
        user.password_hash = generate_password_hash(admin_password)
        click.echo(f'Updated password for admin "{admin_username}".')
    else:
        db.session.add(AdminUser(username=admin_username, password_hash=generate_password_hash(admin_password)))
        click.echo(f'Created admin "{admin_username}".')
    db.session.commit()
