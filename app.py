"""Leaseth Rental Income Advance API
Evaluates rental income streams and generates cash offers for property owners.

ARCHITECTURE:
- Two-stage scoring: Stage 1 (eviction check) + Stage 2 (ML model)
- Model: XGBoost trained on honest_model.py
- Features: Loaded from honest_features.pkl (21 features)
- Offer calculation: Converts reliability score to cash offer via discount rate
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pickle
import pandas as pd
import numpy as np
from typing import Optional, List
import logging
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

import os
from src.database import SessionLocal, Application, Score, init_db, get_db
from src.offer_calculator import calculate_offer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Leaseth Rental Income Advance API", version="3.0.0")

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
def startup():
    """Initialize database and load model"""
    # Initialize database tables
    init_db()
    logger.info("Database initialized")

    # Load the model
    load_model()


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

# Keep old name as alias for backward compatibility
class ApplicantInput(BaseModel):
    """Property submission for rental income advance evaluation"""
    # Submission ID
    applicant_id: str = Field(..., description="Unique submission ID")
    
    # Tenant Info (existing tenant, NOT prospective)
    name: str = Field(..., description="Current tenant name")
    age: int = Field(..., ge=18, le=120, description="Tenant age")
    
    # Financial
    monthly_income: float = Field(..., gt=0, description="Tenant monthly income")
    credit_score: int = Field(..., ge=300, le=850, description="Tenant credit score")
    monthly_rent: float = Field(..., gt=0, description="Monthly rent amount")
    security_deposit: float = Field(default=0, ge=0)
    
    # Employment & Verification
    employment_status: str = Field(default="employed", description="Tenant employment status")
    employment_verified: bool = Field(default=False)
    income_verified: bool = Field(default=False)
    
    # Tenant Rental History
    previous_evictions: int = Field(default=0, ge=0)
    rental_history_years: float = Field(default=0, ge=0)
    on_time_payments_percent: float = Field(default=100, ge=0, le=100)
    late_payments_count: int = Field(default=0, ge=0)
    
    # Property & Lease
    lease_term_months: int = Field(default=12, ge=1, le=60, description="Remaining lease months")
    months_to_sell: int = Field(default=12, ge=1, le=60, description="Months of rent to sell")
    bedrooms: int = Field(default=1, ge=1)
    property_type: str = Field(default="apartment", description="Property type")
    location: str = Field(default="Mumbai", description="City/Location")
    property_address: str = Field(default="", description="Property address")
    
    # Market Context
    market_median_rent: float = Field(default=0, ge=0)
    local_unemployment_rate: float = Field(default=5.0, ge=0)
    inflation_rate: float = Field(default=3.0, ge=0)


class ScoringResponse(BaseModel):
    """Response with offer details for rental income advance"""
    success: bool
    applicant_id: str
    
    # Risk assessment (kept for internal use)
    risk_score: int  # 0-100
    risk_category: str  # LOW, MEDIUM, HIGH
    default_probability: float  # 0-1
    recommendation: str  # APPROVE, MANUAL_REVIEW, REJECT (legacy)
    confidence: float  # 0-1
    reasoning: str
    
    # Offer details (new for rental income advance)
    reliability_score: int = 0         # 0-100 (inverted risk: higher = more reliable)
    offer_status: str = "NO_OFFER"     # OFFERED or NO_OFFER
    offer_amount: float = 0.0          # Cash offer amount
    gross_rental_value: float = 0.0    # Total value of rent stream
    discount_rate: float = 0.0         # Discount percentage applied
    discount_amount: float = 0.0       # Amount discounted
    months_purchased: int = 0          # Months of rent being purchased
    

# ============================================================
# Main Scoring Endpoint
# ============================================================

@app.post("/api/score", response_model=ScoringResponse)
async def score_applicant(applicant: ApplicantInput, db: Session = Depends(get_db)):
    """
    Evaluate a rental income stream and generate a cash offer.
    Uses two-stage approach:
    - Stage 1: Tenant reliability check (eviction history)
    - Stage 2: ML model prediction -> reliability score -> offer calculation
    Persists submission and offer to database.
    """
    import time
    start_time = time.time()

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
            inference_time_ms = (time.time() - start_time) * 1000

            # Persist rejection to database
            try:
                db_application = Application(
                    user_id=1,
                    applicant_id=applicant.applicant_id,
                    applicant_name=applicant.name,
                    monthly_income=applicant.monthly_income,
                    monthly_rent=applicant.monthly_rent,
                    credit_score=applicant.credit_score,
                    rental_history_years=applicant.rental_history_years,
                    previous_evictions=applicant.previous_evictions,
                    employment_verified=applicant.employment_verified,
                    income_verified=applicant.income_verified,
                    raw_data=applicant.model_dump(),
                )
                db.add(db_application)
                db.flush()

                db_score = Score(
                    application_id=db_application.id,
                    request_id=str(uuid.uuid4()),
                    user_id=1,
                    default_probability=0.95,
                    risk_score=95,
                    risk_category='HIGH',
                    recommendation='REJECT',
                    confidence_score=0.90,
                    model_version="V2_2025_01",
                    inference_time_ms=inference_time_ms,
                )
                db.add(db_score)
                db.commit()
            except Exception as db_error:
                logger.error(f"Failed to persist Stage 1 rejection: {db_error}")
                db.rollback()

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
                gross_rental_value=applicant.monthly_rent * getattr(applicant, 'months_to_sell', applicant.lease_term_months),
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
        logger.info(
            f"Scored {applicant.applicant_id}: "
            f"Base={base_probability:.2%}, Calibrated={calibrated_probability:.2%}, "
            f"Eviction+={eviction_penalty:.2%}, Final={final_probability:.2%} ({risk_score}%), "
            f"Rec={decision['recommendation']}"
        )

        # Calculate inference time
        inference_time_ms = (time.time() - start_time) * 1000

        # Persist to database
        try:
            # Create Application record
            db_application = Application(
                user_id=1,  # Default user for now (no auth)
                applicant_id=applicant.applicant_id,
                applicant_name=applicant.name,
                monthly_income=applicant.monthly_income,
                monthly_rent=applicant.monthly_rent,
                credit_score=applicant.credit_score,
                rental_history_years=applicant.rental_history_years,
                previous_evictions=applicant.previous_evictions,
                employment_verified=applicant.employment_verified,
                income_verified=applicant.income_verified,
                raw_data=applicant.model_dump(),
            )
            db.add(db_application)
            db.flush()  # Get the application ID

            # Create Score record
            db_score = Score(
                application_id=db_application.id,
                request_id=str(uuid.uuid4()),
                user_id=1,
                default_probability=final_probability,
                risk_score=risk_score,
                risk_category=decision['risk_category'],
                recommendation=decision['recommendation'],
                confidence_score=abs(final_probability - 0.5) * 2,
                model_version="V3_2026_02",
                inference_time_ms=inference_time_ms,
                reliability_score=reliability_score,
                offer_status=offer.offer_status,
                offer_amount=offer.offer_amount,
                gross_rental_value=offer.gross_rental_value,
                discount_rate=offer.discount_rate,
                months_purchased=months_to_sell if offer.offer_status == 'OFFERED' else 0,
            )
            db.add(db_score)
            db.commit()
            logger.info(f"Persisted application {db_application.id} and score {db_score.id}")
        except Exception as db_error:
            logger.error(f"Failed to persist to database: {db_error}")
            db.rollback()
            # Continue returning response even if persistence fails

        # ============================================================
        # OFFER CALCULATION
        # ============================================================
        reliability_score = max(0, min(100, 100 - risk_score))
        months_to_sell = getattr(applicant, 'months_to_sell', applicant.lease_term_months)
        
        income_ratio = applicant.monthly_income / applicant.monthly_rent if applicant.monthly_rent > 0 else 10
        offer = calculate_offer(
            monthly_rent=applicant.monthly_rent,
            months_to_sell=months_to_sell,
            reliability_score=reliability_score,
            property_type=applicant.property_type,
            lease_term_months=applicant.lease_term_months,
            credit_score=applicant.credit_score,
            on_time_payments_pct=applicant.on_time_payments_percent,
            income_ratio=income_ratio,
        )
        
        logger.info(
            f"Offer for {applicant.applicant_id}: "
            f"reliability={reliability_score}, status={offer.offer_status}, "
            f"amount=₹{offer.offer_amount:,.0f}"
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
            offer_status=offer.offer_status,
            offer_amount=offer.offer_amount,
            gross_rental_value=offer.gross_rental_value,
            discount_rate=offer.discount_rate,
            discount_amount=offer.discount_amount,
            months_purchased=months_to_sell if offer.offer_status == 'OFFERED' else 0,
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
    1. Uses a CONTINUOUS income/rent curve (no step functions) for smooth sensitivity
    2. Gives credit to applicants with strong financial profiles
    3. Penalizes applicants with very low income relative to rent
    
    Income/rent ratio is the dominant factor. The continuous curve ensures
    every dollar of income change produces a measurable score difference.
    
    Boundaries:
    - Below 1.5x: penalty applied (income too low for rent)
    - 1.5x to 6.0x: continuous improvement curve
    - Above 6.0x: capped (no further benefit)
    """
    
    # Calculate financial strength indicators
    income = features['monthly_income']
    rent = features['monthly_rent']
    credit = features['credit_score']
    income_ratio = income / rent if rent > 0 else 10
    
    # ---- Income penalty for very low income/rent ratios ----
    # If income barely covers rent, ADD risk to the raw probability
    income_penalty = 0.0
    if income_ratio < 2.0:
        # Linear penalty: +0.08 at ratio=1.0, tapering to 0 at ratio=2.0
        income_penalty = 0.08 * max(0, (2.0 - income_ratio) / 1.0)
        income_penalty = min(0.08, income_penalty)  # Cap at +8%
    
    penalized_prob = min(0.99, raw_prob + income_penalty)
    
    # ---- Financial strength score (0 to 0.6, continuous) ----
    financial_strength = 0.0
    
    # Income ratio bonus: CONTINUOUS curve over [1.5, 6.0] → [0, 0.35]
    # Every fractional change in income/rent ratio produces a different score
    INCOME_FLOOR = 1.5
    INCOME_CAP = 6.0
    MAX_INCOME_BONUS = 0.35
    
    if income_ratio >= INCOME_CAP:
        financial_strength += MAX_INCOME_BONUS
    elif income_ratio > INCOME_FLOOR:
        # Linear interpolation: (ratio - 1.5) / (6.0 - 1.5) * 0.35
        financial_strength += MAX_INCOME_BONUS * (income_ratio - INCOME_FLOOR) / (INCOME_CAP - INCOME_FLOOR)
    # else: ratio <= 1.5 → no income bonus (0)
    
    # Credit score bonus (unchanged)
    if credit >= 750:
        financial_strength += 0.2  # Excellent
    elif credit >= 700:
        financial_strength += 0.15  # Good
    elif credit >= 670:
        financial_strength += 0.1  # Fair
    elif credit >= 620:
        financial_strength += 0.05  # Subprime but not terrible
    
    # Verification bonus (unchanged)
    if features['employment_verified'] and features['income_verified']:
        financial_strength += 0.1  # Both verified
    elif features['employment_verified'] or features['income_verified']:
        financial_strength += 0.05  # One verified
    
    # Cap financial strength at 0.6 (raised from 0.5 to widen range)
    financial_strength = min(0.6, financial_strength)
    
    # Apply leniency reduction based on financial strength
    # Multiplier 0.7 (raised from 0.6) so income changes have ~2x more effect
    calibrated = penalized_prob * (1.0 - financial_strength * 0.7)
    
    # No global compression — removed the old ×0.85 that flattened all differences
    # The continuous curve + penalty above already handles the full range
    
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
    
    # Continuous first-time renter adjustment based on income ratio and credit
    # Instead of two discrete steps, interpolate the reduction for smoother sensitivity
    
    # Income component: 0 at ratio<=2.0, scaling to 1.0 at ratio>=5.0
    income_factor = max(0.0, min(1.0, (income_ratio - 2.0) / 3.0))
    
    # Credit component: 0 at credit<=600, scaling to 1.0 at credit>=750
    credit_factor = max(0.0, min(1.0, (credit - 600) / 150.0))
    
    # Verification component: 0, 0.5, or 1.0
    verification_factor = 0.0
    if employment_verified and income_verified:
        verification_factor = 1.0
    elif employment_verified or income_verified:
        verification_factor = 0.5
    
    # Combined strength: weighted average (income matters most)
    combined_strength = (income_factor * 0.5) + (credit_factor * 0.35) + (verification_factor * 0.15)
    
    # Maximum reduction: -0.15 for perfect profile, scaling down to 0 for weak
    max_reduction = 0.15
    reduction = combined_strength * max_reduction
    
    if reduction > 0.02:  # Only apply if meaningful
        floor = 0.05 if combined_strength >= 0.7 else 0.10
        adjusted = max(floor, probability - reduction)
        return adjusted, f"First-time renter adjustment: -{reduction:.1%} (strength={combined_strength:.2f})."
    
    return probability, None


def make_decision(probability: float, risk_score: int, features: dict, eviction_reasoning: str = "") -> dict:
    """
    Three-tier decision logic with more lenient thresholds.
    
    Thresholds (after adjustments):
    - LOW RISK: < 38% -> APPROVE
    - MEDIUM RISK: 38-65% -> MANUAL_REVIEW
    - HIGH RISK: > 65% -> REJECT
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
# Applicants List Endpoint
# ============================================================

class StoredApplicantResponse(BaseModel):
    """Response model for stored applicant data"""
    id: str
    input: dict
    result: dict
    scored_at: str


@app.get("/api/applicants", response_model=List[StoredApplicantResponse])
async def get_applicants(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Retrieve all scored applicants from database.
    Returns data in format compatible with frontend StoredApplicant type.
    """
    try:
        # Query applications with their scores, ordered by most recent first
        applications = db.query(Application).order_by(
            Application.created_at.desc()
        ).offset(skip).limit(limit).all()

        result = []
        for app_record in applications:
            # Get the associated score
            score = db.query(Score).filter(
                Score.application_id == app_record.id
            ).first()

            if score is None:
                continue  # Skip applications without scores

            # Build the response in frontend-compatible format
            stored_applicant = StoredApplicantResponse(
                id=app_record.applicant_id,
                input=app_record.raw_data or {
                    "applicant_id": app_record.applicant_id,
                    "name": app_record.applicant_name,
                    "monthly_income": app_record.monthly_income,
                    "monthly_rent": app_record.monthly_rent,
                    "credit_score": app_record.credit_score,
                    "rental_history_years": app_record.rental_history_years,
                    "previous_evictions": app_record.previous_evictions,
                    "employment_verified": app_record.employment_verified,
                    "income_verified": app_record.income_verified,
                },
                result={
                    "applicant_id": app_record.applicant_id,
                    "risk_score": score.risk_score,
                    "risk_category": score.risk_category,
                    "recommendation": score.recommendation,
                    "confidence": score.confidence_score,
                    "reasoning": f"Risk score: {score.risk_score}%",
                    "processing_time_ms": score.inference_time_ms,
                    "reliability_score": max(0, 100 - score.risk_score),
                    "offer_status": getattr(score, 'offer_status', 'OFFERED' if score.risk_score < 60 else 'NO_OFFER'),
                    "offer_amount": getattr(score, 'offer_amount', 0),
                    "gross_rental_value": getattr(score, 'gross_rental_value', 0),
                    "discount_rate": getattr(score, 'discount_rate', 0),
                    "months_purchased": getattr(score, 'months_purchased', 0),
                },
                scored_at=app_record.created_at.isoformat() if app_record.created_at else datetime.utcnow().isoformat(),
            )
            result.append(stored_applicant)

        return result
    except Exception as e:
        logger.error(f"Failed to fetch applicants: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
        "name": "Leaseth Rental Income Advance API",
        "version": "3.0.0",
        "description": "Evaluate rental income streams and get cash offers",
        "endpoints": {
            "score": "POST /api/score",
            "submissions": "GET /api/applicants",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
