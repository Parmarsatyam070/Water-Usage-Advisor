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
      personaSelect.addEventListener("change", async (e) => {
        this.currentUserId = parseInt(e.target.value, 10);
        await this.apiClient.syncPersona(this.currentUserId);
        this.updateAuthUI();
        await this.loadActiveTab();
      });
    }

    // Initialize Auth Modal & UI
    this.initAuthModal();

    // In dev mode, initialize token for default persona if not already authenticated
    if (!this.apiClient.isAuthenticated()) {
      await this.apiClient.syncPersona(this.currentUserId);
      this.updateAuthUI();
    }

    // Initial Data Load
    await this.loadActiveTab();
  }

  initAuthModal() {
    const authBtn = document.getElementById("btn-auth-login");
    const modal = document.getElementById("auth-modal-backdrop");
    const closeBtn = document.getElementById("btn-close-auth-modal");
    const cancelBtn = document.getElementById("btn-cancel-auth-modal");
    const form = document.getElementById("auth-login-form");
    const logoutBtn = document.getElementById("btn-auth-logout");
    const errorEl = document.getElementById("auth-login-error");

    this.updateAuthUI();

    if (authBtn) {
      authBtn.addEventListener("click", () => this.openAuthModal());
    }

    if (closeBtn) {
      closeBtn.addEventListener("click", () => this.closeAuthModal());
    }

    if (cancelBtn) {
      cancelBtn.addEventListener("click", () => this.closeAuthModal());
    }

    if (modal) {
      modal.addEventListener("click", (e) => {
        if (e.target === modal) this.closeAuthModal();
      });
    }

    // Demo persona autofill buttons
    document.querySelectorAll(".btn-demo-fill").forEach(btn => {
      btn.addEventListener("click", () => {
        const email = btn.getAttribute("data-email");
        const uid = btn.getAttribute("data-uid");
        const emailInput = document.getElementById("input-auth-email");
        const passInput = document.getElementById("input-auth-password");
        if (emailInput && email) emailInput.value = email;
        if (passInput) passInput.value = "ResidentPass2026!";
        if (uid && personaSelect) personaSelect.value = uid;
      });
    });

    // Handle Login Submit
    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const emailInput = document.getElementById("input-auth-email");
        const passInput = document.getElementById("input-auth-password");
        const submitBtn = document.getElementById("btn-submit-auth-login");

        if (!emailInput || !passInput) return;
        const email = emailInput.value.trim();
        const password = passInput.value;

        if (errorEl) {
          errorEl.style.display = "none";
          errorEl.textContent = "";
        }

        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.textContent = "Authenticating...";
        }

        try {
          const data = await this.apiClient.login(email, password);
          if (data && data.user) {
            this.currentUserId = data.user.user_id;
            const personaSelect = document.getElementById("persona-select");
            if (personaSelect) personaSelect.value = String(data.user.user_id);
          }
          this.updateAuthUI();
          this.closeAuthModal();
          await this.loadActiveTab();
        } catch (err) {
          if (errorEl) {
            errorEl.textContent = err.message || "Authentication failed. Please check credentials.";
            errorEl.style.display = "block";
          }
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = "Sign In";
          }
        }
      });
    }

    // Handle Logout
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => {
        this.apiClient.logout();
        this.updateAuthUI();
        this.closeAuthModal();
      });
    }
  }

  openAuthModal() {
    const modal = document.getElementById("auth-modal-backdrop");
    const errorEl = document.getElementById("auth-login-error");
    if (errorEl) {
      errorEl.style.display = "none";
      errorEl.textContent = "";
    }
    if (modal) {
      modal.style.display = "flex";
      modal.setAttribute("aria-hidden", "false");
    }
    const authBtn = document.getElementById("btn-auth-login");
    if (authBtn) authBtn.setAttribute("aria-expanded", "true");
  }

  closeAuthModal() {
    const modal = document.getElementById("auth-modal-backdrop");
    if (modal) {
      modal.style.display = "none";
      modal.setAttribute("aria-hidden", "true");
    }
    const authBtn = document.getElementById("btn-auth-login");
    if (authBtn) authBtn.setAttribute("aria-expanded", "false");
  }

  updateAuthUI() {
    const authLabel = document.getElementById("auth-btn-label");
    const authIcon = document.getElementById("auth-btn-icon");
    const logoutBtn = document.getElementById("btn-auth-logout");
    const submitBtn = document.getElementById("btn-submit-auth-login");

    if (this.apiClient.isAuthenticated()) {
      const user = this.apiClient.getCurrentUser();
      const userName = user ? (user.first_name || user.email.split("@")[0]) : "User";
      if (authLabel) authLabel.textContent = `${userName}`;
      if (authIcon) authIcon.textContent = "🔓";
      if (logoutBtn) logoutBtn.style.display = "inline-block";
      if (submitBtn) submitBtn.textContent = "Switch Account";
    } else {
      if (authLabel) authLabel.textContent = "Log In";
      if (authIcon) authIcon.textContent = "🔐";
      if (logoutBtn) logoutBtn.style.display = "none";
      if (submitBtn) submitBtn.textContent = "Sign In";
    }
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
        await renderSavingsSimulator(this.apiClient, () => this.currentUserId);
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
