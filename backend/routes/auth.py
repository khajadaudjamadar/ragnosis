import re

from bson import ObjectId
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("auth", __name__)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def public_user(u):
    return {"id": str(u["_id"]), "name": u["name"], "email": u["email"], "role": u["role"]}


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = data.get("role", "patient")

    if not name or not EMAIL_RE.match(email):
        return jsonify(error="Valid name and email are required"), 400
    if len(password) < 6:
        return jsonify(error="Password must be at least 6 characters"), 400
    if role not in ("patient", "doctor"):
        return jsonify(error="Role must be patient or doctor"), 400

    db = current_app.db
    if db.users.find_one({"email": email}):
        return jsonify(error="Email already registered"), 409

    user = {"name": name, "email": email, "role": role, "password": generate_password_hash(password)}
    user["_id"] = db.users.insert_one(user).inserted_id
    token = create_access_token(identity=str(user["_id"]))
    return jsonify(token=token, user=public_user(user)), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    user = current_app.db.users.find_one({"email": email})
    if not user or not check_password_hash(user["password"], data.get("password") or ""):
        return jsonify(error="Invalid email or password"), 401
    token = create_access_token(identity=str(user["_id"]))
    return jsonify(token=token, user=public_user(user))


@bp.get("/me")
@jwt_required()
def me():
    user = current_app.db.users.find_one({"_id": ObjectId(get_jwt_identity())})
    if not user:
        return jsonify(error="User not found"), 404
    return jsonify(user=public_user(user))
