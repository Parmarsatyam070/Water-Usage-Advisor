import sys, os, pandas as pd, numpy as np
sys.path.insert(0, os.path.abspath("5_AI_COMPONENTS/predictive_models"))
from preprocessing import aggregate_hourly_to_daily, extract_forecasting_features, chronological_train_val_test_split, ALL_PREDICTOR_FEATURES
from evaluation import compute_regression_metrics, evaluate_baseline_models, evaluate_per_profile
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge

hourly_df = pd.read_csv("4_DEVELOPMENT/data/generated/water_usage_data.csv")
daily_df = aggregate_hourly_to_daily(hourly_df)
feat_df = extract_forecasting_features(daily_df)
train_df, val_df, test_df = chronological_train_val_test_split(feat_df, val_days=14, test_days=14)
combined_train = pd.concat([train_df, val_df], ignore_index=True)

models = {
    "Random Forest (default)": RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42),
    "Random Forest (tuned)": RandomForestRegressor(n_estimators=150, max_depth=8, min_samples_leaf=2, random_state=42),
    "Gradient Boosting (default)": GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42),
    "Gradient Boosting (tuned)": GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, max_depth=4, random_state=42),
    "Ridge (alpha=10)": Ridge(alpha=10.0, random_state=42)
}

print("=== BASELINES ON TEST SET ===")
base = evaluate_baseline_models(test_df)
for k, v in base.items():
    print(f"{k}: MAE={v['MAE']} L, RMSE={v['RMSE']} L, MAPE={v['MAPE']}%, R2={v['R2']}")

print("\n=== VALIDATION SET COMPARISON (Tuning on Train, Eval on Val) ===")
for name, m in models.items():
    m.fit(train_df[ALL_PREDICTOR_FEATURES], train_df["daily_consumption_liters"])
    val_p = np.maximum(0.0, m.predict(val_df[ALL_PREDICTOR_FEATURES]))
    v_met = compute_regression_metrics(val_df["daily_consumption_liters"].values, val_p)
    print(f"{name:<30} | Val MAE: {v_met['MAE']:>6.2f} L | Val RMSE: {v_met['RMSE']:>6.2f} L | Val MAPE: {v_met['MAPE']:>5.2f}% | Val R2: {v_met['R2']:>6.4f}")

print("\n=== TEST SET COMPARISON (Retrained on Train+Val, Eval on Untouched Test) ===")
for name, m in models.items():
    m.fit(combined_train[ALL_PREDICTOR_FEATURES], combined_train["daily_consumption_liters"])
    test_p = np.maximum(0.0, m.predict(test_df[ALL_PREDICTOR_FEATURES]))
    t_met = compute_regression_metrics(test_df["daily_consumption_liters"].values, test_p)
    print(f"{name:<30} | Test MAE: {t_met['MAE']:>6.2f} L | Test RMSE: {t_met['RMSE']:>6.2f} L | Test MAPE: {t_met['MAPE']:>5.2f}% | Test R2: {t_met['R2']:>6.4f} | AccProxy: {t_met['accuracy_proxy']:>5.2f}%")
    for prof, pmet in evaluate_per_profile(test_df, test_p).items():
        print(f"      {prof:<36}: MAE={pmet['MAE']:>6.2f} L | MAPE={pmet['MAPE']:>5.2f}% | R2={pmet['R2']:>6.4f}")
