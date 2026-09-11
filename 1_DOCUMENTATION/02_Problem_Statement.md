# 🌊 Problem Statement & SDG 6 Alignment: Smart Water Usage Advisor
**Document ID:** 02_Problem_Statement  
**Focus:** Sustainable Resource Management & Clean Water  
**SDG Reference:** UN Sustainable Development Goal 6 (Clean Water & Sanitation — Target 6.4)

---

## 1. The Core Problem
Freshwater is an increasingly scarce natural resource under severe pressure from population growth, climate variability, and urbanization. Despite modern water infrastructure, substantial volumes of clean municipal water are squandered every day due to undetected plumbing leaks, unoptimized irrigation, and inefficient consumer usage habits. 

Most water consumers—whether private households, school campus administrators, or municipal district planners—experience water usage purely in retrospect: through a monthly paper utility bill. This lack of granular visibility means that leaks can run unnoticed for weeks or months, costing billions of liters and imposing severe financial burdens.

---

## 2. Root Causes of Inefficient Water Consumption
1. **Information Asymmetry & Lag:** Traditional mechanical meters are read once per billing cycle. Users receive feedback 30 to 45 days after consumption occurs.
2. **Hidden / Silent Leaks:** Toilet flapper leaks, irrigation solenoid failures, and underground service pipe pinholes frequently consume 100 to 1,000 liters per day without showing visible surface pooling.
3. **Generic & Impractical Advice:** Traditional utility conservation campaigns offer generic slogans (e.g., "Take shorter showers") rather than actionable, context-aware suggestions tailored to household occupancy, property size, or fixture age.
4. **Cognitive Disconnect with Volume:** Consumers struggle to correlate abstract volumetric units ($m^3$, gallons, liters) with daily activities (dishwashing, laundry, irrigation, showering).

---

## 3. Current Challenges
- **Absence of Intelligent Analytics:** Even where Advanced Metering Infrastructure (AMI) or digital meters are deployed, raw volumetric time-series data is dumped into utility databases without automated consumer-facing anomaly detection.
- **Data Overload without Interpretation:** Simple charts of raw data fail to engage users unless accompanied by clear baselines, peer comparisons, and predictive forecasts.
- **Siloed Stakeholder Needs:** Facility managers require multi-building comparative analytics, homeowners demand simple cost and alert notifications, and municipalities require aggregate demand elasticity metrics.

---

## 4. Target Users
- **Tier 1 — Residential Households:** Homeowners, tenants, and families seeking to reduce monthly utility expenditures, catch plumbing leaks early, and adopt sustainable lifestyle habits.
- **Tier 2 — Commercial & Institutional Facility Managers:** Operators of schools, universities, hotels, and office parks responsible for large, multi-zoned plumbing systems with complex demand schedules.
- **Tier 3 — Municipal Water Authorities & Utilities:** District managers who require aggregate consumption forecasting to balance reservoir drawdowns and evaluate community-wide conservation programs.

---

## 5. The Opportunity: AI-Powered Intelligence
Advancements in machine learning, statistical anomaly detection, and Large Language Models (LLMs) allow us to build a digital advisor that:
- Decomposes consumption patterns into predictable diurnal baselines.
- Flags deviations (abnormal baseline shifts, persistent night-flow) instantaneously.
- Generates precise forecasts of future consumption based on historical patterns and environmental variables (temperature, seasonality).
- Translates numerical data into natural language conservation strategies through an interactive conversational assistant.

---

## 6. Alignment with UN Sustainable Development Goal 6
This project directly aligns with **UN SDG 6: Ensure availability and sustainable management of water and sanitation for all**:
- **Target 6.4:** *"By 2030, substantially increase water-use efficiency across all sectors and ensure sustainable withdrawals and supply of freshwater to address water scarcity."*
- **Target 6.b:** *"Support and strengthen the participation of local communities in improving water and sanitation management."*

The Smart Water Usage Advisor advances Target 6.4 by empowering the end-user with actionable intelligence, targeting an aggregate conservation impact of **20% to 30%**.

---

## 7. Project Boundaries & Operational Constraints (V1 Scope)
To ensure high engineering rigor and timely delivery, explicit boundaries are set for Version 1:

| Dimension | In Scope (MVP) | Out of Scope (MVP) |
| :--- | :--- | :--- |
| **Data Ingestion** | Simulated / synthetic smart-meter telemetry with diurnal & seasonal variance. | Physical hardware sensor installation / LoRaWAN deployment. |
| **Billing & Payments** | Tariff simulation and estimated cost savings. | Direct integration with municipal payment gateways. |
| **Platforms** | Responsive Web Application (Desktop, Tablet, Mobile browser). | Native iOS / Android compilation. |
| **Language Support** | Standard English conversational chatbot and interface. | Multi-language localization / translation. |
| **Plumbing Controls** | Automated anomaly alerts and guidance to shut off valves. | Automated motorized shut-off solenoid actuation. |

---

## 8. Measurable Objectives
1. **Target Water Savings:** Enable users to achieve a documented **20–30% reduction** in wasteful consumption.
2. **Predictive Accuracy:** Deliver consumption forecasts with **MAPE < 15%** (Accuracy > 85%).
3. **Leak Detection Rate:** Achieve **> 95% sensitivity** on simulated continuous leak events.
4. **Chatbot Responsiveness:** Maintain average query latency **< 2.0 seconds** for all conversational interactions.
5. **Usability & Adoption:** Attain user satisfaction score of **>= 4.0 / 5.0** and task completion rate **> 80%**.
