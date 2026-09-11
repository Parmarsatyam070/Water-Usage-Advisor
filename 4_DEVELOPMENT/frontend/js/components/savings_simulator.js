/**
 * Smart Water Usage Advisor - Savings Simulator & What-If Scenario Component
 * Phase 7 - Advanced Water Intelligence & Impact Features
 * Location: 4_DEVELOPMENT/frontend/js/components/savings_simulator.js
 */

export function renderSavingsSimulator(apiClient, getUserId) {
  const container = document.getElementById("simulator-container");
  if (!container) return;

  container.innerHTML = `
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
            <input type="number" id="calc-baseline" value="440" min="0" step="10" required class="chat-input" style="width: 100%;">
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
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; text-align: center;">
            <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: var(--radius-md);">
              <div style="font-size: 0.75rem; color: var(--text-muted);">Daily Saved</div>
              <div id="res-saved-liters" style="font-size: 1.25rem; font-weight: 700; color: var(--accent-emerald);">-- L</div>
            </div>
            <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: var(--radius-md);">
              <div style="font-size: 0.75rem; color: var(--text-muted);">Annualized Savings</div>
              <div id="res-annual-savings" style="font-size: 1.25rem; font-weight: 700; color: var(--accent-cyan);">₹--</div>
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
  `;

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

        document.getElementById("res-saved-liters").textContent = `${res.estimated_liters_saved} L/d`;
        document.getElementById("res-annual-savings").textContent = res.annualized_monetary_savings !== null ? `₹${res.annualized_monetary_savings}` : `${res.annualized_liters_saved} L/yr`;
        document.getElementById("calc-disclaimer").textContent = res.disclaimer;
        document.getElementById("calc-results").classList.remove("hidden");
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
          user_id: getUserId(),
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
      } catch (err) {
        console.error("Failed to run what-if scenario:", err);
      }
    });
  }
}
