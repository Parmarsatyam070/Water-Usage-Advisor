"""
Smart Water Usage Advisor - Data Preprocessing & Feature Engineering Module
Provides reusable data preparation pipelines for time-series analysis and future ML models (Phase 3).
Includes timestamp parsing, sorting, missing-value handling, cyclical time encodings,
rolling statistics, lag features, and profile one-hot encoding.
"""

import pandas as pd
import numpy as np

class WaterDataPreprocessor:
    """
    Reusable preprocessor for raw smart water meter telemetry.
    Extracts temporal, statistical, and lagged features without data leakage.
    """

    def __init__(self, fill_method="interpolate"):
        self.fill_method = fill_method

    def prepare_features(self, df: pd.DataFrame, is_training: bool = False) -> pd.DataFrame:
        """
        Transforms raw water telemetry dataframe into rich engineered feature set.
        """
        df_out = df.copy()

        # 1. Ensure datetime format and sort chronologically
        if not pd.api.types.is_datetime64_any_dtype(df_out["timestamp"]):
            df_out["timestamp"] = pd.to_datetime(df_out["timestamp"])

        df_out = df_out.sort_values(by=["meter_id", "timestamp"]).reset_index(drop=True)

        # 2. Missing Value Imputation
        if df_out["hourly_consumption_liters"].isnull().any():
            if self.fill_method == "interpolate":
                df_out["hourly_consumption_liters"] = df_out.groupby("meter_id")["hourly_consumption_liters"].transform(
                    lambda x: x.interpolate(method="linear").bfill().ffill()
                )
            else:
                df_out["hourly_consumption_liters"] = df_out["hourly_consumption_liters"].fillna(0.0)

        # 3. Calendar & Temporal Features
        df_out["hour"] = df_out["timestamp"].dt.hour
        df_out["day_of_week"] = df_out["timestamp"].dt.dayofweek  # 0=Monday, 6=Sunday
        df_out["day_of_month"] = df_out["timestamp"].dt.day
        df_out["month"] = df_out["timestamp"].dt.month
        df_out["is_weekend"] = (df_out["day_of_week"] >= 5).astype(int)

        # 4. Cyclical Encodings for Hour and Day of Week (Preserves periodic continuity)
        df_out["hour_sin"] = np.sin(2 * np.pi * df_out["hour"] / 24.0)
        df_out["hour_cos"] = np.cos(2 * np.pi * df_out["hour"] / 24.0)
        df_out["dow_sin"] = np.sin(2 * np.pi * df_out["day_of_week"] / 7.0)
        df_out["dow_cos"] = np.cos(2 * np.pi * df_out["day_of_week"] / 7.0)

        # 5. Lagged Consumption Features (Past values per meter)
        for lag in [1, 2, 3, 24, 48, 168]:  # 1h, 2h, 3h, 1 day, 2 days, 1 week
            col_name = f"lag_{lag}h"
            df_out[col_name] = df_out.groupby("meter_id")["hourly_consumption_liters"].shift(lag)

        # 6. Rolling Window Statistics (6-hour and 24-hour windows)
        for window in [6, 24]:
            roll = df_out.groupby("meter_id")["hourly_consumption_liters"].rolling(window=window, min_periods=1)
            df_out[f"rolling_mean_{window}h"] = roll.mean().reset_index(drop=True)
            df_out[f"rolling_std_{window}h"] = roll.std().fillna(0.0).reset_index(drop=True)
            df_out[f"rolling_max_{window}h"] = roll.max().reset_index(drop=True)
            df_out[f"rolling_min_{window}h"] = roll.min().reset_index(drop=True)

        # 7. Night-Flow Indicator (01:00 to 05:00 window)
        df_out["is_night_window"] = df_out["hour"].isin([1, 2, 3, 4]).astype(int)

        # 8. Profile Mapping / Encoding
        profile_map = {1: "single_family", 2: "multi_family", 3: "commercial"}
        df_out["profile_type"] = df_out["meter_id"].map(profile_map).fillna("unknown")
        profile_dummies = pd.get_dummies(df_out["profile_type"], prefix="profile", drop_first=False)
        df_out = pd.concat([df_out, profile_dummies], axis=1)

        # 9. Clean up NaN values introduced by shift lags (backfill for early rows)
        lag_cols = [c for c in df_out.columns if c.startswith("lag_")]
        for col in lag_cols:
            df_out[col] = df_out.groupby("meter_id")[col].bfill().fillna(df_out["hourly_consumption_liters"])

        return df_out

    def aggregate_summary(self, df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
        """
        Aggregates consumption telemetry to Daily ('D') or Monthly ('ME') summary metrics.
        """
        df_work = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df_work["timestamp"]):
            df_work["timestamp"] = pd.to_datetime(df_work["timestamp"])

        grouped = df_work.set_index("timestamp").groupby([pd.Grouper(freq=freq), "meter_id"])
        summary = grouped.agg(
            total_liters=("hourly_consumption_liters", "sum"),
            avg_hourly_liters=("hourly_consumption_liters", "mean"),
            max_hourly_liters=("hourly_consumption_liters", "max"),
            min_hourly_liters=("hourly_consumption_liters", "min"),
            avg_temperature=("temperature_celsius", "mean")
        ).reset_index()

        return summary
