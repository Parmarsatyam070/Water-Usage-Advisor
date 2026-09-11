/**
 * Smart Water Usage Advisor - Smart Goals & Water Budget Component
 * Phase 7 - Advanced Water Intelligence & Impact Features
 * Location: 4_DEVELOPMENT/frontend/js/components/smart_goals.js
 */

export async function renderSmartGoals(apiClient, getUserId) {
  const container = document.getElementById("goals-budget-container");
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
          Please sign in to track your active monthly water budget and adopt tailored WHO-aligned conservation goals.
        </p>
        <button type="button" class="btn-chart-toggle active btn-goals-login" style="padding: 0.5rem 1.25rem; font-size: 0.85rem;">
          Sign In to Access Goals & Budget
        </button>
      </div>
    `;
    const loginBtn = container.querySelector(".btn-goals-login");
    if (loginBtn) {
      loginBtn.addEventListener("click", () => {
        if (window.smartWaterApp && window.smartWaterApp.openAuthModal) {
          window.smartWaterApp.openAuthModal();
        }
      });
    }
    return;
  }

  let budgetData = null;
  let recsData = null;

  try {
    [budgetData, recsData] = await Promise.all([
      apiClient.fetchBudget(userId),
      apiClient.fetchGoalRecommendations(userId)
    ]);
  } catch (err) {
    console.error("Failed to load goals & budget:", err);
    container.innerHTML = `
      <div class="card" style="padding: 2rem; text-align: center; color: var(--status-critical);">
        ⚠️ Unable to retrieve goals and budget data. Please verify that the advisor service is running.
      </div>
    `;
    return;
  }

  const isWarning = budgetData.forecast_projection.is_overshoot_predicted;
  const statusColor = isWarning ? "var(--status-high)" : "var(--accent-emerald)";

  container.innerHTML = `
    <div style="display: flex; flex-direction: column; gap: 1rem;">
      <div id="goals-notification-banner" style="display: none; padding: 0.75rem 1rem; border-radius: var(--radius-md); font-size: 0.825rem; font-weight: 600;"></div>

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
            <button type="submit" id="btn-submit-budget" class="btn-chart-toggle active" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">Update Budget</button>
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
              <div style="background: var(--bg-secondary); border: 1px solid var(--border-subtle); padding: 0.85rem; border-radius: var(--radius-md); display: flex; justify-content: space-between; align-items: center; gap: 0.75rem;">
                <div style="flex: 1;">
                  <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-primary);">${r.title}</div>
                  <div style="font-size: 0.75rem; color: var(--text-secondary); margin: 0.2rem 0;">${r.description}</div>
                  <div style="font-size: 0.7rem; color: var(--accent-emerald);">Est. Savings: ${r.estimated_monthly_savings_liters} L/mo (${r.currency_symbol}${r.estimated_monthly_financial_savings})</div>
                </div>
                <button class="btn-chart-toggle btn-adopt-goal" data-title="${r.title}" data-type="${r.goal_type}" data-val="${r.target_value}" data-unit="${r.target_unit}" data-days="${r.duration_days}" style="padding: 0.4rem 0.75rem; font-size: 0.75rem; white-space: nowrap;">
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
    </div>
  `;

  function showBanner(message, isSuccess = true) {
    const banner = document.getElementById("goals-notification-banner");
    if (banner) {
      banner.textContent = message;
      banner.style.display = "block";
      banner.style.background = isSuccess ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)";
      banner.style.color = isSuccess ? "var(--accent-emerald)" : "var(--status-critical)";
      banner.style.border = `1px solid ${isSuccess ? "var(--accent-emerald)" : "var(--status-critical)"}`;
      setTimeout(() => {
        banner.style.display = "none";
      }, 4000);
    }
  }

  // Bind Budget update form
  const budgetForm = document.getElementById("set-budget-form");
  if (budgetForm) {
    budgetForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const val = parseFloat(document.getElementById("new-budget-val").value);
      const submitBtn = document.getElementById("btn-submit-budget");
      if (submitBtn) submitBtn.disabled = true;

      try {
        await apiClient.setBudget({
          user_id: userId,
          period: "monthly",
          target_liters: val
        });
        showBanner(`✓ Water budget successfully updated to ${val.toLocaleString()} L for this billing cycle.`);
        await renderSmartGoals(apiClient, getUserId);
      } catch (err) {
        console.error("Failed to update budget:", err);
        showBanner(`⚠️ Failed to update budget: ${err.message || 'Unknown error'}`, false);
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  // Bind Adopt Goal buttons
  const adoptBtns = container.querySelectorAll(".btn-adopt-goal");
  adoptBtns.forEach(btn => {
    btn.addEventListener("click", async () => {
      const gTitle = btn.getAttribute("data-title") || "Conservation Goal";
      const gType = btn.getAttribute("data-type");
      const gVal = parseFloat(btn.getAttribute("data-val"));
      const gUnit = btn.getAttribute("data-unit");
      const gDays = parseInt(btn.getAttribute("data-days"), 10);

      btn.disabled = true;
      btn.textContent = "Adopting...";

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
        showBanner(`✓ Goal adopted: "${gTitle}" is now active in your conservation plan.`);
      } catch (err) {
        console.error("Failed to adopt goal:", err);
        btn.disabled = false;
        btn.textContent = "Adopt";
        showBanner(`⚠️ Failed to adopt goal: ${err.message || 'Unknown error'}`, false);
      }
    });
  });
}
