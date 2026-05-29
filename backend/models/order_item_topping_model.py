from config.db import db


class OrderItemTopping(db.Model):
    __tablename__ = "order_item_toppings"

    id = db.Column(db.Integer, primary_key=True)

    order_item_id = db.Column(
        db.Integer,
        db.ForeignKey("order_items.id", ondelete="CASCADE"),
        nullable=False,
    )

    topping_id = db.Column(
        db.Integer,
        db.ForeignKey("toppings.id", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        db.UniqueConstraint("order_item_id", "topping_id", name="unique_orderitem_topping"),
    )

