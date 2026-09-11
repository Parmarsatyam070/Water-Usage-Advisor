/**
 * Smart Water Usage Advisor - Frontend API Client
 * Location: 4_DEVELOPMENT/frontend/js/api_client.js
 * 
 * Communicates with backend endpoints (/api/dashboard/* and /api/water/*, /api/alerts/*, /api/sdg6/*, /api/goals/*, /api/reports/*, /api/admin/*).
 * Never exposes database passwords or internal Python objects to the browser.
 */

export class DashboardApiClient {
  constructor(baseUrl = "") {
    this.baseUrl = baseUrl;
    this.authToken = (typeof localStorage !== "undefined" ? localStorage.getItem("swa_auth_token") : null) || null;
  }

  setAuthToken(token) {
    this.authToken = token;
    if (typeof localStorage !== "undefined") {
      if (token) {
        localStorage.setItem("swa_auth_token", token);
      } else {
        localStorage.removeItem("swa_auth_token");
        localStorage.removeItem("swa_current_user");
      }
    }
  }

  getAuthToken() {
    if (!this.authToken && typeof localStorage !== "undefined") {
      this.authToken = localStorage.getItem("swa_auth_token") || null;
    }
    return this.authToken;
  }

  isAuthenticated() {
    return Boolean(this.getAuthToken());
  }

  getCurrentUser() {
    if (typeof localStorage === "undefined") return null;
    try {
      return JSON.parse(localStorage.getItem("swa_current_user") || "null");
    } catch {
      return null;
    }
  }

  async login(email, password) {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: String(email).trim(), password: String(password) })
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}: Authentication failed`);
      }
      if (data.token) {
        this.setAuthToken(data.token);
        if (data.user && typeof localStorage !== "undefined") {
          localStorage.setItem("swa_current_user", JSON.stringify(data.user));
        }
      }
      return data;
    } catch (err) {
      console.error("ApiClient: Login error", err.message);
      throw err;
    }
  }

  logout() {
    this.setAuthToken(null);
  }

  _getHeaders(extraHeaders = {}) {
    const headers = { ...extraHeaders };
    const token = this.getAuthToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  // Phase 4/5 Core Dashboard Endpoints
  async fetchSummary(userId = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/api/dashboard/summary?user_id=${userId}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch summary`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch summary", err);
      throw err;
    }
  }

  async fetchConsumption(userId = 1, range = "30d") {
    try {
      const response = await fetch(`${this.baseUrl}/api/dashboard/consumption?user_id=${userId}&range=${range}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch consumption`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch consumption", err);
      throw err;
    }
  }

  async fetchForecast(userId = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/api/dashboard/forecast?user_id=${userId}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch forecast`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch forecast", err);
      throw err;
    }
  }

  async fetchAnomalies(userId = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/api/dashboard/anomalies?user_id=${userId}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch anomalies`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch anomalies", err);
      throw err;
    }
  }

  async fetchRecommendations(userId = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/api/dashboard/recommendations?user_id=${userId}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch recommendations`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch recommendations", err);
      throw err;
    }
  }

  async fetchGoals(userId = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/api/dashboard/goals?user_id=${userId}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch goals`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch goals", err);
      throw err;
    }
  }

  async sendChatMessage(userId, message) {
    try {
      const response = await fetch(`${this.baseUrl}/api/dashboard/chat`, {
        method: "POST",
        headers: this._getHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ user_id: userId, message: message })
      });
      if (response.status === 401) {
        this.setAuthToken(null);
        throw new Error("HTTP 401: Authentication required");
      }
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || `HTTP ${response.status}: Failed to send chat message`);
      }
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to send chat message", err.message);
      throw err;
    }
  }

  // ==========================================
  // Phase 7 Advanced Water Intelligence APIs
  // ==========================================

  // Feature 1: Water Savings Simulator
  async simulateSavings(params) {
    try {
      const response = await fetch(`${this.baseUrl}/api/water/savings/simulate`, {
        method: "POST",
        headers: this._getHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify(params)
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to simulate savings`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to simulate savings", err);
      throw err;
    }
  }

  // Feature 2: What-If Scenario Analysis
  async runScenario(params) {
    try {
      const response = await fetch(`${this.baseUrl}/api/water/scenarios`, {
        method: "POST",
        headers: this._getHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify(params)
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to run scenario`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to run scenario", err);
      throw err;
    }
  }

  async fetchScenarioHistory(userId = 1, limit = 10) {
    try {
      const response = await fetch(`${this.baseUrl}/api/water/scenarios/history?user_id=${userId}&limit=${limit}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch scenario history`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch scenario history", err);
      throw err;
    }
  }

  // Feature 3: Sustainability Score
  async fetchSustainabilityScore(userId = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/api/water/sustainability-score?user_id=${userId}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch sustainability score`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch sustainability score", err);
      throw err;
    }
  }

  // Feature 4: Alert History & Resolution
  async fetchAlertHistory(userId = 1, status = "ALL", limit = 50, offset = 0) {
    try {
      let url = `${this.baseUrl}/api/alerts/history?user_id=${userId}&limit=${limit}&offset=${offset}`;
      if (status && status !== "ALL") {
        url += `&status=${status}`;
      }
      const response = await fetch(url, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch alert history`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch alert history", err);
      throw err;
    }
  }

  async updateAlertStatus(alertId, newStatus, resolutionNote = "") {
    try {
      const response = await fetch(`${this.baseUrl}/api/alerts/${alertId}/status`, {
        method: "PATCH",
        headers: this._getHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ status: newStatus, resolution_note: resolutionNote })
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to update alert status`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to update alert status", err);
      throw err;
    }
  }

  // Feature 5: SDG 6.4 Impact
  async fetchSdg6Impact(userId = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/api/sdg6/impact?user_id=${userId}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch SDG 6 impact`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch SDG 6 impact", err);
      throw err;
    }
  }

  // Feature 6: Smart Goal Recommendations & Adoption
  async fetchGoalRecommendations(userId = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/api/goals/recommendations?user_id=${userId}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch goal recommendations`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch goal recommendations", err);
      throw err;
    }
  }

  async adoptGoal(params) {
    try {
      const response = await fetch(`${this.baseUrl}/api/goals/adopt`, {
        method: "POST",
        headers: this._getHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify(params)
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to adopt goal`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to adopt goal", err);
      throw err;
    }
  }

  // Feature 7: Trend & Pattern Insights
  async fetchInsights(userId = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/api/water/insights?user_id=${userId}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch insights`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch insights", err);
      throw err;
    }
  }

  // Feature 8: Water Budget Tracker
  async fetchBudget(userId = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/api/water/budget?user_id=${userId}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch budget`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch budget", err);
      throw err;
    }
  }

  async setBudget(params) {
    try {
      const response = await fetch(`${this.baseUrl}/api/water/budget`, {
        method: "POST",
        headers: this._getHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify(params)
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to set budget`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to set budget", err);
      throw err;
    }
  }

  // Feature 10: Admin System Summary (Municipal only)
  async fetchSystemSummary() {
    try {
      const response = await fetch(`${this.baseUrl}/api/admin/system-summary`, {
        headers: this._getHeaders()
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: Access Denied or Server Error`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to fetch system summary", err);
      throw err;
    }
  }

  // Feature 9: Authenticated Reports Exports
  async downloadReportCsv(userId = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/api/reports/water.csv?user_id=${userId}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to export CSV report`);
      }
      const blob = await response.blob();
      if (typeof window !== "undefined") {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = `water_audit_report_user_${userId}.csv`;
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
        }, 100);
      }
      return true;
    } catch (err) {
      console.error("ApiClient: Failed to export CSV", err);
      throw err;
    }
  }

  async fetchReportHtml(userId = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/api/reports/water.html?user_id=${userId}`, {
        headers: this._getHeaders()
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to generate executive report`);
      }
      return await response.text();
    } catch (err) {
      console.error("ApiClient: Failed to generate executive report", err);
      throw err;
    }
  }

  // Persona synchronization (strictly isolated to development/demo mode)
  async syncPersona(userId = 1) {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/demo-token?user_id=${userId}`);
      if (response.ok) {
        const data = await response.json();
        if (data && data.token) {
          this.setAuthToken(data.token);
          if (data.user && typeof localStorage !== "undefined") {
            localStorage.setItem("swa_current_user", JSON.stringify(data.user));
          }
          return data;
        }
      }
      return null;
    } catch {
      return null;
    }
  }
}
