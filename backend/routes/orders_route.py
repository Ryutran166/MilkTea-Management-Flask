from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config.db import db
from middlewares.auth_middleware import role_required

from models.branch_model import Branch
from models.product_model import Product
from models.size_model import Size
from models.topping_model import Topping
from models.product_size_model import ProductSize
from models.order_model import Order
from models.order_item_model import OrderItem
from models.order_item_topping_model import OrderItemTopping


orders_bp = Blueprint(
    "orders_bp",
    __name__,
)


def _json_error(message, status_code=400, **extra):
    payload = {"success": False, "message": message}
    payload.update(extra)
    return jsonify(payload), status_code


def _parse_int(value, field_name: str):
    try:
        if isinstance(value, bool) or value is None:
            raise ValueError
        return int(value)
    except Exception:
        return _json_error(f"{field_name} must be an integer", 400)


def _parse_boolish(value):
    if isinstance(value, str):
        return value.strip().lower() in ["true", "1", "yes", "y", "on"]
    return bool(value)


def _get_allowed_product_toppings(product_id: int):
    # Read from product_toppings(product_id, topping_id)
    q = text(
        """
        SELECT topping_id
        FROM product_toppings
        WHERE product_id = :product_id
        """
    )
    rows = db.session.execute(q, {"product_id": product_id}).fetchall()
    return {int(r.topping_id) for r in rows}


def _is_size_of_product(product_id: int, size_id: int) -> bool:
    return db.session.query(ProductSize.id).filter_by(product_id=product_id, size_id=size_id).first() is not None


@orders_bp.route("/orders", methods=["POST"])
@jwt_required()
@role_required(["staff", "admin", "manager"])
def create_order():
    data = request.get_json(silent=True) or {}

    branch_id = data.get("branch_id", None)
    items = data.get("items", None)
    payment_method = data.get("payment_method", None)

    if branch_id is None:
        return _json_error("Missing required field: branch_id", 400)
    if payment_method is None:
        return _json_error("Missing required field: payment_method", 400)
    if not isinstance(items, list) or len(items) == 0:
        return _json_error("Field 'items' must be a non-empty array", 400)

    # basic whitelist to match schema check in milktea-management.sql
    payment_method_allowed = {"cash", "momo", "banking", "vnpay"}
    payment_method = str(payment_method).strip().lower()
    if payment_method not in payment_method_allowed:
        return _json_error("payment_method is invalid", 400)



    try:
        branch_id_int = int(branch_id)
    except Exception:
        return _json_error("branch_id must be an integer", 400)

    branch = Branch.query.get(branch_id_int)
    if not branch:
        return _json_error("branch_id not found", 404)
    # Optional: if you want strict branch status
    if branch.status is not True:
        return _json_error("Branch is not available", 409)

    # Validate items first (fail-fast) then write a transaction
    order_items_payload = []

    for idx, item in enumerate(items):

        if not isinstance(item, dict):
            return _json_error(f"items[{idx}] must be an object", 400)

        product_id = item.get("product_id", None)
        size_id = item.get("size_id", None)
        qty = item.get("quantity", None)
        # backward compatibility: accept old field name "qty" if provided
        if qty is None and "qty" in item:
            qty = item.get("qty", None)
        toppings = item.get("toppings", [])
        note = item.get("note", None)


        missing = []
        if product_id is None:
            missing.append("product_id")
        if size_id is None:
            missing.append("size_id")
        if qty is None:
            # theo spec yêu cầu key là quantity
            missing.append("quantity")

        if toppings is None:
            toppings = []
        if missing:
            return _json_error(f"items[{idx}] missing required field(s): {', '.join(missing)}", 400)

        try:
            product_id_int = int(product_id)
            size_id_int = int(size_id)
            qty_int = int(qty)
        except Exception:
            return _json_error(f"items[{idx}] has invalid product_id/size_id/qty (must be integers)", 400)

        if qty_int <= 0:
            return _json_error(f"items[{idx}].qty must be > 0", 400)

        product = Product.query.get(product_id_int)
        if not product:
            return _json_error(f"items[{idx}].product_id not found", 404)
        if product.status is not True:
            return _json_error(f"Product {product_id_int} is not available", 409)

        size = Size.query.get(size_id_int)

        if not size:
            return _json_error(f"items[{idx}].size_id not found", 404)

        if not _is_size_of_product(product_id_int, size_id_int):
            return _json_error(
                f"items[{idx}] size_id {size_id_int} is not valid for product_id {product_id_int}",
                409,
            )

        if not isinstance(toppings, list):
            return _json_error(f"items[{idx}].toppings must be an array", 400)

        # Validate topping ids: exist + status=true + allowed for product
        allowed_topping_ids = _get_allowed_product_toppings(product_id_int)

        topping_ids = []
        for t_idx, t_id in enumerate(toppings):
            try:
                t_id_int = int(t_id)
            except Exception:
                return _json_error(f"items[{idx}].toppings[{t_idx}] must be an integer", 400)
            topping_ids.append(t_id_int)

        # Enforce uniqueness per order item (avoid duplicate rows)
        unique_topping_ids = sorted(set(topping_ids))

        topping_records = Topping.query.filter(Topping.id.in_(unique_topping_ids)).all() if unique_topping_ids else []
        existing_ids = {t.id for t in topping_records}
        missing_ids = [t for t in unique_topping_ids if t not in existing_ids]
        if missing_ids:
            return _json_error(
                f"items[{idx}] contains non-existent topping_id(s): {missing_ids}",
                404,
            )

        # status + allowed check
        for t in topping_records:
            if t.status is not True:
                return _json_error(f"Topping {t.id} is not available", 409)
            if t.id not in allowed_topping_ids:
                return _json_error(
                    f"Topping {t.id} is not allowed for product_id {product_id_int}",
                    409,
                )

        toppings_cost = sum([t.price for t in topping_records]) if topping_records else 0

        # Compute price components
        unit_price = product.base_price + (size.extra_price or 0) + toppings_cost
        subtotal = unit_price * qty_int

        order_items_payload.append(
            {
                "product_id": product_id_int,
                "size_id": size_id_int,
                "qty": qty_int,
                "topping_ids": unique_topping_ids,
                "note": note,
                "unit_price": unit_price,
                "subtotal": subtotal,
            }
        )

    total_amount = sum([it["subtotal"] for it in order_items_payload])

    # Write DB (tránh dùng db.session.begin() vì có thể xung đột transaction đã mở sẵn)
    from flask_jwt_extended import get_jwt_identity
    user_id = get_jwt_identity()

    try:
        o = Order(
            branch_id=branch_id_int,
            user_id=user_id,
            total_amount=total_amount,
            payment_method=payment_method,
           
            # nên không set để tránh lỗi UndefinedColumn
        )

        db.session.add(o)
        db.session.flush()  # get order.id

        created_items = []
        for it in order_items_payload:
            oi = OrderItem(
                order_id=o.id,
                product_id=it["product_id"],
                size_id=it["size_id"],
                quantity=it["qty"],
                unit_price=it["unit_price"],
                subtotal=it["subtotal"],
                note=it["note"],
            )
            db.session.add(oi)
            db.session.flush()

            for topping_id in it["topping_ids"]:
                db.session.add(
                    OrderItemTopping(
                        order_item_id=oi.id,
                        topping_id=topping_id,
                    )
                )

            created_items.append(
                {
                    "id": oi.id,
                    "product_id": oi.product_id,
                    "size_id": oi.size_id,
                    "qty": oi.quantity,
                    "unit_price": str(oi.unit_price) if oi.unit_price is not None else None,
                    "subtotal": str(oi.subtotal) if oi.subtotal is not None else None,
                    "note": oi.note,
                    "topping_ids": it["topping_ids"],
                }
            )

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Order created successfully",
                "data": {
                    "order": {
                        "id": o.id,
                        "branch_id": o.branch_id,

                        "created_at": o.created_at.isoformat() if o.created_at else None,
                    },
                    "items": created_items,
                },
            }
        ), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return _json_error("Failed to create order", 500, detail=str(e))
    except Exception as e:
        db.session.rollback()
        return _json_error("Failed to create order", 500, detail=str(e))


