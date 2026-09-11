"""
Smart Water Usage Advisor - Anomaly Inference & Database Persistence Engine
Location: 5_AI_COMPONENTS/anomaly_detection/inference.py

Provides:
1. Sequential real-time streaming inference simulating timestamp-by-timestamp arrival.
2. Safe parameterized persistence into the authoritative PostgreSQL `anomalies` table.
3. Non-destructive anomaly flagging interface to protect downstream forecasting models.
"""

import os
import sys
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

# Ensure module import resolution
AI_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if AI_MODULE_DIR not in sys.path:
    sys.path.insert(0, AI_MODULE_DIR)

from anomaly_detector import HybridWaterAnomalyDetector

def detect_realtime_observation(
    historical_window_df: pd.DataFrame,
    current_observation: pd.Series,
    detector: HybridWaterAnomalyDetector
) -> Dict[str, Any]:
    """
    Simulates real-time streaming detection for an incoming telemetry reading at timestamp T.
    Strictly uses historical observations up to T (no future information).
    """
    if not detector.is_fitted:
        raise RuntimeError("Detector must be fitted prior to real-time inference.")

    # Combine historical window with current observation
    stream_slice = pd.concat([historical_window_df, pd.DataFrame([current_observation])], ignore_index=True)
    detected_slice = detector.detect(stream_slice)
    current_result = detected_slice.iloc[-1]

    return {
        "meter_id": int(current_result["meter_id"]),
        "user_id": int(current_result["user_id"]),
        "timestamp": str(current_result["timestamp"]),
        "is_anomaly": bool(current_result["is_anomaly"]),
        "anomaly_type": current_result["anomaly_type_detected"],
        "anomaly_score": float(current_result["anomaly_score"]),
        "severity": current_result["severity"],
        "observed_consumption": float(current_result["hourly_consumption_liters"]),
        "expected_baseline": float(current_result["base_median"]),
        "deviation_liters": float(current_result["estimated_excess_liters"]),
        "explanation": current_result["explanation"]
    }

def persist_anomalies_to_database(
    anomaly_records: List[Dict[str, Any]],
    engine=None
) -> int:
    """
    Safely persists detected anomaly records into the authoritative PostgreSQL `anomalies` table.
    Uses parameterized SQL to prevent SQL injection.
    Credentials loaded from environment (.env).
    """
    if not anomaly_records:
        return 0

    if engine is None:
        try:
            sys.path.insert(0, os.path.abspath("4_DEVELOPMENT/backend/database"))
            from db_config import create_db_engine
            engine = create_db_engine()
        except Exception as e:
            print(f"Database connection unavailable for persistence: {e}")
            return 0

    from sqlalchemy import text

    inserted = 0
    insert_sql = text("""
        INSERT INTO anomalies (
            meter_id, user_id, detection_timestamp, anomaly_type,
            consumption_value, expected_value, deviation_percentage,
            severity, leak_probability_score, alert_sent,
            alert_timestamp, user_acknowledged, resolution_status
        )
        VALUES (
            :meter_id, :user_id, :detection_timestamp, :anomaly_type,
            :consumption_value, :expected_value, :deviation_percentage,
            :severity, :leak_probability_score, :alert_sent,
            :alert_timestamp, :user_acknowledged, :resolution_status
        );
    """)

    with engine.begin() as conn:
        for r in anomaly_records:
            # Map parameters matching schema CHECK constraints
            conn.execute(insert_sql, {
                "meter_id": r["meter_id"],
                "user_id": r["user_id"],
                "detection_timestamp": r["detection_timestamp"],
                "anomaly_type": r["anomaly_type"],
                "consumption_value": r["consumption_value"],
                "expected_value": r["expected_value"],
                "deviation_percentage": r.get("deviation_percentage", 0.0),
                "severity": r["severity"],
                "leak_probability_score": r.get("leak_probability_score", r.get("anomaly_score", 0.9)),
                "alert_sent": False,
                "alert_timestamp": None,
                "user_acknowledged": False,
                "resolution_status": "pending"
            })
            inserted += 1

    print(f"Successfully persisted {inserted} anomaly records into the authoritative anomalies table.")
    return inserted

def generate_forecaster_clean_flags(
    telemetry_df: pd.DataFrame,
    detected_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Non-destructively annotates raw telemetry with anomaly flags for downstream forecaster protection.
    Does NOT modify or delete raw telemetry observations.
    """
    out_df = telemetry_df.copy()
    out_df["is_anomaly_flag"] = detected_df["is_anomaly"].values
    out_df["detected_anomaly_type"] = detected_df["anomaly_type_detected"].values
    out_df["anomaly_severity"] = detected_df["severity"].values
    return out_df
