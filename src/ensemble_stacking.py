"""
Ensemble Stacking Model - 3 Algorithms + Meta-Learner
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve
from sklearn.isotonic import IsotonicRegression
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StackingEnsemble:
    """
    3-Layer Stacking Ensemble:
    - Layer 1: CatBoost, XGBoost, LightGBM (base learners)
    - Layer 2: Logistic Regression (meta-learner)
    - Layer 3: Isotonic Regression (calibration)
    """
    
    def __init__(self, base_params=None):
        """
        Initialize ensemble with optional hyperparameters
        """
        self.base_params = base_params or self._default_params()
        
        # Layer 1: Base learners
        self.catboost_model = None
        self.xgboost_model = None
        self.lightgbm_model = None
        
        # Layer 2: Meta-learner
        self.meta_model = LogisticRegression(max_iter=1000, random_state=42)
        
        # Layer 3: Calibration
        self.calibrator = IsotonicRegression(out_of_bounds='clip')
        
        # Optimal threshold
        self.optimal_threshold = 0.5
        
        logger.info("Stacking ensemble initialized")
    
    def _default_params(self):
        """Default hyperparameters (can be overridden by Optuna)"""
        return {
            'catboost': {
                'iterations': 500,
                'depth': 6,
                'learning_rate': 0.05,
                'l2_leaf_reg': 3,
                'random_seed': 42,
                'verbose': False,
                'loss_function': 'Logloss',
                'eval_metric': 'AUC'
            },
            'xgboost': {
                'n_estimators': 500,
                'max_depth': 6,
                'learning_rate': 0.05,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'reg_lambda': 1.0,
                'gamma': 0.5,
                'min_child_weight': 2,
                'random_state': 42,
                'eval_metric': 'logloss',
                'verbosity': 0
            },
            'lightgbm': {
                'n_estimators': 500,
                'max_depth': 8,
                'learning_rate': 0.05,
                'num_leaves': 31,
                'reg_lambda': 1.0,
                'random_state': 42,
                'verbosity': -1
            }
        }
    
    def fit(self, X_train, y_train, X_val, y_val, scale_pos_weight=None):
        """
        Train the 3-layer stacking ensemble
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            scale_pos_weight: Class weight for imbalanced data
        """
        logger.info("=" * 80)
        logger.info("LAYER 1: Training Base Learners")
        logger.info("=" * 80)
        
        # Add scale_pos_weight to all models
        if scale_pos_weight:
            self.base_params['catboost']['scale_pos_weight'] = scale_pos_weight
            self.base_params['xgboost']['scale_pos_weight'] = scale_pos_weight
            self.base_params['lightgbm']['scale_pos_weight'] = scale_pos_weight
        
        # Train CatBoost
        logger.info("\n[1/3] Training CatBoost...")
        self.catboost_model = CatBoostClassifier(**self.base_params['catboost'])
        self.catboost_model.fit(X_train, y_train, verbose=False)
        
        # Train XGBoost
        logger.info("[2/3] Training XGBoost...")
        self.xgboost_model = xgb.XGBClassifier(**self.base_params['xgboost'])
        self.xgboost_model.fit(X_train, y_train)
        
        # Train LightGBM
        logger.info("[3/3] Training LightGBM...")
        self.lightgbm_model = lgb.LGBMClassifier(**self.base_params['lightgbm'])
        self.lightgbm_model.fit(X_train, y_train)
        
        logger.info("Base learners trained successfully")
        
        # ============================================================
        # LAYER 2: Meta-Learner (Stacking)
        # ============================================================
        logger.info("\n" + "=" * 80)
        logger.info("LAYER 2: Training Meta-Learner (Stacking)")
        logger.info("=" * 80)
        
        # Get predictions from base learners on validation set
        cat_pred = self.catboost_model.predict_proba(X_val)[:, 1]
        xgb_pred = self.xgboost_model.predict_proba(X_val)[:, 1]
        lgb_pred = self.lightgbm_model.predict_proba(X_val)[:, 1]
        
        # Stack predictions as features for meta-learner
        meta_features = np.column_stack([cat_pred, xgb_pred, lgb_pred])
        
        # Train meta-learner
        self.meta_model.fit(meta_features, y_val)
        logger.info("Meta-learner trained successfully")
        
        # ============================================================
        # LAYER 3: Calibration
        # ============================================================
        logger.info("\n" + "=" * 80)
        logger.info("LAYER 3: Calibrating Predictions")
        logger.info("=" * 80)
        
        # Get meta predictions on validation set
        meta_pred = self.meta_model.predict_proba(meta_features)[:, 1]
        
        # Train calibrator
        self.calibrator.fit(meta_pred, y_val)
        logger.info("Calibration complete")
        
        # ============================================================
        # Find Optimal Threshold
        # ============================================================
        calibrated_pred = self.calibrator.predict(meta_pred)
        fpr, tpr, thresholds = roc_curve(y_val, calibrated_pred)
        optimal_idx = np.argmax(tpr - fpr)
        self.optimal_threshold = thresholds[optimal_idx]
        
        logger.info(f"Optimal threshold: {self.optimal_threshold:.4f}")
        logger.info("\nStacking ensemble training complete!")
    
    def predict_proba(self, X):
        """
        Generate calibrated probability predictions
        """
        # Layer 1: Base learner predictions
        cat_pred = self.catboost_model.predict_proba(X)[:, 1]
        xgb_pred = self.xgboost_model.predict_proba(X)[:, 1]
        lgb_pred = self.lightgbm_model.predict_proba(X)[:, 1]
        
        # Stack predictions
        meta_features = np.column_stack([cat_pred, xgb_pred, lgb_pred])
        
        # Layer 2: Meta-learner prediction
        meta_pred = self.meta_model.predict_proba(meta_features)[:, 1]
        
        # Layer 3: Calibration
        calibrated_pred = self.calibrator.predict(meta_pred)
        
        return calibrated_pred
    
    def predict(self, X):
        """
        Generate binary predictions using optimal threshold
        """
        proba = self.predict_proba(X)
        return (proba >= self.optimal_threshold).astype(int)
    
    def evaluate(self, X_test, y_test):
        """
        Comprehensive evaluation on test set
        """
        y_pred_proba = self.predict_proba(X_test)
        y_pred = self.predict(X_test)
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0),
            'auc_roc': roc_auc_score(y_test, y_pred_proba)
        }
        
        return metrics
    
    def save(self, path_prefix='models/ensemble'):
        """
        Save all models
        """
        with open(f'{path_prefix}_catboost.pkl', 'wb') as f:
            pickle.dump(self.catboost_model, f)
        with open(f'{path_prefix}_xgboost.pkl', 'wb') as f:
            pickle.dump(self.xgboost_model, f)
        with open(f'{path_prefix}_lightgbm.pkl', 'wb') as f:
            pickle.dump(self.lightgbm_model, f)
        with open(f'{path_prefix}_meta.pkl', 'wb') as f:
            pickle.dump(self.meta_model, f)
        with open(f'{path_prefix}_calibrator.pkl', 'wb') as f:
            pickle.dump(self.calibrator, f)
        with open(f'{path_prefix}_threshold.pkl', 'wb') as f:
            pickle.dump(self.optimal_threshold, f)
        
        logger.info(f"Ensemble saved to {path_prefix}_*.pkl")
    
    @staticmethod
    def load(path_prefix='models/ensemble'):
        """
        Load all models
        """
        ensemble = StackingEnsemble()
        
        with open(f'{path_prefix}_catboost.pkl', 'rb') as f:
            ensemble.catboost_model = pickle.load(f)
        with open(f'{path_prefix}_xgboost.pkl', 'rb') as f:
            ensemble.xgboost_model = pickle.load(f)
        with open(f'{path_prefix}_lightgbm.pkl', 'rb') as f:
            ensemble.lightgbm_model = pickle.load(f)
        with open(f'{path_prefix}_meta.pkl', 'rb') as f:
            ensemble.meta_model = pickle.load(f)
        with open(f'{path_prefix}_calibrator.pkl', 'rb') as f:
            ensemble.calibrator = pickle.load(f)
        with open(f'{path_prefix}_threshold.pkl', 'rb') as f:
            ensemble.optimal_threshold = pickle.load(f)
        
        logger.info(f"Ensemble loaded from {path_prefix}_*.pkl")
        return ensemble
