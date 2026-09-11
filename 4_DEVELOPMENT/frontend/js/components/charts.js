/**
 * Smart Water Usage Advisor - Chart.js Visualization Component
 * Location: 4_DEVELOPMENT/frontend/js/components/charts.js
 * 
 * Uses the locally vendored Chart.js v4.4.1 bundle (js/vendor/chart.umd.js).
 * Operates 100% offline with zero external runtime network dependency.
 */

let consumptionChartInstance = null;
let forecastChartInstance = null;
let activeConsumptionView = "diurnal"; // "diurnal" or "daily"
let cachedConsumptionData = null;

function getChartThemeColors() {
  const isDark = document.documentElement.getAttribute("data-theme") !== "light";
  return {
    textColor: isDark ? "#94a3b8" : "#475569",
    gridColor: isDark ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)",
    cyan: "#06b6d4",
    cyanAlpha: "rgba(6, 182, 212, 0.15)",
    blue: "#0284c7",
    purple: "#8b5cf6",
    purpleAlpha: "rgba(139, 92, 246, 0.15)",
    amber: "#f59e0b",
    emerald: "#10b981"
  };
}

export function initChartToggles() {
  const btnDiurnal = document.getElementById("btn-diurnal-view");
  const btnDaily = document.getElementById("btn-daily-view");

  if (btnDiurnal && btnDaily) {
    btnDiurnal.addEventListener("click", () => {
      if (activeConsumptionView !== "diurnal") {
        activeConsumptionView = "diurnal";
        btnDiurnal.classList.add("active");
        btnDaily.classList.remove("active");
        if (cachedConsumptionData) renderConsumptionChart(cachedConsumptionData);
      }
    });

    btnDaily.addEventListener("click", () => {
      if (activeConsumptionView !== "daily") {
        activeConsumptionView = "daily";
        btnDaily.classList.add("active");
        btnDiurnal.classList.remove("active");
        if (cachedConsumptionData) renderConsumptionChart(cachedConsumptionData);
      }
    });
  }
}

export function renderConsumptionChart(consumptionData) {
  if (!consumptionData) return;
  cachedConsumptionData = consumptionData;

  const canvas = document.getElementById("consumption-chart");
  if (!canvas || !window.Chart) return;

  const colors = getChartThemeColors();

  // Update peak hours callouts
  const morningEl = document.getElementById("val-morning-peak");
  const eveningEl = document.getElementById("val-evening-peak");
  const benchEl = document.getElementById("val-benchmark");
  if (morningEl) morningEl.textContent = consumptionData.peak_morning_hour || "08:00";
  if (eveningEl) eveningEl.textContent = consumptionData.peak_evening_hour || "19:00";
  if (benchEl) benchEl.textContent = `${consumptionData.regional_benchmark_lpd || 440} L/d`;

  if (consumptionChartInstance) {
    consumptionChartInstance.destroy();
    consumptionChartInstance = null;
  }

  const ctx = canvas.getContext("2d");

  if (activeConsumptionView === "diurnal") {
    // 24-Hour Diurnal Profile (Dual Line)
    consumptionChartInstance = new window.Chart(ctx, {
      type: "line",
      data: {
        labels: consumptionData.diurnal_hours,
        datasets: [
          {
            label: "Recent 24h Flow (L/hr)",
            data: consumptionData.diurnal_recent,
            borderColor: colors.cyan,
            backgroundColor: colors.cyanAlpha,
            fill: true,
            tension: 0.35,
            borderWidth: 2.5,
            pointRadius: 3,
            pointHoverRadius: 6
          },
          {
            label: "Diurnal Median Baseline (L/hr)",
            data: consumptionData.diurnal_baseline,
            borderColor: colors.textColor,
            borderDash: [5, 5],
            borderWidth: 1.5,
            fill: false,
            tension: 0.35,
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: {
            position: "top",
            labels: { color: colors.textColor, font: { size: 12 } }
          },
          tooltip: {
            callbacks: {
              label: (item) => `${item.dataset.label}: ${item.raw} Liters`
            }
          }
        },
        scales: {
          x: {
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor, maxTicksLimit: 12 }
          },
          y: {
            title: { display: true, text: "Flow Rate (Liters / Hour)", color: colors.textColor },
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor },
            beginAtZero: true
          }
        }
      }
    });
  } else {
    // 30-Day Historical Daily Bars + 7-day Moving Average Line
    consumptionChartInstance = new window.Chart(ctx, {
      data: {
        labels: consumptionData.daily_labels.map(l => l.slice(5)), // Short MM-DD
        datasets: [
          {
            type: "bar",
            label: "Daily Consumption (L)",
            data: consumptionData.daily_values,
            backgroundColor: colors.blue,
            borderRadius: 4,
            barPercentage: 0.6
          },
          {
            type: "line",
            label: "7-Day Moving Avg (L)",
            data: consumptionData.moving_avg_7d,
            borderColor: colors.amber,
            borderWidth: 2,
            tension: 0.3,
            pointRadius: 0,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: {
            position: "top",
            labels: { color: colors.textColor, font: { size: 12 } }
          }
        },
        scales: {
          x: {
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor, maxTicksLimit: 10 }
          },
          y: {
            title: { display: true, text: "Daily Volume (Liters)", color: colors.textColor },
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor },
            beginAtZero: true
          }
        }
      }
    });
  }
}

export function renderForecastChart(forecastData) {
  if (!forecastData) return;

  const canvas = document.getElementById("forecast-chart");
  if (!canvas || !window.Chart) return;

  const colors = getChartThemeColors();

  // Update peak day callout and model name
  const peakEl = document.getElementById("val-peak-day-label");
  const badgeEl = document.getElementById("badge-forecast-model");
  if (peakEl) peakEl.textContent = `${forecastData.peak_day_date} (~${forecastData.peak_day_liters} L)`;
  if (badgeEl) badgeEl.textContent = forecastData.model_name || "Random Forest (Phase 3A)";

  if (forecastChartInstance) {
    forecastChartInstance.destroy();
    forecastChartInstance = null;
  }

  const ctx = canvas.getContext("2d");

  // Short labels
  const shortLabels = forecastData.forecast_dates.map(d => d.slice(5));

  forecastChartInstance = new window.Chart(ctx, {
    type: "line",
    data: {
      labels: shortLabels,
      datasets: [
        {
          label: "7-Day Model Forecast (L)",
          data: forecastData.predicted_liters,
          borderColor: colors.purple,
          backgroundColor: colors.purpleAlpha,
          borderDash: [4, 4],
          borderWidth: 2.5,
          fill: true,
          tension: 0.3,
          pointRadius: 4,
          pointHoverRadius: 7
        },
        {
          label: "Seasonal Naive Baseline (L)",
          data: forecastData.baseline_liters,
          borderColor: colors.textColor,
          borderWidth: 1.5,
          fill: false,
          pointRadius: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: {
          position: "top",
          labels: { color: colors.textColor, font: { size: 12 } }
        },
        tooltip: {
          callbacks: {
            footer: (items) => {
              const idx = items[0].dataIndex;
              const low = forecastData.confidence_lower[idx];
              const high = forecastData.confidence_upper[idx];
              return `95% Confidence Band: ${low} - ${high} L`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: colors.gridColor },
          ticks: { color: colors.textColor }
        },
        y: {
          title: { display: true, text: "Forecasted Liters / Day", color: colors.textColor },
          grid: { color: colors.gridColor },
          ticks: { color: colors.textColor },
          beginAtZero: false
        }
      }
    }
  });
}
