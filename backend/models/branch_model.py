from config.db import db
from datetime import datetime


class Branch(db.Model):
    __tablename__ = "branches"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)

    status = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

