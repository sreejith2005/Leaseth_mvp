import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import pickle
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_honest_model():
    print("\n" + "="*80)
    print("TRAINING HONEST PREDICTIVE MODEL")
    print("Expected AUC: 75-82% (realistic performance)")
    print("="*80 + "\n")
    
    logger.info("Loading clean dataset...")
    df = pd.read_csv('data/clean_tenant_dataset.csv')
    
    print(f"Dataset shape: {df.shape}")
    print(f"Default rate: {df['default_flag'].mean():.1%}\n")
    
    logger.info("Selecting features...")
    
    feature_cols = [
        'credit_score',
        'monthly_income',
        'monthly_rent',
        'employment_verified',
        'income_verified',
        'rental_history_years',
        'previous_evictions',
        'bedrooms',
        'bathrooms',
        'square_feet',
        'property_age_years',
        'lease_term_months',
        'market_median_rent',
        'local_unemployment_rate',
        'inflation_rate',
        'furnished',
        'pets_allowed',
        'parking_spaces',
    ]
    
    df_encoded = df.copy()
    df_encoded['employment_type'] = df_encoded['employment_type'].astype('category').cat.codes
    df_encoded['property_type'] = df_encoded['property_type'].astype('category').cat.codes
    df_encoded['city'] = df_encoded['city'].astype('category').cat.codes
    
    feature_cols.extend(['employment_type', 'property_type', 'city'])
    
    X = df_encoded[feature_cols]
    y = df_encoded['default_flag']
    
    print(f"Feature count: {len(feature_cols)}")
    print(f"Features: {feature_cols}\n")
    
    logger.info("Splitting data (80/20 train/test)...")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    print(f"Train: {len(X_train):,} | Test: {len(X_test):,}")
    print(f"Train default rate: {y_train.mean():.1%}")
    print(f"Test default rate: {y_test.mean():.1%}\n")
    
    print("="*80)
    print("XGBOOST TRAINING")
    print("="*80 + "\n")
    
    baseline_weight = (y_train == 0).sum() / (y_train == 1).sum()
    
    xgb_params = {
        'n_estimators': 200,
        'max_depth': 4,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'reg_lambda': 5.0,
        'reg_alpha': 1.0,
        'min_child_weight': 5,
        'scale_pos_weight': baseline_weight,
        'objective': 'binary:logistic',
        'random_state': 42,
        'verbosity': 0
    }
    
    logger.info("Training XGBoost model...")
    model = xgb.XGBClassifier(**xgb_params)
    model.fit(X_train, y_train)
    
    logger.info("Training complete")
    
    print("\n" + "="*80)
    print("TRAIN SET PERFORMANCE")
    print("="*80 + "\n")
    
    y_train_pred = model.predict(X_train)
    y_train_proba = model.predict_proba(X_train)[:, 1]
    
    train_metrics = {
        'accuracy': accuracy_score(y_train, y_train_pred),
        'precision': precision_score(y_train, y_train_pred),
        'recall': recall_score(y_train, y_train_pred),
        'f1': f1_score(y_train, y_train_pred),
        'auc': roc_auc_score(y_train, y_train_proba)
    }
    
    for metric, value in train_metrics.items():
        print(f"{metric.upper():12s}: {value:.4f}")
    
    print("\n" + "="*80)
    print("TEST SET PERFORMANCE (Honest Model Performance)")
    print("="*80 + "\n")
    
    y_test_pred = model.predict(X_test)
    y_test_proba = model.predict_proba(X_test)[:, 1]
    
    test_metrics = {
        'precision': precision_score(y_test, y_test_pred),
        'recall': recall_score(y_test, y_test_pred),
        'f1': f1_score(y_test, y_test_pred),
        'auc': roc_auc_score(y_test, y_test_proba)
    }
    
    for metric, value in test_metrics.items():
        print(f"{metric.upper():12s}: {value:.4f}")
    
    print("\n" + "="*80)
    print("GENERALIZATION CHECK")
    print("="*80 + "\n")
    
    train_auc = train_metrics['auc']
    test_auc = test_metrics['auc']
    gap = train_auc - test_auc
    
    print(f"Train AUC: {train_auc:.4f}")
    print(f"Test AUC:  {test_auc:.4f}")
    print(f"Gap:       {gap:+.4f}")
    
    if gap > 0.10:
        print("WARNING: Overfitting detected (gap > 10%)")
    elif gap > 0.05:
        print("CAUTION: Slight overfitting (gap > 5%)")
    else:
        print("GOOD: Good generalization (gap < 5%)")
    
    print("\n" + "="*80)
    print("FEATURE IMPORTANCE (Top 20)")
    print("="*80 + "\n")
    
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    cumulative = 0
    for idx, row in feature_importance.head(20).iterrows():
        cumulative += row['importance']
        cumulative_pct = (cumulative / feature_importance['importance'].sum()) * 100
        print(f"{row['feature']:30s} {row['importance']*100:6.2f}% (Cumulative: {cumulative_pct:6.1f}%)")
    
    print("\n" + "="*80)
    print("CONFUSION MATRIX (Test Set)")
    print("="*80 + "\n")
    
    cm = confusion_matrix(y_test, y_test_pred)
    print(f"True Negatives:  {cm[0,0]:,}")
    print(f"False Positives: {cm[0,1]:,}")
    print(f"False Negatives: {cm[1,0]:,}")
    print(f"True Positives:  {cm[1,1]:,}")
    
    logger.info("\nSaving model artifacts...")
    
    with open('models/honest_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('models/honest_features.pkl', 'wb') as f:
        pickle.dump(feature_cols, f)
    
    metadata = {
        'model_type': 'XGBoost',
        'training_date': datetime.now().isoformat(),
        'dataset': 'clean_synthetic_tenant_data',
        'feature_count': len(feature_cols),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'default_rate': float(y.mean()),
        'train_metrics': train_metrics,
        'test_metrics': test_metrics,
        'generalization_gap': float(gap),
        'top_10_features': feature_importance.head(10).to_dict('records'),
        'hyperparameters': xgb_params
    }
    
    with open('models/honest_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*80)
    print("MODELS SAVED")
    print("="*80)
    print("  - models/honest_model.pkl")
    print("  - models/honest_features.pkl")
    print("  - models/honest_metadata.json")
    
    print("\n" + "="*80)
    print("FINAL ASSESSMENT")
    print("="*80 + "\n")
    
    if test_auc >= 0.75 and test_auc <= 0.85:
        print(f"HONEST MODEL: {test_auc:.2%} AUC")
        print("   This is REALISTIC and PRODUCTION-READY!")
        print("   Comparable to industry-standard credit scoring models")
    elif test_auc > 0.85:
        print(f"WARNING: Model achieves {test_auc:.2%} AUC")
        print("   Higher than typical - verify no remaining leakage")
    else:
        print(f"CAUTION: Model achieves {test_auc:.2%} AUC")
        print("   Lower than expected - may need more features or better data quality")
    
    return model, X_test, y_test, feature_cols, test_metrics


if __name__ == "__main__":
    train_honest_model()
