/**
 * Smart Water Usage Advisor - Trend & Pattern Insights Component
 * Phase 7 - Advanced Water Intelligence & Impact Features
 * Location: 4_DEVELOPMENT/frontend/js/components/insights_feed.js
 */

export async function renderInsightsFeed(apiClient, getUserId) {
  const container = document.getElementById("insights-container");
  if (!container) return;

  const userId = getUserId();
  let insightsData = null;

  try {
    insightsData = await apiClient.fetchInsights(userId);
  } catch (err) {
    console.error("Failed to load insights:", err);
    return;
  }

  const badgeColors = {
    critical: "var(--accent-rose)",
    high: "var(--status-high)",
    medium: "var(--accent-amber)",
    low: "var(--accent-cyan)"
  };

  container.innerHTML = `
    <div class="card" style="padding: 1.5rem;">
      <div class="section-header" style="margin-bottom: 1.25rem;">
        <h3 class="section-title"><span>🔍</span> Behavioral & Temporal Usage Insights</h3>
        <span class="sdg-badge">${insightsData.total_insights_count} Patterns Detected</span>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
        ${insightsData.insights.map(item => {
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

      <div style="font-size: 0.725rem; color: var(--text-muted); border-top: 1px solid var(--border-subtle); padding-top: 0.75rem;">
        ℹ️ ${insightsData.methodology_note}
      </div>
    </div>
  `;
}
