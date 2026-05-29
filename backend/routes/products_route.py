from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from config.db import db
from models.product_model import Product
from models.product_size_model import ProductSize
from models.size_model import Size
from models.topping_model import Topping
from models.category_model import Category
from models.order_item_model import OrderItem

# Tồn tại bảng product_toppings trong SQL, nhưng hiện chưa có model trong backend.
# Vì vậy dùng SQLAlchemy text để đọc/ghi trực tiếp bảng này.
from sqlalchemy import text

from middlewares.auth_middleware import role_required

products_bp = Blueprint(
    "products_bp",
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


def _get_pagination():
    # default: page=1, page_size=10
    page = request.args.get("page", "1")
    page_size = request.args.get("page_size", "10")

    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        page = 1
        page_size = 10

    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    if page_size > 100:
        page_size = 100

    return page, page_size


def _product_to_dict_basic(p):
    return {
        "id": p.id,
        "category_id": p.category_id,
        "name": p.name,
        "description": p.description,
        "base_price": str(p.base_price) if p.base_price is not None else None,
        "image": p.image,
        "status": p.status,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


def _get_product_sizes(product_id: int):
    rows = (
        db.session.query(ProductSize, Size)
        .join(Size, ProductSize.size_id == Size.id)
        .filter(ProductSize.product_id == product_id)
        .order_by(Size.id.asc())
        .all()
    )

    sizes = [
        {
            "id": size.id,
            "name": size.name,
            "extra_price": str(size.extra_price) if size.extra_price is not None else None,
            
        }
        for _ps, size in rows
    ]
    size_ids = [s["id"] for s in sizes]
    return sizes, size_ids


def _get_product_toppings(product_id: int):
    # product_toppings(product_id, topping_id)
    q = text(
        """
        SELECT t.id, t.name, t.price, t.status
        FROM product_toppings pt
        JOIN toppings t ON t.id = pt.topping_id
        WHERE pt.product_id = :product_id
        ORDER BY t.id ASC
        """
    )
    rows = db.session.execute(q, {"product_id": product_id}).fetchall()

    return [
        {
            "id": r.id,
            "name": r.name,
            "price": str(r.price) if r.price is not None else None,
            "status": r.status,
        }
        for r in rows
    ]


@products_bp.route("/products", methods=["GET"])
@jwt_required()
@role_required(["admin", "manager", "staff"])
def list_products():
    page, page_size = _get_pagination()

    category_id = request.args.get("category_id", None)
    status = request.args.get("status", None)
    search = request.args.get("search", None)

    query = Product.query

    if category_id is not None and str(category_id).strip() != "":
        try:
            category_id = int(category_id)
            query = query.filter(Product.category_id == category_id)
        except ValueError:
            return _json_error("category_id must be an integer", 400)

    if status is not None and str(status).strip() != "":
        status_bool = _parse_boolish(status)
        query = query.filter(Product.status == status_bool)

    if search is not None and str(search).strip() != "":
        s = f"%{search.strip()}%"
        # ilike for PostgreSQL
        query = query.filter(Product.name.ilike(s))

    total = query.count()
    items = (
        query.order_by(Product.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return jsonify(
        {
            "success": True,
            "data": {
                "items": [_product_to_dict_basic(p) for p in items],
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size if page_size else 0,
            },
        }
    )


@products_bp.route("/products", methods=["POST"])
@jwt_required()
@role_required(["admin", "manager"])
def create_product():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    if not name:
        return _json_error("Missing required field: name", 400)

    category_id = data.get("category_id", None)
    description = (data.get("description") or None)

    base_price = data.get("base_price", None)
    if base_price is None:
        return _json_error("Missing required field: base_price", 400)

    image = data.get("image", None)
    status = data.get("status", True)
    status = _parse_boolish(status) if status is not None else True

    # NOTE: POST /products không đi kèm size.
    # Nếu client gửi size_ids thì backend sẽ bỏ qua.

    # optional: validate category exists
    if category_id is not None:
        try:
            category_id = int(category_id)
        except ValueError:
            return _json_error("category_id must be integer", 400)
        if not Category.query.get(category_id):
            return _json_error("Category not found", 404)

    try:
        base_price_val = str(base_price)
        product = Product(
            category_id=category_id,
            name=name,
            description=description,
            base_price=base_price_val,
            image=image,
            status=status,
        )

        db.session.add(product)
        db.session.flush()  # get product.id

        db.session.commit()

        toppings = _get_product_toppings(product.id)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Product created successfully",
                    "data": {
                        **_product_to_dict_basic(product),
                        "toppings": toppings,
                    },
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to create product", 500, detail=str(e))



@products_bp.route("/products/<int:product_id>", methods=["GET"])
@jwt_required()
@role_required(["admin", "manager", "staff"])
def get_product_detail(product_id: int):
    p = Product.query.get(product_id)
    if not p:
        return _json_error("Product not found", 404)

    include_sizes = _parse_boolish(request.args.get("include_sizes", False))
    include_toppings = _parse_boolish(request.args.get("include_toppings", True))

    sizes = []
    toppings = []

    if include_sizes:
        sizes, _size_ids = _get_product_sizes(product_id)

    if include_toppings:
        toppings = _get_product_toppings(product_id)

    data = {**_product_to_dict_basic(p)}
    if include_sizes:
        data["sizes"] = sizes
    if include_toppings:
        data["toppings"] = toppings

    return jsonify(
        {
            "success": True,
            "data": data,
        }
    )



@products_bp.route("/products/<int:product_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin", "manager"])
def update_product(product_id: int):
    p = Product.query.get(product_id)
    if not p:
        return _json_error("Product not found", 404)

    data = request.get_json(silent=True) or {}

    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return _json_error("Field 'name' cannot be empty", 400)
        p.name = name

    if "description" in data:
        p.description = data.get("description")

    if "base_price" in data:
        base_price = data.get("base_price")
        if base_price is None:
            return _json_error("Field 'base_price' cannot be null", 400)
        p.base_price = str(base_price)

    if "image" in data:
        p.image = data.get("image")

    if "category_id" in data:
        category_id = data.get("category_id", None)
        if category_id is not None:
            try:
                category_id = int(category_id)
            except ValueError:
                return _json_error("category_id must be integer", 400)
            if not Category.query.get(category_id):
                return _json_error("Category not found", 404)
        p.category_id = category_id

    if "status" in data:
        p.status = _parse_boolish(data.get("status"))

    if "size_ids" in data:
        size_ids = data.get("size_ids")
        if size_ids is None or not isinstance(size_ids, list):
            return _json_error("size_ids must be a list", 400)
        if len(size_ids) == 0:
            return _json_error("size_ids cannot be empty", 400)
        try:
            size_ids_int = sorted(set(int(x) for x in size_ids))
        except (TypeError, ValueError):
            return _json_error("size_ids[] must be a list of integers", 400)

        existing_size_count = Size.query.filter(Size.id.in_(size_ids_int)).count()
        if existing_size_count != len(size_ids_int):
            return _json_error("Some size_ids do not exist", 400)

        # sync product_sizes
        ProductSize.query.filter_by(product_id=product_id).delete(synchronize_session=False)
        for sid in size_ids_int:
            db.session.add(ProductSize(product_id=product_id, size_id=sid))

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to update product", 500, detail=str(e))

    sizes, _ = _get_product_sizes(product_id)
    toppings = _get_product_toppings(product_id)

    return jsonify(
        {
            "success": True,
            "message": "Product updated successfully",
            "data": {
                **_product_to_dict_basic(p),
                "sizes": sizes,
                "toppings": toppings,
            },
        }
    )


@products_bp.route("/products/<int:product_id>/status", methods=["PATCH"])
@jwt_required()
@role_required(["admin"])
def toggle_product_status(product_id: int):
    p = Product.query.get(product_id)
    if not p:
        return _json_error("Product not found", 404)

    p.status = not p.status
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": "Product status updated successfully",
            "data": {
                "id": p.id,
                "status": p.status,
            },
        }
    )


@products_bp.route("/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_product(product_id: int):
    p = Product.query.get(product_id)
    if not p:
        return _json_error("Product not found", 404)

    used_count = OrderItem.query.filter_by(product_id=product_id).count()
    if used_count > 0:
        return _json_error(
            "Cannot delete product because it is used in orders",
            409,
            used_order_items=used_count,
        )

    try:
        db.session.delete(p)
        db.session.commit()
        return jsonify({"success": True, "message": "Product deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to delete product", 500, detail=str(e))

