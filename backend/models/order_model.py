from config.db import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    total_amount = db.Column(db.Numeric(12, 2), nullable=False)

    payment_method = db.Column(db.String(50))


    created_at = db.Column(db.DateTime, default=datetime.utcnow)

