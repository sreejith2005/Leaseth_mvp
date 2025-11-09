"""
Utility functions and validators
"""

import uuid
import hashlib
from typing import Dict, Any
from datetime import datetime
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)

# ============================================================
# Request ID & Correlation
# ============================================================

def generate_request_id() -> str:
    """Generate unique request ID for tracking"""
    return f"REQ_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"


def generate_model_hash(model_path: str) -> str:
    """Generate SHA256 hash of model file for reproducibility"""
    try:
        with open(model_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"Error hashing model: {e}")
        return "unknown"


# ============================================================
# Validation
# ============================================================

class ValidatorError(Exception):
    """Custom validation error"""
    pass


def validate_credit_score(score: int) -> bool:
    """Validate credit score range"""
    return 300 <= score <= 850


def validate_income(income: float) -> bool:
    """Validate income is positive"""
    return income > 0


def validate_rent(rent: float) -> bool:
    """Validate rent is positive"""
    return rent > 0


def validate_rti(rent: float, income: float) -> bool:
    """Validate rent-to-income ratio is reasonable"""
    if income <= 0:
        return False
    rti = rent / income
    return 0 <= rti <= 2.0  # Reasonable range


def validate_applicant_data(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate applicant data and return errors
    Returns: Dict of field -> error message (empty if valid)
    """
    errors = {}
    
    # Required fields
    required_fields = [
        'monthly_income', 'monthly_rent', 'credit_score',
        'rental_history_years', 'previous_evictions',
        'employment_verified', 'income_verified'
    ]
    
    for field in required_fields:
        if field not in data or data[field] is None:
            errors[field] = f"{field} is required"
    
    # Numeric validations
    try:
        if 'credit_score' in data and not validate_credit_score(data['credit_score']):
            errors['credit_score'] = "Credit score must be 300-850"
        
        if 'monthly_income' in data and not validate_income(data['monthly_income']):
            errors['monthly_income'] = "Monthly income must be positive"
        
        if 'monthly_rent' in data and not validate_rent(data['monthly_rent']):
            errors['monthly_rent'] = "Monthly rent must be positive"
        
        if 'monthly_income' in data and 'monthly_rent' in data:
            if not validate_rti(data['monthly_rent'], data['monthly_income']):
                errors['rent_to_income_ratio'] = "Rent-to-income ratio invalid (0-2.0)"
        
        if 'rental_history_years' in data and data['rental_history_years'] < 0:
            errors['rental_history_years'] = "Rental history must be non-negative"
        
        if 'previous_evictions' in data and data['previous_evictions'] < 0:
            errors['previous_evictions'] = "Previous evictions must be non-negative"
    
    except (TypeError, ValueError) as e:
        errors['_general'] = f"Invalid data types: {str(e)}"
    
    return errors


# ============================================================
# Logging & Timing
# ============================================================

class CorrelationIDMiddleware:
    """Middleware to add correlation ID to all logs"""
    
    def __init__(self, request_id: str):
        self.request_id = request_id
    
    def __call__(self, record):
        record.request_id = self.request_id
        return True


def log_execution_time(func):
    """Decorator to log function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        request_id = kwargs.get('request_id', 'unknown')
        
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.time() - start_time) * 1000
            logger.info(
                f"[{request_id}] {func.__name__} completed in {elapsed_ms:.2f}ms"
            )
            return result
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(
                f"[{request_id}] {func.__name__} failed after {elapsed_ms:.2f}ms: {str(e)}"
            )
            raise
    
    return wrapper


# ============================================================
# Response Formatting
# ============================================================

def success_response(data: Dict[str, Any], request_id: str = None) -> Dict[str, Any]:
    """Format success response"""
    return {
        "status": "success",
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": data
    }


def error_response(message: str, error_code: str = None, request_id: str = None) -> Dict[str, Any]:
    """Format error response"""
    return {
        "status": "error",
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "error": message,
        "error_code": error_code or "INTERNAL_ERROR"
    }


def validation_error_response(errors: Dict[str, str], request_id: str = None) -> Dict[str, Any]:
    """Format validation error response"""
    return {
        "status": "validation_error",
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "errors": errors
    }
