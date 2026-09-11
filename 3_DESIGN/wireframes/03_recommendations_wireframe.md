# 💡 Wireframe 03: Personalized Recommendations Engine
**Document ID:** 03_recommendations_wireframe  
**Target View:** Dedicated Recommendations & Conservation Action Center  
**Status:** Phase 1 Design Specification (Non-production wireframe)

---

## 1. ASCII Layout Wireframe

```
+---------------------------------------------------------------------------------------------------------+
| [LOGO] Smart Water Usage Advisor > Actionable Recommendations             Filter: [ All | Active | Done ]|
+---------------------------------------------------------------------------------------------------------+
|                                                                                                         |
|  PROJECTED IMPACT SUMMARY                                                                               |
|  Total Potential Water Savings: 460 Liters / day (-28% reduction) | Est. Annual Financial Savings: $410 |
|                                                                                                         |
+---------------------------------------------------------------------------------------------------------+
|  CARD 1: [ URGENT PRIORITY ]                                                                            |
|  +---------------------------------------------------------------------------------------------------+  |
|  | Title: Inspect & Replace Worn Bathroom Toilet Flapper                                              |  |
|  | Explanation: Anomaly detection flagged continuous 14 L/hr nighttime flow. A degraded flapper is  |  |
|  | the most common cause. Replacing it takes 10 minutes and costs ~$6 at any hardware store.        |  |
|  |                                                                                                   |  |
|  | Metrics:                                                                                          |  |
|  | - Est. Savings: 336 Liters / day (10,080 L / month)                                               |  |
|  | - Financial Savings: $35.00 / month                                                               |  |
|  | - Status: ACTIVE                                                                                  |  |
|  |                                                                                                   |  |
|  | [ Mark as Completed ✓ ]    [ How-To Video / Guide 📖 ]    [ Dismiss ✕ ]                           |  |
|  +---------------------------------------------------------------------------------------------------+  |
|                                                                                                         |
|  CARD 2: [ HIGH PRIORITY ]                                                                              |
|  +---------------------------------------------------------------------------------------------------+  |
|  | Title: Optimize Lawn Irrigation Schedule to Early Morning (05:30 AM)                              |  |
|  | Explanation: Outdoor watering is currently logged at 02:00 PM. High solar evaporation rates      |  |
|  | lose up to 35% of irrigated water before it reaches root systems.                                 |  |
|  |                                                                                                   |  |
|  | Metrics:                                                                                          |  |
|  | - Est. Savings: 95 Liters / session (760 L / month)                                               |  |
|  | - Financial Savings: $9.50 / month                                                                |  |
|  | - Status: IN_PROGRESS                                                                             |  |
|  |                                                                                                   |  |
|  | [ Mark as Completed ✓ ]    [ Adjust Timer Guide 📖 ]     [ Dismiss ✕ ]                           |  |
|  +---------------------------------------------------------------------------------------------------+  |
|                                                                                                         |
|  CARD 3: [ MEDIUM PRIORITY ]                                                                            |
|  +---------------------------------------------------------------------------------------------------+  |
|  | Title: Install High-Efficiency Aerators on Bathroom & Kitchen Faucets                             |  |
|  | Explanation: Standard faucets run at 8.3 L/min. Installing 5.7 L/min aerators reduces domestic   |  |
|  | sink consumption without noticeable water pressure loss.                                          |  |
|  |                                                                                                   |  |
|  | Metrics:                                                                                          |  |
|  | - Est. Savings: 30 Liters / day (900 L / month)                                                   |  |
|  | - Financial Savings: $4.00 / month                                                                |  |
|  | - Status: ACTIVE                                                                                  |  |
|  |                                                                                                   |  |
|  | [ Mark as Completed ✓ ]    [ Recommended Models 📖 ]     [ Dismiss ✕ ]                           |  |
|  +---------------------------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------------------------+
```

---

## 2. Component Specifications

### 2.1 Impact Summary Header
- Computes aggregate volumetric and cost savings across all currently active recommendations.

### 2.2 Recommendation Cards
- **Title:** Actionable, positive verb-oriented heading.
- **Explanation:** Grounded explanation explaining why the recommendation was generated.
- **Estimated Savings:** Explicitly reports liters preserved per day/month and dollar utility impact.
- **Priority Badge:** Visual coding (`URGENT`, `HIGH`, `MEDIUM`, `LOW`).
- **Action / Status Workflow:** Allows users to mark items `IN_PROGRESS`, `COMPLETED`, or `DISMISSED`, which triggers real-time updates in the `recommendations` table.
