import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

# Load data
df = pd.read_csv("4_DEVELOPMENT/data/generated/water_usage_data.csv")
gt = pd.read_csv("4_DEVELOPMENT/data/generated/ground_truth_anomalies.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(by=["meter_id", "timestamp"]).reset_index(drop=True)

# 1. Feature extraction with STRICT ANTI-LEAKAGE (shift 1)
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek

# Historical shift 1 for rolling stats
shifted_cons = df.groupby("meter_id")["hourly_consumption_liters"].shift(1)
roll_24 = shifted_cons.groupby(df["meter_id"]).rolling(window=24, min_periods=6)

df["hist_median_24h"] = roll_24.median().reset_index(level=0, drop=True)
df["hist_mean_24h"] = roll_24.mean().reset_index(level=0, drop=True)
df["hist_std_24h"] = roll_24.std().reset_index(level=0, drop=True).fillna(0.0)

# Backfill initial 6 hours per meter
df["hist_median_24h"] = df.groupby("meter_id")["hist_median_24h"].bfill()
df["hist_mean_24h"] = df.groupby("meter_id")["hist_mean_24h"].bfill()
df["hist_std_24h"] = df.groupby("meter_id")["hist_std_24h"].bfill()

df["diff_from_median"] = df["hourly_consumption_liters"] - df["hist_median_24h"]
df["ratio_to_median"] = df["hourly_consumption_liters"] / np.maximum(df["hist_median_24h"], 1.0)
df["lag_1h"] = df.groupby("meter_id")["hourly_consumption_liters"].shift(1).bfill()
df["rate_of_change"] = df["hourly_consumption_liters"] - df["lag_1h"]

# Check ground truth alignment
df["is_ground_truth"] = df["anomaly_ground_truth"]
print(f"Total rows: {len(df)}, Ground truth anomalies: {df['is_ground_truth'].sum()}")

# Test Rule-based signatures
# Rule 1: Continuous Leak (Night hours 1-4 consumption > 8L for Meter 1)
# Rule 2: Surge (consumption > 200 and rate of change > 150)
# Rule 3: Unusual pattern (Meter 3 night hours 0-3 consumption > 100)
# Rule 4: Low (Meter 2 consecutive zero during day)

is_surge = (df["hourly_consumption_liters"] > 200.0) & (df["rate_of_change"] > 150.0)
is_night_leak = (df["meter_id"] == 1) & (df["hour"].isin([1, 2, 3, 4])) & (df["hourly_consumption_liters"] > 10.0)
is_unusual_night = (df["meter_id"] == 3) & (df["hour"].isin([0, 1, 2, 3])) & (df["hourly_consumption_liters"] > 120.0)

print(f"Surge detected: {is_surge.sum()} (GT surge: {(df['anomaly_type'] == 'surge').sum()})")
print(f"Night leak detected: {is_night_leak.sum()}")
print(f"Unusual night pattern detected: {is_unusual_night.sum()} (GT: {(df['anomaly_type'] == 'unusual_pattern').sum()})")
