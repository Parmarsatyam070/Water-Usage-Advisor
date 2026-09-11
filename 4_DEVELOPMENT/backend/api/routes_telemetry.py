"""
Smart Water Usage Advisor - Telemetry Blueprint
Location: 4_DEVELOPMENT/backend/api/routes_telemetry.py

Provides modular REST endpoints for smart meter telemetry:
- GET /api/v1/telemetry/meters/<int:meter_id>/readings
- GET /api/v1/telemetry/meters/<int:meter_id>/daily
"""

from flask import Blueprint, request, jsonify, g
from backend.dashboard_data_service import get_data_service
from backend.api.middleware import auth_required, meter_access_required

telemetry_bp = Blueprint("telemetry", __name__, url_prefix="/api/v1/telemetry")


@telemetry_bp.route("/meters/<int:meter_id>/readings", methods=["GET"])
@auth_required
@meter_access_required
def get_meter_readings(meter_id: int):
    """Retrieves recent smart meter hourly telemetry for authorized meter."""
    limit = min(int(request.args.get("limit", 168)), 720)  # max 30 days hourly
    ds = get_data_service()
    raw_df = ds._load_telemetry()
    meter_df = raw_df[raw_df["meter_id"] == meter_id].sort_values("timestamp").tail(limit)

    readings = []
    for _, row in meter_df.iterrows():
        val = round(float(row["consumption_liters"]), 2)
        cum = round(float(row.get("cumulative_reading_m3", 12450.0)), 3)
        readings.append({
            "timestamp": str(row["timestamp"]),
            "meter_id": int(row["meter_id"]),
            "consumption_liters": val,
            "hourly_consumption_liters": val,
            "cumulative_reading_m3": cum,
            "temperature_celsius": round(float(row.get("temperature_celsius", 25.0)), 1)
        })

    return jsonify({
        "meter_id": meter_id,
        "record_count": len(readings),
        "readings": readings
    }), 200


@telemetry_bp.route("/meters/<int:meter_id>/daily", methods=["GET"])
@auth_required
@meter_access_required
def get_meter_daily(meter_id: int):
    """Retrieves aggregated daily consumption history for authorized meter."""
    limit = min(int(request.args.get("limit", 30)), 90)
    ds = get_data_service()
    ds._load_telemetry()
    daily_df = ds._daily_telemetry[ds._daily_telemetry["meter_id"] == meter_id].sort_values("date").tail(limit)

    records = []
    for _, row in daily_df.iterrows():
        records.append({
            "date": str(row["date"]),
            "meter_id": int(row["meter_id"]),
            "daily_consumption_liters": round(float(row["daily_consumption_liters"]), 1)
        })

    return jsonify({
        "meter_id": meter_id,
        "record_count": len(records),
        "daily_records": records,
        "daily_summary": records,
        "daily": records
    }), 200
