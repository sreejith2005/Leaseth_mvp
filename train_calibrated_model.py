"""
Train properly calibrated models with isotonic regression
Learns calibration from validation set instead of using hardcoded coefficients
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, brier_score_loss, log_loss
)
import pickle
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_calibrated_model():
    """
    Train XGBoost model with proper calibration using validation set
    """
    
    print("\n" + "="*80)
    print("TRAINING CALIBRATED MODEL")
    print("="*80 + "\n")
    
    # Load data
    logger.info("Loading dataset...")
    df = pd.read_csv('data/clean_tenant_dataset.csv')
    
    print(f"Dataset shape: {df.shape}")
    print(f"Default rate: {df['default_flag'].mean():.1%}\n")
    
    # Feature selection (same as honest_model.py)
    feature_cols = [
        'credit_score', 'monthly_income', 'monthly_rent',
        'employment_verified', 'income_verified',
        'rental_history_years', 'previous_evictions',
        'bedrooms', 'bathrooms', 'square_feet', 'property_age_years',
        'lease_term_months', 'market_median_rent', 
        'local_unemployment_rate', 'inflation_rate',
        'furnished', 'pets_allowed', 'parking_spaces',
    ]
    
    # Encode categorical
    df_encoded = df.copy()
    df_encoded['employment_type'] = df_encoded['employment_type'].astype('category').cat.codes
    df_encoded['property_type'] = df_encoded['property_type'].astype('category').cat.codes
    df_encoded['city'] = df_encoded['city'].astype('category').cat.codes
    
    feature_cols.extend(['employment_type', 'property_type', 'city'])
    
    X = df_encoded[feature_cols]
    y = df_encoded['default_flag']
    
    print(f"Feature count: {len(feature_cols)}\n")
    
    # Three-way split: train (60%), calibration (20%), test (20%)
    logger.info("Splitting data (60/20/20 train/cal/test)...")
    
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    X_train, X_cal, y_train, y_cal = train_test_split(
        X_temp, y_temp, test_size=0.25, stratify=y_temp, random_state=42
    )
    
    print(f"Train: {len(X_train):,} | Cal: {len(X_cal):,} | Test: {len(X_test):,}")
    print(f"Train default: {y_train.mean():.1%} | Cal default: {y_cal.mean():.1%} | Test default: {y_test.mean():.1%}\n")
    
    # ============================================================
    # TRAIN BASE MODEL
    # ============================================================
    
    print("="*80)
    print("TRAINING BASE XGBOOST MODEL")
    print("="*80 + "\n")
    
    xgb_params = {
        'n_estimators': 200,
        'max_depth': 4,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'reg_lambda': 5.0,
        'reg_alpha': 1.0,
        'min_child_weight': 5,
        'scale_pos_weight': (y_train == 0).sum() / (y_train == 1).sum(),
        'random_state': 42,
        'verbosity': 0
    }
    
    base_model = xgb.XGBClassifier(**xgb_params)
    base_model.fit(X_train, y_train)
    
    logger.info("Base model training complete\n")
    
    # ============================================================
    # CALIBRATION: Isotonic Regression
    # ============================================================
    
    print("="*80)
    print("CALIBRATING MODEL (Isotonic Regression)")
    print("="*80 + "\n")
    
    logger.info("Fitting calibration on validation set...")
    
    # Get base model predictions for calibration
    y_cal_proba = base_model.predict_proba(X_cal)[:, 1]
    
    # Use sklearn's isotonic regression directly
    from sklearn.isotonic import IsotonicRegression
    
    calibrator = IsotonicRegression(out_of_bounds='clip')
    calibrator.fit(y_cal_proba, y_cal)
    
    logger.info("Calibration complete\n")
    
    # ============================================================
    # EVALUATE: Uncalibrated vs Calibrated
    # ============================================================
    
    print("="*80)
    print("CALIBRATION QUALITY ASSESSMENT")
    print("="*80 + "\n")
    
    # Base model predictions
    y_test_proba_base = base_model.predict_proba(X_test)[:, 1]
    y_test_pred_base = (y_test_proba_base > 0.5).astype(int)
    
    # Calibrated predictions
    y_test_proba_cal = calibrator.predict(base_model.predict_proba(X_test)[:, 1])
    y_test_pred_cal = (y_test_proba_cal > 0.5).astype(int)
    
    # Metrics comparison
    print("Base Model (Uncalibrated):")
    print(f"  AUC:          {roc_auc_score(y_test, y_test_proba_base):.4f}")
    print(f"  Brier Score:  {brier_score_loss(y_test, y_test_proba_base):.4f} (lower is better)")
    print(f"  Log Loss:     {log_loss(y_test, y_test_proba_base):.4f} (lower is better)")
    print(f"  Accuracy:     {accuracy_score(y_test, y_test_pred_base):.4f}")
    print(f"  Precision:    {precision_score(y_test, y_test_pred_base):.4f}")
    print(f"  Recall:       {recall_score(y_test, y_test_pred_base):.4f}\n")
    
    print("Calibrated Model (Isotonic Regression):")
    print(f"  AUC:          {roc_auc_score(y_test, y_test_proba_cal):.4f}")
    print(f"  Brier Score:  {brier_score_loss(y_test, y_test_proba_cal):.4f} (lower is better)")
    print(f"  Log Loss:     {log_loss(y_test, y_test_proba_cal):.4f} (lower is better)")
    print(f"  Accuracy:     {accuracy_score(y_test, y_test_pred_cal):.4f}")
    print(f"  Precision:    {precision_score(y_test, y_test_pred_cal):.4f}")
    print(f"  Recall:       {recall_score(y_test, y_test_pred_cal):.4f}\n")
    
    brier_improvement = (brier_score_loss(y_test, y_test_proba_base) - 
                         brier_score_loss(y_test, y_test_proba_cal))
    
    print(f"Brier Score Improvement: {brier_improvement:.4f}")
    print(f"  {'Better calibration!' if brier_improvement > 0 else 'No improvement'}\n")
    
    # ============================================================
    # RELIABILITY ANALYSIS (Calibration Curve)
    # ============================================================
    
    print("="*80)
    print("RELIABILITY ANALYSIS")
    print("="*80 + "\n")
    
    # Bin predictions and calculate actual default rates
    bins = np.linspace(0, 1, 11)  # 10 bins
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    print("Predicted Prob Range | Actual Default Rate | Sample Size")
    print("-" * 60)
    
    for i in range(len(bins) - 1):
        mask = (y_test_proba_cal >= bins[i]) & (y_test_proba_cal < bins[i+1])
        if mask.sum() > 0:
            actual_rate = y_test[mask].mean()
            print(f"{bins[i]:.1f} - {bins[i+1]:.1f}          | {actual_rate:.1%}                | {mask.sum():,}")
        else:
            print(f"{bins[i]:.1f} - {bins[i+1]:.1f}          | N/A                  | 0")
    
    # ============================================================
    # SAVE CALIBRATED MODEL
    # ============================================================
    
    print("\n" + "="*80)
    print("SAVING CALIBRATED MODEL")
    print("="*80 + "\n")
    
    # Save both base model and calibrator
    with open('models/honest_model_calibrated.pkl', 'wb') as f:
        pickle.dump(base_model, f)
    
    with open('models/honest_calibrator.pkl', 'wb') as f:
        pickle.dump(calibrator, f)
    
    with open('models/honest_features_calibrated.pkl', 'wb') as f:
        pickle.dump(feature_cols, f)
    
    metadata = {
        'model_type': 'XGBoost + Isotonic Calibration',
        'training_date': datetime.now().isoformat(),
        'dataset': 'clean_synthetic_tenant_data',
        'calibration_method': 'isotonic',
        'feature_count': len(feature_cols),
        'train_samples': len(X_train),
        'calibration_samples': len(X_cal),
        'test_samples': len(X_test),
        'default_rate': float(y.mean()),
        'base_metrics': {
            'auc': float(roc_auc_score(y_test, y_test_proba_base)),
            'brier': float(brier_score_loss(y_test, y_test_proba_base)),
            'log_loss': float(log_loss(y_test, y_test_proba_base)),
            'accuracy': float(accuracy_score(y_test, y_test_pred_base)),
            'precision': float(precision_score(y_test, y_test_pred_base)),
            'recall': float(recall_score(y_test, y_test_pred_base))
        },
        'calibrated_metrics': {
            'auc': float(roc_auc_score(y_test, y_test_proba_cal)),
            'brier': float(brier_score_loss(y_test, y_test_proba_cal)),
            'log_loss': float(log_loss(y_test, y_test_proba_cal)),
            'accuracy': float(accuracy_score(y_test, y_test_pred_cal)),
            'precision': float(precision_score(y_test, y_test_pred_cal)),
            'recall': float(recall_score(y_test, y_test_pred_cal))
        },
        'brier_improvement': float(brier_improvement),
        'hyperparameters': xgb_params
    }
    
    with open('models/honest_metadata_calibrated.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("Saved:")
    print("  - models/honest_model_calibrated.pkl (base model)")
    print("  - models/honest_calibrator.pkl (isotonic calibrator)")
    print("  - models/honest_features_calibrated.pkl")
    print("  - models/honest_metadata_calibrated.json\n")
    
    print("="*80)
    print("CALIBRATION COMPLETE")
    print("="*80)
    
    return base_model, calibrator, X_test, y_test, feature_cols


if __name__ == "__main__":
    train_calibrated_model()
