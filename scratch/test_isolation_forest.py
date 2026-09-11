import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

df = pd.read_csv("4_DEVELOPMENT/data/generated/water_usage_data.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(by=["meter_id", "timestamp"]).reset_index(drop=True)

# 1. Feature Engineering with historical shift (anti-leakage)
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek
df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

shifted_1 = df.groupby("meter_id")["hourly_consumption_liters"].shift(1)
roll_24 = shifted_1.groupby(df["meter_id"]).rolling(window=24, min_periods=6)
roll_168 = shifted_1.groupby(df["meter_id"]).rolling(window=168, min_periods=24)

df["roll_median_24h"] = roll_24.median().reset_index(level=0, drop=True)
df["roll_mean_24h"] = roll_24.mean().reset_index(level=0, drop=True)
df["roll_std_24h"] = roll_24.std().reset_index(level=0, drop=True).fillna(0.0)
df["roll_min_24h"] = roll_24.min().reset_index(level=0, drop=True)
df["roll_max_24h"] = roll_24.max().reset_index(level=0, drop=True)

df["roll_median_168h"] = roll_168.median().reset_index(level=0, drop=True)
df["roll_mean_168h"] = roll_168.mean().reset_index(level=0, drop=True)

# Backfill initial window
for col in ["roll_median_24h", "roll_mean_24h", "roll_std_24h", "roll_min_24h", "roll_max_24h", "roll_median_168h", "roll_mean_168h"]:
    df[col] = df.groupby("meter_id")[col].bfill()

df["diff_median"] = df["hourly_consumption_liters"] - df["roll_median_24h"]
df["ratio_median"] = df["hourly_consumption_liters"] / np.maximum(df["roll_median_24h"], 0.5)
df["lag_1h"] = df.groupby("meter_id")["hourly_consumption_liters"].shift(1).bfill()
df["rate_of_change"] = df["hourly_consumption_liters"] - df["lag_1h"]

# Fit Isolation Forest on first 60 days (calibration period: ~1440 hours per meter = 4320 total rows)
calib_mask = df["timestamp"] < "2026-08-01"
train_df = df[calib_mask].copy()

if_features = [
    "hourly_consumption_liters", "roll_median_24h", "roll_mean_24h", "roll_std_24h",
    "diff_median", "ratio_median", "rate_of_change", "hour", "day_of_week", "temperature_celsius"
]

# Estimated contamination ~0.035
iso = IsolationForest(n_estimators=100, contamination=0.035, random_state=42)
iso.fit(train_df[if_features])

# Predict across full dataset
raw_scores = iso.decision_function(df[if_features])
# Transform to normalized score [0, 1] where 1 is highly anomalous
# decision_function: positive is normal, negative is anomalous
min_s, max_s = raw_scores.min(), raw_scores.max()
df["iso_score"] = np.round(1.0 - (raw_scores - min_s) / (max_s - min_s), 4)
df["iso_pred"] = iso.predict(df[if_features]) == -1

print("Isolation forest flags:", df["iso_pred"].sum())
print("Confusion with ground truth:")
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
cm = confusion_matrix(df["anomaly_ground_truth"], df["iso_pred"])
print(cm)
print("Precision:", precision_score(df["anomaly_ground_truth"], df["iso_pred"]))
print("Recall:", recall_score(df["anomaly_ground_truth"], df["iso_pred"]))
print("F1:", f1_score(df["anomaly_ground_truth"], df["iso_pred"]))
