"""
Smart Water Usage Advisor - Forecasting Inference & Persistence Engine
Generates demonstration 7-day rolling consumption forecasts from historical data.
Computes derived secondary metrics (weekly total, monthly projection, peak day).
Provides safe persistence helper for the authoritative `predictions` database table.
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.abspath("5_AI_COMPONENTS/predictive_models"))
from forecasting_model import WaterConsumptionForecaster
from preprocessing import extract_forecasting_features, ALL_PREDICTOR_FEATURES

def generate_7day_forecast(
    daily_df: pd.DataFrame,
    forecaster: WaterConsumptionForecaster,
    meter_id: int,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Generates a 7-day forward multi-step consumption forecast for a given meter.
    Uses autoregressive roll-forward where each day's prediction updates subsequent lag features.
    Enforces deterministic reproducibility using a fixed random seed for minor weather variations.
    """
    meter_history = daily_df[daily_df["meter_id"] == meter_id].copy().sort_values("date")
    if len(meter_history) < 14:
        raise ValueError(f"Meter {meter_id} requires at least 14 days of history.")

    user_id = int(meter_history["user_id"].iloc[0])
    profile_name = meter_history["profile_name"].iloc[-1] if "profile_name" in meter_history.columns else "single_family"
    last_date = meter_history["date"].max()

    rng = np.random.default_rng(seed + meter_id)
    forecast_records = []
    working_df = meter_history.copy()

    for step in range(1, 8):
        target_date = last_date + timedelta(days=step)

        # Build feature vector for target_date using working_df history
        day_of_week = target_date.weekday()
        month = target_date.month

        # Deterministic temperature continuity
        last_temp = float(working_df["temperature_celsius"].iloc[-1])
        temp_delta = float(rng.normal(0.0, 0.2))
        step_temp = round(last_temp + temp_delta, 2)

        # Construct historical lags
        consumption_series = working_df["daily_consumption_liters"].values
        lag_1 = consumption_series[-1]
        lag_2 = consumption_series[-2] if len(consumption_series) >= 2 else lag_1
        lag_3 = consumption_series[-3] if len(consumption_series) >= 3 else lag_2
        lag_7 = consumption_series[-7] if len(consumption_series) >= 7 else lag_1
        lag_14 = consumption_series[-14] if len(consumption_series) >= 14 else lag_7

        roll_7 = float(np.mean(consumption_series[-7:]))
        roll_14 = float(np.mean(consumption_series[-14:]))
        roll_7_std = float(np.std(consumption_series[-7:]))
        roll_7_min = float(np.min(consumption_series[-7:]))
        roll_7_max = float(np.max(consumption_series[-7:]))

        row_features = {
            "day_of_week": day_of_week,
            "day_of_month": target_date.day,
            "month": month,
            "is_weekend": int(day_of_week >= 5),
            "dow_sin": np.sin(2 * np.pi * day_of_week / 7.0),
            "dow_cos": np.cos(2 * np.pi * day_of_week / 7.0),
            "month_sin": np.sin(2 * np.pi * month / 12.0),
            "month_cos": np.cos(2 * np.pi * month / 12.0),
            "temperature_celsius": step_temp,
            "lag_1d": lag_1,
            "lag_2d": lag_2,
            "lag_3d": lag_3,
            "lag_7d": lag_7,
            "lag_14d": lag_14,
            "rolling_mean_7d": roll_7,
            "rolling_std_7d": roll_7_std,
            "rolling_min_7d": roll_7_min,
            "rolling_max_7d": roll_7_max,
            "rolling_mean_14d": roll_14,
            "profile_single_family": int(profile_name == "single_family"),
            "profile_multi_family": int(profile_name == "multi_family"),
            "profile_commercial": int(profile_name == "commercial")
        }

        feature_df = pd.DataFrame([row_features])[ALL_PREDICTOR_FEATURES]
        pred_val = float(round(forecaster.predict(feature_df)[0], 2))

        forecast_records.append({
            "meter_id": meter_id,
            "user_id": user_id,
            "date": target_date.strftime("%Y-%m-%d"),
            "predicted_daily_liters": pred_val,
            "temperature_celsius": step_temp
        })

        # Append prediction to working_df so subsequent multi-step lags roll forward
        new_row = pd.DataFrame([{
            "meter_id": meter_id,
            "user_id": user_id,
            "date": target_date,
            "daily_consumption_liters": pred_val,
            "temperature_celsius": step_temp,
            "profile_name": profile_name
        }])
        working_df = pd.concat([working_df, new_row], ignore_index=True)

    # Derived Secondary Outputs
    daily_preds = [r["predicted_daily_liters"] for r in forecast_records]
    total_7d_liters = round(float(sum(daily_preds)), 2)
    daily_avg = float(np.mean(daily_preds))
    monthly_projected_liters = round(float(daily_avg * 30.0), 2)

    # Peak usage day
    peak_idx = int(np.argmax(daily_preds))
    peak_day_record = forecast_records[peak_idx]

    return {
        "meter_id": meter_id,
        "user_id": user_id,
        "profile_name": profile_name,
        "forecast_horizon_days": 7,
        "daily_forecasts": forecast_records,
        "predicted_7day_total_liters": total_7d_liters,
        "predicted_monthly_liters": monthly_projected_liters,
        "predicted_peak_day": peak_day_record["date"],
        "predicted_peak_volume_liters": peak_day_record["predicted_daily_liters"],
        "model_version": forecaster.model_version,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

def persist_forecast_to_database(forecast_output: Dict[str, Any], engine=None) -> int:
    """
    Safely persists daily forecast records into the authoritative `predictions` database table.
    NOTE: `confidence_score` is intentionally left NULL because the deterministic tree regressor
    does not provide a calibrated statistical interval. We do not invent fake confidence scores.
    """
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
    with engine.begin() as conn:
        for r in forecast_output["daily_forecasts"]:
            conn.execute(text("""
                INSERT INTO predictions (
                    meter_id, user_id, prediction_date, predicted_daily_liters,
                    predicted_weekly_liters, predicted_monthly_liters,
                    confidence_score, model_version, prediction_timestamp
                )
                VALUES (
                    :meter_id, :user_id, :pred_date, :pred_daily,
                    :pred_weekly, :pred_monthly,
                    :conf, :version, CURRENT_TIMESTAMP
                );
            """), {
                "meter_id": r["meter_id"],
                "user_id": r["user_id"],
                "pred_date": r["date"],
                "pred_daily": r["predicted_daily_liters"],
                "pred_weekly": forecast_output["predicted_7day_total_liters"],
                "pred_monthly": forecast_output["predicted_monthly_liters"],
                "conf": None,  # No fabricated confidence score
                "version": forecast_output["model_version"]
            })
            inserted += 1

    print(f"Persisted {inserted} forecast records into predictions table for meter {forecast_output['meter_id']}.")
    return inserted
