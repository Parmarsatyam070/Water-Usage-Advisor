"""
Smart Water Usage Advisor - Anomaly & Leak Detection Unit Tests
Location: 6_TESTING/unit_tests/test_anomaly_detection.py

Comprehensive test suite verifying:
1. Detector initialization
2. Detector fitting/calibration
3. Detector prediction functionality
4. Output schema validity
5. Numeric scores verification
6. Finite scores verification
7. Absence of NaN anomaly scores
8. Specificity verification (normal records are not classified anomalous)
9. Known leak detection (Meter 1 toilet leak)
10. Known burst detection (Meter 1 Day 71 burst)
11. Continuous leak rule (Minimum Night Flow)
12. Severity classification validity
13. Zero future data leakage
14. Historical-only rolling baseline calculations
15. Deterministic reproducibility with fixed seed
16. Isolation of ground-truth labels from detector features
17. Classification metrics accuracy
18. Event-level evaluation execution
19. Detection delay calculation correctness
20. Database persistence schema conformance
"""

import os
import sys
import tempfile
import pytest
import numpy as np
import pandas as pd

import importlib.util

ANOMALY_DIR = os.path.abspath("5_AI_COMPONENTS/anomaly_detection")
if ANOMALY_DIR not in sys.path:
    sys.path.append(ANOMALY_DIR)

DEV_DIR = os.path.abspath("4_DEVELOPMENT")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

import ml_models
from statistical_detector import StatisticalAnomalyDetector
from isolation_forest_detector import IsolationForestAnomalyDetector, ISO_FOREST_FEATURES
from leak_rules import RuleBasedLeakDetector
from severity import classify_severity, generate_evidence_explanation
from anomaly_detector import HybridWaterAnomalyDetector

# Load anomaly evaluation cleanly
_ev_spec = importlib.util.spec_from_file_location("anomaly_eval", os.path.join(ANOMALY_DIR, "evaluation.py"))
anomaly_eval = importlib.util.module_from_spec(_ev_spec)
_ev_spec.loader.exec_module(anomaly_eval)

compute_row_level_metrics = anomaly_eval.compute_row_level_metrics
evaluate_event_level_detection = anomaly_eval.evaluate_event_level_detection
evaluate_per_meter = anomaly_eval.evaluate_per_meter
evaluate_per_anomaly_type = anomaly_eval.evaluate_per_anomaly_type

@pytest.fixture(scope="module")
def raw_telemetry_df():
    csv_path = "4_DEVELOPMENT/data/generated/water_usage_data.csv"
    assert os.path.isfile(csv_path), f"Telemetry dataset missing: {csv_path}"
    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

@pytest.fixture(scope="module")
def fitted_detector(raw_telemetry_df):
    calib = raw_telemetry_df[raw_telemetry_df["timestamp"] < "2026-08-01"].copy()
    detector = HybridWaterAnomalyDetector(random_state=42)
    detector.fit(calib)
    return detector

# 1. Detector initializes
def test_detector_initializes():
    detector = HybridWaterAnomalyDetector()
    assert detector is not None
    assert not detector.is_fitted
    assert detector.stat_detector is not None
    assert detector.iso_detector is not None
    assert detector.rule_detector is not None

# 2. Detector trains/fits
def test_detector_trains_fits(raw_telemetry_df):
    calib = raw_telemetry_df[raw_telemetry_df["timestamp"] < "2026-07-15"].copy()
    detector = HybridWaterAnomalyDetector(random_state=42)
    detector.fit(calib)
    assert detector.is_fitted
    assert detector.stat_detector.is_fitted
    assert detector.iso_detector.is_fitted
    assert detector.calibration_metadata["calibration_samples"] == len(calib)

# 3. Detector predicts
def test_detector_predicts(raw_telemetry_df, fitted_detector):
    sub = raw_telemetry_df.head(100).copy()
    res = fitted_detector.detect(sub)
    assert len(res) == len(sub)
    assert "is_anomaly" in res.columns

# 4. Output schema valid
def test_output_schema_valid(raw_telemetry_df, fitted_detector):
    sub = raw_telemetry_df.head(50).copy()
    res = fitted_detector.detect(sub)
    required_cols = [
        "is_anomaly",
        "anomaly_type_detected",
        "anomaly_score",
        "severity",
        "explanation",
        "estimated_excess_liters",
        "deviation_percentage"
    ]
    for col in required_cols:
        assert col in res.columns, f"Required column {col} missing from output schema"

# 5. Scores numeric
def test_scores_are_numeric(raw_telemetry_df, fitted_detector):
    sub = raw_telemetry_df.head(50).copy()
    res = fitted_detector.detect(sub)
    assert issubclass(res["anomaly_score"].dtype.type, np.floating)

# 6. Scores finite
def test_scores_are_finite(raw_telemetry_df, fitted_detector):
    sub = raw_telemetry_df.head(100).copy()
    res = fitted_detector.detect(sub)
    assert np.isfinite(res["anomaly_score"]).all()

# 7. No NaN anomaly scores
def test_no_nan_anomaly_scores(raw_telemetry_df, fitted_detector):
    res = fitted_detector.detect(raw_telemetry_df.head(200))
    assert not res["anomaly_score"].isna().any()

# 8. Normal records are not all classified anomalous
def test_normal_records_not_all_anomalous(raw_telemetry_df, fitted_detector):
    normal_slice = raw_telemetry_df[(raw_telemetry_df["timestamp"] >= "2026-06-01") & (raw_telemetry_df["timestamp"] <= "2026-06-15")].copy()
    res = fitted_detector.detect(normal_slice)
    specificity = 1.0 - (res["is_anomaly"].sum() / len(res))
    assert specificity >= 0.90, f"Specificity too low ({specificity:.2f}), normal points over-flagged!"

# 9. Known leak anomaly can be detected
def test_known_leak_anomaly_detected(raw_telemetry_df, fitted_detector):
    leak_window = raw_telemetry_df[(raw_telemetry_df["meter_id"] == 1) & (raw_telemetry_df["timestamp"].between("2026-07-13", "2026-07-17"))].copy()
    res = fitted_detector.detect(leak_window)
    assert res["is_anomaly"].sum() > 0, "Known continuous leak was completely missed!"
    assert "leak" in res["anomaly_type_detected"].values

# 10. Burst anomaly detection works where ground truth exists
def test_burst_anomaly_detected(raw_telemetry_df, fitted_detector):
    surge_window = raw_telemetry_df[(raw_telemetry_df["meter_id"] == 1) & (raw_telemetry_df["timestamp"].dt.date == pd.to_datetime("2026-08-11").date())].copy()
    res = fitted_detector.detect(surge_window)
    burst_flags = res[res["anomaly_type_detected"] == "surge"]
    assert len(burst_flags) >= 1, "Known catastrophic burst was not flagged as surge!"
    assert (burst_flags["severity"] == "critical").any()

# 11. Continuous leak detection works (Minimum Night Flow)
def test_continuous_leak_rules(raw_telemetry_df):
    m1_nights = raw_telemetry_df[(raw_telemetry_df["meter_id"] == 1) & (raw_telemetry_df["timestamp"].between("2026-07-13", "2026-07-15"))].copy()
    rule_det = RuleBasedLeakDetector()
    evaluated = rule_det.evaluate_rules(m1_nights)
    assert evaluated["rule_leak"].sum() > 0, "Minimum Night Flow did not flag continuous leak days!"

# 12. Severity classification works
def test_severity_classification():
    allowed = {"critical", "high", "medium", "low"}
    assert classify_severity("surge", 350.0, 420.0, 0.95) in allowed
    assert classify_severity("leak", 16.5, 16.5, 0.85) in allowed
    assert classify_severity("low", 0.0, 0.0, 0.50) in allowed
    assert classify_severity("surge", 350.0, 420.0, 0.95) == "critical"

# 13. No future data leakage
def test_no_future_data_leakage(raw_telemetry_df):
    detector = StatisticalAnomalyDetector()
    calib = raw_telemetry_df.head(500).copy()
    detector.fit(calib)
    feats = detector.extract_statistical_features(calib)

    # Verify roll_median_24h at index i does not depend on observation at index i
    m1_feats = feats[feats["meter_id"] == 1].sort_values("timestamp").reset_index(drop=True)
    for i in range(7, len(m1_feats)):
        curr_val = m1_feats.iloc[i]["hourly_consumption_liters"]
        roll_med = m1_feats.iloc[i]["roll_median_24h"]
        strictly_past = m1_feats.iloc[i-24:i]["hourly_consumption_liters"].values if i >= 24 else m1_feats.iloc[:i]["hourly_consumption_liters"].values
        expected_past_med = float(np.median(strictly_past))
        assert np.isclose(roll_med, expected_past_med, atol=1e-2), f"Rolling median at {i} leaked current observation!"

# 14. Rolling baseline uses historical observations only
def test_rolling_baseline_historical_only(raw_telemetry_df):
    stat_det = StatisticalAnomalyDetector()
    stat_det.fit(raw_telemetry_df.head(500))
    feats = stat_det.extract_statistical_features(raw_telemetry_df.head(500))
    # Confirm lag_1h exactly equals previous row's hourly_consumption_liters
    m1 = feats[feats["meter_id"] == 1].reset_index(drop=True)
    for i in range(1, len(m1)):
        assert np.isclose(m1.iloc[i]["lag_1h"], m1.iloc[i-1]["hourly_consumption_liters"])

# 15. Deterministic results with fixed seed
def test_deterministic_results_with_fixed_seed(raw_telemetry_df):
    calib = raw_telemetry_df[raw_telemetry_df["timestamp"] < "2026-07-15"].copy()
    det1 = HybridWaterAnomalyDetector(random_state=42).fit(calib)
    det2 = HybridWaterAnomalyDetector(random_state=42).fit(calib)

    sample = raw_telemetry_df.head(100).copy()
    res1 = det1.detect(sample)
    res2 = det2.detect(sample)

    np.testing.assert_array_equal(res1["is_anomaly"].values, res2["is_anomaly"].values)
    np.testing.assert_array_almost_equal(res1["anomaly_score"].values, res2["anomaly_score"].values, decimal=4)

# 16. Ground-truth labels are not used as detector features
def test_ground_truth_labels_not_used_as_features():
    forbidden = ["anomaly_ground_truth", "ground_truth_id", "is_ground_truth"]
    for feat in ISO_FOREST_FEATURES:
        assert feat not in forbidden, f"Target label {feat} found in Isolation Forest feature list!"

# 17. Precision/recall/F1 calculations correct
def test_precision_recall_f1_calculations():
    y_true = np.array([True, True, False, False])
    y_pred = np.array([True, False, False, False])
    met = compute_row_level_metrics(y_true, y_pred)
    assert met["recall"] == 0.5
    assert met["precision"] == 1.0
    assert np.isclose(met["f1"], 2 * (1.0 * 0.5) / (1.0 + 0.5), atol=1e-2)

# 18. Event-level evaluation works
def test_event_level_evaluation(raw_telemetry_df, fitted_detector):
    detected = fitted_detector.detect(raw_telemetry_df)
    ev_met = evaluate_event_level_detection(detected)
    assert "event_detection_rate" in ev_met
    assert "mean_detection_delay_hours" in ev_met
    assert ev_met["event_detection_rate"] >= 0.75, "Expected macro events were missed!"

# 19. Detection delay calculation works
def test_detection_delay_calculation(raw_telemetry_df, fitted_detector):
    detected = fitted_detector.detect(raw_telemetry_df)
    ev_met = evaluate_event_level_detection(detected)
    assert isinstance(ev_met["mean_detection_delay_hours"], float)
    assert ev_met["mean_detection_delay_hours"] >= 0.0

# 20. Database persistence schema conformance
def test_database_persistence_schema_conformance(raw_telemetry_df, fitted_detector):
    sample = raw_telemetry_df[(raw_telemetry_df["meter_id"] == 1) & (raw_telemetry_df["timestamp"].between("2026-07-13", "2026-07-14"))].copy()
    detected = fitted_detector.detect(sample)
    records = fitted_detector.format_records_for_database(detected)

    assert len(records) > 0
    allowed_types = {"leak", "surge", "low", "unusual_pattern"}
    allowed_sevs = {"critical", "high", "medium", "low"}

    for r in records:
        assert r["anomaly_type"] in allowed_types, f"Invalid anomaly_type: {r['anomaly_type']}"
        assert r["severity"] in allowed_sevs, f"Invalid severity: {r['severity']}"
        assert r["consumption_value"] >= 0.0
        assert r["expected_value"] >= 0.0
        assert 0.0 <= r["leak_probability_score"] <= 1.0
        assert r["resolution_status"] == "pending"
