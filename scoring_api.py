"""
Local Testing API - Quick Model Testing
FastAPI for fast local testing via /docs endpoint
No HTML interface - just API endpoints for Swagger UI testing
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pickle
import pandas as pd
import numpy as np
import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model = None
features = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load models
    global model, features
    try:
        with open('models/honest_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('models/honest_features.pkl', 'rb') as f:
            features = pickle.load(f)
        logger.info("Models and features loaded successfully")
        logger.info(f"Feature count: {len(features)}")
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        raise
    
    yield  # App runs here
    
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Local Testing API - Quick Model Testing", 
    version="2.0.0",
    description="Fast local testing API. Use /docs for Swagger UI testing interface.",
    lifespan=lifespan
)

# ============================================================
# Request/Response Models
# ============================================================

class ApplicantData(BaseModel):
    # Required fields
    credit_score: int = Field(..., ge=300, le=850, description="Credit score (300-850)")
    monthly_income: float = Field(..., gt=0, description="Monthly income in currency")
    monthly_rent: float = Field(..., gt=0, description="Monthly rent amount")
    
    # Verification fields
    employment_verified: int = Field(default=0, ge=0, le=1, description="1 if verified, 0 otherwise")
    income_verified: int = Field(default=0, ge=0, le=1, description="1 if verified, 0 otherwise")
    
    # Rental history
    rental_history_years: int = Field(default=0, ge=0, description="Years of rental history")
    previous_evictions: int = Field(default=0, ge=0, description="Number of previous evictions")
    
    # Property details
    employment_type: str = Field(default="Full-time", description="Employment type")
    property_type: str = Field(default="Apartment", description="Property type")
    city: str = Field(default="Mumbai", description="City name")
    bedrooms: int = Field(default=2, ge=1, description="Number of bedrooms")
    bathrooms: int = Field(default=1, ge=1, description="Number of bathrooms")
    square_feet: float = Field(default=800, gt=0, description="Property square footage")
    property_age_years: int = Field(default=5, ge=0, description="Age of property in years")
    furnished: int = Field(default=0, ge=0, le=1, description="1 if furnished")
    pets_allowed: int = Field(default=0, ge=0, le=1, description="1 if pets allowed")
    parking_spaces: int = Field(default=0, ge=0, description="Number of parking spaces")
    lease_term_months: int = Field(default=12, ge=1, description="Lease term in months")
    
    # Market context
    market_median_rent: float = Field(default=25000, ge=0, description="Market median rent")
    local_unemployment_rate: float = Field(default=4.5, ge=0, description="Local unemployment rate %")
    inflation_rate: float = Field(default=3.0, ge=0, description="Inflation rate %")

class ScoringResponse(BaseModel):
    decision: str
    stage: int
    risk_probability: float
    rent_to_income_ratio: float
    explanation: str
    metrics: dict

# ============================================================
# Optimized Two-Stage Logic
# ============================================================

def stage_1_quick_reject(row):
    # Bypass Stage 1 completely - let ML model handle all decisions
    # Only catch truly impossible cases
    if row['monthly_rent'] / max(row['monthly_income'], 0.01) > 2.0:
        return 'DECLINE', 'Rent exceeds 200% of income (data error or impossible)'
    
    return 'CONTINUE', 'Bypassing Stage 1 - ML model decides'

def two_stage_decision(row, model, features):
    """Optimized two-stage decision with improved thresholds"""
    decision_1, reason = stage_1_quick_reject(row)
    
    if decision_1 == 'DECLINE':
        return 'DECLINE', 1, 1.0, reason
    elif decision_1 == 'MANUAL_REVIEW':
        return 'MANUAL_REVIEW', 1, 0.8, reason
    else:
        # ML model prediction
        df_feat = pd.DataFrame([row])
        
        # Encode categorical variables
        for col in ['property_type', 'employment_type', 'city']:
            if col in df_feat.columns and df_feat[col].dtype == 'object':
                df_feat[col] = df_feat[col].astype('category').cat.codes
        
        X = df_feat[features]
        risk_prob = model.predict_proba(X)[0, 1]
        
        # Optimized thresholds: Precision 0.2661, Recall 0.6461, F1 0.3770, AUC 0.7203
        if risk_prob < 0.38:
            decision = 'APPROVE'
            explanation = f'Low risk ({risk_prob:.1%}). Applicant approved.'
        elif risk_prob < 0.56:
            decision = 'MANUAL_REVIEW'
            explanation = f'Moderate risk ({risk_prob:.1%}). Recommend manual review.'
        else:
            decision = 'DECLINE'
            explanation = f'High risk ({risk_prob:.1%}). Application declined.'
        
        return decision, 2, risk_prob, explanation

# ============================================================
# API Endpoints
# ============================================================

@app.get("/")
async def root():
    """Root endpoint - Use /docs for interactive testing"""
    return {
        "message": "Local Testing API - Use /docs for Swagger UI interface",
        "instructions": "Go to http://127.0.0.1:8002/docs to test the model",
        "endpoints": {
            "swagger_ui": "/docs",
            "health": "/health",
            "score": "/api/score"
        },
        "model_metrics": {
            "precision": 0.2661,
            "recall": 0.6461,
            "f1_score": 0.3770,
            "auc": 0.7203
        }
    }

@app.post("/api/score", response_model=ScoringResponse)
async def score_applicant(applicant: ApplicantData):
    """Score a tenant applicant using optimized two-stage model"""
    try:
        if model is None or features is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Convert to dict with all fields
        data = {
            'credit_score': applicant.credit_score,
            'monthly_income': applicant.monthly_income,
            'monthly_rent': applicant.monthly_rent,
            'employment_verified': applicant.employment_verified,
            'income_verified': applicant.income_verified,
            'rental_history_years': applicant.rental_history_years,
            'previous_evictions': applicant.previous_evictions,
            'bedrooms': applicant.bedrooms,
            'bathrooms': applicant.bathrooms,
            'square_feet': applicant.square_feet,
            'property_age_years': applicant.property_age_years,
            'lease_term_months': applicant.lease_term_months,
            'market_median_rent': applicant.market_median_rent,
            'local_unemployment_rate': applicant.local_unemployment_rate,
            'inflation_rate': applicant.inflation_rate,
            'furnished': applicant.furnished,
            'pets_allowed': applicant.pets_allowed,
            'parking_spaces': applicant.parking_spaces,
            'employment_type': applicant.employment_type,
            'property_type': applicant.property_type,
            'city': applicant.city,
        }
        
        # Calculate rent-to-income ratio
        rent_to_income = data['monthly_rent'] / max(data['monthly_income'], 0.01)
        
        # Get decision
        decision, stage, risk_prob, explanation = two_stage_decision(data, model, features)
        
        logger.info(f"Scored applicant: {decision} (Stage {stage}, Risk: {risk_prob:.2%})")
        
        return ScoringResponse(
            decision=decision,
            stage=stage,
            risk_probability=risk_prob,
            rent_to_income_ratio=rent_to_income,
            explanation=explanation,
            metrics={
                "precision": 0.2661,
                "recall": 0.6461,
                "f1_score": 0.3770,
                "auc": 0.7203
            }
        )
    
    except Exception as e:
        logger.error(f"Scoring error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "features_loaded": features is not None,
        "feature_count": len(features) if features is not None else 0,
        "metrics": {
            "precision": 0.2661,
            "recall": 0.6461,
            "f1_score": 0.3770,
            "auc": 0.7203
        }
    }
