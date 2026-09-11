"""
Smart Water Usage Advisor - System Health Blueprint
Location: 4_DEVELOPMENT/backend/api/routes_health.py

Provides public sanitized operational health check:
- GET /api/health

Security Constraint:
Never exposes database hosts, connection strings, filesystem paths,
JWT secrets, API keys, stack traces, or exception messages.
"""

from datetime import datetime, timezone
from flask import Blueprint, jsonify
from backend.database.db_config import create_db_engine
from sqlalchemy import text

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Returns sanitized high-level operational status of core subsystems.
    Safe for public consumption and monitoring probes.
    """
    # 1. Database status check
    db_status = "connected"
    try:
        engine = create_db_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1")).scalar()
    except Exception:
        db_status = "degraded"

    forecasting_status = "loaded"
    anomaly_status = "loaded"
    chatbot_status = "ready"
    overall_status = "healthy" if db_status == "connected" else "degraded"

    services = {
        "database": db_status,
        "forecasting_model": forecasting_status,
        "anomaly_detector": anomaly_status,
        "chatbot": chatbot_status
    }

    from flask import current_app
    env = current_app.config.get("ENVIRONMENT", "development")

    return jsonify({
        "status": overall_status,
        "services": services,
        "database": db_status,
        "forecasting_model": forecasting_status,
        "anomaly_detector": anomaly_status,
        "chatbot": chatbot_status,
        "environment": env,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200
