/**
 * Smart Water Usage Advisor - Personalized Recommendations Component
 * Location: 4_DEVELOPMENT/frontend/js/components/recommendations.js
 */

export function renderRecommendations(recsData, onConsultAdvisorCallback) {
  if (!recsData) return;

  const totalChipEl = document.getElementById("val-total-potential");
  const listEl = document.getElementById("recommendations-list");
  const currency = recsData.currency_symbol || "₹";

  if (totalChipEl) {
    totalChipEl.textContent = `Potential: -${recsData.total_potential_savings_lpd} L/d (${currency}${recsData.total_potential_financial}/mo)`;
  }

  if (listEl) {
    const recs = recsData.recommendations || [];
    if (recs.length === 0) {
      listEl.innerHTML = `
        <div style="padding: 1.5rem; text-align: center; color: var(--text-secondary); font-size: 0.85rem;">
          No active conservation actions needed. You are currently operating at peak efficiency!
        </div>
      `;
      return;
    }

    listEl.innerHTML = recs.map((r, idx) => `
      <article class="rec-card" role="article" id="rec-card-${idx}">
        <div class="rec-header">
          <h3 class="rec-title">${escapeHtml(r.title)}</h3>
          <span class="savings-chip">+${r.estimated_savings_liters_day} L/d</span>
        </div>
        <p class="rec-desc">${escapeHtml(r.description)}</p>
        <div class="rec-footer">
          <div class="rec-badges">
            <span class="mini-badge" style="text-transform: capitalize;">⭐ ${r.priority}</span>
            <span class="mini-badge" style="text-transform: capitalize;">⚙️ ${r.difficulty}</span>
            <span class="mini-badge" style="color: var(--accent-emerald);">💰 ${currency}${r.monthly_financial_savings}/mo</span>
          </div>
          <button class="btn-rec-action" data-title="${escapeHtml(r.title)}" data-idx="${idx}">
            Ask AI Advisor
          </button>
        </div>
      </article>
    `).join("");

    // Wire up Ask AI Advisor buttons
    listEl.querySelectorAll(".btn-rec-action").forEach(btn => {
      btn.addEventListener("click", () => {
        const title = btn.getAttribute("data-title");
        if (onConsultAdvisorCallback) {
          onConsultAdvisorCallback(`Can you guide me step-by-step on how to: ${title}?`);
        }
      });
    });
  }
}

function escapeHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
