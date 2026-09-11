"""
Smart Water Usage Advisor - Alert History & Resolution Blueprint
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/api/routes_alerts_history.py

Provides:
- GET   /api/alerts/history (Feature 4: Alert History with Status Filtering)
- PATCH /api/alerts/<int:alert_id>/status (Feature 4: Alert Status & Resolution Tracking)

Enforces strict BOLA / IDOR protection and role-based boundaries.
"""

from flask import Blueprint, request, jsonify, g
from backend.api.middleware import auth_required
from backend.services.alert_history_service import AlertHistoryService

alerts_history_bp = Blueprint("alerts_history", __name__, url_prefix="/api/alerts")
_alerts_service = AlertHistoryService()


@alerts_history_bp.route("/history", methods=["GET"])
@auth_required
def get_alert_history():
    """
    Feature 4: Retrieve paginated alert history with status filtering.
    """
    user_id = g.current_user["user_id"]
    user_role = g.current_user.get("user_type", "household")

    status_filter = request.args.get("status")
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))

    try:
        res = _alerts_service.get_alert_history(
            user_id=user_id,
            user_role=user_role,
            status=status_filter,
            limit=limit,
            offset=offset
        )
        return jsonify(res), 200
    except ValueError as ve:
        return jsonify({
            "error": str(ve),
            "error_code": "INVALID_PARAMETER",
            "status_code": 400
        }), 400


@alerts_history_bp.route("/<int:alert_id>/status", methods=["PATCH"])
@auth_required
def update_alert_status(alert_id: int):
    """
    Feature 4: Update alert status (NEW -> ACKNOWLEDGED -> RESOLVED / DISMISSED).
    BOLA defense: Only owner or municipal role can mutate alert.
    """
    user_id = g.current_user["user_id"]
    user_role = g.current_user.get("user_type", "household")

    body = request.get_json(silent=True) or {}
    new_status = body.get("status")
    note = body.get("resolution_note")

    if not new_status:
        return jsonify({
            "error": "Missing required field 'status'.",
            "error_code": "INVALID_PARAMETER",
            "status_code": 400
        }), 400

    try:
        res = _alerts_service.update_alert_status(
            alert_id=alert_id,
            new_status=new_status,
            user_id=user_id,
            user_role=user_role,
            resolution_note=note
        )
        return jsonify(res), 200
    except PermissionError as pe:
        return jsonify({
            "error": str(pe),
            "error_code": "FORBIDDEN",
            "status_code": 403
        }), 403
    except ValueError as ve:
        err_msg = str(ve)
        status_code = 404 if "not found" in err_msg.lower() else 400
        err_code = "NOT_FOUND" if status_code == 404 else "INVALID_PARAMETER"
        return jsonify({
            "error": err_msg,
            "error_code": err_code,
            "status_code": status_code
        }), status_code
