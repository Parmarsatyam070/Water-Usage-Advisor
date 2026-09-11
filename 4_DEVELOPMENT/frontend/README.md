# Smart Water Usage Advisor — Phase 4 Frontend Architecture

**UN Sustainable Development Goal 6**: Clean Water & Sanitation  
**Phase**: 4 — Dashboard & Web User Interface  

---

## 1. Overview

The Smart Water Usage Advisor web interface is a high-performance, accessible, zero-build-overhead Single-Page Application (SPA) built purely with **Semantic HTML5, Vanilla CSS3, and Modular ES6 JavaScript**.

It operates completely offline with zero external runtime network dependencies:
- **Local Vendored Charting**: Uses the pinned **Chart.js v4.4.1 (UMD standalone bundle)** located at `js/vendor/chart.umd.js`.
- **Zero Build Toolchains**: No npm, Node.js, Webpack, Vite, or external bundlers are required.
- **Python Standard-Library Server**: Served locally via Python's built-in `http.server` via `python run_dashboard.py`.

---

## 2. Directory Structure

```
4_DEVELOPMENT/frontend/
├── index.html                    # Semantic single-page application dashboard
├── README.md                     # Frontend documentation (this file)
├── css/
│   └── styles.css                # Design system: CSS custom properties, dark/light theme, grid
└── js/
    ├── app.js                    # Main controller, theme management, and persona coordinator
    ├── api_client.js             # HTTP client communicating with /api/dashboard/* endpoints
    ├── vendor/
    │   └── chart.umd.js          # Pinned local Chart.js v4.4.1 bundle (offline, no CDN)
    └── components/
        ├── kpi_cards.js          # Section A: Today's usage, 7-day forecast avg, savings, goal
        ├── charts.js             # Section B & C: Diurnal curve, 30d daily bars, 7d prediction
        ├── alerts.js             # Section D: Phase 3B anomaly & leak incident log & alert banner
        ├── recommendations.js    # Section E: Phase 3C personalized conservation action cards
        ├── goals.js              # Section G: Conservation goal & SDG 6 progress bar
        └── chatbot.js            # Section F: Slide-out AI advisor chat drawer & multi-turn UI
```

---

## 3. Key Features

### 3.1. Overview KPI Cards (Section A)
- Real-time today's consumption in liters with week-over-week percentage delta.
- 7-day forecast average derived from the Phase 3A Machine Learning model.
- Monthly financial and volumetric water savings ($ and Liters preserved).
- Conservation target completion gauge.

### 3.2. Dual-Mode Consumption Analytics (Section B)
- **24-Hour Diurnal Profile**: Dual-line chart comparing recent 24-hour hourly flow against the learned historical median baseline.
- **30-Day History**: Daily volumetric bar chart paired with a 7-day moving average trendline.
- Callouts for morning peak hours (08:00), evening peak hours (19:00), and regional municipal benchmarks.

### 3.3. 7-Day Forward Demand Forecast (Section C)
- Powered by the Phase 3A Random Forest forecasting engine.
- Distinct dashed styling with 95% confidence interval boundaries.
- Identifies expected high-demand peak days.
- Transparent Responsible AI model attribution card.

### 3.4. Anomaly & Leak Incident Center (Section D)
- Real-time alert banner for continuous night flow leaks or burst surges.
- Filterable incident cards with severity badges (`critical`, `high`, `medium`, `low`), flow rate, and diagnostic root-cause explanation.
- One-click **"Diagnose with AI"** shortcut to open the chatbot.

### 3.5. Personalized Conservation Action Center (Section E)
- Ranked recommendations synthesized by the Phase 3C expert engine.
- Quantified daily water savings (L/day) and monthly utility bill reductions.
- Difficulty ratings (`Easy`, `Moderate`, `Hard`) and urgency badges.

### 3.6. Slide-Out AI Conservation Chatbot Drawer (Section F)
- Accessible from any section via the header button or diagnostic shortcuts.
- Context pill showing active customer meter profile.
- Multi-turn conversation bubble stream with timestamps.
- Authoritative source attribution chips (`EPA WaterSense`, `AWWA`).
- Mandatory licensed plumber safety advisory for pipe bursts.

---

## 4. Local Execution & Evaluation

To launch the dashboard locally using Python's standard-library `http.server`:

```bash
# From the repository root
python run_dashboard.py --port 8080
```

Open your browser to:
```
http://127.0.0.1:8080/
```
