# Leaseth Tenant Risk Scoring API

**Purpose**: FastAPI-based ML scoring service for tenant risk assessment using hybrid XGBoost models with two-stage evaluation (eviction check + financial analysis).

## Tech Stack

- **Backend**: FastAPI 0.104.1 + Uvicorn (ASGI)
- **ML**: XGBoost 2.0, scikit-learn 1.3.0, Optuna (hyperparameter tuning)
- **Database**: SQLAlchemy 2.0.23 (SQLite dev → PostgreSQL prod)
- **Auth**: JWT (PyJWT 2.9.0) + bcrypt password hashing (12 rounds)
- **Testing**: pytest 7.4.3 + pytest-asyncio + httpx
- **Deployment**: Hugging Face Spaces

## Project Structure

```
app.py                       # Main API entrypoint - two-stage scoring logic
honest_model.py              # Model training script (72% AUC XGBoost)
generate_clean_data.py       # Synthetic dataset generation

models/
  honest_model.pkl           # Trained XGBoost model (200 estimators, depth=4)
  honest_features.pkl        # Feature list (21 features in exact order)
  honest_metadata.json       # Model performance metrics
tests/                       # pytest test suite
  conftest.py                # Test fixtures (test_client, test_db)
  test_api.py                # API endpoint tests
  test_features.py           # Feature engineering tests
  test_scoring.py            # Scoring logic tests
data/
  clean_tenant_dataset.csv   # Training data (50K synthetic records)
docs/                        # Deployment guides and architecture
frontend/                    # Vanilla HTML/CSS/JS (MVP)
```

## Key Directories

- **[app.py](app.py)**: Main application with `/api/score` endpoint, model loading, feature engineering, and two-stage decision logic
- **[src/](src/)**: Core modules for auth, database, and optimization
- **[models/](models/)**: Pickle files for XGBoost model and feature list (loaded at startup into global vars)
- **[tests/](tests/)**: Unit tests with shared fixtures for database and API client
- **[docs/](docs/)**: Extensive deployment guides (Render, Fly.io, Railway, Lovable integration)
- **[data/](data/)**: Synthetic training datasets (15% default rate)

## Essential Commands

### Development
```powershell
# Install dependencies
pip install -r requirements.txt

# Run API server (auto-reload on changes)
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Access API docs
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Model Training
```powershell
# Train honest model (generates models/honest_model.pkl)
python honest_model.py

# Generate synthetic dataset (outputs to data/)
python generate_clean_data.py
```

### Testing
```powershell
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_api.py -v
```

### Docker
```powershell
# Build image
docker build -t leaseth-api .

# Run container
docker run -p 8000:8000 leaseth-api

# Docker Compose (includes database)
docker-compose up
```

## Core Architecture

### Model Loading Pattern
- Models loaded at startup via `@app.on_event("startup")` decorator → [app.py:71-89](app.py#L71-L89)
- Stored in global variables `MODEL` and `FEATURES` (never reload during requests)
- Feature order from pickle **must match** feature engineering order → [app.py:80-84](app.py#L80-L84)

### Two-Stage Scoring
1. **Stage 1**: Eviction check with credit score weighting → [app.py:163-177](app.py#L163-L177)
   - 3+ evictions + credit < 650 = immediate REJECT
2. **Stage 2**: XGBoost prediction with calibration → [app.py:179-208](app.py#L179-L208)
   - Base probability → Platt scaling → Eviction penalty → First-time renter adjustment

### Request Flow
1. Pydantic validation (`ApplicantInput` schema) → [app.py:98-127](app.py#L98-L127)
2. Feature engineering (21 features with category encoding) → [app.py:267-330](app.py#L267-L330)
3. Model prediction (XGBoost probability) → [app.py:189-191](app.py#L189-L191)
4. Calibration and adjustments → [app.py:199-207](app.py#L199-L207)
5. Decision logic (LOW/MEDIUM/HIGH thresholds) → [app.py:210-219](app.py#L210-L219)
6. Return `ScoringResponse` with risk score, category, recommendation

### Database Pattern
- SQLAlchemy with dependency injection → [src/database.py:26-32](src/database.py#L26-L32)
- Models: `User`, `Application`, `Score`, `AuditLog`, `Feedback`
- Session lifecycle managed by `get_db()` generator
- SQLite (dev) auto-detects via connection string → [src/database.py:11-17](src/database.py#L11-L17)

### Authentication Flow
- Dual-token system: 15-min access + 7-day refresh tokens → [src/auth.py:34-61](src/auth.py#L34-L61)
- Password hashing with bcrypt (12 rounds) → [src/auth.py:19-26](src/auth.py#L19-L26)
- JWT verification with expiration handling → [src/auth.py:64-75](src/auth.py#L64-L75)
- Dependency injection for current user → [src/auth.py:78-89](src/auth.py#L78-L89)

## Additional Documentation

For specialized topics, consult:
- **[.claude/docs/architectural_patterns.md](.claude/docs/architectural_patterns.md)**: Design patterns, dependency injection, state management, API patterns
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**: System diagrams, component flow, scaling strategy
- **[docs/API_Documentation.md](docs/API_Documentation.md)**: Complete API reference, request/response schemas
- **[docs/DEPLOYMENT.md](docs/DEPLOYEMNT.md)**: Production deployment steps
- **[docs/RENDER_LOVABLE_DEPLOYMENT_GUIDE.md](docs/RENDER_LOVABLE_DEPLOYMENT_GUIDE.md)**: Render + Lovable integration
- **[docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)**: Common operations, debugging, troubleshooting

## Critical Constraints

1. **Feature Order**: Models expect exact feature order from pickle - changing feature engineering requires retraining → [app.py:189-193](app.py#L189-L193)
2. **Global Model Variables**: `MODEL` and `FEATURES` are globals - never reload mid-request → [app.py:37-38](app.py#L37-L38)
3. **Category Encodings**: Employment, property type, city mappings must match training → [app.py:41-66](app.py#L41-L66)
4. **Calibration Constants**: Platt scaling coefficients are hardcoded placeholders → [app.py:241-249](app.py#L241-L249)
5. **No Migrations**: Database schema changes require manual recreation (no Alembic) → [src/database.py:11-21](src/database.py#L11-L21)

## Known Gaps

- **No rate limiting** (SlowAPI in requirements but not implemented)
- **Frontend incomplete** (vanilla HTML placeholder, React planned)
- **No batch scoring** (CSV parser stub exists)
- **No model monitoring** (metrics/alerting module empty)
- **Hardcoded calibration** (needs validation data for real coefficients)
