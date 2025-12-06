"""
Simple FastAPI for Lovable Dashboard Integration
Minimal setup - just score endpoint
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pickle
import pandas as pd
import numpy as np
from typing import Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Leaseth Scoring API", version="1.0.0")

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

@app.on_event("startup")
def load_model():
    """Load the honest model"""
    global MODEL, FEATURES
    try:
        logger.info("Loading honest model...")
        with open('models/honest_model.pkl', 'rb') as f:
            MODEL = pickle.load(f)
        
        # Feature list (from honest_model.py training)
        FEATURES = [
            'credit_score', 'monthly_income', 'monthly_rent',
            'employment_verified', 'income_verified',
            'previous_evictions', 'rental_history_years',
            'on_time_payments_percent', 'late_payments_count',
            'security_deposit', 'lease_term_months',
            'age', 'bedrooms',
            'local_unemployment_rate', 'inflation_rate',
            'market_median_rent',
            # Engineered features
            'rent_to_income_ratio', 'income_stability',
            'verification_score', 'high_rent_burden', 'subprime_credit'
        ]
        
        logger.info("Model loaded successfully")
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
    Score a tenant applicant
    This is the ONLY endpoint Lovable needs to call
    """
    try:
        if MODEL is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Engineer features
        features = engineer_features(applicant)
        
        # Create feature array in correct order
        X = np.array([[features[f] for f in FEATURES]])
        
        # Predict
        probability = MODEL.predict_proba(X)[0][1]
        risk_score = int(round(probability * 100))
        
        # Make decision
        decision = make_decision(probability, risk_score, features)
        
        logger.info(f"Scored {applicant.applicant_id}: {risk_score}% risk, {decision['recommendation']}")
        
        return ScoringResponse(
            success=True,
            applicant_id=applicant.applicant_id,
            risk_score=risk_score,
            risk_category=decision['risk_category'],
            default_probability=probability,
            recommendation=decision['recommendation'],
            confidence=abs(probability - 0.5) * 2,  # Distance from 50%
            reasoning=decision['reasoning']
        )
        
    except Exception as e:
        logger.error(f"Scoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Helper Functions
# ============================================================

def engineer_features(applicant: ApplicantInput) -> dict:
    """Create engineered features"""
    
    # Calculate ratios
    rent_to_income = applicant.monthly_rent / applicant.monthly_income if applicant.monthly_income > 0 else 0
    
    # Income stability (employed + verified + 3x rent rule)
    income_stability = int(
        applicant.employment_verified and 
        applicant.monthly_income >= applicant.monthly_rent * 3
    )
    
    # Verification score
    verification_score = int(applicant.employment_verified) + int(applicant.income_verified)
    
    # High rent burden
    high_rent_burden = int(rent_to_income > 0.4)
    
    # Subprime credit
    subprime_credit = int(applicant.credit_score < 670)
    
    return {
        'credit_score': applicant.credit_score,
        'monthly_income': applicant.monthly_income,
        'monthly_rent': applicant.monthly_rent,
        'employment_verified': int(applicant.employment_verified),
        'income_verified': int(applicant.income_verified),
        'previous_evictions': applicant.previous_evictions,
        'rental_history_years': applicant.rental_history_years,
        'on_time_payments_percent': applicant.on_time_payments_percent,
        'late_payments_count': applicant.late_payments_count,
        'security_deposit': applicant.security_deposit,
        'lease_term_months': applicant.lease_term_months,
        'age': applicant.age,
        'bedrooms': applicant.bedrooms,
        'local_unemployment_rate': applicant.local_unemployment_rate,
        'inflation_rate': applicant.inflation_rate,
        'market_median_rent': applicant.market_median_rent,
        'rent_to_income_ratio': rent_to_income,
        'income_stability': income_stability,
        'verification_score': verification_score,
        'high_rent_burden': high_rent_burden,
        'subprime_credit': subprime_credit
    }


def make_decision(probability: float, risk_score: int, features: dict) -> dict:
    """Simple three-tier decision logic"""
    
    credit = features['credit_score']
    evictions = features['previous_evictions']
    
    # LOW RISK: <30% probability
    if probability < 0.30:
        return {
            'risk_category': 'LOW',
            'recommendation': 'APPROVE',
            'reasoning': f'Low default risk ({probability:.1%}). Strong applicant profile.'
        }
    
    # HIGH RISK: >70% probability OR has evictions
    elif probability > 0.70 or (evictions >= 2 and credit < 600):
        return {
            'risk_category': 'HIGH',
            'recommendation': 'REJECT',
            'reasoning': f'High default risk ({probability:.1%}). Consider alternative housing options.'
        }
    
    # MEDIUM RISK: Manual review needed
    else:
        if probability < 0.50:
            rec = 'MANUAL_REVIEW (Lean Approve)'
            reason = f'Moderate risk ({probability:.1%}). Recommend income verification and co-signer consideration.'
        else:
            rec = 'MANUAL_REVIEW (Lean Reject)'
            reason = f'Elevated risk ({probability:.1%}). Recommend increased deposit or guarantor.'
        
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
    uvicorn.run(app, host="0.0.0.0", port=8002)
