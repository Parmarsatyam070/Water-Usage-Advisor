/**
 * Smart Water Usage Advisor - Admin System Monitoring Component
 * Phase 7 - Advanced Water Intelligence & Impact Features
 * Location: 4_DEVELOPMENT/frontend/js/components/admin_monitor.js
 */

export async function renderAdminMonitor(apiClient, getUserId) {
  const container = document.getElementById("admin-container");
  if (!container) return;

  const isAuthenticated = apiClient && apiClient.isAuthenticated();

  if (!isAuthenticated) {
    container.innerHTML = `
      <div class="card" style="padding: 2rem; text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🔒</div>
        <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">
          Authentication Required
        </h3>
        <p style="font-size: 0.85rem; color: var(--text-secondary); max-width: 480px; margin: 0 auto 1.25rem;">
          Please sign in with municipal credentials (e.g. Elena Rostova - Municipal Operator) to inspect district-level administration and system health telemetry.
        </p>
        <button type="button" class="btn-chart-toggle active btn-admin-login" style="padding: 0.5rem 1.25rem; font-size: 0.85rem;">
          Sign In to Access Admin Monitor
        </button>
      </div>
    `;
    const loginBtn = container.querySelector(".btn-admin-login");
    if (loginBtn) {
      loginBtn.addEventListener("click", () => {
        if (window.smartWaterApp && window.smartWaterApp.openAuthModal) {
          window.smartWaterApp.openAuthModal();
        }
      });
    }
    return;
  }

  let summary = null;

  try {
    summary = await apiClient.fetchSystemSummary();
  } catch (err) {
    const is403 = err.message && (err.message.includes("403") || err.message.includes("Forbidden") || err.message.includes("role"));
    const is401 = err.message && err.message.includes("401");

    if (is401) {
      container.innerHTML = `
        <div class="card" style="padding: 2rem; text-align: center;">
          <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🔒</div>
          <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">
            Session Expired
          </h3>
          <p style="font-size: 0.85rem; color: var(--text-secondary); max-width: 480px; margin: 0 auto 1.25rem;">
            Your session has expired. Please log in again with municipal privileges.
          </p>
          <button type="button" class="btn-chart-toggle active btn-admin-relogin" style="padding: 0.5rem 1.25rem; font-size: 0.85rem;">
            Log In Again
          </button>
        </div>
      `;
      const reloginBtn = container.querySelector(".btn-admin-relogin");
      if (reloginBtn) {
        reloginBtn.addEventListener("click", () => {
          if (window.smartWaterApp && window.smartWaterApp.openAuthModal) {
            window.smartWaterApp.openAuthModal();
          }
        });
      }
      return;
    }

    container.innerHTML = `
      <div class="card" style="padding: 2rem; text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🛡️</div>
        <div style="font-size: 1.2rem; font-weight: 700; color: var(--status-critical); margin-bottom: 0.5rem;">
          Access Denied: Municipal Role Required (HTTP 403)
        </div>
        <p style="font-size: 0.85rem; color: var(--text-secondary); max-width: 520px; margin: 0 auto 1.5rem; line-height: 1.5;">
          This operational monitoring dashboard is restricted to authorized municipal operators and district administrators. Your current account does not hold the <code>municipal</code> or <code>admin</code> role.
        </p>
        <div style="display: flex; gap: 0.75rem; justify-content: center; align-items: center;">
          <button type="button" id="btn-switch-to-municipal" class="btn-chart-toggle active" style="padding: 0.5rem 1rem; font-size: 0.85rem;">
            Switch to Elena Rostova (Municipal)
          </button>
        </div>
      </div>
    `;

    const switchBtn = document.getElementById("btn-switch-to-municipal");
    if (switchBtn) {
      switchBtn.addEventListener("click", async () => {
        switchBtn.disabled = true;
        switchBtn.textContent = "Switching Role...";
        const syncResult = await apiClient.syncPersona(3);
        if (syncResult) {
          const personaSelect = document.getElementById("persona-select");
          if (personaSelect) personaSelect.value = "3";
          if (window.smartWaterApp) {
            window.smartWaterApp.currentUserId = 3;
            window.smartWaterApp.updateAuthUI();
          }
          await renderAdminMonitor(apiClient, () => 3);
        } else {
          // If in production mode where demo token is disabled, open auth modal with Elena's email
          if (window.smartWaterApp && window.smartWaterApp.openAuthModal) {
            window.smartWaterApp.openAuthModal();
            const emailInput = document.getElementById("input-auth-email");
            if (emailInput) emailInput.value = "elena.rostova@smartwater.internal";
          }
        }
      });
    }
    return;
  }

  container.innerHTML = `
    <div class="card" style="padding: 1.5rem;">
      <div class="section-header" style="margin-bottom: 1.25rem;">
        <h3 class="section-title"><span>⚙️</span> District Administration & System Health</h3>
        <span class="severity-pill severity-low" style="font-weight: 700;">SYSTEM ${summary.system_status.toUpperCase()}</span>
      </div>

      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
        <div style="background: var(--bg-secondary); padding: 0.85rem; border-radius: var(--radius-md);">
          <div style="font-size: 0.75rem; color: var(--text-muted);">Uptime</div>
          <div style="font-size: 1.2rem; font-weight: 700; color: var(--text-primary); margin-top: 0.2rem;">${summary.uptime_seconds}s</div>
        </div>
        <div style="background: var(--bg-secondary); padding: 0.85rem; border-radius: var(--radius-md);">
          <div style="font-size: 0.75rem; color: var(--text-muted);">Database Engine</div>
          <div style="font-size: 1.2rem; font-weight: 700; color: var(--accent-cyan); margin-top: 0.2rem;">${summary.database.engine.toUpperCase()}</div>
        </div>
        <div style="background: var(--bg-secondary); padding: 0.85rem; border-radius: var(--radius-md);">
          <div style="font-size: 0.75rem; color: var(--text-muted);">Active Incidents</div>
          <div style="font-size: 1.2rem; font-weight: 700; color: var(--accent-amber); margin-top: 0.2rem;">${summary.active_alerts_summary.total_active}</div>
        </div>
        <div style="background: var(--bg-secondary); padding: 0.85rem; border-radius: var(--radius-md);">
          <div style="font-size: 0.75rem; color: var(--text-muted);">Security State</div>
          <div style="font-size: 1.2rem; font-weight: 700; color: var(--accent-emerald); margin-top: 0.2rem;">ENFORCED</div>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem;">

        <!-- Table Record Counts -->
        <div style="background: var(--bg-secondary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 1rem;">
          <h4 style="font-size: 0.9rem; margin-bottom: 0.75rem; color: var(--text-primary);">Authoritative Database Tables</h4>
          <table style="width: 100%; font-size: 0.8rem; border-collapse: collapse;">
            ${Object.entries(summary.database.table_record_counts).map(([tbl, cnt]) => `
              <tr style="border-bottom: 1px solid var(--border-subtle);">
                <td style="padding: 0.4rem 0; color: var(--text-secondary);">${tbl}</td>
                <td style="padding: 0.4rem 0; text-align: right; font-weight: 700;">${cnt} records</td>
              </tr>
            `).join('')}
          </table>
        </div>

        <!-- AI Component Status -->
        <div style="background: var(--bg-secondary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 1rem;">
          <h4 style="font-size: 0.9rem; margin-bottom: 0.75rem; color: var(--text-primary);">AI Component Registry</h4>
          <div style="display: flex; flex-direction: column; gap: 0.6rem; font-size: 0.8rem;">
            ${Object.entries(summary.ai_models).map(([k, m]) => `
              <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.4rem;">
                <div>
                  <div style="color: var(--text-primary); font-weight: 600;">${m.name}</div>
                  <div style="font-size: 0.7rem; color: var(--text-muted);">${m.status}</div>
                </div>
                <span class="severity-pill severity-${m.available ? 'low' : 'critical'}">
                  ${m.available ? 'AVAILABLE' : 'OFFLINE'}
                </span>
              </div>
            `).join('')}
          </div>
        </div>

      </div>
    </div>
  `;
}
