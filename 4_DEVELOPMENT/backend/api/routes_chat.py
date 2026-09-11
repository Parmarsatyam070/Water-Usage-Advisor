"""
Smart Water Usage Advisor - Conversational Advisor Blueprint
Location: 4_DEVELOPMENT/backend/api/routes_chat.py

Provides modular REST endpoints for the AI Water Conservation Chatbot:
- POST /api/v1/chat
"""

from flask import Blueprint, request, jsonify, g
from backend.dashboard_data_service import get_data_service
from backend.api.middleware import auth_required

chat_bp = Blueprint("chat", __name__, url_prefix="/api/v1/chat")


@chat_bp.route("", methods=["POST"])
@auth_required
def send_chat_message():
    """
    Submits a conversational message to the AI Water Advisor.
    Grounded strictly in the authenticated user's active meter telemetry,
    detected anomalies, forward forecasts, and curated knowledge base.
    """
    if not request.is_json:
        return jsonify({
            "error": "Request body must be JSON.",
            "error_code": "INVALID_CONTENT_TYPE",
            "status_code": 400
        }), 400

    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({
            "error": "Message parameter is required.",
            "error_code": "MISSING_MESSAGE",
            "status_code": 400
        }), 400

    user_id = g.current_user["user_id"]
    ds = get_data_service()
    chat_response = ds.handle_chat(user_id=user_id, user_message=message)
    return jsonify(chat_response), 200
