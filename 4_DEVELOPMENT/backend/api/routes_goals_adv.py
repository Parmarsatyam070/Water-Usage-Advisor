"""
Smart Water Usage Advisor - Smart Goals Blueprint
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/api/routes_goals_adv.py

Provides:
- GET  /api/goals/recommendations (Feature 6: 3 Tailored Smart Goal Recommendations)
- POST /api/goals/adopt (Feature 6: Direct Goal Adoption)
"""

from flask import Blueprint, request, jsonify, g
from backend.api.middleware import auth_required, meter_access_required
from backend.services.goal_recommendation_service import GoalRecommendationService

goals_adv_bp = Blueprint("goals_adv", __name__, url_prefix="/api/goals")
_goals_service = GoalRecommendationService()


@goals_adv_bp.route("/recommendations", methods=["GET"])
@auth_required
@meter_access_required
def get_goal_recommendations():
    """
    Feature 6: Returns 3 tailored smart goal recommendations respecting WHO health guidelines.
    """
    user_id = int(request.args.get("user_id", g.current_user["user_id"]))
    res = _goals_service.generate_recommendations(user_id=user_id)
    return jsonify(res), 200


@goals_adv_bp.route("/adopt", methods=["POST"])
@auth_required
@meter_access_required
def adopt_goal():
    """
    Feature 6: Adopts a smart goal into the active database records.
    """
    body = request.get_json(silent=True) or {}
    user_id = int(body.get("user_id", g.current_user["user_id"]))

    goal_type = body.get("goal_type")
    target_value = body.get("target_value")
    target_unit = body.get("target_unit", "liters")
    duration_days = body.get("duration_days", 30)

    if not goal_type or target_value is None:
        return jsonify({
            "error": "Missing required fields 'goal_type' or 'target_value'.",
            "error_code": "INVALID_PARAMETER",
            "status_code": 400
        }), 400

    try:
        target_value = float(target_value)
        duration_days = int(duration_days)
        res = _goals_service.adopt_goal(
            user_id=user_id,
            goal_type=goal_type,
            target_value=target_value,
            target_unit=target_unit,
            duration_days=duration_days
        )
        return jsonify(res), 200
    except ValueError as ve:
        return jsonify({
            "error": str(ve),
            "error_code": "INVALID_PARAMETER",
            "status_code": 400
        }), 400
