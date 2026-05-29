from config.db import db


class ProductSize(db.Model):
    __tablename__ = "product_sizes"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    size_id = db.Column(db.Integer, db.ForeignKey("sizes.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("product_id", "size_id", name="unique_product_size"),
    )

