"""
Smart Water Usage Advisor - Authentication Blueprint
Location: 4_DEVELOPMENT/backend/api/routes_auth.py

Routes:
- POST /api/auth/login: Email/password authentication returning JWT
- GET /api/auth/me: Authenticated user context
- GET /api/auth/demo-token: Development/test fixture token generator (disabled in production)
"""

from flask import Blueprint, request, jsonify, g, current_app
from backend.services.auth_service import get_auth_service
from backend.api.middleware import auth_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticates user with email and password, returning a JWT token."""
    if not request.is_json:
        return jsonify({
            "error": "Request body must be JSON.",
            "error_code": "INVALID_CONTENT_TYPE",
            "status_code": 400
        }), 400

    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required.",
            "error_code": "MISSING_CREDENTIALS",
            "status_code": 400
        }), 400

    auth_service = get_auth_service()
    user = auth_service.authenticate_user(email, password)

    if not user:
        return jsonify({
            "error": "Invalid email or password.",
            "error_code": "AUTHENTICATION_FAILED",
            "status_code": 401
        }), 401

    token = auth_service.generate_token(user)

    return jsonify({
        "token": token,
        "token_type": "Bearer",
        "user": user
    }), 200


@auth_bp.route("/me", methods=["GET"])
@auth_required
def get_current_user_profile():
    """Returns the profile of the currently authenticated user."""
    return jsonify({
        "user": g.current_user
    }), 200


@auth_bp.route("/demo-token", methods=["GET"])
def get_demo_token():
    """
    DEVELOPMENT/TEST ONLY: Generates a pre-signed JWT for a seeded demo persona.
    Strictly disabled in production mode.
    Permitted user_ids: [1, 2, 3].
    """
    config = current_app.config
    if config.get("ENVIRONMENT") == "production" or not config.get("ENABLE_DEMO_AUTH"):
        return jsonify({
            "error": "Demo token endpoint is disabled in production.",
            "error_code": "FORBIDDEN",
            "status_code": 403
        }), 403

    user_id_param = request.args.get("user_id", "1")
    try:
        user_id = int(user_id_param)
    except ValueError:
        return jsonify({
            "error": "Invalid user_id parameter.",
            "error_code": "INVALID_PARAMETER",
            "status_code": 400
        }), 400

    auth_service = get_auth_service()
    try:
        token_info = auth_service.get_demo_token(user_id)
        token_str = token_info["token"] if isinstance(token_info, dict) else token_info
        safe_user = token_info.get("user", {"user_id": user_id}) if isinstance(token_info, dict) else {"user_id": user_id}
        return jsonify({
            "token": token_str,
            "token_type": "Bearer",
            "user_id": user_id,
            "user": safe_user,
            "note": "Development/Test token only. Not valid for production use."
        }), 200
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "error_code": "INVALID_DEMO_USER",
            "status_code": 400
        }), 400
    except PermissionError as e:
        return jsonify({
            "error": str(e),
            "error_code": "FORBIDDEN",
            "status_code": 403
        }), 403
