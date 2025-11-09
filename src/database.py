"""
Database configuration and session management
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from src.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
    pool_pre_ping=True  # Verify connections before using
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for getting DB session
def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# SQLAlchemy ORM Models
# ============================================================

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="landlord")  # landlord, manager, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Application(Base):
    """Applicant application model"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    applicant_id = Column(String(100), index=True, nullable=False)
    applicant_name = Column(String(255), nullable=False)
    applicant_email = Column(String(255), nullable=True)
    monthly_income = Column(Float, nullable=False)
    monthly_rent = Column(Float, nullable=False)
    credit_score = Column(Integer, nullable=False)
    rental_history_years = Column(Float, nullable=False)
    previous_evictions = Column(Integer, default=0)
    employment_verified = Column(Boolean, default=False)
    income_verified = Column(Boolean, default=False)
    raw_data = Column(JSON, nullable=True)  # Store full input JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Score(Base):
    """Risk score results model"""
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, index=True, nullable=False)
    request_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Risk assessment
    default_probability = Column(Float, nullable=False)
    risk_score = Column(Integer, nullable=False)  # 0-100
    risk_category = Column(String(50), nullable=False)  # LOW, MEDIUM, HIGH
    recommendation = Column(String(100), nullable=False)  # APPROVE, REQUEST_INFO, REJECT
    confidence_score = Column(Float, nullable=False)
    
    # Model metadata
    model_version = Column(String(50), nullable=False)  # V1_2025_11
    model_hash = Column(String(64), nullable=True)  # SHA256 of model
    feature_version = Column(String(50), nullable=True)  # features_v3
    
    # Performance
    inference_time_ms = Column(Float, nullable=False)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Audit trail for compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    action = Column(String(100), nullable=False)  # SCORE, LOGIN, IMPORT, DELETE
    resource_id = Column(String(100), nullable=True)
    resource_type = Column(String(50), nullable=True)  # application, score
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class Feedback(Base):
    """Actual vs predicted outcomes for model improvement"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    score_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Actual outcome
    actual_default = Column(Boolean, nullable=False)
    
    # Metadata
    feedback_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)


# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")
