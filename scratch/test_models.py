import sys, os, pandas as pd, numpy as np
sys.path.insert(0, os.path.abspath("5_AI_COMPONENTS/predictive_models"))
from preprocessing import aggregate_hourly_to_daily, extract_forecasting_features, chronological_train_val_test_split, ALL_PREDICTOR_FEATURES
from evaluation import compute_regression_metrics, evaluate_baseline_models, evaluate_per_profile
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

hourly_df = pd.read_csv("4_DEVELOPMENT/data/generated/water_usage_data.csv")
daily_df = aggregate_hourly_to_daily(hourly_df)
feat_df = extract_forecasting_features(daily_df)
train_df, val_df, test_df = chronological_train_val_test_split(feat_df, val_days=14, test_days=14)
combined_train = pd.concat([train_df, val_df], ignore_index=True)

print("=== 1. GLOBAL MODEL TEST ===")
from forecasting_model import WaterConsumptionForecaster
gf = WaterConsumptionForecaster(algorithm="random_forest", model_params={"n_estimators": 100, "max_depth": 6})
gf.train(combined_train, combined_train["daily_consumption_liters"].values)
g_preds = gf.predict(test_df)
print("Global RF Overall:", compute_regression_metrics(test_df["daily_consumption_liters"].values, g_preds))
for k, v in evaluate_per_profile(test_df, g_preds).items():
    print(f"  {k}: {v}")

print("\n=== 2. PER-METER LOCAL MODELS TEST ===")
local_features = [f for f in ALL_PREDICTOR_FEATURES if not f.startswith("profile_")]
m_preds = []
m_actuals = []

for m_id in [1, 2, 3]:
    tr_m = combined_train[combined_train["meter_id"] == m_id]
    te_m = test_df[test_df["meter_id"] == m_id]
    
    rf = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
    rf.fit(tr_m[local_features], tr_m["daily_consumption_liters"])
    preds_rf = np.maximum(0.0, rf.predict(te_m[local_features]))
    
    met_rf = compute_regression_metrics(te_m["daily_consumption_liters"].values, preds_rf)
    print(f"Meter {m_id} RF: MAE={met_rf['MAE']} L, MAPE={met_rf['MAPE']}%, R2={met_rf['R2']}")
    m_preds.extend(preds_rf)
    m_actuals.extend(te_m["daily_consumption_liters"].values)

overall_local = compute_regression_metrics(np.array(m_actuals), np.array(m_preds))
print("Per-Meter RF Overall:", overall_local)
