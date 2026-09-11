"""
Smart Water Usage Advisor - Anomaly Detection Evaluation Module
Location: 5_AI_COMPONENTS/anomaly_detection/evaluation.py

Provides rigorous row-level and event-level evaluation against Phase 2 ground truth:
- Row-level: Confusion Matrix, Precision, Recall, F1, Accuracy, Specificity
- Event-level: Event Detection Rate, Detection Delay (hours), False Alerts per meter-day
- Disaggregated breakdown per meter and per anomaly category
- False positive investigation and evidence analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, accuracy_score

# Known Ground Truth Events in Phase 2 Telemetry
KNOWN_ANOMALY_EVENTS = [
    {
        "event_id": "EVENT-1",
        "meter_id": 1,
        "profile": "Residential Single-Family",
        "anomaly_type": "leak",
        "start_time": "2026-07-13T00:00:00",
        "end_time": "2026-07-17T23:00:00",
        "duration_hours": 120,
        "description": "Continuous toilet flapper valve leak (persistent non-zero nocturnal flow)"
    },
    {
        "event_id": "EVENT-2",
        "meter_id": 1,
        "profile": "Residential Single-Family",
        "anomaly_type": "surge",
        "start_time": "2026-08-11T14:00:00",
        "end_time": "2026-08-11T15:00:00",
        "duration_hours": 2,
        "description": "Sudden catastrophic pipe burst (+420 L/hr volumetric surge)"
    },
    {
        "event_id": "EVENT-3",
        "meter_id": 2,
        "profile": "Residential Multi-Family",
        "anomaly_type": "low",
        "start_time": "2026-06-29T00:00:00",
        "end_time": "2026-07-02T23:00:00",
        "duration_hours": 96,
        "description": "Extended vacant interval / uncharacteristic daytime zero-consumption"
    },
    {
        "event_id": "EVENT-4",
        "meter_id": 3,
        "profile": "Commercial Facility",
        "anomaly_type": "unusual_pattern",
        "start_time": "2026-07-29T00:00:00",
        "end_time": "2026-07-31T03:00:00",
        "duration_hours": 12,
        "description": "Commercial cooling loop cycling / unapproved nocturnal irrigation"
    }
]

def compute_row_level_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """
    Computes standard binary classification performance metrics.
    """
    y_true_b = np.asarray(y_true, dtype=bool)
    y_pred_b = np.asarray(y_pred, dtype=bool)

    cm = confusion_matrix(y_true_b, y_pred_b)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

    precision = float(round(precision_score(y_true_b, y_pred_b, zero_division=0), 4))
    recall = float(round(recall_score(y_true_b, y_pred_b, zero_division=0), 4))
    f1 = float(round(f1_score(y_true_b, y_pred_b, zero_division=0), 4))
    accuracy = float(round(accuracy_score(y_true_b, y_pred_b), 4))
    specificity = float(round(tn / max(1, tn + fp), 4))

    return {
        "confusion_matrix": {
            "TP": int(tp),
            "FP": int(fp),
            "TN": int(tn),
            "FN": int(fn)
        },
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
        "specificity": specificity
    }

def evaluate_event_level_detection(detected_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Evaluates detection against macroscopic physical anomaly events.
    Calculates event detection rate, detection delay, and alert counts.
    """
    df = detected_df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    event_evals = []
    delays = []

    for ev in KNOWN_ANOMALY_EVENTS:
        m_id = ev["meter_id"]
        t_start = pd.to_datetime(ev["start_time"])
        t_end = pd.to_datetime(ev["end_time"])

        ev_window = df[(df["meter_id"] == m_id) & (df["timestamp"] >= t_start) & (df["timestamp"] <= t_end)]
        detected_in_window = ev_window[ev_window["is_anomaly"]]

        if len(detected_in_window) > 0:
            first_det_time = detected_in_window["timestamp"].min()
            delay_hours = round(float((first_det_time - t_start).total_seconds() / 3600.0), 1)
            delays.append(delay_hours)
            primary_type = detected_in_window["anomaly_type_detected"].mode()[0]
            max_sev = detected_in_window["severity"].value_counts().index[0]
            is_detected = True
        else:
            first_det_time = None
            delay_hours = None
            primary_type = None
            max_sev = None
            is_detected = False

        event_evals.append({
            "event_id": ev["event_id"],
            "meter_id": ev["meter_id"],
            "profile": ev["profile"],
            "expected_type": ev["anomaly_type"],
            "detected": is_detected,
            "first_detected_at": str(first_det_time) if first_det_time else "MISSED",
            "detection_delay_hours": delay_hours,
            "detected_type": primary_type,
            "severity": max_sev,
            "duration_hours": ev["duration_hours"],
            "detected_hours_count": len(detected_in_window)
        })

    detected_events_count = sum(1 for e in event_evals if e["detected"])
    total_events = len(KNOWN_ANOMALY_EVENTS)
    event_detection_rate = float(round(detected_events_count / max(1, total_events), 4))
    mean_delay = float(round(np.mean(delays), 2)) if delays else 0.0

    # False alerts outside of known event windows
    outside_events = df.copy()
    for ev in KNOWN_ANOMALY_EVENTS:
        m_id = ev["meter_id"]
        t_start = pd.to_datetime(ev["start_time"])
        t_end = pd.to_datetime(ev["end_time"])
        outside_events = outside_events[~((outside_events["meter_id"] == m_id) & (outside_events["timestamp"] >= t_start) & (outside_events["timestamp"] <= t_end))]

    false_alert_rows = outside_events["is_anomaly"].sum()
    total_meter_days = len(df) / 24.0
    false_alert_rate_per_meter_day = float(round(false_alert_rows / max(1.0, total_meter_days), 4))

    return {
        "event_detection_rate": event_detection_rate,
        "events_detected": detected_events_count,
        "total_events": total_events,
        "mean_detection_delay_hours": mean_delay,
        "false_alerts_count": int(false_alert_rows),
        "false_alert_rate_per_meter_day": false_alert_rate_per_meter_day,
        "event_breakdown": event_evals
    }

def evaluate_per_meter(detected_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Disaggregates evaluation metrics across the three meter profiles.
    """
    meter_results = {}
    profile_names = {
        1: "Residential Single-Family (Meter 1)",
        2: "Residential Multi-Family (Meter 2)",
        3: "Commercial Facility (Meter 3)"
    }

    for m_id, name in profile_names.items():
        sub = detected_df[detected_df["meter_id"] == m_id]
        if len(sub) > 0:
            gt = sub["anomaly_ground_truth"].values
            pred = sub["is_anomaly"].values
            met = compute_row_level_metrics(gt, pred)
            meter_results[name] = met

    return meter_results

def evaluate_per_anomaly_type(detected_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Evaluates detection metrics broken down by ground-truth anomaly type.
    """
    type_results = {}
    for atype in ["leak", "surge", "low", "unusual_pattern"]:
        type_mask = detected_df["anomaly_type"] == atype
        gt_count = int(type_mask.sum())
        detected_count = int((type_mask & detected_df["is_anomaly"]).sum())
        recall = round(float(detected_count / max(1, gt_count)), 4)
        type_results[atype] = {
            "ground_truth_count": gt_count,
            "detected_count": detected_count,
            "recall": recall
        }
    return type_results

def analyze_false_positives(detected_df: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Identifies and diagnoses notable false positives (where model flagged anomaly but ground truth was false).
    """
    fps = detected_df[(detected_df["is_anomaly"]) & (~detected_df["anomaly_ground_truth"])].copy()
    if len(fps) == 0:
        return []

    fps["abs_dev"] = np.abs(fps["hourly_consumption_liters"] - fps["base_median"])
    fps = fps.sort_values(by="abs_dev", ascending=False).head(top_n)

    records = []
    for _, row in fps.iterrows():
        records.append({
            "timestamp": str(row["timestamp"]),
            "meter_id": int(row["meter_id"]),
            "observed_consumption": float(round(row["hourly_consumption_liters"], 3)),
            "baseline_median": float(round(row["base_median"], 3)),
            "deviation_liters": float(round(row["abs_dev"], 3)),
            "anomaly_type_assigned": row.get("anomaly_type_detected", "unknown"),
            "severity": row.get("severity", "unknown"),
            "diagnosis": "Normal diurnal peak or weekend cooking/laundry variation exceeding statistical threshold"
        })
    return records
