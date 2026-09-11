/**
 * Smart Water Usage Advisor - Frontend API Client
 * Location: 4_DEVELOPMENT/frontend/js/api_client.js
 * 
 * Communicates with the local Python standard-library development server (/api/dashboard/*).
 * Never exposes database passwords or internal Python objects to the browser.
 */

export class DashboardApiClient {
  constructor(baseUrl = "") {
    this.baseUrl = baseUrl;
    this.authToken = null;
  }

  setAuthToken(token) {
    this.authToken = token;
  }

  _getHeaders(extraHeaders = {}) {
    const headers = { ...extraHeaders };
    if (this.authToken) {
      headers["Authorization"] = `Bearer ${this.authToken}`;
    }
    return headers;
  }

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
      if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to send chat message`);
      return await response.json();
    } catch (err) {
      console.error("ApiClient: Failed to send chat message", err);
      throw err;
    }
  }
}
