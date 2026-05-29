from config.db import db
from datetime import datetime


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    size_id = db.Column(db.Integer, db.ForeignKey("sizes.id", ondelete="SET NULL"), nullable=True)

    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

    note = db.Column(db.Text)

    # Keep a created_at to be safe; original SQL doesn't define it.
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

