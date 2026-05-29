from flask import Blueprint, request, jsonify

from flask_jwt_extended import jwt_required, get_jwt_identity

from middlewares.auth_middleware import role_required

from config.db import db
from models.branch_model import Branch
from models.user_model import User


branches_bp = Blueprint(
    "branches_bp",
    __name__
)


def _get_request_json():
    return request.get_json() or {}


# =========================
# READ: admin/manager/staff
# =========================

@branches_bp.route("/branches", methods=["GET"])
@jwt_required()
@role_required(["admin", "manager", "staff"])
def list_branches():
    branches = Branch.query.order_by(Branch.id.desc()).all()

    return jsonify({
        "success": True,
        "data": [
            {
                "id": b.id,
                "name": b.name,
                "phone": b.phone,
                "address": b.address,
                "status": b.status,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in branches
        ]
    })


@branches_bp.route("/branches/<int:branch_id>", methods=["GET"])
@jwt_required()
@role_required(["admin", "manager", "staff"])
def get_branch(branch_id: int):
    b = Branch.query.get(branch_id)
    if not b:
        return jsonify({
            "success": False,
            "message": "Branch not found"
        }), 404

    return jsonify({
        "success": True,
        "data": {
            "id": b.id,
            "name": b.name,
            "phone": b.phone,
            "address": b.address,
            "status": b.status,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
    })


# =========================
# WRITE: admin only
# =========================

@branches_bp.route("/branches", methods=["POST"])
@jwt_required()
@role_required(["admin"])
def create_branch():
    data = _get_request_json()

    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip() or None
    address = (data.get("address") or "").strip() or None

    status = data.get("status", True)
    # ensure bool-ish
    if isinstance(status, str):
        status = status.lower() in ["true", "1", "yes", "y"]

    if not name:
        return jsonify({
            "success": False,
            "message": "Missing required field: name"
        }), 400

    b = Branch(name=name, phone=phone, address=address, status=status)
    db.session.add(b)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Branch created successfully",
        "data": {
            "id": b.id,
            "name": b.name,
            "phone": b.phone,
            "address": b.address,
            "status": b.status,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
    }), 201


@branches_bp.route("/branches/<int:branch_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin"])
def update_branch(branch_id: int):
    b = Branch.query.get(branch_id)
    if not b:
        return jsonify({
            "success": False,
            "message": "Branch not found"
        }), 404

    data = _get_request_json()

    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({
                "success": False,
                "message": "Field 'name' cannot be empty"
            }), 400
        b.name = name

    if "phone" in data:
        phone = (data.get("phone") or "").strip() or None
        b.phone = phone

    if "address" in data:
        address = (data.get("address") or "").strip() or None
        b.address = address

    if "status" in data:
        status = data.get("status")
        if isinstance(status, str):
            status = status.lower() in ["true", "1", "yes", "y"]
        b.status = bool(status)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Branch updated successfully",
        "data": {
            "id": b.id,
            "name": b.name,
            "phone": b.phone,
            "address": b.address,
            "status": b.status,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
    })


@branches_bp.route("/branches/<int:branch_id>/status", methods=["PATCH"])
@jwt_required()
@role_required(["admin"])
def toggle_branch_status(branch_id: int):
    b = Branch.query.get(branch_id)
    if not b:
        return jsonify({
            "success": False,
            "message": "Branch not found"
        }), 404

    b.status = not b.status
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Branch status updated successfully",
        "data": {
            "id": b.id,
            "status": b.status,
        }
    })


@branches_bp.route("/branches/<int:branch_id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_branch(branch_id: int):
    b = Branch.query.get(branch_id)
    if not b:
        return jsonify({
            "success": False,
            "message": "Branch not found"
        }), 404

    # Không cho xóa chi nhánh khi còn nhân viên đang hoạt động (User.status=True)
    active_staff_count = User.query.filter_by(branch_id=branch_id, status=True).count()
    if active_staff_count > 0:
        return jsonify({
            "success": False,
            "message": "Cannot delete branch because it still has active employees",
            "active_staff_count": active_staff_count
        }), 409

    db.session.delete(b)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Branch deleted successfully"
    })



