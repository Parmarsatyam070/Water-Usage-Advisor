# 👤 Persona 2: Institutional Facility Manager
**Identifier:** Persona_2_Facility_Manager  
**User Archetype:** Commercial & Institutional Operations Lead  
**Target Group:** University Campuses, Educational Facilities & Office Complexes

---

## 1. Profile Overview
- **Name Archetype:** Marcus Vance
- **Role:** Director of Facilities & Physical Plant Operations
- **Facility Context:** Mid-size university campus comprising 8 academic buildings, 3 dormitory towers, central dining facilities, and athletic fields with extensive irrigation networks.
- **Technical Comfort:** Advanced (Experienced with Building Management Systems (BMS), SCADA, energy dashboards, and maintenance ticketing software).

---

## 2. Core Goals
1. **Multi-Meter Infrastructure Oversight:** Monitor consumption across 45 separate zone meters in a single consolidated interface.
2. **Prevent Catastrophic Water Incidents:** Detect major pipe bursts or unmonitored irrigation head shears within 30 minutes to prevent structural flood damage.
3. **Institutional ESG & Budget Reporting:** Automate monthly water consumption and carbon intensity reporting for campus sustainability boards.

---

## 3. Key Pain Points
- **Siloed Metering Data:** Meters from different building eras output into disparate spreadsheets, requiring days of manual aggregation.
- **Delayed Leak Identification:** A broken irrigation pipe or running commercial urinal on campus can waste 50,000 liters before physical maintenance discovers it.
- **Lack of Predictive Load Management:** No accurate forecasting tool to plan water buffering for cooling towers during forecasted heat waves.

---

## 4. Water-Management Needs
- High-level multi-zone dashboard with hierarchical drill-down from campus level to individual meter level.
- Multi-tier alert thresholds (Notice, Warning, Critical) with automatic anomaly tagging.
- Predictive demand forecasting for 7-to-30 day horizons based on student occupancy and weather.

---

## 5. Expected Application Features
1. **Multi-Meter Facility Dashboard:** Aggregated campus view with automated sorting by highest deviation from baseline.
2. **Comparative Zone Analytics:** Benchmarking water use intensity (liters per student / square meter) across dormitory buildings.
3. **Compliance & Export Tools:** Automated one-click PDF/CSV generation of SDG 6 metrics and trend audits for regulatory reporting.

---

## 6. Key User Journey
```mermaid
sequenceDiagram
    autonumber
    actor Marcus as Marcus (Facility Director)
    participant App as Smart Water Advisor
    participant AI as Predictive ML & Alert Engine

    App->>Marcus: Dispatches "Critical Anomaly: Science Hall Meter #04"
    Marcus->>App: Logs into Facility Dashboard; filters to Science Hall
    App-->>Marcus: Shows 300% spike above normal Friday evening baseline
    Marcus->>Marcus: Dispatches plumbing team to inspect Science Hall basement
    Note over Marcus: Team locates cracked cooling loop valve; shuts off segment
    Marcus->>App: Submits feedback: "Leak verified & resolved (valved isolated)"
    App-->>Marcus: Updates campus savings tracker: "Saved est. 45,000 L of potable water"
```

---

## 7. Success Criteria
- Reduction of campus-wide unaccounted water loss by > 25%.
- Mean Time to Detection (MTTD) of anomalous flow reduced from 72 hours to under 4 hours.
- Automated ESG reporting reducing manual administrative reporting time by 80%.
