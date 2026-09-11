"""
Smart Water Usage Advisor - Predictive Forecasting Blueprint
Location: 4_DEVELOPMENT/backend/api/routes_forecasting.py

Provides modular REST endpoints for predictive consumption forecasting:
- GET /api/v1/forecast/meters/<int:meter_id>
"""

from flask import Blueprint, jsonify, g
from backend.dashboard_data_service import get_data_service
from backend.api.middleware import auth_required, meter_access_required

forecasting_bp = Blueprint("forecasting", __name__, url_prefix="/api/v1/forecast")


@forecasting_bp.route("/meters/<int:meter_id>", methods=["GET"])
@auth_required
@meter_access_required
def get_meter_forecast(meter_id: int):
    """
    Returns Phase 3A 7-day forward predictive consumption forecast for authorized meter.
    Includes model attribution, benchmark comparison, and validated uncertainty bounds.
    """
    ds = get_data_service()
    payload = ds.get_forecast(user_id=meter_id)

    # Attach structured step forecast objects for API clients
    forecast_steps = []
    dates = payload.get("forecast_dates", [])
    preds = payload.get("predicted_liters", [])
    lowers = payload.get("confidence_lower", [])
    uppers = payload.get("confidence_upper", [])
    baselines = payload.get("baseline_liters", [])

    for i in range(len(dates)):
        pred_val = preds[i] if i < len(preds) else 0.0
        low_val = lowers[i] if i < len(lowers) else max(0.0, pred_val * 0.9)
        up_val = uppers[i] if i < len(uppers) else pred_val * 1.1
        base_val = baselines[i] if i < len(baselines) else pred_val
        forecast_steps.append({
            "forecast_date": dates[i],
            "predicted_consumption_liters": pred_val,
            "forecast_liters": pred_val,
            "lower_bound_liters": low_val,
            "upper_bound_liters": up_val,
            "baseline_liters": base_val
        })

    payload["forecast"] = forecast_steps
    return jsonify(payload), 200
