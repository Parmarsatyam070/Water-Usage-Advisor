"""
Smart Water Usage Advisor - Severity Classification & Explanation Generator
Location: 5_AI_COMPONENTS/anomaly_detection/severity.py

Implements evidence-grounded severity classification and interpretable evidence descriptions:
- Severity levels strictly conform to authoritative PostgreSQL schema:
  CHECK (severity IN ('critical', 'high', 'medium', 'low'))
- Explanations describe observed telemetry facts without unverified causal assertions.
"""

from typing import Dict, Any, Optional

def classify_severity(
    anomaly_type: str,
    deviation_liters: float,
    consumption_value: float,
    anomaly_score: float
) -> str:
    """
    Classifies anomaly severity based on volume deviation, absolute consumption, and score:
    - critical: Sudden catastrophic surges (> 200L deviation) or extreme risk
    - high: Continuous leaks (> 10L/hr sustained) or major off-hour spikes (> 100L)
    - medium: Moderate baseline deviations or extended unexpected inactivity
    - low: Minor statistical anomalies or initial low-confidence deviations
    """
    if anomaly_type == "surge" or deviation_liters > 200.0 or consumption_value > 300.0:
        return "critical"

    if anomaly_type == "leak":
        if deviation_liters > 15.0 or consumption_value > 15.0:
            return "high"
        return "medium"

    if anomaly_type == "unusual_pattern":
        if deviation_liters > 100.0:
            return "high"
        return "medium"

    if anomaly_type == "low":
        return "medium"

    # Default statistical escalation based on normalized anomaly score
    if anomaly_score >= 0.90:
        return "high"
    elif anomaly_score >= 0.75:
        return "medium"
    else:
        return "low"

def generate_evidence_explanation(
    anomaly_type: str,
    consumption_value: float,
    expected_baseline: float,
    deviation_liters: float,
    hour: int,
    meter_id: int
) -> str:
    """
    Formulates a factual, human-readable explanation of the anomaly evidence.
    Refrains from asserting unconfirmed physical causes (e.g. says 'possible burst' rather than 'burst confirmed').
    """
    if anomaly_type == "surge":
        return (
            f"Sudden extreme volumetric surge of {consumption_value:.1f} L/hr at {hour:02d}:00 "
            f"(+{deviation_liters:.1f} L above expected baseline of {expected_baseline:.1f} L/hr). "
            "Pattern indicates a probable sudden pipe rupture or major fixture failure."
        )

    if anomaly_type == "leak":
        return (
            f"Persistent non-zero flow of {consumption_value:.1f} L/hr observed during nocturnal low-demand hours "
            f"at {hour:02d}:00 (normal night baseline is {expected_baseline:.1f} L/hr). "
            "Sustained non-zero nocturnal flow is a classic signature of a continuous fixture or toilet flapper leak."
        )

    if anomaly_type == "unusual_pattern":
        return (
            f"Uncharacteristic off-hours consumption spike of {consumption_value:.1f} L/hr at {hour:02d}:00 "
            f"(+{deviation_liters:.1f} L above baseline of {expected_baseline:.1f} L/hr). "
            "Consistent with unapproved nocturnal irrigation or automated cooling loop cycling."
        )

    if anomaly_type == "low":
        return (
            f"Unusually prolonged near-zero consumption of {consumption_value:.1f} L/hr during expected diurnal active period "
            f"at {hour:02d}:00 (typical daytime baseline is {expected_baseline:.1f} L/hr). "
            "Indicates potential property vacancy, meter malfunction, or supply interruption."
        )

    return (
        f"Statistical anomaly detected at {hour:02d}:00: observed {consumption_value:.1f} L/hr vs. "
        f"expected {expected_baseline:.1f} L/hr (deviation: {deviation_liters:+.1f} L/hr)."
    )
