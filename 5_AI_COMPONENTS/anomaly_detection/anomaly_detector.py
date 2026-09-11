"""
Smart Water Usage Advisor - Unified Hybrid Water Anomaly & Leak Detector
Location: 5_AI_COMPONENTS/anomaly_detection/anomaly_detector.py

Orchestrates multi-layered anomaly detection:
1. Robust Statistical Thresholding (diurnal baselines, rolling median/MAD, robust z-scores)
2. Unsupervised Isolation Forest (normalized scale-invariant features)
3. Domain Rule-Based Signatures (Minimum Night Flow, surge spikes, nocturnal irrigation, low inactive periods)
4. Evidence-based Severity Classification & Human-Readable Explanations
5. Non-destructive anomaly flagging
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional

# Ensure module path resolution
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from statistical_detector import StatisticalAnomalyDetector
from isolation_forest_detector import IsolationForestAnomalyDetector
from leak_rules import RuleBasedLeakDetector
from severity import classify_severity, generate_evidence_explanation

class HybridWaterAnomalyDetector:
    """
    Production-capable hybrid water anomaly and leak detector.
    Combines statistical thresholds, Isolation Forest, and physical domain leak rules.
    """

    def __init__(
        self,
        z_threshold: float = 3.5,
        isolation_contamination: float = 0.035,
        night_flow_threshold: float = 8.0,
        burst_threshold: float = 150.0,
        random_state: int = 42
    ):
        self.stat_detector = StatisticalAnomalyDetector(z_threshold=z_threshold)
        self.iso_detector = IsolationForestAnomalyDetector(
            contamination=isolation_contamination,
            random_state=random_state
        )
        self.rule_detector = RuleBasedLeakDetector(
            night_flow_threshold_liters=night_flow_threshold,
            burst_threshold_liters=burst_threshold
        )
        self.is_fitted = False
        self.calibration_metadata = {}

    def fit(self, calibration_df: pd.DataFrame) -> "HybridWaterAnomalyDetector":
        """
        Calibrates statistical baselines and Isolation Forest on historical calibration data.
        Zero future information used.
        """
        # 1. Fit statistical diurnal baselines
        self.stat_detector.fit(calibration_df)

        # 2. Extract statistical features for Isolation Forest
        stat_features_df = self.stat_detector.extract_statistical_features(calibration_df)

        # 3. Fit Isolation Forest
        self.iso_detector.fit(stat_features_df)

        self.is_fitted = True
        self.calibration_metadata = {
            "calibration_samples": len(calibration_df),
            "calibration_start": str(calibration_df["timestamp"].min()),
            "calibration_end": str(calibration_df["timestamp"].max()),
            "isolation_contamination": self.iso_detector.contamination,
            "z_threshold": self.stat_detector.z_threshold
        }
        return self

    def detect(self, telemetry_df: pd.DataFrame) -> pd.DataFrame:
        """
        Runs hybrid anomaly detection across the supplied telemetry.
        Returns copy of DataFrame with non-destructive anomaly attributes.
        """
        if not self.is_fitted:
            raise RuntimeError("Detector must be fitted on historical calibration data before running detection.")

        # 1. Statistical Detection
        _, stat_df = self.stat_detector.detect(telemetry_df)

        # 2. Isolation Forest Scoring
        iso_scores = self.iso_detector.compute_anomaly_scores(stat_df)
        stat_df["isolation_score"] = iso_scores
        stat_df["iso_flag"] = self.iso_detector.predict(stat_df, score_threshold=0.65)

        # 3. Domain Rule Signatures
        rule_df = self.rule_detector.evaluate_rules(stat_df)

        # 4. Multi-Layer Arbitration
        # Anomaly is flagged if domain rule triggers OR strong combined ML/statistical deviation
        is_rule = rule_df["rule_any_flag"].values
        is_strong_ml_stat = (rule_df["isolation_score"].values >= 0.85) & (rule_df["stat_anomaly_flag"].values)

        is_anomaly = is_rule | is_strong_ml_stat

        rule_df["is_anomaly"] = is_anomaly

        # Assign canonical anomaly_type conforming to schema: ('leak', 'surge', 'low', 'unusual_pattern')
        anomaly_types = []
        severities = []
        explanations = []
        excess_liters_list = []
        deviation_pct_list = []

        for idx, row in rule_df.iterrows():
            if not row["is_anomaly"]:
                anomaly_types.append("none")
                severities.append("none")
                explanations.append("Normal consumption within expected historical envelope.")
                excess_liters_list.append(0.0)
                deviation_pct_list.append(0.0)
                continue

            # Classify type
            if row["rule_surge"]:
                a_type = "surge"
            elif row["rule_leak"]:
                a_type = "leak"
            elif row["rule_unusual_pattern"]:
                a_type = "unusual_pattern"
            elif row["rule_low"]:
                a_type = "low"
            elif row["diurnal_zscore"] > 0:
                a_type = "surge" if row["rate_of_change_1h"] > 80.0 else "unusual_pattern"
            else:
                a_type = "low"

            obs_val = float(row["hourly_consumption_liters"])
            base_val = float(row["base_median"])
            dev_liters = round(max(0.0, obs_val - base_val), 3)
            denom = max(base_val, 1.0)
            dev_pct = round(((obs_val - base_val) / denom) * 100.0, 2)

            score = float(row["isolation_score"])
            severity = classify_severity(a_type, dev_liters, obs_val, score)
            explanation = generate_evidence_explanation(
                a_type, obs_val, base_val, dev_liters, int(row["hour"]), int(row["meter_id"])
            )

            anomaly_types.append(a_type)
            severities.append(severity)
            explanations.append(explanation)
            excess_liters_list.append(dev_liters)
            deviation_pct_list.append(dev_pct)

        rule_df["anomaly_type_detected"] = anomaly_types
        rule_df["severity"] = severities
        rule_df["explanation"] = explanations
        rule_df["estimated_excess_liters"] = excess_liters_list
        rule_df["deviation_percentage"] = deviation_pct_list
        rule_df["anomaly_score"] = rule_df["isolation_score"]

        return rule_df

    def format_records_for_database(self, detected_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Converts detected anomaly rows into records ready for the authoritative `anomalies` table.
        """
        anomalies_only = detected_df[detected_df["is_anomaly"]].copy()
        records = []

        for _, row in anomalies_only.iterrows():
            ts_str = row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"])
            records.append({
                "meter_id": int(row["meter_id"]),
                "user_id": int(row["user_id"]),
                "detection_timestamp": ts_str,
                "anomaly_type": row["anomaly_type_detected"],
                "consumption_value": float(round(row["hourly_consumption_liters"], 3)),
                "expected_value": float(round(row["base_median"], 3)),
                "deviation_percentage": float(row["deviation_percentage"]),
                "severity": row["severity"],
                "leak_probability_score": float(row["anomaly_score"]),
                "alert_sent": False,
                "alert_timestamp": None,
                "user_acknowledged": False,
                "resolution_status": "pending",
                "explanation": row["explanation"]
            })

        return records

    def save(self, model_dir: str = "5_AI_COMPONENTS/anomaly_detection/models"):
        """Serializes detector artifacts to disk."""
        os.makedirs(model_dir, exist_ok=True)
        self.iso_detector.save(model_dir)
        meta_path = os.path.join(model_dir, "detector_metadata.json")
        baseline_path = os.path.join(model_dir, "diurnal_baselines.csv")

        self.stat_detector.diurnal_baselines.to_csv(baseline_path, index=False)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self.calibration_metadata, f, indent=2)

        print(f"Hybrid anomaly detector artifacts saved to {model_dir}")

    def load(self, model_dir: str = "5_AI_COMPONENTS/anomaly_detection/models"):
        """Loads serialized detector artifacts from disk."""
        self.iso_detector.load(model_dir)
        meta_path = os.path.join(model_dir, "detector_metadata.json")
        baseline_path = os.path.join(model_dir, "diurnal_baselines.csv")

        if os.path.isfile(baseline_path):
            self.stat_detector.diurnal_baselines = pd.read_csv(baseline_path)
            self.stat_detector.is_fitted = True

        if os.path.isfile(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.calibration_metadata = json.load(f)

        self.is_fitted = True
        print(f"Hybrid anomaly detector loaded from {model_dir}")

HybridAnomalyDetector = HybridWaterAnomalyDetector

if __name__ == "__main__":
    csv_path = "4_DEVELOPMENT/data/generated/water_usage_data.csv"
    if not os.path.isfile(csv_path):
        print(f"Telemetry file not found: {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Calibration window: Days 1-60 (June 1 - July 31)
    calib = df[df["timestamp"] < "2026-08-01"].copy()
    print(f"Fitting Hybrid Anomaly Detector on calibration window ({len(calib)} rows)...")

    detector = HybridWaterAnomalyDetector()
    detector.fit(calib)

    print("Running detection on full telemetry...")
    results = detector.detect(df)
    anom_count = results["is_anomaly"].sum()
    print(f"Detected {anom_count} anomalous readings out of {len(df)} total observations.")

    detector.save()
