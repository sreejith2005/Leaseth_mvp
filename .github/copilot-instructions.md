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

- **Calibrated outputs**: Raw XGBoost probabilities are transformed using Platt scaling to ensure risk scores reflect real-world default likelihoods. Calibration coefficients are currently hardcoded but must be adjusted after validation for production trustworthiness.
- **Explainability**: Design supports integration with SHAP, but `src/explainability.py` must be filled for full transparency.
- **Fairness/Compliance**: Architecture allows for future disparate impact/fairness auditing by passing protected attributes and collecting audit logs. Fairness checks are not yet implemented.

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

### Testing
- **No pytest tests exist yet** - `tests/` directory contains empty files
- Manual testing via `/docs` (FastAPI Swagger UI)
- For new tests: use `pytest-asyncio` for async endpoints, `httpx.AsyncClient` for requests

### Database
- **SQLite by default** (`leaseth.db` auto-created)
- Init happens in `src/api.py:startup_event()` via `init_db()`
- Models: `User`, `Application`, `Score`, `AuditLog`, `Feedback` (see `src/database.py`)
- **No migrations** - schema changes require manual DB deletion/recreation
- **Future:** Plan for PostgreSQL; models are compatible for upgrade.

## Critical Patterns

### Feature Engineering Dependency Chain
`src/features.py:create_new_features()` has **hardcoded composite indicators**:
```python
# These are computed columns, not input fields:
df['rent_to_income_ratio'] = df['monthly_rent'] / df['monthly_income']
df['income_stability'] = ((df['employment_verified'] == 1) & 
                          (df['monthly_income'] >= df['monthly_rent'] * 3)).astype(int)
df['verification_score'] = df['employment_verified'].astype(int) + df['income_verified'].astype(int)
```
**When modifying**: Ensure model pickle files (`feature_list.pkl`, `feature_list_financial.pkl`) contain matching feature names. Features must be extracted in **exact order** matching training.

- **Missing field defense**: Every engineered feature should be robust to missing columns via `.fillna()` defaults.
- **Changing features**: Retrain both models and update pickled feature lists and hashes in `/models/` if you add or change any computed columns.

### Authentication Pattern
- **Dual-token system**: 15-min access tokens + 7-day refresh tokens
- JWT payload includes `user_id`, `username`, `type` (access/refresh)
- Dependency injection: `get_current_user()` extracts user from `Authorization: Bearer <token>`
- **Critical**: `src/auth.py:verify_password()` uses bcrypt with 12 rounds (see `.env.example`)
- **Password reset flow and multi-user/role support** are not present.

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

- **Add an actual calibration step** as soon as validation stats are available; don't trust raw probabilities with real money or real tenants.

## Configuration

### Settings Management
- `src/config.py` uses `pydantic-settings` to load `.env` variables
- **All paths are relative** to project root (e.g., `./models/`, `./logs/`)
- Change DB: set `DATABASE_URL` to PostgreSQL format `postgresql://user:pass@host:5432/db`
- **Security**: Change `JWT_SECRET` in production (default is "change-me-in-production")
- Always use environment variables for secrets, avoid committing secrets in code or repo.

### Model Files
Expected in `models/` directory (currently empty):
- `xgboost_model.pkl` / `xgboost_model_financial.pkl` (XGBoost Booster objects)
- `feature_list.pkl` / `feature_list_financial.pkl` (Python lists of feature names)
- `model_metadata.json` (optional: document model version and hash)
- **Model version/hashes** should also be persisted in DB for auditing; see `Score` model in `database.py`.

**Without these files, API startup will fail.** Generate via separate training script.

## API Contracts

### Input Validation
`src/api.py:ApplicantRequest` enforces:
- `age`: 18-120
- `employment_status`: regex `^(employed|self-employed|unemployed)$`
- `credit_score`: 300-850
- `monthly_rent`: must not exceed `2 * monthly_income` (Pydantic validator)
- `on_time_payments_percent`: 0-100

- **Extra:** Use Pydantic/validator methods for tight value checking on all numeric and enum fields (e.g., property_type).

### Response Format
All endpoints use standardized wrappers (`src/utils.py`):
```python
success_response(data, request_id)  # Returns { "status": "success", "data": ..., "request_id": ... }
error_response(message, error_code, request_id)  # Returns {"status": "error", "error": ...}
```

### Risk Scoring Output
- `risk_score`: 0-100 integer (derived from calibrated probability × 100)
- `risk_category`: LOW (<30), MEDIUM (30-60), HIGH (>60)
- `recommendation`: APPROVE, REQUEST_INFO, REJECT
- `confidence_score`: Model certainty (0-1, computed from distance to 0.5 probability)

- **Audit**: Each prediction record should persist model version, model hash, and feature version to `Score` table.

## Common Operations

### Adding New Features
1. Update `src/features.py:create_new_features()` to compute new columns
2. Retrain models with new feature set
3. Replace pickle files in `models/` directory
4. Restart API to reload models
5. **Critical**: Feature order in pickle must match computation order

- Also update feature importance list and audit changes in `models/model_metadata.json`.

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
Verify feature extraction didn't fail (logs in `scoring.py:predict_and_score()`).
- If model fails due to feature mismatch, expect a ValueError; check exact feature ordering in pickle versus new DataFrame columns.

## Conventions

- **Import order**: stdlib → third-party → local (`from src.x import y`)
- **Logging**: Use module-level `logger = logging.getLogger(__name__)`
- **DB sessions**: Always use `get_db()` dependency, never create SessionLocal() directly in endpoints
- **Timestamps**: All DB timestamps use `datetime.utcnow()` (not timezone-aware)
- **Error handling**: Log errors with request_id, then raise HTTPException or return JSONResponse
- **Security**: All sensitive secrets go in `.env`; never hardcode any API keys or passwords.

## Known Gaps

- **No model files present** - API will fail at startup without `models/*.pkl`
- **Empty test suite** - `tests/` directory scaffolded but not implemented
- **Frontend incomplete** - `frontend/index.html` empty, React scaffold exists in `frontend/react/`
- **No monitoring** - `src/monitoring.py` and `src/explainability.py` are empty stubs
- **Hardcoded calibration** - Platt scaling coefficients need real validation data
- **No explicit fairness/impact audit** - add disparate impact/fairness testing before US launch
- **No batch/CSV scoring endpoint implemented yet;** see roadmap for phase 5