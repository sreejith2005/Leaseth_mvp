# Complete Render + Lovable Deployment Guide for AI Agents

**Last Updated:** December 6, 2025  
**Purpose:** Step-by-step guide to deploy a FastAPI ML model to Render and integrate with Lovable dashboard  
**Target Audience:** AI agents assisting with future model deployments

---

## 🎯 Overview

This guide walks through deploying a FastAPI-based ML scoring API to Render.com and connecting it to a Lovable frontend dashboard. Follow these steps exactly to avoid common pitfalls.

**Expected Outcome:**
- ✅ Live API at `https://[service-name].onrender.com`
- ✅ Lovable dashboard successfully calling API
- ✅ No CORS errors
- ✅ No Python version conflicts

---

## 📋 Prerequisites

### Required Files in Repository
```
your-repo/
├── simple_api.py                 # FastAPI application
├── requirements_render.txt       # Python dependencies
├── Procfile                      # Render startup command
├── runtime.txt                   # Python version specification
├── .python-version              # Alternative Python version file
└── models/
    └── your_model.pkl           # Trained model file
```

### GitHub Repository Setup
1. Model files (`.pkl`) must be committed with `git add -f models/*.pkl` (bypasses .gitignore)
2. Repository must be public or connected to Render via OAuth
3. Branch should be stable (e.g., `main`, `production`, or `new_strategies`)

---

## 🚀 Part 1: Render Deployment

### Step 1: Create Required Files

#### 1.1 Create `simple_api.py`
This is your FastAPI application. **Critical requirements:**

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pickle
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Your Scoring API", version="1.0.0")

# CORS Configuration - CRITICAL for Lovable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows Lovable domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model at startup
MODEL = None

@app.on_event("startup")
def load_model():
    global MODEL
    try:
        logger.info("Loading model...")
        with open('models/your_model.pkl', 'rb') as f:
            MODEL = pickle.load(f)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

# Health check endpoint - REQUIRED for Render monitoring
@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": MODEL is not None}

# Root endpoint
@app.get("/")
def root():
    return {"message": "API is running", "version": "1.0.0"}

# Pydantic models for request/response
class ApplicantInput(BaseModel):
    applicant_id: str = Field(..., description="Unique applicant ID")
    name: str = Field(..., description="Applicant name")
    age: int = Field(..., ge=18, le=120)
    monthly_income: float = Field(..., gt=0)
    credit_score: int = Field(..., ge=300, le=850)
    monthly_rent: float = Field(..., gt=0)
    # Add all other required fields with proper validation
    employment_verified: bool = Field(default=False)
    income_verified: bool = Field(default=False)
    previous_evictions: int = Field(default=0, ge=0)
    rental_history_years: float = Field(default=0, ge=0)
    on_time_payments_percent: float = Field(default=100, ge=0, le=100)
    late_payments_count: int = Field(default=0, ge=0)
    lease_term_months: int = Field(default=12, ge=1, le=60)
    security_deposit: float = Field(default=0, ge=0)
    bedrooms: int = Field(default=1, ge=1)
    market_median_rent: float = Field(default=0, ge=0)
    local_unemployment_rate: float = Field(default=5.0, ge=0)
    inflation_rate: float = Field(default=3.0, ge=0)

class ScoringResponse(BaseModel):
    success: bool
    applicant_id: str
    risk_score: int
    risk_category: str
    default_probability: float
    recommendation: str
    confidence: float
    reasoning: str

# Main scoring endpoint
@app.post("/api/score", response_model=ScoringResponse)
async def score_applicant(applicant: ApplicantInput):
    try:
        if MODEL is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Feature engineering (implement your logic)
        features = engineer_features(applicant)
        
        # Prediction
        X = prepare_features(features)  # Your feature preparation logic
        probability = MODEL.predict_proba(X)[0][1]
        risk_score = int(round(probability * 100))
        
        # Decision logic
        decision = make_decision(probability, risk_score, features)
        
        logger.info(f"Scored {applicant.applicant_id}: {risk_score}% risk")
        
        return ScoringResponse(
            success=True,
            applicant_id=applicant.applicant_id,
            risk_score=risk_score,
            risk_category=decision['risk_category'],
            default_probability=probability,
            recommendation=decision['recommendation'],
            confidence=abs(probability - 0.5) * 2,
            reasoning=decision['reasoning']
        )
    except Exception as e:
        logger.error(f"Scoring error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def engineer_features(applicant: ApplicantInput) -> dict:
    # Implement your feature engineering logic
    pass

def prepare_features(features: dict) -> np.ndarray:
    # Prepare features in correct order for model
    pass

def make_decision(probability: float, risk_score: int, features: dict) -> dict:
    # Implement your decision logic
    pass
```

**Key Points:**
- ✅ CORS middleware with `allow_origins=["*"]` is MANDATORY
- ✅ `/health` endpoint required for Render health checks
- ✅ Model loaded in `@app.on_event("startup")` (NOT in endpoint)
- ✅ Proper error handling with HTTPException
- ✅ Logging for debugging

#### 1.2 Create `requirements_render.txt`

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
numpy==1.26.2
pandas==2.1.3
scikit-learn==1.3.2
xgboost==2.0.2
setuptools>=65.0.0
wheel
```

**Critical Notes:**
- ✅ Use `uvicorn[standard]` (includes production dependencies)
- ✅ Include `setuptools>=65.0.0` and `wheel` (fixes build errors)
- ✅ Pin major versions but allow patch updates
- ⚠️ If using other ML libraries (catboost, lightgbm), add them here

#### 1.3 Create `Procfile`

```
web: uvicorn simple_api:app --host 0.0.0.0 --port $PORT
```

**Format:**
- No file extension
- `web:` must be lowercase
- `simple_api:app` = `filename:fastapi_instance_name`
- `$PORT` is environment variable provided by Render

#### 1.4 Create `runtime.txt`

```
python-3.11.9
```

**Python Version Strategy:**
- ✅ Use Python 3.11.x (best compatibility with XGBoost/FastAPI)
- ❌ Avoid Python 3.13 (causes setuptools.build_meta errors)
- ❌ Avoid Python 3.9 or older (missing features)

#### 1.5 Create `.python-version` (Optional Backup)

```
python-3.11.0
```

This serves as a backup if `runtime.txt` is ignored.

---

### Step 2: Commit and Push to GitHub

```powershell
# Stage all deployment files
git add simple_api.py requirements_render.txt Procfile runtime.txt .python-version

# Force add model files (they're usually in .gitignore)
git add -f models/*.pkl

# Commit
git commit -m "Add Render deployment configuration"

# Push to your deployment branch
git push origin new_strategies
```

**Verification:**
- Go to GitHub repository
- Verify all files are present in the branch
- Confirm model `.pkl` files are visible (check file sizes)

---

### Step 3: Create Render Service

#### 3.1 Sign Up / Log In
- Go to https://dashboard.render.com
- Sign up with GitHub (recommended for OAuth integration)

#### 3.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect GitHub repository (grant OAuth access if needed)
3. Select your repository (e.g., `sreejith2005/Leaseth_mvp`)
4. Select branch (e.g., `new_strategies`)

#### 3.3 Configure Service Settings

**Basic Configuration:**
- **Name:** `leaseth-mvp` (or your preferred name, becomes part of URL)
- **Region:** Select closest to users (e.g., `Oregon (US West)`)
- **Branch:** `new_strategies` (or your deployment branch)
- **Root Directory:** Leave blank (unless API is in subdirectory)
- **Runtime:** Select **Python 3**

**Build & Deploy Settings:**
- **Build Command:** 
  ```bash
  pip install --upgrade pip setuptools wheel && pip install -r requirements_render.txt
  ```
  ⚠️ This is CRITICAL - forces pip/setuptools upgrade before installing dependencies

- **Start Command:** 
  ```bash
  uvicorn simple_api:app --host 0.0.0.0 --port $PORT
  ```
  (Should auto-detect from Procfile, but specify anyway)

**Instance Type:**
- Select **Free** (sufficient for MVP, spins down after 15 min inactivity)
- Upgrade to Starter ($7/mo) for 24/7 uptime if needed

#### 3.4 Environment Variables (Optional)
Add if your app uses secrets:
- `JWT_SECRET` = your-secret-key
- `DATABASE_URL` = your-db-url
- `MODEL_PATH` = models/your_model.pkl

---

### Step 4: Deploy and Monitor

#### 4.1 Trigger Deploy
- Click **"Create Web Service"**
- Deployment starts automatically
- Monitor build logs in real-time

#### 4.2 Watch for Common Errors

**Error 1: Python 3.13 being used instead of 3.11**
```
ERROR: Could not build wheels for setuptools
/opt/render/project/src/.venv/lib/python3.13/...
```

**Solution:**
1. Edit **Build Command** in Render dashboard:
   ```bash
   pip install --upgrade pip setuptools wheel && pip install -r requirements_render.txt
   ```
2. Trigger manual redeploy
3. If still failing, delete service and recreate (Render may cache Python version)

**Error 2: Model file not found**
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/your_model.pkl'
```

**Solution:**
- Verify model is committed: `git ls-files | grep models/`
- Force add if missing: `git add -f models/*.pkl`
- Push again: `git push origin new_strategies`

**Error 3: CORS errors (after deployment)**
```
No 'Access-Control-Allow-Origin' header is present
```

**Solution:**
- Verify `CORSMiddleware` is configured with `allow_origins=["*"]`
- Redeploy after fixing `simple_api.py`

**Error 4: Port binding error**
```
Error binding to port
```

**Solution:**
- Ensure Procfile uses `--port $PORT` (not hardcoded port)
- Verify Start Command matches Procfile

#### 4.3 Verify Successful Deployment

**Deployment logs should show:**
```
==> Build successful 🎉
==> Deploying...
==> Starting service with 'uvicorn simple_api:app --host 0.0.0.0 --port $PORT'
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Loading model...
INFO:     Model loaded successfully
INFO:     Application startup complete.
==> Your service is live 🎉
https://leaseth-mvp.onrender.com
```

**Test endpoints:**
```powershell
# Health check
Invoke-WebRequest -Uri "https://leaseth-mvp.onrender.com/health"
# Should return: {"status":"healthy","model_loaded":true}

# Root endpoint
Invoke-WebRequest -Uri "https://leaseth-mvp.onrender.com/"
# Should return: {"message":"API is running","version":"1.0.0"}
```

---

## 🎨 Part 2: Lovable Dashboard Integration

### Step 1: Prepare Lovable Prompt

**Important:** Lovable uses AI to generate code from natural language prompts. Be EXTREMELY specific to avoid wasting credits.

#### Optimal Prompt Structure:

```
Update the tenant risk scoring form to connect to production API at https://[YOUR-SERVICE-NAME].onrender.com/api/score

CRITICAL REQUIREMENTS:

1. API ENDPOINT
URL: https://[YOUR-SERVICE-NAME].onrender.com/api/score
Method: POST
Headers: Content-Type: application/json

2. REQUEST BODY STRUCTURE
Send this exact JSON (replace [values] with form inputs):

{
  "applicant_id": "AUTO_" + Date.now(),
  "name": [value from name input],
  "age": [value as number, min 18, max 120],
  "monthly_income": [value as number, must be > 0],
  "credit_score": [value as number, 300-850],
  "monthly_rent": [value as number, must be > 0],
  "employment_verified": [boolean from checkbox],
  "income_verified": [boolean from checkbox],
  "previous_evictions": [number, default 0],
  "rental_history_years": [number, default 0],
  "on_time_payments_percent": [number 0-100, default 100],
  "late_payments_count": [number, default 0],
  "lease_term_months": [number, default 12],
  "security_deposit": [number, default 0],
  "bedrooms": [number, default 1],
  "market_median_rent": [number, default 0],
  "local_unemployment_rate": [number, default 5.0],
  "inflation_rate": [number, default 3.0]
}

3. FETCH CODE
const response = await fetch('https://[YOUR-SERVICE-NAME].onrender.com/api/score', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(applicantData)
});

if (!response.ok) {
  throw new Error(`API error: ${response.status}`);
}

const result = await response.json();

4. RESPONSE STRUCTURE
API returns:
{
  "success": true,
  "applicant_id": "AUTO_1733123456",
  "risk_score": 65,
  "risk_category": "MEDIUM",
  "default_probability": 0.65,
  "recommendation": "MANUAL_REVIEW (Lean Reject)",
  "confidence": 0.29,
  "reasoning": "Elevated risk. Recommend increased deposit."
}

5. UI DISPLAY
Show results in a card:
- Risk Score: Large number with color coding
  - Green if risk_score < 40
  - Yellow if 40 <= risk_score <= 70
  - Red if risk_score > 70
- Risk Category: Badge (LOW/MEDIUM/HIGH)
- Recommendation: Bold text
- Reasoning: Paragraph text
- Confidence: Display as percentage (confidence * 100)

6. ERROR HANDLING
- Add loading state: "Analyzing applicant... (first request may take 30-60 seconds)"
- Show error message if fetch fails
- Validate required fields before submit

7. FORM VALIDATION
Required fields with validation:
- name: string, required
- age: number, 18-120
- monthly_income: number, > 0
- credit_score: number, 300-850
- monthly_rent: number, > 0

Optional fields with defaults (include all in request):
- employment_verified: boolean, default false
- income_verified: boolean, default false
- previous_evictions: number, default 0
- rental_history_years: number, default 0
- on_time_payments_percent: number, default 100
- late_payments_count: number, default 0
- lease_term_months: number, default 12
- security_deposit: number, default 0
- bedrooms: number, default 1
- market_median_rent: number, default 0
- local_unemployment_rate: number, default 5.0
- inflation_rate: number, default 3.0

Keep existing UI styling. Focus on correct API integration.
```

**Replace `[YOUR-SERVICE-NAME]` with your actual Render service name.**

---

### Step 2: Common Lovable Integration Issues

#### Issue 1: Still Using Old URL (ngrok/localhost)
**Symptoms:**
```
Access to fetch at 'https://88c2b9794cf8.ngrok-free.app/api/score' has been blocked by CORS
```

**Solution:**
Provide updated prompt:
```
CRITICAL FIX: Replace ALL fetch URLs with https://[YOUR-SERVICE-NAME].onrender.com/api/score

Remove any references to:
- localhost URLs
- ngrok URLs
- Any old API endpoints

Update fetch call to:
const response = await fetch('https://[YOUR-SERVICE-NAME].onrender.com/api/score', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(applicantData)
});
```

#### Issue 2: Missing Required Fields
**Symptoms:**
```
422 Unprocessable Entity
Field required: applicant_id
```

**Solution:**
Verify form sends ALL required fields. Check Pydantic model in `simple_api.py` for required fields (those without `default=`).

Update Lovable prompt:
```
Ensure request body includes ALL required fields:
- applicant_id (auto-generate with "AUTO_" + Date.now())
- name
- age
- monthly_income
- credit_score
- monthly_rent

Include optional fields with defaults if not provided by user.
```

#### Issue 3: Type Mismatches
**Symptoms:**
```
422 Unprocessable Entity
value is not a valid integer
```

**Solution:**
```
Convert form values to correct types before sending:
- age: parseInt(formData.age)
- monthly_income: parseFloat(formData.monthly_income)
- credit_score: parseInt(formData.credit_score)
- employment_verified: Boolean(formData.employment_verified)
```

#### Issue 4: Cold Start Timeout
**Symptoms:**
- First request takes 30-60 seconds
- User sees "Failed to fetch" error

**Solution:**
Add loading state with clear message:
```
Show loading message: "Analyzing applicant... This may take 30-60 seconds on first request (API is waking up). Subsequent requests will be instant."

Set fetch timeout to 65 seconds:
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 65000);

const response = await fetch(url, {
  ...options,
  signal: controller.signal
});

clearTimeout(timeoutId);
```

---

## 🧪 Part 3: Testing the Integration

### Test 1: Health Check
```powershell
Invoke-WebRequest -Uri "https://[YOUR-SERVICE-NAME].onrender.com/health"
```
**Expected:** `{"status":"healthy","model_loaded":true}`

### Test 2: API Scoring (Good Tenant)
```powershell
$body = @{
    applicant_id = "TEST001"
    name = "John Doe"
    age = 28
    monthly_income = 5500
    credit_score = 720
    monthly_rent = 1400
    employment_verified = $true
    income_verified = $true
    previous_evictions = 0
    rental_history_years = 4
    on_time_payments_percent = 95
    late_payments_count = 0
    lease_term_months = 12
    security_deposit = 2800
    bedrooms = 2
    market_median_rent = 1500
    local_unemployment_rate = 5.0
    inflation_rate = 3.0
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://[YOUR-SERVICE-NAME].onrender.com/api/score" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

**Expected:** Risk score 20-40% (LOW risk, AUTO_APPROVE)

### Test 3: API Scoring (High-Risk Tenant)
```powershell
$body = @{
    applicant_id = "TEST002"
    name = "Jane Smith"
    age = 22
    monthly_income = 2000
    credit_score = 550
    monthly_rent = 1800
    employment_verified = $false
    income_verified = $false
    previous_evictions = 2
    rental_history_years = 0.5
    on_time_payments_percent = 60
    late_payments_count = 5
    lease_term_months = 6
    security_deposit = 900
    bedrooms = 1
    market_median_rent = 1500
    local_unemployment_rate = 7.0
    inflation_rate = 4.5
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://[YOUR-SERVICE-NAME].onrender.com/api/score" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

**Expected:** Risk score 70-100% (HIGH risk, AUTO_REJECT)

### Test 4: End-to-End via Lovable
1. Open Lovable dashboard
2. Fill form with good tenant data
3. Submit form
4. Verify results display correctly
5. Check browser console for errors (F12 → Console tab)

---

## 🔧 Troubleshooting Reference

### Problem: Render build fails with Python 3.13 error
**Error Message:**
```
ERROR: Could not import 'setuptools.build_meta'
/opt/render/project/src/.venv/lib/python3.13/
```

**Root Cause:** Render is ignoring `runtime.txt` and using Python 3.13 (incompatible with some packages)

**Solutions (in order of preference):**
1. **Edit Build Command** in Render dashboard:
   ```bash
   pip install --upgrade pip setuptools wheel && pip install -r requirements_render.txt
   ```
2. **Delete and recreate service** (Render may cache Python version)
3. **Contact Render support** to manually set Python 3.11

---

### Problem: Model file not loading
**Error Message:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/your_model.pkl'
```

**Root Cause:** Model file not in GitHub repository (usually .gitignored)

**Solution:**
```powershell
# Force add model files
git add -f models/*.pkl

# Commit and push
git commit -m "Add model files for deployment"
git push origin new_strategies

# Trigger manual deploy in Render dashboard
```

---

### Problem: CORS errors in browser
**Error Message:**
```
Access to fetch from origin '...' has been blocked by CORS policy
```

**Root Cause:** Missing or incorrect CORS middleware configuration

**Solution:**
Update `simple_api.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # CRITICAL: Must be ["*"] or specific Lovable domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Redeploy after fixing.

---

### Problem: 422 Unprocessable Entity
**Error Message:**
```
422 Unprocessable Entity
Field required: [field_name]
```

**Root Cause:** Missing required fields or type mismatches

**Solution:**
1. Check Pydantic model in `simple_api.py` for required fields
2. Verify Lovable form sends all required fields
3. Ensure type conversions (parseInt, parseFloat, Boolean)
4. Test with curl/PowerShell first to isolate issue

---

### Problem: Cold start timeout
**Error Message:**
```
Failed to fetch
```

**Root Cause:** Render free tier spins down after 15 min inactivity. First request takes 30-60 seconds.

**Solution:**
1. Add loading state in Lovable: "First request may take 30-60 seconds"
2. Increase fetch timeout to 65 seconds
3. Consider upgrading to Render Starter ($7/mo) for 24/7 uptime
4. Use external service to ping API every 10 minutes (keeps it warm)

---

## 📚 Additional Resources

### Render Documentation
- **Python on Render:** https://render.com/docs/deploy-python
- **Environment Variables:** https://render.com/docs/environment-variables
- **Health Checks:** https://render.com/docs/health-checks

### FastAPI Documentation
- **CORS:** https://fastapi.tiangolo.com/tutorial/cors/
- **Pydantic Models:** https://docs.pydantic.dev/latest/

### Debugging Tools
- **Render Logs:** Dashboard → Your Service → Logs tab
- **Browser DevTools:** F12 → Console/Network tabs
- **API Testing:** Use Postman or PowerShell Invoke-WebRequest

---

## ✅ Deployment Checklist

Use this checklist for future deployments:

### Pre-Deployment
- [ ] Model file trained and saved as `.pkl`
- [ ] `simple_api.py` created with CORS middleware
- [ ] `requirements_render.txt` with all dependencies
- [ ] `Procfile` with correct startup command
- [ ] `runtime.txt` with Python 3.11.9
- [ ] All files committed to GitHub
- [ ] Model files force-added with `git add -f`

### Render Setup
- [ ] Service created on Render
- [ ] Correct repository and branch selected
- [ ] Build command includes pip upgrade
- [ ] Start command matches Procfile
- [ ] Python 3 runtime selected
- [ ] Environment variables added (if needed)

### Deployment Verification
- [ ] Build logs show "Build successful 🎉"
- [ ] Deploy logs show "Model loaded successfully"
- [ ] Service status shows "Live"
- [ ] `/health` endpoint returns 200 OK
- [ ] Test scoring request returns valid response

### Lovable Integration
- [ ] Prompt includes correct Render URL
- [ ] All required fields specified
- [ ] Type conversions included
- [ ] Loading state added
- [ ] Error handling implemented

### End-to-End Testing
- [ ] Form submission works
- [ ] Results display correctly
- [ ] No console errors
- [ ] Colors/badges render properly
- [ ] Second request is fast (<2 seconds)

---

## 🎯 Quick Reference Commands

### Git Commands
```powershell
# Force add model files
git add -f models/*.pkl

# Commit deployment files
git commit -m "Add deployment configuration"

# Push to deployment branch
git push origin new_strategies
```

### Testing Commands
```powershell
# Health check
Invoke-WebRequest -Uri "https://[SERVICE-NAME].onrender.com/health"

# Score applicant
$body = @{ applicant_id = "TEST001"; name = "Test"; age = 30; ... } | ConvertTo-Json
Invoke-WebRequest -Uri "https://[SERVICE-NAME].onrender.com/api/score" -Method POST -Body $body -ContentType "application/json"
```

### Render Dashboard URLs
- **Dashboard:** https://dashboard.render.com
- **Service Logs:** https://dashboard.render.com/web/[service-id]/logs
- **Service Settings:** https://dashboard.render.com/web/[service-id]/settings

---

## 🚨 Critical Warnings for AI Agents

1. **NEVER use localhost or ngrok URLs in production** - Always use the Render URL
2. **ALWAYS include CORS middleware** - Without it, Lovable cannot connect
3. **ALWAYS force-add model files** - They're usually in .gitignore
4. **ALWAYS use Python 3.11** - Python 3.13 causes build errors
5. **ALWAYS include setuptools in requirements** - Prevents build failures
6. **ALWAYS test with PowerShell/curl first** - Isolate API issues before testing frontend
7. **ALWAYS mention cold start behavior** - Users need to know about 30-60 second delays
8. **NEVER hardcode ports** - Use `$PORT` environment variable
9. **ALWAYS load models at startup** - Not in endpoint handlers
10. **ALWAYS provide detailed Lovable prompts** - Vague prompts waste credits

---

## 📝 Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-06 | 1.0.0 | Initial guide based on successful Leaseth MVP deployment |

---

**End of Guide**

For questions or issues not covered here, refer to Render documentation or check service logs for specific error messages.
