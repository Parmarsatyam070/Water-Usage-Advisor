/**
 * Smart Water Usage Advisor - Reports & Exports Component
 * Phase 7 - Advanced Water Intelligence & Impact Features
 * Location: 4_DEVELOPMENT/frontend/js/components/reports_manager.js
 */

export function renderReportsManager(apiClient, getUserId) {
  const container = document.getElementById("reports-container");
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
          Please sign in to generate authenticated telemetry audit exports (CSV) and official executive compliance reports (Print / PDF).
        </p>
        <button type="button" class="btn-chart-toggle active btn-reports-login" style="padding: 0.5rem 1.25rem; font-size: 0.85rem;">
          Sign In to Access Reports
        </button>
      </div>
    `;
    const loginBtn = container.querySelector(".btn-reports-login");
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
    <div class="card" style="padding: 1.5rem;">
      <div class="section-header" style="margin-bottom: 1.25rem;">
        <h3 class="section-title"><span>📄</span> Audit Reports & Data Exports</h3>
        <span class="sdg-badge">RFC 4180 Compliant</span>
      </div>

      <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1.5rem;">
        Export complete 30-day historical water consumption telemetry, financial breakdowns, and executive summaries for municipal filing or billing reconciliation.
      </p>

      <div id="reports-status-msg" style="display: none; padding: 0.75rem 1rem; border-radius: var(--radius-md); font-size: 0.825rem; margin-bottom: 1.25rem;"></div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.5rem;">

        <!-- CSV Export Card -->
        <div style="background: var(--bg-secondary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.35rem;">
              📊 Telemetry Audit Log (CSV)
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem; line-height: 1.4;">
              Raw daily volumetric consumption, benchmark variances, and flow intensities formatted for spreadsheet and GIS analysis.
            </div>
          </div>
          <button type="button" id="btn-download-csv" class="btn-chart-toggle active" style="padding: 0.5rem 1rem; font-size: 0.8rem; align-self: flex-start;">
            ⬇️ Download CSV Log
          </button>
        </div>

        <!-- Executive Print/PDF Report Card -->
        <div style="background: var(--bg-secondary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.35rem;">
              📑 Executive Audit Report (Print / PDF Ready)
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem; line-height: 1.4;">
              Official printable executive brief featuring sustainability score breakdown, active budget pacing, SDG 6.4 indicators, and model attribution notes.
            </div>
          </div>
          <button type="button" id="btn-view-print-report" class="btn-chart-toggle active" style="padding: 0.5rem 1rem; font-size: 0.8rem; align-self: flex-start;">
            🖨️ View & Print Executive Report
          </button>
        </div>

      </div>

      <div style="font-size: 0.725rem; color: var(--text-muted); border-top: 1px solid var(--border-subtle); padding-top: 0.75rem;">
        ℹ️ Disclosure: Exported datasets include synthetic demonstration telemetry generated for sustainable water management prototyping and research evaluation.
      </div>
    </div>
  `;

  function showStatus(msg, isSuccess = true) {
    const el = document.getElementById("reports-status-msg");
    if (el) {
      el.textContent = msg;
      el.style.display = "block";
      el.style.background = isSuccess ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)";
      el.style.color = isSuccess ? "var(--accent-emerald)" : "var(--status-critical)";
      el.style.border = `1px solid ${isSuccess ? "var(--accent-emerald)" : "var(--status-critical)"}`;
      setTimeout(() => {
        el.style.display = "none";
      }, 4000);
    }
  }

  // Bind CSV download
  const csvBtn = document.getElementById("btn-download-csv");
  if (csvBtn) {
    csvBtn.addEventListener("click", async () => {
      csvBtn.disabled = true;
      csvBtn.textContent = "Generating CSV...";
      try {
        await apiClient.downloadReportCsv(userId);
        showStatus("✓ Telemetry audit CSV report downloaded successfully.");
      } catch (err) {
        console.error("Failed to download CSV:", err);
        showStatus(`⚠️ Failed to download CSV: ${err.message || 'Error'}`, false);
      } finally {
        csvBtn.disabled = false;
        csvBtn.textContent = "⬇️ Download CSV Log";
      }
    });
  }

  // Bind Print/HTML report
  const printBtn = document.getElementById("btn-view-print-report");
  if (printBtn) {
    printBtn.addEventListener("click", async () => {
      printBtn.disabled = true;
      printBtn.textContent = "Generating Report...";
      try {
        const html = await apiClient.fetchReportHtml(userId);
        const printWindow = window.open("", "_blank");
        if (printWindow) {
          printWindow.document.open();
          printWindow.document.write(html);
          printWindow.document.close();
          showStatus("✓ Executive audit report loaded in new print-ready window.");
        } else {
          showStatus("⚠️ Pop-up blocked. Please allow pop-ups for this site to view the report.", false);
        }
      } catch (err) {
        console.error("Failed to load report HTML:", err);
        showStatus(`⚠️ Failed to generate report: ${err.message || 'Error'}`, false);
      } finally {
        printBtn.disabled = false;
        printBtn.textContent = "🖨️ View & Print Executive Report";
      }
    });
  }
}
