from flask import Blueprint
from flask import request
from flask import jsonify

from flask_bcrypt import Bcrypt

from config.db import db
from models.user_model import User

auth_bp = Blueprint(
    "auth",
    __name__
)

bcrypt = Bcrypt()

# =====================================
# REGISTER
# =====================================

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name")
    phone = data.get("phone")
    role = data.get("role")

    # ==========================
    # Check username
    # ==========================

    existing_user = User.query.filter_by(
        username=username
    ).first()

    if existing_user:
        return jsonify({
            "success": False,
            "message": "Username already exists"
        }), 400

    # ==========================
    # Hash password
    # ==========================

    hashed_password = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    # ==========================
    # Create user
    # ==========================

    new_user = User(
        username=username,
        password=hashed_password,
        full_name=full_name,
        phone=phone,
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Register successfully"
    })


# =====================================
# LOGIN
# =====================================

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    # ==========================
    # Find user
    # ==========================

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    # ==========================
    # Check password
    # ==========================

    is_correct_password = bcrypt.check_password_hash(
        user.password,
        password
    )

    if not is_correct_password:
        return jsonify({
            "success": False,
            "message": "Wrong password"
        }), 401

    return jsonify({
        "success": True,
        "message": "Login successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role
        }
    })