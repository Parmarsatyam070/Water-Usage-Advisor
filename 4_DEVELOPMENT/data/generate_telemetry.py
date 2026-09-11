"""
Smart Water Usage Advisor - Synthetic Telemetry Generator
Generates 90 days of realistic hourly smart meter telemetry (2,160 readings/meter)
across 3 distinct profiles (Single-Family Household, Multi-Family Residential, Commercial Facility).
Injects controlled ground-truth anomalies (leak, surge, low, unusual_pattern).
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_synthetic_telemetry(seed=42, output_dir="4_DEVELOPMENT/data/generated"):
    np.random.seed(seed)
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)

    # 90 Days of Hourly Readings
    start_date = datetime(2026, 6, 1, 0, 0, 0)
    total_hours = 90 * 24  # 2,160 hours per meter
    timestamps = [start_date + timedelta(hours=i) for i in range(total_hours)]

    # Meter and User Profiles Configuration
    profiles = [
        {
            "meter_id": 1,
            "user_id": 1,
            "profile_name": "Residential Single-Family",
            "base_multiplier": 1.0,
            "meter_type": "smart",
            "initial_meter_reading": 12450.000
        },
        {
            "meter_id": 2,
            "user_id": 2,
            "profile_name": "Residential Multi-Family",
            "base_multiplier": 2.8,
            "meter_type": "smart",
            "initial_meter_reading": 38200.000
        },
        {
            "meter_id": 3,
            "user_id": 3,
            "profile_name": "Commercial Facility",
            "base_multiplier": 5.0,
            "meter_type": "digital",
            "initial_meter_reading": 95600.000
        }
    ]

    all_readings = []
    ground_truth_anomalies = []
    reading_id_counter = 1
    anomaly_id_counter = 1

    # Base Diurnal Weights (Hourly 0 to 23)
    # Residential: low night (0-5), morning peak (7-9), midday dip (11-14), evening peak (18-21)
    res_hourly_curve = np.array([
        0.05, 0.02, 0.01, 0.01, 0.02, 0.10,  # 00:00 - 05:00 Night
        0.55, 1.20, 1.45, 0.90, 0.60, 0.70,  # 06:00 - 11:00 Morning Peak
        0.80, 0.65, 0.50, 0.55, 0.75, 1.10,  # 12:00 - 17:00 Midday / Pre-evening
        1.55, 1.60, 1.30, 0.85, 0.40, 0.15   # 18:00 - 23:00 Evening Peak & Taper
    ])
    res_hourly_curve /= res_hourly_curve.mean()

    # Commercial Facility: low night & weekend, high business hours (08:00 - 18:00)
    comm_hourly_curve = np.array([
        0.05, 0.05, 0.05, 0.05, 0.05, 0.10,  # 00:00 - 05:00
        0.25, 0.80, 1.60, 1.85, 1.90, 1.70,  # 06:00 - 11:00
        1.60, 1.75, 1.80, 1.70, 1.50, 1.20,  # 12:00 - 17:00
        0.60, 0.30, 0.15, 0.10, 0.08, 0.05   # 18:00 - 23:00
    ])
    comm_hourly_curve /= comm_hourly_curve.mean()

    for p in profiles:
        m_id = p["meter_id"]
        u_id = p["user_id"]
        is_commercial = (m_id == 3)
        curve = comm_hourly_curve if is_commercial else res_hourly_curve

        cumulative = p["initial_meter_reading"]

        meter_records = []

        for h_idx, ts in enumerate(timestamps):
            hour = ts.hour
            day_of_week = ts.weekday()  # 0=Mon, 6=Sun
            day_idx = h_idx // 24

            # Ambient Temperature Simulation (Seasonal sinusoidal + diurnal wave)
            # Baseline summer temp: 22C to 34C
            daily_temp_base = 24.0 + 4.0 * np.sin(2 * np.pi * day_idx / 90.0)
            hourly_temp_var = 5.0 * np.sin(2 * np.pi * (hour - 9) / 24.0)
            ambient_temp = round(float(daily_temp_base + hourly_temp_var + np.random.normal(0, 0.4)), 2)

            # Baseline Hourly Volume
            base_lph = 14.0 * p["base_multiplier"]

            # Profile Day-of-week adjustments
            if is_commercial:
                dow_factor = 0.2 if day_of_week >= 5 else 1.0  # Weekends low in offices
            else:
                dow_factor = 1.25 if day_of_week >= 5 else 0.95 # Weekends higher in homes

            # Temperature sensitivity factor (hotter days = slightly higher usage)
            temp_factor = 1.0 + max(0.0, (ambient_temp - 26.0) * 0.02)

            expected_consumption = base_lph * curve[hour] * dow_factor * temp_factor
            noise = np.random.normal(0, max(0.8, expected_consumption * 0.12))
            actual_consumption = max(0.0, float(expected_consumption + noise))

            # Guarantee clean nocturnal zero-flow in normal conditions for households
            if not is_commercial and hour in [1, 2, 3, 4] and np.random.rand() > 0.15:
                actual_consumption = 0.0

            # Default Ground Truth Attributes
            is_anomaly = False
            anomaly_type = "none"
            anomaly_severity = "none"
            anomaly_desc = ""

            # -------------------------------------------------------------
            # Controlled Anomaly Injections
            # -------------------------------------------------------------
            # Anomaly 1: Continuous Low-Flow Toilet Leak (Meter 1, Days 42-46)
            if m_id == 1 and 42 <= day_idx <= 46:
                leak_flow = 16.5 + np.random.normal(0, 1.0)
                actual_consumption += max(8.0, float(leak_flow))
                is_anomaly = True
                anomaly_type = "leak"
                anomaly_severity = "high"
                anomaly_desc = "Continuous toilet flapper valve leak (non-zero night flow)"

            # Anomaly 2: Sudden Catastrophic Pipe Burst / Surge (Meter 1, Day 71, 14:00-15:00)
            elif m_id == 1 and day_idx == 71 and hour in [14, 15]:
                actual_consumption += 420.0 + np.random.normal(0, 15.0)
                is_anomaly = True
                anomaly_type = "surge"
                anomaly_severity = "critical"
                anomaly_desc = "Sudden pipe burst or severed irrigation line"

            # Anomaly 3: Abnormal Low Consumption / Vacant Interval (Meter 2, Days 28-31)
            elif m_id == 2 and 28 <= day_idx <= 31:
                actual_consumption = 0.0 if np.random.rand() > 0.05 else 1.2
                is_anomaly = True
                anomaly_type = "low"
                anomaly_severity = "medium"
                anomaly_desc = "Extended uncharacteristic zero-consumption during normal active period"

            # Anomaly 4: Unusual Nocturnal Irrigation Pattern (Meter 3, Days 58-60, 00:00-03:00)
            elif m_id == 3 and 58 <= day_idx <= 60 and hour in [0, 1, 2, 3]:
                actual_consumption += 195.0 + np.random.normal(0, 10.0)
                is_anomaly = True
                anomaly_type = "unusual_pattern"
                anomaly_severity = "high"
                anomaly_desc = "Commercial cooling loop cycling or unapproved nocturnal irrigation"

            # Log Anomaly Ground Truth if active
            if is_anomaly:
                ground_truth_anomalies.append({
                    "ground_truth_id": anomaly_id_counter,
                    "meter_id": m_id,
                    "user_id": u_id,
                    "timestamp": ts.isoformat(),
                    "anomaly_type": anomaly_type,
                    "severity": anomaly_severity,
                    "observed_consumption": round(actual_consumption, 3),
                    "expected_baseline": round(expected_consumption, 3),
                    "deviation_liters": round(actual_consumption - expected_consumption, 3),
                    "description": anomaly_desc
                })
                anomaly_id_counter += 1

            actual_consumption = round(actual_consumption, 3)
            cumulative = round(cumulative + actual_consumption, 3)

            # Quality score & validation status
            quality_score = 98 if not is_anomaly else 85

            meter_records.append({
                "reading_id": reading_id_counter,
                "meter_id": m_id,
                "user_id": u_id,
                "timestamp": ts,
                "cumulative_reading": cumulative,
                "hourly_consumption_liters": actual_consumption,
                "temperature_celsius": ambient_temp,
                "quality_score": quality_score,
                "data_source": "estimated",
                "is_validated": True,
                "anomaly_ground_truth": is_anomaly,
                "anomaly_type": anomaly_type
            })
            reading_id_counter += 1

        # Calculate Consistent Daily and Monthly Aggregates for each meter
        df_meter = pd.DataFrame(meter_records)
        df_meter['date'] = df_meter['timestamp'].dt.date
        df_meter['year_month'] = df_meter['timestamp'].dt.to_period('M')

        # Group sums
        daily_sums = df_meter.groupby('date')['hourly_consumption_liters'].transform('sum')
        monthly_sums = df_meter.groupby('year_month')['hourly_consumption_liters'].transform('sum')

        df_meter['daily_consumption_liters'] = daily_sums.round(3)
        df_meter['monthly_consumption_liters'] = monthly_sums.round(3)

        # Created timestamp
        df_meter['created_at'] = df_meter['timestamp'].apply(lambda x: (x + timedelta(minutes=2)).isoformat())
        df_meter['timestamp'] = df_meter['timestamp'].apply(lambda x: x.isoformat())

        all_readings.append(df_meter)

    # Combine all meter telemetry
    final_telemetry_df = pd.concat(all_readings, ignore_index=True)

    # Reorder columns matching authoritative water_usage_data schema
    columns_order = [
        "reading_id",
        "meter_id",
        "user_id",
        "timestamp",
        "cumulative_reading",
        "hourly_consumption_liters",
        "daily_consumption_liters",
        "monthly_consumption_liters",
        "temperature_celsius",
        "quality_score",
        "data_source",
        "is_validated",
        "created_at",
        "anomaly_ground_truth",
        "anomaly_type"
    ]
    final_telemetry_df = final_telemetry_df[columns_order]

    # Save to CSV
    telemetry_path = os.path.join(output_dir, "water_usage_data.csv")
    anomalies_path = os.path.join(output_dir, "ground_truth_anomalies.csv")

    final_telemetry_df.to_csv(telemetry_path, index=False)
    pd.DataFrame(ground_truth_anomalies).to_csv(anomalies_path, index=False)

    print("==================================================")
    print("SYNTHETIC TELEMETRY GENERATION COMPLETE")
    print("==================================================")
    print(f"Total Records Generated: {len(final_telemetry_df)} ({len(profiles)} meters x {total_hours} hours)")
    print(f"Total Ground-Truth Anomaly Timestamps: {len(ground_truth_anomalies)}")
    print(f"Telemetry Saved to: {telemetry_path}")
    print(f"Ground Truth Saved to: {anomalies_path}")
    print("==================================================")

    return final_telemetry_df, ground_truth_anomalies

if __name__ == "__main__":
    generate_synthetic_telemetry()
