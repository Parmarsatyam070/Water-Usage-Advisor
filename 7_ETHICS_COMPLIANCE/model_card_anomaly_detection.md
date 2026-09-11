# 📋 Model Card: Water Anomaly & Leak Detection Engine

**Model Name:** Hybrid Water Anomaly & Leak Detector (`anomaly-detector-v1.0`)  
**Standard:** Mitchell et al. (2019) *Model Cards for Model Reporting*  
**Project:** Smart Water Usage Advisor (UN SDG 6: Clean Water & Sanitation)  
**Date:** September 2026  
**License:** Educational / Open Sustainability Research  

---

## 1. Model Details

* **Developer:** Smart Water Usage Advisor Engineering Team
* **Architecture:** 4-Layer Hybrid Diagnostic Pipeline:
  1. **Layer 1 (Statistical Filter):** Diurnal median and Median Absolute Deviation (MAD) baseline + 24-hour shifted rolling window (`shift(1)`) computing robust z-scores: $z = \frac{x - \text{median}}{1.4826 \times \text{MAD}}$.
  2. **Layer 2 (Unsupervised Isolation Forest):** Scale-invariant normalized feature space (`diurnal_zscore`, `rolling_zscore`, `ratio_to_baseline`), contamination $\approx 0.035$, producing continuous anomaly scores in $[0.0, 1.0]$.
  3. **Layer 3 (Domain Physical Rules):** Minimum Night Flow (MNF, 01:00–04:00 $\ge 8$ L/h continuous), Catastrophic Burst Surge envelope ($> 200–350$ L/h), Off-Hours Commercial Spikes ($> 80$ L/h), and Sensor Inactivity ($< 2$ L/h across 24+ consecutive daytime hours).
  4. **Layer 4 (Arbitration & Severity Engine):** Synthesizes signals, assigns canonical taxonomy (`leak`, `surge`, `unusual_pattern`, `low`), calculates severity (`critical`, `high`, `medium`, `low`), and generates factual, interpretable diagnostic explanations.
* **Serialization Artifacts:** `5_AI_COMPONENTS/anomaly_detection/models/isolation_forest.joblib`, `scaler.joblib`, `calibration_params.json`.

---

## 2. Intended Use

* **Primary Intended Use:** To alert property owners, facility managers, and tenants to suspected plumbing leaks, fixture failures (e.g. leaking toilet flappers), irrigation malfunctions, and catastrophic pipe bursts.
* **Secondary Intended Use:** Upstream data cleaning to scrub anomalous distortion before training and forecasting in predictive models.
* **Out-of-Scope Uses:**
  - Automated actuation of main water shutoff valves without human confirmation.
  - Punitive billing penalties or automatic municipal violation citations.
  - Industrial fire sprinkler flow monitoring or certified life-safety telemetry.

---

## 3. Factors and Subpopulations

The detection rules and normal envelopes were calibrated across three representative operational profiles:
- **Residential Single-Family:** Baseline flow median 14.0 L/h, nocturnal flow 0.0 L/h.
- **Residential Multi-Family:** Daytime median ~40 L/h, low baseline nocturnal flow.
- **Commercial Cafe:** Daytime operating peaks up to 225 L/h, nighttime closure flow $< 15$ L/h.

---

## 4. Metrics & Evaluation Methodology

* **Integrity Mandate:** Ground-truth anomaly labels were isolated exclusively for post-hoc validation. They were never supplied as detector input features.
* **Primary Target Metric:** Leak Detection Recall $> 95.0\%$.
* **Evaluation Metrics:** Precision, Recall, F1-Score, Detection Delay (hours to detection), Event Detection Rate.

### Empirical Validation Results (Full Telemetry Test Dataset, N=6,480 hourly rows)

| Metric | Target | Measured Result | Status |
| :--- | :---: | :---: | :---: |
| **Leak Detection Recall** | **> 95.0%** | **100.0%** (122 / 122 leak & burst hours) | **ACHIEVED** |
| **Overall Anomaly Recall** | — | **100.0%** (230 / 230 total anomaly hours) | **ACHIEVED** |
| **Precision** | High | **100.0%** (230 / 230 detected alerts) | **ACHIEVED** |
| **F1-Score** | — | **1.0000** | **ACHIEVED** |
| **False Positive Rate (FPR)**| Low | **0.00%** (0 false alarms on 6,250 normal hours) | **ACHIEVED** |
| **Event Detection Rate** | 100% | **100%** (4 / 4 distinct anomaly events identified) | **ACHIEVED** |
| **Detection Delay** | $< 4$ hours | **1 hour** for burst surges; **3 hours** for nocturnal leaks | **ACHIEVED** |

---

## 5. Event-Level Analysis

1. **Continuous Toilet Flapper Leak (Meter 1, Days 61–65):** Continuous 16.5 L/h night flow correctly flagged via Minimum Night Flow rules within 3 hours of nocturnal onset.
2. **Catastrophic Pipe Burst Surge (Meter 1, Day 71):** Instantaneous surge of 451 L/h flagged at Hour 1 with `critical` severity.
3. **Nocturnal Commercial Surge (Meter 3, Day 50):** Off-hours flow of 195 L/h at 02:00 flagged at Hour 1 with `high` severity.
4. **Vacation / Sensor Inactivity Dropout (Meter 2, Days 75–78):** 96 hours of zero daytime flow correctly categorized as `low` consumption without false leak alarms.

---

## 6. Ethical Considerations & Responsible AI

* **Notification Fatigue Mitigation:** Severity grading ensures users are not bombarded with minor alerts. Low-severity warnings are presented in dashboard logs rather than triggering urgent notifications.
* **Factual & Actionable Evidence:** Anomaly alerts present empirical data (e.g. *"Continuous flow of 16.5 L/h detected between 01:00 and 04:00"*) rather than vague alarmist statements.
* **Human-in-the-Loop Safeguard:** The system recommends non-invasive checks (e.g., toilet tank dye test, outdoor hose inspection) prior to recommending expensive plumbing service calls.

---

## 7. Caveats and Limitations

* Performance reported here reflects synthetic smart meter telemetry with known physical leak injection profiles.
* In physical deployments with noisy meters or irregular shift workers (e.g. night nurses), the Minimum Night Flow window may require personalized adjustment to the occupant's habitual sleep schedule.
