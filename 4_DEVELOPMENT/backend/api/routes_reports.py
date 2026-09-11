"""
Smart Water Usage Advisor - Reports Blueprint
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/api/routes_reports.py

Provides:
- GET /api/reports/water.csv (Feature 9: RFC 4180 CSV Export)
- GET /api/reports/water.pdf (Feature 9: Executive HTML / Print-Ready Report)
"""

from flask import Blueprint, Response, g, request
from backend.api.middleware import auth_required, meter_access_required
from backend.services.report_service import ReportService

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")
_report_service = ReportService()


@reports_bp.route("/water.csv", methods=["GET"])
@auth_required
@meter_access_required
def export_water_csv():
    """
    Feature 9: Export RFC 4180-compliant CSV report with telemetry and synthetic data disclosure.
    """
    req_uid = request.args.get("user_id")
    user_id = int(req_uid) if req_uid and g.current_user.get("user_type") == "municipal" else g.current_user["user_id"]
    csv_content = _report_service.generate_csv_report(user_id=user_id)

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=water_audit_report_user_{user_id}.csv",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )


@reports_bp.route("/water.html", methods=["GET"])
@reports_bp.route("/water.pdf", methods=["GET"])
@auth_required
@meter_access_required
def export_water_report():
    """
    Feature 9: Export print-ready executive summary report (HTML / print-to-PDF optimized).
    """
    req_uid = request.args.get("user_id")
    user_id = int(req_uid) if req_uid and g.current_user.get("user_type") == "municipal" else g.current_user["user_id"]
    html_content = _report_service.generate_executive_html_report(user_id=user_id)

    return Response(
        html_content,
        mimetype="text/html",
        headers={
            "Content-Type": "text/html; charset=utf-8"
        }
    )
