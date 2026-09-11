"""
Smart Water Usage Advisor - Predictive Model Evaluation Module
Calculates standard regression metrics: MAE, RMSE, MAPE, R2, and accuracy proxy.
Includes safe zero-handling for MAPE, baseline comparison, per-profile breakdown,
error analysis, and the authoritative Model vs Baseline Comparison table.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def calculate_safe_mape(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1.0) -> float:
    """
    Computes Mean Absolute Percentage Error safely.
    Uses denominator max(y_true, epsilon) to prevent division by zero or infinite error
    during low-consumption or zero-consumption periods.
    Returns value in percentage (e.g. 12.4 for 12.4%).
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.maximum(y_true, epsilon)
    mape = np.mean(np.abs(y_true - y_pred) / denom) * 100.0
    return float(round(mape, 2))

def compute_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Computes standard regression performance metrics.
    Accuracy proxy is defined as max(0.0, 100.0 - MAPE).
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.maximum(0.0, np.asarray(y_pred, dtype=float))  # Predictions cannot be negative

    mae = float(round(mean_absolute_error(y_true, y_pred), 3))
    rmse = float(round(np.sqrt(mean_squared_error(y_true, y_pred)), 3))
    r2 = float(round(r2_score(y_true, y_pred), 4))
    mape = calculate_safe_mape(y_true, y_pred)
    accuracy_proxy = float(round(max(0.0, 100.0 - mape), 2))

    return {
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape,
        "R2": r2,
        "accuracy_proxy": accuracy_proxy
    }

def evaluate_baseline_models(test_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Evaluates naive and seasonal naive baseline models on the test set.
    Baseline 1: Previous-day persistence (y_hat_t = lag_1d)
    Baseline 2: Seasonal 7-day persistence (y_hat_t = lag_7d) [OFFICIAL BENCHMARK]
    """
    y_true = test_df["daily_consumption_liters"].values

    # Naive t-1
    y_naive_1d = test_df["lag_1d"].values
    metrics_naive_1d = compute_regression_metrics(y_true, y_naive_1d)

    # Seasonal Naive t-7 (Official Benchmark)
    y_naive_7d = test_df["lag_7d"].values
    metrics_naive_7d = compute_regression_metrics(y_true, y_naive_7d)

    return {
        "naive_previous_day": metrics_naive_1d,
        "seasonal_naive_7d": metrics_naive_7d
    }

def generate_model_vs_baseline_comparison(
    test_df: pd.DataFrame,
    predictions_dict: Dict[str, np.ndarray]
) -> Dict[str, Any]:
    """
    Constructs the authoritative Model vs Baseline Comparison.
    Designates Seasonal Naive 7-day as the benchmark and explicitly assesses
    whether candidate ML models beat the benchmark MAPE.
    """
    baselines = evaluate_baseline_models(test_df)
    seasonal_naive_mape = baselines["seasonal_naive_7d"]["MAPE"]
    y_true = test_df["daily_consumption_liters"].values

    comparison_rows = []

    # 1. Benchmark entry
    sn_met = baselines["seasonal_naive_7d"]
    comparison_rows.append({
        "model_name": "Seasonal Naive 7-day",
        "MAE": sn_met["MAE"],
        "RMSE": sn_met["RMSE"],
        "MAPE": sn_met["MAPE"],
        "R2": sn_met["R2"],
        "accuracy_proxy": sn_met["accuracy_proxy"],
        "beats_seasonal_naive": "Benchmark",
        "target_achieved": sn_met["MAPE"] < 15.0
    })

    # 2. Naive previous-day entry
    np_met = baselines["naive_previous_day"]
    comparison_rows.append({
        "model_name": "Naive Previous-Day (t-1)",
        "MAE": np_met["MAE"],
        "RMSE": np_met["RMSE"],
        "MAPE": np_met["MAPE"],
        "R2": np_met["R2"],
        "accuracy_proxy": np_met["accuracy_proxy"],
        "beats_seasonal_naive": "YES" if np_met["MAPE"] < seasonal_naive_mape else "NO",
        "target_achieved": np_met["MAPE"] < 15.0
    })

    # 3. Model candidate entries
    for model_name, preds in predictions_dict.items():
        met = compute_regression_metrics(y_true, preds)
        beats = "YES" if met["MAPE"] < seasonal_naive_mape else "NO"
        comparison_rows.append({
            "model_name": model_name,
            "MAE": met["MAE"],
            "RMSE": met["RMSE"],
            "MAPE": met["MAPE"],
            "R2": met["R2"],
            "accuracy_proxy": met["accuracy_proxy"],
            "beats_seasonal_naive": beats,
            "target_achieved": met["MAPE"] < 15.0
        })

    # Generate markdown table string
    table_lines = [
        "| Model / Benchmark | Test MAE (L) | Test RMSE (L) | Test MAPE (%) | Test R2 | Accuracy Proxy | Beats Seasonal Naive? |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |"
    ]
    for r in comparison_rows:
        table_lines.append(
            f"| **{r['model_name']}** | {r['MAE']:.2f} | {r['RMSE']:.2f} | {r['MAPE']:.2f}% | {r['R2']:.4f} | {r['accuracy_proxy']:.2f}% | {r['beats_seasonal_naive']} |"
        )
    markdown_table = "\n".join(table_lines)

    return {
        "benchmark_mape": seasonal_naive_mape,
        "rows": comparison_rows,
        "markdown_table": markdown_table
    }

def evaluate_per_profile(
    test_df: pd.DataFrame,
    y_pred: np.ndarray
) -> Dict[str, Dict[str, float]]:
    """
    Disaggregates evaluation metrics across the three distinct consumer profiles.
    Meter 1: Residential Single-Family
    Meter 2: Residential Multi-Family
    Meter 3: Commercial Facility
    """
    df = test_df.copy()
    df["predicted"] = y_pred

    profile_results = {}
    profile_names = {
        1: "Residential Single-Family (Meter 1)",
        2: "Residential Multi-Family (Meter 2)",
        3: "Commercial Facility (Meter 3)"
    }

    for meter_id, name in profile_names.items():
        subset = df[df["meter_id"] == meter_id]
        if len(subset) > 0:
            metrics = compute_regression_metrics(
                subset["daily_consumption_liters"].values,
                subset["predicted"].values
            )
            profile_results[name] = metrics

    return profile_results

def analyze_top_errors(
    test_df: pd.DataFrame,
    y_pred: np.ndarray,
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Identifies and investigates top residual errors in test predictions.
    """
    df = test_df.copy()
    df["predicted"] = np.round(y_pred, 2)
    df["actual"] = np.round(df["daily_consumption_liters"], 2)
    df["abs_error"] = np.round(np.abs(df["actual"] - df["predicted"]), 2)
    df["pct_error"] = np.round((df["abs_error"] / np.maximum(df["actual"], 1.0)) * 100.0, 2)

    top_errors_df = df.sort_values(by="abs_error", ascending=False).head(top_n)

    records = []
    for _, row in top_errors_df.iterrows():
        records.append({
            "date": str(row["date"].date()) if hasattr(row["date"], "date") else str(row["date"]),
            "meter_id": int(row["meter_id"]),
            "profile": row.get("profile_name", f"Meter {row['meter_id']}"),
            "actual": float(row["actual"]),
            "predicted": float(row["predicted"]),
            "abs_error": float(row["abs_error"]),
            "pct_error": float(row["pct_error"])
        })

    return records
