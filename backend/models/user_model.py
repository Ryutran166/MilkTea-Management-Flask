from config.db import db


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer,primary_key=True)

    branch_id = db.Column(db.Integer,nullable=True)

    username = db.Column(db.String(100),unique=True,nullable=False)

    password = db.Column(db.String(255),nullable=False)
    
    full_name = db.Column(db.String(100),nullable=False)

    phone = db.Column(db.String(20))

    role = db.Column(db.String(20),nullable=False)

    status = db.Column(db.Boolean,default=True)