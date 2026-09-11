"""
Smart Water Usage Advisor - Anomaly & Leak Detection Blueprint
Location: 4_DEVELOPMENT/backend/api/routes_anomalies.py

Provides modular REST endpoints for anomaly and leak detection:
- GET /api/v1/anomalies/meters/<int:meter_id>
"""

from flask import Blueprint, jsonify, g
from backend.dashboard_data_service import get_data_service
from backend.api.middleware import auth_required, meter_access_required

anomalies_bp = Blueprint("anomalies", __name__, url_prefix="/api/v1/anomalies")


@anomalies_bp.route("/meters/<int:meter_id>", methods=["GET"])
@auth_required
@meter_access_required
def get_meter_anomalies(meter_id: int):
    """
    Returns Phase 3B anomaly and leak detection incidents for authorized meter.
    Includes active alerts, severity classification, and diagnostic root cause.
    """
    ds = get_data_service()
    payload = ds.get_anomalies(user_id=meter_id)
    # Ensure anomalies key is present for REST integration
    payload["anomalies"] = payload.get("incidents", [])
    return jsonify(payload), 200
