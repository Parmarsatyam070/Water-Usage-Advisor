/**
 * Smart Water Usage Advisor - Savings Simulator & What-If Scenario Component
 * Phase 7 - Advanced Water Intelligence & Impact Features
 * Location: 4_DEVELOPMENT/frontend/js/components/savings_simulator.js
 */

export async function renderSavingsSimulator(apiClient, getUserId) {
  const container = document.getElementById("simulator-container");
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
          Please sign in to run deterministic water conservation simulations, evaluate what-if scenarios, and inspect saved scenario telemetry.
        </p>
        <button type="button" class="btn-chart-toggle active btn-simulator-login" style="padding: 0.5rem 1.25rem; font-size: 0.85rem;">
          Sign In to Access Simulator
        </button>
      </div>
    `;
    const loginBtn = container.querySelector(".btn-simulator-login");
    if (loginBtn) {
      loginBtn.addEventListener("click", () => {
        if (window.smartWaterApp && window.smartWaterApp.openAuthModal) {
          window.smartWaterApp.openAuthModal();
        }
      });
    }
    return;
  }

  container.innerHTML = `
    <div style="display: flex; flex-direction: column; gap: 1.5rem;">
      <div class="simulator-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">

        <!-- Feature 1: Water Savings Calculator -->
        <div class="card" style="padding: 1.5rem;">
          <h3 class="section-title" style="margin-bottom: 1rem;"><span>💧</span> Water Savings Calculator</h3>
          <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1.25rem;">
            Estimate potential volumetric and financial savings by modeling custom reduction targets.
          </p>

          <form id="calc-form" style="display: flex; flex-direction: column; gap: 1rem;">
            <div>
              <label style="font-size: 0.8rem; color: var(--text-secondary); display: block; margin-bottom: 0.25rem;">Baseline Consumption (Liters)</label>
              <input type="number" id="calc-baseline" value="440" min="1" step="10" required class="chat-input" style="width: 100%;">
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div>
                <label style="font-size: 0.8rem; color: var(--text-secondary); display: block; margin-bottom: 0.25rem;">Reduction (%)</label>
                <input type="number" id="calc-pct" value="15" min="0" max="100" step="1" class="chat-input" style="width: 100%;">
              </div>
              <div>
                <label style="font-size: 0.8rem; color: var(--text-secondary); display: block; margin-bottom: 0.25rem;">Rate per kL (₹)</label>
                <input type="number" id="calc-rate" value="45" min="0" step="1" class="chat-input" style="width: 100%;">
              </div>
            </div>

            <button type="submit" class="btn-chart-toggle active" style="margin-top: 0.5rem; padding: 0.6rem;">Calculate Savings</button>
          </form>

          <div id="calc-results" class="hidden" style="margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid var(--border-subtle);">
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; text-align: center; margin-bottom: 0.75rem;">
              <div style="background: var(--bg-secondary); padding: 0.6rem; border-radius: var(--radius-sm);">
                <div style="font-size: 0.7rem; color: var(--text-muted);">Baseline</div>
                <div id="res-base-liters" style="font-size: 1rem; font-weight: 700; color: var(--text-primary);">-- L</div>
              </div>
              <div style="background: var(--bg-secondary); padding: 0.6rem; border-radius: var(--radius-sm);">
                <div style="font-size: 0.7rem; color: var(--text-muted);">Projected Volume</div>
                <div id="res-proj-liters" style="font-size: 1rem; font-weight: 700; color: var(--accent-cyan);">-- L</div>
              </div>
              <div style="background: var(--bg-secondary); padding: 0.6rem; border-radius: var(--radius-sm);">
                <div style="font-size: 0.7rem; color: var(--text-muted);">Reduction</div>
                <div id="res-red-pct" style="font-size: 1rem; font-weight: 700; color: var(--accent-emerald);">--%</div>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; text-align: center;">
              <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: var(--radius-md);">
                <div style="font-size: 0.75rem; color: var(--text-muted);">Period Saved</div>
                <div id="res-saved-liters" style="font-size: 1.15rem; font-weight: 700; color: var(--accent-emerald);">-- L</div>
                <div id="res-saved-cost" style="font-size: 0.75rem; color: var(--accent-amber); margin-top: 0.2rem;">₹--</div>
              </div>
              <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: var(--radius-md);">
                <div style="font-size: 0.75rem; color: var(--text-muted);">Annualized Savings</div>
                <div id="res-annual-liters" style="font-size: 1.15rem; font-weight: 700; color: var(--accent-cyan);">-- L/yr</div>
                <div id="res-annual-savings" style="font-size: 0.75rem; color: var(--accent-cyan); margin-top: 0.2rem;">₹--/yr</div>
              </div>
            </div>
            <p id="calc-disclaimer" style="font-size: 0.725rem; color: var(--text-muted); margin-top: 0.75rem; font-style: italic;"></p>
          </div>
        </div>

        <!-- Feature 2: What-If Scenario Analysis -->
        <div class="card" style="padding: 1.5rem;">
          <h3 class="section-title" style="margin-bottom: 1rem;"><span>🔬</span> What-If End-Use Scenario</h3>
          <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1.25rem;">
            Simulate behavioral adjustments or fixture retrofits across specific consumption categories.
          </p>

          <form id="scenario-form" style="display: flex; flex-direction: column; gap: 1rem;">
            <div>
              <label style="font-size: 0.8rem; color: var(--text-secondary); display: block; margin-bottom: 0.25rem;">Scenario Name</label>
              <input type="text" id="scen-name" value="Low-Flow Aerators" required class="chat-input" style="width: 100%;">
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
              <div>
                <label style="font-size: 0.8rem; color: var(--text-secondary); display: block; margin-bottom: 0.25rem;">Target Category</label>
                <select id="scen-category" class="persona-select" style="width: 100%;">
                  <option value="bathroom">Bathroom (40%)</option>
                  <option value="kitchen">Kitchen (20%)</option>
                  <option value="laundry">Laundry (15%)</option>
                  <option value="garden">Garden (15%)</option>
                  <option value="cleaning">Cleaning (5%)</option>
                  <option value="all">All Categories</option>
                </select>
              </div>
              <div>
                <label style="font-size: 0.8rem; color: var(--text-secondary); display: block; margin-bottom: 0.25rem;">Delta % (-100 to +100)</label>
                <input type="number" id="scen-pct" value="-20" min="-100" max="100" step="5" class="chat-input" style="width: 100%;">
              </div>
            </div>

            <div style="display: flex; gap: 0.5rem; align-items: center;">
              <input type="checkbox" id="scen-save" checked>
              <label for="scen-save" style="font-size: 0.8rem; color: var(--text-secondary);">Save scenario to user history</label>
            </div>

            <button type="submit" class="btn-chart-toggle active" style="margin-top: 0.5rem; padding: 0.6rem;">Run Simulation</button>
          </form>

          <div id="scenario-results" class="hidden" style="margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid var(--border-subtle);">
            <div id="scen-explanation" style="font-size: 0.85rem; color: var(--text-primary); margin-bottom: 0.75rem; line-height: 1.4;"></div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; text-align: center;">
              <div style="background: var(--bg-secondary); padding: 0.5rem; border-radius: var(--radius-sm);">
                <div style="font-size: 0.7rem; color: var(--text-muted);">Baseline Daily</div>
                <div id="scen-base-val" style="font-weight: 700;">-- L</div>
              </div>
              <div style="background: var(--bg-secondary); padding: 0.5rem; border-radius: var(--radius-sm);">
                <div style="font-size: 0.7rem; color: var(--text-muted);">Simulated Daily</div>
                <div id="scen-sim-val" style="font-weight: 700; color: var(--accent-cyan);">-- L</div>
              </div>
              <div style="background: var(--bg-secondary); padding: 0.5rem; border-radius: var(--radius-sm);">
                <div style="font-size: 0.7rem; color: var(--text-muted);">Monthly Impact</div>
                <div id="scen-impact-val" style="font-weight: 700; color: var(--accent-emerald);">--</div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Feature 2: Scenario History Section -->
      <div class="card" style="padding: 1.5rem;">
        <div class="section-header" style="margin-bottom: 1rem;">
          <h3 class="section-title"><span>📜</span> Saved Scenario History</h3>
          <span class="sdg-badge" id="scen-history-count">0 Scenarios</span>
        </div>
        <div id="scen-history-table-container" style="overflow-x: auto;">
          <div style="text-align: center; padding: 1.5rem; color: var(--text-muted); font-size: 0.85rem;">
            Loading scenario history...
          </div>
        </div>
      </div>
    </div>
  `;

  // Function to load and render scenario history
  async function loadScenarioHistory() {
    const histContainer = document.getElementById("scen-history-table-container");
    const countBadge = document.getElementById("scen-history-count");
    if (!histContainer) return;

    try {
      const data = await apiClient.fetchScenarioHistory(userId);
      const scenarios = (data && data.scenarios) ? data.scenarios : [];
      if (countBadge) countBadge.textContent = `${scenarios.length} Saved`;

      if (scenarios.length === 0) {
        histContainer.innerHTML = `
          <div style="text-align: center; padding: 1.5rem; color: var(--text-muted); font-size: 0.85rem;">
            No saved scenarios recorded yet. Run a What-If simulation above with "Save scenario" checked to track interventions.
          </div>
        `;
        return;
      }

      histContainer.innerHTML = `
        <table style="width: 100%; font-size: 0.8rem; border-collapse: collapse; text-align: left;">
          <thead>
            <tr style="border-bottom: 1px solid var(--border-subtle); color: var(--text-muted);">
              <th style="padding: 0.5rem;">Scenario Name</th>
              <th style="padding: 0.5rem;">Category</th>
              <th style="padding: 0.5rem;">Delta %</th>
              <th style="padding: 0.5rem;">Baseline (L/d)</th>
              <th style="padding: 0.5rem;">Simulated (L/d)</th>
              <th style="padding: 0.5rem;">Est. Savings</th>
              <th style="padding: 0.5rem;">Created</th>
            </tr>
          </thead>
          <tbody>
            ${scenarios.map(s => `
              <tr style="border-bottom: 1px solid var(--border-subtle);">
                <td style="padding: 0.5rem; font-weight: 600; color: var(--text-primary);">${s.scenario_name}</td>
                <td style="padding: 0.5rem; text-transform: capitalize; color: var(--text-secondary);">${s.category}</td>
                <td style="padding: 0.5rem; font-weight: 600; color: ${s.percentage_change < 0 ? 'var(--accent-emerald)' : 'var(--status-high)'};">
                  ${s.percentage_change > 0 ? '+' : ''}${s.percentage_change}%
                </td>
                <td style="padding: 0.5rem; color: var(--text-secondary);">${s.baseline_liters} L</td>
                <td style="padding: 0.5rem; font-weight: 600; color: var(--accent-cyan);">${s.scenario_liters} L</td>
                <td style="padding: 0.5rem; color: var(--accent-emerald);">₹${s.estimated_savings_amount}</td>
                <td style="padding: 0.5rem; color: var(--text-muted);">${s.created_at ? s.created_at.substring(0, 10) : 'Recent'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    } catch (err) {
      console.error("Failed to load scenario history:", err);
      histContainer.innerHTML = `
        <div style="text-align: center; padding: 1rem; color: var(--text-muted); font-size: 0.8rem;">
          Unable to retrieve scenario history.
        </div>
      `;
    }
  }

  // Initial load of scenario history
  loadScenarioHistory();

  // Bind Calculator form
  const calcForm = document.getElementById("calc-form");
  if (calcForm) {
    calcForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const baseline = parseFloat(document.getElementById("calc-baseline").value);
      const pct = parseFloat(document.getElementById("calc-pct").value);
      const rate = parseFloat(document.getElementById("calc-rate").value);

      try {
        const res = await apiClient.simulateSavings({
          baseline_consumption: baseline,
          reduction_percentage: pct,
          rate_per_kiloliter: rate,
          period: "daily",
          currency_symbol: "₹"
        });

        const baseEl = document.getElementById("res-base-liters");
        const projEl = document.getElementById("res-proj-liters");
        const redEl = document.getElementById("res-red-pct");
        const savedLitersEl = document.getElementById("res-saved-liters");
        const savedCostEl = document.getElementById("res-saved-cost");
        const annualLitersEl = document.getElementById("res-annual-liters");
        const annualSavingsEl = document.getElementById("res-annual-savings");
        const disclaimerEl = document.getElementById("calc-disclaimer");

        if (baseEl) baseEl.textContent = `${res.baseline_consumption_liters} L`;
        if (projEl) projEl.textContent = `${res.projected_consumption_liters} L`;
        if (redEl) redEl.textContent = `-${res.estimated_percentage_reduction}%`;
        if (savedLitersEl) savedLitersEl.textContent = `${res.estimated_liters_saved} L/d`;
        if (savedCostEl) savedCostEl.textContent = res.estimated_monetary_savings !== null ? `₹${res.estimated_monetary_savings}/d` : "₹0.00/d";
        if (annualLitersEl) annualLitersEl.textContent = `${res.annualized_liters_saved.toLocaleString()} L/yr`;
        if (annualSavingsEl) annualSavingsEl.textContent = res.annualized_monetary_savings !== null ? `₹${res.annualized_monetary_savings.toLocaleString()}/yr` : "₹0.00/yr";
        if (disclaimerEl) disclaimerEl.textContent = res.disclaimer;

        const resCard = document.getElementById("calc-results");
        if (resCard) resCard.classList.remove("hidden");
      } catch (err) {
        console.error("Failed to run savings simulator:", err);
      }
    });
  }

  // Bind Scenario form
  const scenForm = document.getElementById("scenario-form");
  if (scenForm) {
    scenForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("scen-name").value;
      const category = document.getElementById("scen-category").value;
      const pct = parseFloat(document.getElementById("scen-pct").value);
      const save = document.getElementById("scen-save").checked;

      try {
        const res = await apiClient.runScenario({
          user_id: userId,
          scenario_name: name,
          category: category,
          percentage_change: pct,
          save_to_history: save
        });

        document.getElementById("scen-explanation").textContent = res.explanation;
        document.getElementById("scen-base-val").textContent = `${res.baseline_daily_liters} L`;
        document.getElementById("scen-sim-val").textContent = `${res.scenario_daily_liters} L`;
        document.getElementById("scen-impact-val").textContent = `₹${res.monthly_financial_impact}`;
        document.getElementById("scenario-results").classList.remove("hidden");

        if (save) {
          await loadScenarioHistory();
        }
      } catch (err) {
        console.error("Failed to run what-if scenario:", err);
      }
    });
  }
}
