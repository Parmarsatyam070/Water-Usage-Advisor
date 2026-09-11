/**
 * Smart Water Usage Advisor - Sustainability Score & SDG 6.4 Component
 * Phase 7 - Advanced Water Intelligence & Impact Features
 * Location: 4_DEVELOPMENT/frontend/js/components/sustainability_score.js
 */

export async function renderSustainabilityScore(apiClient, getUserId) {
  const container = document.getElementById("sustainability-container");
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
          Please sign in to inspect your personalized 0-100 Water Sustainability Score and UN SDG 6.4 water efficiency benchmarks.
        </p>
        <button type="button" class="btn-chart-toggle active btn-sustainability-login" style="padding: 0.5rem 1.25rem; font-size: 0.85rem;">
          Sign In to Access Sustainability Metrics
        </button>
      </div>
    `;
    const loginBtn = container.querySelector(".btn-sustainability-login");
    if (loginBtn) {
      loginBtn.addEventListener("click", () => {
        if (window.smartWaterApp && window.smartWaterApp.openAuthModal) {
          window.smartWaterApp.openAuthModal();
        }
      });
    }
    return;
  }

  let scoreData = null;
  let sdgData = null;

  try {
    [scoreData, sdgData] = await Promise.all([
      apiClient.fetchSustainabilityScore(userId),
      apiClient.fetchSdg6Impact(userId)
    ]);
  } catch (err) {
    console.error("Failed to load sustainability and SDG metrics:", err);
    container.innerHTML = `
      <div class="card" style="padding: 2rem; text-align: center; color: var(--status-critical);">
        ⚠️ Unable to retrieve sustainability metrics. Please verify that the advisor service is accessible.
      </div>
    `;
    return;
  }

  const gradeColors = {
    A: "var(--accent-emerald)",
    B: "var(--accent-cyan)",
    C: "var(--accent-amber)",
    D: "var(--status-high)",
    F: "var(--accent-rose)"
  };

  const gradeColor = gradeColors[scoreData.grade] || "var(--accent-cyan)";
  const opps = scoreData.improvement_opportunities || [];

  container.innerHTML = `
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">

      <!-- Feature 3: Sustainability Score Card -->
      <div class="card" style="padding: 1.5rem;">
        <div class="section-header" style="margin-bottom: 1.25rem;">
          <h3 class="section-title"><span>🌿</span> Water Sustainability Score</h3>
          <span class="sdg-badge" style="background: ${gradeColor}22; color: ${gradeColor}; font-weight: 700;">
            Grade ${scoreData.grade} (${scoreData.rating})
          </span>
        </div>

        <div style="display: flex; align-items: center; justify-content: center; gap: 2rem; margin: 1.25rem 0;">
          <div style="text-align: center;">
            <div style="font-size: 3.5rem; font-weight: 800; color: ${gradeColor}; line-height: 1;">
              ${scoreData.sustainability_score}
            </div>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">out of 100</div>
          </div>
          <div style="flex: 1; display: flex; flex-direction: column; gap: 0.6rem;">
            <div>
              <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 0.2rem;">
                <span>Efficiency (30%)</span>
                <strong>${scoreData.components.efficiency.score}</strong>
              </div>
              <div class="progress-track"><div class="progress-fill" style="width: ${scoreData.components.efficiency.score}%;"></div></div>
            </div>
            <div>
              <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 0.2rem;">
                <span>Anomaly Status (25%)</span>
                <strong>${scoreData.components.anomaly_status.score}</strong>
              </div>
              <div class="progress-track"><div class="progress-fill" style="width: ${scoreData.components.anomaly_status.score}%;"></div></div>
            </div>
            <div>
              <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 0.2rem;">
                <span>Goal Achievement (25%)</span>
                <strong>${scoreData.components.goal_progress.score}</strong>
              </div>
              <div class="progress-track"><div class="progress-fill" style="width: ${scoreData.components.goal_progress.score}%;"></div></div>
            </div>
            <div>
              <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 0.2rem;">
                <span>Trend Stability (20%)</span>
                <strong>${scoreData.components.usage_trend.score}</strong>
              </div>
              <div class="progress-track"><div class="progress-fill" style="width: ${scoreData.components.usage_trend.score}%;"></div></div>
            </div>
          </div>
        </div>

        <!-- Deterministic Narrative Explanation -->
        ${scoreData.explanation ? `
          <div style="background: var(--bg-secondary); border-left: 3px solid ${gradeColor}; padding: 0.75rem; border-radius: var(--radius-sm); font-size: 0.8rem; color: var(--text-primary); margin-bottom: 1rem; line-height: 1.4;">
            <strong>Advisor Assessment:</strong> ${scoreData.explanation}
          </div>
        ` : ''}

        <!-- Structured Improvement Opportunities -->
        ${opps.length > 0 ? `
          <div style="margin-bottom: 1rem;">
            <div style="font-size: 0.8rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.4rem;">
              🎯 High-Impact Improvement Opportunities:
            </div>
            <ul style="margin: 0; padding-left: 1.2rem; font-size: 0.775rem; color: var(--text-secondary); line-height: 1.4;">
              ${opps.map(op => `<li style="margin-bottom: 0.25rem;">${op}</li>`).join('')}
            </ul>
          </div>
        ` : ''}

        <div style="font-size: 0.725rem; color: var(--text-muted); border-top: 1px solid var(--border-subtle); padding-top: 0.75rem;">
          ℹ️ ${scoreData.methodology_disclosure}
        </div>
      </div>

      <!-- Feature 5: SDG 6.4 Impact Dashboard -->
      <div class="card" style="padding: 1.5rem;">
        <div class="section-header" style="margin-bottom: 1.25rem;">
          <h3 class="section-title"><span>🌐</span> SDG 6.4 Impact Indicators</h3>
          <span class="sdg-badge">Target 6.4 Alignment</span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.25rem;">
          <!-- Card 1: Measured Consumption -->
          <div style="background: var(--bg-secondary); padding: 0.85rem; border-radius: var(--radius-md); position: relative;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Measured Consumption</span>
              <span class="severity-pill" style="background: rgba(6, 182, 212, 0.15); color: var(--accent-cyan); font-size: 0.65rem; font-weight: 700;">[MEASURED]</span>
            </div>
            <div style="font-size: 1.4rem; font-weight: 700; color: var(--text-primary); margin-top: 0.25rem;">
              ${sdgData.measured_telemetry.monthly_consumption_m3} m³
            </div>
            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.15rem;">
              ${sdgData.measured_telemetry.per_capita_daily_liters} L/person/day
            </div>
          </div>

          <!-- Card 2: Avoided Leak Volume -->
          <div style="background: var(--bg-secondary); padding: 0.85rem; border-radius: var(--radius-md); position: relative;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Avoided Leak Volume</span>
              <span class="severity-pill" style="background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); font-size: 0.65rem; font-weight: 700;">[ESTIMATED]</span>
            </div>
            <div style="font-size: 1.4rem; font-weight: 700; color: var(--accent-emerald); margin-top: 0.25rem;">
              ${sdgData.leak_impact.estimated_avoided_leak_volume_liters} L
            </div>
            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.15rem;">
              ${sdgData.leak_impact.metric_name}
            </div>
          </div>

          <!-- Card 3: Water Efficiency Ratio -->
          <div style="background: var(--bg-secondary); padding: 0.85rem; border-radius: var(--radius-md); position: relative;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Water Efficiency Ratio</span>
              <span class="severity-pill" style="background: rgba(6, 182, 212, 0.15); color: var(--accent-cyan); font-size: 0.65rem; font-weight: 700;">[MEASURED]</span>
            </div>
            <div style="font-size: 1.4rem; font-weight: 700; color: var(--accent-cyan); margin-top: 0.25rem;">
              ${sdgData.efficiency_benchmark.water_use_efficiency_index}x
            </div>
            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.15rem;">
              vs benchmark (${sdgData.efficiency_benchmark.status})
            </div>
          </div>

          <!-- Card 4: Avoided Water Cost -->
          <div style="background: var(--bg-secondary); padding: 0.85rem; border-radius: var(--radius-md); position: relative;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Avoided Water Cost</span>
              <span class="severity-pill" style="background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); font-size: 0.65rem; font-weight: 700;">[ESTIMATED]</span>
            </div>
            <div style="font-size: 1.4rem; font-weight: 700; color: var(--accent-amber); margin-top: 0.25rem;">
              ${sdgData.leak_impact.currency_symbol}${sdgData.leak_impact.estimated_cost_avoided}
            </div>
            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.15rem;">
              Savings from verified resolutions
            </div>
          </div>
        </div>

        <div style="font-size: 0.725rem; color: var(--text-muted); border-top: 1px solid var(--border-subtle); padding-top: 0.75rem;">
          ℹ️ ${sdgData.methodology_disclosure}
        </div>
      </div>

    </div>
  `;
}
