# 📄 Datasheet for Dataset: Synthetic Smart Water Meter Telemetry

**Dataset Name:** Smart Water Usage Advisor Synthetic Telemetry (`water_usage_data.csv`)  
**Standard:** Gebru et al. (2018) *Datasheets for Datasets*  
**Project:** Smart Water Usage Advisor (UN SDG 6: Clean Water & Sanitation)  
**Date:** September 2026  
**License:** Open Educational / Academic Sustainability Research  
**Primary Files:**  
- `4_DEVELOPMENT/data/generated/water_usage_data.csv`  
- `4_DEVELOPMENT/data/generated/ground_truth_anomalies.csv`  
- `4_DEVELOPMENT/data/generated/database_seed.sql`  

---

## 1. Motivation

* **For what purpose was the dataset created?**  
  The dataset was created to provide a realistic, mathematically grounded, and reproducible hourly water consumption benchmark for training and evaluating predictive time-series forecasting models (Phase 3A) and unsupervised/hybrid leak detection systems (Phase 3B).
* **Why was synthetic data chosen over real-world utility data?**  
  Real-world municipal smart meter datasets rarely contain verified, timestamped ground-truth labels for subterranean pipe leaks, toilet flapper weeping, or burst pipes. Additionally, real-world utility telemetry often carries consumer privacy restrictions (revealing occupancy patterns and domestic habits). Synthetic modeling allows controlled, reproducible injection of physical anomaly signatures while strictly eliminating PII risks.
* **Who created the dataset and who funded it?**  
  Created by the Smart Water Usage Advisor project team for research in AI for environmental sustainability and water conservation.

---

## 2. Composition

* **What do the instances that comprise the dataset represent?**  
  Each instance represents an hourly smart water meter reading from one of three distinct consumer archetypes over a 90-day period (June 1, 2026 to August 29, 2026).
* **How many instances are there in total?**  
  - Total records: $6,480$ hourly readings ($2,160$ hours $\times$ 3 meters).
  - Ground-truth anomaly records: $230$ hours across 4 distinct physical anomaly events.
* **What data does each instance consist of?**  
  - `reading_id`: Unique surrogate integer primary key.
  - `meter_id`: Foreign key reference to the smart meter ($1, 2, 3$).
  - `timestamp`: ISO 8601 timestamp at 1-hour resolution.
  - `hourly_consumption_liters`: Liters consumed during the preceding 1-hour window.
  - `cumulative_reading_m3`: Strictly non-decreasing cumulative mechanical meter index in cubic meters.
  - `daily_consumption_liters`: Daily cumulative sum to date.
  - `monthly_consumption_liters`: Monthly cumulative sum to date.
  - `temperature_celsius`: Ambient daily mean temperature (°C).
  - `is_anomaly`: Binary ground-truth indicator (for post-hoc validation only).
  - `anomaly_type`: Ground-truth label (`leak`, `surge`, `unusual_pattern`, `low`, or `normal`).
* **Is any information missing?**  
  No missing values, nulls, or NaN entries exist in the canonical dataset. Sensor dropouts are explicitly simulated as extended zero-flow sequences.
* **Are there confidential or PII elements?**  
  No. All data is synthetically generated. No real consumer names, GPS coordinates, or real IP/MAC addresses are contained.

---

## 3. Collection / Synthesis Process

* **How was the data generated?**  
  Generated via `4_DEVELOPMENT/data/generate_telemetry.py` utilizing Python's `random` and `numpy.random` with a fixed pseudo-random seed (`seed=42`).
* **What mathematical models were used?**  
  - Diurnal base demand was modeled using dual-peaked Gaussian mixture distributions matching empirical municipal water demand profiles (morning residential peak 07:00–09:00, evening peak 18:00–21:00).
  - Commercial profiles modeled business operating hours (08:00–18:00 Mon–Fri).
  - Gaussian noise was added to simulate random appliance usage.
  - Cumulative readings were modeled with monotonic summation.
* **How were anomalies synthesized?**  
  Physical leak dynamics were injected deterministically:
  1. *Continuous Leak:* $+16.5$ L/h added continuously across 120 hours on Meter 1 (simulating a toilet flapper weeping).
  2. *Catastrophic Surge:* $+420$ L/h added during hours 14:00–15:00 on Meter 1 (simulating a burst service pipe).
  3. *Nocturnal Surge:* $+195$ L/h added during hours 00:00–03:00 on Meter 3 (simulating runaway cooling tower or irrigation).
  4. *Sensor Dropout:* Set to $0.0$ L/h across 96 daytime hours on Meter 2 (simulating apartment vacancy or shutoff valve closure).

---

## 4. Preprocessing, Cleaning, and Labeling

* **Was any data cleaning applied?**  
  Calculations were verified for zero discrepancy: hourly sums match daily totals ($0.00\%$ discrepancy), cumulative readings are strictly monotonic, and temperature correlates logically with seasonal summer trends.
* **How were labels created?**  
  Labels were assigned deterministically at injection time and stored separately in `ground_truth_anomalies.csv` to ensure models could not peek at evaluation labels during feature extraction.

---

## 5. Uses

* **Has the dataset been used for specific tasks?**  
  - Evaluating time-series forecasting algorithms (Random Forest, Gradient Boosting, Ridge, Seasonal Naive).
  - Training and benchmarking unsupervised Isolation Forest and statistical anomaly detection algorithms.
  - Powering the interactive dashboard and conversational chatbot in the Smart Water Usage Advisor.
* **Are there tasks for which the dataset should not be used?**  
  The dataset should not be used to train municipal water distribution hydraulics or pressure-drop simulations, as pipe diameter, network elevation, and hydraulic pressure heads are not modeled.

---

## 6. Distribution & Maintenance

* **How is the dataset distributed?**  
  Distributed directly within the project repository under `4_DEVELOPMENT/data/generated/`.
* **Who maintains the dataset?**  
  The Smart Water Usage Advisor open-source maintenance team.
* **Ethical Safeguards:**  
  Because the dataset is fully synthetic, there is zero risk of deanonymization or domestic surveillance.
