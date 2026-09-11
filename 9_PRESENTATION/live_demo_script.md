# Smart Water Usage Advisor — Live Interactive Demonstration Script

**Project:** Smart Water Usage Advisor (UN Sustainable Development Goal 6: Clean Water & Sanitation)  
**Lifecycle Stage:** Phase 6 — Deployment, Documentation & Final Presentation  
**Target Audience:** Project Review Committee, Academic Evaluators, and Industry Assessors  
**Demonstration Duration:** 10–12 Minutes  
**Document Location:** `9_PRESENTATION/live_demo_script.md`  

---

## Demonstration Setup & Prerequisites

Before starting the presentation, ensure the environment is initialized:
- Terminal window open at repository root: `AI-Sustainability-internship/`
- Browser open at `http://localhost:5000/` (or deployed cloud URL)
- Docker Desktop running (for containerized demo) or Python virtual environment active

---

## 11-Step Interactive Demonstration Sequence

### Step 1: Multi-Container Stack Launch & Health Verification
- **Action:** Launch the application stack via Docker Compose:
  ```bash
  docker compose -f 8_DEPLOYMENT/docker-compose.yml up -d
  ```
- **Verification:** Execute healthcheck probe:
  ```bash
  curl -s http://localhost:5000/api/health
  ```
- **Spoken Narration:**
  > *"We start by bringing up our multi-container deployment. Notice that the web container waits for PostgreSQL to become fully healthy before serving traffic. The health endpoint confirms all services—database, forecaster, anomaly detector, and chatbot—are initialized and operational."*

---

### Step 2: Responsive Dashboard Landing Page
- **Action:** Open `http://localhost:5000/` in browser.
- **Visual Highlight:** Sustainable color palette (deep teal, emerald green, slate), clean typography, and instant rendering.
- **Technical Highlight:** Locally vendored Chart.js bundle (`4_DEVELOPMENT/frontend/js/vendor/chart.umd.js`) with zero runtime external CDN dependency.
- **Spoken Narration:**
  > *"Here is the Smart Water Usage Advisor web interface. It is built entirely in vanilla HTML5, CSS3, and ES6 JavaScript. Notice how quickly it loads—there are no heavy frontend frameworks or external CDN dependencies. Even the charting engine is vendored locally within the repository."*

---

### Step 3: Consumer Persona Authentication & Session Establishment
- **Action:** Select Sarah Jenkins from the persona switcher or log in:
  - **Email:** `sarah.jenkins@example.com`
  - **Password:** `ResidentPass2026!`
- **Technical Highlight:** Browser receives RFC 7519 HMAC-SHA256 JWT access token stored in memory.
- **Spoken Narration:**
  > *"We log in as Sarah Jenkins, representing a Single-Family household of four in Bengaluru. The backend verifies credentials using salted bcrypt hashing and issues a standard JSON Web Token containing her authorized meter IDs."*

---

### Step 4: 24-Hour Telemetry & SDG 6 Efficiency Evaluation
- **Visual Highlight:** Section A Summary Cards:
  - Today's Usage: ~342 Liters/day
  - Weekly Delta: -6.2% reduction vs. same day last week
  - SDG 6 Efficiency Rating: "Good" (within municipal per-capita benchmarks of 135 L/person/day)
  - Conservation Goal Progress: 82.4% achieved
- **Spoken Narration:**
  > *"The dashboard immediately synthesizes Sarah's key metrics. She is consuming approximately 342 liters today—comfortably aligned with UN SDG 6 residential benchmarks. Her conservation goal progress shows 82% attainment toward her monthly reduction target."*

---

### Step 5: Diurnal Curve & Historical Analytics
- **Visual Highlight:** Section B Diurnal Consumption Chart:
  - Bimodal consumption peaks at 07:00 (morning showers, breakfast) and 19:00 (evening cooking, dishwashing).
  - 30-day historical trend graph showing daily volumes.
- **Spoken Narration:**
  > *"In Section B, we observe the characteristic human diurnal consumption pattern. We see two distinct daily peaks: morning routines around 7 AM and evening activities around 7 PM, modeled with hourly precision from smart meter telemetry."*

---

### Step 6: Phase 3A Predictive 7-Day Consumption Forecast
- **Visual Highlight:** Section C 7-Day Forward Forecast Chart:
  - Dashed projection line showing expected daily consumption over the next week.
  - Shaded uncertainty envelope representing upper and lower validation residual quantile bounds.
- **Technical Highlight:** Outperforms Seasonal Naive 7-day benchmark with a validated **9.85% MAPE**.
- **Spoken Narration:**
  > *"Section C presents our Phase 3A machine learning model. Our Global Random Forest Regressor forecasts the next 7 days of consumption with a validated 9.85% MAPE. Rather than displaying theoretical confidence intervals, our uncertainty bands are empirically derived from validation residual quantiles."*

---

### Step 7: Phase 3B Anomaly & Continuous Leak Alert
- **Visual Highlight:** Urgent Amber/Red Alert Banner:
  - Type: Continuous Baseflow Leak (Nighttime Window)
  - Severity: **High**
  - Estimated Loss: 18.5 Liters/hour (444 Liters/day)
  - Cause: Toilet flapper valve failure or concealed service pipe fissure.
- **Spoken Narration:**
  > *"Notice the alert banner at the top of the screen. Our 4-layer hybrid detection engine identified continuous water flow between 2 AM and 5 AM—a physical window where baseline consumption should drop to zero. The system flags this as a high-severity leak wasting over 440 liters daily."*

---

### Step 8: Personalized Conservation Action Center
- **Visual Highlight:** Ranked action cards with quantified volumetric (L/day) and financial ($/mo) savings:
  1. Inspect Toilet Flapper Valve: Save ~200 L/day (₹390/mo)
  2. Install Low-Flow Aerators: Save ~45 L/day (₹88/mo)
  3. Optimize Garden Drip Irrigation: Save ~80 L/day (₹156/mo)
- **Spoken Narration:**
  > *"Rather than presenting generic conservation slogans, the Action Center personalizes recommendations based on Sarah's property profile—she has a garden, four residents, and an active flapper leak. Each card quantifies the potential volumetric and financial savings."*

---

### Step 9: Phase 3C Conversational RAG Chatbot
- **Action:** Open the chatbot drawer and submit query:
  > *"I have a leak in my toilet. How do I fix it and what should I check?"*
- **Visual Highlight:**
  - Fast, grounded response detailing flapper valve inspection.
  - Citation tags: `KB-04: Toilet Flapper Inspection & Replacement`.
  - Safety notice: *"For complex or concealed plumbing, consult a licensed plumbing professional."*
- **Spoken Narration:**
  > *"We now open the AI Conservation Chatbot. When Sarah inquires about the leak, the system retrieves verified municipal knowledge from KB-04. Notice the safety guardrail: the chatbot provides DIY guidance for surface flappers but explicitly includes a certified plumber disclaimer for pressurized systems."*

---

### Step 10: Fail-Closed Security & BOLA/IDOR Protection
- **Action:** Open browser developer tools / console and attempt an unauthorized cross-tenant API query:
  ```javascript
  fetch("/api/v1/forecast/meters/2", {
    headers: { "Authorization": "Bearer " + localStorage.getItem("token") }
  }).then(r => console.log("Status:", r.status));
  ```
- **Visual Highlight:** Network tab shows `HTTP 403 Forbidden` with response envelope:
  `{"error": "Forbidden", "message": "Access to meter 2 is not authorized for your account"}`
- **Spoken Narration:**
  > *"Security is critical in utility infrastructure. Sarah owns Meter 1. If an attacker tampers with the API request to inspect Meter 2 belonging to Marcus Vance, our `@meter_access_required` decorator intercepts the request and terminates it with HTTP 403 Forbidden."*

---

### Step 11: Deployment Smoke Verification & Quality Audit
- **Action:** Run the automated standard-library smoke verification probe in the terminal:
  ```bash
  python 8_DEPLOYMENT/verify_deployment.py --url http://localhost:5000
  ```
- **Visual Highlight:** All 8 automated probes pass cleanly (with transparent reporting of degraded database dependency in the local standalone test environment).
- **Spoken Narration:**
  > *"Finally, we run our deployment verification script. In seconds, it probes health, static routing, offline Chart.js, JWT authentication, BOLA defense, forecasting, and chatbot grounding across 8 automated checks. Notice that in this local standalone test without an external PostgreSQL instance running, the health probe transparently documents the database dependency as degraded while the graceful fallback cache ensures full service continuity. Combined with our 137 passing automated regression tests, the Smart Water Usage Advisor's local deployment is verified and ready for evaluation."*
