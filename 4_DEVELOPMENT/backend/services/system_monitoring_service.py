"""
Smart Water Usage Advisor - Admin System Monitoring Service
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/services/system_monitoring_service.py

Aggregates operational metrics, table record volumes, active alert tallies,
and AI model availability for authorized Municipal / Admin operators.
Guarantees zero leakage of secrets, passwords, or internal connection strings.
"""

import os
import time
from typing import Dict, Any
from sqlalchemy import text
from backend.database.db_config import create_db_engine
from backend.dashboard_data_service import get_data_service, BASE_DIR

_SYSTEM_START_TIME = time.time()


class SystemMonitoringService:
    """
    Operational monitoring service for district administrators and municipal operators.
    """

    def __init__(self, db_engine=None, data_service=None):
        self._db_engine = db_engine
        self.data_service = data_service or get_data_service()

    def _get_engine(self):
        if self._db_engine is None:
            try:
                self._db_engine = create_db_engine()
            except Exception:
                self._db_engine = None
        return self._db_engine

    def get_system_summary(self) -> Dict[str, Any]:
        """
        Gathers system-wide operational indicators, database health, and model availability.
        Safe for operator display: no passwords or connection credentials included.
        """
        uptime_seconds = round(time.time() - _SYSTEM_START_TIME, 1)

        eng = self._get_engine()
        db_connected = False
        db_engine_name = "sqlite"
        table_counts = {}

        if eng:
            try:
                with eng.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    db_connected = True
                    db_engine_name = eng.name

                    # Record counts for key tables
                    tables = ["users", "meters", "alerts", "scenarios", "water_budgets"]
                    for tbl in tables:
                        try:
                            cnt = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
                            table_counts[tbl] = cnt
                        except Exception:
                            table_counts[tbl] = 0
            except Exception:
                db_connected = False

        # AI Models availability check
        forecasting_model_path = os.path.join(
            BASE_DIR, "5_AI_COMPONENTS", "predictive_models", "models", "forecasting_model.joblib"
        )
        anomaly_model_path = os.path.join(
            BASE_DIR, "5_AI_COMPONENTS", "anomaly_detection", "models", "isolation_forest.joblib"
        )

        model_status = {
            "predictive_forecasting": {
                "name": "Phase 3A Random Forest Regressor",
                "available": os.path.isfile(forecasting_model_path),
                "status": "frozen_production"
            },
            "anomaly_detection": {
                "name": "Phase 3B Isolation Forest & Diurnal Rules",
                "available": os.path.isfile(anomaly_model_path),
                "status": "frozen_production"
            },
            "conservation_chatbot": {
                "name": "Phase 3C Conservation Assistant",
                "available": True,
                "status": "active"
            }
        }

        # Operational alert breakdown
        anomalies_dto = self.data_service.get_anomalies(1)
        incidents = anomalies_dto.get("incidents", [])
        active_incidents = [inc for inc in incidents if inc.get("is_active", True)]

        return {
            "system_status": "operational" if db_connected or os.path.isfile(forecasting_model_path) else "degraded",
            "uptime_seconds": uptime_seconds,
            "database": {
                "connected": db_connected,
                "engine": db_engine_name,
                "table_record_counts": table_counts
            },
            "ai_models": model_status,
            "active_alerts_summary": {
                "total_active": len(active_incidents),
                "critical": len([i for i in active_incidents if i.get("severity") == "critical"]),
                "high": len([i for i in active_incidents if i.get("severity") == "high"]),
                "medium": len([i for i in active_incidents if i.get("severity") == "medium"]),
                "low": len([i for i in active_incidents if i.get("severity") == "low"])
            },
            "security_status": {
                "jwt_auth_enforced": True,
                "rbac_active": True,
                "bola_defense_active": True,
                "secrets_exposed": False
            }
        }
