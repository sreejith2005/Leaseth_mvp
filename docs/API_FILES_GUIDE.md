# API Files Guide - Quick Reference

**Last Updated**: December 6, 2025  
**Purpose**: Quick reference for all API files in the Leaseth MVP project

---

## 🎯 MVP CORE (Active Production)

### **1. `simple_api.py`**
**Purpose**: Production API for Lovable dashboard integration (Deployed on Render)

**Key Details**:
- **Port**: 8001 (local), dynamic on Render
- **Deployment**: https://leaseth-mvp.onrender.com
- **Model**: `honest_model.pkl`
- **CORS**: Enabled for frontend access
- **Features**: Minimal - just scoring, no auth/database

**Endpoints**:
- `GET /health` - Health check
- `POST /api/score` - Score applicant and return risk assessment

**When to Use**:
- Production scoring for Lovable dashboard
- Public-facing API on Render
- Simple, fast tenant risk scoring

**Testing**: `test_lovable_api.py`

---

### **2. `scoring_api.py`**
**Purpose**: Local testing API for quick model testing via Swagger UI

**Key Details**:
- **Port**: 8002 (local only)
- **Model**: `honest_model.pkl` + `honest_features.pkl`
- **Interface**: FastAPI Swagger UI at `/docs`
- **NO HTML**: Clean API-only interface (removed 218 lines of HTML)
- **Lines**: 233 lines
- **Two-stage logic**: Stage 1 (rule-based) → Stage 2 (ML model)

**Endpoints**:
- `GET /` - API info and available endpoints
- `POST /api/score` - Two-stage scoring with detailed explanation
- `GET /health` - Health check with model metrics

**When to Use**:
- Quick local testing without waking up Render
- Testing model performance on sample data
- Debugging two-stage decision logic
- Use **http://127.0.0.1:8002/docs** for interactive testing

**How to Start**:
```powershell
python run_scoring_api.py
# Then open: http://127.0.0.1:8002/docs
```

**Metrics**:
- Precision: 0.2661
- Recall: 0.6461
- F1 Score: 0.3770
- AUC: 0.7203

---

### **3. `run_scoring_api.py`**
**Purpose**: Production runner for `scoring_api.py`

**Key Details**:
- Development mode: `python run_scoring_api.py` (hot reload)
- Production mode: `python run_scoring_api.py prod` (4 workers)
- Configurable via environment variables (HOST, PORT, WORKERS)

**When to Use**:
- Start `scoring_api.py` with proper configuration
- Easily switch between dev/prod modes

---

## 🔬 FUTURE PRODUCTION (Advanced Features)

### **4. `src/api.py`**
**Purpose**: Full-featured enterprise API with authentication, database, and audit logs

**Key Details**:
- **Port**: 8000 (from settings)
- **Authentication**: JWT (bcrypt + PyJWT)
- **Database**: SQLAlchemy (SQLite dev, PostgreSQL prod)
- **Models**: User, Application, Score, AuditLog, Feedback
- **Dual-model routing**: V1 (with evictions) vs V3 (financial only)
- **Request tracking**: Unique request IDs, middleware
- **Lines**: 443 lines

**Endpoints** (20+ endpoints):
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (returns JWT)
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/score` - Score applicant (saves to database)
- `GET /api/v1/scores/history` - Get scoring history
- `GET /api/v1/model/info` - Model metadata
- `GET /api/v1/health` - Health check
- And many more...

**Dependencies**:
- `src/config.py` - Settings management (Pydantic)
- `src/database.py` - SQLAlchemy models
- `src/auth.py` - JWT authentication
- `src/scoring.py` - Hybrid dual-model routing
- `src/features.py` - Feature engineering
- `src/utils.py` - Response formatters

**When to Use** (Future):
- Multi-user system with logins
- Tracking all applications and scores
- User roles (landlord, manager, admin)
- Audit logs for compliance
- API key authentication
- Production scaling with database

**How to Start**:
```powershell
python run_api.py
# Then open: http://127.0.0.1:8000/docs
```

**Status**: **NOT USED IN MVP** - Ready for production upgrade

---

### **5. `run_api.py`**
**Purpose**: Production runner for `src/api.py`

**Key Details**:
- Loads settings from `src/config.py`
- Shows startup info (environment, version, URLs)
- Development mode with hot reload
- Configurable host/port

**When to Use**:
- Start the full production API (`src/api.py`)
- When you need auth, database, and user management

---

## 🧪 TESTING FILES

### **6. `test_lovable_api.py`**
**Purpose**: Test script for `simple_api.py` (Render deployment)

**What it Tests**:
- Health endpoint
- Good applicant scoring
- High-risk applicant scoring
- Expected API: port 8001

**When to Use**:
- Verify Render deployment is working
- Test production API locally before deploying

**How to Run**:
```powershell
python test_lovable_api.py
```

---

### **7. `tests/test_api.py`**
**Purpose**: Unit tests for `src/api.py` (production API)

**What it Tests**:
- Health check endpoint
- Root endpoint
- User registration validation
- Score endpoint validation
- Uses pytest fixtures from `tests/conftest.py`

**When to Use**:
- Testing the full production API (`src/api.py`)
- Running automated test suite

**How to Run**:
```powershell
pytest tests/test_api.py -v
```

---

## 📊 QUICK DECISION MATRIX

| Scenario | Use This File | Command |
|----------|---------------|---------|
| **Testing locally (quick)** | `scoring_api.py` | `python run_scoring_api.py` then open `/docs` |
| **Lovable dashboard (production)** | `simple_api.py` | Already on Render |
| **Test Render deployment** | `test_lovable_api.py` | `python test_lovable_api.py` |
| **Future: Multi-user system** | `src/api.py` | `python run_api.py` |
| **Future: Unit testing** | `tests/test_api.py` | `pytest tests/` |

---

## 🔄 WORKFLOW EXAMPLES

### **Quick Local Testing:**
```powershell
# Start local API
python run_scoring_api.py

# Open browser
http://127.0.0.1:8002/docs

# Use Swagger UI "Try it out" button
# Test with sample data
# Get instant results
```

### **Testing Lovable Integration:**
```powershell
# Test Render deployment
python test_lovable_api.py

# Or visit directly
https://leaseth-mvp.onrender.com/health
```

### **Future Production Setup:**
```powershell
# Setup environment
cp .env.example .env
# Edit DATABASE_URL, JWT_SECRET

# Start production API
python run_api.py

# Access Swagger UI
http://127.0.0.1:8000/docs

# Register user, login, get token
# Use token for authenticated endpoints
```

---

## 🎯 KEY DIFFERENCES

### **`simple_api.py` vs `scoring_api.py`**

| Feature | simple_api.py | scoring_api.py |
|---------|---------------|----------------|
| **Purpose** | Production (Render) | Local testing |
| **Port** | 8001 | 8002 |
| **Deployed** | Yes (Render) | No (local only) |
| **Decision Logic** | Simple ML | Two-stage (rules + ML) |
| **Interface** | API only | Swagger UI |
| **CORS** | Enabled | Not needed |
| **Features** | Minimal | Feature list from pickle |

### **`simple_api.py` vs `src/api.py`**

| Feature | simple_api.py | src/api.py |
|---------|---------------|------------|
| **Complexity** | Minimal | Enterprise |
| **Auth** | None | JWT |
| **Database** | None | SQLAlchemy |
| **Users** | Single tenant | Multi-user |
| **Tracking** | None | Full audit logs |
| **Model** | honest_model.pkl | Dual-model routing |
| **Use Case** | MVP | Production scaling |

---

## 💡 TIPS

1. **For MVP**: Only use `simple_api.py` (on Render) and `scoring_api.py` (local testing)

2. **Avoid Render Free Tier Delays**: Use `scoring_api.py` locally instead of waking up Render every time

3. **Swagger UI is Your Friend**: All APIs have `/docs` endpoint for interactive testing

4. **Future Scaling**: When you need users, auth, and database → migrate to `src/api.py`

5. **Keep It Simple**: Don't run multiple APIs at once unless testing comparisons

---

## 📝 NOTES

- All APIs use `honest_model.pkl` (trained by `honest_model.py`)
- Port conflicts: If 8000/8001/8002 are busy, check for running Python processes
- Render deployment uses `Procfile` which runs `simple_api.py`
- Local testing APIs (`scoring_api.py`) are NOT meant for production deployment
- Always check `/health` endpoint first to verify model is loaded

---

## ❓ WHEN CONFUSED

**Q: Which API should I use for testing?**  
A: `scoring_api.py` locally (port 8002/docs), or `test_lovable_api.py` for Render

**Q: Which API is deployed on Render?**  
A: Only `simple_api.py` (via Procfile)

**Q: When should I use `src/api.py`?**  
A: When you need users, authentication, database tracking, or multi-tenant features

**Q: Can I delete `scoring_api.py`?**  
A: No! It's your quick local testing tool without waking up Render

**Q: Why do I have 3 different APIs?**  
A: 
- `simple_api.py` = MVP production (Render)
- `scoring_api.py` = Local testing (quick/fast)
- `src/api.py` = Future production (enterprise features)

---

**Need Help?** Check this file first before asking which API to use! 🎯
