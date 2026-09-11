/**
 * Smart Water Usage Advisor - Main Application Controller
 * Location: 4_DEVELOPMENT/frontend/js/app.js
 * 
 * Coordinates:
 * - DashboardApiClient
 * - Persona switching (User 1: Household, User 2: Institution, User 3: Municipal)
 * - Dark/Light theme switching with localStorage persistence
 * - Phase 4/5 Component renders: KPIs, Charts, Alerts, Recommendations, Goals, Chatbot
 * - Phase 7 Component renders: Simulator, Sustainability Score, SDG 6.4, Smart Goals, Budget, Insights, Alerts Manager, Reports, Admin
 */

import { DashboardApiClient } from "./api_client.js";
import { renderKpiCards } from "./components/kpi_cards.js";
import { initChartToggles, renderConsumptionChart, renderForecastChart } from "./components/charts.js";
import { renderAlerts } from "./components/alerts.js";
import { renderRecommendations } from "./components/recommendations.js";
import { renderGoals } from "./components/goals.js";
import { ChatbotDrawer } from "./components/chatbot.js";

// Phase 7 Component Imports
import { renderSavingsSimulator } from "./components/savings_simulator.js";
import { renderSustainabilityScore } from "./components/sustainability_score.js";
import { renderSmartGoals } from "./components/smart_goals.js";
import { renderInsightsFeed } from "./components/insights_feed.js";
import { renderAlertsManager } from "./components/alerts_manager.js";
import { renderReportsManager } from "./components/reports_manager.js";
import { renderAdminMonitor } from "./components/admin_monitor.js";

class DashboardApp {
  constructor() {
    this.apiClient = new DashboardApiClient();
    this.currentUserId = 1;
    this.currentTab = "overview";
    this.chatbot = null;

    this.init();
  }

  async init() {
    this.initTheme();
    this.initSubnav();
    initChartToggles();

    // Initialize Chatbot Drawer
    this.chatbot = new ChatbotDrawer(this.apiClient, () => this.currentUserId);

    // Persona Switcher Event
    const personaSelect = document.getElementById("persona-select");
    if (personaSelect) {
      personaSelect.addEventListener("change", (e) => {
        this.currentUserId = parseInt(e.target.value, 10);
        this.loadActiveTab();
      });
    }

    // Initial Data Load
    await this.loadActiveTab();
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

        // Re-render charts with new theme colors if on overview
        if (this.currentTab === "overview") {
          this.reloadChartsOnly();
        }
      });
    }
  }

  initSubnav() {
    const subnavBtns = document.querySelectorAll(".subnav-btn");
    subnavBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const targetTab = btn.getAttribute("data-tab");
        if (!targetTab || targetTab === this.currentTab) return;

        // Switch active button class
        subnavBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        // Switch active tab pane
        const panes = document.querySelectorAll(".tab-pane");
        panes.forEach(p => p.classList.remove("active"));
        const activePane = document.getElementById(`tab-${targetTab}`);
        if (activePane) activePane.classList.add("active");

        this.currentTab = targetTab;
        this.loadActiveTab();
      });
    });
  }

  async loadActiveTab() {
    switch (this.currentTab) {
      case "overview":
        await this.loadDashboardData();
        break;
      case "simulator":
        renderSavingsSimulator(this.apiClient, () => this.currentUserId);
        break;
      case "sustainability":
        await renderSustainabilityScore(this.apiClient, () => this.currentUserId);
        break;
      case "goals-budget":
        await renderSmartGoals(this.apiClient, () => this.currentUserId);
        break;
      case "insights":
        await renderInsightsFeed(this.apiClient, () => this.currentUserId);
        break;
      case "alerts":
        await renderAlertsManager(this.apiClient, () => this.currentUserId);
        break;
      case "reports":
        renderReportsManager(this.apiClient, () => this.currentUserId);
        break;
      case "admin":
        await renderAdminMonitor(this.apiClient, () => this.currentUserId);
        break;
      default:
        await this.loadDashboardData();
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
