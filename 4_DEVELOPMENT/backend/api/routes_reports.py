"""
Smart Water Usage Advisor - Reports Blueprint
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/api/routes_reports.py

Provides:
- GET /api/reports/water.csv (Feature 9: RFC 4180 CSV Export)
- GET /api/reports/water.pdf (Feature 9: Executive HTML / Print-Ready Report)
"""

from flask import Blueprint, Response, g
from backend.api.middleware import auth_required
from backend.services.report_service import ReportService

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")
_report_service = ReportService()


@reports_bp.route("/water.csv", methods=["GET"])
@auth_required
def export_water_csv():
    """
    Feature 9: Export RFC 4180-compliant CSV report with telemetry and synthetic data disclosure.
    """
    user_id = g.current_user["user_id"]
    csv_content = _report_service.generate_csv_report(user_id=user_id)

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=water_audit_report_user_{user_id}.csv",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )


@reports_bp.route("/water.pdf", methods=["GET"])
@auth_required
def export_water_pdf():
    """
    Feature 9: Export print-ready executive summary report (PDF/print optimized).
    """
    user_id = g.current_user["user_id"]
    html_content = _report_service.generate_executive_html_report(user_id=user_id)

    return Response(
        html_content,
        mimetype="text/html",
        headers={
            "Content-Type": "text/html; charset=utf-8"
        }
    )
