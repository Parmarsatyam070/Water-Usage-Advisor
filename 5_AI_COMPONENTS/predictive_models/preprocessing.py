"""
Smart Water Usage Advisor - Predictive Model Preprocessing Pipeline
Aggregates hourly smart meter telemetry into daily consumption series per meter.
Computes lag features, rolling statistics, calendar indicators, and cyclical transforms.
Enforces strict anti-leakage principles: features are calculated using ONLY past observations.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict

# Feature definitions
CALENDAR_FEATURES = ["day_of_week", "day_of_month", "month", "is_weekend"]
CYCLICAL_FEATURES = ["dow_sin", "dow_cos", "month_sin", "month_cos"]
ENVIRONMENT_FEATURES = ["temperature_celsius"]
LAG_FEATURES = ["lag_1d", "lag_2d", "lag_3d", "lag_7d", "lag_14d"]
ROLLING_FEATURES = ["rolling_mean_7d", "rolling_std_7d", "rolling_min_7d", "rolling_max_7d", "rolling_mean_14d"]
PROFILE_FEATURES = ["profile_single_family", "profile_multi_family", "profile_commercial"]

ALL_PREDICTOR_FEATURES = (
    CALENDAR_FEATURES
    + CYCLICAL_FEATURES
    + ENVIRONMENT_FEATURES
    + LAG_FEATURES
    + ROLLING_FEATURES
    + PROFILE_FEATURES
)

def aggregate_hourly_to_daily(hourly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates hourly meter telemetry into daily time-series records per meter.
    Computes exact daily sum of consumption and daily mean temperature.
    """
    df = hourly_df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    df["date"] = df["timestamp"].dt.date

    daily_df = df.groupby(["meter_id", "user_id", "date"]).agg(
        daily_consumption_liters=("hourly_consumption_liters", "sum"),
        temperature_celsius=("temperature_celsius", "mean"),
        reading_count=("hourly_consumption_liters", "count")
    ).reset_index()

    # Sort strictly chronologically per meter
    daily_df["date"] = pd.to_datetime(daily_df["date"])
    daily_df = daily_df.sort_values(by=["meter_id", "date"]).reset_index(drop=True)
    daily_df["daily_consumption_liters"] = daily_df["daily_consumption_liters"].round(3)
    daily_df["temperature_celsius"] = daily_df["temperature_celsius"].round(2)

    return daily_df

def extract_forecasting_features(daily_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts time-series predictors for daily consumption forecasting.
    CRITICAL ANTI-LEAKAGE ENFORCEMENT:
    - All lags reference past days (t-1, t-2, t-7, etc.).
    - All rolling statistics use shift(1) so the current day's consumption is NEVER included in rolling features.
    """
    df = daily_df.copy()
    df = df.sort_values(by=["meter_id", "date"]).reset_index(drop=True)

    # 1. Calendar Features
    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # 2. Cyclical Transforms
    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7.0)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7.0)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12.0)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12.0)

    # 3. Lag Features (per meter)
    for lag in [1, 2, 3, 7, 14]:
        df[f"lag_{lag}d"] = df.groupby("meter_id")["daily_consumption_liters"].shift(lag)

    # 4. Rolling Statistics (per meter, STRICTLY shifted by 1 to prevent data leakage)
    for window in [7, 14]:
        # shift(1) ensures today's actual value is never observed in historical rolling statistics
        past_series = df.groupby("meter_id")["daily_consumption_liters"].shift(1)
        roll = past_series.groupby(df["meter_id"]).rolling(window=window, min_periods=window)
        df[f"rolling_mean_{window}d"] = roll.mean().reset_index(level=0, drop=True)
        if window == 7:
            df["rolling_std_7d"] = roll.std().reset_index(level=0, drop=True).fillna(0.0)
            df["rolling_min_7d"] = roll.min().reset_index(level=0, drop=True)
            df["rolling_max_7d"] = roll.max().reset_index(level=0, drop=True)

    # 5. Profile One-Hot Encoding (context without learning arbitrary raw IDs)
    profile_mapping = {1: "single_family", 2: "multi_family", 3: "commercial"}
    df["profile_name"] = df["meter_id"].map(profile_mapping)

    df["profile_single_family"] = (df["profile_name"] == "single_family").astype(int)
    df["profile_multi_family"] = (df["profile_name"] == "multi_family").astype(int)
    df["profile_commercial"] = (df["profile_name"] == "commercial").astype(int)

    # 6. Drop initial rows that lack 14-day lag history
    clean_df = df.dropna(subset=ALL_PREDICTOR_FEATURES).reset_index(drop=True)

    return clean_df

def chronological_train_val_test_split(
    df: pd.DataFrame,
    val_days: int = 14,
    test_days: int = 14
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Performs a strict chronological split across all meters.
    - Test: most recent test_days (unseen future)
    - Validation: preceding val_days (for tuning)
    - Train: earliest historical period
    """
    unique_dates = sorted(df["date"].unique())
    total_dates = len(unique_dates)

    if total_dates <= (val_days + test_days):
        raise ValueError(f"Insufficient dates ({total_dates}) for val ({val_days}) and test ({test_days}) splits.")

    split_test_idx = total_dates - test_days
    split_val_idx = split_test_idx - val_days

    train_dates = unique_dates[:split_val_idx]
    val_dates = unique_dates[split_val_idx:split_test_idx]
    test_dates = unique_dates[split_test_idx:]

    train_df = df[df["date"].isin(train_dates)].copy().reset_index(drop=True)
    val_df = df[df["date"].isin(val_dates)].copy().reset_index(drop=True)
    test_df = df[df["date"].isin(test_dates)].copy().reset_index(drop=True)

    return train_df, val_df, test_df
