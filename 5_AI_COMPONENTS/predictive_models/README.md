# Predictive Consumption Forecasting Engine

**Component**: AI Predictive Models (`5_AI_COMPONENTS/predictive_models/`)  
**Project**: Smart Water Usage Advisor (UN SDG 6: Clean Water & Sanitation)  
**Phase**: 3A — AI Model Development (Week 4)  
**Model Version**: `forecasting-v1.0`  
**Target Target Metric**: MAPE < 15.0% (Accuracy Proxy > 85.0%)  

---

## 1. Executive Summary & Benchmark Findings

The **Predictive Consumption Forecasting Engine** provides reproducible time-series regression for forecasting future daily water consumption from historical hourly smart meter telemetry.

### Key Benchmark Finding
> **IMPORTANT: Official Benchmark vs. Machine Learning Performance**
> - **Official Benchmark**: The **Seasonal Naive 7-day model** ($\hat{y}_t = y_{t-7}$) is the designated project benchmark, achieving **MAPE = 9.85%** ($R^2 = 0.9353$, MAE = 56.19 L) on the untouched test set.
> - **Primary ML Model**: The **Random Forest Regressor** is preserved as the primary machine-learning artifact for interpretability and feature attribution. On the untouched test set, the Global Random Forest achieves **MAPE = 21.66%** ($R^2 = 0.9153$, MAE = 96.16 L).
> - **Transparent Comparison**: **Seasonal Naive 7-day currently outperforms the Global Random Forest (9.85% vs. 21.66%) and Per-Meter Local Models (9.85% vs. 15.70%) on the untouched synthetic test set.**
> - The Random Forest is **not** described as the best-performing model overall. The system is not claimed to be "85% accurate" merely because the baseline achieved MAPE < 15%.

---

## 2. Model vs Baseline Comparison (Untouched Test Set)

Evaluation on the 14-day holdout test period (August 16–29, 2026; $N=42$ meter-days):

| Model / Benchmark | Test MAE (L) | Test RMSE (L) | Test MAPE (%) | Test R2 | Accuracy Proxy (100 - MAPE) | Beats Seasonal Naive? | Target (MAPE < 15%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Seasonal Naive 7-day** (Official Benchmark) | **56.19** | **140.10** | **9.85%** | **0.9353** | **90.15%** | **Benchmark** | **ACHIEVED** |
| **Per-Meter Local Random Forest** | 80.55 | 129.49 | 15.70% | 0.9447 | 84.30% | NO | NOT ACHIEVED |
| **Ridge Regression ($\alpha=10$)** | 95.58 | 134.28 | 18.25% | 0.9406 | 81.75% | NO | NOT ACHIEVED |
| **Global Random Forest (Primary ML)** | 96.16 | 160.29 | 21.66% | 0.9153 | 78.34% | NO | NOT ACHIEVED |
| **Global Gradient Boosting (tuned)** | 113.04 | 202.01 | 27.05% | 0.8655 | 72.95% | NO | NOT ACHIEVED |
| **Naive Previous-Day ($t-1$)** | 189.34 | 417.50 | 30.83% | 0.4256 | 69.17% | NO | NOT ACHIEVED |

---

## 3. Disaggregated Per-Profile Performance (Global Random Forest)

| Meter ID | Consumer Profile | Test MAE (L) | Test RMSE (L) | Test MAPE (%) | Test R2 | Accuracy Proxy | Target Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Meter 1** | Residential Single-Family | 183.80 | 259.02 | 55.88% | -26.7900 | 44.12% | NOT ACHIEVED |
| **Meter 2** | Residential Multi-Family | 27.48 | 34.65 | **2.90%** | **0.9392** | **97.10%** | **ACHIEVED** |
| **Meter 3** | Commercial Facility | 77.20 | 93.72 | **6.21%** | **0.9776** | **93.79%** | **ACHIEVED** |

### Root-Cause Diagnosis of Error on Meter 1
1. **Historical Anomaly Echo**: On Day 71 (August 11), a massive leak/surge anomaly (+420 L surge / 1,166.58 L daily total) was injected into Meter 1. Because the tree model heavily relies on $lag_{7d}$ (42.6% importance) and $lag_{14d}$ (36.8% importance), that historical anomaly echoes into test forecasts on August 18 ($t+7$) and August 25 ($t+14$), where predictions spike to ~903 L and ~963 L against actual normal usage of ~320 L.
2. **Cross-Meter Pooling**: In a global model, Meter 1 (~330 L/day) is pooled with Meter 2 (~1,100 L) and Meter 3 (~1,800 L). High-lag observations cause tree splits to route single-family predictions to higher-volume leaf nodes.
3. **Production Recommendation**: Highlights that **Phase 3B (Anomaly & Leak Detection / Telemetry Cleaning)** is an essential upstream prerequisite in production before feeding raw telemetry into lag features.

---

## 4. Architecture & Anti-Leakage Design

```
Raw Telemetry (water_usage_data.csv)
      │
      ▼
Hourly-to-Daily Aggregation [aggregate_hourly_to_daily()]
      │
      ▼
Anti-Leakage Feature Extraction [extract_forecasting_features()]
      ├─ Calendar & Cyclical Features (DOW, Month, sin/cos)
      ├─ Lags (t-1, t-2, t-3, t-7, t-14)
      ├─ Strictly Shifted Rolling Stats (7d/14d mean/std/min/max via shift(1))
      └─ Profile Categorical Context (One-hot encoding)
      │
      ▼
Chronological Split [chronological_train_val_test_split()]
      ├─ Training Set:   Days 15–76 (144 rows, 2026-06-15 to 2026-08-01)
      ├─ Validation Set: Days 77–90 (42 rows, 2026-08-02 to 2026-08-15)
      └─ Test Set:       Days 91–104 (42 rows, 2026-08-16 to 2026-08-29) [UNTOUCHED]
      │
      ▼
Candidate Tuning (Val Set Only) ──► Random Forest Regressor Selected
      │
      ▼
Retrain on Combined Train+Val ──► Final Evaluation on Untouched Test Set
      │
      ▼
Multi-Step Autoregressive 7-Day Forward Forecast Generator
      │
      ▼
Artifact Serialization: forecasting_model.joblib & model_metadata.json
```

### Strict Anti-Leakage Protocol
1. **Chronological Splitting**: No random shuffling. Test data represents unseen future dates.
2. **Shifted Rolling Windows**: All rolling calculations explicitly apply `.shift(1)` to ensure the current day's consumption is NEVER included in rolling statistics.
3. **Purely Historical Lags**: Lags strictly reference days $t-1, t-2, t-3, t-7, t-14$.
4. **Validation-Only Tuning**: Hyperparameter decisions are evaluated strictly on the validation set; the test set remains untouched until final benchmarking.

---

## 5. Feature Engineering Schema (22 Predictors)

1. **Calendar Features** (4): `day_of_week`, `day_of_month`, `month`, `is_weekend`
2. **Cyclical Transforms** (4): `dow_sin`, `dow_cos`, `month_sin`, `month_cos`
3. **Environment** (1): `temperature_celsius`
4. **Historical Lags** (5): `lag_1d`, `lag_2d`, `lag_3d`, `lag_7d`, `lag_14d`
5. **Shifted Rolling Windows** (5): `rolling_mean_7d`, `rolling_std_7d`, `rolling_min_7d`, `rolling_max_7d`, `rolling_mean_14d`
6. **Profile Context** (3): `profile_single_family`, `profile_multi_family`, `profile_commercial`

### Tree Feature Importances (Random Forest)
- `lag_7d`: **42.57%**
- `lag_14d`: **36.81%**
- `rolling_min_7d`: **5.81%**
- `profile_multi_family`: **4.76%**
- `rolling_max_7d`: **1.61%**
- `day_of_week`: **1.56%**

*(Note: Feature importance indicates predictive association within the regression tree, not causal proof).*

---

## 6. Model Serialization & Versioning

- **Serialized Artifact**: `5_AI_COMPONENTS/predictive_models/models/forecasting_model.joblib`
- **Metadata Document**: `5_AI_COMPONENTS/predictive_models/models/model_metadata.json`
- **Feature Schema**: `5_AI_COMPONENTS/predictive_models/models/feature_names.json`
- **Demonstration Forecasts**: `5_AI_COMPONENTS/predictive_models/models/demonstration_7day_forecasts.json`

### Metadata Schema
```json
{
  "algorithm": "random_forest",
  "model_version": "forecasting-v1.0",
  "training_samples": 186,
  "training_duration_sec": 0.2101,
  "official_benchmark": "Seasonal Naive 7-day",
  "benchmark_mape": 9.85,
  "beats_seasonal_naive": false,
  "overall_test_metrics": {
    "MAE": 96.158,
    "RMSE": 160.288,
    "MAPE": 21.66,
    "R2": 0.9153,
    "accuracy_proxy": 78.34
  },
  "synthetic_data_disclaimer": "Evaluation was performed on synthetic Phase 2 telemetry."
}
```

---

## 7. Database Integration & Security Protocol

- **Target Table**: Authoritative `predictions` table in PostgreSQL.
- **Columns Populated**: `meter_id`, `user_id`, `prediction_date`, `predicted_daily_liters`, `predicted_weekly_liters`, `predicted_monthly_liters`, `confidence_score`, `model_version`, `prediction_timestamp`.
- **Honest Confidence Representation**: `confidence_score` is intentionally left `NULL`. The deterministic tree regressor does not provide calibrated statistical intervals; no fabricated or hardcoded confidence percentages are stored.
- **Security Rule**: Database credentials are never hardcoded and must be loaded from `.env`.

---

## 8. Usage Instructions

### Running Training & Benchmark Pipeline
```powershell
.venv\Scripts\python 5_AI_COMPONENTS/predictive_models/train_forecasting_model.py
```

### Programmatic Usage via Compatibility Wrapper
```python
from 4_DEVELOPMENT.ml_models import train_model, evaluate_model, predict, load_model

# 1. Train model
forecaster, metadata = train_model("4_DEVELOPMENT/data/generated/water_usage_data.csv")

# 2. Evaluate on test set
eval_results = evaluate_model(forecaster, test_df)
print(eval_results["comparison_table"])

# 3. Predict on new observations
daily_predictions = predict(forecaster, feature_df)
```

### Running Unit Tests
```powershell
.venv\Scripts\pytest 6_TESTING/unit_tests/test_ml_models.py -v
```

---

## 9. Synthetic Data Disclaimer

> **Evaluation was performed on synthetic Phase 2 telemetry.**  
> Synthetic data generated in Phase 2 contains deterministic weekly cycles and injected anomaly pulses. Real-world validation on actual municipal or industrial meter networks will be required in subsequent phases.
