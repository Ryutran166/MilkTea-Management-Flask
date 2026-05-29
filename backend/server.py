from flask import Flask
from flask import send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
from pathlib import Path

from config.db import db
from routes.auth_route import auth_bp
from routes.test_route import test_bp
from routes.branches_route import branches_bp
from routes.products_route import products_bp
from routes.categories_route import categories_bp
from routes.sizes_route import sizes_bp
from routes.toppings_route import toppings_bp
from routes.orders_route import orders_bp


# Ensure models are registered before db.create_all()

from models import (  # noqa: F401
    Branch,
    User,
    RefreshToken,
    Category,
    Product,
    Size,
    Topping,
    ProductSize,
    Order,
    OrderItem,
    OrderItemTopping,
)


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path=""
)

CORS(app)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:1662004@localhost:5432/milktea-management"

app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False

app.config[
    "JWT_SECRET_KEY"
] = "super-secret-key"

app.config[
    "JWT_ACCESS_TOKEN_EXPIRES"
] = timedelta(days=7)

app.config[
    "JWT_REFRESH_TOKEN_EXPIRES"
] = timedelta(days=7)

db.init_app(app)

jwt = JWTManager(app)

# =========================
# JWT ERROR HANDLER
# =========================

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):

    return {
        "success": False,
        "message": "Token expired"
    }, 401


@jwt.invalid_token_loader
def invalid_token_callback(error):

    return {
        "success": False,
        "message": "Invalid token"
    }, 401


@jwt.unauthorized_loader
def missing_token_callback(error):

    return {
        "success": False,
        "message": "Authorization token required"
    }, 401


@app.route("/")
def home():

    return send_from_directory(
        app.static_folder,
        "index.html"
    )


app.register_blueprint(auth_bp)
app.register_blueprint(test_bp)
app.register_blueprint(branches_bp)
app.register_blueprint(products_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(sizes_bp)
app.register_blueprint(toppings_bp)
app.register_blueprint(orders_bp)

with app.app_context():
    db.create_all()



if __name__ == "__main__":
    app.run(debug=True)
