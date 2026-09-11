"""
Smart Water Usage Advisor - Backend Services Package
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/services/__init__.py
"""

from backend.services.auth_service import AuthService, get_auth_service
from backend.services.water_savings_service import WaterSavingsService
from backend.services.scenario_service import ScenarioAnalysisService
from backend.services.sustainability_score_service import SustainabilityScoreService
from backend.services.alert_history_service import AlertHistoryService
from backend.services.sdg6_service import SDG6Service
from backend.services.goal_recommendation_service import GoalRecommendationService
from backend.services.water_insights_service import WaterInsightsService
from backend.services.water_budget_service import WaterBudgetService
from backend.services.report_service import ReportService
from backend.services.system_monitoring_service import SystemMonitoringService

__all__ = [
    "AuthService",
    "get_auth_service",
    "WaterSavingsService",
    "ScenarioAnalysisService",
    "SustainabilityScoreService",
    "AlertHistoryService",
    "SDG6Service",
    "GoalRecommendationService",
    "WaterInsightsService",
    "WaterBudgetService",
    "ReportService",
    "SystemMonitoringService",
]
