# Leaseth Architecture Documentation

## System Overview

Leaseth is a FastAPI-based microservice that scores tenant risk using hybrid XGBoost models.

## Component Diagram

\`\`\`
Client (Browser/API)
        ↓
API Gateway (FastAPI)
        ↓
    ├─ Auth Service
    ├─ Feature Engineering
    ├─ Model Routing (V1/V3)
    ├─ Calibration
    └─ Database Service
        ↓
    ├─ SQLite/PostgreSQL
    ├─ Audit Logs
    └─ Model Cache
\`\`\`

## Data Flow

1. **Request Reception** - Client sends applicant data
2. **Validation** - Pydantic validates input schema
3. **Feature Engineering** - Transform raw data to model features
4. **Model Selection** - Route to V1 or V3 based on eviction history
5. **Prediction** - XGBoost generates probability
6. **Calibration** - Apply Platt scaling to probability
7. **Response** - Return risk score and metadata
8. **Persistence** - Store prediction in database for audit

## Model Architecture

### V1 Model (With Evictions)
- **Training Data**: 50,000 applications
- **Features**: 41 (including previous_evictions)
- **Algorithm**: XGBoost
- **Accuracy**: 85%

### V3 Model (Financial Only)
- **Training Data**: 50,000 applications (no evictions)
- **Features**: 36 (no eviction-related features)
- **Algorithm**: XGBoost
- **Accuracy**: 83%

## Database Schema

See `src/database.py` for complete schema.

Key tables:
- **users**: User accounts and authentication
- **applications**: Submitted applications
- **scores**: Predictions and results
- **audit_logs**: Compliance and tracking
- **feedback**: Actual outcomes for model improvement

## Security

- **JWT Authentication**: 15-min access tokens
- **Password Hashing**: bcrypt with 12 rounds
- **Data Encryption**: AES-256 at rest (planned)
- **Request Tracing**: Unique request IDs
- **Audit Logging**: All scoring actions logged

## Scaling Strategy

### Phase 1-2 (MVP)
- Single instance
- SQLite database
- No caching

### Phase 3-4 (Growth)
- Load balanced (2-4 instances)
- PostgreSQL database
- Redis caching

### Phase 5+ (Production)
- Serverless (Lambda)
- Multi-region
- Advanced caching

See deployment guide for infrastructure details.
