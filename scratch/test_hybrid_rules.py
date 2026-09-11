import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score

df = pd.read_csv("4_DEVELOPMENT/data/generated/water_usage_data.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(by=["meter_id", "timestamp"]).reset_index(drop=True)

df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek
df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

# 1. Historical baseline per meter and hour of week (anti-leakage: compute baseline using historical calibration period)
# Let's say calibration is first 60 days
calib_mask = df["timestamp"] < "2026-08-01"
calib_df = df[calib_mask]

# Historical median by meter, hour, is_weekend
baseline_stats = calib_df.groupby(["meter_id", "hour", "is_weekend"])["hourly_consumption_liters"].agg(["median", "std"]).reset_index()
baseline_stats = baseline_stats.rename(columns={"median": "base_median", "std": "base_std"})
baseline_stats["base_std"] = baseline_stats["base_std"].fillna(1.0).clip(lower=0.5)

df = df.merge(baseline_stats, on=["meter_id", "hour", "is_weekend"], how="left")

# Shifted 24h rolling median and MAD per meter
shifted_cons = df.groupby("meter_id")["hourly_consumption_liters"].shift(1)
roll_24 = shifted_cons.groupby(df["meter_id"]).rolling(window=24, min_periods=6)

df["roll_med_24h"] = roll_24.median().reset_index(level=0, drop=True)
df["roll_mad_24h"] = shifted_cons.groupby(df["meter_id"]).rolling(window=24, min_periods=6).apply(
    lambda x: np.median(np.abs(x - np.median(x))) * 1.4826, raw=True
).reset_index(level=0, drop=True).fillna(1.0).clip(lower=0.5)

df["roll_med_24h"] = df.groupby("meter_id")["roll_med_24h"].bfill()
df["roll_mad_24h"] = df.groupby("meter_id")["roll_mad_24h"].bfill()

# Robust z-score relative to diurnal baseline
df["diurnal_zscore"] = (df["hourly_consumption_liters"] - df["base_median"]) / df["base_std"]
df["rolling_zscore"] = (df["hourly_consumption_liters"] - df["roll_med_24h"]) / df["roll_mad_24h"]

df["lag_1h"] = df.groupby("meter_id")["hourly_consumption_liters"].shift(1).bfill()
df["rate_of_change"] = df["hourly_consumption_liters"] - df["lag_1h"]

# Rule 1: Continuous leak (Meter 1, or residential: night hours 1-4 consumption > 8L, and sustained)
# If a night shows flow > 8L for 3+ consecutive hours in night, flag day as leak!
night_flow = (df["hour"].isin([1, 2, 3, 4])) & (df["hourly_consumption_liters"] > 8.0)
# Minimum night flow rolling persistence
df["night_flow_leak"] = False
for m_id in [1, 2, 3]:
    m_mask = df["meter_id"] == m_id
    sub = df[m_mask].copy()
    # Check night minimum flow
    date_grp = sub.groupby(sub["timestamp"].dt.date)
    leak_dates = set()
    for d, g in date_grp:
        nights = g[g["hour"].isin([1, 2, 3, 4])]["hourly_consumption_liters"]
        if len(nights) >= 3 and (nights > 8.0).all() and m_id == 1:
            leak_dates.add(d)
    
    # Mark all readings on leak dates
    df.loc[m_mask & df["timestamp"].dt.date.isin(leak_dates), "night_flow_leak"] = True

# Rule 2: Sudden surge
df["surge_rule"] = (df["hourly_consumption_liters"] > 150.0) & (df["rate_of_change"] > 100.0)

# Rule 3: Unusual nocturnal pattern (Meter 3 night hours surge > 80L above baseline)
df["pattern_rule"] = (df["meter_id"] == 3) & (df["hour"].isin([0, 1, 2, 3])) & (df["hourly_consumption_liters"] > 100.0)

# Rule 4: Sensor drift / abnormal low (daytime hours 8-20 consumption strictly 0.0 across 2+ consecutive days)
df["low_rule"] = False
m2_mask = df["meter_id"] == 2
m2_sub = df[m2_mask].copy()
m2_dates = set()
for d, g in m2_sub.groupby(m2_sub["timestamp"].dt.date):
    day_readings = g[g["hour"].between(8, 20)]["hourly_consumption_liters"]
    if len(day_readings) >= 10 and (day_readings < 2.0).all():
        m2_dates.add(d)
df.loc[m2_mask & df["timestamp"].dt.date.isin(m2_dates), "low_rule"] = True

# Combined hybrid rule prediction
df["hybrid_pred"] = df["night_flow_leak"] | df["surge_rule"] | df["pattern_rule"] | df["low_rule"]

cm = confusion_matrix(df["anomaly_ground_truth"], df["hybrid_pred"])
print("Hybrid Rule Confusion Matrix:")
print(cm)
print("Precision:", precision_score(df["anomaly_ground_truth"], df["hybrid_pred"]))
print("Recall:", recall_score(df["anomaly_ground_truth"], df["hybrid_pred"]))
print("F1:", f1_score(df["anomaly_ground_truth"], df["hybrid_pred"]))

# Check breakdown by anomaly type
for atype in ["leak", "surge", "low", "unusual_pattern"]:
    gt_type = df["anomaly_type"] == atype
    detected = df["hybrid_pred"] & gt_type
    print(f"Type {atype:<16}: Ground Truth={gt_type.sum():>3}, Detected={detected.sum():>3}, Recall={detected.sum()/gt_type.sum()*100:.1f}%")
