# Leaseth AI Tenant Risk Scoring System

## Architecture Overview

This is a **FastAPI-based ML scoring API** for tenant risk assessment using a **hybrid dual-model system**. The core innovation is **dynamic model routing** based on applicant eviction history:
- **V1 Model** (`xgboost_model.pkl`): Routes applicants with `previous_evictions > 0`
- **V3 Model** (`xgboost_model_financial.pkl`): Routes applicants with `previous_evictions == 0`

### Request Flow
1. `src/api.py` → receives applicant data via POST `/api/v1/score`
2. `src/features.py` → feature engineering with composite indicators (rent_to_income_ratio, income_stability, etc.)
3. `src/scoring.py` → hybrid model routing → prediction → calibration
4. `src/database.py` → persist Application, Score, AuditLog to SQLAlchemy DB

**Critical**: Models are loaded into global variables (`V1_MODEL`, `V3_MODEL`) at startup in `scoring.py:load_models()`. Never reload during requests.

### Tech Stack
- **Backend**: FastAPI + Uvicorn (ASGI)
- **ML**: XGBoost 2.0 with Borderline-SMOTE, Platt scaling calibration
- **Database**: SQLite (dev) → PostgreSQL (production)
- **Auth**: JWT (bcrypt + PyJWT)
- **Testing**: pytest + pytest-asyncio + httpx
- **Frontend**: Vanilla HTML/CSS/JS (MVP) → React (future)

## Development Workflow

### Starting the API
```powershell
# Configure environment
cp .env.example .env  # Edit JWT_SECRET, DATABASE_URL

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

### Model Training Workflow
**Two separate training scripts generate model artifacts:**

1. **V1 Model (With Evictions)** - `main_v1_improved.py`:
   ```powershell
   python main_v1_improved.py
   ```
   - Trains on applicants **with eviction history** (`previous_evictions > 0`)
   - Uses **BorderlineSMOTE** for class balancing (25% sampling strategy)
   - Applies **extreme sample weighting**: 1-eviction = 0.20x, 2+ evictions = 0.08x
   - Implements **monotonic constraints** (41 features total)
   - Generates: `models/xgboost_model.pkl`, `models/feature_list.pkl`
   - Hyperparameters: n_estimators=300, max_depth=5, learning_rate=0.03, reg_lambda=2.0

2. **V3 Model (Financial Only)** - `main_v3_final.py`:
   ```powershell
   python main_v3_final.py
   ```
   - Trains on **financial features only** (no `previous_evictions`)
   - Uses BorderlineSMOTE without custom weighting
   - 36 features (excludes eviction-related columns)
   - Generates: `models/xgboost_model_financial.pkl`, `models/feature_list_financial.pkl`
   - Hyperparameters: n_estimators=300, max_depth=4, learning_rate=0.03, reg_lambda=2.5

**Training Data**: Both scripts expect `C:\Users\LENOVO\leaseth_mvp\data\leaseth_tenant_risk_dataset_v2_50k.csv` with 50,000+ records.

**Critical**: After training, restart API to reload models via `load_models()` in `scoring.py`.

### Testing
- **Test framework**: pytest with async support (`pytest-asyncio`, `httpx.AsyncClient`)
- **Test files**: `tests/test_api.py`, `tests/test_features.py`, `tests/test_scoring.py`
- **Fixtures**: `tests/conftest.py` provides `test_db`, `test_client`, `test_engine`
- **Run tests**: `pytest tests/ -v`
- **Coverage**: `pytest --cov=src tests/`
- **Manual testing**: FastAPI Swagger UI at `/docs` endpoint

### Database
- **SQLite by default** (`leaseth.db` auto-created)
- Init happens in `src/api.py:startup_event()` via `init_db()`
- Models: `User`, `Application`, `Score`, `AuditLog`, `Feedback` (see `src/database.py`)
- **No migrations** - schema changes require manual DB deletion/recreation

### PostgreSQL Migration (Production)
**Planned for production deployment. SQLite is sufficient for MVP.**

Migration steps:
1. Update `.env`: `DATABASE_URL=postgresql://user:pass@localhost:5432/leaseth`
2. Install PostgreSQL driver (already in requirements: `psycopg2-binary==2.9.9`)
3. Engine auto-detects PostgreSQL via `config/database.py`:
   ```python
   if "sqlite" in settings.DATABASE_URL:
       engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
   else:
       engine = create_engine(DATABASE_URL, pool_pre_ping=True)  # PostgreSQL
   ```
4. Run `init_db()` to create schema
5. Optional: Use Alembic for migrations (not yet implemented)

**PostgreSQL benefits**:
- Connection pooling for concurrent requests
- Better performance for joins/aggregations
- JSONB support for `raw_data` field
- Full-text search capabilities

**Warning**: No migration scripts exist. Schema changes require manual SQL or recreation.

## Critical Patterns

### Feature Engineering Dependency Chain
`src/features.py:create_new_features()` has **hardcoded composite indicators**:
```python
# These are computed columns, not input fields:
df['rent_to_income_ratio'] = df['monthly_rent'] / df['monthly_income']
df['income_stability'] = ((df['employment_verified'] == 1) & 
                          (df['monthly_income'] >= df['monthly_rent'] * 3)).astype(int)
df['verification_score'] = df['employment_verified'].astype(int) + df['income_verified'].astype(int)
df['high_rent_burden'] = (df['rent_to_income_ratio'] > 0.4).astype(int)
df['subprime_credit'] = (df['credit_score'] < 670).astype(int)
df['tenant_stability_score'] = ((df['rental_history_years'] / 10).clip(0, 1) * 0.6 + 
                                  (df['lease_term_months'] / 24).clip(0, 1) * 0.4)
```
**When modifying**: 
- Ensure model pickle files (`feature_list.pkl`, `feature_list_financial.pkl`) contain matching feature names
- Features must be extracted in **exact order** matching training
- Constants defined in `config/constants.py` (e.g., `INCOME_STABILITY_THRESHOLD=3.0`, `RENT_BURDEN_THRESHOLD=0.4`, `SUBPRIME_CREDIT_THRESHOLD=670`)
- Missing data defaults in `config/constants.py:DEFAULT_VALUES`
- **Missing field defense**: Every engineered feature should be robust to missing columns via `.fillna()` defaults
- **Changing features**: Retrain both models and update pickled feature lists and hashes in `/models/` if you add or change any computed columns

### Authentication Pattern
- **Dual-token system**: 15-min access tokens + 7-day refresh tokens
- JWT payload includes `user_id`, `username`, `type` (access/refresh)
- Dependency injection: `get_current_user()` extracts user from `Authorization: Bearer <token>`
- **Critical**: `src/auth.py:verify_password()` uses bcrypt with 12 rounds (see `.env.example`)
- User roles: `landlord`, `manager`, `admin` (defined in `config/constants.py:ROLES`)
- **Password reset flow and multi-role permissions** are not yet implemented

### Request Tracing
Every request gets a unique `request_id` via middleware:
```python
request_id = f"REQ_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4()[:8]}"
```
Use `logger.info(f"[{request_id}] ...")` for correlation across logs, DB audit trail, and response headers (`X-Request-ID`).

### Calibration Logic
Raw XGBoost probabilities undergo **Platt scaling** in `scoring.py:_calibrate_probability()`:
```python
calibrated = 1.0 / (1.0 + np.exp(-(a * prob + b)))
```
Coefficients `a`, `b` differ per model (V1: 1.2/-0.3, V3: 1.1/-0.2). These are **placeholder values** - production should compute from validation set.

### Rate Limiting Strategy (Planned)
**SlowAPI integration for rate limiting** (not yet implemented):
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/score")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def score_applicant(...):
    ...
```

**Planned rate limits**:
- Anonymous: 10 req/min per IP
- Authenticated landlord: 100 req/min per user
- Authenticated manager: 500 req/min per user
- Admin: unlimited

**Implementation location**: Add to `src/api.py` after MVP testing phase. SlowAPI already in `requirements.txt`.

## Configuration

### Settings Management
- `src/config.py` uses `pydantic-settings` to load `.env` variables
- **All paths are relative** to project root (e.g., `./models/`, `./logs/`)
- Change DB: set `DATABASE_URL` to PostgreSQL format `postgresql://user:pass@host:5432/db`
- **Security**: Change `JWT_SECRET` in production (default is "change-me-in-production")

### Model Files
Expected in `models/` directory:
- `xgboost_model.pkl` / `xgboost_model_financial.pkl` (XGBoost Booster objects)
- `feature_list.pkl` / `feature_list_financial.pkl` (Python lists of feature names)

**Without these files, API startup will fail.** Generate via `main_v1_improved.py` and `main_v3_final.py`.

## API Contracts

### Input Validation
`src/api.py:ApplicantRequest` enforces:
- `age`: 18-120
- `employment_status`: regex `^(employed|self-employed|unemployed)$`
- `credit_score`: 300-850
- `monthly_rent`: must not exceed `2 * monthly_income` (Pydantic validator)
- `on_time_payments_percent`: 0-100

### Response Format
All endpoints use standardized wrappers (`src/utils.py`):
```python
success_response(data, request_id)  # Returns {"success": true, "data": ..., "request_id": ...}
error_response(message, error_code, request_id)  # Returns {"success": false, "error": ...}
```

### Risk Scoring Output
- `risk_score`: 0-100 integer (derived from calibrated probability × 100)
- `risk_category`: LOW (<30), MEDIUM (30-60), HIGH (>60) - thresholds in `config/constants.py`
- `recommendation`: APPROVE, REQUEST_INFO, REJECT
- `confidence_score`: Model certainty (0-1, computed from distance to 0.5 probability)

## Common Operations

### Adding New Features
1. Update `src/features.py:create_new_features()` to compute new columns
2. Retrain models with new feature set using `main_v1_improved.py` and `main_v3_final.py`
3. Replace pickle files in `models/` directory
4. Restart API to reload models
5. **Critical**: Feature order in pickle must match computation order

### Adding Endpoints
Follow FastAPI patterns in `src/api.py`:
- Tag with `tags=["Category"]` for Swagger grouping
- Use `Depends(get_db)` for DB session injection
- Use `Depends(get_current_user)` for auth-protected routes
- Wrap responses with `success_response()` or `error_response()`
- Log key events with `logger.info(f"[{request_id}] ...")`

### Debugging Model Issues
Check logs for model routing:
```python
logger.info(f"[{request_id}] Using V1 model (evictions: {previous_evictions})")
logger.info(f"[{request_id}] Using V3 model (no evictions)")
```
Verify feature extraction didn't fail (logs in `scoring.py:predict_and_score()`). If model fails due to feature mismatch, expect a ValueError; check exact feature ordering in pickle versus new DataFrame columns.

## Conventions

- **Import order**: stdlib → third-party → local (`from src.x import y`)
- **Logging**: Use module-level `logger = logging.getLogger(__name__)`
- **DB sessions**: Always use `get_db()` dependency, never create SessionLocal() directly in endpoints
- **Timestamps**: All DB timestamps use `datetime.utcnow()` (not timezone-aware)
- **Error handling**: Log errors with request_id, then raise HTTPException or return JSONResponse

## Frontend Architecture

### MVP Frontend (Current)
- **Stack**: Vanilla HTML/CSS/JS (`frontend/index.html`, `frontend/styles.css`, `frontend/script.js`)
- **Purpose**: Simple demo/test interface for MVP phase
- **Features**: Form submission, real-time validation, result visualization
- **API Integration**: Direct fetch calls to `http://localhost:8000/api/v1/score`

### React Frontend (Future)
- **Location**: `frontend/react/` subdirectory (to be scaffolded)
- **Planned Tools**: Lovable/Bolt or manual setup with Vite/Next.js
- **Features**: Professional UI, dashboard, batch uploads, analytics
- **Migration**: Will coexist with vanilla frontend during transition

## Model Explainability (Planned)

### SHAP Integration
- **Library**: `shap==0.43.0` already in requirements
- **Implementation**: `src/explainability.py` (currently empty stub)
- **Planned Features**:
  - Feature importance visualization
  - Individual prediction explanations
  - Waterfall plots for stakeholder transparency
  - Integration with `/api/v1/score` endpoint (optional explainability flag)

### Usage Pattern (Future)
```python
# In src/explainability.py
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)
```

## Known Gaps

- **No model files present** - API will fail at startup without `models/*.pkl` (generate via training scripts)
- **Frontend incomplete** - `frontend/index.html` has basic structure, React scaffold not yet created
- **No monitoring** - `src/monitoring.py` empty (planned for metrics/alerting)
- **Explainability stub** - `src/explainability.py` empty (SHAP integration planned)
- **Hardcoded calibration** - Platt scaling coefficients need real validation data
- **No CSV parser** - `src/csv_parser.py` empty (planned for batch scoring)