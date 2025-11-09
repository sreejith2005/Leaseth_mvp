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
    request_id: str = None
) -> Dict[str, Any]:
    """
    Hybrid model routing and prediction
    
    Args:
        engineered_features: Feature engineering output (from features.py)
        request_id: Request ID for logging
    
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
        
        # Calibration: Convert raw probability to calibrated probability
        # Using Platt scaling approximation
        calibrated_probability = _calibrate_probability(probability, use_v1_model)
        
        # Convert to risk score (0-100)
        risk_score = int(round(calibrated_probability * 100))
        risk_score = max(0, min(100, risk_score))  # Clip to 0-100
        
        # Categorize risk
        if risk_score < 30:
            risk_category = "LOW"
            recommendation = "APPROVE"
        elif risk_score < 60:
            risk_category = "MEDIUM"
            recommendation = "REQUEST_INFO"
        else:
            risk_category = "HIGH"
            recommendation = "REJECT"
        
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
            "calibrated_probability": float(calibrated_probability),
            "risk_score": risk_score,
            "risk_category": risk_category,
            "recommendation": recommendation,
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
