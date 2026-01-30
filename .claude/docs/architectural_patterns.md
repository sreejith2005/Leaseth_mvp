# Architectural Patterns

This document captures recurring design patterns and conventions used throughout the Leaseth codebase.

## 1. Global State for Model Loading

**Pattern**: Load ML models into global variables at application startup, never reload during requests.

**Implementation**:
- Global variables declared at module level → [app.py:37-38](app.py#L37-L38)
- Loaded via FastAPI startup event → [app.py:71-89](app.py#L71-L89)
- Models accessed directly in request handlers → [app.py:154-156](app.py#L154-L156)

**Rationale**: 
- Pickle deserialization is expensive (~50-100ms)
- Models are immutable after training
- Thread-safe reads in ASGI workers

**Critical**: Changing model files requires application restart to reload globals.

---

## 2. Dependency Injection for Database Sessions

**Pattern**: Use FastAPI's dependency injection system to manage database session lifecycle.

**Implementation**:
- Generator function with `yield` → [src/database.py:26-32](src/database.py#L26-L32)
- Injected via `Depends()` in endpoints
- Automatic cleanup on request completion (even if exception occurs)

**Example**:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in endpoint
@app.post("/api/v1/score")
async def score_applicant(data: Input, db: Session = Depends(get_db)):
    # db session automatically managed
```

**Rationale**:
- Prevents connection leaks
- Centralizes session management
- Enables easy testing with mock sessions → [tests/conftest.py:28-32](tests/conftest.py#L28-L32)

---

## 3. Dual-Token JWT Authentication

**Pattern**: Separate short-lived access tokens from long-lived refresh tokens.

**Implementation**:
- Access token: 15 minutes, used for API requests → [src/auth.py:34-44](src/auth.py#L34-L44)
- Refresh token: 7 days, used to obtain new access tokens → [src/auth.py:47-58](src/auth.py#L47-L58)
- Token type stored in JWT payload (`"type": "access"` or `"refresh"`)

**Security Benefits**:
- Limits exposure window if access token compromised
- Refresh tokens can be invalidated server-side (future: store in DB)
- Follows OAuth2 best practices

**Token Payload Structure**:
```python
{
    "sub": user_id,        # Subject (user identifier)
    "username": "...",
    "type": "access",      # or "refresh"
    "exp": timestamp,      # Expiration
    "iat": timestamp       # Issued at
}
```

---

## 4. Pydantic Schema Validation

**Pattern**: Use Pydantic models for request/response validation and serialization.

**Implementation**:
- Input schemas with field constraints → [app.py:98-127](app.py#L98-L127)
- Output schemas for consistent responses → [app.py:130-139](app.py#L130-L139)
- Automatic OpenAPI docs generation

**Example Constraints**:
```python
class ApplicantInput(BaseModel):
    age: int = Field(..., ge=18, le=120)          # Range validation
    credit_score: int = Field(..., ge=300, le=850) # Credit score bounds
    monthly_income: float = Field(..., gt=0)       # Must be positive
    employment_status: str = Field(default="employed")
```

**Benefits**:
- Runtime type checking
- Auto-generated API docs at `/docs`
- Clear error messages for invalid inputs
- Prevents SQL injection via type coercion

---

## 5. Multi-Stage Decision Pipeline

**Pattern**: Break complex decisions into sequential stages with early exits.

**Implementation**:
- Stage 1: Rule-based eviction check → [app.py:163-177](app.py#L163-L177)
- Stage 2: ML model prediction → [app.py:179-208](app.py#L179-L208)
- Early return on Stage 1 rejection (avoid expensive ML call)

**Stage Flow**:
```
Input → Eviction Check → [REJECT if 3+ evictions + bad credit]
                      ↓
                   XGBoost Prediction
                      ↓
                   Calibration
                      ↓
                   Eviction Penalty
                      ↓
                   First-Time Adjustment
                      ↓
                   Final Decision
```

**Rationale**:
- Reduces latency for clear reject cases
- Combines rule-based and ML approaches
- Allows domain expertise to override model

---

## 6. Feature Engineering with Category Mappings

**Pattern**: Convert categorical variables to numeric codes using predefined dictionaries.

**Implementation**:
- Static mapping dictionaries at module level → [app.py:41-66](app.py#L41-L66)
- Applied during feature engineering → [app.py:289-291](app.py#L289-L291)
- Must match training data encodings exactly

**Critical**: Mappings are hardcoded and must align with model training:
- `employment_type`: full-time=1, part-time=2, self-employed=3, etc.
- `property_type`: apartment=0, condo=1, studio=2, etc.
- `city`: bangalore=0, delhi=1, mumbai=3, etc.

**Fragility**: Adding new categories requires model retraining.

---

## 7. Centralized Logging with Request Tracing

**Pattern**: Use Python's logging module with request-level correlation IDs.

**Implementation**:
- Module-level logger → `logger = logging.getLogger(__name__)`
- Structured log messages with context → [app.py:76](app.py#L76), [app.py:215-220](app.py#L215-L220)
- Request ID generation planned (not yet in app.py, but in full architecture)

**Example**:
```python
logger.info("Loading honest model...")
logger.info(f"Scored {applicant_id}: Base={prob:.2%}, Final={final:.2%}")
logger.error(f"Scoring failed: {e}", exc_info=True)
```

**Benefits**:
- Centralized error tracking
- Production debugging via log aggregation
- Audit trail for compliance

---

## 8. Pickle-Based Model Persistence

**Pattern**: Serialize trained models and metadata using Python pickle.

**Implementation**:
- Model saved after training → [honest_model.py:196-211](honest_model.py#L196-L211)
- Features list pickled separately → [honest_model.py:206](honest_model.py#L206)
- Loaded at startup → [app.py:77-84](app.py#L77-L84)

**Critical Files**:
- `models/honest_model.pkl`: XGBoost Booster object
- `models/honest_features.pkl`: List of 21 feature names in exact order
- `models/honest_metadata.json`: Performance metrics (AUC, precision, recall)

**Versioning Strategy**: No model versioning - single "live" model. Future: use MLflow or DVC.

---

## 9. Test Fixtures for Isolation

**Pattern**: Use pytest fixtures to provide clean test dependencies.

**Implementation**:
- Session-scoped engine → [tests/conftest.py:14-19](tests/conftest.py#L14-L19)
- Function-scoped database session → [tests/conftest.py:28-32](tests/conftest.py#L28-L32)
- Test client fixture → [tests/conftest.py:35-38](tests/conftest.py#L35-L38)

**Benefits**:
- Tests don't pollute production database
- Parallel test execution with isolated DBs
- Fast teardown (SQLite in-memory)

**Example**:
```python
@pytest.fixture
def test_db(test_session_factory):
    connection = test_session_factory()
    yield connection
    connection.close()  # Auto-cleanup
```

---

## 10. CORS Middleware for Cross-Origin Access

**Pattern**: Enable CORS to allow frontend (Lovable dashboard) to call API.

**Implementation**:
- Middleware added at app startup → [app.py:27-34](app.py#L27-L34)
- Configured for all origins (MVP only - tighten in production)

**Security Note**: 
- Current: `allow_origins=["*"]` - accepts all domains
- Production: Specify exact Lovable domain or use environment variable

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["https://lovable.app"] in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 11. Calibration Pattern for Model Adjustment

**Pattern**: Post-process raw model probabilities to align with business risk tolerance.

**Implementation**:
- Base XGBoost probability → [app.py:190](app.py#L190)
- Platt scaling calibration → [app.py:199](app.py#L199), [app.py:241-263](app.py#L241-L263)
- Domain-specific penalties (evictions, first-time renters) → [app.py:202-206](app.py#L202-L206)

**Calibration Formula** (Platt Scaling):
```python
# Compress high probabilities (be more lenient)
calibrated = raw_prob ** 1.5

# Additional adjustments:
# - Strong profiles: -5% to -15% reduction
# - Weak verifications: +10% to +20% increase
```

**Critical**: Coefficients are **placeholders** - production needs validation data to fit proper Platt scaling.

---

## 12. Feature Order Invariance Requirement

**Pattern**: Models expect features in exact order matching training - no tolerance for reordering.

**Implementation**:
- Feature list loaded from pickle → [app.py:82-84](app.py#L82-L84)
- Features extracted in order → [app.py:189-193](app.py#L189-L193)
- Order mismatches cause silent prediction errors (wrong values in wrong positions)

**Critical**:
```python
# FEATURES from pickle: ['credit_score', 'monthly_income', ...]
X = np.array([[features[f] for f in FEATURES]])  # Must iterate in pickle order
```

**Why This Matters**:
- XGBoost doesn't store feature names internally
- Relies on positional indexing (feature 0, feature 1, etc.)
- Reordering causes semantic mismatch without errors

**Mitigation**: Always generate features using same `engineer_features()` function → [app.py:267-330](app.py#L267-L330)

---

## 13. Exception Handling with HTTP Status Codes

**Pattern**: Convert Python exceptions to appropriate HTTP responses.

**Implementation**:
- Pydantic validation errors → 422 Unprocessable Entity (automatic)
- Business logic failures → `HTTPException` with custom codes → [app.py:155-156](app.py#L155-L156)
- Unexpected errors → 500 Internal Server Error → [app.py:224-226](app.py#L224-L226)

**Example**:
```python
try:
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    # ... scoring logic
except HTTPException:
    raise  # Re-raise HTTP exceptions as-is
except Exception as e:
    logger.error(f"Scoring failed: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail=str(e))
```

**HTTP Status Codes Used**:
- 200: Success
- 422: Validation error (invalid input)
- 500: Internal error (model failure, database error)
- 503: Service unavailable (model not loaded)

---

## 14. Synthetic Data Generation for Training

**Pattern**: Generate realistic synthetic datasets when real data unavailable.

**Implementation**:
- Controlled distributions → [generate_clean_data.py](generate_clean_data.py)
- Realistic correlations (e.g., credit score ↔ income)
- 15% default rate matching real-world baselines

**Key Distributions**:
- Credit scores: Normal(680, 80) truncated to 300-850
- Income: Lognormal with rent correlation
- Evictions: Rare event (5% have 1+, <1% have 3+)

**Trade-offs**:
- Pros: No privacy concerns, infinite samples, controlled biases
- Cons: May not capture real-world edge cases, distribution shift risk

---

## Conventions Summary

1. **File references over code snippets**: Link to `[file.py:line](file.py#Lline)` instead of copying code
2. **Global state for immutable resources**: Models, feature lists, configuration
3. **Dependency injection for lifecycle management**: Database sessions, authentication
4. **Pydantic for API contracts**: Request/response validation, OpenAPI generation
5. **Multi-stage pipelines**: Break complex logic into sequential stages
6. **Centralized logging**: Module-level loggers with structured messages
7. **Pickle for model persistence**: Simple serialization for prototypes
8. **Pytest fixtures for test isolation**: Session/function scoping as needed
9. **CORS for cross-origin APIs**: Enable frontend integration
10. **Feature order invariance**: Maintain exact order from training
