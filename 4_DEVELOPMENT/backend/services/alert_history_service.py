"""
Smart Water Usage Advisor - Alert History & Resolution Service
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/services/alert_history_service.py

Manages alert history, workflow lifecycle (NEW -> ACKNOWLEDGED -> RESOLVED / DISMISSED),
and resolution tracking with strict BOLA/IDOR and role boundaries.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy import text
from backend.database.db_config import create_db_engine
from backend.dashboard_data_service import get_data_service


class AlertHistoryService:
    """
    Service for querying, acknowledging, and resolving system water alerts and anomaly incidents.
    Enforces object-level ownership and role-based permissions.
    """

    VALID_STATUSES = ["NEW", "ACKNOWLEDGED", "RESOLVED", "DISMISSED"]

    def __init__(self, db_engine=None, data_service=None):
        self._db_engine = db_engine
        self.data_service = data_service or get_data_service()

    def _get_engine(self):
        if self._db_engine is None:
            try:
                self._db_engine = create_db_engine()
            except Exception:
                self._db_engine = None
        return self._db_engine

    def ensure_seeded_alerts(self, user_id: int):
        """Seeds initial alerts from anomaly incident data if table is empty for user."""
        eng = self._get_engine()
        if not eng:
            return

        try:
            with eng.connect() as conn:
                count = conn.execute(
                    text("SELECT COUNT(*) FROM alerts WHERE user_id = :u_id"),
                    {"u_id": user_id}
                ).scalar() or 0

            if count == 0:
                anomalies_dto = self.data_service.get_anomalies(user_id)
                incidents = anomalies_dto.get("incidents", [])
                if incidents:
                    with eng.begin() as conn:
                        for idx, inc in enumerate(incidents):
                            status = "NEW" if idx < 2 else "RESOLVED"
                            conn.execute(text("""
                                INSERT INTO alerts (
                                    user_id, alert_type, title, message, severity,
                                    is_read, status, action_url, resolution_note
                                ) VALUES (
                                    :u_id, :a_type, :title, :msg, :sev,
                                    :read, :st, :url, :note
                                )
                            """), {
                                "u_id": user_id,
                                "a_type": inc.get("anomaly_type", "leak"),
                                "title": f"Anomaly Detected: {inc.get('anomaly_type', 'flow').title()}",
                                "msg": inc.get("explanation", "Abnormal flow rate detected relative to diurnal baseline."),
                                "sev": inc.get("severity", "medium"),
                                "read": status != "NEW",
                                "st": status,
                                "url": "/dashboard#anomalies",
                                "note": "Resolved during scheduled maintenance" if status == "RESOLVED" else None
                            })
        except Exception:
            pass

    def get_alert_history(
        self,
        user_id: int,
        user_role: str = "household",
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Retrieves alert history for the authenticated user or district-wide for municipal role.
        """
        self.ensure_seeded_alerts(user_id)
        eng = self._get_engine()

        norm_status = status.upper().strip() if status and status.upper().strip() != "ALL" else None
        if norm_status and norm_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status filter '{status}'. Allowed: ALL, {', '.join(self.VALID_STATUSES)}")

        if not eng:
            # Fallback memory response if DB is not available
            anomalies_dto = self.data_service.get_anomalies(user_id)
            mock_alerts = []
            for idx, inc in enumerate(anomalies_dto.get("incidents", [])):
                st = "NEW" if idx < 2 else "RESOLVED"
                if norm_status and st != norm_status:
                    continue
                mock_alerts.append({
                    "alert_id": idx + 1,
                    "user_id": user_id,
                    "alert_type": inc.get("anomaly_type", "leak"),
                    "title": f"Anomaly Detected: {inc.get('anomaly_type', 'flow').title()}",
                    "message": inc.get("explanation", ""),
                    "severity": inc.get("severity", "medium"),
                    "status": st,
                    "is_read": st != "NEW",
                    "created_timestamp": inc.get("timestamp"),
                    "acknowledged_timestamp": None,
                    "resolved_timestamp": inc.get("timestamp") if st == "RESOLVED" else None,
                    "resolution_note": "Resolved baseline adjustment" if st == "RESOLVED" else None
                })
            return {
                "alerts": mock_alerts[offset:offset + limit],
                "total": len(mock_alerts),
                "counts": {
                    "new": len([a for a in mock_alerts if a["status"] == "NEW"]),
                    "acknowledged": len([a for a in mock_alerts if a["status"] == "ACKNOWLEDGED"]),
                    "resolved": len([a for a in mock_alerts if a["status"] == "RESOLVED"]),
                    "dismissed": len([a for a in mock_alerts if a["status"] == "DISMISSED"])
                }
            }

        try:
            with eng.connect() as conn:
                # Base query conditions
                conditions = []
                params: Dict[str, Any] = {"lim": limit, "off": offset}

                if user_role != "municipal":
                    conditions.append("user_id = :u_id")
                    params["u_id"] = user_id

                if norm_status:
                    conditions.append("status = :status")
                    params["status"] = norm_status

                where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

                query = f"""
                    SELECT alert_id, user_id, alert_type, title, message, severity,
                           is_read, created_timestamp, status, acknowledged_timestamp,
                           resolved_timestamp, resolution_note, resolved_by_user_id
                    FROM alerts
                    {where_clause}
                    ORDER BY created_timestamp DESC
                    LIMIT :lim OFFSET :off
                """
                rows = conn.execute(text(query), params).fetchall()

                # Get counts summary
                count_where = "WHERE user_id = :u_id" if user_role != "municipal" else ""
                c_params = {"u_id": user_id} if user_role != "municipal" else {}
                count_rows = conn.execute(text(f"""
                    SELECT status, COUNT(*) FROM alerts
                    {count_where}
                    GROUP BY status
                """), c_params).fetchall()

                status_counts = {"NEW": 0, "ACKNOWLEDGED": 0, "RESOLVED": 0, "DISMISSED": 0}
                total_count = 0
                for st, count in count_rows:
                    if st in status_counts:
                        status_counts[st] = count
                    total_count += count

                alerts_list = []
                for r in rows:
                    alerts_list.append({
                        "alert_id": r[0],
                        "user_id": r[1],
                        "alert_type": r[2],
                        "title": r[3],
                        "message": r[4],
                        "severity": r[5],
                        "is_read": bool(r[6]),
                        "created_timestamp": str(r[7]) if r[7] else None,
                        "status": r[8] or "NEW",
                        "acknowledged_timestamp": str(r[9]) if r[9] else None,
                        "resolved_timestamp": str(r[10]) if r[10] else None,
                        "resolution_note": r[11],
                        "resolved_by_user_id": r[12]
                    })

                return {
                    "alerts": alerts_list,
                    "total": total_count,
                    "counts": {
                        "new": status_counts["NEW"],
                        "acknowledged": status_counts["ACKNOWLEDGED"],
                        "resolved": status_counts["RESOLVED"],
                        "dismissed": status_counts["DISMISSED"]
                    }
                }
        except Exception as ex:
            return {"alerts": [], "total": 0, "counts": {"new": 0, "acknowledged": 0, "resolved": 0, "dismissed": 0}, "error": str(ex)}

    def update_alert_status(
        self,
        alert_id: int,
        new_status: str,
        user_id: int,
        user_role: str = "household",
        resolution_note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Updates the status of an alert with validation and ownership defense.

        Raises:
            ValueError: If status is invalid or alert not found.
            PermissionError: If user attempts to modify another user's alert without municipal permissions.
        """
        norm_status = new_status.upper().strip() if new_status else ""
        if norm_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{new_status}'. Allowed: {', '.join(self.VALID_STATUSES)}")

        eng = self._get_engine()
        now_utc = datetime.now(timezone.utc)

        if not eng:
            # Memory mock return: validate that alert_id corresponds to a valid mock incident
            anomalies_dto = self.data_service.get_anomalies(user_id)
            incidents = anomalies_dto.get("incidents", [])
            valid_ids = [idx + 1 for idx in range(len(incidents))]
            if alert_id not in valid_ids:
                raise ValueError(f"Alert with ID {alert_id} not found.")

            return {
                "alert_id": alert_id,
                "status": norm_status,
                "resolution_note": resolution_note,
                "updated": True
            }

        with eng.begin() as conn:
            # Check existence and ownership
            row = conn.execute(
                text("SELECT user_id, status FROM alerts WHERE alert_id = :a_id"),
                {"a_id": alert_id}
            ).fetchone()

            if not row:
                raise ValueError(f"Alert with ID {alert_id} not found.")

            owner_id, current_status = row[0], row[1]
            if user_role != "municipal" and owner_id != user_id:
                raise PermissionError(f"Access denied: You do not own alert {alert_id}.")

            ack_time = now_utc if norm_status == "ACKNOWLEDGED" else None
            res_time = now_utc if norm_status in ("RESOLVED", "DISMISSED") else None
            res_by = user_id if norm_status in ("RESOLVED", "DISMISSED") else None

            conn.execute(text("""
                UPDATE alerts
                SET status = :st,
                    is_read = TRUE,
                    resolution_note = COALESCE(:note, resolution_note),
                    acknowledged_timestamp = CASE WHEN :ack IS NOT NULL THEN :ack ELSE acknowledged_timestamp END,
                    resolved_timestamp = CASE WHEN :res IS NOT NULL THEN :res ELSE resolved_timestamp END,
                    resolved_by_user_id = CASE WHEN :res_by IS NOT NULL THEN :res_by ELSE resolved_by_user_id END
                WHERE alert_id = :a_id
            """), {
                "st": norm_status,
                "note": resolution_note,
                "ack": ack_time,
                "res": res_time,
                "res_by": res_by,
                "a_id": alert_id
            })

            # Fetch updated record
            updated_row = conn.execute(
                text("SELECT alert_id, user_id, status, resolution_note, acknowledged_timestamp, resolved_timestamp FROM alerts WHERE alert_id = :a_id"),
                {"a_id": alert_id}
            ).fetchone()

            return {
                "alert_id": updated_row[0],
                "user_id": updated_row[1],
                "status": updated_row[2],
                "resolution_note": updated_row[3],
                "acknowledged_timestamp": str(updated_row[4]) if updated_row[4] else None,
                "resolved_timestamp": str(updated_row[5]) if updated_row[5] else None,
                "success": True
            }
