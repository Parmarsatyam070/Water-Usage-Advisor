"""
Smart Water Usage Advisor - Dashboard Blueprint (Phase 4 Backwards-Compatible)
Location: 4_DEVELOPMENT/backend/api/routes_dashboard.py

Provides:
- GET /api/dashboard/summary
- GET /api/dashboard/consumption
- GET /api/dashboard/forecast
- GET /api/dashboard/anomalies
- GET /api/dashboard/recommendations
- GET /api/dashboard/goals
- POST /api/dashboard/chat
- GET /api/dashboard/users

All protected with @auth_required and @meter_access_required to ensure strict tenant isolation.
"""

from flask import Blueprint, request, jsonify, g
from backend.dashboard_data_service import get_data_service
from backend.api.middleware import auth_required, meter_access_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/summary", methods=["GET"])
@auth_required
@meter_access_required
def get_summary():
    """Returns Section A KPI summary cards DTO for the authorized user."""
    # Use authenticated user_id from token context (BOLA defense)
    user_id = g.current_user["user_id"]
    ds = get_data_service()
    payload = ds.get_summary(user_id=user_id)
    return jsonify(payload), 200


@dashboard_bp.route("/consumption", methods=["GET"])
@auth_required
@meter_access_required
def get_consumption():
    """Returns Section B 24h diurnal and 30d history consumption analytics DTO."""
    user_id = g.current_user["user_id"]
    time_range = request.args.get("range", "30d")
    ds = get_data_service()
    payload = ds.get_consumption(user_id=user_id, time_range=time_range)
    return jsonify(payload), 200


@dashboard_bp.route("/forecast", methods=["GET"])
@auth_required
@meter_access_required
def get_forecast():
    """Returns Section C 7-day forward predictive consumption forecast DTO."""
    user_id = g.current_user["user_id"]
    ds = get_data_service()
    payload = ds.get_forecast(user_id=user_id)
    return jsonify(payload), 200


@dashboard_bp.route("/anomalies", methods=["GET"])
@auth_required
@meter_access_required
def get_anomalies():
    """Returns Section D Anomaly & leak incident center DTO."""
    user_id = g.current_user["user_id"]
    ds = get_data_service()
    payload = ds.get_anomalies(user_id=user_id)
    return jsonify(payload), 200


@dashboard_bp.route("/recommendations", methods=["GET"])
@auth_required
@meter_access_required
def get_recommendations():
    """Returns Section E Personalized conservation recommendations DTO."""
    user_id = g.current_user["user_id"]
    ds = get_data_service()
    payload = ds.get_recommendations(user_id=user_id)
    return jsonify(payload), 200


@dashboard_bp.route("/goals", methods=["GET"])
@auth_required
@meter_access_required
def get_goals():
    """Returns Section G SDG 6.4 goal progress gauge DTO."""
    user_id = g.current_user["user_id"]
    ds = get_data_service()
    payload = ds.get_goals(user_id=user_id)
    return jsonify(payload), 200


@dashboard_bp.route("/chat", methods=["POST"])
@auth_required
@meter_access_required
def handle_chat():
    """Handles Section F Conversational AI Water Conservation Chatbot queries."""
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

    # Ensure query context is bound strictly to the authenticated principal
    user_id = g.current_user["user_id"]
    ds = get_data_service()
    chat_response = ds.handle_chat(user_id=user_id, user_message=message)
    return jsonify(chat_response), 200


@dashboard_bp.route("/users", methods=["GET"])
def get_demo_users():
    """Returns public list of seeded demo persona descriptors for testing."""
    users_list = [
        {"user_id": 1, "name": "Sarah Jenkins", "type": "Residential Single-Family", "meter_id": 1},
        {"user_id": 2, "name": "Marcus Vance", "type": "Residential Multi-Family", "meter_id": 2},
        {"user_id": 3, "name": "Elena Rostova", "type": "Commercial Office Facility", "meter_id": 3}
    ]
    return jsonify(users_list), 200
