"""
Smart Water Usage Advisor - API Middleware & Security Layer
Location: 4_DEVELOPMENT/backend/api/middleware.py

Provides:
- @auth_required: JWT extraction, signature validation, expiration checking
- @meter_access_required: BOLA / IDOR defense cross-checking requested meter/user ID
- Global JSON error handlers preventing information leakage
"""

from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
from typing import Optional, Callable

from backend.services.auth_service import get_auth_service


def auth_required(f: Callable) -> Callable:
    """
    Decorator requiring a valid JWT token in Authorization: Bearer <token> header.
    In testing/dev mode, if ENABLE_DEMO_AUTH is True and no header is provided,
    it can fall back to user_id parameter for seamless local evaluation if configured,
    but in production, token is MANDATORY (fail-closed).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        token = None

        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
            else:
                return jsonify({
                    "error": "Invalid Authorization header format. Expected 'Bearer <token>'.",
                    "error_code": "INVALID_HEADER_FORMAT",
                    "status_code": 401
                }), 401
        elif "token" in request.cookies:
            token = request.cookies.get("token")

        # In dev/test mode only: if demo token allowed and explicit demo user query param
        auth_service = get_auth_service()
        config = current_app.config

        if not token:
            if config.get("ENABLE_DEMO_AUTH") and config.get("ENVIRONMENT") != "production":
                # For development ease, allow fallback to demo token generation if requested
                demo_uid = request.args.get("demo_user_id") or request.args.get("user_id")
                if demo_uid:
                    try:
                        uid_int = int(demo_uid)
                        if uid_int in (1, 2, 3):
                            token = auth_service.get_demo_token(uid_int)
                    except Exception:
                        token = None

        if not token:
            return jsonify({
                "error": "Authentication required. Please provide a valid Bearer token.",
                "error_code": "UNAUTHORIZED",
                "status_code": 401
            }), 401

        if isinstance(token, dict):
            token = token.get("token")

        try:
            payload = auth_service.decode_token(token)
            raw_sub = payload.get("sub")
            try:
                sub_int = int(raw_sub)
            except (ValueError, TypeError):
                sub_int = 1

            meter_ids = [int(m) for m in payload.get("meter_ids", [sub_int])]

            g.current_user = {
                "user_id": sub_int,
                "email": payload.get("email"),
                "user_type": payload.get("user_type", "household"),
                "meter_ids": meter_ids,
                "first_name": payload.get("first_name", ""),
                "last_name": payload.get("last_name", "")
            }
        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Authentication token has expired. Please log in again.",
                "error_code": "TOKEN_EXPIRED",
                "status_code": 401
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Invalid authentication token signature or payload.",
                "error_code": "INVALID_TOKEN",
                "status_code": 401
            }), 401

        return f(*args, **kwargs)

    return decorated_function


def meter_access_required(f: Callable) -> Callable:
    """
    BOLA / IDOR Defense Decorator.
    Verifies that any client-supplied user_id or meter_id belongs to the authenticated user's scope.
    Role 'municipal' possesses district-level aggregate read permissions.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, "current_user") or not g.current_user:
            return jsonify({
                "error": "Authentication context missing.",
                "error_code": "UNAUTHORIZED",
                "status_code": 401
            }), 401

        user = g.current_user
        req_uid = request.args.get("user_id") or kwargs.get("user_id")
        req_mid = request.args.get("meter_id") or kwargs.get("meter_id")

        # Check JSON body for POST requests
        if request.is_json and request.content_length and request.content_length > 0:
            try:
                body = request.get_json(silent=True) or {}
                req_uid = req_uid or body.get("user_id")
                req_mid = req_mid or body.get("meter_id")
            except Exception:
                pass

        # Municipal role has district-level read access
        if user["user_type"] == "municipal":
            return f(*args, **kwargs)

        # Validate user_id if provided
        if req_uid is not None:
            try:
                if int(req_uid) != int(user["user_id"]):
                    return jsonify({
                        "error": "Access denied: Unauthorized tenant or user ID access.",
                        "error_code": "FORBIDDEN",
                        "status_code": 403
                    }), 403
            except ValueError:
                return jsonify({
                    "error": "Invalid user_id parameter.",
                    "error_code": "INVALID_PARAMETER",
                    "status_code": 400
                }), 400

        # Validate meter_id if provided
        if req_mid is not None:
            try:
                if int(req_mid) not in user["meter_ids"]:
                    return jsonify({
                        "error": "Access denied: Unauthorized meter access.",
                        "error_code": "FORBIDDEN",
                        "status_code": 403
                    }), 403
            except ValueError:
                return jsonify({
                    "error": "Invalid meter_id parameter.",
                    "error_code": "INVALID_PARAMETER",
                    "status_code": 400
                }), 400

        return f(*args, **kwargs)

    return decorated_function


def register_error_handlers(app):
    """Registers standard JSON error handlers across the Flask application."""

    @app.errorhandler(400)
    def bad_request(err):
        return jsonify({
            "error": getattr(err, "description", "Bad Request"),
            "error_code": "BAD_REQUEST",
            "status_code": 400
        }), 400

    @app.errorhandler(401)
    def unauthorized(err):
        return jsonify({
            "error": getattr(err, "description", "Unauthorized"),
            "error_code": "UNAUTHORIZED",
            "status_code": 401
        }), 401

    @app.errorhandler(403)
    def forbidden(err):
        return jsonify({
            "error": getattr(err, "description", "Forbidden"),
            "error_code": "FORBIDDEN",
            "status_code": 403
        }), 403

    @app.errorhandler(404)
    def not_found(err):
        return jsonify({
            "error": getattr(err, "description", "Resource not found"),
            "error_code": "NOT_FOUND",
            "status_code": 404
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(err):
        return jsonify({
            "error": getattr(err, "description", "Method Not Allowed"),
            "error_code": "METHOD_NOT_ALLOWED",
            "status_code": 405
        }), 405

    @app.errorhandler(413)
    def payload_too_large(err):
        return jsonify({
            "error": "Request payload exceeds maximum allowed size.",
            "error_code": "PAYLOAD_TOO_LARGE",
            "status_code": 413
        }), 413

    @app.errorhandler(500)
    def internal_error(err):
        # Log error securely server-side; never expose trace to client
        app.logger.error(f"Internal Server Error: {err}")
        return jsonify({
            "error": "An internal server error occurred. Please contact the administrator.",
            "error_code": "INTERNAL_SERVER_ERROR",
            "status_code": 500
        }), 500

    @app.errorhandler(503)
    def service_unavailable(err):
        return jsonify({
            "error": getattr(err, "description", "Service Unavailable"),
            "error_code": "SERVICE_UNAVAILABLE",
            "status_code": 503
        }), 503
