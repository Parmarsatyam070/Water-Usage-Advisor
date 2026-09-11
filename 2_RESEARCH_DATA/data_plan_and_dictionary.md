# 📊 Data Architecture, Synthesis Methodology & Data Dictionary
**Document ID:** data_plan_and_dictionary  
**Directory:** 2_RESEARCH_DATA/  
**Lifecycle Stage:** Phase 2 (Week 3 Data Preparation Complete)  
**Status:** Validated Synthetic Dataset Generated & Verified

---

## 1. Dataset Generation Methodology & Reproducibility
The Phase 2 synthetic dataset was generated using `4_DEVELOPMENT/data/generate_telemetry.py` to establish a statistically realistic, deterministic foundation for subsequent predictive modeling and leak detection in Phase 3.

### 1.1 Reproducibility Parameters
- **Random Seed:** `42` (Fixed pseudo-random seed in Python `random` and `numpy.random`).
- **Telemetry Window:** 90 continuous days (2026-06-01 00:00:00 to 2026-08-29 23:00:00).
- **Temporal Resolution:** Hourly (24 observations per meter per day).
- **Total Duration:** 2,160 hours per meter.
- **Active Meter Count:** 3 distinct profiles ($3 \times 2,160 = 6,480$ total telemetry records).
- **Generated File Location:** [`4_DEVELOPMENT/data/generated/water_usage_data.csv`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/4_DEVELOPMENT/data/generated/water_usage_data.csv)
- **Ground-Truth Anomalies Location:** [`4_DEVELOPMENT/data/generated/ground_truth_anomalies.csv`](file:///c:/Users/singh/Cisco%20Packet%20Tracer%209.0.0/saves/ai%20sustainability%20project/4_DEVELOPMENT/data/generated/ground_truth_anomalies.csv)

---

## 2. Meter Profiles & Temporal Behavioral Modeling

| Meter ID | User ID | Profile Classification | Base Multiplier | Diurnal Pattern Dynamics | Initial Reading ($m^3$) |
| :---: | :---: | :--- | :---: | :--- | :---: |
| **1** | **1** | **Residential Single-Family** | $1.0\times$ | Sharp morning peak (07:00–09:00), afternoon lull, prominent evening peak (18:00–21:00), and near-zero nocturnal flow (01:00–04:00). Weekend volume $+25\%$. | $12,450.000$ |
| **2** | **2** | **Residential Multi-Family** | $2.8\times$ | Broader diurnal morning/evening peaks reflecting staggered tenant schedules. Higher baseline flow. | $38,200.000$ |
| **3** | **3** | **Commercial Campus Facility** | $5.0\times$ | Concentrated during business hours (08:00–18:00 on Mon–Fri). Minimal weekend and nocturnal usage ($<10\%$ of peak). | $95,600.000$ |

---

## 3. Ground-Truth Anomaly Catalog (For Honest Phase 3 Evaluation)
A total of **230 ground-truth anomaly hours** were injected with isolated metadata so that Phase 3 anomaly detection models can be evaluated objectively without data contamination:

| Anomaly Category | Target Meter | Schedule Window | Injected Signature | Total Hours | Operational Real-World Analogue |
| :--- | :---: | :--- | :--- | :---: | :--- |
| **Continuous Leak** | Meter 1 | Days 42–46 (all hours) | $+16.5\text{ L/hr}$ continuous non-zero flow through all nocturnal windows. | 120 hrs | Leaking toilet flapper valve or cracked service line. |
| **Sudden Surge** | Meter 1 | Day 71 (14:00–15:00) | $+420\text{ L/hr}$ catastrophic volumetric surge. | 2 hrs | Major pipe burst, ruptured outdoor bib, or severed line. |
| **Abnormal Low Flow** | Meter 2 | Days 28–31 (all hours) | Drops to $0.0\text{ L/hr}$ during normal active weekday hours. | 96 hrs | Vacant apartment block, main shutoff valve closure, or sensor failure. |
| **Unusual Nocturnal Pattern** | Meter 3 | Days 58–60 (00:00–03:00) | $+195\text{ L/hr}$ abnormal spike during closed hours. | 12 hrs | Runaway cooling tower fill valve or unmonitored overnight irrigation. |

> **Important Boundary Note:** Phase 2 establishes these labeled ground-truth events. Detection accuracy metrics (such as the target $>95\%$ sensitivity) will be formally measured in Phase 3.

---

## 4. Cumulative & Aggregate Calculation Logic
1. **Cumulative Reading:**
   $$\text{cumulative\_reading}[t] = \text{cumulative\_reading}[t-1] + \text{hourly\_consumption\_liters}[t]$$
   Strictly monotonic and non-decreasing across all $2,160$ timestamps per meter.
2. **Daily Aggregates (`daily_consumption_liters`):**
   Calculated as the exact sum of the 24 hourly readings for each calendar date. Verified with $0.00\%$ mismatch.
3. **Monthly Aggregates (`monthly_consumption_liters`):**
   Calculated as the exact sum of all hourly readings within each calendar month period (`2026-06`, `2026-07`, `2026-08`).

---

## 5. Telemetry Data Dictionary

| Column Name | Database Type | Unit / Format | Nullable | Validation Rules | Description |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `reading_id` | `BIGINT` | Integer ID | No | Auto-increment PK | Unique identifier for the telemetry reading. |
| `meter_id` | `INTEGER` | Integer ID | No | FK to `meters(meter_id)` | Linked smart meter hardware identity. |
| `user_id` | `INTEGER` | Integer ID | No | FK to `users(user_id)` | Owning user account identity. |
| `timestamp` | `TIMESTAMPTZ` | ISO 8601 | No | Hourly continuity | Exact timestamp of the interval reading. |
| `cumulative_reading` | `NUMERIC(12,3)`| Liters | No | Monotonic non-decreasing | Total cumulative flow registered on meter dial. |
| `hourly_consumption_liters`| `NUMERIC(10,3)`| Liters | No | $\ge 0.000$ | Volume consumed during the 1-hour interval. |
| `daily_consumption_liters` | `NUMERIC(10,3)`| Liters | Yes | $\sum \text{hourly}$ for date | Daily accumulated volume. |
| `monthly_consumption_liters`| `NUMERIC(12,3)`| Liters | Yes | $\sum \text{hourly}$ for month | Monthly accumulated volume. |
| `temperature_celsius` | `NUMERIC(5,2)` | Celsius ($^\circ\text{C}$)| Yes | $-20.0 \le T \le 55.0$ | Ambient local outdoor temperature. |
| `quality_score` | `INTEGER` | Score [0–100] | No | $0 \le Q \le 100$ | Telemetry integrity rating (98 for normal, 85 for anomalies). |
| `data_source` | `VARCHAR(50)` | Categorical | No | In `('api', 'manual', 'estimated')` | Always labeled `'estimated'` for synthetic telemetry. |
| `is_validated` | `BOOLEAN` | Boolean | No | `True` | Flags completion of automated pipeline quality checks. |

---

## 6. Known Assumptions & Limitations
- **Simulated Water Physics:** Synthetic data captures macroscopic diurnal trends, ambient temperature correlations, and known leak shapes, but does not simulate micro-level plumbing pressure transients or water hammer effects.
- **Data Source Labeling:** All synthetic records are explicitly tagged as `data_source = 'estimated'` to maintain research transparency and prevent conflation with live utility AMI telemetry.
