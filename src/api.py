"""
FastAPI application with all endpoints
"""

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
import logging
import time
import pandas as pd

from src.config import settings, setup_logging
from src.database import SessionLocal, init_db, User, Application, Score, AuditLog, get_db
from src.features import create_new_features
from src.scoring import load_models, predict_and_score
from src.auth import create_user, authenticate_user, create_access_token, create_refresh_token, get_current_user
from src.utils import (
    generate_request_id, validate_applicant_data, log_execution_time,
    success_response, error_response, validation_error_response
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-powered tenant risk scoring API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request ID middleware
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests"""
    async def dispatch(self, request: Request, call_next):
        request_id = generate_request_id()
        request.state.request_id = request_id
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        logger.info(f"[{request_id}] {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
        return response

app.add_middleware(RequestIDMiddleware)

# ============================================================
# Pydantic Models for Request/Response
# ============================================================

class ApplicantRequest(BaseModel):
    """Applicant data for scoring"""
    applicant_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    age: int = Field(..., ge=18, le=120)
    employment_status: str = Field(..., pattern="^(employed|self-employed|unemployed)$")
    employment_verified: bool = False
    income_verified: bool = False
    
    # Financial
    monthly_income: float = Field(..., gt=0)
    credit_score: int = Field(..., ge=300, le=850)
    
    # Payment history
    previous_evictions: int = Field(default=0, ge=0)
    rental_history_years: float = Field(..., ge=0)
    on_time_payments_percent: float = Field(default=100, ge=0, le=100)
    late_payments_count: int = Field(default=0, ge=0)
    
    # Property
    monthly_rent: float = Field(..., gt=0)
    security_deposit: float = Field(default=0, ge=0)
    lease_term_months: int = Field(default=12, ge=1, le=60)
    bedrooms: int = Field(default=1, ge=1)
    property_type: str = Field(default="apartment")
    location: str = Field(default="Unknown")
    market_median_rent: float = Field(default=0, ge=0)
    
    # Market context
    local_unemployment_rate: float = Field(default=5.0, ge=0)
    inflation_rate: float = Field(default=5.0, ge=0)
    
    # Optional custom thresholds for decision system
    custom_thresholds: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional custom decision thresholds. Keys: auto_approve, manual_review, auto_reject"
    )
    
    @validator('monthly_rent')
    def validate_rent(cls, v, values):
        if 'monthly_income' in values and v > values['monthly_income'] * 2:
            raise ValueError('Rent cannot be more than 2x monthly income')
        return v


class LoginRequest(BaseModel):
    """Login request"""
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=255)


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class ScoreResponse(BaseModel):
    """Score response"""
    risk_score: int
    risk_category: str
    default_probability: float
    recommendation: str
    confidence_score: float
    model_version: str
    inference_time_ms: float


# ============================================================
# Startup/Shutdown Events
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database and load models on startup"""
    logger.info("Starting up Leaseth API...")
    
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized")
        
        # Load models
        load_models()
        logger.info("Models loaded successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Leaseth API...")


# ============================================================
# Health Check Endpoint
# ============================================================

@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Check database
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        # Try to score test data
        test_data = {
            'monthly_income': 50000,
            'monthly_rent': 15000,
            'credit_score': 720,
            'rental_history_years': 5,
            'previous_evictions': 0,
            'employment_verified': True,
            'income_verified': True
        }
        
        # Create dummy features
        df = pd.DataFrame([test_data])
        df_feat = create_new_features(df)
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "models": "loaded",
            "api_version": settings.API_VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


# ============================================================
# Authentication Endpoints
# ============================================================

@app.post("/api/v1/auth/register", tags=["Authentication"])
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register new user"""
    request_id = generate_request_id()
    
    try:
        user = create_user(
            db,
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name or ""
        )
        
        logger.info(f"[{request_id}] User registered: {user.username}")
        
        return success_response({
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }, request_id=request_id)
    
    except ValueError as e:
        logger.warning(f"[{request_id}] Registration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[{request_id}] Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/api/v1/auth/login", tags=["Authentication"], response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login and get tokens"""
    request_id = generate_request_id()
    
    try:
        user = authenticate_user(db, request.username, request.password)
        
        if not user:
            logger.warning(f"[{request_id}] Failed login: {request.username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(user.id, user.username)  # type: ignore
        refresh_token = create_refresh_token(user.id, user.username)  # type: ignore
        
        # Log to audit trail
        audit = AuditLog(
            user_id=user.id,  # type: ignore
            action="LOGIN",
            resource_id=str(user.id),
            resource_type="user"
        )
        db.add(audit)
        db.commit()
        
        logger.info(f"[{request_id}] User logged in: {user.username}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


# ============================================================
# Scoring Endpoint
# ============================================================

@app.post("/api/v1/score", tags=["Scoring"])
async def score_applicant(
    applicant: ApplicantRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Score single applicant"""
    request_id = request.state.request_id
    current_user = None  # TODO: Add auth dependency when needed
    
    try:
        # Validate input
        applicant_dict = applicant.dict()
        errors = validate_applicant_data(applicant_dict)
        
        if errors:
            logger.warning(f"[{request_id}] Validation errors: {errors}")
            return JSONResponse(
                status_code=422,
                content=validation_error_response(errors, request_id=request_id)
            )
        
        # Feature engineering
        df = pd.DataFrame([applicant_dict])
        df_feat = create_new_features(df)
        
        # Get prediction with optional custom thresholds
        prediction = predict_and_score(
            df_feat.iloc[0].to_dict(), 
            request_id=request_id,
            custom_thresholds=applicant.custom_thresholds
        )
        
        # Store in database
        db_app = Application(
            user_id=current_user.id if current_user else 1,
            applicant_id=applicant.applicant_id,
            applicant_name=applicant.name,
            monthly_income=applicant.monthly_income,
            monthly_rent=applicant.monthly_rent,
            credit_score=applicant.credit_score,
            rental_history_years=applicant.rental_history_years,
            previous_evictions=applicant.previous_evictions,
            employment_verified=applicant.employment_verified,
            income_verified=applicant.income_verified,
            raw_data=applicant_dict
        )
        db.add(db_app)
        db.commit()
        db.refresh(db_app)
        
        # Store score
        db_score = Score(
            application_id=db_app.id,
            user_id=current_user.id if current_user else 1,
            request_id=request_id,
            default_probability=prediction['default_probability'],
            risk_score=prediction['risk_score'],
            risk_category=prediction['risk_category'],
            recommendation=prediction['recommendation'],
            confidence_score=prediction['confidence_score'],
            model_version=prediction['model_version'],
            model_hash=prediction['model_hash'],
            inference_time_ms=prediction['inference_time_ms']
        )
        db.add(db_score)
        db.commit()
        
        # Audit log
        audit = AuditLog(
            user_id=current_user.id if current_user else 1,
            action="SCORE",
            resource_id=str(db_score.id),
            resource_type="score",
            details={"risk_score": prediction['risk_score'], "recommendation": prediction['recommendation']}
        )
        db.add(audit)
        db.commit()
        
        logger.info(f"[{request_id}] Score stored: {prediction['risk_score']}% ({prediction['risk_category']})")
        
        return success_response({
            "score_id": db_score.id,
            "applicant_id": applicant.applicant_id,
            "risk_score": prediction['risk_score'],
            "risk_category": prediction['risk_category'],
            "default_probability": prediction['default_probability'],
            "recommendation": prediction['recommendation'],
            "confidence_score": prediction['confidence_score'],
            "model_version": prediction['model_version'],
            "inference_time_ms": prediction['inference_time_ms']
        }, request_id=request_id)
    
    except Exception as e:
        logger.error(f"[{request_id}] Scoring failed: {e}")
        return JSONResponse(
            status_code=500,
            content=error_response(str(e), error_code="SCORING_FAILED", request_id=request_id)
        )


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API info"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "/docs"
    }


# ============================================================
# Error Handlers
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.detail, request_id=request_id)
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(f"[{request_id}] Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=error_response("Internal server error", request_id=request_id)
    )


# Import pandas here to avoid circular imports
import pandas as pd
