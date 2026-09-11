# Smart Water Usage Advisor — REST API Reference

**Project:** Smart Water Usage Advisor (UN Sustainable Development Goal 6: Clean Water & Sanitation)  
**Document Version:** 1.0 (OpenAPI & Endpoint Specification)  
**Base URL (Local):** `http://localhost:5000`  
**Base URL (Production):** `https://<deployed-service-domain>`  

---

## 1. Authentication & Security Architecture

The API implements a defense-in-depth security model:
- **Authentication Scheme:** RFC 7519 JSON Web Token (JWT) signed with HMAC-SHA256 (`HS256`).
- **Authorization Header:** `Authorization: Bearer <access_token>`
- **Token Lifespan:** 24 hours (configurable via `JWT_EXPIRATION_HOURS`).
- **Object-Level Authorization (BOLA/IDOR Defense):** Endpoints accessing meter-specific telemetry or forecasts enforce `@meter_access_required`, guaranteeing users can only access meters associated with their authenticated account ID (`sub`).
- **Sanitized Error Responses:** All error responses return standard JSON envelopes (`error`, `message`, `status_code`) without internal stack traces.

```json
{
  "error": "Forbidden",
  "message": "Access to meter 2 is not authorized for your account",
  "status_code": 403
}
```

---

## 2. API Endpoints Overview

| Blueprint | Route Path | Method | Auth Required | Description |
| :--- | :--- | :---: | :---: | :--- |
| **Health** | `/api/health` | GET | No | System operational status and component readiness |
| **Auth** | `/api/auth/login` | POST | No | Authenticate user credentials and issue JWT token |
| **Auth** | `/api/auth/me` | GET | Yes | Retrieve authenticated user profile and meters |
| **Auth** | `/api/auth/demo-token` | GET | Dev/Test | Issue instant test token (disabled in production) |
| **Dashboard** | `/api/dashboard/summary` | GET | Yes | Aggregate 24h KPIs, SDG rating, and meter status |
| **Dashboard** | `/api/dashboard/consumption` | GET | Yes | Diurnal curve and historical daily volume series |
| **Dashboard** | `/api/dashboard/forecast` | GET | Yes | 7-day predicted consumption with uncertainty bounds |
| **Dashboard** | `/api/dashboard/anomalies` | GET | Yes | Active leak and anomaly alerts with severity scoring |
| **Dashboard** | `/api/dashboard/recommendations` | GET | Yes | Ranked conservation actions with estimated savings |
| **Dashboard** | `/api/dashboard/goals` | GET | Yes | Active water conservation targets and progress |
| **Telemetry** | `/api/v1/telemetry/meters/<id>/readings` | GET | Yes | Hourly telemetry reading series with pagination |
| **Telemetry** | `/api/v1/telemetry/meters/<id>/summary` | GET | Yes | Statistical summary across time windows |
| **Forecast** | `/api/v1/forecast/meters/<id>` | GET | Yes | 7-day multi-step forecast array and model metadata |
| **Anomalies** | `/api/v1/anomalies/meters/<id>` | GET | Yes | Incident list with severity arbitration and notices |
| **Anomalies** | `/api/v1/anomalies/meters/<id>/scores` | GET | Yes | Hourly anomaly scores and threshold baselines |
| **Chat** | `/api/v1/chat` | POST | Yes | Grounded conversational advisor query with citations |

---

## 3. Blueprint Details & Specifications

### 3.1. System Health Blueprint (`/api/health`)

#### `GET /api/health`
Sanitized operational probe safe for public uptime monitors and container orchestration.

- **Request Headers:** None required
- **Response `200 OK`:**
```json
{
  "status": "healthy",
  "environment": "production",
  "services": {
    "database": "connected",
    "forecasting_model": "loaded",
    "anomaly_detector": "loaded",
    "chatbot": "ready"
  },
  "database": "connected",
  "forecasting_model": "loaded",
  "anomaly_detector": "loaded",
  "chatbot": "ready",
  "timestamp": "2026-09-11T12:00:00.000000+00:00"
}
```

---

### 3.2. Authentication Blueprint (`/api/auth`)

#### `POST /api/auth/login`
Authenticates user with email and password, returning JWT access token.

- **Request Body:**
```json
{
  "email": "sarah.jenkins@example.com",
  "password": "Password123!"
}
```
- **Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in_hours": 24,
  "user": {
    "user_id": 1,
    "email": "sarah.jenkins@example.com",
    "first_name": "Sarah",
    "last_name": "Jenkins",
    "user_type": "household",
    "meters": [1]
  }
}
```
- **Response `401 Unauthorized`:**
```json
{
  "error": "Unauthorized",
  "message": "Invalid email or password",
  "status_code": 401
}
```

#### `GET /api/auth/me`
Returns details of the currently authenticated user.
- **Request Headers:** `Authorization: Bearer <access_token>`
- **Response `200 OK`:**
```json
{
  "user_id": 1,
  "email": "sarah.jenkins@example.com",
  "first_name": "Sarah",
  "last_name": "Jenkins",
  "user_type": "household",
  "meters": [1]
}
```

---

### 3.3. Dashboard Blueprint (`/api/dashboard`)

#### `GET /api/dashboard/summary`
Aggregates summary telemetry, active meter, 24-hour volumetric consumption, SDG 6 efficiency rating, and system state.

- **Request Headers:** `Authorization: Bearer <access_token>`
- **Query Parameters:** `meter_id` (optional, defaults to primary meter)
- **Response `200 OK`:**
```json
{
  "meter_id": 1,
  "persona": "Sarah Jenkins (Single-Family Residential)",
  "today_usage_liters": 342.5,
  "yesterday_usage_liters": 365.2,
  "pct_change_vs_yesterday": -6.22,
  "sdg_efficiency_rating": "Good",
  "active_alerts_count": 1,
  "conservation_goal_pct": 82.4,
  "timestamp": "2026-09-11T12:00:00.000000+00:00"
}
```

---

### 3.4. Predictive Forecaster Blueprint (`/api/v1/forecast`)

#### `GET /api/v1/forecast/meters/<int:meter_id>`
Delivers a 7-day multi-step consumption forecast with validated uncertainty bounds.

- **Request Headers:** `Authorization: Bearer <access_token>`
- **Path Parameters:** `meter_id` (integer)
- **Response `200 OK`:**
```json
{
  "meter_id": 1,
  "model_type": "Global Random Forest Regressor",
  "benchmark_type": "Seasonal Naive (7-day lag)",
  "benchmark_mape": 9.85,
  "forecast_horizon_days": 7,
  "uncertainty_method": "Validation Residual Quantiles",
  "forecast": [
    {
      "day_offset": 1,
      "date": "2026-09-12",
      "predicted_liters": 348.2,
      "lower_bound": 312.4,
      "upper_bound": 384.0
    },
    {
      "day_offset": 2,
      "date": "2026-09-13",
      "predicted_liters": 352.1,
      "lower_bound": 315.8,
      "upper_bound": 388.4
    }
  ],
  "disclaimer": "Forecast projections represent mathematical estimations derived from historical usage patterns with validated uncertainty bounds."
}
```

---

### 3.5. Anomaly & Leak Detection Blueprint (`/api/v1/anomalies`)

#### `GET /api/v1/anomalies/meters/<int:meter_id>`
Returns active detected anomalies and pipeline leaks evaluated by the 4-layer hybrid engine.

- **Request Headers:** `Authorization: Bearer <access_token>`
- **Response `200 OK`:**
```json
{
  "meter_id": 1,
  "total_incidents": 1,
  "incidents": [
    {
      "incident_id": "INC-001",
      "anomaly_type": "continuous_leak",
      "severity": "high",
      "detection_layer": "Domain Physical Leak Rules",
      "start_time": "2026-09-10T02:00:00Z",
      "estimated_loss_liters_per_hour": 18.5,
      "estimated_daily_loss_liters": 444.0,
      "description": "Continuous baseline flow detected during minimum nighttime consumption window (02:00-05:00).",
      "referral_disclaimer": "High-severity leak detected. A licensed plumbing professional should inspect physical valves and fittings."
    }
  ]
}
```

---

### 3.6. Grounded Conservation Chatbot Blueprint (`/api/v1/chat`)

#### `POST /api/v1/chat`
Conversational decision support grounded in municipal water conservation knowledge and consumer telemetry context.

- **Request Headers:**
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **Request Body:**
```json
{
  "message": "How can I reduce my water consumption and fix the toilet leak?",
  "meter_id": 1
}
```
- **Response `200 OK`:**
```json
{
  "response": "To address toilet leaks, check the flapper valve inside the tank. A worn flapper is the most common cause of silent leaks, wasting up to 200 liters daily. For complex plumbing issues or concealed pipes, consult a licensed plumbing professional.\n\nKey Conservation Tip: Installing aerators on bathroom faucets can reduce tap flow by up to 30% without noticeable pressure loss.",
  "grounding_citations": [
    "KB-04: Toilet Flapper Inspection & Replacement",
    "KB-09: Low-Flow Aerators & Fixture Retrofits"
  ],
  "safety_disclaimers": {
    "plumber_referral": "High-severity leak advice requires certified inspection.",
    "human_oversight": "Recommendations provide decision support only. Automated valve actuators are not supported."
  }
}
```
