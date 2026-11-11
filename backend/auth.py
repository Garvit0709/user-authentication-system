
import re
import bcrypt
import psycopg

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, make_response, current_app
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    unset_jwt_cookies
)

from database import get_connection


auth = Blueprint("auth", __name__, url_prefix="/api/auth")


# User Registration
@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all(isinstance(x, str) for x in [username, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    username = username.strip()
    email = email.strip().lower()

    if not (3 <= len(username) <= 50):
        return jsonify({
            "error": "Username must be 3 to 50 characters"
        }), 400

    if len(email) > 100 or not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", email
    ):
        return jsonify({"error": "Enter a valid email"}), 400

    if len(password) < 8 or len(password.encode("utf-8")) > 72:
        return jsonify({
            "error": "Password must be at least 8 characters and at most 72 bytes"
        }), 400

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (username, email, password_hash)
                    VALUES (%s, %s, %s)
                    RETURNING id, username, email
                """, (username, email, password_hash))

                user = cur.fetchone()

        return jsonify({
            "message": "Registration successful",
            "user": {
                "id": user[0],
                "username": user[1],
                "email": user[2]
            }
        }), 201

    except psycopg.errors.UniqueViolation:
        return jsonify({
            "error": "Username or email already registered"
        }), 409

    except Exception:
        current_app.logger.exception("Registration failed")
        return jsonify({"error": "Registration failed"}), 500


# User Login
@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "error": "Email and password are required"
        }), 400

    email = email.strip().lower()

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    if len(password.encode("utf-8")) > 72:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, username, password_hash
                    FROM users
                    WHERE email = %s
                    """,
                    (email,)
                )
                user = cur.fetchone()

    except Exception:
        current_app.logger.exception("Login database error")
        return jsonify({"error": "Unable to process login"}), 500

    if user is None:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    user_id, username, password_hash = user

    try:
        password_valid = bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        current_app.logger.error("Password verification failed")
        return jsonify({"error": "Unable to process login"}), 500

    if not password_valid:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    access_token = create_access_token(identity=str(user_id))

    response = make_response(jsonify({
        "message": "Login successful",
        "user": {
            "id": user_id,
            "username": username
        }
    }))

    set_access_cookies(response, access_token)

    return response, 200


# Protected User Profile
@auth.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, username, email
                    FROM users
                    WHERE id = %s
                    """,
                    (int(user_id),)
                )
                user = cur.fetchone()

        if user is None:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "id": user[0],
            "username": user[1],
            "email": user[2]
        }), 200

    except Exception:
        current_app.logger.exception("Profile retrieval failed")
        return jsonify({"error": "Unable to load profile"}), 500


# Logout
@auth.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    token = get_jwt()

    token_id = token["jti"]
    expiry = datetime.fromtimestamp(
        token["exp"],
        timezone.utc
    )

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO revoked_tokens (jti, expires_at)
                    VALUES (%s, %s)
                    ON CONFLICT (jti) DO NOTHING
                    """,
                    (token_id, expiry)
                )

    except Exception:
        current_app.logger.exception("Logout failed")
        return jsonify({"error": "Logout failed"}), 500

    response = jsonify({
        "message": "Logged out successfully"
    })

    unset_jwt_cookies(response)

    return response, 200


# Check Authentication Status
@auth.route("/check", methods=["GET"])
@jwt_required()
def check_auth():
    return jsonify({
        "authenticated": True,
        "user_id": get_jwt_identity()
    }), 200
