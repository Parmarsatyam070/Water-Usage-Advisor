/**
 * Smart Water Usage Advisor - Alert History & Resolution Manager Component
 * Phase 7 - Advanced Water Intelligence & Impact Features
 * Location: 4_DEVELOPMENT/frontend/js/components/alerts_manager.js
 */

export async function renderAlertsManager(apiClient, getUserId, currentFilter = "ALL") {
  const container = document.getElementById("alerts-manager-container");
  if (!container) return;

  const userId = getUserId();
  let historyData = null;

  try {
    historyData = await apiClient.fetchAlertHistory(userId, currentFilter);
  } catch (err) {
    console.error("Failed to load alert history:", err);
    return;
  }

  const counts = historyData.counts || { new: 0, acknowledged: 0, resolved: 0, dismissed: 0 };

  container.innerHTML = `
    <div class="card" style="padding: 1.5rem;">
      <div class="section-header" style="margin-bottom: 1.25rem;">
        <div>
          <h3 class="section-title"><span>🚨</span> Incident & Alert Lifecycle Manager</h3>
          <p style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.2rem;">
            Acknowledge and track remediation for active leaks and flow anomalies.
          </p>
        </div>

        <!-- Filter Controls -->
        <div class="chart-controls" id="alert-filter-controls">
          <button class="btn-chart-toggle ${currentFilter === 'ALL' ? 'active' : ''}" data-filter="ALL">All (${historyData.total})</button>
          <button class="btn-chart-toggle ${currentFilter === 'NEW' ? 'active' : ''}" data-filter="NEW">New (${counts.new})</button>
          <button class="btn-chart-toggle ${currentFilter === 'ACKNOWLEDGED' ? 'active' : ''}" data-filter="ACKNOWLEDGED">Ack (${counts.acknowledged})</button>
          <button class="btn-chart-toggle ${currentFilter === 'RESOLVED' ? 'active' : ''}" data-filter="RESOLVED">Resolved (${counts.resolved})</button>
        </div>
      </div>

      <!-- Alerts Stream -->
      <div style="display: flex; flex-direction: column; gap: 0.85rem;">
        ${historyData.alerts.length === 0 ? `
          <div style="text-align: center; padding: 2rem; color: var(--text-muted); font-size: 0.85rem;">
            No alerts found matching filter '${currentFilter}'.
          </div>
        ` : historyData.alerts.map(a => {
          const statusBadgeColor = a.status === 'NEW' ? 'var(--status-critical)' : (a.status === 'ACKNOWLEDGED' ? 'var(--accent-amber)' : 'var(--accent-emerald)');
          return `
            <div style="background: var(--bg-secondary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 1rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
              <div style="flex: 1;">
                <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.3rem;">
                  <span class="severity-pill severity-${a.severity}">${a.severity.toUpperCase()}</span>
                  <span class="severity-pill" style="background: ${statusBadgeColor}22; color: ${statusBadgeColor};">${a.status}</span>
                  <span style="font-size: 0.75rem; color: var(--text-muted);">${a.created_timestamp ? a.created_timestamp.substring(0, 16) : ''}</span>
                </div>
                <div style="font-size: 0.9rem; font-weight: 700; color: var(--text-primary);">${a.title}</div>
                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.2rem;">${a.message}</div>
                ${a.resolution_note ? `
                  <div style="font-size: 0.75rem; color: var(--accent-cyan); margin-top: 0.35rem; background: rgba(6, 182, 212, 0.08); padding: 0.3rem 0.6rem; border-radius: var(--radius-sm);">
                    <strong>Resolution Note:</strong> ${a.resolution_note}
                  </div>
                ` : ''}
              </div>

              <div style="display: flex; gap: 0.4rem; flex-direction: column;">
                ${a.status === 'NEW' ? `
                  <button class="btn-chart-toggle btn-ack-alert" data-id="${a.alert_id}" style="font-size: 0.75rem; padding: 0.3rem 0.6rem;">
                    Acknowledge
                  </button>
                ` : ''}
                ${a.status !== 'RESOLVED' && a.status !== 'DISMISSED' ? `
                  <button class="btn-chart-toggle active btn-res-alert" data-id="${a.alert_id}" style="font-size: 0.75rem; padding: 0.3rem 0.6rem;">
                    Resolve
                  </button>
                ` : ''}
              </div>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  `;

  // Bind filter buttons
  const filterBtns = container.querySelectorAll("#alert-filter-controls button");
  filterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const f = btn.getAttribute("data-filter");
      renderAlertsManager(apiClient, getUserId, f);
    });
  });

  // Bind Acknowledge buttons
  const ackBtns = container.querySelectorAll(".btn-ack-alert");
  ackBtns.forEach(btn => {
    btn.addEventListener("click", async () => {
      const aid = parseInt(btn.getAttribute("data-id"), 10);
      try {
        await apiClient.updateAlertStatus(aid, "ACKNOWLEDGED");
        await renderAlertsManager(apiClient, getUserId, currentFilter);
      } catch (err) {
        console.error("Failed to acknowledge alert:", err);
      }
    });
  });

  // Bind Resolve buttons
  const resBtns = container.querySelectorAll(".btn-res-alert");
  resBtns.forEach(btn => {
    btn.addEventListener("click", async () => {
      const aid = parseInt(btn.getAttribute("data-id"), 10);
      const note = prompt("Enter resolution details (e.g. 'Replaced toilet flapper valve'):") || "Issue resolved by user";
      try {
        await apiClient.updateAlertStatus(aid, "RESOLVED", note);
        await renderAlertsManager(apiClient, getUserId, currentFilter);
      } catch (err) {
        console.error("Failed to resolve alert:", err);
      }
    });
  });
}
