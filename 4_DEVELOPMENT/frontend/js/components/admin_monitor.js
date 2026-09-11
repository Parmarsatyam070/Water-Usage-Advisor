/**
 * Smart Water Usage Advisor - Admin System Monitoring Component
 * Phase 7 - Advanced Water Intelligence & Impact Features
 * Location: 4_DEVELOPMENT/frontend/js/components/admin_monitor.js
 */

export async function renderAdminMonitor(apiClient, getUserId) {
  const container = document.getElementById("admin-container");
  if (!container) return;

  const userId = getUserId();
  let summary = null;

  try {
    summary = await apiClient.fetchSystemSummary();
  } catch (err) {
    container.innerHTML = `
      <div class="card" style="padding: 1.5rem; text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔒</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: var(--status-critical); margin-bottom: 0.25rem;">
          Access Denied: Municipal Role Required
        </div>
        <div style="font-size: 0.8rem; color: var(--text-secondary);">
          This operational monitoring dashboard is restricted to authorized municipal operators and district administrators.
          Select Persona 3 (Elena Rostova - Municipal) from the top profile switcher to evaluate administrative telemetry.
        </div>
      </div>
    `;
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
