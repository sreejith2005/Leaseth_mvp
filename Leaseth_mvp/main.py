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
    'townhouse': 4, 'Townhouse': 4,
    'unknown': 0, 'Unknown': 0
}

# City mapping (global cities from frontend + legacy Indian cities)
CITY_MAP = {
    'London': 0, 'london': 0,
    'Dubai': 1, 'dubai': 1,
    'New York': 2, 'new york': 2,
    'Berlin': 3, 'berlin': 3,
    'Paris': 4, 'paris': 4,
    'Toronto': 5, 'toronto': 5,
    'Sydney': 6, 'sydney': 6,
    'Singapore': 7, 'singapore': 7,
    'Amsterdam': 8, 'amsterdam': 8,
    'Zurich': 9, 'zurich': 9,
    'Mumbai': 10, 'mumbai': 10,
    'São Paulo': 11, 'são paulo': 11, 'Sao Paulo': 11, 'sao paulo': 11,
    'Tokyo': 12, 'tokyo': 12,
    'Riyadh': 13, 'riyadh': 13,
    'Other': 0, 'other': 0,
    'Bangalore': 0, 'bangalore': 0,
    'Delhi': 1, 'delhi': 1,
    'Hyderabad': 2, 'hyderabad': 2,
    'Pune': 4, 'pune': 4,
    'Chennai': 0, 'chennai': 0,
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
    months_to_sell: int = Field(default=12, ge=1, le=60, description="Months of rent to sell")
    bedrooms: int = Field(default=1, ge=1)
    property_type: str = Field(default="apartment", description="Property type")
    location: str = Field(default="Mumbai", description="City/Location")
    property_address: str = Field(default="", description="Property address")
    currency: Optional[str] = Field(default="USD", description="Currency code")
    
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
    
    # Offer details (required by frontend)
    reliability_score: int = 0         # 0-100 (inverted risk: higher = more reliable)
    offer_status: str = "NO_OFFER"     # OFFERED or NO_OFFER
    offer_amount: float = 0.0          # Cash offer amount
    gross_rental_value: float = 0.0    # Total value of rent stream
    discount_rate: float = 0.0         # Discount percentage applied
    discount_amount: float = 0.0       # Amount discounted
    months_purchased: int = 0          # Months of rent being purchased
    

# ============================================================
# Offer Calculation (inline, no external imports needed)
# ============================================================

MIN_RELIABILITY_THRESHOLD = 30  # Lenient: most applicants except high-risk get offers
BASE_DISCOUNT_RATE = 0.10
RISK_PREMIUM_PER_POINT = 0.004
MAX_DISCOUNT_RATE = 0.45

PROPERTY_TYPE_ADJUSTMENTS = {
    'apartment': 0.00, 'house': -0.02, 'condo': 0.01,
    'townhouse': -0.01, 'studio': 0.02, 'villa': -0.02,
}

def calculate_inline_offer(
    monthly_rent: float,
    months_to_sell: int,
    reliability_score: int,
    property_type: str = "apartment",
    lease_term_months: int = 12,
    credit_score: int = 650,
    on_time_payments_pct: float = 90.0,
) -> dict:
    """Calculate a cash offer for purchasing a rental income stream."""
    gross_value = monthly_rent * months_to_sell

    if reliability_score < MIN_RELIABILITY_THRESHOLD:
        return {
            'offer_amount': 0, 'gross_rental_value': gross_value,
            'discount_rate': 0, 'discount_amount': 0, 'offer_status': 'NO_OFFER',
        }

    risk_points = 100 - reliability_score
    base_discount = BASE_DISCOUNT_RATE + (risk_points * RISK_PREMIUM_PER_POINT)
    base_discount += PROPERTY_TYPE_ADJUSTMENTS.get(property_type.lower(), 0.0)

    # Lease term adjustment
    if lease_term_months >= 24:
        base_discount -= 0.03
    elif lease_term_months >= 12:
        base_discount -= 0.01
    elif lease_term_months < 6:
        base_discount += 0.03

    # Payment history bonus
    if on_time_payments_pct >= 95:
        base_discount -= 0.02
    elif on_time_payments_pct >= 85:
        base_discount -= 0.01

    # Credit score bonus
    if credit_score >= 750:
        base_discount -= 0.02
    elif credit_score >= 700:
        base_discount -= 0.01

    # Volume bonus
    if months_to_sell >= 18:
        base_discount -= 0.01
    elif months_to_sell <= 3:
        base_discount += 0.02

    final_discount = max(0.05, min(MAX_DISCOUNT_RATE, base_discount))
    discount_amount = gross_value * final_discount
    offer_amount = gross_value - discount_amount

    return {
        'offer_amount': round(offer_amount, 2),
        'gross_rental_value': gross_value,
        'discount_rate': round(final_discount, 4),
        'discount_amount': round(discount_amount, 2),
        'offer_status': 'OFFERED',
    }


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
            months_to_sell = getattr(applicant, 'months_to_sell', applicant.lease_term_months)
            return ScoringResponse(
                success=True,
                applicant_id=applicant.applicant_id,
                risk_score=95,  # High risk score for auto-reject
                risk_category='HIGH',
                default_probability=0.95,
                recommendation='REJECT',
                confidence=0.90,
                reasoning=eviction_reasoning,
                reliability_score=5,
                offer_status='NO_OFFER',
                offer_amount=0,
                gross_rental_value=applicant.monthly_rent * months_to_sell,
                discount_rate=0,
                discount_amount=0,
                months_purchased=0,
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
        income_ratio = features['monthly_income'] / features['monthly_rent'] if features['monthly_rent'] > 0 else 10
        logger.info(
            f"Scored {applicant.applicant_id}: "
            f"Income/Rent={income_ratio:.1f}x, "
            f"Base={base_probability:.2%}, Calibrated={calibrated_probability:.2%}, "
            f"Eviction+={eviction_penalty:.2%}, Final={final_probability:.2%} ({risk_score}%), "
            f"Rec={decision['recommendation']}"
        )
        
        # ============================================================
        # OFFER CALCULATION
        # ============================================================
        reliability_score = max(0, min(100, 100 - risk_score))
        months_to_sell = getattr(applicant, 'months_to_sell', applicant.lease_term_months)
        offer = calculate_inline_offer(
            monthly_rent=applicant.monthly_rent,
            months_to_sell=months_to_sell,
            reliability_score=reliability_score,
            property_type=applicant.property_type,
            lease_term_months=applicant.lease_term_months,
            credit_score=applicant.credit_score,
            on_time_payments_pct=applicant.on_time_payments_percent,
        )
        
        logger.info(
            f"Offer for {applicant.applicant_id}: "
            f"reliability={reliability_score}, status={offer['offer_status']}, "
            f"amount={offer['offer_amount']:,.0f}"
        )
        
        return ScoringResponse(
            success=True,
            applicant_id=applicant.applicant_id,
            risk_score=risk_score,
            risk_category=decision['risk_category'],
            default_probability=final_probability,
            recommendation=decision['recommendation'],
            confidence=abs(final_probability - 0.5) * 2,  # Higher confidence at extremes
            reasoning=decision['reasoning'],
            reliability_score=reliability_score,
            offer_status=offer['offer_status'],
            offer_amount=offer['offer_amount'],
            gross_rental_value=offer['gross_rental_value'],
            discount_rate=offer['discount_rate'],
            discount_amount=offer['discount_amount'],
            months_purchased=months_to_sell if offer['offer_status'] == 'OFFERED' else 0,
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
    Calibrate raw model probability using financial strength AND rent burden.
    
    The XGBoost model was trained on synthetic data and underweights the
    income-to-rent ratio. This calibration compensates by:
    1. REDUCING probability for genuinely strong profiles (high credit, income, verified)
    2. INCREASING probability when rent burden is dangerously high (income barely covers rent)
    
    This ensures:
    - Excellent profiles (750+ credit, 5x income, verified) → significant reduction
    - Good profiles (700+ credit, 4x income) → moderate reduction
    - Average profiles → model output preserved (no change)
    - High rent burden (income < 2x rent) → explicit penalty added
    - Extreme rent burden (income ≈ rent) → large penalty (near-certain default)
    """
    
    # Calculate financial strength indicators
    income = features['monthly_income']
    rent = features['monthly_rent']
    credit = features['credit_score']
    income_ratio = income / rent if rent > 0 else 10
    
    # ================================================================
    # STEP 1: Financial strength reduction (rewards strong profiles)
    # ================================================================
    # Lenient approach: give meaningful credit for good-to-average profiles
    # so more applicants qualify. Only truly weak profiles get no bonus.
    financial_strength = 0.0
    
    # Income ratio bonus (generous — 3x income is standard industry threshold)
    if income_ratio >= 5:
        financial_strength += 0.30  # Very strong
    elif income_ratio >= 4:
        financial_strength += 0.22  # Strong
    elif income_ratio >= 3:
        financial_strength += 0.15  # Standard (meets 3x rule)
    elif income_ratio >= 2.5:
        financial_strength += 0.05  # Below standard but not terrible
    # Below 2.5x: no bonus
    
    # Credit score bonus (lenient — give credit starting at 620)
    if credit >= 750:
        financial_strength += 0.20  # Excellent credit
    elif credit >= 700:
        financial_strength += 0.15  # Good credit
    elif credit >= 670:
        financial_strength += 0.10  # Fair credit
    elif credit >= 620:
        financial_strength += 0.05  # Subprime but not terrible
    # Below 620: no credit bonus
    
    # Verification bonus
    if features['employment_verified'] and features['income_verified']:
        financial_strength += 0.10  # Both verified — strong signal
    elif features['employment_verified'] or features['income_verified']:
        financial_strength += 0.05  # One verified — partial signal
    # Unverified: no bonus
    
    # Cap financial strength at 0.55 (max 33% probability reduction)
    financial_strength = min(0.55, financial_strength)
    
    # Apply financial strength reduction
    calibrated = raw_prob * (1.0 - financial_strength * 0.6)
    
    # ================================================================
    # STEP 2: Rent burden penalty (penalizes high rent-to-income)
    # ================================================================
    # The ML model doesn't adequately differentiate on income alone.
    # When rent consumes a large portion of income, default risk rises sharply,
    # regardless of what the model predicts. This is a well-known financial rule:
    # - Healthy: rent < 30% of income (ratio > 3.3x)
    # - Stretched: rent 30-40% of income (ratio 2.5-3.3x)
    # - Burdened: rent 40-50% of income (ratio 2.0-2.5x)
    # - Severely burdened: rent > 50% of income (ratio < 2.0x)
    
    rent_burden_penalty = 0.0
    
    if income_ratio < 1.5:
        # EXTREME: rent is 67%+ of income — near-impossible to sustain
        rent_burden_penalty = 0.20
    elif income_ratio < 2.0:
        # SEVERE: rent is 50-67% of income — high default risk
        rent_burden_penalty = 0.12
    elif income_ratio < 2.5:
        # BURDENED: rent is 40-50% of income — moderate concern
        rent_burden_penalty = 0.05
    # ratio >= 2.5: no penalty (manageable rent burden)
    
    calibrated = calibrated + rent_burden_penalty
    
    # ================================================================
    # Final bounds
    # ================================================================
    # Ensure probability stays in valid range
    calibrated = max(0.05, min(0.99, calibrated))
    
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
    
    # LOW RISK: < 45% probability — lenient to accept good/medium tenants
    if probability < 0.45:
        return {
            'risk_category': 'LOW',
            'recommendation': 'APPROVE',
            'reasoning': f'Low default risk ({probability:.1%}). Strong applicant profile. {base_reasoning}'
        }
    
    # HIGH RISK: > 72% probability OR severe eviction + poor credit
    elif probability > 0.72 or (evictions >= 3 and credit < 620):
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
