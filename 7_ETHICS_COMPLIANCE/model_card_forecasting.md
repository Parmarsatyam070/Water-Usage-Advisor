# 📋 Model Card: Predictive Water Consumption Forecaster

**Model Name:** Smart Water Usage Forecaster (`forecasting-v1.0`)  
**Standard:** Mitchell et al. (2019) *Model Cards for Model Reporting*  
**Project:** Smart Water Usage Advisor (UN SDG 6: Clean Water & Sanitation)  
**Date:** September 2026  
**License:** Educational / Open Sustainability Research  

---

## 1. Model Details

* **Developer:** Smart Water Usage Advisor Engineering Team
* **Model Type:** Tabular Ensemble Regression (Global Random Forest Regressor, `n_estimators=150`, `max_depth=12`, `min_samples_leaf=2`)
* **Input Features (22 total):**
  - *Calendar & Cyclical:* Day of week, day of month, month, weekend indicator, sine/cosine cyclical transforms.
  - *Environmental:* Daily mean temperature (°C).
  - *Historical Lags:* Lags at $t-1, t-2, t-3, t-7, t-14$ days.
  - *Strictly Shifted Rolling Statistics:* 7-day and 14-day rolling mean, standard deviation, min, max (computed with `.shift(1)` to eliminate temporal leakage).
  - *Profile Context:* One-hot encoded consumer profile (Single-Family Residential, Multi-Family Residential, Commercial Facility).
* **Output:** Predicted next-day total consumption in Liters ($\hat{y}_{t+1}$), extensible via iterative autoregression to a 7-day forward horizon.
* **Serialization Artifacts:** `5_AI_COMPONENTS/predictive_models/models/forecasting_model.joblib`, `model_metadata.json`.

---

## 2. Intended Use

* **Primary Intended Use:** To provide domestic and commercial water consumers with forward-looking 7-day water consumption forecasts and budget trajectory estimates on an interactive advisory dashboard.
* **Secondary Intended Use:** Educational awareness regarding the impact of weather and weekly routines on household water demand.
* **Out-of-Scope Uses:**
  - Automated billing dispute adjudication or punitive utility surcharges.
  - Sub-hourly hydraulic pressure control or real-time pump scheduling.
  - Life-safety critical systems or emergency municipal reservoir allocation.

---

## 3. Factors and Subpopulations

The model was evaluated across three distinct consumer profiles representing diverse consumption scales and occupancy patterns:
1. **Meter 1 (Residential Single-Family):** ~330 L/day base usage, 1–2 occupants, diurnal peaks at morning and evening.
2. **Meter 2 (Residential Multi-Family):** ~1,100 L/day base usage, 4–5 occupants, continuous domestic activity.
3. **Meter 3 (Commercial Cafe/Facility):** ~1,800 L/day base usage, high weekday operating volume, low nighttime base flow.

---

## 4. Metrics & Evaluation Methodology

* **Splitting Protocol:** Strict chronological splitting (Zero Future Data Leakage):
  - Training Set: Days 15–76 (144 meter-days)
  - Validation Set: Days 77–90 (42 meter-days, hyperparameter tuning)
  - Test Set: Days 91–104 (42 meter-days, completely untouched until final benchmark)
* **Evaluation Metrics:** Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), Mean Absolute Percentage Error (MAPE), Coefficient of Determination ($R^2$).

### Empirical Holdout Test Results (Days 91–104, N=42)

| Model / Benchmark | Test MAE (L) | Test RMSE (L) | Test MAPE (%) | Test $R^2$ | Accuracy Proxy ($100 - \text{MAPE}$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Seasonal Naive 7-day** (Official Benchmark) | **56.19** | **140.10** | **9.85%** | **0.9353** | **90.15%** |
| **Per-Meter Local Random Forest** | 80.55 | 129.49 | 15.70% | 0.9447 | 84.30% |
| **Ridge Regression ($\alpha=10$)** | 95.58 | 134.28 | 18.25% | 0.9406 | 81.75% |
| **Global Random Forest (Primary ML)** | 96.16 | 160.29 | 21.66% | 0.9153 | 78.34% |
| **Global Gradient Boosting (tuned)** | 113.04 | 202.01 | 27.05% | 0.8655 | 72.95% |
| **Naive Previous-Day ($t-1$)** | 189.34 | 417.50 | 30.83% | 0.4256 | 69.17% |

### Disaggregated Profile Performance (Global Random Forest)

| Meter Profile | Test MAE (L) | Test RMSE (L) | Test MAPE (%) | Test $R^2$ |
| :--- | :---: | :---: | :---: | :---: |
| **Meter 1 (Single-Family)** | 183.80 | 259.02 | 55.88% | -26.7900 |
| **Meter 2 (Multi-Family)** | 27.48 | 34.65 | **2.90%** | **0.9392** |
| **Meter 3 (Commercial)** | 77.20 | 93.72 | **6.21%** | **0.9776** |

---

## 5. Quantitative Analyses & Error Diagnosis

1. **Benchmark Superiority:** The designated project benchmark (Seasonal Naive 7-day) achieved MAPE = 9.85%, meeting the project target (<15%), while the Global Random Forest achieved MAPE = 21.66%.
2. **Anomaly Echoing on Meter 1:** On Day 71 (August 11), a major pipe burst surge was injected into Meter 1. Because the Random Forest assigns high feature importance to $lag_{7d}$ (42.6%) and $lag_{14d}$ (36.8%), this historical surge echoed into predictions at $t+7$ and $t+14$, artificially inflating forecasted usage.
3. **Engineering Insight:** Demonstrates that Phase 3B anomaly detection is a critical preprocessing prerequisite to scrub abnormal surges before computing lag features for forecasting.

---

## 6. Ethical Considerations & Responsible AI

* **Uncertainty Presentation:** The model outputs validated forecast uncertainty bounds derived from validation residual quantiles (Phase 3A methodology) rather than unverified Gaussian assumptions.
* **No Shaming:** Predictions are framed as forward planning tools ("Forecasted weekly budget trajectory: within normal target") rather than warnings.
* **Fairness:** Normalization parameters prevent multi-family residential households from receiving disproportionate surge warnings.

---

## 7. Caveats and Recommendations

* For production deployments where sudden pipe bursts or hardware anomalies may occur, upstream anomaly flags from Phase 3B must be used to impute median consumption values before updating lag buffers.
* When historical data is limited (< 14 days), the system gracefully falls back to the Seasonal Naive 7-day benchmark.
