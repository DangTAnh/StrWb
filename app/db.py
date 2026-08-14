import os

import click
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case, text, update as sa_update
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


def resequence_product_ids():
    """Close gaps in products.id (1,2,4,5 -> 1,2,3,4) and re-point child FKs.

    ponytail: renumbering PKs is destructive, so this is a no-op unless gaps exist.
    Runs in a FK-disabled transaction; child FKs (ProductImage, OrderItem) are
    remapped first. Negative temp ids buffer the in-place swap so no two rows ever
    share an id mid-update. Auto SKUs ('#<id>') are realigned to the new id;
    manually-typed SKUs are preserved (SKU-01 rule).
    """
    from .models import OrderItem, Product, ProductImage

    ids = [r[0] for r in db.session.query(Product.id).order_by(Product.id.asc()).all()]
    n = len(ids)
    if n == 0 or ids == list(range(1, n + 1)):
        return 0  # already contiguous — touch nothing

    mapping = {old: new for new, old in enumerate(ids, 1)}

    conn = db.session.connection()
    prev_fk = conn.exec_driver_sql('PRAGMA foreign_keys').scalar()
    conn.exec_driver_sql('PRAGMA foreign_keys=OFF')
    try:
        for old, new in mapping.items():
            if new == old:
                continue
            # 1. re-point children to negative temp
            db.session.execute(
                sa_update(ProductImage).where(ProductImage.product_id == old).values(product_id=-new)
            )
            db.session.execute(
                sa_update(OrderItem).where(OrderItem.product_id == old).values(product_id=-new)
            )
            # 2. move parent to negative temp
            db.session.execute(sa_update(Product).where(Product.id == old).values(id=-old))
        for old, new in mapping.items():
            if new == old:
                continue
            # 3. flip children back to positive new id
            db.session.execute(
                sa_update(ProductImage).where(ProductImage.product_id == -new).values(product_id=new)
            )
            db.session.execute(
                sa_update(OrderItem).where(OrderItem.product_id == -new).values(product_id=new)
            )
            # 4. flip parent back to positive new id; realign auto SKU
            db.session.execute(
                sa_update(Product)
                .where(Product.id == -old)
                .values(id=new, sku=case((Product.sku == f'#{old}', f'#{new}'), else_=Product.sku))
            )
        db.session.commit()
    finally:
        conn.exec_driver_sql(f'PRAGMA foreign_keys={"ON" if prev_fk else "OFF"}')
    return n
