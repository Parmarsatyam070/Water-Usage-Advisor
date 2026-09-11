"""
Smart Water Usage Advisor - Telemetry Data Validation Pipeline
Performs 14 automated data quality checks against generated water usage records:
1. Non-negative consumption
2. Monotonic non-decreasing cumulative readings
3. Valid ISO timestamps
4. Exact 1-hour interval continuity
5. Zero duplicate meter/timestamp records
6. Quality scores in range [0, 100]
7. Valid categorical fields
8. Zero missing values
9. Realistic temperature range [-20C, 55C]
10. Daily aggregate consistency
11. Monthly aggregate consistency
12. Valid anomaly ground truth
13. Minimum 3 distinct meter profiles
14. Expected total record count (2,160 readings/meter)
"""

import os
import sys
import pandas as pd
import numpy as np

def validate_telemetry_dataset(data_path="4_DEVELOPMENT/data/generated/water_usage_data.csv",
                               anomalies_path="4_DEVELOPMENT/data/generated/ground_truth_anomalies.csv"):
    print("==================================================")
    print("STARTING TELEMETRY DATASET VALIDATION (14 CHECKS)")
    print("==================================================")

    if not os.path.isfile(data_path):
        print(f"FATAL: Telemetry file not found at {data_path}")
        return False, ["Telemetry file missing"]

    df = pd.read_csv(data_path)
    errors = []
    passes = []

    # Check 1: Non-negative consumption
    negative_count = (df["hourly_consumption_liters"] < 0).sum()
    if negative_count == 0:
        passes.append("Check 1 PASS: Zero negative consumption values.")
    else:
        errors.append(f"Check 1 FAIL: Found {negative_count} negative consumption readings.")

    # Check 2: Monotonic non-decreasing cumulative readings per meter
    monotonic_errors = 0
    for meter_id, group in df.groupby("meter_id"):
        diffs = group["cumulative_reading"].diff().dropna()
        if (diffs < -1e-5).any():
            monotonic_errors += 1
    if monotonic_errors == 0:
        passes.append("Check 2 PASS: Cumulative readings are strictly monotonic non-decreasing per meter.")
    else:
        errors.append(f"Check 2 FAIL: Decreasing cumulative readings found in {monotonic_errors} meters.")

    # Check 3: Valid timestamps
    try:
        df["parsed_timestamp"] = pd.to_datetime(df["timestamp"])
        passes.append("Check 3 PASS: All timestamps parsed to valid datetime objects.")
    except Exception as e:
        errors.append(f"Check 3 FAIL: Timestamp parsing failed: {e}")

    # Check 4: Expected hourly intervals (1 hour difference)
    interval_errors = 0
    for meter_id, group in df.groupby("meter_id"):
        sorted_ts = group["parsed_timestamp"].sort_values()
        diffs = sorted_ts.diff().dropna()
        if not (diffs == pd.Timedelta(hours=1)).all():
            interval_errors += 1
    if interval_errors == 0:
        passes.append("Check 4 PASS: Continuous exact 1-hour intervals across all meter time series.")
    else:
        errors.append(f"Check 4 FAIL: Timestamp discontinuity detected in {interval_errors} meters.")

    # Check 5: No duplicate meter/timestamp records
    duplicates = df.duplicated(subset=["meter_id", "timestamp"]).sum()
    if duplicates == 0:
        passes.append("Check 5 PASS: Zero duplicate (meter_id, timestamp) records.")
    else:
        errors.append(f"Check 5 FAIL: Found {duplicates} duplicate records.")

    # Check 6: Valid quality scores (0 to 100)
    invalid_quality = ((df["quality_score"] < 0) | (df["quality_score"] > 100)).sum()
    if invalid_quality == 0:
        passes.append("Check 6 PASS: All quality scores within [0, 100].")
    else:
        errors.append(f"Check 6 FAIL: Found {invalid_quality} invalid quality scores.")

    # Check 7: Valid categorical values
    valid_sources = {"api", "manual", "estimated"}
    invalid_sources = (~df["data_source"].isin(valid_sources)).sum()
    if invalid_sources == 0:
        passes.append("Check 7 PASS: All data_source values are valid.")
    else:
        errors.append(f"Check 7 FAIL: Found {invalid_sources} invalid data_source values.")

    # Check 8: Missing-value percentage (0%)
    null_count = df[["reading_id", "meter_id", "user_id", "timestamp", "hourly_consumption_liters", "cumulative_reading"]].isnull().sum().sum()
    if null_count == 0:
        passes.append("Check 8 PASS: Zero missing values in mandatory columns.")
    else:
        errors.append(f"Check 8 FAIL: Found {null_count} null values in core columns.")

    # Check 9: Reasonable temperature range [-20°C, 55°C]
    invalid_temp = ((df["temperature_celsius"] < -20.0) | (df["temperature_celsius"] > 55.0)).sum()
    if invalid_temp == 0:
        passes.append("Check 9 PASS: All temperature readings within realistic range [-20C, 55C].")
    else:
        errors.append(f"Check 9 FAIL: Found {invalid_temp} unrealistic temperature values.")

    # Check 10: Daily aggregates match hourly data
    df["date"] = df["parsed_timestamp"].dt.date
    daily_calc = df.groupby(["meter_id", "date"])["hourly_consumption_liters"].transform("sum").round(3)
    daily_mismatch = (np.abs(df["daily_consumption_liters"] - daily_calc) > 0.01).sum()
    if daily_mismatch == 0:
        passes.append("Check 10 PASS: Daily aggregates match sum of hourly readings perfectly.")
    else:
        errors.append(f"Check 10 FAIL: Found {daily_mismatch} daily aggregate mismatches.")

    # Check 11: Monthly aggregates match hourly data
    df["year_month"] = df["parsed_timestamp"].dt.to_period("M")
    monthly_calc = df.groupby(["meter_id", "year_month"])["hourly_consumption_liters"].transform("sum").round(3)
    monthly_mismatch = (np.abs(df["monthly_consumption_liters"] - monthly_calc) > 0.01).sum()
    if monthly_mismatch == 0:
        passes.append("Check 11 PASS: Monthly aggregates match sum of hourly readings perfectly.")
    else:
        errors.append(f"Check 11 FAIL: Found {monthly_mismatch} monthly aggregate mismatches.")

    # Check 12: Anomaly ground truth validity
    if os.path.isfile(anomalies_path):
        df_anom = pd.read_csv(anomalies_path)
        valid_anom_types = {"leak", "surge", "low", "unusual_pattern"}
        invalid_types = (~df_anom["anomaly_type"].isin(valid_anom_types)).sum()
        if invalid_types == 0 and len(df_anom) > 0:
            passes.append(f"Check 12 PASS: Valid ground truth anomalies file with {len(df_anom)} labeled events.")
        else:
            errors.append(f"Check 12 FAIL: Invalid anomaly types in ground truth: {invalid_types}")
    else:
        errors.append("Check 12 FAIL: Ground truth anomalies file not found.")

    # Check 13: At least three meter profiles exist
    unique_meters = df["meter_id"].nunique()
    if unique_meters >= 3:
        passes.append(f"Check 13 PASS: {unique_meters} distinct meter profiles present.")
    else:
        errors.append(f"Check 13 FAIL: Expected at least 3 distinct meter profiles, found {unique_meters}.")

    # Check 14: Expected number of records exists (2,160 per meter)
    expected_per_meter = 90 * 24
    expected_total = unique_meters * expected_per_meter
    if len(df) == expected_total:
        passes.append(f"Check 14 PASS: Exactly {len(df)} records ({unique_meters} meters x {expected_per_meter} hours).")
    else:
        errors.append(f"Check 14 FAIL: Record count mismatch. Expected {expected_total}, found {len(df)}.")

    # Print summary
    print("\nPASSED CHECKS:")
    for p in passes:
        print(f" [x] {p}")

    if errors:
        print("\nFAILED CHECKS:")
        for e in errors:
            print(f" [ ] {e}")
        return False, errors
    else:
        print("\nALL 14 TELEMETRY VALIDATION CHECKS PASSED!")
        print("==================================================")
        return True, []

if __name__ == "__main__":
    success, issues = validate_telemetry_dataset()
    if not success:
        sys.exit(1)
