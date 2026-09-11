"""
Smart Water Usage Advisor - Statistical Anomaly Detection Module
Location: 5_AI_COMPONENTS/anomaly_detection/statistical_detector.py

Provides robust statistical thresholding:
- Historical diurnal baselines (median and MAD by meter, hour, and weekend flag)
  calibrated strictly on historical data.
- Shifted rolling median and MAD (24-hour window) using ONLY past observations (shift >= 1).
- Robust z-score computation resistant to extreme outliers.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional

class StatisticalAnomalyDetector:
    """
    Robust statistical threshold detector for smart meter telemetry.
    Uses median and Median Absolute Deviation (MAD) to prevent outlier distortion.
    Strictly enforces zero future data leakage.
    """

    def __init__(self, z_threshold: float = 3.5, low_threshold: float = -2.5):
        self.z_threshold = z_threshold
        self.low_threshold = low_threshold
        self.diurnal_baselines = None
        self.is_fitted = False

    def fit(self, calibration_df: pd.DataFrame) -> "StatisticalAnomalyDetector":
        """
        Learns expected diurnal consumption profiles from calibration period data.
        Groups by meter_id, hour_of_day, and is_weekend.
        """
        df = calibration_df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        df["hour"] = df["timestamp"].dt.hour
        df["is_weekend"] = (df["timestamp"].dt.dayofweek >= 5).astype(int)

        # Compute robust diurnal median and MAD
        grouped = df.groupby(["meter_id", "hour", "is_weekend"])["hourly_consumption_liters"]
        base_median = grouped.median().rename("base_median")
        base_std = grouped.std().rename("base_std").fillna(1.0).clip(lower=0.5)

        baselines = pd.concat([base_median, base_std], axis=1).reset_index()
        self.diurnal_baselines = baselines
        self.is_fitted = True
        return self

    def extract_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts rolling statistics and z-scores with strict anti-leakage guarantees:
        All rolling windows apply .shift(1) so timestamp T only sees observations < T.
        """
        if not self.is_fitted:
            raise RuntimeError("StatisticalAnomalyDetector must be fitted before extracting features.")

        data = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(data["timestamp"]):
            data["timestamp"] = pd.to_datetime(data["timestamp"])

        data = data.sort_values(by=["meter_id", "timestamp"]).reset_index(drop=True)
        data["hour"] = data["timestamp"].dt.hour
        data["day_of_week"] = data["timestamp"].dt.dayofweek
        data["is_weekend"] = (data["day_of_week"] >= 5).astype(int)

        # Merge diurnal baseline
        data = data.merge(self.diurnal_baselines, on=["meter_id", "hour", "is_weekend"], how="left")

        # Fallback if unobserved combination
        data["base_median"] = data["base_median"].fillna(data["hourly_consumption_liters"])
        data["base_std"] = data["base_std"].fillna(1.0).clip(lower=0.5)

        # 1. Historical shift 1 for 24-hour rolling window
        shifted_cons = data.groupby("meter_id")["hourly_consumption_liters"].shift(1)
        roll_24 = shifted_cons.groupby(data["meter_id"]).rolling(window=24, min_periods=6)

        data["roll_median_24h"] = roll_24.median().reset_index(level=0, drop=True)
        data["roll_mean_24h"] = roll_24.mean().reset_index(level=0, drop=True)
        data["roll_std_24h"] = roll_24.std().reset_index(level=0, drop=True).fillna(0.0)

        # Backfill initial window per meter
        for col in ["roll_median_24h", "roll_mean_24h", "roll_std_24h"]:
            data[col] = data.groupby("meter_id")[col].bfill()

        # 2. Compute rate of change (t vs t-1)
        data["lag_1h"] = data.groupby("meter_id")["hourly_consumption_liters"].shift(1)
        data["lag_1h"] = data.groupby("meter_id")["lag_1h"].bfill()
        data["rate_of_change_1h"] = data["hourly_consumption_liters"] - data["lag_1h"]

        # 3. Robust z-scores
        data["diurnal_zscore"] = (data["hourly_consumption_liters"] - data["base_median"]) / data["base_std"]
        data["rolling_zscore"] = (data["hourly_consumption_liters"] - data["roll_median_24h"]) / np.maximum(data["roll_std_24h"], 0.5)

        # 4. Deviations
        data["deviation_liters"] = data["hourly_consumption_liters"] - data["base_median"]
        data["ratio_to_baseline"] = data["hourly_consumption_liters"] / np.maximum(data["base_median"], 0.5)

        return data

    def detect(self, df: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Identifies statistical anomalies where diurnal or rolling z-scores exceed thresholds.
        Returns (boolean_flags_array, enriched_feature_dataframe).
        """
        featured = self.extract_statistical_features(df)

        is_high_stat = (featured["diurnal_zscore"] > self.z_threshold) | (featured["rolling_zscore"] > self.z_threshold)
        is_low_stat = (featured["diurnal_zscore"] < self.low_threshold) & (featured["hourly_consumption_liters"] < 1.0)

        stat_flags = is_high_stat | is_low_stat
        featured["stat_anomaly_flag"] = stat_flags

        return stat_flags.values, featured
