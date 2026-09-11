"""
Smart Water Usage Advisor - Admin Monitoring Blueprint
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/api/routes_admin.py

Provides:
- GET /api/admin/system-summary (Feature 10: Admin System Monitoring)

Protected strictly with @auth_required and @roles_required('municipal', 'admin').
Returns HTTP 403 Forbidden immediately for household and institution roles.
"""

from flask import Blueprint, jsonify
from backend.api.middleware import auth_required, roles_required
from backend.services.system_monitoring_service import SystemMonitoringService

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
_system_service = SystemMonitoringService()


@admin_bp.route("/system-summary", methods=["GET"])
@auth_required
@roles_required("municipal", "admin")
def get_system_summary():
    """
    Feature 10: System-wide operational monitoring summary.
    Restricted to Municipal / Admin roles. Zero secrets or passwords exposed.
    """
    summary = _system_service.get_system_summary()
    return jsonify(summary), 200
