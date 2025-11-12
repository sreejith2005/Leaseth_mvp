"""
V1 Model Training - With Eviction History
Now includes both XGBoost and LightGBM for comparison
Uses scale_pos_weight instead of SMOTE
Real calibration using validation set
Full feature importance output
"""

import pandas as pd
import xgboost as xgb
import lightgbm as lgb
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve
from sklearn.isotonic import IsotonicRegression
from src.features import create_new_features
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_PATH = "data/processed_dataset.csv"
MODEL_XGBOOST_PATH = "models/xgboost_model.pkl"
MODEL_LIGHTGBM_PATH = "models/lightgbm_model.pkl"
FEATURES_PATH = "models/feature_list.pkl"
CALIBRATION_PATH = "models/calibration_model.pkl"
TARGET = 'default_flag'

def print_all_feature_importance(feature_importance_df, model_name):
    """Print complete feature importance (all features, not just top 20)"""
    print("\n" + "=" * 80)
    print(f"COMPLETE FEATURE IMPORTANCE - {model_name}")
    print("=" * 80)
    
    total_importance = feature_importance_df['importance'].sum()
    cumulative = 0
    
    for idx, (_, row) in enumerate(feature_importance_df.iterrows(), 1):
        cumulative += row['importance']
        cumulative_pct = (cumulative / total_importance) * 100
        print(f"{idx:3d}. {row['feature']:45s} {row['importance']*100:7.3f}% (Cumulative: {cumulative_pct:6.2f}%)")

def main():
    print("=" * 80)
    print("V1 MODEL TRAINING - WITH EVICTION HISTORY")
    print("XGBoost + LightGBM Comparison with Real Calibration")
    print("=" * 80)

    # Load data
    logger.info(f"Loading data from {DATA_PATH}...")
    df_raw = pd.read_csv(DATA_PATH)
    print(f"\nLoaded {len(df_raw):,} records")

    # Feature engineering
    logger.info("Performing feature engineering...")
    df_feat = create_new_features(df_raw)
    print(f"Feature engineering complete. Shape: {df_feat.shape}")

    # Remove leaky and raw features
    leaky_features = ['on_time_payments', 'late_payments', 'missed_payments', 
                      'payment_consistency_score', 'total_late_missed', 'rental_id']
    raw_cats = ['country', 'city', 'property_type', 'employment_type', 'currency']
    exclude_cols = leaky_features + raw_cats + [TARGET, 'eviction_binary',
                                                  'number_of_bedrooms', 'property_size_sqft', 
                                                  'property_age', 'currency_enc']

    v1_features = [col for col in df_feat.columns if col not in exclude_cols]
    
    print(f"\nV1 feature count: {len(v1_features)}")
    print("Strategy: ALL features included with eviction history")
    print("Class imbalance handling: scale_pos_weight (no SMOTE)")

    X = df_feat[v1_features]
    y = df_feat[TARGET]

    # Calculate class weights
    pos_weight = (y == 0).sum() / (y == 1).sum()
    print(f"\nClass weight (scale_pos_weight): {pos_weight:.4f}")
    print(f"Negative class: {(y == 0).sum():,} samples")
    print(f"Positive class (defaults): {(y == 1).sum():,} samples")

    # Train/test/validation split
    logger.info("Splitting data (70/15/15 for train/validation/test)...")
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.176, stratify=y_temp, random_state=42
    )
    
    print(f"Train: {len(X_train):,} | Validation: {len(X_val):,} | Test: {len(X_test):,}")

    # ============================================================
    # XGBOOST MODEL TRAINING
    # ============================================================
    print("\n" + "=" * 80)
    print("XGBOOST MODEL TRAINING")
    print("=" * 80)
    
    print("\nXGBoost Hyperparameters:")
    print("  - n_estimators: 500")
    print("  - max_depth: 6")
    print("  - learning_rate: 0.05")
    print("  - reg_lambda: 1.0")
    print("  - gamma: 0.5")
    print("  - min_child_weight: 2")
    print("  - scale_pos_weight: {:.4f}".format(pos_weight))

    xgb_model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        gamma=0.5,
        min_child_weight=2,
        scale_pos_weight=pos_weight,
        random_state=42,
        eval_metric='logloss',
        verbosity=0
    )

    xgb_model.fit(X_train, y_train)
    logger.info("XGBoost training complete")

    # XGBoost feature importance
    xgb_feature_importance = pd.DataFrame({
        'feature': v1_features,
        'importance': xgb_model.feature_importances_
    }).sort_values('importance', ascending=False)

    print_all_feature_importance(xgb_feature_importance, "XGBoost")

    # XGBoost predictions and metrics
    y_pred_xgb = xgb_model.predict(X_test)
    y_pred_proba_xgb = xgb_model.predict_proba(X_test)[:, 1]

    print("\n" + "=" * 80)
    print("XGBOOST MODEL PERFORMANCE")
    print("=" * 80)
    print(f"Accuracy:  {accuracy_score(y_test, y_pred_xgb):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred_xgb, zero_division=0):.4f}")
    print(f"Recall:    {recall_score(y_test, y_pred_xgb, zero_division=0):.4f}")
    print(f"F1-Score:  {f1_score(y_test, y_pred_xgb, zero_division=0):.4f}")
    print(f"AUC-ROC:   {roc_auc_score(y_test, y_pred_proba_xgb):.4f}")

    # ============================================================
    # LIGHTGBM MODEL TRAINING
    # ============================================================
    print("\n" + "=" * 80)
    print("LIGHTGBM MODEL TRAINING")
    print("=" * 80)
    
    print("\nLightGBM Hyperparameters:")
    print("  - n_estimators: 500")
    print("  - max_depth: 8")
    print("  - learning_rate: 0.05")
    print("  - reg_lambda: 1.0")
    print("  - num_leaves: 31")
    print("  - scale_pos_weight: {:.4f}".format(pos_weight))

    lgb_model = lgb.LGBMClassifier(
        n_estimators=500,
        max_depth=8,
        learning_rate=0.05,
        num_leaves=31,
        reg_lambda=1.0,
        random_state=42,
        verbose=-1,
        scale_pos_weight=pos_weight
    )

    lgb_model.fit(X_train, y_train)
    logger.info("LightGBM training complete")

    # LightGBM feature importance
    lgb_feature_importance = pd.DataFrame({
        'feature': v1_features,
        'importance': lgb_model.feature_importances_
    }).sort_values('importance', ascending=False)

    print_all_feature_importance(lgb_feature_importance, "LightGBM")

    # LightGBM predictions and metrics
    y_pred_lgb = lgb_model.predict(X_test)
    y_pred_proba_lgb = lgb_model.predict_proba(X_test)[:, 1] # type: ignore

    print("\n" + "=" * 80)
    print("LIGHTGBM MODEL PERFORMANCE")
    print("=" * 80)
    print(f"Accuracy:  {accuracy_score(y_test, y_pred_lgb):.4f}") # type: ignore
    print(f"Precision: {precision_score(y_test, y_pred_lgb, zero_division=0):.4f}") # type: ignore
    print(f"Recall:    {recall_score(y_test, y_pred_lgb, zero_division=0):.4f}") # type: ignore
    print(f"F1-Score:  {f1_score(y_test, y_pred_lgb, zero_division=0):.4f}") # type: ignore
    print(f"AUC-ROC:   {roc_auc_score(y_test, y_pred_proba_lgb):.4f}")

    # ============================================================
    # MODEL COMPARISON
    # ============================================================
    print("\n" + "=" * 80)
    print("MODEL COMPARISON - XGBOOST vs LIGHTGBM")
    print("=" * 80)

    comparison_data = {
        'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC-ROC'],
        'XGBoost': [
            accuracy_score(y_test, y_pred_xgb),
            precision_score(y_test, y_pred_xgb, zero_division=0),
            recall_score(y_test, y_pred_xgb, zero_division=0),
            f1_score(y_test, y_pred_xgb, zero_division=0),
            roc_auc_score(y_test, y_pred_proba_xgb)
        ],
        'LightGBM': [
            accuracy_score(y_test, y_pred_lgb), # type: ignore
            precision_score(y_test, y_pred_lgb, zero_division=0), # type: ignore
            recall_score(y_test, y_pred_lgb, zero_division=0), # type: ignore
            f1_score(y_test, y_pred_lgb, zero_division=0), # type: ignore
            roc_auc_score(y_test, y_pred_proba_lgb)
        ]
    }

    comparison_df = pd.DataFrame(comparison_data)
    print("\n" + comparison_df.to_string(index=False))

    # ============================================================
    # CALIBRATION
    # ============================================================
    print("\n" + "=" * 80)
    print("MODEL CALIBRATION ON VALIDATION SET")
    print("=" * 80)

    print("Fitting isotonic calibration on validation set...")

    xgb_val_proba = xgb_model.predict_proba(X_val)[:, 1]
    lgb_val_proba = lgb_model.predict_proba(X_val)[:, 1]  # type: ignore

    calibrated_xgb = IsotonicRegression(out_of_bounds='clip')
    calibrated_xgb.fit(xgb_val_proba, y_val)

    calibrated_lgb = IsotonicRegression(out_of_bounds='clip')
    calibrated_lgb.fit(lgb_val_proba, y_val)

    print("Calibration complete")

    # ============================================================
    # FIND OPTIMAL THRESHOLD
    # ============================================================
    print("\n" + "=" * 80)
    print("OPTIMAL THRESHOLD TUNING")
    print("=" * 80)

    fpr_xgb, tpr_xgb, thresholds_xgb = roc_curve(y_test, y_pred_proba_xgb)
    optimal_idx_xgb = np.argmax(tpr_xgb - fpr_xgb)
    optimal_threshold_xgb = thresholds_xgb[optimal_idx_xgb]

    fpr_lgb, tpr_lgb, thresholds_lgb = roc_curve(y_test, y_pred_proba_lgb)
    optimal_idx_lgb = np.argmax(tpr_lgb - fpr_lgb)
    optimal_threshold_lgb = thresholds_lgb[optimal_idx_lgb]

    print(f"XGBoost optimal threshold: {optimal_threshold_xgb:.4f}")
    print(f"LightGBM optimal threshold: {optimal_threshold_lgb:.4f}")

    # ============================================================
    # SAVE MODELS
    # ============================================================
    print("\n" + "=" * 80)
    print("SAVING MODELS AND ARTIFACTS")
    print("=" * 80)

    print(f"Saving XGBoost model to {MODEL_XGBOOST_PATH}...")
    with open(MODEL_XGBOOST_PATH, "wb") as f:
        pickle.dump(xgb_model, f)

    print(f"Saving LightGBM model to {MODEL_LIGHTGBM_PATH}...")
    with open(MODEL_LIGHTGBM_PATH, "wb") as f:
        pickle.dump(lgb_model, f)

    print(f"Saving feature list to {FEATURES_PATH}...")
    with open(FEATURES_PATH, "wb") as f:
        pickle.dump(v1_features, f)

    print(f"Saving calibration models...")
    calibration_data = {
        'xgboost': calibrated_xgb,
        'lightgbm': calibrated_lgb,
        'optimal_threshold_xgb': optimal_threshold_xgb,
        'optimal_threshold_lgb': optimal_threshold_lgb
    }
    with open(CALIBRATION_PATH, "wb") as f:
        pickle.dump(calibration_data, f)

    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n" + "=" * 80)
    print("V1 MODEL TRAINING COMPLETE")
    print("=" * 80)
    print(f"XGBoost Model saved: {MODEL_XGBOOST_PATH}")
    print(f"LightGBM Model saved: {MODEL_LIGHTGBM_PATH}")
    print(f"Features saved: {FEATURES_PATH}")
    print(f"Calibration data saved: {CALIBRATION_PATH}")
    print(f"Total features: {len(v1_features)}")
    print("\nKey improvements:")
    print("  - Replaced SMOTE with scale_pos_weight")
    print("  - Better default values for missing data")
    print("  - Added feature interactions")
    print("  - Improved calibration using validation set")
    print("  - Included LightGBM for model comparison")

if __name__ == "__main__":
    main()
