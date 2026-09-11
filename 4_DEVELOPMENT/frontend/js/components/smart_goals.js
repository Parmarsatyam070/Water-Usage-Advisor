/**
 * Smart Water Usage Advisor - Smart Goals & Water Budget Component
 * Phase 7 - Advanced Water Intelligence & Impact Features
 * Location: 4_DEVELOPMENT/frontend/js/components/smart_goals.js
 */

export async function renderSmartGoals(apiClient, getUserId) {
  const container = document.getElementById("goals-budget-container");
  if (!container) return;

  const userId = getUserId();
  let budgetData = null;
  let recsData = null;

  try {
    [budgetData, recsData] = await Promise.all([
      apiClient.fetchBudget(userId),
      apiClient.fetchGoalRecommendations(userId)
    ]);
  } catch (err) {
    console.error("Failed to load goals & budget:", err);
    return;
  }

  const isWarning = budgetData.forecast_projection.is_overshoot_predicted;
  const statusColor = isWarning ? "var(--status-high)" : "var(--accent-emerald)";

  container.innerHTML = `
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">

      <!-- Feature 8: Water Budget Tracker -->
      <div class="card" style="padding: 1.5rem;">
        <div class="section-header" style="margin-bottom: 1rem;">
          <h3 class="section-title"><span>🎯</span> Water Budget Planner</h3>
          <span class="severity-pill" style="background: ${statusColor}22; color: ${statusColor}; font-weight: 600;">
            ${isWarning ? "⚠️ Overshoot Risk" : "✅ On Track"}
          </span>
        </div>

        <div style="margin-bottom: 1.25rem;">
          <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.35rem;">
            <span>Consumed: <strong>${budgetData.consumption_status.consumed_liters_to_date.toLocaleString()} L</strong></span>
            <span>Target: <strong>${budgetData.target_liters.toLocaleString()} L</strong></span>
          </div>
          <div class="progress-track" style="height: 10px;">
            <div class="progress-fill" style="width: ${Math.min(100, budgetData.consumption_status.consumed_percentage)}%; background: ${statusColor};"></div>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); margin-top: 0.35rem;">
            <span>${budgetData.time_progress.days_elapsed} of ${budgetData.time_progress.total_days} days elapsed</span>
            <span>${budgetData.consumption_status.consumed_percentage}% budget used</span>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin-bottom: 1.25rem;">
          <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: var(--radius-md);">
            <div style="font-size: 0.7rem; color: var(--text-muted);">Ideal Burn Rate</div>
            <div style="font-size: 1.1rem; font-weight: 700;">${budgetData.consumption_status.ideal_burn_rate_lpd} L/d</div>
          </div>
          <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: var(--radius-md);">
            <div style="font-size: 0.7rem; color: var(--text-muted);">Actual Burn Rate</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: ${statusColor};">${budgetData.consumption_status.actual_burn_rate_lpd} L/d</div>
          </div>
        </div>

        ${isWarning ? `
          <div style="background: var(--status-high-bg); border-left: 3px solid var(--status-high); padding: 0.75rem; border-radius: var(--radius-sm); font-size: 0.8rem; color: var(--text-primary); margin-bottom: 1rem;">
            <strong>Overshoot Warning:</strong> At the current forecast burn rate, you are projected to exceed your budget by
            <strong>${budgetData.forecast_projection.projected_overshoot_liters} L</strong>
            (est. ₹${budgetData.forecast_projection.projected_overshoot_cost}).
          </div>
        ` : ''}

        <!-- Update Budget Form -->
        <form id="set-budget-form" style="display: flex; gap: 0.5rem; align-items: flex-end;">
          <div style="flex: 1;">
            <label style="font-size: 0.75rem; color: var(--text-secondary); display: block; margin-bottom: 0.2rem;">New Target (Liters)</label>
            <input type="number" id="new-budget-val" value="${budgetData.target_liters}" min="100" step="50" required class="chat-input" style="width: 100%; padding: 0.4rem 0.6rem;">
          </div>
          <button type="submit" class="btn-chart-toggle active" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">Update Budget</button>
        </form>
      </div>

      <!-- Feature 6: Smart Goal Recommendations -->
      <div class="card" style="padding: 1.5rem;">
        <div class="section-header" style="margin-bottom: 1rem;">
          <h3 class="section-title"><span>💡</span> Smart Goal Recommendations</h3>
          <span class="sdg-badge">WHO Aligned</span>
        </div>

        <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1rem;">
          ${recsData.recommendations.map(r => `
            <div style="background: var(--bg-secondary); border: 1px solid var(--border-subtle); padding: 0.85rem; border-radius: var(--radius-md); display: flex; justify-content: space-between; align-items: center;">
              <div>
                <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-primary);">${r.title}</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin: 0.2rem 0;">${r.description}</div>
                <div style="font-size: 0.7rem; color: var(--accent-emerald);">Est. Savings: ${r.estimated_monthly_savings_liters} L/mo (${r.currency_symbol}${r.estimated_monthly_financial_savings})</div>
              </div>
              <button class="btn-chart-toggle btn-adopt-goal" data-type="${r.goal_type}" data-val="${r.target_value}" data-unit="${r.target_unit}" data-days="${r.duration_days}" style="padding: 0.4rem 0.75rem; font-size: 0.75rem; white-space: nowrap;">
                Adopt
              </button>
            </div>
          `).join('')}
        </div>

        <div style="font-size: 0.725rem; color: var(--text-muted); border-top: 1px solid var(--border-subtle); padding-top: 0.75rem;">
          ℹ️ ${recsData.sanitary_floor_disclosure}
        </div>
      </div>

    </div>
  `;

  // Bind Budget update form
  const budgetForm = document.getElementById("set-budget-form");
  if (budgetForm) {
    budgetForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const val = parseFloat(document.getElementById("new-budget-val").value);
      try {
        await apiClient.setBudget({
          user_id: userId,
          period: "monthly",
          target_liters: val
        });
        await renderSmartGoals(apiClient, getUserId);
      } catch (err) {
        console.error("Failed to update budget:", err);
      }
    });
  }

  // Bind Adopt Goal buttons
  const adoptBtns = container.querySelectorAll(".btn-adopt-goal");
  adoptBtns.forEach(btn => {
    btn.addEventListener("click", async () => {
      const gType = btn.getAttribute("data-type");
      const gVal = parseFloat(btn.getAttribute("data-val"));
      const gUnit = btn.getAttribute("data-unit");
      const gDays = parseInt(btn.getAttribute("data-days"), 10);

      try {
        await apiClient.adoptGoal({
          user_id: userId,
          goal_type: gType,
          target_value: gVal,
          target_unit: gUnit,
          duration_days: gDays
        });
        btn.textContent = "✓ Active";
        btn.classList.add("active");
        btn.disabled = true;
      } catch (err) {
        console.error("Failed to adopt goal:", err);
      }
    });
  });
}
