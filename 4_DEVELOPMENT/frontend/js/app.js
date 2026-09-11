/**
 * Smart Water Usage Advisor - Main Application Controller
 * Location: 4_DEVELOPMENT/frontend/js/app.js
 * 
 * Coordinates:
 * - DashboardApiClient
 * - Persona switching (User 1, 2, 3)
 * - Dark/Light theme switching with localStorage persistence
 * - Component renders: KPIs, Charts, Alerts, Recommendations, Goals, Chatbot
 */

import { DashboardApiClient } from "./api_client.js";
import { renderKpiCards } from "./components/kpi_cards.js";
import { initChartToggles, renderConsumptionChart, renderForecastChart } from "./components/charts.js";
import { renderAlerts } from "./components/alerts.js";
import { renderRecommendations } from "./components/recommendations.js";
import { renderGoals } from "./components/goals.js";
import { ChatbotDrawer } from "./components/chatbot.js";

class DashboardApp {
  constructor() {
    this.apiClient = new DashboardApiClient();
    this.currentUserId = 1;
    this.chatbot = null;

    this.init();
  }

  async init() {
    this.initTheme();
    initChartToggles();

    // Initialize Chatbot Drawer
    this.chatbot = new ChatbotDrawer(this.apiClient, () => this.currentUserId);

    // Persona Switcher Event
    const personaSelect = document.getElementById("persona-select");
    if (personaSelect) {
      personaSelect.addEventListener("change", (e) => {
        this.currentUserId = parseInt(e.target.value, 10);
        this.loadDashboardData();
      });
    }

    // Initial Data Load
    await this.loadDashboardData();
  }

  initTheme() {
    const themeBtn = document.getElementById("theme-toggle");
    const themeIcon = document.getElementById("theme-icon");
    const savedTheme = localStorage.getItem("swa-theme") || "dark";

    document.documentElement.setAttribute("data-theme", savedTheme);
    if (themeIcon) themeIcon.textContent = savedTheme === "light" ? "🌙" : "☀️";

    if (themeBtn) {
      themeBtn.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme");
        const next = current === "light" ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("swa-theme", next);
        if (themeIcon) themeIcon.textContent = next === "light" ? "🌙" : "☀️";

        // Re-render charts with new theme colors
        this.reloadChartsOnly();
      });
    }
  }

  async loadDashboardData() {
    try {
      // Parallel fetch across all DTO endpoints
      const [summary, consumption, forecast, anomalies, recommendations, goals] = await Promise.all([
        this.apiClient.fetchSummary(this.currentUserId),
        this.apiClient.fetchConsumption(this.currentUserId, "30d"),
        this.apiClient.fetchForecast(this.currentUserId),
        this.apiClient.fetchAnomalies(this.currentUserId),
        this.apiClient.fetchRecommendations(this.currentUserId),
        this.apiClient.fetchGoals(this.currentUserId)
      ]);

      // 1. Render KPI Overview
      renderKpiCards(summary);

      // 2. Render Charts
      renderConsumptionChart(consumption);
      renderForecastChart(forecast);

      // 3. Render Anomaly Alerts
      renderAlerts(anomalies, (promptText) => {
        if (this.chatbot) {
          this.chatbot.open();
          this.chatbot.sendMessage(promptText);
        }
      });

      // 4. Render Conservation Recommendations
      renderRecommendations(recommendations, (promptText) => {
        if (this.chatbot) {
          this.chatbot.open();
          this.chatbot.sendMessage(promptText);
        }
      });

      // 5. Render Conservation Goals
      renderGoals(goals);

      // 6. Update Chatbot Context Pill
      if (this.chatbot && summary.user) {
        this.chatbot.updateContextText(summary.user.meter_id, summary.user.property_type);
      }

    } catch (err) {
      console.error("DashboardApp: Error loading dashboard data:", err);
    }
  }

  async reloadChartsOnly() {
    try {
      const [consumption, forecast] = await Promise.all([
        this.apiClient.fetchConsumption(this.currentUserId, "30d"),
        this.apiClient.fetchForecast(this.currentUserId)
      ]);
      renderConsumptionChart(consumption);
      renderForecastChart(forecast);
    } catch (err) {
      console.error("Error reloading charts:", err);
    }
  }
}

// Instantiate application once DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.smartWaterApp = new DashboardApp();
});
