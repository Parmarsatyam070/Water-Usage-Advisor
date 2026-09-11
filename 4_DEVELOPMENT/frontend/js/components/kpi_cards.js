/**
 * Smart Water Usage Advisor - KPI Summary Cards Component
 * Location: 4_DEVELOPMENT/frontend/js/components/kpi_cards.js
 */

export function renderKpiCards(summaryData) {
  if (!summaryData) return;

  const currency = summaryData.currency_symbol || "₹";

  // 1. Today's Usage
  const todayEl = document.getElementById("val-today-usage");
  const todayTrendEl = document.getElementById("badge-today-trend");
  if (todayEl) todayEl.textContent = Number(summaryData.today_usage_liters || 0).toLocaleString();

  if (todayTrendEl) {
    const delta = Number(summaryData.today_delta_pct || 0);
    todayTrendEl.textContent = `${delta > 0 ? "▲ +" : "▼ "}${Math.abs(delta)}% vs last week`;
    todayTrendEl.className = `trend-badge ${delta <= 0 ? "trend-down" : "trend-up"}`;
  }

  // 2. 7-Day Forecast Average
  const forecastEl = document.getElementById("val-forecast-avg");
  const forecastTrendEl = document.getElementById("badge-forecast-trend");
  if (forecastEl) forecastEl.textContent = Number(summaryData.forecast_avg_liters_day || 0).toLocaleString();

  if (forecastTrendEl) {
    const fTrend = Number(summaryData.forecast_trend_pct || 0);
    forecastTrendEl.textContent = `${fTrend > 0 ? "▲ +" : "▼ "}${Math.abs(fTrend)}% vs 30d avg`;
    forecastTrendEl.className = `trend-badge ${fTrend <= 0 ? "trend-down" : "trend-up"}`;
  }

  // 3. Monthly Savings
  const savingsEl = document.getElementById("val-monthly-savings");
  const waterPreservedEl = document.getElementById("val-water-preserved");
  const currencyLabelEl = document.getElementById("val-savings-currency");

  if (savingsEl) savingsEl.textContent = `${currency}${Number(summaryData.monthly_financial_saved || 0).toFixed(2)}`;
  if (currencyLabelEl) currencyLabelEl.textContent = "Saved / mo";
  if (waterPreservedEl) {
    waterPreservedEl.textContent = `${Number(summaryData.monthly_water_saved_liters || 0).toLocaleString()} L preserved`;
  }

  // 4. Conservation Goal
  const goalEl = document.getElementById("val-goal-progress");
  const goalTargetLabelEl = document.getElementById("val-goal-target-label");
  if (goalEl) goalEl.textContent = `${Math.round(summaryData.goal_progress_pct || 0)}%`;

  if (goalTargetLabelEl) {
    goalTargetLabelEl.textContent = `Target: -${summaryData.goal_target_pct || 25}%`;
  }
}
