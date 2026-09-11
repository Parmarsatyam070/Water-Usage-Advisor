"""
Smart Water Usage Advisor - Domain Rule-Based Leak Signatures (Calibrated)
Location: 5_AI_COMPONENTS/anomaly_detection/leak_rules.py

Implements domain-grounded physical water leak detection rules:
1. Continuous Low-Flow Leak (Minimum Night Flow - MNF analysis)
2. Sudden Burst Pipe / Catastrophic Surge (profile-relative thresholds)
3. Unusual Nocturnal Pattern / Off-Hour Commercial Irrigation
4. Sensor Inactivity / Extended Low-Consumption Period
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional

class RuleBasedLeakDetector:
    """
    Expert system for detecting physical water leakage patterns.
    Calibrated against historical smart meter consumption envelopes:
    - Meter 1 (Single-family): normal max ~55 L/hr, night median 0 L/hr
    - Meter 2 (Multi-family): normal max ~151 L/hr, daytime active median ~40 L/hr
    - Meter 3 (Commercial): normal night flow < 15 L/hr, daytime peak ~225 L/hr
    """

    def __init__(
        self,
        night_flow_threshold_liters: float = 8.0,
        burst_threshold_liters: float = 300.0,
        nocturnal_pattern_threshold: float = 80.0
    ):
        self.night_flow_threshold_liters = night_flow_threshold_liters
        self.burst_threshold_liters = burst_threshold_liters
        self.nocturnal_pattern_threshold = nocturnal_pattern_threshold

    def evaluate_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies calibrated domain rules across time series.
        Operates per meter in chronological order without future data leakage.
        """
        data = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(data["timestamp"]):
            data["timestamp"] = pd.to_datetime(data["timestamp"])

        data = data.sort_values(by=["meter_id", "timestamp"]).reset_index(drop=True)
        data["hour"] = data["timestamp"].dt.hour
        data["date"] = data["timestamp"].dt.date

        data["rule_leak"] = False
        data["rule_surge"] = False
        data["rule_unusual_pattern"] = False
        data["rule_low"] = False

        for m_id in data["meter_id"].unique():
            m_idx = data["meter_id"] == m_id
            m_data = data.loc[m_idx].copy()
            date_groups = m_data.groupby("date")

            # -------------------------------------------------------------
            # 1. Rule 1: Continuous Low-Flow Leak (Minimum Night Flow)
            # -------------------------------------------------------------
            # In residential households, hours 01:00-04:00 are typically inactive (< 2L).
            # If night flow stays persistently above threshold (> 8L) for 3+ night hours,
            # it indicates a non-closing valve, flapper leak, or continuous pipe fissure.
            if m_id in [1, 2]:
                leak_dates = set()
                for d, g in date_groups:
                    night_hours = g[g["hour"].isin([1, 2, 3, 4])]["hourly_consumption_liters"]
                    if len(night_hours) >= 3 and (night_hours > self.night_flow_threshold_liters).all():
                        leak_dates.add(d)

                data.loc[m_idx & data["date"].isin(leak_dates), "rule_leak"] = True

            # -------------------------------------------------------------
            # 2. Rule 2: Sudden Burst Pipe / Catastrophic Surge
            # -------------------------------------------------------------
            # Profile-relative extreme volumetric spike:
            # - Meter 1 (normal max 55 L/hr): burst > 200 L/hr
            # - Meter 2 (normal max 151 L/hr): burst > 250 L/hr
            # - Meter 3 (normal max 225 L/hr): burst > 350 L/hr
            profile_burst_thresholds = {1: 200.0, 2: 250.0, 3: 350.0}
            thresh = profile_burst_thresholds.get(m_id, self.burst_threshold_liters)
            is_burst = (m_data["hourly_consumption_liters"] > thresh)

            data.loc[is_burst[is_burst].index, "rule_surge"] = True

            # -------------------------------------------------------------
            # 3. Rule 3: Unusual Nocturnal Pattern / Irrigation Runaway
            # -------------------------------------------------------------
            # In commercial facilities (Meter 3) or residential, nocturnal usage
            # in hours 00:00-03:00 suddenly surges > 80 L/hr above historical baseline (normal < 15L).
            if m_id == 3:
                is_nocturnal_spike = (
                    (m_data["hour"].isin([0, 1, 2, 3])) &
                    (m_data["hourly_consumption_liters"] > self.nocturnal_pattern_threshold)
                )
                data.loc[m_idx & is_nocturnal_spike, "rule_unusual_pattern"] = True

            # -------------------------------------------------------------
            # 4. Rule 4: Sensor Inactivity / Vacant Period (Abnormal Low)
            # -------------------------------------------------------------
            # If an active facility shows continuous near-zero consumption (< 2L)
            # across daytime active hours (08:00 to 20:00) on consecutive days.
            if m_id in [1, 2]:
                low_dates = set()
                for d, g in date_groups:
                    daytime_hours = g[g["hour"].between(8, 20)]["hourly_consumption_liters"]
                    if len(daytime_hours) >= 10 and (daytime_hours < 2.0).all():
                        low_dates.add(d)

                data.loc[m_idx & data["date"].isin(low_dates), "rule_low"] = True

        data["rule_any_flag"] = (
            data["rule_leak"] |
            data["rule_surge"] |
            data["rule_unusual_pattern"] |
            data["rule_low"]
        )

        return data
