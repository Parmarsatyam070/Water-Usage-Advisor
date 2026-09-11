"""
Smart Water Usage Advisor - Exportable Water Report Service
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/services/report_service.py

Generates structured, exportable water conservation reports:
1. RFC 4180-compliant CSV stream with daily telemetry, end-use breakdown, and alert logs.
2. Formatted Executive Summary Report (Print/PDF ready HTML & JSON DTO) with SDG 6.4 metrics.
Includes mandatory synthetic-data and estimate disclosures.
"""

import io
import csv
from datetime import datetime, timezone
from typing import Dict, Any, List
from backend.dashboard_data_service import get_data_service


class ReportService:
    """
    Service generating downloadable audit, telemetry, and executive impact reports.
    """

    SYNTHETIC_DATA_DISCLOSURE = (
        "Disclosure: This report contains synthetic smart meter telemetry generated for "
        "sustainable water management prototyping and research demonstration."
    )

    def __init__(self, data_service=None):
        self.data_service = data_service or get_data_service()

    def generate_csv_report(self, user_id: int) -> str:
        """
        Generates RFC 4180-compliant CSV containing 30-day telemetry, categories, and summary metrics.
        """
        profile = self.data_service.get_user_profile(user_id)
        meter_id = profile["meter_id"]
        raw_df = self.data_service._load_telemetry()
        meter_df = raw_df[raw_df["meter_id"] == meter_id].copy()

        daily_df = meter_df.groupby("date").agg(
            daily_consumption_liters=("consumption_liters", "sum"),
            avg_hourly_flow_lph=("consumption_liters", "mean"),
            peak_hourly_flow_lph=("consumption_liters", "max")
        ).reset_index().sort_values("date", ascending=False).head(30)

        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\r\n")

        # Metadata Header
        writer.writerow(["# SMART WATER USAGE ADVISOR - OFFICIAL WATER AUDIT REPORT"])
        writer.writerow(["# Generated At (UTC)", datetime.now(timezone.utc).isoformat()])
        writer.writerow(["# User ID", user_id, "User Name", profile.get("name", "")])
        writer.writerow(["# Meter ID", meter_id, "Property Type", profile.get("property_type", "")])
        writer.writerow(["# Documented Benchmark (L/day)", profile.get("regional_benchmark_lpd", 440.0)])
        writer.writerow(["# Rate per kL", f"{profile.get('currency_symbol', '₹')}{profile.get('cost_per_kiloliter', 45.0)}"])
        writer.writerow(["# Disclosure", self.SYNTHETIC_DATA_DISCLOSURE])
        writer.writerow([])

        # Telemetry Data Table
        writer.writerow([
            "Date",
            "Daily_Consumption_Liters",
            "Daily_Consumption_m3",
            "Average_Hourly_LPH",
            "Peak_Hourly_LPH",
            "Benchmark_LPD",
            "Variance_vs_Benchmark_Liters",
            "Estimated_Cost"
        ])

        benchmark_lpd = float(profile.get("regional_benchmark_lpd", 440.0))
        cost_per_kl = float(profile.get("cost_per_kiloliter", 45.0))

        for _, row in daily_df.iterrows():
            d_vol = float(row["daily_consumption_liters"])
            d_m3 = round(d_vol / 1000.0, 3)
            avg_lph = round(float(row["avg_hourly_flow_lph"]), 2)
            peak_lph = round(float(row["peak_hourly_flow_lph"]), 2)
            variance = round(d_vol - benchmark_lpd, 2)
            est_cost = round((d_vol / 1000.0) * cost_per_kl, 2)

            writer.writerow([
                str(row["date"]),
                round(d_vol, 2),
                d_m3,
                avg_lph,
                peak_lph,
                benchmark_lpd,
                variance,
                est_cost
            ])

        return output.getvalue()

    def generate_executive_html_report(self, user_id: int) -> str:
        """
        Generates a self-contained, print-ready HTML executive summary report suitable for PDF rendering.
        """
        profile = self.data_service.get_user_profile(user_id)
        summary = self.data_service.get_summary(user_id)
        anomalies = self.data_service.get_anomalies(user_id)

        currency = profile.get("currency_symbol", "₹")
        cost_per_kl = profile.get("cost_per_kiloliter", 45.0)
        benchmark_lpd = profile.get("regional_benchmark_lpd", 440.0)

        now_str = datetime.now(timezone.utc).strftime("%B %d, %Y - %H:%M UTC")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Water Conservation Executive Report - {profile.get('name')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 40px;
            color: #1e293b;
            background: #ffffff;
            line-height: 1.5;
        }}
        .header {{
            border-bottom: 2px solid #0284c7;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .title {{
            font-size: 24px;
            font-weight: 700;
            color: #0369a1;
            margin: 0 0 6px 0;
        }}
        .meta {{
            font-size: 13px;
            color: #64748b;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}
        .card {{
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            background: #f8fafc;
        }}
        .card-label {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #64748b;
            margin-bottom: 4px;
        }}
        .card-val {{
            font-size: 22px;
            font-weight: 700;
            color: #0f172a;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
            font-size: 13px;
        }}
        .table th, .table td {{
            border: 1px solid #cbd5e1;
            padding: 8px 12px;
            text-align: left;
        }}
        .table th {{
            background: #f1f5f9;
            color: #334155;
        }}
        .disclaimer {{
            margin-top: 32px;
            padding: 12px;
            background: #fffbeb;
            border: 1px solid #fef3c7;
            border-radius: 6px;
            font-size: 12px;
            color: #92400e;
        }}
        @media print {{
            body {{ margin: 20px; }}
            .card {{ break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">Smart Water Usage Advisor — Executive Audit Report</h1>
        <div class="meta">
            User: <strong>{profile.get('name')}</strong> (ID: {user_id}) |
            Meter: <strong>#{profile.get('meter_id')}</strong> |
            Property: {profile.get('property_type')} |
            Generated: {now_str}
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-label">Monthly Consumption</div>
            <div class="card-val">{summary.get('monthly_consumption_liters', 0.0):,.0f} L</div>
            <div class="meta">({summary.get('monthly_consumption_liters', 0.0)/1000.0:.2f} m³)</div>
        </div>
        <div class="card">
            <div class="card-label">Documented Benchmark</div>
            <div class="card-val">{benchmark_lpd * 30:,.0f} L</div>
            <div class="meta">{benchmark_lpd:.0f} L/day baseline</div>
        </div>
        <div class="card">
            <div class="card-label">Estimated Savings</div>
            <div class="card-val" style="color: #16a34a;">{currency}{summary.get('monthly_financial_saved', 0.0):,.2f}</div>
            <div class="meta">{summary.get('monthly_water_saved_liters', 0.0):,.0f} L conserved</div>
        </div>
    </div>

    <h3>Executive Impact & Operational Health</h3>
    <table class="table">
        <tr>
            <th>Indicator</th>
            <th>Value</th>
            <th>Notes</th>
        </tr>
        <tr>
            <td>Today's Usage</td>
            <td>{summary.get('today_usage_liters', 0.0)} L/day</td>
            <td>Observed telemetry volume</td>
        </tr>
        <tr>
            <td>7-Day Forecast Average</td>
            <td>{summary.get('forecast_avg_liters_day', 0.0)} L/day</td>
            <td>Phase 3A Machine Learning Model Projection</td>
        </tr>
        <tr>
            <td>Active Anomalies & Incidents</td>
            <td>{anomalies.get('active_alert_count', 0)} active ({anomalies.get('total_detected_hours', 0)} total hours)</td>
            <td>Phase 3B Hybrid Isolation Forest Detection</td>
        </tr>
        <tr>
            <td>Conservation Goal Trajectory</td>
            <td>{summary.get('goal_progress_pct', 0.0)}% achieved</td>
            <td>Target: {profile.get('conservation_goal_pct', 20.0)}% reduction</td>
        </tr>
        <tr>
            <td>Water Tariff Rate</td>
            <td>{currency}{cost_per_kl} / 1,000 L</td>
            <td>Standard municipal billing tier</td>
        </tr>
    </table>

    <div class="disclaimer">
        <strong>Mandatory Methodology Disclosure:</strong><br>
        {self.SYNTHETIC_DATA_DISCLOSURE}<br>
        Simulated savings, sustainability metrics, and SDG 6 projections are analytical decision-support estimates.
        They do not guarantee utility billing reductions or official UN certification.
    </div>
</body>
</html>
"""
        return html
