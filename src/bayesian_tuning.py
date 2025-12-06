"""
Bayesian Hyperparameter Tuning using Optuna
Finds optimal parameters for all 3 models in ensemble
"""

import optuna
import numpy as np
from sklearn.model_selection import cross_val_score
from ensemble_stacking import StackingEnsemble
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BayesianOptimizer:
    """
    Bayesian hyperparameter optimization for stacking ensemble
    """
    
    def __init__(self, X_train, y_train, X_val, y_val, scale_pos_weight=None):
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val
        self.scale_pos_weight = scale_pos_weight
        self.best_params = None
        self.study = None
    
    def objective(self, trial):
        """
        Objective function for Optuna optimization
        """
        # Suggest hyperparameters
        params = {
            'catboost': {
                'iterations': trial.suggest_int('cat_iterations', 300, 800),
                'depth': trial.suggest_int('cat_depth', 4, 10),
                'learning_rate': trial.suggest_float('cat_lr', 0.01, 0.3, log=True),
                'l2_leaf_reg': trial.suggest_float('cat_l2', 0.1, 10.0),
                'random_seed': 42,
                'verbose': False,
                'loss_function': 'Logloss',
                'eval_metric': 'AUC'
            },
            'xgboost': {
                'n_estimators': trial.suggest_int('xgb_n_estimators', 300, 800),
                'max_depth': trial.suggest_int('xgb_max_depth', 4, 10),
                'learning_rate': trial.suggest_float('xgb_lr', 0.01, 0.3, log=True),
                'subsample': trial.suggest_float('xgb_subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('xgb_colsample', 0.6, 1.0),
                'reg_lambda': trial.suggest_float('xgb_lambda', 0.1, 10.0),
                'gamma': trial.suggest_float('xgb_gamma', 0.0, 5.0),
                'min_child_weight': trial.suggest_int('xgb_min_child', 1, 10),
                'random_state': 42,
                'eval_metric': 'logloss',
                'verbosity': 0
            },
            'lightgbm': {
                'n_estimators': trial.suggest_int('lgb_n_estimators', 300, 800),
                'max_depth': trial.suggest_int('lgb_max_depth', 4, 12),
                'learning_rate': trial.suggest_float('lgb_lr', 0.01, 0.3, log=True),
                'num_leaves': trial.suggest_int('lgb_num_leaves', 20, 150),
                'reg_lambda': trial.suggest_float('lgb_lambda', 0.1, 10.0),
                'feature_fraction': trial.suggest_float('lgb_feature_frac', 0.5, 1.0),
                'random_state': 42,
                'verbosity': -1
            }
        }
        
        # Train ensemble with suggested parameters
        ensemble = StackingEnsemble(base_params=params)
        ensemble.fit(self.X_train, self.y_train, self.X_val, self.y_val, self.scale_pos_weight)
        
        # Evaluate on validation set
        metrics = ensemble.evaluate(self.X_val, self.y_val)
        
        return metrics['auc_roc']
    
    def optimize(self, n_trials=100):
        """
        Run Bayesian optimization
        
        Args:
            n_trials: Number of optimization trials
        """
        logger.info("=" * 80)
        logger.info(f"BAYESIAN HYPERPARAMETER OPTIMIZATION ({n_trials} trials)")
        logger.info("=" * 80)
        
        # Create study
        self.study = optuna.create_study(
            direction='maximize',
            sampler=optuna.samplers.TPESampler(seed=42)
        )
        
        # Optimize
        self.study.optimize(
            self.objective,
            n_trials=n_trials,
            show_progress_bar=True
        )
        
        # Get best parameters
        self.best_params = self.study.best_params
        
        logger.info("\n" + "=" * 80)
        logger.info("OPTIMIZATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Best AUC-ROC: {self.study.best_value:.4f}")
        logger.info(f"Best trial: #{self.study.best_trial.number}")
        
        return self.best_params, self.study.best_value
    
    def get_best_ensemble_params(self):
        """
        Convert Optuna best_params to ensemble format
        """
        if not self.best_params:
            raise ValueError("No optimization run yet. Call optimize() first.")
        
        return {
            'catboost': {
                'iterations': self.best_params['cat_iterations'],
                'depth': self.best_params['cat_depth'],
                'learning_rate': self.best_params['cat_lr'],
                'l2_leaf_reg': self.best_params['cat_l2'],
                'random_seed': 42,
                'verbose': False,
                'loss_function': 'Logloss',
                'eval_metric': 'AUC'
            },
            'xgboost': {
                'n_estimators': self.best_params['xgb_n_estimators'],
                'max_depth': self.best_params['xgb_max_depth'],
                'learning_rate': self.best_params['xgb_lr'],
                'subsample': self.best_params['xgb_subsample'],
                'colsample_bytree': self.best_params['xgb_colsample'],
                'reg_lambda': self.best_params['xgb_lambda'],
                'gamma': self.best_params['xgb_gamma'],
                'min_child_weight': self.best_params['xgb_min_child'],
                'random_state': 42,
                'eval_metric': 'logloss',
                'verbosity': 0
            },
            'lightgbm': {
                'n_estimators': self.best_params['lgb_n_estimators'],
                'max_depth': self.best_params['lgb_max_depth'],
                'learning_rate': self.best_params['lgb_lr'],
                'num_leaves': self.best_params['lgb_num_leaves'],
                'reg_lambda': self.best_params['lgb_lambda'],
                'feature_fraction': self.best_params['lgb_feature_frac'],
                'random_state': 42,
                'verbosity': -1
            }
        }
