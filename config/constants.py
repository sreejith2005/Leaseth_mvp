"""
Application constants and enumerations
"""

# Risk Categories
RISK_CATEGORY_LOW = "LOW"
RISK_CATEGORY_MEDIUM = "MEDIUM"
RISK_CATEGORY_HIGH = "HIGH"

RISK_CATEGORIES = [RISK_CATEGORY_LOW, RISK_CATEGORY_MEDIUM, RISK_CATEGORY_HIGH]

# Risk Score Thresholds
RISK_SCORE_LOW_THRESHOLD = 30
RISK_SCORE_MEDIUM_THRESHOLD = 60

# Three-Tier Decision Thresholds (OPTIMAL - Based on Cost Analysis)
# Threshold 0.60 is the true economic optimum: 20% FPR, $53M total cost
# This is 34% cheaper and 43% fewer false positives than 0.50 threshold
AUTO_APPROVE_THRESHOLD = 0.45  # Below: auto-approve (~2-3% default rate)
MANUAL_REVIEW_THRESHOLD = 0.60  # Optimal economic threshold
AUTO_REJECT_THRESHOLD = 0.75    # Above: auto-reject (~40%+ default rate)

# Cost Multipliers (for dynamic threshold adjustment)
FP_COST_MULTIPLIER = 1.0  # Cost of rejecting good tenant (baseline)
FN_COST_MULTIPLIER = 0.6  # Cost of accepting bad tenant (60% of FP cost)

# Recommendations
RECOMMENDATION_APPROVE = "APPROVE"
RECOMMENDATION_AUTO_APPROVE = "AUTO_APPROVE"  # High confidence approval
RECOMMENDATION_REQUEST_INFO = "REQUEST_INFO"
RECOMMENDATION_MANUAL_REVIEW = "MANUAL_REVIEW"  # Requires human review
RECOMMENDATION_REJECT = "REJECT"

RECOMMENDATIONS = [
    RECOMMENDATION_APPROVE, 
    RECOMMENDATION_AUTO_APPROVE,
    RECOMMENDATION_REQUEST_INFO, 
    RECOMMENDATION_MANUAL_REVIEW,
    RECOMMENDATION_REJECT
]

# User Roles
ROLE_LANDLORD = "landlord"
ROLE_MANAGER = "manager"
ROLE_ADMIN = "admin"

ROLES = [ROLE_LANDLORD, ROLE_MANAGER, ROLE_ADMIN]

# Employment Status
EMPLOYMENT_EMPLOYED = "employed"
EMPLOYMENT_SELF_EMPLOYED = "self-employed"
EMPLOYMENT_UNEMPLOYED = "unemployed"

EMPLOYMENT_STATUSES = [EMPLOYMENT_EMPLOYED, EMPLOYMENT_SELF_EMPLOYED, EMPLOYMENT_UNEMPLOYED]

# Property Types
PROPERTY_APARTMENT = "apartment"
PROPERTY_HOUSE = "house"
PROPERTY_CONDO = "condo"
PROPERTY_TOWNHOUSE = "townhouse"

PROPERTY_TYPES = [PROPERTY_APARTMENT, PROPERTY_HOUSE, PROPERTY_CONDO, PROPERTY_TOWNHOUSE]

# Audit Actions
AUDIT_ACTION_LOGIN = "LOGIN"
AUDIT_ACTION_LOGOUT = "LOGOUT"
AUDIT_ACTION_SCORE = "SCORE"
AUDIT_ACTION_IMPORT = "IMPORT"
AUDIT_ACTION_DELETE = "DELETE"
AUDIT_ACTION_UPDATE = "UPDATE"

AUDIT_ACTIONS = [
    AUDIT_ACTION_LOGIN, AUDIT_ACTION_LOGOUT, AUDIT_ACTION_SCORE,
    AUDIT_ACTION_IMPORT, AUDIT_ACTION_DELETE, AUDIT_ACTION_UPDATE
]

# Feature Engineering Constants
INCOME_STABILITY_THRESHOLD = 3.0  # Income should be >= 3x rent
RENT_BURDEN_THRESHOLD = 0.4  # Rent burden threshold (40%)
SUBPRIME_CREDIT_THRESHOLD = 670  # Credit score threshold for subprime

# Model Versions
MODEL_VERSION_V1 = "V1_2025_11"
MODEL_VERSION_V3 = "V3_2025_11"

# Default Values for Missing Data
DEFAULT_VALUES = {
    "bedrooms": 1,
    "bathrooms": 1,
    "square_feet": 500,
    "property_age_years": 10,
    "parking_spaces": 0,
    "pets_allowed": 0,
    "furnished": 0,
    "monthly_rent": 0,
    "security_deposit": 0,
    "lease_term_months": 12,
    "tenant_age": 30,
    "monthly_income": 0,
    "employment_verified": 0,
    "income_verified": 0,
    "credit_score": 0,
    "rental_history_years": 0,
    "previous_evictions": 0,
    "market_median_rent": 0,
    "days_to_rent_property": 30,
    "local_unemployment_rate": 5.0,
    "inflation_rate": 5.0,
}
