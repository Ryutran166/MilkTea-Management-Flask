from flask import Blueprint
from flask import jsonify

from flask_jwt_extended import jwt_required

from middlewares.auth_middleware import role_required

test_bp = Blueprint(
    "test_bp",
    __name__
)


# =========================
# ADMIN ONLY
# =========================

@test_bp.route(
    "/admin-only",
    methods=["GET"]
)
@jwt_required()
@role_required(["admin"])
def admin_only():

    return jsonify({
        "success": True,
        "message": "Welcome admin"
    })


# =========================
# MANAGER ONLY
# =========================

@test_bp.route(
    "/manager-only",
    methods=["GET"]
)
@jwt_required()
@role_required(["manager"])
def manager_only():

    return jsonify({
        "success": True,
        "message": "Welcome manager"
    })


# =========================
# STAFF + ADMIN
# =========================

@test_bp.route(
    "/staff-admin",
    methods=["GET"]
)
@jwt_required()
@role_required([
    "staff",
    "admin"
])
def staff_admin():

    return jsonify({
        "success": True,
        "message": "Welcome staff/admin"
    })