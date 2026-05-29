from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from config.db import db
from middlewares.auth_middleware import role_required
from models.topping_model import Topping


toppings_bp = Blueprint(
    "toppings_bp",
    __name__,
)


def _parse_boolish(value):
    if isinstance(value, str):
        return value.strip().lower() in ["true", "1", "yes", "y", "on"]
    return bool(value)


def _json_error(message, status_code=400, **extra):
    payload = {"success": False, "message": message}
    payload.update(extra)
    return jsonify(payload), status_code


def _get_request_int(name: str, default=None):
    raw = request.args.get(name, None)
    if raw is None:
        return default
    raw = str(raw).strip()
    if raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"{name} must be an integer")


def _normalize_name(name):
    if name is None:
        return ""
    return str(name).strip()


@toppings_bp.route("/toppings", methods=["GET"])
@jwt_required()
@role_required(["admin", "manager", "staff"])
def list_toppings():
    status = request.args.get("status", None)

    query = Topping.query

    if status is not None and str(status).strip() != "":
        try:
            status_bool = _parse_boolish(status)
        except Exception:
            return _json_error("status must be a boolean", 400)
        query = query.filter(Topping.status == status_bool)

    items = query.order_by(Topping.id.desc()).all()

    return jsonify(
        {
            "success": True,
            "data": [
                {
                    "id": t.id,
                    "name": t.name,
                    "price": str(t.price) if t.price is not None else None,
                    "status": t.status,
                }
                for t in items
            ],
        }
    )


@toppings_bp.route("/toppings", methods=["POST"])
@jwt_required()
@role_required(["admin", "manager"])
def create_topping():
    data = request.get_json(silent=True) or {}

    name = _normalize_name(data.get("name"))
    if not name:
        return _json_error("Missing required field: name", 400)

    price = data.get("price", None)
    if price is None:
        return _json_error("Missing required field: price", 400)

    # validate numeric price by converting to string/decimal-friendly
    try:
        price_val = str(price)
    except Exception:
        return _json_error("price must be a valid number", 400)

    exists = (
        Topping.query.filter(func.lower(Topping.name) == func.lower(name)).first()
    )
    if exists:
        return _json_error("Topping name already exists", 409)

    try:
        t = Topping(name=name, price=price_val, status=True)
        db.session.add(t)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Topping created successfully",
                    "data": {
                        "id": t.id,
                        "name": t.name,
                        "price": str(t.price) if t.price is not None else None,
                        "status": t.status,
                    },
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to create topping", 500, detail=str(e))


@toppings_bp.route("/toppings/<int:topping_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin", "manager"])
def update_topping(topping_id: int):
    t = Topping.query.get(topping_id)
    if not t:
        return _json_error("Topping not found", 404)

    data = request.get_json(silent=True) or {}

    # PUT không yêu cầu đủ cả 2 giá trị
    # Client có thể gửi: {"name": ...} hoặc {"price": ...} hoặc cả hai.

    new_name = None
    new_price = None

    if "name" in data:
        new_name = _normalize_name(data.get("name"))
        if not new_name:
            return _json_error("Field 'name' cannot be empty", 400)

        conflict = (
            Topping.query.filter(func.lower(Topping.name) == func.lower(new_name))
            .filter(Topping.id != topping_id)
            .first()
        )
        if conflict:
            return _json_error("Topping name already exists", 409)

    if "price" in data:
        new_price = data.get("price", None)
        if new_price is None:
            return _json_error("Field 'price' cannot be null", 400)

    if new_name is None and new_price is None:
        return _json_error("At least one of fields 'name' or 'price' must be provided", 400)

    try:
        if new_name is not None:
            t.name = new_name
        if new_price is not None:
            t.price = str(new_price)
        db.session.commit()


        return jsonify(
            {
                "success": True,
                "message": "Topping updated successfully",
                "data": {
                    "id": t.id,
                    "name": t.name,
                    "price": str(t.price) if t.price is not None else None,
                    "status": t.status,
                },
            }
        )
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to update topping", 500, detail=str(e))


@toppings_bp.route("/toppings/<int:topping_id>/status", methods=["PATCH"])
@jwt_required()
@role_required(["admin", "manager"])
def toggle_topping_status(topping_id: int):
    t = Topping.query.get(topping_id)
    if not t:
        return _json_error("Topping not found", 404)

    t.status = not t.status

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to update topping status", 500, detail=str(e))

    return jsonify(
        {
            "success": True,
            "message": "Topping status updated successfully",
            "data": {
                "id": t.id,
                "status": t.status,
            },
        }
    )


@toppings_bp.route("/toppings/<int:topping_id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin", "manager"])
def delete_topping(topping_id: int):
    t = Topping.query.get(topping_id)
    if not t:
        return _json_error("Topping not found", 404)

    try:
        db.session.delete(t)
        db.session.commit()
        return jsonify(
            {
                "success": True,
                "message": "Topping deleted successfully",
            }
        )
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to delete topping", 500, detail=str(e))




