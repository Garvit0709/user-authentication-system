
import os
from datetime import timedelta
from database import get_connection
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from pathlib import Path
from flask import send_from_directory, redirect, url_for
from auth import auth

load_dotenv(Path(__file__).resolve().parent / ".env")
app = Flask(__name__, static_folder=None)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = True
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

# Local development uses HTTP.
# Set this to True when deploying over HTTPS.
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_SAMESITE"] = "Lax"

if not app.config["JWT_SECRET_KEY"]:
    raise RuntimeError("JWT_SECRET_KEY is missing from .env")

jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_revoked_token(jwt_header, jwt_payload):
    token_id = jwt_payload["jti"]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM revoked_tokens WHERE jti = %s",
                (token_id,)
            )
            result = cur.fetchone()

    return result is not None

app.register_blueprint(auth)


@app.route("/")
def home():
    return jsonify({
        "message": "User Authentication API is running"
    })


@app.route("/register")
def register_page():
    return send_from_directory(FRONTEND_DIR, "register.html")


@app.route("/login")
def login_page():
    return send_from_directory(FRONTEND_DIR, "login.html")


@app.route("/dashboard")
def dashboard_page():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")


@app.route("/static/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)
