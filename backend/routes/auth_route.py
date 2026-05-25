from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

from datetime import datetime
from datetime import timedelta

from config.db import db

from models.user_model import User
from models.refresh_token_model import RefreshToken

from utils.auth_utils import (
    hash_password,
    verify_password
)

from middlewares.auth_middleware import role_required
from models.branch_model import Branch

auth_bp = Blueprint(
    "auth_bp",
    __name__
)



# =========================
# REGISTER
# =========================

@auth_bp.route(
    "/auth/register",
    methods=["POST"]
)
def register():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name")
    phone = data.get("phone")
    role = data.get("role")

    existing_user = User.query.filter_by(
        username=username
    ).first()

    if existing_user:

        return jsonify({
            "success": False,
            "message": "Username already exists"
        }), 400

    hashed_password = hash_password(password)

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
        "message": "Register successful"
    })


# =========================
# LOGIN
# =========================

@auth_bp.route(
    "/auth/login",
    methods=["POST"]
)
def login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:

        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    is_valid = verify_password(
        password,
        user.password
    )

    if not is_valid:

        return jsonify({
            "success": False,
            "message": "Wrong password"
        }), 401

    access_token = create_access_token(
        identity=str(user.id)
    )

    refresh_token = create_refresh_token(
        identity=str(user.id)
    )

    refresh_token_db = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow()
        + timedelta(days=7)
    )

    db.session.add(refresh_token_db)

    db.session.commit()

    return jsonify({
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    })


# =========================
# REFRESH TOKEN
# =========================
@auth_bp.route(
    "/auth/refresh",
    methods=["POST"]
)
@jwt_required(refresh=True)
def refresh():

    refresh_token = request.headers.get(
        "Authorization"
    ).split(" ")[1]

    token_in_db = RefreshToken.query.filter_by(
        token=refresh_token
    ).first()

    if not token_in_db:

        return jsonify({
            "success": False,
            "message": "Refresh token not found"
        }), 401

    if token_in_db.is_revoked:

        return jsonify({
            "success": False,
            "message": "Refresh token revoked"
        }), 401

    if token_in_db.expires_at < datetime.utcnow():

        return jsonify({
            "success": False,
            "message": "Refresh token expired"
        }), 401

    current_user_id = get_jwt_identity()

    new_access_token = create_access_token(
        identity=current_user_id
    )

    return jsonify({
        "success": True,
        "access_token": new_access_token
    })


# =========================
# LOGOUT
# =========================

@auth_bp.route(
    "/auth/logout",
    methods=["POST"]
)
@jwt_required(refresh=True)
def logout():

    refresh_token = request.headers.get(
        "Authorization"
    ).split(" ")[1]

    token = RefreshToken.query.filter_by(
        token=refresh_token
    ).first()

    if token:

        token.is_revoked = True

        db.session.commit()

    return jsonify({
        "success": True,
        "message": "Logout successful"
    })


# =========================
# PROTECTED ROUTE
# =========================

@auth_bp.route(
    "/auth/profile",
    methods=["GET"]
)
@jwt_required()
def profile():

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": user.role
    })


# =========================
# GET CURRENT USER (ME)
# =========================

@auth_bp.route(
    "/auth/me",
    methods=["GET"]
)
@jwt_required()
def me():

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    return jsonify({
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role
    })


# =========================
# CHANGE PASSWORD
# =========================

@auth_bp.route(
    "/users",
    methods=["POST"]
)
@jwt_required()
@role_required(["admin"])
def create_user():

    data = request.get_json() or {}



    username = (data.get("username") or "").strip()
    password = data.get("password")
    full_name = (data.get("full_name") or "").strip()
    phone = (data.get("phone") or "").strip() or None
    role = (data.get("role") or "").strip()
    branch_id = data.get("branch_id")

    if not username or not password or not full_name or not role or branch_id is None:
        return jsonify({
            "success": False,
            "message": "Missing required fields: username, password, full_name, role, branch_id"
        }), 400

    if role not in ["manager", "staff"]:
        return jsonify({
            "success": False,
            "message": "Invalid role. Only 'manager' and 'staff' are allowed"
        }), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({
            "success": False,
            "message": "Username already exists"
        }), 400

    b = Branch.query.get(branch_id)
    if not b:
        return jsonify({
            "success": False,
            "message": "Branch not found"
        }), 404

    hashed_password = hash_password(password)

    new_user = User(
        username=username,
        password=hashed_password,
        full_name=full_name,
        phone=phone,
        role=role,
        branch_id=branch_id
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "User created successfully",
        "data": {
            "id": new_user.id,
            "username": new_user.username,
            "full_name": new_user.full_name,
            "phone": new_user.phone,
            "role": new_user.role,
            "branch_id": new_user.branch_id,
            "status": new_user.status,
        }
    }), 201


@auth_bp.route(
    "/users/<int:user_id>",
    methods=["GET"]
)
@jwt_required()
@role_required(["admin"])
def get_user_by_id(user_id: int):

    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "data": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role,
            "branch_id": user.branch_id,
            "status": user.status,
        }
    }), 200


@auth_bp.route(
    "/auth/change-password",
    methods=["PUT"]
)
@jwt_required()
def change_password():







    data = request.get_json() or {}

    old_password = data.get("old_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not old_password or not new_password or not confirm_password:
        return jsonify({
            "success": False,
            "message": "Missing required fields"
        }), 400

    if new_password != confirm_password:
        return jsonify({
            "success": False,
            "message": "New password and confirm password do not match"
        }), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    is_valid_old = verify_password(
        old_password,
        user.password
    )

    if not is_valid_old:
        return jsonify({
            "success": False,
            "message": "Wrong old password"
        }), 401

    user.password = hash_password(new_password)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Password changed successfully"
    }), 200


