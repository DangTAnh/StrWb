from datetime import datetime, timezone

from flask_login import UserMixin

from .db import db


def utcnow():
    """Timezone-aware UTC now (datetime.utcnow is deprecated in 3.12+)."""
    return datetime.now(timezone.utc)


class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)  # VND, Integer only (D-05; never Float)
    brand = db.Column(db.String(100), nullable=True)
    measurements = db.Column(db.Text, nullable=True)  # D-07 free text, e.g. "60x40x2cm" or "M / L / XL"
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    discontinued = db.Column(db.Boolean, default=False, nullable=False)  # D-08 override
    sku = db.Column(db.String(100), nullable=True)          # D-06 optional
    sort_order = db.Column(db.Integer, default=0, nullable=False)  # D-06 optional
    admin_note = db.Column(db.Text, nullable=True)          # D-06 optional, admin-only
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    images = db.relationship('ProductImage', backref='product', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def status(self):
        """D-08: discontinued overrides; else available if in stock, else out_of_stock."""
        if self.discontinued:
            return 'discontinued'
        return 'available' if self.quantity > 0 else 'out_of_stock'

    @property
    def primary_image(self):
        """First image in gallery order = primary (D-12)."""
        return self.images.order_by(ProductImage.sort_order.asc()).first()


class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # UUID filesystem name, set by image_utils
    original_filename = db.Column(db.String(255), nullable=True)  # user's Vietnamese name, display only (D-16)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)  # gallery position; 0 = first = primary (D-12/D-13)
    created_at = db.Column(db.DateTime, default=utcnow)

    @property
    def thumb_filename(self):
        """Derived thumb asset name: <uuid>_thumb.jpg alongside <uuid>.jpg (IMG-04)."""
        if not self.filename or not self.filename.endswith('.jpg'):
            return None
        return self.filename[:-4] + '_thumb.jpg'
