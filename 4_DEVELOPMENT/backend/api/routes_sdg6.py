"""
Smart Water Usage Advisor - SDG 6.4 Impact Blueprint
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/api/routes_sdg6.py

Provides:
- GET /api/sdg6/impact (Feature 5: SDG 6.4 Water-Use Efficiency & Impact Metrics)
"""

from flask import Blueprint, request, jsonify, g
from backend.api.middleware import auth_required, meter_access_required
from backend.services.sdg6_service import SDG6Service

sdg6_bp = Blueprint("sdg6_impact", __name__, url_prefix="/api/sdg6")
_sdg6_service = SDG6Service()


@sdg6_bp.route("/impact", methods=["GET"])
@auth_required
@meter_access_required
def get_sdg6_impact():
    """
    Feature 5: Computes UN SDG 6.4 impact indicators.
    Labels avoided leak volume strictly as 'Estimated avoided leak volume after resolution'.
    """
    user_id = int(request.args.get("user_id", g.current_user["user_id"]))
    res = _sdg6_service.get_impact_metrics(user_id=user_id)
    return jsonify(res), 200
