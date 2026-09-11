"""
Smart Water Usage Advisor - Water Intelligence Blueprint
Phase 7 - Advanced Water Intelligence & Impact Features
Location: 4_DEVELOPMENT/backend/api/routes_water_intelligence.py

Provides:
- POST /api/water/savings/simulate (Feature 1: Water Savings Simulator)
- POST /api/water/scenarios (Feature 2: What-If Scenario Analysis)
- GET  /api/water/scenarios/history (Feature 2: Saved Scenario History)
- GET  /api/water/sustainability-score (Feature 3: 0-100 Sustainability Score)
- GET  /api/water/insights (Feature 7: Trend & Pattern Insights)
- GET  /api/water/budget (Feature 8: Water Budget Tracker)
- POST /api/water/budget (Feature 8: Set Water Budget)
- PUT  /api/water/budget (Feature 8: Update Water Budget)
"""

from flask import Blueprint, request, jsonify, g
from backend.api.middleware import auth_required, meter_access_required
from backend.services.water_savings_service import WaterSavingsService
from backend.services.scenario_service import ScenarioAnalysisService
from backend.services.sustainability_score_service import SustainabilityScoreService
from backend.services.water_insights_service import WaterInsightsService
from backend.services.water_budget_service import WaterBudgetService

water_bp = Blueprint("water_intelligence", __name__, url_prefix="/api/water")

_scenario_service = ScenarioAnalysisService()
_score_service = SustainabilityScoreService()
_insights_service = WaterInsightsService()
_budget_service = WaterBudgetService()


@water_bp.route("/savings/simulate", methods=["POST"])
@auth_required
def simulate_savings():
    """
    Feature 1: Deterministic Water Conservation Savings Simulator.
    Calculates volumetric, financial, and annualized projected savings.
    """
    body = request.get_json(silent=True) or {}
    baseline = body.get("baseline_consumption")
    if baseline is None:
        return jsonify({
            "error": "Missing required parameter 'baseline_consumption'.",
            "error_code": "INVALID_PARAMETER",
            "status_code": 400
        }), 400

    try:
        baseline = float(baseline)
        reduction_pct = float(body.get("reduction_percentage")) if body.get("reduction_percentage") is not None else None
        target_vol = float(body.get("target_consumption")) if body.get("target_consumption") is not None else None
        rate = float(body.get("rate_per_kiloliter")) if body.get("rate_per_kiloliter") is not None else None
        period = body.get("period", "monthly")
        currency = body.get("currency_symbol", "₹")

        res = WaterSavingsService.simulate_savings(
            baseline_consumption=baseline,
            reduction_percentage=reduction_pct,
            target_consumption=target_vol,
            rate_per_kiloliter=rate,
            period=period,
            currency_symbol=currency
        )
        return jsonify(res), 200
    except ValueError as ve:
        return jsonify({
            "error": str(ve),
            "error_code": "INVALID_PARAMETER",
            "status_code": 400
        }), 400


@water_bp.route("/scenarios", methods=["POST"])
@auth_required
@meter_access_required
def run_scenario():
    """
    Feature 2: What-If Scenario Analysis on disaggregated end-uses.
    """
    user_id = g.current_user["user_id"]
    body = request.get_json(silent=True) or {}

    name = body.get("scenario_name", "Hypothetical Scenario")
    category = body.get("category", "all")
    pct_change = body.get("percentage_change")
    save = bool(body.get("save_to_history", False))

    if pct_change is None:
        return jsonify({
            "error": "Missing required parameter 'percentage_change'.",
            "error_code": "INVALID_PARAMETER",
            "status_code": 400
        }), 400

    try:
        pct_change = float(pct_change)
        res = _scenario_service.run_scenario(
            user_id=user_id,
            scenario_name=name,
            category=category,
            percentage_change=pct_change,
            save_to_history=save
        )
        return jsonify(res), 200
    except ValueError as ve:
        return jsonify({
            "error": str(ve),
            "error_code": "INVALID_PARAMETER",
            "status_code": 400
        }), 400


@water_bp.route("/scenarios/history", methods=["GET"])
@auth_required
@meter_access_required
def get_scenario_history():
    """
    Feature 2: Retrieve previously saved scenario history for the authenticated user.
    """
    user_id = int(request.args.get("user_id", g.current_user["user_id"]))
    limit = int(request.args.get("limit", 10))
    history = _scenario_service.get_scenario_history(user_id=user_id, limit=limit)
    return jsonify({"user_id": user_id, "count": len(history), "scenarios": history}), 200


@water_bp.route("/sustainability-score", methods=["GET"])
@auth_required
@meter_access_required
def get_sustainability_score():
    """
    Feature 3: 0-100 Water Usage Sustainability Score.
    """
    user_id = int(request.args.get("user_id", g.current_user["user_id"]))
    res = _score_service.calculate_score(user_id=user_id)
    return jsonify(res), 200


@water_bp.route("/insights", methods=["GET"])
@auth_required
@meter_access_required
def get_insights():
    """
    Feature 7: Trend & Pattern Statistical Insights.
    """
    user_id = int(request.args.get("user_id", g.current_user["user_id"]))
    res = _insights_service.get_insights(user_id=user_id)
    return jsonify(res), 200


@water_bp.route("/budget", methods=["GET"])
@auth_required
@meter_access_required
def get_budget():
    """
    Feature 8: Active Water Budget status and overshoot warning.
    """
    user_id = int(request.args.get("user_id", g.current_user["user_id"]))
    res = _budget_service.get_active_budget(user_id=user_id)
    return jsonify(res), 200


@water_bp.route("/budget", methods=["POST", "PUT"])
@auth_required
@meter_access_required
def set_budget():
    """
    Feature 8: Create or update active Water Budget.
    """
    body = request.get_json(silent=True) or {}
    user_id = int(body.get("user_id", g.current_user["user_id"]))

    period = body.get("period", "monthly")
    target_liters = body.get("target_liters")
    cost_budget = body.get("cost_budget")
    duration_days = body.get("duration_days")

    if target_liters is None:
        return jsonify({
            "error": "Missing required parameter 'target_liters'.",
            "error_code": "INVALID_PARAMETER",
            "status_code": 400
        }), 400

    try:
        target_liters = float(target_liters)
        cost_budget = float(cost_budget) if cost_budget is not None else None
        duration_days = int(duration_days) if duration_days is not None else None

        res = _budget_service.set_budget(
            user_id=user_id,
            period=period,
            target_liters=target_liters,
            cost_budget=cost_budget,
            duration_days=duration_days
        )
        return jsonify(res), 200
    except ValueError as ve:
        return jsonify({
            "error": str(ve),
            "error_code": "INVALID_PARAMETER",
            "status_code": 400
        }), 400
