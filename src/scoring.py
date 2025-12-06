"""
Hybrid model routing and prediction logic
"""

import pickle
import time
import logging
from typing import Dict, Any, Tuple
import numpy as np
from src.config import settings
from src.utils import generate_model_hash

logger = logging.getLogger(__name__)

# Global model cache
V1_MODEL = None
V3_MODEL = None
V1_FEATURES = None
V3_FEATURES = None
MODEL_HASH_V1 = None
MODEL_HASH_V3 = None


def load_models():
    """Load XGBoost models into memory at startup"""
    global V1_MODEL, V3_MODEL, V1_FEATURES, V3_FEATURES, MODEL_HASH_V1, MODEL_HASH_V3
    
    try:
        logger.info("Loading V1 model...")
        with open(settings.MODEL_V1_PATH, 'rb') as f:
            V1_MODEL = pickle.load(f)
        with open(settings.FEATURE_V1_PATH, 'rb') as f:
            V1_FEATURES = pickle.load(f)
        MODEL_HASH_V1 = generate_model_hash(settings.MODEL_V1_PATH)
        logger.info(f"V1 model loaded. Hash: {MODEL_HASH_V1[:8]}...")
        
        logger.info("Loading V3 model...")
        with open(settings.MODEL_V3_PATH, 'rb') as f:
            V3_MODEL = pickle.load(f)
        with open(settings.FEATURE_V3_PATH, 'rb') as f:
            V3_FEATURES = pickle.load(f)
        MODEL_HASH_V3 = generate_model_hash(settings.MODEL_V3_PATH)
        logger.info(f"V3 model loaded. Hash: {MODEL_HASH_V3[:8]}...")
        
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        raise


def check_models_loaded() -> bool:
    """Check if models are loaded"""
    return V1_MODEL is not None and V3_MODEL is not None


def predict_and_score(
    engineered_features: Dict[str, Any],
    request_id: str = None,
    custom_thresholds: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Hybrid model routing and prediction
    
    Args:
        engineered_features: Feature engineering output (from features.py)
        request_id: Request ID for logging
        custom_thresholds: Optional custom thresholds for decision boundaries
            Example: {"auto_approve": 0.30, "manual_review": 0.65, "auto_reject": 0.85}
    
    Returns:
        Prediction results with risk score and metadata
    """
    
    start_time = time.time()
    
    try:
        # Check models are loaded
        if not check_models_loaded():
            logger.error(f"[{request_id}] Models not loaded")
            raise RuntimeError("Models not loaded")
        
        # Determine which model to use
        previous_evictions = engineered_features.get('previous_evictions', 0)
        use_v1_model = previous_evictions > 0
        
        if use_v1_model:
            logger.info(f"[{request_id}] Using V1 model (evictions: {previous_evictions})")
            model = V1_MODEL
            features = V1_FEATURES
            model_version = "V1_2025_11"
            model_hash = MODEL_HASH_V1
        else:
            logger.info(f"[{request_id}] Using V3 model (no evictions)")
            model = V3_MODEL
            features = V3_FEATURES
            model_version = "V3_2025_11"
            model_hash = MODEL_HASH_V3
        
        # Extract features in correct order
        try:
            X = np.array([[engineered_features.get(f, 0) for f in features]])
        except Exception as e:
            logger.error(f"[{request_id}] Feature extraction failed: {e}")
            raise ValueError(f"Feature extraction error: {e}")
        
        # Get prediction
        probability = model.predict_proba(X)[0][1]  # Probability of default
        
        # Convert to risk score (0-100) - use raw probability directly
        risk_score = int(round(probability * 100))
        risk_score = max(0, min(100, risk_score))  # Clip to 0-100
        
        # Three-tier decision system (cost-aware)
        decision_result = _make_cost_aware_decision(
            probability, 
            risk_score,
            engineered_features,
            custom_thresholds
        )
        
        risk_category = decision_result["risk_category"]
        recommendation = decision_result["recommendation"]
        decision_reasoning = decision_result["reasoning"]
        
        # Confidence score (model confidence)
        confidence_score = _calculate_confidence(probability)
        
        # Calculate inference time
        inference_time_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"[{request_id}] Prediction: {model_version}, "
            f"Risk: {risk_score}% ({risk_category}), "
            f"Confidence: {confidence_score:.2f}, "
            f"Time: {inference_time_ms:.1f}ms"
        )
        
        return {
            "success": True,
            "default_probability": float(probability),
            "risk_score": risk_score,
            "risk_category": risk_category,
            "recommendation": recommendation,
            "decision_tier": decision_result["decision_tier"],
            "decision_reasoning": decision_reasoning,
            "confidence_score": float(confidence_score),
            "model_version": model_version,
            "model_hash": model_hash,
            "inference_time_ms": inference_time_ms,
            "model_used": "V1" if use_v1_model else "V3",
            "num_features": len(features)
        }
    
    except Exception as e:
        logger.error(f"[{request_id}] Prediction failed: {e}")
        raise


def _calibrate_probability(prob: float, is_v1: bool) -> float:
    """
    Calibrate raw probability to true default rate
    Using Platt scaling coefficients
    
    Calibration = 1 / (1 + exp(-(a*p + b)))
    where a, b are learned from training data
    """
    
    # Platt scaling coefficients (learned during training)
    # These are example values - in production, compute from validation set
    if is_v1:
        a, b = 1.2, -0.3  # V1 calibration
    else:
        a, b = 1.1, -0.2  # V3 calibration
    
    try:
        calibrated = 1.0 / (1.0 + np.exp(-(a * prob + b)))
        return float(np.clip(calibrated, 0.0, 1.0))
    except:
        return prob  # Return uncalibrated if error


def _calculate_confidence(probability: float) -> float:
    """
    Calculate model confidence in prediction
    Higher confidence at extremes (very low or very high probability)
    Lower confidence near 0.5
    """
    # Confidence = 1 - distance from 0.5
    distance_from_half = abs(probability - 0.5)
    confidence = (distance_from_half * 2)  # Scale to 0-1
    return max(0.0, min(1.0, confidence))


def _make_cost_aware_decision(
    probability: float,
    risk_score: int,
    features: Dict[str, Any],
    custom_thresholds: Dict[str, float] = None
) -> Dict[str, str]:
    """
    Three-tier cost-aware decision system
    Optimized for scenario where FP cost > FN cost
    (Rejecting good tenants is MORE expensive than accepting bad ones)
    
    Tier 1: AUTO_APPROVE (prob < threshold)
    Tier 2: MANUAL_REVIEW (threshold <= prob < high_threshold)
    Tier 3: AUTO_REJECT (prob >= high_threshold)
    
    Args:
        probability: Calibrated probability of default
        risk_score: Risk score (0-100)
        features: Engineered features for context
        custom_thresholds: Optional custom thresholds
    
    Returns:
        Dict with risk_category, recommendation, reasoning, and decision_tier
    """
    
    # Use custom thresholds if provided, otherwise use defaults from constants
    from config.constants import (
        AUTO_APPROVE_THRESHOLD, 
        MANUAL_REVIEW_THRESHOLD, 
        AUTO_REJECT_THRESHOLD
    )
    
    if custom_thresholds:
        approve_threshold = custom_thresholds.get('auto_approve', AUTO_APPROVE_THRESHOLD)
        manual_threshold = custom_thresholds.get('manual_review', MANUAL_REVIEW_THRESHOLD)
        reject_threshold = custom_thresholds.get('auto_reject', AUTO_REJECT_THRESHOLD)
    else:
        approve_threshold = AUTO_APPROVE_THRESHOLD
        manual_threshold = MANUAL_REVIEW_THRESHOLD
        reject_threshold = AUTO_REJECT_THRESHOLD
    
    # Extract key features for context
    credit_score = features.get('credit_score', 0)
    monthly_income = features.get('monthly_income', 0)
    monthly_rent = features.get('monthly_rent', 0)
    previous_evictions = features.get('previous_evictions', 0)
    rent_to_income_ratio = features.get('rent_to_income_ratio', 0)
    
    # Tier 1: AUTO_APPROVE
    if probability < approve_threshold:
        return {
            "risk_category": "LOW",
            "recommendation": "AUTO_APPROVE",
            "decision_tier": "TIER_1_AUTO_APPROVE",
            "reasoning": f"Low default probability ({probability:.1%}). Strong applicant profile."
        }
    
    # Tier 3: AUTO_REJECT (only for extreme cases)
    elif probability >= reject_threshold:
        # Auto-reject if ANY of these severe conditions are met:
        # - Multiple evictions (2+) with poor credit
        # - Any evictions with very high probability (>85%)
        # - No evictions but extremely high risk (>90%) and poor credit
        
        if previous_evictions >= 2 and credit_score < 600:
            return {
                "risk_category": "HIGH",
                "recommendation": "REJECT",
                "decision_tier": "TIER_3_AUTO_REJECT",
                "reasoning": f"Very high default probability ({probability:.1%}). Multiple evictions and poor credit."
            }
        elif previous_evictions >= 1 and probability >= 0.85:
            return {
                "risk_category": "HIGH",
                "recommendation": "REJECT",
                "decision_tier": "TIER_3_AUTO_REJECT",
                "reasoning": f"Extremely high default probability ({probability:.1%}) with eviction history."
            }
        elif previous_evictions == 0 and probability >= 0.90 and credit_score < 600:
            return {
                "risk_category": "HIGH",
                "recommendation": "REJECT",
                "decision_tier": "TIER_3_AUTO_REJECT",
                "reasoning": f"Near-certain default ({probability:.1%}) with poor credit."
            }
        else:
            # Downgrade to manual review if no strong negative indicators
            return {
                "risk_category": "HIGH",
                "recommendation": "MANUAL_REVIEW",
                "decision_tier": "TIER_2_MANUAL_REVIEW",
                "reasoning": f"High probability ({probability:.1%}) but warrants human review."
            }
    
    # Tier 2: MANUAL_REVIEW
    else:
        # Sub-categorize within manual review
        mid_point = (approve_threshold + manual_threshold) / 2
        
        if probability < mid_point:
            # Lower risk manual review
            return {
                "risk_category": "LOW-MEDIUM",
                "recommendation": "MANUAL_REVIEW",
                "decision_tier": "TIER_2_MANUAL_REVIEW",
                "reasoning": f"Moderate probability ({probability:.1%}). Recommend approval with income verification."
            }
        elif probability < manual_threshold:
            # Mid-range manual review
            return {
                "risk_category": "MEDIUM",
                "recommendation": "MANUAL_REVIEW",
                "decision_tier": "TIER_2_MANUAL_REVIEW",
                "reasoning": f"Elevated risk ({probability:.1%}). Consider co-signer or increased deposit."
            }
        else:
            # Higher risk manual review
            return {
                "risk_category": "MEDIUM-HIGH",
                "recommendation": "MANUAL_REVIEW",
                "decision_tier": "TIER_2_MANUAL_REVIEW",
                "reasoning": f"High probability ({probability:.1%}). Review financial history and references carefully."
            }


def get_feature_importance(is_v1: bool = True) -> Dict[str, float]:
    """Get feature importance from model"""
    try:
        model = V1_MODEL if is_v1 else V3_MODEL
        features = V1_FEATURES if is_v1 else V3_FEATURES
        
        if model is None:
            return {}
        
        importances = model.feature_importances_
        feature_dict = dict(zip(features, importances))
        
        # Sort by importance
        return dict(sorted(feature_dict.items(), key=lambda x: x[1], reverse=True))
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        return {}


def calculate_dynamic_thresholds(
    fp_cost: float = 5000.0,
    fn_cost: float = 3000.0,
    vacancy_rate: float = 0.05,
    application_volume: str = "normal"
) -> Dict[str, float]:
    """
    Calculate dynamic thresholds based on business context
    
    Args:
        fp_cost: Cost of rejecting a good tenant (default: $5,000 - lost rent)
        fn_cost: Cost of accepting a bad tenant (default: $3,000 - eviction, etc.)
        vacancy_rate: Current market vacancy rate (0-1)
        application_volume: "high", "normal", or "low"
    
    Returns:
        Dict with auto_approve, manual_review, and auto_reject thresholds
    """
    from config.constants import (
        AUTO_APPROVE_THRESHOLD,
        MANUAL_REVIEW_THRESHOLD,
        AUTO_REJECT_THRESHOLD
    )
    
    # Start with base thresholds
    approve = AUTO_APPROVE_THRESHOLD
    manual = MANUAL_REVIEW_THRESHOLD
    reject = AUTO_REJECT_THRESHOLD
    
    # Adjust based on cost ratio
    cost_ratio = fp_cost / fn_cost
    
    if cost_ratio > 1.5:  # FP cost significantly higher
        # Be more lenient (approve more, reject less)
        approve += 0.05
        manual += 0.05
        reject += 0.05
    elif cost_ratio < 0.7:  # FN cost higher
        # Be more strict (approve less, reject more)
        approve -= 0.05
        manual -= 0.05
        reject -= 0.05
    
    # Adjust based on vacancy rate
    if vacancy_rate > 0.10:  # High vacancy - need tenants
        approve += 0.05
        manual += 0.05
    elif vacancy_rate < 0.03:  # Low vacancy - can be selective
        approve -= 0.05
        manual -= 0.05
    
    # Adjust based on application volume
    if application_volume == "high":
        # Lots of applicants - can be more selective
        approve -= 0.03
        manual -= 0.03
    elif application_volume == "low":
        # Few applicants - need to be more lenient
        approve += 0.03
        manual += 0.03
    
    # Ensure thresholds stay in valid ranges
    approve = max(0.20, min(0.50, approve))
    manual = max(0.50, min(0.80, manual))
    reject = max(0.75, min(0.95, reject))
    
    return {
        "auto_approve": round(approve, 2),
        "manual_review": round(manual, 2),
        "auto_reject": round(reject, 2),
        "cost_ratio": round(cost_ratio, 2),
        "reasoning": f"FP cost ${fp_cost:,.0f} vs FN cost ${fn_cost:,.0f} (ratio: {cost_ratio:.2f})"
    }
