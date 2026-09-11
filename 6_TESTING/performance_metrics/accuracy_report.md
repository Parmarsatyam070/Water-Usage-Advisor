# Phase 3A Performance & Accuracy Report: Predictive Consumption Forecasting

**Project**: Smart Water Usage Advisor (UN SDG 6: Clean Water & Sanitation)  
**Phase**: 3A — AI Model Development (Predictive Consumption Forecasting)  
**Date**: September 11, 2026  
**Evaluation Target**: MAPE < 15.0% (Accuracy Proxy > 85.0%)  
**Primary ML Model**: Random Forest Regressor (`forecasting-v1.0`)  
**Official Benchmark**: Seasonal Naive 7-Day Persistence ($\hat{y}_t = y_{t-7}$)  

---

## 1. Executive Summary & Benchmark Comparison

This report documents the empirical evaluation of the Phase 3A predictive forecasting pipeline. Daily water consumption models were trained on chronological smart meter telemetry and evaluated against an untouched holdout test period.

### Critical Benchmark Finding
> **HONEST EVALUATION FINDING**:  
> The **Seasonal Naive 7-day persistence model** ($\hat{y}_t = y_{t-7}$) is designated as the official project benchmark and achieves **MAPE = 9.85%** ($R^2 = 0.9353$, MAE = 56.19 L).  
> The **Global Random Forest Regressor** (primary ML model) achieves **MAPE = 21.66%** ($R^2 = 0.9153$, MAE = 96.16 L).  
> **Seasonal Naive 7-day currently outperforms the Random Forest and all other candidate ML models on the untouched synthetic test set.**  
> Random Forest is preserved as the primary ML artifact for explainability and non-linear feature interactions, but it is **not** described as the best-performing forecasting method overall. The overall forecasting system is **not** claimed to be "85% accurate" merely because the baseline achieved MAPE < 15%.

---

## 2. Model vs. Baseline Comparison (Untouched Test Set)

Evaluation conducted on the 14-day holdout test period (August 16–29, 2026; $N=42$ meter-days):

| Model / Benchmark | Test MAE (L) | Test RMSE (L) | Test MAPE (%) | Test R2 | Accuracy Proxy (100 - MAPE) | Beats Seasonal Naive? | Target (MAPE < 15%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Seasonal Naive 7-day** (Official Benchmark) | **56.19** | **140.10** | **9.85%** | **0.9353** | **90.15%** | **Benchmark** | **ACHIEVED** |
| **Per-Meter Local Random Forest** | 80.55 | 129.49 | 15.70% | 0.9447 | 84.30% | NO | NOT ACHIEVED |
| **Ridge Regression ($\alpha=10$)** | 95.58 | 134.28 | 18.25% | 0.9406 | 81.75% | NO | NOT ACHIEVED |
| **Global Random Forest (Primary ML)** | 96.16 | 160.29 | 21.66% | 0.9153 | 78.34% | NO | NOT ACHIEVED |
| **Global Gradient Boosting (tuned)** | 113.04 | 202.01 | 27.05% | 0.8655 | 72.95% | NO | NOT ACHIEVED |
| **Naive Previous-Day ($t-1$)** | 189.34 | 417.50 | 30.83% | 0.4256 | 69.17% | NO | NOT ACHIEVED |

---

## 3. Dataset & Chronological Split Specification

### Telemetry Dataset
- **Source**: `4_DEVELOPMENT/data/generated/water_usage_data.csv` (Phase 2 Deterministic Telemetry)
- **Observations**: 6,480 hourly readings aggregated into 270 daily records across 3 meters (90 days per meter).
- **Consumer Profiles**:
  - Meter 1 (User 1): Residential Single-Family (~300–450 L/day)
  - Meter 2 (User 2): Residential Multi-Family (~1,000–1,400 L/day)
  - Meter 3 (User 3): Commercial Facility (~1,500–2,500 L/day)
- **Synthetic Data Disclaimer**: *Evaluation was performed on synthetic Phase 2 telemetry.*

### Strict Chronological Partitioning (No Shuffling)
- Initial 14 days dropped due to 14-day historical lag and rolling window calculation.
- **Training Period**: June 15, 2026 – August 1, 2026 (48 calendar days, 144 meter-days).
- **Validation Period**: August 2, 2026 – August 15, 2026 (14 calendar days, 42 meter-days) — *Used exclusively for candidate tuning*.
- **Test Period (Untouched Holdout)**: August 16, 2026 – August 29, 2026 (14 calendar days, 42 meter-days) — *Unseen future observations*.

---

## 4. Candidate Model Comparison

### Baseline Models
1. **Seasonal Naive 7-Day** ($\hat{y}_t = y_{t-7}$):
   - MAE: 56.19 L | RMSE: 140.10 L | **MAPE: 9.85%** | $R^2$: 0.9353
2. **Naive Previous-Day** ($\hat{y}_t = y_{t-1}$):
   - MAE: 189.34 L | RMSE: 417.50 L | **MAPE: 30.83%** | $R^2$: 0.4256

### Model 1: Random Forest Regressor (Primary ML Model)
- **Algorithm**: `RandomForestRegressor`
- **Tuned Hyperparameters**: `n_estimators=100`, `max_depth=6`, `min_samples_split=4`, `min_samples_leaf=2`, `random_state=42`
- **Validation Performance**: Val MAE = 163.32 L | Val MAPE = 16.07% | Val $R^2$ = 0.7357
- **Test Performance (Overall)**:
  - MAE: **96.16 L**
  - RMSE: **160.29 L**
  - MAPE: **21.66%**
  - $R^2$: **0.9153**
  - Accuracy Proxy: **78.34%**
  - Training Time: 0.2101 sec | Inference Time: 0.0135 sec

### Model 2: Gradient Boosting Regressor
- **Algorithm**: `GradientBoostingRegressor`
- **Tuned Hyperparameters**: `n_estimators=120`, `learning_rate=0.08`, `max_depth=4`, `min_samples_split=4`, `random_state=42`
- **Validation Performance**: Val MAE = 230.80 L | Val MAPE = 20.53% | Val $R^2$ = 0.4221
- **Test Performance (Overall)**:
  - MAE: **113.04 L**
  - RMSE: **202.01 L**
  - MAPE: **27.05%**
  - $R^2$: **0.8655**
  - Accuracy Proxy: **72.95%**

### Model 3: Ridge Regression (Linear Regularized Baseline)
- **Algorithm**: `Ridge(alpha=10.0, random_state=42)`
- **Test Performance**: MAE = 95.58 L | RMSE = 134.28 L | **MAPE: 18.25%** | $R^2$: 0.9406

### Final Model Selection Rationale
Random Forest Regressor was selected as the primary ML model because:
1. It achieved the lowest validation MAPE (16.07% vs. 20.53% for Gradient Boosting and 29.00% for Ridge).
2. It captures non-linear interactions across cyclical calendar features and rolling statistics.
3. It natively provides feature importance attribution for user-facing explainability.
4. It outperforms the naive previous-day baseline (21.66% vs. 30.83% MAPE, a 29.74% relative error reduction).

---

## 5. Disaggregated Per-Profile Performance (Global Random Forest)

| Meter ID | Profile Type | Test MAE (L) | Test RMSE (L) | Test MAPE (%) | Test R2 | Accuracy Proxy | Target Status (MAPE < 15%) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Meter 1** | Residential Single-Family | 183.80 | 259.02 | 55.88% | -26.7900 | 44.12% | **NOT ACHIEVED** |
| **Meter 2** | Residential Multi-Family | 27.48 | 34.65 | **2.90%** | **0.9392** | **97.10%** | **ACHIEVED** |
| **Meter 3** | Commercial Facility | 77.20 | 93.72 | **6.21%** | **0.9776** | **93.79%** | **ACHIEVED** |

### Per-Profile Evaluation Analysis
- **Multi-Family (Meter 2)** and **Commercial (Meter 3)** perform exceptionally well, achieving **sub-3%** and **sub-7%** MAPE respectively, easily surpassing the <15% target and explaining over 93% and 97% of consumption variance ($R^2 > 0.93$).
- **Single-Family (Meter 1)** fails the target due to the root cause detailed below.

---

## 6. In-Depth Error Analysis & Root Cause Diagnosis

### Top 4 Residual Errors on Test Set
| Date | Meter ID | Profile | Actual (L) | Predicted (L) | Absolute Error (L) | Percentage Error |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **2026-08-25** | 1 | Single-Family | 318.62 | 963.49 | 644.87 L | **202.39%** |
| **2026-08-18** | 1 | Single-Family | 329.30 | 903.15 | 573.85 L | **174.26%** |
| **2026-08-28** | 3 | Commercial | 1684.19 | 1897.97 | 213.78 L | **12.69%** |
| **2026-08-26** | 1 | Single-Family | 325.20 | 521.01 | 195.81 L | **60.21%** |

### Root Cause Diagnosis: The Historical Anomaly Echo
1. **The Injected Outlier**: In Phase 2, a ground-truth continuous leak/surge anomaly (+420 L surge) was injected into Meter 1 on **Day 71 (August 11, 2026)**, causing daily consumption to jump from normal ~320 L to **1,166.58 L**.
2. **Lag Propagation**: In the Random Forest model, the two most influential predictors are $lag_{7d}$ (42.6% importance) and $lag_{14d}$ (36.8% importance).
   - On **August 18** (Day 78, test set day 3), $lag_{7d}$ referenced August 11 ($1,166.58$ L). The model predicted **903.15 L** against actual normal usage of **329.30 L** (error: +573.85 L).
   - On **August 25** (Day 85, test set day 10), $lag_{14d}$ referenced August 11 ($1,166.58$ L). The model predicted **963.49 L** against actual normal usage of **318.62 L** (error: +644.87 L).
3. **Why Seasonal Naive Outperformed ML Here**:
   - Seasonal Naive ($t-7$) suffered the echo once on August 18, but had no $t-14$ predictor, escaping the second error on August 25.
   - The tree model had *two* opportunities to echo the anomaly.
4. **Architectural Insight**:
   - This diagnostic proves why **Phase 3B (Anomaly Detection & Telemetry Cleaning)** is an essential upstream prerequisite in the production pipeline before feeding historical telemetry into autoregressive lag features.

---

## 7. Model Explainability & Feature Importance

Feature importance extraction from the trained Global Random Forest:

| Rank | Feature | Importance Weight | Feature Type | Interpretation |
| :---: | :--- | :---: | :--- | :--- |
| 1 | `lag_7d` | **0.4257** | Historical Lag | Strong 7-day weekly recurrence pattern |
| 2 | `lag_14d` | **0.3681** | Historical Lag | Bi-weekly seasonal consistency |
| 3 | `rolling_min_7d` | **0.0581** | Shifted Rolling | Baseline non-leak floor consumption |
| 4 | `profile_multi_family` | **0.0476** | Categorical Context | Shifts base predictions to ~1,100 L regime |
| 5 | `rolling_max_7d` | **0.0161** | Shifted Rolling | Captures peak usage envelope |
| 6 | `day_of_week` | **0.0156** | Calendar | Differentiates weekend vs. weekday patterns |
| 7 | `day_of_month` | **0.0131** | Calendar | Minor monthly cycle variations |
| 8 | `lag_1d` | **0.0123** | Historical Lag | Day-to-day persistence |

*(Note: Feature importances represent empirical splits in the decision trees, demonstrating predictive association rather than causal proof).*

---

## 8. Demonstration 7-Day Forward Forecast

Multi-step autoregressive forecasts generated from the end of historical data:

### Meter 1 (Residential Single-Family)
- **Predicted 7-Day Total**: **2,788.74 Liters** (Daily avg: 398.39 L)
- **Predicted Monthly Projected Volume**: **11,951.74 Liters**
- **Predicted Peak Day**: **2026-08-30** (582.52 L, Sunday weekend spike)

### Meter 2 (Residential Multi-Family)
- **Predicted 7-Day Total**: **6,790.42 Liters** (Daily avg: 970.06 L)
- **Predicted Monthly Projected Volume**: **29,101.80 Liters**
- **Predicted Peak Day**: **2026-08-30** (1,255.30 L, Sunday weekend spike)

### Meter 3 (Commercial Facility)
- **Predicted 7-Day Total**: **9,753.27 Liters** (Daily avg: 1,393.32 L)
- **Predicted Monthly Projected Volume**: **41,799.73 Liters**
- **Predicted Peak Day**: **2026-08-31** (1,997.91 L, Monday commercial peak)

---

## 9. Compliance & Quality Verification

| Check Item | Status | Verification Detail |
| :--- | :---: | :--- |
| **Phase 2 Dataset Reused** | PASSED | `4_DEVELOPMENT/data/generated/water_usage_data.csv` (6,480 rows) |
| **No Target Leakage** | PASSED | Rolling stats use `shift(1)`; lags strictly historical |
| **Chronological Split** | PASSED | Train (6/15–8/1) < Val (8/2–8/15) < Test (8/16–8/29) |
| **Baseline Implemented** | PASSED | Seasonal Naive 7-day (9.85%) & Naive 1-day (30.83%) |
| **Multiple Models Evaluated** | PASSED | Random Forest, Gradient Boosting, Ridge |
| **Safe Zero MAPE** | PASSED | $\epsilon = 1.0$ denominator prevents division by zero |
| **Per-Profile Breakdown** | PASSED | Separately reported for Meters 1, 2, and 3 |
| **Error Analysis Performed** | PASSED | August 18 and August 25 anomaly echoes diagnosed |
| **Model Serialized** | PASSED | `joblib` artifact and `model_metadata.json` saved |
| **No Fake Confidence Scores** | PASSED | `confidence_score` set to `NULL` in prediction persistence |
| **Unit Tests Passing** | PASSED | 15/15 unit tests in `test_ml_models.py` passing |

---

## 10. Final Conclusion on Target Metric

- **Project Target**: MAPE < 15.0%
- **Seasonal Naive 7-Day Benchmark**: **ACHIEVED (9.85%)**
- **Global Random Forest ML Model**: **NOT ACHIEVED (21.66%)**
- **Sub-Profile Performance**:
  - Residential Multi-Family: **ACHIEVED (2.90%)**
  - Commercial Facility: **ACHIEVED (6.21%)**
  - Residential Single-Family: **NOT ACHIEVED (55.88%)**

**Official Finding**: The Seasonal Naive 7-day baseline serves as the official benchmark and achieves the project target. The primary Random Forest ML model achieves strong performance on multi-family and commercial profiles, but suffers on single-family due to historical anomaly propagation. Data cleaning in Phase 3B will resolve anomaly echoes for future production deployment.
