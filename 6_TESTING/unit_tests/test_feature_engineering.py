"""
Unit tests for data preprocessing and feature engineering.
Verifies temporal extraction, cyclical transformations, lag creations, and aggregation summaries.
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath("4_DEVELOPMENT/utils"))
from data_preprocessing import WaterDataPreprocessor

TELEMETRY_CSV = "4_DEVELOPMENT/data/generated/water_usage_data.csv"

@pytest.fixture(scope="module")
def sample_telemetry():
    df = pd.read_csv(TELEMETRY_CSV).head(300)
    return df

def test_feature_engineering_columns(sample_telemetry):
    """Ensure all required engineered features are created."""
    preprocessor = WaterDataPreprocessor()
    df_feat = preprocessor.prepare_features(sample_telemetry)

    expected_cols = [
        "hour", "day_of_week", "day_of_month", "month", "is_weekend",
        "hour_sin", "hour_cos", "dow_sin", "dow_cos",
        "lag_1h", "lag_24h", "rolling_mean_24h", "rolling_std_24h",
        "is_night_window", "profile_type"
    ]
    for col in expected_cols:
        assert col in df_feat.columns, f"Engineered column {col} missing."

def test_cyclical_encoding_range(sample_telemetry):
    """Verify sine and cosine cyclical encodings remain within [-1.0, 1.0]."""
    preprocessor = WaterDataPreprocessor()
    df_feat = preprocessor.prepare_features(sample_telemetry)

    assert df_feat["hour_sin"].between(-1.001, 1.001).all()
    assert df_feat["hour_cos"].between(-1.001, 1.001).all()
    assert df_feat["dow_sin"].between(-1.001, 1.001).all()
    assert df_feat["dow_cos"].between(-1.001, 1.001).all()

def test_aggregation_summary(sample_telemetry):
    """Verify aggregation summary correctly groups by daily frequency."""
    preprocessor = WaterDataPreprocessor()
    daily = preprocessor.aggregate_summary(sample_telemetry, freq="D")
    assert "total_liters" in daily.columns
    assert "avg_temperature" in daily.columns
    assert (daily["total_liters"] >= 0).all()
