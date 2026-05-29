from config.db import db
from datetime import datetime


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    # relationship defined in product_size_model / other modules to avoid circular imports

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    base_price = db.Column(db.Numeric(10, 2), nullable=False)

    image = db.Column(db.String(255))

    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

