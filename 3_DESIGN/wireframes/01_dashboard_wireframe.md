# 🖥️ Wireframe 01: Water Usage Dashboard
**Document ID:** 01_dashboard_wireframe  
**Target View:** Main Web Dashboard (Desktop & Tablet Layout)  
**Status:** Phase 1 Design Specification (Non-production wireframe)

---

## 1. ASCII Layout Wireframe

```
+---------------------------------------------------------------------------------------------------------+
| [LOGO] Smart Water Usage Advisor       [Alerts (1)] [SDG 6 Progress: 24%]         User: Sarah J. [Logout] |
+---------------------------------------------------------------------------------------------------------+
|  NAV: [ Dashboard ]   [ Analytics & Forecast ]   [ AI Chatbot ]   [ Recommendations ]   [ Settings ]    |
+---------------------------------------------------------------------------------------------------------+
|                                                                                                         |
|  [CRITICAL ALERT BANNER]                                                                               |
|  ⚠️ Persistent Night Flow Detected: 14 L/hr between 02:00-05:00 AM. [Diagnose with AI] [Dismiss]        |
|                                                                                                         |
+---------------------------------------------------------------------------------------------------------+
|  KPI SUMMARY CARDS                                                                                      |
|  +---------------------+ +---------------------+ +---------------------+ +-------------------------+  |
|  | TODAY'S USAGE       | | 7-DAY FORECAST      | | MONTHLY SAVINGS     | | CONSERVATION GOAL       |  |
|  | 385 Liters          | | 410 L/day (Avg)     | | $28.40 Saved        | | 22% / 25% Target        |  |
|  | ▼ 12% vs yesterday  | | ▲ 8% weekend surge  | | 3,420 L preserved   | | [=======>---] On Track  |  |
|  +---------------------+ +---------------------+ +---------------------+ +-------------------------+  |
+---------------------------------------------------------------------------------------------------------+
|                                                   |                                                     |
|  MAIN CHART: CONSUMPTION TRENDS & FORECAST        |  CATEGORY BREAKDOWN (DISAGGREGATED USAGE)           |
|  [Daily View | Weekly View | Monthly View]        |                                                     |
|  Liters                                           |  - Showers & Bath:      145 L  (38%) [========]    |
|   600 |            __- Actual Usage               |  - Toilets:              92 L  (24%) [=====]       |
|   400 |      /\   /  \-- Forecasted Demand        |  - Outdoor / Lawn:       68 L  (18%) [====]        |
|   200 |  /\ /  \_/    \                           |  - Kitchen & Cooking:    50 L  (13%) [===]         |
|     0 +-----------------------                    |  - Laundry:              30 L   (7%) [==]          |
|       Mon Tue Wed Thu Fri Sat Sun                 |                                                     |
|                                                   |  SIMILAR HOUSEHOLD BENCHMARK                        |
|                                                   |  You: 385 L/day | Benchmark: 440 L/day (Good!)      |
+---------------------------------------------------+-----------------------------------------------------+
|                                                                                                         |
|  ACTIVE CONSERVATION RECOMMENDATIONS                                                                    |
|  +---------------------------------------------------------------------------------------------------+  |
|  | [HIGH PRIORITY] Check Bathroom Flapper Valve | Est. Savings: 280 L/day ($35/mo) | [Take Action]   |  |
|  | [MEDIUM] Shift Lawn Irrigation to 06:00 AM   | Est. Savings: 120 L/week ($8/mo)  | [Dismiss]       |  |
|  +---------------------------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------------------------+
```

---

## 2. Component Specifications

### 2.1 Alert Notification Banner
- **Trigger:** Active unacknowledged records from the `alerts` table.
- **Visuals:** High-contrast amber/red alert card displaying continuous night flow or sudden volumetric spikes with a direct one-click CTA to open the AI Chatbot with diagnostic pre-prompts.

### 2.2 KPI Summary Cards
1. **Today's Usage:** Real-time day-to-date accumulation in liters with comparative percentage delta vs. same day last week.
2. **7-Day Forecast:** Machine learning prediction of next 7 days' average demand with heat/weather surge indicators.
3. **Monthly Savings:** Accumulated dollar and volume savings derived from user's active baseline.
4. **Conservation Goal:** Progress bar tracking adherence to the user's committed reduction target (e.g., -25%).

### 2.3 Consumption Charting Area
- Dual-series time-series line chart comparing observed hourly/daily consumption against ML projected demand with 95% confidence intervals.

### 2.4 Category Breakdown & Peer Benchmarking
- Disaggregated end-use breakdown across domestic fixtures (showers, toilets, irrigation, laundry).
- Demographic normalization comparing household liters/capita/day against regional baseline.
