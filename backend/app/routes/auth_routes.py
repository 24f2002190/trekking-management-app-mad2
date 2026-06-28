import uuid
from flask import Blueprint, request, jsonify
from flask_security import verify_password, hash_password
from app.models import db, User, StaffProfile
from app import user_datastore

auth_bp = Blueprint("auth", __name__)


def user_to_dict(user):
    return {
        "id":        user.id,
        "email":     user.email,
        "username":  user.username,
        "full_name": user.full_name,
        "roles":     [r.name for r in user.roles],
        "active":    user.active,
    }


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    required = ["email", "username", "password", "full_name"]
    for field in required:
        if not data.get(field):
            return jsonify({"message": f"{field} is required"}), 400

    if user_datastore.find_user(email=data["email"]):
        return jsonify({"message": "Email already registered"}), 409

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "Username already taken"}), 409

    new_user = user_datastore.create_user(
        email=data["email"],
        username=data["username"],
        full_name=data["full_name"],
        phone=data.get("phone", ""),
        password=hash_password(data["password"]),
        fs_uniquifier=str(uuid.uuid4()),
        roles=["trekker"],
    )
    db.session.commit()

    return jsonify({
        "message": "Registration successful",
        "user": user_to_dict(new_user)
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    
    data = request.get_json()

    email    = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = user_datastore.find_user(email=email)

    if not user or not verify_password(password, user.password):
        return jsonify({"message": "Invalid email or password"}), 401

    if not user.active:
        return jsonify({"message": "Your account has been deactivated"}), 403

    token = user.get_auth_token()

    return jsonify({
        "message": "Login successful",
        "token":   token,
        "user":    user_to_dict(user)
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():

    data  = request.get_json()
    email = data.get("email", "")

    user = user_datastore.find_user(email=email)
    if user:
        user.fs_uniquifier = str(uuid.uuid4())
        db.session.commit()

    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """
    Frontend sends token in header: Authentication-Token: <token>
    Returns the logged-in user's info.
    """
    from flask_security import auth_token_required, current_user

    token = request.headers.get("Authentication-Token")
    if not token:
        return jsonify({"message": "Token missing"}), 401

    user = User.query.filter_by(fs_uniquifier=_get_uniquifier_from_token(token)).first()
    if not user:
        return jsonify({"message": "Invalid or expired token"}), 401

    return jsonify({"user": user_to_dict(user)}), 200


def _get_uniquifier_from_token(token: str):

    from flask_security.utils import parse_auth_token
    try:
        data = parse_auth_token(token)
        return data.get("uid") if data else None
    except Exception:
        return None