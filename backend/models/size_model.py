from config.db import db
from datetime import datetime


class Size(db.Model):
    __tablename__ = "sizes"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(10), nullable=False, unique=True)
    extra_price = db.Column(db.Numeric(10, 2), default=0)
   

