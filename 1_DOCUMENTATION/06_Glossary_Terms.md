# 📖 Glossary of Terms & Definitions
**Document ID:** 06_Glossary_Terms  
**Domain:** AI, Sustainability, Water Utilities & Software Architecture

---

| Term / Acronym | Definition & Context in Smart Water Advisor |
| :--- | :--- |
| **SDG (Sustainable Development Goals)** | A collection of 17 interlinked global objectives set by the United Nations. This project targets **SDG 6 (Clean Water & Sanitation)**, specifically Target 6.4 (water-use efficiency). |
| **AI (Artificial Intelligence)** | Systems capable of performing tasks that typically require human cognition, including conversational problem-solving, pattern recognition, and decision support. |
| **ML (Machine Learning)** | Computational algorithms that parse data, learn underlying distributions, and make inferences or forecasts without being explicitly hard-coded. |
| **MAPE (Mean Absolute Percentage Error)** | A key statistical metric measuring the accuracy of consumption predictions. Calculated as $\text{MAPE} = \frac{100\%}{n}\sum \left|\frac{\text{Actual} - \text{Forecast}}{\text{Actual}}\right|$. Target: $<15\%$. |
| **RAG (Retrieval-Augmented Generation)** | An AI architecture where an LLM is provided with factual, retrieved reference context (e.g., user profiles, conservation guides) to generate accurate, non-hallucinatory answers. |
| **MVP (Minimum Viable Product)** | The version of the product with the essential feature set required to validate user value and meet initial scientific goals (Phase 1–6 scope). |
| **AMI (Advanced Metering Infrastructure)** | Digital smart metering networks that measure, collect, and transmit high-frequency water consumption data (hourly or sub-hourly) back to databases. |
| **Anomaly** | An observation or sequence of consumption readings that deviates significantly from expected baseline behavior (e.g., sudden volumetric spikes or continuous non-zero nighttime flow). |
| **Minimum Night Flow (MNF)** | The lowest observed water flow rate between 01:00 AM and 05:00 AM, typically indicating baseline continuous plumbing leaks if flow does not drop to zero. |
| **Diurnal Pattern** | The recurring 24-hour daily cycle of water usage, typically characterized by a morning peak (07:00–09:00), afternoon lull, evening peak (18:00–21:00), and nocturnal drop. |
| **Personalization** | The capability to tailor conservation advice, goal metrics, and alerts to specific household characteristics (occupancy, garden size, fixture age) rather than generic utility averages. |
| **Predictive Analytics** | Time-series forecasting techniques that project expected future consumption over 7-to-30 day horizons based on historical lags, day of week, and temperature. |
| **Isolation Forest** | An unsupervised machine learning algorithm used for anomaly detection that isolates anomalies by randomly selecting a feature and splitting values. |
| **RBAC (Role-Based Access Control)** | Security mechanism restricting application permissions based on user roles (`household`, `facility_manager`, `municipality`). |
| **Z-Score** | A statistical measurement that describes a value's relationship to the mean of a group of values, measured in terms of standard deviations ($\sigma$). Used for spike detection. |
