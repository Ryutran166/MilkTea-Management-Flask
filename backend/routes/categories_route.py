from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from sqlalchemy import func

from config.db import db
from models.category_model import Category
from models.product_model import Product

from middlewares.auth_middleware import role_required


categories_bp = Blueprint(
    "categories_bp",
    __name__,
)


def _json_error(message, status_code=400, **extra):
    payload = {"success": False, "message": message}
    payload.update(extra)
    return jsonify(payload), status_code


def _get_request_json():
    return request.get_json(silent=True) or {}


def _normalize_name(name):
    if name is None:
        return ""
    return str(name).strip()


@categories_bp.route("/categories", methods=["GET"])
@jwt_required()
@role_required(["admin", "manager", "staff"])
def list_categories():
    categories = Category.query.order_by(Category.id.desc()).all()

    return jsonify(
        {
            "success": True,
            "data": [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in categories
            ],
        }
    )


@categories_bp.route("/categories", methods=["POST"])
@jwt_required()
@role_required(["admin", "manager"])
def create_category():
    data = _get_request_json()

    name = _normalize_name(data.get("name"))
    description = (data.get("description") or None)

    if not name:
        return _json_error("Missing required field: name", 400)

    # Validate unique name (case-insensitive)
    exists = (
        Category.query.filter(func.lower(Category.name) == func.lower(name)).first()
    )
    if exists:
        return _json_error("Category name already exists", 409)

    try:
        c = Category(name=name, description=description)
        db.session.add(c)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Category created successfully",
                    "data": {
                        "id": c.id,
                        "name": c.name,
                        "description": c.description,
                        "created_at": c.created_at.isoformat() if c.created_at else None,
                    },
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to create category", 500, detail=str(e))


@categories_bp.route("/categories/<int:category_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin", "manager"])
def update_category(category_id: int):
    c = Category.query.get(category_id)
    if not c:
        return _json_error("Category not found", 404)

    data = _get_request_json()

    if "name" in data:
        new_name = _normalize_name(data.get("name"))
        if not new_name:
            return _json_error("Field 'name' cannot be empty", 400)

        if (
            Category.query.filter(func.lower(Category.name) == func.lower(new_name))
            .filter(Category.id != category_id)
            .first()
        ):
            return _json_error("Category name already exists", 409)

        c.name = new_name

    if "description" in data:
        c.description = data.get("description") or None

    try:
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Category updated successfully",
                "data": {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                },
            }
        )
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to update category", 500, detail=str(e))


@categories_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_category(category_id: int):
    c = Category.query.get(category_id)
    if not c:
        return _json_error("Category not found", 404)

    used_count = Product.query.filter_by(category_id=category_id).count()
    if used_count > 0:
        return _json_error(
            "Cannot delete category because it is used by products",
            409,
            used_products_count=used_count,
        )

    try:
        db.session.delete(c)
        db.session.commit()
        return jsonify({"success": True, "message": "Category deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to delete category", 500, detail=str(e))

