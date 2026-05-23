from config.db import db
from datetime import datetime


class RefreshToken(db.Model):

    __tablename__ = "refresh_tokens"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    token = db.Column(
        db.Text,
        nullable=False
    )

    is_revoked = db.Column(
        db.Boolean,
        default=False
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )