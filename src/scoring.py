"""
Scoring Module for Leaseth

Handles ML model loading, prediction, and risk scoring.
Implements hybrid dual-model routing based on eviction history.
"""

import logging
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

from src.features import create_new_features
from src.offer_calculator import calculate_offer

logger = logging.getLogger(__name__)

# Global model variables (loaded at startup)
V1_MODEL = None  # Model for applicants with evictions
V3_MODEL = None  # Model for applicants without evictions
V1_FEATURES = None
V3_FEATURES = None

MODEL_DIR = Path("models")


def load_models():
    """
    Load trained XGBoost models at application startup.
    Should be called once during FastAPI startup event.
    """
    global V1_MODEL, V3_MODEL, V1_FEATURES, V3_FEATURES
    
    try:
        # Load V1 model (with evictions)
        v1_model_path = MODEL_DIR / "xgboost_model.pkl"
        v1_features_path = MODEL_DIR / "feature_list.pkl"
        
        if v1_model_path.exists() and v1_features_path.exists():
            V1_MODEL = joblib.load(v1_model_path)
            V1_FEATURES = joblib.load(v1_features_path)
            logger.info(f"Loaded V1 model with {len(V1_FEATURES)} features")
        else:
            logger.warning(f"V1 model files not found in {MODEL_DIR}")
        
        # Load V3 model (financial only)
        v3_model_path = MODEL_DIR / "xgboost_model_financial.pkl"
        v3_features_path = MODEL_DIR / "feature_list_financial.pkl"
        
        if v3_model_path.exists() and v3_features_path.exists():
            V3_MODEL = joblib.load(v3_model_path)
            V3_FEATURES = joblib.load(v3_features_path)
            logger.info(f"Loaded V3 model with {len(V3_FEATURES)} features")
        else:
            logger.warning(f"V3 model files not found in {MODEL_DIR}")
            
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        raise


def _calibrate_probability(prob: float, model_type: str = "V3") -> float:
    """
    Apply Platt scaling calibration to raw model probability.
    
    Args:
        prob: Raw probability from model
        model_type: "V1" or "V3"
        
    Returns:
        Calibrated probability
    """
    # Placeholder calibration coefficients
    # In production, these should be computed from a validation set
    if model_type == "V1":
        a, b = 1.2, -0.3
    else:
        a, b = 1.1, -0.2
    
    calibrated = 1.0 / (1.0 + np.exp(-(a * np.log(prob / (1 - prob + 1e-10)) + b)))
    return float(calibrated)


def predict_and_score(
    applicant_data: Dict[str, Any],
    request_id: str = "unknown"
) -> Dict[str, Any]:
    """
    Generate risk score and cash offer for a rental income stream.
    
    Args:
        applicant_data: Dictionary with applicant/property information
        request_id: Unique request ID for logging
        
    Returns:
        Dictionary with risk score, offer details, and reasoning
    """
    logger.info(f"[{request_id}] Starting prediction for applicant")
    
    # Determine which model to use
    previous_evictions = applicant_data.get('previous_evictions', 0)
    model_type = "V1" if previous_evictions > 0 else "V3"
    model = V1_MODEL if previous_evictions > 0 else V3_MODEL
    features = V1_FEATURES if previous_evictions > 0 else V3_FEATURES
    
    if model is None or features is None:
        logger.error(f"[{request_id}] Model not loaded: {model_type}")
        # Return a default response when models aren't available
        return {
            "risk_score": 50,
            "risk_category": "MEDIUM",
            "recommendation": "MANUAL_REVIEW",
            "confidence": 0.5,
            "reasoning": "Model not available - manual review required",
            "reliability_score": 50,
            "offer_status": "NO_OFFER",
            "offer_amount": 0,
            "gross_rental_value": 0,
            "discount_rate": 0,
            "discount_amount": 0,
            "months_purchased": 0,
        }
    
    logger.info(f"[{request_id}] Using {model_type} model")
    
    # Feature engineering
    df = pd.DataFrame([applicant_data])
    df = create_new_features(df)
    
    # Extract required features in correct order
    X = df[features]
    
    # Predict
    if hasattr(model, 'predict_proba'):
        prob = model.predict_proba(X)[0, 1]  # Probability of default
    else:
        prob = model.predict(X)[0]
    
    # Calibrate
    prob = _calibrate_probability(prob, model_type)
    
    # Convert to risk score (0-100, higher = riskier)
    risk_score = int(prob * 100)
    
    # Determine risk category
    if risk_score < 30:
        risk_category = "LOW"
    elif risk_score < 60:
        risk_category = "MEDIUM"
    else:
        risk_category = "HIGH"
    
    # Calculate reliability score (inverse of risk)
    reliability_score = 100 - risk_score
    
    # Calculate cash offer
    offer = calculate_offer(
        monthly_rent=applicant_data['monthly_rent'],
        months_to_sell=applicant_data.get('months_to_sell', 12),
        reliability_score=reliability_score,
        property_type=applicant_data.get('property_type', 'apartment'),
        lease_term_months=applicant_data.get('lease_term_months', 12),
        credit_score=applicant_data.get('credit_score', 650),
        on_time_payments_pct=applicant_data.get('on_time_payments_percent', 90),
    )
    
    # Determine recommendation
    if offer.offer_status == "OFFERED":
        if reliability_score >= 70:
            recommendation = "APPROVE"
            reasoning = f"High reliability income stream (score: {reliability_score}/100). Offer: {offer.offer_amount:,.0f} for {offer.months} months."
        else:
            recommendation = "APPROVE"
            reasoning = f"Moderate reliability (score: {reliability_score}/100). Offer reflects higher discount due to risk factors."
    else:
        recommendation = "REJECT"
        reasoning = f"Reliability score {reliability_score}/100 below minimum threshold (40). Income stream too risky for purchase."
    
    # Confidence (distance from decision boundary)
    confidence = abs(prob - 0.5) * 2
    
    result = {
        "risk_score": risk_score,
        "risk_category": risk_category,
        "recommendation": recommendation,
        "confidence": round(confidence, 3),
        "reasoning": reasoning,
        "default_probability": round(prob, 4),
        "reliability_score": reliability_score,
        "offer_status": offer.offer_status,
        "offer_amount": offer.offer_amount,
        "gross_rental_value": offer.gross_rental_value,
        "discount_rate": offer.discount_rate,
        "discount_amount": offer.discount_amount,
        "months_purchased": offer.months,
    }
    
    logger.info(
        f"[{request_id}] Prediction complete: "
        f"risk={risk_score}, category={risk_category}, "
        f"offer_status={offer.offer_status}, offer_amount={offer.offer_amount:,.0f}"
    )
    
    return result
