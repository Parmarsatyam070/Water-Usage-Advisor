"""
Smart Water Usage Advisor - Predictive Model Unit Tests
Location: 6_TESTING/unit_tests/test_ml_models.py

Comprehensive test suite validating:
1. Model training functionality
2. Model prediction generation
3. Numeric type of predictions
4. Non-negativity constraint enforcement
5. Prediction output shape consistency
6. Absence of NaN / inf predictions
7. Feature column consistency
8. Model serialization and deserialization via joblib
9. Deterministic consistency between saved and loaded models
10. Strict chronological split preservation (no leakage/overlap)
11. Anti-leakage compliance (historical shift >= 1 for rolling and lags)
12. Baseline model evaluation (Naive 1d and Seasonal Naive 7d)
13. Safe zero-handling in MAPE calculation
14. Model vs Baseline Comparison table generation
"""

import os
import sys
import tempfile
import pytest
import numpy as np
import pandas as pd

# Add source paths
sys.path.insert(0, os.path.abspath("5_AI_COMPONENTS/predictive_models"))
sys.path.insert(0, os.path.abspath("4_DEVELOPMENT"))

from preprocessing import (
    aggregate_hourly_to_daily,
    extract_forecasting_features,
    chronological_train_val_test_split,
    ALL_PREDICTOR_FEATURES
)
from forecasting_model import WaterConsumptionForecaster
from evaluation import (
    calculate_safe_mape,
    compute_regression_metrics,
    evaluate_baseline_models,
    generate_model_vs_baseline_comparison,
    evaluate_per_profile
)
from inference import generate_7day_forecast
import ml_models

@pytest.fixture(scope="module")
def sample_telemetry_df():
    """Loads actual Phase 2 telemetry dataset."""
    csv_path = "4_DEVELOPMENT/data/generated/water_usage_data.csv"
    assert os.path.isfile(csv_path), f"Telemetry file not found: {csv_path}"
    return pd.read_csv(csv_path)

@pytest.fixture(scope="module")
def prepared_splits(sample_telemetry_df):
    """Aggregates, extracts features, and splits chronologically."""
    daily_df = aggregate_hourly_to_daily(sample_telemetry_df)
    feat_df = extract_forecasting_features(daily_df)
    train_df, val_df, test_df = chronological_train_val_test_split(feat_df, val_days=14, test_days=14)
    return train_df, val_df, test_df, feat_df

# 1. Model can train
def test_model_training(prepared_splits):
    train_df, val_df, _, _ = prepared_splits
    combined_train = pd.concat([train_df, val_df], ignore_index=True)

    forecaster = WaterConsumptionForecaster(algorithm="random_forest", model_params={"n_estimators": 20, "max_depth": 4})
    duration = forecaster.train(combined_train, combined_train["daily_consumption_liters"].values)

    assert forecaster.model is not None
    assert duration >= 0.0
    assert forecaster.training_metadata["training_samples"] == len(combined_train)

# 2. Model can predict
def test_model_prediction(prepared_splits):
    train_df, val_df, test_df, _ = prepared_splits
    combined_train = pd.concat([train_df, val_df], ignore_index=True)

    forecaster = WaterConsumptionForecaster(algorithm="random_forest", model_params={"n_estimators": 20, "max_depth": 4})
    forecaster.train(combined_train, combined_train["daily_consumption_liters"].values)

    preds = forecaster.predict(test_df)
    assert preds is not None
    assert len(preds) == len(test_df)

# 3. Predictions are numeric
def test_predictions_are_numeric(prepared_splits):
    train_df, val_df, test_df, _ = prepared_splits
    combined_train = pd.concat([train_df, val_df], ignore_index=True)

    forecaster = WaterConsumptionForecaster(algorithm="random_forest", model_params={"n_estimators": 20, "max_depth": 4})
    forecaster.train(combined_train, combined_train["daily_consumption_liters"].values)

    preds = forecaster.predict(test_df)
    assert issubclass(preds.dtype.type, np.floating)

# 4. Predictions are non-negative
def test_predictions_are_non_negative(prepared_splits):
    train_df, val_df, test_df, _ = prepared_splits
    combined_train = pd.concat([train_df, val_df], ignore_index=True)

    forecaster = WaterConsumptionForecaster(algorithm="random_forest", model_params={"n_estimators": 20, "max_depth": 4})
    forecaster.train(combined_train, combined_train["daily_consumption_liters"].values)

    preds = forecaster.predict(test_df)
    assert np.all(preds >= 0.0), "Found negative prediction in output!"

# 5. Prediction output has expected shape
def test_prediction_output_shape(prepared_splits):
    train_df, val_df, test_df, _ = prepared_splits
    combined_train = pd.concat([train_df, val_df], ignore_index=True)

    forecaster = WaterConsumptionForecaster(algorithm="random_forest", model_params={"n_estimators": 20, "max_depth": 4})
    forecaster.train(combined_train, combined_train["daily_consumption_liters"].values)

    preds = forecaster.predict(test_df)
    assert preds.shape == (len(test_df),)

# 6. No NaN predictions
def test_no_nan_predictions(prepared_splits):
    train_df, val_df, test_df, _ = prepared_splits
    combined_train = pd.concat([train_df, val_df], ignore_index=True)

    forecaster = WaterConsumptionForecaster(algorithm="random_forest", model_params={"n_estimators": 20, "max_depth": 4})
    forecaster.train(combined_train, combined_train["daily_consumption_liters"].values)

    preds = forecaster.predict(test_df)
    assert not np.isnan(preds).any(), "Found NaN in predictions!"
    assert not np.isinf(preds).any(), "Found Inf in predictions!"

# 7. Feature columns are consistent
def test_feature_columns_consistent(prepared_splits):
    train_df, _, test_df, _ = prepared_splits
    for feat in ALL_PREDICTOR_FEATURES:
        assert feat in train_df.columns, f"Feature {feat} missing from training set"
        assert feat in test_df.columns, f"Feature {feat} missing from test set"

# 8. Saved model can be loaded
def test_saved_model_serialization(prepared_splits):
    train_df, val_df, _, _ = prepared_splits
    combined_train = pd.concat([train_df, val_df], ignore_index=True)

    forecaster = WaterConsumptionForecaster(algorithm="random_forest", model_params={"n_estimators": 20, "max_depth": 4})
    forecaster.train(combined_train, combined_train["daily_consumption_liters"].values)

    with tempfile.TemporaryDirectory() as tmpdir:
        forecaster.save(tmpdir)
        assert os.path.isfile(os.path.join(tmpdir, "forecasting_model.joblib"))
        assert os.path.isfile(os.path.join(tmpdir, "model_metadata.json"))

        loaded = WaterConsumptionForecaster(algorithm="random_forest")
        loaded.load(tmpdir)
        assert loaded.model is not None

# 9. Loaded model produces consistent predictions
def test_loaded_model_produces_consistent_predictions(prepared_splits):
    train_df, val_df, test_df, _ = prepared_splits
    combined_train = pd.concat([train_df, val_df], ignore_index=True)

    forecaster = WaterConsumptionForecaster(algorithm="random_forest", model_params={"n_estimators": 20, "max_depth": 4})
    forecaster.train(combined_train, combined_train["daily_consumption_liters"].values)
    original_preds = forecaster.predict(test_df)

    with tempfile.TemporaryDirectory() as tmpdir:
        forecaster.save(tmpdir)
        loaded = WaterConsumptionForecaster(algorithm="random_forest")
        loaded.load(tmpdir)
        loaded_preds = loaded.predict(test_df)

        np.testing.assert_array_almost_equal(original_preds, loaded_preds, decimal=3)

# 10. Chronological split is respected
def test_chronological_split_is_respected(prepared_splits):
    train_df, val_df, test_df, _ = prepared_splits

    max_train_date = train_df["date"].max()
    min_val_date = val_df["date"].min()
    max_val_date = val_df["date"].max()
    min_test_date = test_df["date"].min()

    assert max_train_date < min_val_date, "Train dates overlap with validation dates!"
    assert max_val_date < min_test_date, "Validation dates overlap with test dates!"

    # Verify each meter has equal representation
    for df in [train_df, val_df, test_df]:
        meter_counts = df["meter_id"].value_counts().unique()
        assert len(meter_counts) == 1, "Meters have unequal time slices in split!"

# 11. No target leakage exists
def test_no_target_leakage(sample_telemetry_df):
    daily_df = aggregate_hourly_to_daily(sample_telemetry_df)
    feat_df = extract_forecasting_features(daily_df)

    # Pick meter 1 and check that rolling_mean_7d uses ONLY past observations (shift 1)
    m1 = feat_df[feat_df["meter_id"] == 1].sort_values("date").reset_index(drop=True)

    for i in range(len(m1)):
        row = m1.iloc[i]
        expected_lag1 = m1.iloc[i - 1]["daily_consumption_liters"] if i >= 1 else None
        if expected_lag1 is not None:
            assert np.isclose(row["lag_1d"], expected_lag1, atol=1e-2), "lag_1d does not match t-1 value!"

        # Verify rolling_mean_7d does NOT equal average including current row
        if i >= 7:
            strictly_past_7 = m1.iloc[i-7:i]["daily_consumption_liters"].values
            expected_roll = float(np.mean(strictly_past_7))
            assert np.isclose(row["rolling_mean_7d"], expected_roll, atol=1e-2), "rolling_mean_7d leaked current day!"

# 12. Baseline calculation works
def test_baseline_calculation(prepared_splits):
    _, _, test_df, _ = prepared_splits
    baselines = evaluate_baseline_models(test_df)

    assert "naive_previous_day" in baselines
    assert "seasonal_naive_7d" in baselines

    assert baselines["seasonal_naive_7d"]["MAPE"] > 0.0
    assert baselines["naive_previous_day"]["MAPE"] > 0.0
    # Confirm Seasonal Naive 7-day is the top baseline
    assert baselines["seasonal_naive_7d"]["MAPE"] < baselines["naive_previous_day"]["MAPE"]

# 13. Safe zero-handling in MAPE calculation
def test_safe_mape_zero_handling():
    y_true_with_zero = np.array([0.0, 100.0, 50.0])
    y_pred = np.array([10.0, 90.0, 50.0])

    mape = calculate_safe_mape(y_true_with_zero, y_pred, epsilon=1.0)
    assert not np.isnan(mape), "Safe MAPE returned NaN on zero value!"
    assert not np.isinf(mape), "Safe MAPE returned Inf on zero value!"
    assert mape > 0.0

# 14. Model vs Baseline Comparison structure
def test_model_vs_baseline_comparison_structure(prepared_splits):
    _, _, test_df, _ = prepared_splits
    dummy_preds = {
        "Test Model A": test_df["lag_7d"].values,
        "Test Model B": test_df["lag_1d"].values
    }
    comp = generate_model_vs_baseline_comparison(test_df, dummy_preds)

    assert "markdown_table" in comp
    assert "rows" in comp
    assert comp["rows"][0]["model_name"] == "Seasonal Naive 7-day"
    assert comp["rows"][0]["beats_seasonal_naive"] == "Benchmark"
    assert "Seasonal Naive 7-day" in comp["markdown_table"]

# 15. Compatibility wrapper ml_models functions
def test_compatibility_wrapper_functions(prepared_splits):
    _, _, test_df, _ = prepared_splits
    forecaster = ml_models.load_model("5_AI_COMPONENTS/predictive_models/models")
    preds = ml_models.predict(forecaster, test_df)

    assert len(preds) == len(test_df)
    eval_res = ml_models.evaluate_model(forecaster, test_df)
    assert "overall_metrics" in eval_res
    assert "comparison_table" in eval_res
