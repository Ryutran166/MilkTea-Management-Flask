from flask import Flask

from config.db import db

from routes.auth_route import auth_bp

app = Flask(__name__)

# =====================================
# PostgreSQL Config
# =====================================

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:1662004@localhost:5432/milktea-management"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# =====================================
# Init DB
# =====================================

db.init_app(app)

# =====================================
# Register Routes
# =====================================

app.register_blueprint(auth_bp)

# =====================================
# Home
# =====================================

@app.route("/")
def home():
    return "Milk Tea Management API"

# =====================================
# Run Server
# =====================================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)