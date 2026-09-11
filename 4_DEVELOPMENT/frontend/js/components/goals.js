/**
 * Smart Water Usage Advisor - Conservation Goal Tracker Component
 * Location: 4_DEVELOPMENT/frontend/js/components/goals.js
 */

export function renderGoals(goalsData) {
  if (!goalsData) return;

  const daysEl = document.getElementById("val-days-remaining");
  const currentEl = document.getElementById("val-goal-current");
  const targetEl = document.getElementById("val-goal-target-vol");
  const barEl = document.getElementById("goal-progress-bar");
  const trackEl = document.querySelector(".progress-track");

  if (daysEl) {
    daysEl.textContent = `${goalsData.days_remaining_in_cycle || 18} Days Left in Cycle`;
  }

  if (currentEl) {
    currentEl.textContent = `${goalsData.current_volume_lpd} L/d`;
  }

  if (targetEl) {
    targetEl.textContent = `${goalsData.target_volume_lpd} L/d (-${goalsData.target_reduction_pct}%)`;
  }

  if (barEl) {
    const progress = Math.min(100, Math.max(0, Math.round(goalsData.achieved_progress_pct || 0)));
    barEl.style.width = `${progress}%`;
    if (trackEl) {
      trackEl.setAttribute("aria-valuenow", String(progress));
    }
  }
}
