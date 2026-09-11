"""
Smart Water Usage Advisor - Machine Learning Model Interface Wrapper
Location: 4_DEVELOPMENT/ml_models.py

Provides the canonical development interface for predictive consumption forecasting:
- train_model()
- evaluate_model()
- predict()
- save_model()
- load_model()

Wraps the authoritative forecasting engine in 5_AI_COMPONENTS/predictive_models.
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, Union

# Ensure 5_AI_COMPONENTS/predictive_models is on python path
AI_MODULE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "5_AI_COMPONENTS", "predictive_models"))
if AI_MODULE_DIR not in sys.path:
    sys.path.insert(0, AI_MODULE_DIR)

from forecasting_model import WaterConsumptionForecaster
from preprocessing import (
    aggregate_hourly_to_daily,
    extract_forecasting_features,
    chronological_train_val_test_split,
    ALL_PREDICTOR_FEATURES
)
from evaluation import (
    compute_regression_metrics,
    evaluate_baseline_models,
    generate_model_vs_baseline_comparison,
    evaluate_per_profile
)
from inference import generate_7day_forecast

def train_model(
    data: Union[str, pd.DataFrame],
    algorithm: str = "random_forest",
    model_params: Optional[Dict[str, Any]] = None
) -> Tuple[WaterConsumptionForecaster, Dict[str, Any]]:
    """
    Trains a water consumption forecasting model.
    Accepts either path to telemetry CSV or an existing DataFrame.
    Returns (trained_forecaster_instance, training_metadata).
    """
    if isinstance(data, str):
        if not os.path.isfile(data):
            raise FileNotFoundError(f"Telemetry file not found: {data}")
        hourly_df = pd.read_csv(data)
        daily_df = aggregate_hourly_to_daily(hourly_df)
        featured_df = extract_forecasting_features(daily_df)
    else:
        featured_df = data

    train_df, val_df, test_df = chronological_train_val_test_split(featured_df, val_days=14, test_days=14)
    combined_train = pd.concat([train_df, val_df], ignore_index=True)

    forecaster = WaterConsumptionForecaster(algorithm=algorithm, model_params=model_params)
    fit_duration = forecaster.train(combined_train, combined_train["daily_consumption_liters"].values)

    metadata = {
        "algorithm": algorithm,
        "training_samples": len(combined_train),
        "fit_duration_sec": fit_duration,
        "features": forecaster.feature_names
    }
    return forecaster, metadata

def evaluate_model(
    forecaster: WaterConsumptionForecaster,
    test_data: pd.DataFrame
) -> Dict[str, Any]:
    """
    Evaluates forecaster against test data and benchmarks against Seasonal Naive 7-day baseline.
    Returns regression metrics, baseline comparison, and per-profile disaggregation.
    """
    y_true = test_data["daily_consumption_liters"].values
    y_pred = forecaster.predict(test_data)

    overall_metrics = compute_regression_metrics(y_true, y_pred)
    baselines = evaluate_baseline_models(test_data)
    profile_metrics = evaluate_per_profile(test_data, y_pred)

    predictions_dict = {
        f"{forecaster.algorithm.title()} ({forecaster.model_version})": y_pred
    }
    comparison = generate_model_vs_baseline_comparison(test_data, predictions_dict)

    return {
        "overall_metrics": overall_metrics,
        "baseline_metrics": baselines,
        "profile_metrics": profile_metrics,
        "comparison_table": comparison["markdown_table"],
        "beats_seasonal_naive": overall_metrics["MAPE"] < baselines["seasonal_naive_7d"]["MAPE"]
    }

def predict(
    forecaster: WaterConsumptionForecaster,
    input_data: pd.DataFrame
) -> np.ndarray:
    """
    Generates non-negative daily consumption forecasts for input feature DataFrame.
    """
    return forecaster.predict(input_data)

def save_model(
    forecaster: WaterConsumptionForecaster,
    save_dir: str = "5_AI_COMPONENTS/predictive_models/models"
) -> str:
    """
    Serializes trained model artifact and metadata to disk.
    """
    forecaster.save(save_dir)
    return os.path.abspath(os.path.join(save_dir, "forecasting_model.joblib"))

def load_model(
    model_dir: str = "5_AI_COMPONENTS/predictive_models/models"
) -> WaterConsumptionForecaster:
    """
    Loads serialized forecasting model artifact from disk.
    """
    forecaster = WaterConsumptionForecaster(algorithm="random_forest")
    forecaster.load(model_dir)
    return forecaster

# ==============================================================================
# PHASE 3B: ANOMALY & LEAK DETECTION INTERFACES
# ==============================================================================

import importlib.util

ANOMALY_MODULE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "5_AI_COMPONENTS", "anomaly_detection"))
if ANOMALY_MODULE_DIR not in sys.path:
    sys.path.append(ANOMALY_MODULE_DIR)

from anomaly_detector import HybridWaterAnomalyDetector

# Load anomaly evaluation module cleanly to avoid sys.modules collision with predictive_models.evaluation
_eval_spec = importlib.util.spec_from_file_location("anomaly_eval", os.path.join(ANOMALY_MODULE_DIR, "evaluation.py"))
anomaly_eval = importlib.util.module_from_spec(_eval_spec)
_eval_spec.loader.exec_module(anomaly_eval)

def load_anomaly_detector(
    model_dir: str = "5_AI_COMPONENTS/anomaly_detection/models"
) -> HybridWaterAnomalyDetector:
    """
    Loads serialized hybrid water anomaly detector from disk.
    """
    detector = HybridWaterAnomalyDetector()
    detector.load(model_dir)
    return detector

def detect_anomalies(
    data: Union[str, pd.DataFrame],
    detector: Optional[HybridWaterAnomalyDetector] = None
) -> pd.DataFrame:
    """
    Executes hybrid anomaly detection across smart meter telemetry.
    Accepts telemetry CSV path or DataFrame.
    Returns enriched DataFrame with non-destructive anomaly annotations.
    """
    if isinstance(data, str):
        if not os.path.isfile(data):
            raise FileNotFoundError(f"Telemetry file not found: {data}")
        df = pd.read_csv(data)
    else:
        df = data.copy()

    if detector is None:
        detector = load_anomaly_detector()

    return detector.detect(df)

def evaluate_anomaly_detector(detected_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Evaluates anomaly detector predictions against Phase 2 ground-truth annotations.
    Returns row-level metrics, event-level metrics, per-meter breakdown, and type recall.
    """
    row_met = anomaly_eval.compute_row_level_metrics(
        detected_df["anomaly_ground_truth"],
        detected_df["is_anomaly"]
    )
    event_met = anomaly_eval.evaluate_event_level_detection(detected_df)
    meter_met = anomaly_eval.evaluate_per_meter(detected_df)
    type_met = anomaly_eval.evaluate_per_anomaly_type(detected_df)

    return {
        "row_level": row_met,
        "event_level": event_met,
        "per_meter": meter_met,
        "per_type": type_met,
        "leak_detection_target_achieved": row_met["recall"] >= 0.95
    }

# ==============================================================================
# PHASE 3C: AI WATER CONSERVATION CHATBOT INTERFACES
# ==============================================================================

CHATBOT_MODULE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "5_AI_COMPONENTS", "chatbot"))
if CHATBOT_MODULE_DIR not in sys.path:
    sys.path.append(CHATBOT_MODULE_DIR)

from chatbot import WaterAdvisorChatbot

def load_chatbot(
    telemetry_df: Optional[pd.DataFrame] = None,
    knowledge_json_path: Optional[str] = None
) -> WaterAdvisorChatbot:
    """
    Initializes and returns a configured WaterAdvisorChatbot instance.
    """
    return WaterAdvisorChatbot(
        knowledge_json_path=knowledge_json_path,
        telemetry_df=telemetry_df
    )

def ask_water_advisor(
    user_message: str,
    user_id: int = 1,
    meter_id: Optional[int] = None,
    chatbot: Optional[WaterAdvisorChatbot] = None,
    operational_anomalies_df: Optional[pd.DataFrame] = None,
    forecast_output: Optional[Dict[str, Any]] = None,
    custom_goal: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience wrapper to query the Water Advisor chatbot.
    Returns structured response dictionary.
    """
    bot = chatbot or load_chatbot()
    return bot.chat(
        user_message=user_message,
        user_id=user_id,
        meter_id=meter_id,
        operational_anomalies_df=operational_anomalies_df,
        forecast_output=forecast_output,
        custom_goal=custom_goal
    )

# ==============================================================================
# PHASE 4: DASHBOARD & WEB UI INTERFACES
# ==============================================================================

def get_dashboard_payload(user_id: int = 1) -> Dict[str, Any]:
    """
    Convenience helper retrieving full dashboard DTO payload for a given user.
    """
    from backend.dashboard_data_service import get_data_service
    ds = get_data_service()
    return {
        "summary": ds.get_summary(user_id=user_id),
        "consumption": ds.get_consumption(user_id=user_id),
        "forecast": ds.get_forecast(user_id=user_id),
        "anomalies": ds.get_anomalies(user_id=user_id),
        "recommendations": ds.get_recommendations(user_id=user_id),
        "goals": ds.get_goals(user_id=user_id)
    }



