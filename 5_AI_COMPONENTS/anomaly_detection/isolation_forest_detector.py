"""
Smart Water Usage Advisor - Isolation Forest Anomaly Detector
Location: 5_AI_COMPONENTS/anomaly_detection/isolation_forest_detector.py

Implements unsupervised anomaly detection using Isolation Forest:
- Operates on scale-normalized features to prevent commercial meters from dominating residential meters.
- Calibrates contamination parameter from historical training data.
- Outputs continuous normalized anomaly scores in [0.0, 1.0].
- Serializes model artifact via joblib.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from sklearn.ensemble import IsolationForest

ISO_FOREST_FEATURES = [
    "diurnal_zscore",
    "rolling_zscore",
    "ratio_to_baseline",
    "rate_of_change_1h",
    "hour",
    "day_of_week",
    "is_weekend"
]

class IsolationForestAnomalyDetector:
    """
    Unsupervised Isolation Forest detector for smart meter anomalies.
    Trained on normalized deviation and temporal context features.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        contamination: float = 0.035,
        random_state: int = 42,
        features: Optional[List[str]] = None
    ):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.features = features or ISO_FOREST_FEATURES
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state
        )
        self.score_min = -0.5
        self.score_max = 0.5
        self.is_fitted = False

    def fit(self, X_train: pd.DataFrame) -> "IsolationForestAnomalyDetector":
        """
        Fits Isolation Forest on calibration data features.
        Stores decision function boundaries for score normalization.
        """
        X = X_train[self.features].copy().fillna(0.0)
        self.model.fit(X)

        raw_scores = self.model.decision_function(X)
        self.score_min = float(raw_scores.min())
        self.score_max = float(raw_scores.max())
        self.is_fitted = True
        return self

    def compute_anomaly_scores(self, X_input: pd.DataFrame) -> np.ndarray:
        """
        Computes normalized continuous anomaly scores in [0.0, 1.0].
        0.0 = completely normal, 1.0 = highly anomalous.
        In scikit-learn's Isolation Forest decision_function:
        Large positive = normal, Large negative = anomalous.
        """
        if not self.is_fitted:
            raise RuntimeError("IsolationForest detector must be fitted before scoring.")

        X = X_input[self.features].copy().fillna(0.0)
        raw_scores = self.model.decision_function(X)

        # Normalize so lower raw score corresponds to higher anomaly score
        spread = max(1e-5, (self.score_max - self.score_min))
        norm_scores = 1.0 - np.clip((raw_scores - self.score_min) / spread, 0.0, 1.0)
        return np.round(norm_scores, 4)

    def predict(self, X_input: pd.DataFrame, score_threshold: float = 0.65) -> np.ndarray:
        """
        Returns boolean flags indicating anomaly detection based on normalized score threshold.
        """
        scores = self.compute_anomaly_scores(X_input)
        return scores >= score_threshold

    def save(self, model_dir: str = "5_AI_COMPONENTS/anomaly_detection/models"):
        """Serializes trained model artifact to disk."""
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "isolation_forest.joblib")
        metadata = {
            "n_estimators": self.n_estimators,
            "contamination": self.contamination,
            "random_state": self.random_state,
            "features": self.features,
            "score_min": self.score_min,
            "score_max": self.score_max
        }
        meta_path = os.path.join(model_dir, "isolation_forest_metadata.json")
        joblib.dump(self.model, model_path)
        import json
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print(f"Isolation Forest model serialized to {model_path}")

    def load(self, model_dir: str = "5_AI_COMPONENTS/anomaly_detection/models"):
        """Loads serialized model artifact from disk."""
        model_path = os.path.join(model_dir, "isolation_forest.joblib")
        meta_path = os.path.join(model_dir, "isolation_forest_metadata.json")

        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Isolation Forest model file not found at {model_path}")

        self.model = joblib.load(model_path)
        if os.path.isfile(meta_path):
            import json
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                self.n_estimators = metadata.get("n_estimators", 100)
                self.contamination = metadata.get("contamination", 0.035)
                self.features = metadata.get("features", ISO_FOREST_FEATURES)
                self.score_min = metadata.get("score_min", -0.5)
                self.score_max = metadata.get("score_max", 0.5)
        self.is_fitted = True
        print(f"Isolation Forest model loaded from {model_path}")
