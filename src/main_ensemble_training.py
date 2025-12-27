"""
Master Training Script - FIXED: NO DATA LEAKAGE
Ensemble Stacking with Bayesian Optimization
Only uses: Financial ratios, demographics, verification, market context
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
import pickle
import logging

# Add project root to sys.path for running as script
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.features import create_new_features
from ensemble_stacking import StackingEnsemble
from bayesian_tuning import BayesianOptimizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_PATH = ROOT_DIR / "data" / "leaseth_tenant_risk_dataset_v2_50k.csv"
TARGET = 'default_flag'

# CLEANED FEATURE SET - NO PAYMENT HISTORY, NO LEAKAGE
CLEAN_FEATURES = [
    # ============================================================
    # FINANCIAL RATIOS (Pure financial fundamentals, no payment history)
    # ============================================================
    'rent_to_income_ratio',           # Key affordability metric
    'income_multiple',                # Income vs Rent ratio
    'income_to_rent_buffer',          # Disposable income
    'rent_vs_market_ratio',           # Market-relative rent
    'rent_per_sqft',                  # Price per unit
    'security_deposit_ratio',         # Deposits as % of rent
    'debt_to_income_proxy',           # Rent burden
    
    # ============================================================
    # RAW ABSOLUTES (Baseline economic capacity)
    # ============================================================
    'absolute_income',                # Raw monthly income
    'absolute_credit_score',          # Raw credit score
    'absolute_rent',                  # Raw monthly rent
    'security_deposit',               # Deposit amount
    'monthly_income',                 # Monthly income
    'monthly_rent',                   # Monthly rent
    
    # ============================================================
    # CREDIT SIGNALS (Credit quality, NOT payment behavior)
    # ============================================================
    'credit_score',                   # Credit score (not behavior-based)
    'subprime_credit',                # Binary: subprime indicator
    
    # ============================================================
    # DEMOGRAPHIC SIGNALS (Non-payment-based)
    # ============================================================
    'tenant_age',                     # Applicant age
    'rental_history_years',           # Years as tenant (NOT payment history)
    'property_age_years',             # Property age
    'square_feet',                    # Property size
    'bedrooms',                       # Number of bedrooms
    'bathrooms',                      # Number of bathrooms
    'lease_term_months',              # Lease commitment
    'furnished',                      # Is property furnished
    'pets_allowed',                   # Pets allowed
    'parking_spaces',                 # Parking spaces
    
    # ============================================================
    # VERIFICATION / EMPLOYMENT (Truthfulness signals)
    # ============================================================
    'employment_verified',            # Employment is verified
    'income_verified',                # Income is verified
    'verification_score',             # Combined verification score
    
    # ============================================================
    # MARKET / ECONOMIC CONTEXT
    # ============================================================
    'market_median_rent',             # Regional housing market median
    'local_unemployment_rate_float',  # Economic health
    'inflation_rate_float',           # Economic conditions
    'market_economic_factor',         # Combined market indicator
    'days_to_rent_property',          # Market demand (how fast property rents)
    
    # ============================================================
    # PROPERTY CHARACTERISTICS (Non-payment)
    # ============================================================
    'property_desirability_score',    # Location/amenities score
    'tenant_stability_score',         # Tenure-based (NOT payment)
    'high_rent_burden',               # Simple binary: rent burden high?
    
    # ============================================================
    # CATEGORICAL ENCODED (Location/Type context)
    # ============================================================
    'property_type_enc',              # Property type encoded
    'employment_type_enc',            # Employment type encoded
    'city_enc',                       # City encoded
    'country_enc',                    # Country encoded
]

def main():
    print("\n" + "="*80)
    print("ENSEMBLE STACKING MODEL - FIXED (NO DATA LEAKAGE)")
    print("Target: Honest 85-90% AUC through genuine predictive features")
    print("="*80 + "\n")
    
    # ============================================================
    # STEP 1: Load and Engineer Features
    # ============================================================
    logger.info("Loading data...")
    df_raw = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df_raw):,} records\n")
    
    logger.info("Performing feature engineering...")
    df_feat = create_new_features(df_raw)
    
    # Remove non-numeric columns
    drop_cols = ['applicant_id', 'employment_status', 'rental_id'] if 'applicant_id' in df_feat.columns else []
    for col in drop_cols:
        if col in df_feat.columns:
            df_feat = df_feat.drop(columns=col)

    # Use CLEAN features (no leakage)
    available_features = [f for f in CLEAN_FEATURES if f in df_feat.columns]
    missing_features = [f for f in CLEAN_FEATURES if f not in df_feat.columns]
    
    if missing_features:
        print(f"\nMissing features (will skip): {missing_features}\n")
    
    X = df_feat[available_features]
    y = df_feat[TARGET]
    
    print("="*80)
    print("DATA QUALITY DIAGNOSTICS")
    print("="*80)

    print(f"\nFeature Statistics:")
    print(f"Total features (clean): {len(available_features)}")
    print(f"Numeric features: {X.select_dtypes(include=[np.number]).shape[1]}")
    
    missing_counts = X.isnull().sum()
    if missing_counts.sum() > 0:
        print(f"Features with missing values: {missing_counts.sum()}")
        print(missing_counts[missing_counts > 0])
    else:
        print(f"Features with missing values: None")

    zero_var = X.var() == 0
    if zero_var.sum() > 0:
        print(f"\nFeatures with zero variance:")
        print(X.columns[zero_var].tolist())
    else:
        print(f"\nFeatures with zero variance: None")

    print(f"\nClass distribution: {y.value_counts().to_dict()}")
    pos_weight = (y == 0).sum() / (y == 1).sum()
    print(f"Scale pos weight: {pos_weight:.4f}\n")

    # ============================================================
    # STEP 2: Train/Val/Test Split
    # ============================================================
    logger.info("Splitting data (70/15/15 split)...")
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.176, stratify=y_temp, random_state=42
    )
    print(f"Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}\n")

    # Save splits for diagnostics
    with open('models/X_train.pkl', 'wb') as f: pickle.dump(X_train, f)
    with open('models/X_val.pkl', 'wb') as f: pickle.dump(X_val, f)
    with open('models/X_test.pkl', 'wb') as f: pickle.dump(X_test, f)
    with open('models/y_train.pkl', 'wb') as f: pickle.dump(y_train, f)
    with open('models/y_val.pkl', 'wb') as f: pickle.dump(y_val, f)
    with open('models/y_test.pkl', 'wb') as f: pickle.dump(y_test, f)

    # ============================================================
    # STEP 3: Baseline Model (Random Forest) Diagnostics
    # ============================================================
    print("="*80)
    print("BASELINE: RANDOM FOREST DIAGNOSTICS (Clean Features)")
    print("="*80)
    rf_baseline = RandomForestClassifier(n_estimators=10, random_state=42, n_jobs=-1)
    rf_baseline.fit(X_train, y_train)
    rf_auc = roc_auc_score(y_test, rf_baseline.predict_proba(X_test)[:, 1])
    print(f"Random Forest Baseline AUC: {rf_auc:.4f}")

    rf_imp = pd.DataFrame({
        'feature': available_features,
        'importance': rf_baseline.feature_importances_
    }).sort_values('importance', ascending=False)
    print("\nTop 15 Most Important Features:")
    print(rf_imp.head(15).to_string(index=False))
    print("\nTop 10 Least Important Features:")
    print(rf_imp.tail(10).to_string(index=False))

    print("\n" + "="*80)

    # ============================================================
    # STEP 4: Bayesian Hyperparameter Optimization
    # ============================================================
    optimizer = BayesianOptimizer(
        X_train, y_train, X_val, y_val,
        scale_pos_weight=pos_weight
    )
    best_params, best_auc = optimizer.optimize(n_trials=20)
    optimized_params = optimizer.get_best_ensemble_params()

    # ============================================================
    # STEP 5: Train Final Ensemble with Best Parameters
    # ============================================================
    print("\n" + "="*80)
    print("TRAINING FINAL ENSEMBLE WITH OPTIMIZED PARAMETERS")
    print("="*80 + "\n")
    
    final_ensemble = StackingEnsemble(base_params=optimized_params)
    final_ensemble.fit(X_train, y_train, X_val, y_val, scale_pos_weight=pos_weight)

    # ============================================================
    # STEP 6: Evaluate on Test Set
    # ============================================================
    print("\n" + "="*80)
    print("FINAL ENSEMBLE PERFORMANCE ON TEST SET (Clean Features)")
    print("="*80 + "\n")
    
    test_metrics = final_ensemble.evaluate(X_test, y_test)
    
    print(f"Accuracy:  {test_metrics['accuracy']:.4f}")
    print(f"Precision: {test_metrics['precision']:.4f}")
    print(f"Recall:    {test_metrics['recall']:.4f}")
    print(f"F1-Score:  {test_metrics['f1']:.4f}")
    print(f"AUC-ROC:   {test_metrics['auc_roc']:.4f}")

    # ============================================================
    # STEP 7: Overfitting Diagnostic
    # ============================================================
    print("\n" + "="*80)
    print("OVERFITTING DIAGNOSTIC")
    print("="*80)

    y_pred_proba_train = final_ensemble.predict_proba(X_train)
    y_pred_proba_val = final_ensemble.predict_proba(X_val)
    y_pred_proba_test = final_ensemble.predict_proba(X_test)

    auc_train = roc_auc_score(y_train, y_pred_proba_train)
    auc_val = roc_auc_score(y_val, y_pred_proba_val)
    auc_test = roc_auc_score(y_test, y_pred_proba_test)

    print(f"\nAUC across all sets:")
    print(f"  Train AUC: {auc_train:.4f}")
    print(f"  Val AUC:   {auc_val:.4f}")
    print(f"  Test AUC:  {auc_test:.4f}")

    print(f"\nOverfitting indicators:")
    print(f"  Train - Val gap: {auc_train - auc_val:.4f}")
    print(f"  Train - Test gap: {auc_train - auc_test:.4f}")

    if auc_train - auc_test > 0.05:
        print("\nOVERFITTING DETECTED (gap > 5%)")
    else:
        print("\nGOOD GENERALIZATION (gap < 5%)")

    # ============================================================
    # STEP 8: Save Everything
    # ============================================================
    print("\n" + "="*80)
    print("SAVING MODELS AND FEATURES")
    print("="*80 + "\n")
    
    final_ensemble.save('models/ensemble_optimized')
    
    with open('models/ensemble_features.pkl', 'wb') as f:
        pickle.dump(available_features, f)
    
    print("All models saved successfully!")
    print(f"\nFinal AUC-ROC (Clean Features): {test_metrics['auc_roc']:.4f}")
    
    if test_metrics['auc_roc'] >= 0.85:
        print("\nHONEST MODEL: 85%+ AUC achieved!")
        print("This is REAL predictive power without data leakage.")
    else:
        print(f"\nAUC is {test_metrics['auc_roc']:.2%}")
        print("This is realistic given financial-only features.")


if __name__ == "__main__":
    main()
