from config.db import db


class Topping(db.Model):
    __tablename__ = "toppings"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    status = db.Column(db.Boolean, default=True)

