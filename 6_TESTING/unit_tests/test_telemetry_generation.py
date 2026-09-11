"""
Unit tests for synthetic telemetry generation.
Verifies record counts, profile attributes, diurnal variance, and anomaly ground-truth tagging.
"""

import os
import pytest
import pandas as pd
import numpy as np

TELEMETRY_CSV = "4_DEVELOPMENT/data/generated/water_usage_data.csv"
ANOMALIES_CSV = "4_DEVELOPMENT/data/generated/ground_truth_anomalies.csv"

@pytest.fixture(scope="module")
def telemetry_df():
    assert os.path.isfile(TELEMETRY_CSV), f"Telemetry file {TELEMETRY_CSV} not found."
    return pd.read_csv(TELEMETRY_CSV)

@pytest.fixture(scope="module")
def anomalies_df():
    assert os.path.isfile(ANOMALIES_CSV), f"Anomalies file {ANOMALIES_CSV} not found."
    return pd.read_csv(ANOMALIES_CSV)

def test_telemetry_record_count(telemetry_df):
    """Verify exact 6,480 hourly records (3 meters x 90 days x 24 hours)."""
    assert len(telemetry_df) == 6480

def test_profiles_represented(telemetry_df):
    """Ensure all three required meter IDs are present."""
    meter_ids = set(telemetry_df["meter_id"].unique())
    assert meter_ids == {1, 2, 3}

def test_non_negative_values(telemetry_df):
    """Ensure consumption and cumulative values are non-negative."""
    assert (telemetry_df["hourly_consumption_liters"] >= 0).all()
    assert (telemetry_df["cumulative_reading"] >= 0).all()

def test_monotonic_cumulative_reading(telemetry_df):
    """Ensure cumulative readings per meter are strictly non-decreasing."""
    for meter_id, group in telemetry_df.groupby("meter_id"):
        diffs = group["cumulative_reading"].diff().dropna()
        assert (diffs >= -1e-5).all(), f"Meter {meter_id} has decreasing cumulative values."

def test_diurnal_pattern_difference(telemetry_df):
    """Ensure peak hours (morning/evening) have higher average consumption than night hours."""
    telemetry_df["hour"] = pd.to_datetime(telemetry_df["timestamp"]).dt.hour
    night_mean = telemetry_df[telemetry_df["hour"].isin([1, 2, 3])]["hourly_consumption_liters"].mean()
    evening_mean = telemetry_df[telemetry_df["hour"].isin([18, 19, 20])]["hourly_consumption_liters"].mean()
    assert evening_mean > night_mean * 2.0, "Evening consumption should significantly exceed night baseline."

def test_anomaly_ground_truth_types(anomalies_df):
    """Ensure all 4 ground-truth anomaly categories are represented."""
    expected_types = {"leak", "surge", "low", "unusual_pattern"}
    observed_types = set(anomalies_df["anomaly_type"].unique())
    assert expected_types.issubset(observed_types)
