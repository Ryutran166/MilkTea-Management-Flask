from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from config.db import db
from middlewares.auth_middleware import role_required
from models.size_model import Size
from models.product_size_model import ProductSize

sizes_bp = Blueprint(
    "sizes_bp",
    __name__,
)


def _get_request_json():
    return request.get_json(silent=True) or {}


def _json_error(message, status_code=400, **extra):
    payload = {"success": False, "message": message}
    payload.update(extra)
    return jsonify(payload), status_code


def _normalize_name(name):
    if name is None:
        return ""
    return str(name).strip()


# =========================
# READ: admin/manager/staff
# =========================


@sizes_bp.route("/sizes", methods=["GET"])
@jwt_required()
@role_required(["admin", "manager", "staff"])
def list_sizes():
    sizes = Size.query.order_by(Size.id.desc()).all()

    return jsonify(
        {
            "success": True,
            "data": [
                {
                    "id": s.id,
                    "name": s.name,
                    "extra_price": str(s.extra_price) if s.extra_price is not None else None,
                }

                for s in sizes
            ],
        }
    )


@sizes_bp.route("/sizes/<int:size_id>", methods=["GET"])
@jwt_required()
@role_required(["admin", "manager", "staff"])
def get_size(size_id: int):
    s = Size.query.get(size_id)
    if not s:
        return _json_error("Size not found", 404)

    return jsonify(
        {
            "success": True,
            "data": {
                "id": s.id,
                "name": s.name,
                "extra_price": str(s.extra_price) if s.extra_price is not None else None,
            },

        }
    )


# =========================
# WRITE: admin/manager
# =========================


@sizes_bp.route("/sizes", methods=["POST"])
@jwt_required()
@role_required(["admin", "manager"])
def create_size():
    data = _get_request_json()

    name = _normalize_name(data.get("name"))
    if not name:
        return _json_error("Missing required field: name", 400)

    extra_price = data.get("extra_price", 0)

    # Validate unique name (case-insensitive)
    exists = (
        Size.query.filter(func.lower(Size.name) == func.lower(name)).first()
    )
    if exists:
        return _json_error("Size name already exists", 409)

    try:
        s = Size(
            name=name,
            extra_price=extra_price,
        )

        db.session.add(s)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Size created successfully",
                    "data": {
                        "id": s.id,
                        "name": s.name,
                    "extra_price": str(s.extra_price) if s.extra_price is not None else None,

                    },
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to create size", 500, detail=str(e))


@sizes_bp.route("/sizes/<int:size_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin", "manager"])
def update_size(size_id: int):
    s = Size.query.get(size_id)
    if not s:
        return _json_error("Size not found", 404)

    data = _get_request_json()

    if "name" in data:
        new_name = _normalize_name(data.get("name"))
        if not new_name:
            return _json_error("Field 'name' cannot be empty", 400)

        conflict = (
            Size.query.filter(func.lower(Size.name) == func.lower(new_name))
            .filter(Size.id != size_id)
            .first()
        )
        if conflict:
            return _json_error("Size name already exists", 409)

        s.name = new_name

    if "extra_price" in data:
        s.extra_price = data.get("extra_price", 0)



    try:
        db.session.commit()
        return jsonify(
            {
                "success": True,
                "message": "Size updated successfully",
                "data": {
                    "id": s.id,
                    "name": s.name,
                    "extra_price": str(s.extra_price) if s.extra_price is not None else None,
                },
            }
        )
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to update size", 500, detail=str(e))


# =========================
# DELETE: admin only
# =========================


@sizes_bp.route("/sizes/<int:size_id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_size(size_id: int):
    s = Size.query.get(size_id)
    if not s:
        return _json_error("Size not found", 404)

    used_count = ProductSize.query.filter_by(size_id=size_id).count()
    if used_count > 0:
        return _json_error(
            "Cannot delete size because it is used by products",
            409,
            used_product_sizes_count=used_count,
        )

    try:
        db.session.delete(s)
        db.session.commit()
        return jsonify({"success": True, "message": "Size deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to delete size", 500, detail=str(e))

