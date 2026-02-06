"""
FastAPI Application for Leaseth Rental Income Advance Platform

Main API module with endpoints for scoring, authentication, and health checks.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from src.scoring import predict_and_score, load_models
from src.database import get_db, init_db, User, Application, Score
from src.auth import get_current_user, create_access_token, hash_password, verify_password

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Leaseth API",
    description="AI-powered rental income advance platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Pydantic Models
# ============================================================

class ApplicantRequest(BaseModel):
    """Request model for tenant/property scoring"""
    applicant_id: str
    name: str
    age: int = Field(ge=18, le=120)
    monthly_income: float = Field(gt=0)
    credit_score: int = Field(ge=300, le=850)
    monthly_rent: float = Field(gt=0)
    security_deposit: Optional[float] = 0
    employment_status: str
    employment_verified: bool = False
    income_verified: bool = False
    rental_history_years: float = 0
    previous_evictions: int = 0
    on_time_payments_percent: float = Field(ge=0, le=100)
    late_payments_count: int = 0
    lease_term_months: int = Field(ge=1)
    months_to_sell: int = Field(ge=1, le=60, default=12)
    bedrooms: int = Field(ge=1, le=10)
    property_type: str
    location: str
    property_address: Optional[str] = None
    currency: Optional[str] = "USD"
    
    @field_validator('employment_status')
    @classmethod
    def validate_employment(cls, v):
        if v not in ['employed', 'self-employed', 'unemployed']:
            raise ValueError('Invalid employment status')
        return v


class RegisterRequest(BaseModel):
    """User registration request"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    """User login request"""
    username: str
    password: str


class ScoringResponse(BaseModel):
    """Scoring response model"""
    applicant_id: str
    risk_score: int
    risk_category: str
    recommendation: str
    confidence: float
    reasoning: str
    reliability_score: int
    offer_status: str
    offer_amount: float
    gross_rental_value: float
    discount_rate: float
    discount_amount: float
    months_purchased: int
    processing_time_ms: Optional[float] = None


# ============================================================
# API Endpoints
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Leaseth API...")
    init_db()
    try:
        load_models()
        logger.info("Models loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load models: {e}")
    logger.info("API ready")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Leaseth API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/auth/register")
async def register(request: RegisterRequest, db = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create user
    user = User(
        username=request.username,
        email=request.email,
        password_hash=hash_password(request.password),
        full_name=request.full_name,
        role="landlord"
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate token
    access_token = create_access_token(int(user.id), str(user.username))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }


@app.post("/api/auth/login")
async def login(request: LoginRequest, db = Depends(get_db)):
    """User login"""
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not verify_password(request.password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    access_token = create_access_token(int(user.id), str(user.username))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }


@app.post("/api/score", response_model=ScoringResponse)
async def score_applicant(request: ApplicantRequest, db = Depends(get_db)):
    """
    Score a rental income stream and generate cash offer.
    
    Returns risk assessment and offer details.
    """
    request_id = f"REQ_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    logger.info(f"[{request_id}] Scoring request for {request.name}")
    
    start_time = datetime.utcnow()
    
    try:
        # Convert request to dict
        data = request.model_dump()
        
        # Run prediction
        result = predict_and_score(data, request_id=request_id)
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result['processing_time_ms'] = processing_time
        result['applicant_id'] = request.applicant_id
        
        # Save to database (optional, can be disabled)
        try:
            app_record = Application(
                user_id=1,  # Default user for MVP
                applicant_id=request.applicant_id,
                applicant_name=request.name,
                monthly_income=request.monthly_income,
                monthly_rent=request.monthly_rent,
                credit_score=request.credit_score,
                rental_history_years=request.rental_history_years,
                previous_evictions=request.previous_evictions,
                employment_verified=request.employment_verified,
                income_verified=request.income_verified,
                property_address=request.property_address,
                months_to_sell=request.months_to_sell,
                raw_data=data
            )
            db.add(app_record)
            db.commit()
            db.refresh(app_record)
            
            score_record = Score(
                application_id=app_record.id,
                request_id=request_id,
                user_id=1,
                default_probability=result.get('default_probability', 0),
                risk_score=result['risk_score'],
                risk_category=result['risk_category'],
                recommendation=result['recommendation'],
                confidence_score=result['confidence'],
                reliability_score=result['reliability_score'],
                offer_status=result['offer_status'],
                offer_amount=result['offer_amount'],
                gross_rental_value=result['gross_rental_value'],
                discount_rate=result['discount_rate'],
                months_purchased=result['months_purchased'],
                model_version="V3_2025",
                model_hash="placeholder"
            )
            db.add(score_record)
            db.commit()
            
        except Exception as db_error:
            logger.warning(f"[{request_id}] DB save failed: {db_error}")
        
        logger.info(f"[{request_id}] Scoring complete in {processing_time:.0f}ms")
        
        return result
        
    except Exception as e:
        logger.error(f"[{request_id}] Scoring error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scoring failed: {str(e)}"
        )


@app.get("/api/applicants")
async def get_applicants(
    skip: int = 0,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get list of scored applicants"""
    applications = db.query(Application).offset(skip).limit(limit).all()
    
    results = []
    for app in applications:
        score = db.query(Score).filter(Score.application_id == app.id).first()
        if score:
            results.append({
                "id": app.applicant_id,
                "input": app.raw_data or {},
                "result": {
                    "risk_score": score.risk_score,
                    "risk_category": score.risk_category,
                    "recommendation": score.recommendation,
                    "reliability_score": score.reliability_score,
                    "offer_status": score.offer_status,
                    "offer_amount": score.offer_amount,
                    "gross_rental_value": score.gross_rental_value,
                    "discount_rate": score.discount_rate,
                    "months_purchased": score.months_purchased,
                },
                "scored_at": score.created_at.isoformat()
            })
    
    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
