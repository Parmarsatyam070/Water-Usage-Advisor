/**
 * Smart Water Usage Advisor - Anomaly & Leak Alerts Component
 * Location: 4_DEVELOPMENT/frontend/js/components/alerts.js
 */

export function renderAlerts(anomaliesData, onDiagnoseCallback) {
  if (!anomaliesData) return;

  const bannerEl = document.getElementById("active-alert-banner");
  const bannerTitleEl = document.getElementById("alert-banner-title");
  const bannerMsgEl = document.getElementById("alert-banner-message");
  const bannerDiagnoseBtn = document.getElementById("btn-banner-diagnose");
  const bannerDismissBtn = document.getElementById("btn-banner-dismiss");
  const activeBadgeEl = document.getElementById("badge-active-incidents");
  const listEl = document.getElementById("anomaly-list");

  const incidents = anomaliesData.incidents || [];
  const activeCount = anomaliesData.active_alert_count || 0;

  // 1. Update Active Alert Badge
  if (activeBadgeEl) {
    activeBadgeEl.textContent = `${activeCount} Active ${activeCount === 1 ? "Alert" : "Alerts"}`;
    activeBadgeEl.className = `severity-pill ${activeCount > 0 ? "severity-critical" : "severity-low"}`;
  }

  // 2. Top Alert Banner
  if (bannerEl) {
    if (anomaliesData.has_critical_alert || activeCount > 0) {
      bannerEl.classList.remove("hidden");
      const primary = anomaliesData.primary_alert || incidents[0];
      if (primary) {
        if (bannerTitleEl) bannerTitleEl.textContent = `Active Alert [${primary.severity.toUpperCase()}]:`;
        if (bannerMsgEl) bannerMsgEl.textContent = `${primary.anomaly_type.toUpperCase()} - ${primary.explanation}`;

        if (bannerDiagnoseBtn) {
          bannerDiagnoseBtn.onclick = () => {
            if (onDiagnoseCallback) {
              onDiagnoseCallback(`I see an active alert: ${primary.explanation}. How should I diagnose and fix this?`);
            }
          };
        }
      }
    } else {
      bannerEl.classList.add("hidden");
    }

    if (bannerDismissBtn) {
      bannerDismissBtn.onclick = () => bannerEl.classList.add("hidden");
    }
  }

  // 3. Render Incident List
  if (listEl) {
    if (incidents.length === 0) {
      listEl.innerHTML = `
        <div style="padding: 1.5rem; text-align: center; color: var(--text-secondary); font-size: 0.85rem;">
          ✅ No active anomalies detected. Smart meter flow is conforming strictly to learned diurnal baselines.
        </div>
      `;
      return;
    }

    listEl.innerHTML = incidents.map(inc => `
      <article class="anomaly-item" role="article">
        <div class="anomaly-item-header">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span class="severity-pill severity-${inc.severity.toLowerCase()}">${inc.severity}</span>
            <strong style="font-size: 0.875rem;">${formatAnomalyTitle(inc.anomaly_type)}</strong>
          </div>
          <span style="font-size: 0.725rem; color: var(--text-muted);">${formatTimestamp(inc.timestamp)}</span>
        </div>
        <div class="anomaly-desc">
          ${escapeHtml(inc.explanation)}
        </div>
        <div class="anomaly-action-callout">
          <span>🛠️</span>
          <span><strong>Action:</strong> ${escapeHtml(inc.recommended_action)}</span>
        </div>
      </article>
    `).join("");
  }
}

function formatAnomalyTitle(type) {
  switch (type) {
    case "leak": return "Continuous Night Leak";
    case "surge": return "Pipe Burst / Surge Event";
    case "unusual_pattern": return "Nocturnal Usage Anomaly";
    case "low": return "Extended Inactivity / Blockage";
    default: return "Hydraulic Flow Anomaly";
  }
}

function formatTimestamp(ts) {
  if (!ts) return "";
  try {
    const d = new Date(ts);
    return d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  } catch {
    return ts;
  }
}

function escapeHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
