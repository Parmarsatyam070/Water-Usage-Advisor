"""
Smart Water Usage Advisor - Forecasting Model Architecture & Wrapper
Implements candidate estimators:
- Random Forest Regressor
- Gradient Boosting Regressor
- Ridge Regression (linear baseline)
Provides hyperparameter tuning on validation set, feature importance extraction,
model serialization with joblib, and multi-step 7-day forward forecasting.
"""

import os
import json
import time
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from preprocessing import ALL_PREDICTOR_FEATURES
from evaluation import compute_regression_metrics

class WaterConsumptionForecaster:
    """
    Production-capable forecasting wrapper for water consumption.
    """

    def __init__(self, algorithm: str = "gradient_boosting", model_params: Optional[Dict[str, Any]] = None):
        self.algorithm = algorithm
        self.model_params = model_params or {}
        self.feature_names = ALL_PREDICTOR_FEATURES
        self.model = None
        self.model_version = "forecasting-v1.0"
        self.training_metadata = {}
        self._init_model()

    def _init_model(self):
        if self.algorithm == "random_forest":
            default_params = {
                "n_estimators": 100,
                "max_depth": 8,
                "min_samples_split": 4,
                "min_samples_leaf": 2,
                "random_state": 42
            }
            default_params.update(self.model_params)
            self.model = RandomForestRegressor(**default_params)

        elif self.algorithm == "gradient_boosting":
            default_params = {
                "n_estimators": 100,
                "learning_rate": 0.08,
                "max_depth": 4,
                "min_samples_split": 4,
                "random_state": 42
            }
            default_params.update(self.model_params)
            self.model = GradientBoostingRegressor(**default_params)

        elif self.algorithm == "ridge":
            default_params = {"alpha": 10.0, "random_state": 42}
            default_params.update(self.model_params)
            self.model = Ridge(**default_params)
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")

    def train(self, X_train: pd.DataFrame, y_train: np.ndarray) -> float:
        """
        Trains the model on chronological historical training data.
        Returns training duration in seconds.
        """
        X = X_train[self.feature_names]
        start_time = time.time()
        self.model.fit(X, y_train)
        duration = round(time.time() - start_time, 4)

        self.training_metadata = {
            "algorithm": self.algorithm,
            "model_version": self.model_version,
            "training_samples": len(X_train),
            "training_duration_sec": duration,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "hyperparameters": self.model.get_params()
        }
        return duration

    def predict(self, X_input: pd.DataFrame) -> np.ndarray:
        """
        Generates predictions for feature matrix X_input.
        Enforces non-negativity constraint.
        """
        if self.model is None:
            raise RuntimeError("Model is not trained. Call train() or load() first.")

        X = X_input[self.feature_names]
        preds = self.model.predict(X)
        return np.maximum(0.0, np.round(preds, 3))

    def get_feature_importance(self) -> Dict[str, float]:
        """
        Returns feature importances for tree-based models sorted in descending order.
        Note: Indicates model association, not causal proof.
        """
        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
            feat_imp = {feat: float(round(imp, 4)) for feat, imp in zip(self.feature_names, importances)}
            return dict(sorted(feat_imp.items(), key=lambda item: item[1], reverse=True))
        return {}

    def save(self, output_dir: str = "5_AI_COMPONENTS/predictive_models/models"):
        """
        Serializes model artifact and metadata to disk.
        """
        os.makedirs(output_dir, exist_ok=True)
        model_path = os.path.join(output_dir, "forecasting_model.joblib")
        meta_path = os.path.join(output_dir, "model_metadata.json")
        feat_path = os.path.join(output_dir, "feature_names.json")

        joblib.dump(self.model, model_path)

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self.training_metadata, f, indent=2)

        with open(feat_path, "w", encoding="utf-8") as f:
            json.dump(self.feature_names, f, indent=2)

        print(f"Model serialized successfully to {model_path}")

    def load(self, model_dir: str = "5_AI_COMPONENTS/predictive_models/models"):
        """
        Loads serialized model artifact from disk.
        """
        model_path = os.path.join(model_dir, "forecasting_model.joblib")
        meta_path = os.path.join(model_dir, "model_metadata.json")

        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")

        self.model = joblib.load(model_path)

        if os.path.isfile(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.training_metadata = json.load(f)

        print(f"Model loaded successfully from {model_path}")

def tune_candidate_models(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Compares candidate models and simple hyperparameter variants on validation data.
    Never touches the final test set.
    """
    X_train = train_df[ALL_PREDICTOR_FEATURES]
    y_train = train_df["daily_consumption_liters"].values

    X_val = val_df[ALL_PREDICTOR_FEATURES]
    y_val = val_df["daily_consumption_liters"].values

    candidates = [
        ("Random Forest (default)", "random_forest", {"n_estimators": 100, "max_depth": 6}),
        ("Random Forest (tuned)", "random_forest", {"n_estimators": 150, "max_depth": 8, "min_samples_leaf": 2}),
        ("Gradient Boosting (default)", "gradient_boosting", {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3}),
        ("Gradient Boosting (tuned)", "gradient_boosting", {"n_estimators": 120, "learning_rate": 0.08, "max_depth": 4}),
        ("Ridge Regression", "ridge", {"alpha": 10.0})
    ]

    results = []
    best_candidate = None
    lowest_val_mape = float("inf")

    for name, algo, params in candidates:
        clf = WaterConsumptionForecaster(algorithm=algo, model_params=params)
        fit_time = clf.train(X_train, y_train)

        start_inf = time.time()
        preds_val = clf.predict(X_val)
        inf_time = round(time.time() - start_inf, 4)

        metrics = compute_regression_metrics(y_val, preds_val)
        metrics["training_time_sec"] = fit_time
        metrics["inference_time_sec"] = inf_time
        metrics["candidate_name"] = name
        metrics["algorithm"] = algo
        metrics["parameters"] = params

        results.append(metrics)

        if metrics["MAPE"] < lowest_val_mape:
            lowest_val_mape = metrics["MAPE"]
            best_candidate = (name, algo, params, metrics)

    return {
        "all_candidates": results,
        "best_candidate": best_candidate
    }
