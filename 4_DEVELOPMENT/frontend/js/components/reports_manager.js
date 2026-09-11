/**
 * Smart Water Usage Advisor - Reports & Exports Component
 * Phase 7 - Advanced Water Intelligence & Impact Features
 * Location: 4_DEVELOPMENT/frontend/js/components/reports_manager.js
 */

export function renderReportsManager(apiClient, getUserId) {
  const container = document.getElementById("reports-container");
  if (!container) return;

  const userId = getUserId();
  const csvUrl = apiClient.getReportCsvUrl(userId);
  const pdfUrl = apiClient.getReportPdfUrl(userId);

  container.innerHTML = `
    <div class="card" style="padding: 1.5rem;">
      <div class="section-header" style="margin-bottom: 1.25rem;">
        <h3 class="section-title"><span>📄</span> Audit Reports & Data Exports</h3>
        <span class="sdg-badge">RFC 4180 Compliant</span>
      </div>

      <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1.5rem;">
        Export complete 30-day historical water consumption telemetry, financial breakdowns, and executive summaries for municipal filing or billing reconciliation.
      </p>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.5rem;">

        <!-- CSV Export Card -->
        <div style="background: var(--bg-secondary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 1.25rem;">
          <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.35rem;">
            📊 Telemetry Audit Log (CSV)
          </div>
          <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;">
            Raw daily volumetric consumption, benchmark variances, and flow intensities formatted for spreadsheet analysis.
          </div>
          <a href="${csvUrl}" download class="btn-chart-toggle active" style="display: inline-block; text-decoration: none; padding: 0.5rem 1rem; font-size: 0.8rem;">
            ⬇️ Download CSV Log
          </a>
        </div>

        <!-- Executive PDF Report Card -->
        <div style="background: var(--bg-secondary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 1.25rem;">
          <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.35rem;">
            📑 Executive Audit Report (Print / PDF)
          </div>
          <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;">
            Official printable executive brief featuring high-level KPI cards, SDG 6.4 indicators, and model attribution notes.
          </div>
          <a href="${pdfUrl}" target="_blank" class="btn-chart-toggle active" style="display: inline-block; text-decoration: none; padding: 0.5rem 1rem; font-size: 0.8rem;">
            🖨️ View & Print Executive Brief
          </a>
        </div>

      </div>

      <div style="font-size: 0.725rem; color: var(--text-muted); border-top: 1px solid var(--border-subtle); padding-top: 0.75rem;">
        ℹ️ Disclosure: Exported datasets include synthetic demonstration telemetry generated for sustainable water management prototyping and research evaluation.
      </div>
    </div>
  `;
}
