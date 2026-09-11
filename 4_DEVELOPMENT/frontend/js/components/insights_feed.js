/**
 * Smart Water Usage Advisor - Trend & Pattern Insights Component
 * Phase 7 - Advanced Water Intelligence & Impact Features
 * Location: 4_DEVELOPMENT/frontend/js/components/insights_feed.js
 */

export async function renderInsightsFeed(apiClient, getUserId) {
  const container = document.getElementById("insights-container");
  if (!container) return;

  const userId = getUserId();
  const isAuthenticated = apiClient && apiClient.isAuthenticated();

  if (!isAuthenticated) {
    container.innerHTML = `
      <div class="card" style="padding: 2rem; text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🔒</div>
        <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">
          Authentication Required
        </h3>
        <p style="font-size: 0.85rem; color: var(--text-secondary); max-width: 480px; margin: 0 auto 1.25rem;">
          Please sign in to inspect statistical usage trends, diurnal variance profiles, and conservation opportunities.
        </p>
        <button type="button" class="btn-chart-toggle active btn-insights-login" style="padding: 0.5rem 1.25rem; font-size: 0.85rem;">
          Sign In to Access Insights
        </button>
      </div>
    `;
    const loginBtn = container.querySelector(".btn-insights-login");
    if (loginBtn) {
      loginBtn.addEventListener("click", () => {
        if (window.smartWaterApp && window.smartWaterApp.openAuthModal) {
          window.smartWaterApp.openAuthModal();
        }
      });
    }
    return;
  }

  let insightsData = null;

  try {
    insightsData = await apiClient.fetchInsights(userId);
  } catch (err) {
    console.error("Failed to load insights:", err);
    container.innerHTML = `
      <div class="card" style="padding: 2rem; text-align: center; color: var(--status-critical);">
        ⚠️ Unable to retrieve behavioral insights. Please verify that the advisor service is running.
      </div>
    `;
    return;
  }

  const badgeColors = {
    critical: "var(--accent-rose)",
    high: "var(--status-high)",
    medium: "var(--accent-amber)",
    low: "var(--accent-cyan)"
  };

  const insightsList = (insightsData && insightsData.insights) ? insightsData.insights : [];

  container.innerHTML = `
    <div class="card" style="padding: 1.5rem;">
      <div class="section-header" style="margin-bottom: 1.25rem;">
        <h3 class="section-title"><span>🔍</span> Behavioral & Temporal Usage Insights</h3>
        <span class="sdg-badge">${insightsList.length} Patterns Detected</span>
      </div>

      ${insightsList.length === 0 ? `
        <div style="text-align: center; padding: 2.5rem 1rem; color: var(--text-muted); background: var(--bg-secondary); border-radius: var(--radius-md); margin-bottom: 1.5rem;">
          <div style="font-size: 1.75rem; margin-bottom: 0.5rem;">📊</div>
          <div style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem;">
            Insufficient data for this insight.
          </div>
          <p style="font-size: 0.8rem; color: var(--text-secondary); max-width: 420px; margin: 0 auto;">
            Statistical analysis requires at least 7 days of continuous smart meter telemetry to establish baseline diurnal variance and detect anomalous spikes.
          </p>
        </div>
      ` : `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
          ${insightsList.map(item => {
            const color = badgeColors[item.significance] || "var(--accent-cyan)";
            return `
              <div style="background: var(--bg-secondary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 1.1rem; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted);">${item.type.replace('_', ' ')}</span>
                    <span class="severity-pill" style="background: ${color}22; color: ${color}; font-size: 0.65rem;">${item.significance}</span>
                  </div>
                  <div style="font-size: 0.95rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">${item.title}</div>
                  <div style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.4;">${item.description}</div>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      `}

      <div style="font-size: 0.725rem; color: var(--text-muted); border-top: 1px solid var(--border-subtle); padding-top: 0.75rem;">
        ℹ️ ${insightsData.methodology_note || "Behavioral insights derived from time-series statistical modeling over 30-day baseline consumption."}
      </div>
    </div>
  `;
}
