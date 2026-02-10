"""
Simple FastAPI for Lovable Dashboard Integration
Minimal setup - just score endpoint

ARCHITECTURE:
- Two-stage scoring: Stage 1 (eviction check) + Stage 2 (ML model)
- Model: XGBoost trained on honest_model.py
- Features: Loaded from honest_features.pkl (21 features)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pickle
import pandas as pd
import numpy as np
from typing import Optional
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Leaseth Scoring API", version="2.0.0")

# CORS - Allow Lovable frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify Lovable domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model at startup
MODEL = None
FEATURES = None

# Employment type mapping (must match training data encoding)
EMPLOYMENT_TYPE_MAP = {
    'full-time': 1, 'Full-time': 1, 'employed': 1, 'Employed': 1,
    'part-time': 2, 'Part-time': 2,
    'self-employed': 3, 'Self-employed': 3,
    'freelance': 0, 'Freelance': 0,
    'unemployed': 4, 'Unemployed': 4,
    'unknown': 0, 'Unknown': 0
}

# Property type mapping
PROPERTY_TYPE_MAP = {
    'apartment': 0, 'Apartment': 0,
    'condo': 1, 'Condo': 1,
    'studio': 2, 'Studio': 2,
    'villa': 3, 'Villa': 3,
    'house': 3, 'House': 3,
    'unknown': 0, 'Unknown': 0
}

# City mapping
CITY_MAP = {
    'bangalore': 0, 'Bangalore': 0,
    'delhi': 1, 'Delhi': 1,
    'hyderabad': 2, 'Hyderabad': 2,
    'mumbai': 3, 'Mumbai': 3,
    'pune': 4, 'Pune': 4,
    'chennai': 0, 'Chennai': 0,
    'unknown': 0, 'Unknown': 0
}

@app.on_event("startup")
def load_model():
    """Load the honest model and features from pickle files"""
    global MODEL, FEATURES
    try:
        logger.info("Loading honest model...")
        with open('models/honest_model.pkl', 'rb') as f:
            MODEL = pickle.load(f)
        
        # CRITICAL: Load features from pickle - must match training order exactly
        with open('models/honest_features.pkl', 'rb') as f:
            FEATURES = pickle.load(f)
        
        logger.info(f"Model loaded successfully with {len(FEATURES)} features")
        logger.info(f"Features: {FEATURES}")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

# ============================================================
# Request/Response Models
# ============================================================

class ApplicantInput(BaseModel):
    """Input from Lovable dashboard"""
    # Basic Info
    applicant_id: str = Field(..., description="Unique applicant ID")
    name: str = Field(..., description="Applicant name")
    age: int = Field(..., ge=18, le=120, description="Age")
    
    # Financial
    monthly_income: float = Field(..., gt=0, description="Monthly income")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score")
    monthly_rent: float = Field(..., gt=0, description="Monthly rent")
    security_deposit: float = Field(default=0, ge=0)
    
    # Employment & Verification
    employment_status: str = Field(default="employed", description="Employment status")
    employment_verified: bool = Field(default=False)
    income_verified: bool = Field(default=False)
    
    # Rental History
    previous_evictions: int = Field(default=0, ge=0)
    rental_history_years: float = Field(default=0, ge=0)
    on_time_payments_percent: float = Field(default=100, ge=0, le=100)
    late_payments_count: int = Field(default=0, ge=0)
    
    # Property
    lease_term_months: int = Field(default=12, ge=1, le=60)
    bedrooms: int = Field(default=1, ge=1)
    property_type: str = Field(default="apartment", description="Property type")
    location: str = Field(default="Mumbai", description="City/Location")
    
    # Market Context
    market_median_rent: float = Field(default=0, ge=0)
    local_unemployment_rate: float = Field(default=5.0, ge=0)
    inflation_rate: float = Field(default=3.0, ge=0)


class ScoringResponse(BaseModel):
    """Response to Lovable dashboard"""
    success: bool
    applicant_id: str
    risk_score: int  # 0-100
    risk_category: str  # LOW, MEDIUM, HIGH
    default_probability: float  # 0-1
    recommendation: str  # APPROVE, MANUAL_REVIEW, REJECT
    confidence: float  # 0-1
    reasoning: str
    

# ============================================================
# Main Scoring Endpoint
# ============================================================

@app.post("/api/score", response_model=ScoringResponse)
async def score_applicant(applicant: ApplicantInput):
    """
    Score a tenant applicant using two-stage approach:
    - Stage 1: Eviction check and first-time renter adjustment
    - Stage 2: ML model prediction with adjustments
    """
    try:
        if MODEL is None or FEATURES is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Engineer features (maps input to model's expected format)
        features = engineer_features(applicant)
        
        # ============================================================
        # STAGE 1: Eviction Check
        # ============================================================
        eviction_penalty, stage1_decision, eviction_reasoning = stage_1_eviction_check(features)
        
        # If Stage 1 says immediate reject (3+ evictions with poor credit)
        if stage1_decision == 'REJECT':
            logger.info(f"Stage 1 REJECT for {applicant.applicant_id}: {eviction_reasoning}")
            return ScoringResponse(
                success=True,
                applicant_id=applicant.applicant_id,
                risk_score=95,  # High risk score for auto-reject
                risk_category='HIGH',
                default_probability=0.95,
                recommendation='REJECT',
                confidence=0.90,
                reasoning=eviction_reasoning
            )
        
        # ============================================================
        # STAGE 2: ML Model Prediction
        # ============================================================
        
        # Create feature array in correct order (must match FEATURES from pickle)
        try:
            X = np.array([[features[f] for f in FEATURES]])
        except KeyError as e:
            logger.error(f"Missing feature: {e}")
            raise HTTPException(status_code=500, detail=f"Missing feature: {e}")
        
        # Get base prediction from ML model
        base_probability = MODEL.predict_proba(X)[0][1]
        
        # ============================================================
        # CALIBRATION: Adjust model output for leniency
        # The model was trained on synthetic data with 15% default rate
        # which may be overly pessimistic. We apply a scaling to be more lenient.
        # ============================================================
        calibrated_probability = calibrate_probability(base_probability, features)
        
        # Apply eviction penalty from Stage 1
        adjusted_probability = min(0.99, calibrated_probability + eviction_penalty)
        
        # Apply first-time renter adjustment (reduces probability for strong profiles)
        final_probability, ftr_reason = apply_first_time_renter_adjustment(adjusted_probability, features)
        
        # Build combined reasoning
        combined_reasoning = eviction_reasoning
        if ftr_reason:
            combined_reasoning = f"{eviction_reasoning} {ftr_reason}"
        
        # Convert to risk score (0-100)
        risk_score = int(round(final_probability * 100))
        risk_score = max(0, min(100, risk_score))
        
        # Make final decision with adjusted probability
        decision = make_decision(final_probability, risk_score, features, combined_reasoning)
        
        # Log detailed scoring info
        logger.info(
            f"Scored {applicant.applicant_id}: "
            f"Base={base_probability:.2%}, Calibrated={calibrated_probability:.2%}, "
            f"Eviction+={eviction_penalty:.2%}, Final={final_probability:.2%} ({risk_score}%), "
            f"Rec={decision['recommendation']}"
        )
        
        return ScoringResponse(
            success=True,
            applicant_id=applicant.applicant_id,
            risk_score=risk_score,
            risk_category=decision['risk_category'],
            default_probability=final_probability,
            recommendation=decision['recommendation'],
            confidence=abs(final_probability - 0.5) * 2,  # Higher confidence at extremes
            reasoning=decision['reasoning']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scoring failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Calibration Function
# ============================================================

def calibrate_probability(raw_prob: float, features: dict) -> float:
    """
    Calibrate raw model probability to be more lenient while preserving ordering.
    
    The model was trained on synthetic data that may overestimate default risk.
    This calibration:
    1. Applies a sigmoid compression to reduce extreme predictions
    2. Gives credit to applicants with strong financial profiles
    
    The goal is to make the model more lenient for borderline cases
    while still being strict for truly risky applicants.
    """
    
    # Calculate financial strength indicators
    income = features['monthly_income']
    rent = features['monthly_rent']
    credit = features['credit_score']
    income_ratio = income / rent if rent > 0 else 10
    
    # Financial strength score (0-1)
    # Higher = stronger financial profile = more leniency
    financial_strength = 0.0
    
    # Income ratio bonus (3x+ income is strong)
    if income_ratio >= 5:
        financial_strength += 0.3  # Very strong
    elif income_ratio >= 4:
        financial_strength += 0.2  # Strong
    elif income_ratio >= 3:
        financial_strength += 0.1  # Adequate
    
    # Credit score bonus
    if credit >= 750:
        financial_strength += 0.2  # Excellent
    elif credit >= 700:
        financial_strength += 0.15  # Good
    elif credit >= 670:
        financial_strength += 0.1  # Fair
    elif credit >= 620:
        financial_strength += 0.05  # Subprime but not terrible
    
    # Verification bonus
    if features['employment_verified'] and features['income_verified']:
        financial_strength += 0.1  # Both verified
    elif features['employment_verified'] or features['income_verified']:
        financial_strength += 0.05  # One verified
    
    # Cap financial strength at 0.5 (max reduction)
    financial_strength = min(0.5, financial_strength)
    
    # Apply leniency reduction based on financial strength
    # Strong profiles get probability reduced, weak profiles stay same
    calibrated = raw_prob * (1.0 - financial_strength * 0.6)
    
    # Also apply general scaling to be more lenient
    # Compress the probability range: 0-1 becomes roughly 0-0.8
    calibrated = calibrated * 0.85
    
    # Ensure we don't go below a minimum (maintain some risk assessment)
    calibrated = max(0.05, calibrated)
    
    return calibrated


# ============================================================
# Helper Functions
# ============================================================

def engineer_features(applicant: ApplicantInput) -> dict:
    """
    Create feature dictionary matching the model's expected features.
    Features must match honest_features.pkl exactly:
    ['credit_score', 'monthly_income', 'monthly_rent', 'employment_verified', 
     'income_verified', 'rental_history_years', 'previous_evictions', 'bedrooms', 
     'bathrooms', 'square_feet', 'property_age_years', 'lease_term_months', 
     'market_median_rent', 'local_unemployment_rate', 'inflation_rate', 'furnished', 
     'pets_allowed', 'parking_spaces', 'employment_type', 'property_type', 'city']
    """
    
    # Map employment status to encoded value
    emp_status = applicant.employment_status if hasattr(applicant, 'employment_status') else 'employed'
    employment_type_encoded = EMPLOYMENT_TYPE_MAP.get(emp_status, 1)  # Default to employed
    
    # Map property type to encoded value  
    prop_type = applicant.property_type if hasattr(applicant, 'property_type') else 'apartment'
    property_type_encoded = PROPERTY_TYPE_MAP.get(prop_type, 0)  # Default to apartment
    
    # Map city to encoded value
    location = applicant.location if hasattr(applicant, 'location') else 'Mumbai'
    city_encoded = CITY_MAP.get(location, 3)  # Default to Mumbai
    
    return {
        # Core financial features
        'credit_score': applicant.credit_score,
        'monthly_income': applicant.monthly_income,
        'monthly_rent': applicant.monthly_rent,
        'employment_verified': int(applicant.employment_verified),
        'income_verified': int(applicant.income_verified),
        
        # Rental history (important for risk)
        'rental_history_years': applicant.rental_history_years,
        'previous_evictions': applicant.previous_evictions,
        
        # Property details
        'bedrooms': applicant.bedrooms,
        'bathrooms': getattr(applicant, 'bathrooms', 1),
        'square_feet': getattr(applicant, 'square_feet', 800),
        'property_age_years': getattr(applicant, 'property_age_years', 5),
        'lease_term_months': applicant.lease_term_months,
        
        # Market context
        'market_median_rent': applicant.market_median_rent if applicant.market_median_rent > 0 else applicant.monthly_rent,
        'local_unemployment_rate': applicant.local_unemployment_rate,
        'inflation_rate': applicant.inflation_rate,
        
        # Property amenities
        'furnished': getattr(applicant, 'furnished', 0),
        'pets_allowed': getattr(applicant, 'pets_allowed', 0),
        'parking_spaces': getattr(applicant, 'parking_spaces', 0),
        
        # Encoded categorical features
        'employment_type': employment_type_encoded,
        'property_type': property_type_encoded,
        'city': city_encoded,
    }


def stage_1_eviction_check(features: dict) -> tuple:
    """
    Stage 1: Check for eviction history and apply risk adjustments.
    This runs BEFORE the ML model to handle evictions explicitly.
    
    Returns:
        (eviction_penalty, stage_1_recommendation, reasoning)
        - eviction_penalty: 0.0 to 0.5 (added to ML probability)
        - stage_1_recommendation: None (continue to Stage 2) or 'REJECT' (immediate)
        - reasoning: Explanation string
    """
    evictions = features['previous_evictions']
    credit = features['credit_score']
    income = features['monthly_income']
    rent = features['monthly_rent']
    
    # Calculate income-to-rent ratio (how many times income covers rent)
    income_ratio = income / rent if rent > 0 else 10
    
    # Eviction penalty schedule (adds to base probability)
    if evictions == 0:
        eviction_penalty = 0.0
        reasoning = "No eviction history."
    elif evictions == 1:
        # 1 eviction: +15% risk, but can be mitigated by good credit/income
        if credit >= 700 and income_ratio >= 4:
            eviction_penalty = 0.10  # Reduced penalty for strong profile
            reasoning = "1 prior eviction, but strong financials mitigate risk."
        else:
            eviction_penalty = 0.15
            reasoning = "1 prior eviction increases risk."
    elif evictions == 2:
        # 2 evictions: +25% risk
        if credit >= 750 and income_ratio >= 5:
            eviction_penalty = 0.20  # Strong profile gets some mitigation
            reasoning = "2 prior evictions - significant concern despite good financials."
        else:
            eviction_penalty = 0.30
            reasoning = "2 prior evictions - high risk indicator."
    else:
        # 3+ evictions: +40% risk, immediate rejection if poor credit
        if credit < 600:
            return 0.50, 'REJECT', f"{evictions} prior evictions with poor credit ({credit}) - auto-reject."
        eviction_penalty = 0.40
        reasoning = f"{evictions} prior evictions - very high risk."
    
    return eviction_penalty, None, reasoning


def apply_first_time_renter_adjustment(probability: float, features: dict) -> tuple:
    """
    Adjust probability for first-time renters with strong profiles.
    Don't penalize heavily if they have good income/credit.
    
    IMPORTANT: Only apply reduction if there are NO evictions!
    
    Returns:
        (adjusted_probability, adjustment_reason)
    """
    rental_years = features['rental_history_years']
    evictions = features['previous_evictions']
    
    if rental_years > 0:
        return probability, None  # Not a first-time renter
    
    # CRITICAL: Don't apply first-time renter benefit if they have evictions!
    if evictions > 0:
        return probability, None  # Has evictions - no reduction
    
    # First-time renter with no evictions - check if they have a strong profile
    credit = features['credit_score']
    income = features['monthly_income']
    rent = features['monthly_rent']
    income_ratio = income / rent if rent > 0 else 10
    employment_verified = features['employment_verified']
    income_verified = features['income_verified']
    
    # Strong first-time renter criteria
    strong_profile = (
        credit >= 650 and
        income_ratio >= 3.5 and
        (employment_verified or income_verified)
    )
    
    very_strong_profile = (
        credit >= 700 and
        income_ratio >= 5 and
        employment_verified and
        income_verified
    )
    
    if very_strong_profile:
        # Very strong first-time renter: reduce probability by 15%
        adjusted = max(0.05, probability - 0.15)
        return adjusted, "First-time renter with excellent profile (700+ credit, 5x income) - reduced risk."
    elif strong_profile:
        # Strong first-time renter: reduce probability by 8%
        adjusted = max(0.10, probability - 0.08)
        return adjusted, "First-time renter with good profile - moderate risk reduction."
    
    return probability, None


def make_decision(probability: float, risk_score: int, features: dict, eviction_reasoning: str = "") -> dict:
    """
    Three-tier decision logic with more lenient thresholds.
    
    Thresholds (after adjustments):
    - LOW RISK: < 38% → APPROVE
    - MEDIUM RISK: 38-65% → MANUAL_REVIEW
    - HIGH RISK: > 65% → REJECT
    """
    
    credit = features['credit_score']
    evictions = features['previous_evictions']
    income = features['monthly_income']
    rent = features['monthly_rent']
    income_ratio = income / rent if rent > 0 else 10
    
    base_reasoning = eviction_reasoning
    
    # LOW RISK: < 38% probability (more lenient than before)
    if probability < 0.38:
        return {
            'risk_category': 'LOW',
            'recommendation': 'APPROVE',
            'reasoning': f'Low default risk ({probability:.1%}). Strong applicant profile. {base_reasoning}'
        }
    
    # HIGH RISK: > 65% probability OR severe eviction + poor credit
    elif probability > 0.65 or (evictions >= 3 and credit < 620):
        return {
            'risk_category': 'HIGH',
            'recommendation': 'REJECT',
            'reasoning': f'High default risk ({probability:.1%}). {base_reasoning}'
        }
    
    # MEDIUM RISK: Manual review needed (38-65%)
    else:
        if probability < 0.50:
            # Lean approve for lower end of medium risk
            if income_ratio >= 4 and credit >= 650:
                rec = 'MANUAL_REVIEW (Lean Approve)'
                reason = f'Moderate risk ({probability:.1%}), but good income ratio ({income_ratio:.1f}x). {base_reasoning}'
            else:
                rec = 'MANUAL_REVIEW'
                reason = f'Moderate risk ({probability:.1%}). Recommend income verification. {base_reasoning}'
        else:
            # Lean reject for higher end of medium risk
            if evictions > 0:
                rec = 'MANUAL_REVIEW (Lean Reject)'
                reason = f'Elevated risk ({probability:.1%}) with eviction history. Recommend increased deposit. {base_reasoning}'
            else:
                rec = 'MANUAL_REVIEW'
                reason = f'Elevated risk ({probability:.1%}). Recommend guarantor or increased deposit. {base_reasoning}'
        
        return {
            'risk_category': 'MEDIUM',
            'recommendation': rec,
            'reasoning': reason
        }


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health_check():
    """Check if API is running"""
    return {
        "status": "healthy",
        "model_loaded": MODEL is not None
    }


@app.get("/")
def root():
    """API info"""
    return {
        "name": "Leaseth Scoring API",
        "version": "1.0.0",
        "endpoints": {
            "score": "POST /api/score",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
