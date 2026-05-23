from functools import wraps

from flask import jsonify

from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity
)

from models.user_model import User


def role_required(roles):

    def wrapper(fn):

        @wraps(fn)
        def decorator(*args, **kwargs):

            verify_jwt_in_request()

            user_id = get_jwt_identity()

            user = User.query.get(user_id)

            if not user:

                return jsonify({
                    "success": False,
                    "message": "User not found"
                }), 404

            if user.role not in roles:

                return jsonify({
                    "success": False,
                    "message": "Permission denied"
                }), 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper