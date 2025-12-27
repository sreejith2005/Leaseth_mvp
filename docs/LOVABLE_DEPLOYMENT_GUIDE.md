# Lovable Dashboard - Complete Execution Order

**From Model Training to Live Dashboard**

---

## 🎯 COMPLETE WORKFLOW

### **STEP 1: Train the Model** ✅ (One-time setup)

```powershell
# Navigate to project directory
cd C:\Users\LENOVO\Downloads\leaseth_mvp_working_backup_3

# Train the honest model
python honest_model.py
```

**What happens**:
- Loads `data/clean_tenant_dataset.csv` (50k records)
- Trains XGBoost classifier with 21 features
- Generates two files:
  - `models/honest_model.pkl` (model file)
  - `models/honest_features.pkl` (feature list)
- Shows training metrics on screen
- **Expected AUC**: ~72% (honest performance)

**Output files created**:
- ✅ `models/honest_model.pkl` - 91KB
- ✅ `models/honest_features.pkl` - Feature list

**Time**: ~2-5 minutes

---

### **STEP 2: Test Locally** ✅ (Optional but recommended)

```powershell
# Start local API for testing
python simple_api.py
```

**What happens**:
- Loads `models/honest_model.pkl`
- Starts API on port 8001
- Ready to accept requests

**Test the API (DEPRECATED)**:
```powershell
# In a new terminal, run test script
python test_lovable_api.py
```

**What you'll see**:
- ✅ Health check: Status OK
- ✅ Good applicant: LOW risk, APPROVE
- ✅ Bad applicant: HIGH risk, REJECT

**Expected output**:
```
Testing SIMPLE API FOR LOVABLE INTEGRATION
1. Health Check...
✓ Status: 200
  {'status': 'ok', 'model': 'honest_model'}

2. Scoring Good Applicant...
✓ Status: 200
  Risk Score: 23%
  Category: LOW
  Recommendation: APPROVE
  Confidence: 87.5%

3. Scoring High-Risk Applicant...
✓ Status: 200
  Risk Score: 78%
  Category: HIGH
  Recommendation: REJECT
```

**Stop local server**: Ctrl+C

---

### **STEP 3: Deploy to Render** ✅ (One-time setup)

#### **3.1: Prepare Files**

Ensure these files exist:
- ✅ `simple_api.py` - Your production API
- ✅ `Procfile` - Tells Render how to start
- ✅ `requirements.txt` - Dependencies
- ✅ `requirements_render.txt` - Render-specific
- ✅ `runtime.txt` - Python version
- ✅ `models/honest_model.pkl` - Model file

#### **3.2: Push to GitHub**

```powershell
# Add all changes
git add .

# Commit
git commit -m "Deploy Lovable MVP with honest model"

# Push to GitHub
git push origin new_stratergies
```

#### **3.3: Deploy on Render**

**On Render Dashboard**:
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `sreejith2005/Leaseth_mvp`
4. Select branch: `new_stratergies`

**Configure**:
- **Name**: `leaseth-mvp`
- **Region**: Choose closest to you
- **Branch**: `new_stratergies`
- **Build Command**: `pip install --upgrade pip setuptools wheel && pip install -r requirements_render.txt`
- **Start Command**: (Auto-detected from Procfile)
  ```
  uvicorn simple_api:app --host 0.0.0.0 --port $PORT
  ```
- **Plan**: Free

**Environment Variables** (if needed):
- None required for basic setup
- Render auto-provides `$PORT`

5. Click **"Create Web Service"**

**Wait for deployment** (~5-10 minutes):
- Render installs dependencies
- Loads model files
- Starts API

**Your live URL**:
```
https://leaseth-mvp.onrender.com
```

---

### **STEP 4: Verify Render Deployment** ✅

#### **4.1: Test Health Endpoint**

Open browser:
```
https://leaseth-mvp.onrender.com/health
```

**Expected response**:
```json
{
  "status": "ok",
  "model": "honest_model",
  "model_loaded": true,
  "feature_count": 21
}
```

#### **4.2: Test API Documentation**

```
https://leaseth-mvp.onrender.com/docs
```

You should see Swagger UI with:
- `GET /health`
- `POST /api/score`

#### **4.3: Test Scoring Endpoint**

In Swagger UI:
1. Click **POST /api/score**
2. Click **"Try it out"**
3. Use this sample data:
```json
{
  "applicant_id": "TEST001",
  "name": "John Doe",
  "age": 32,
  "monthly_income": 5000,
  "credit_score": 720,
  "monthly_rent": 1500,
  "employment_verified": true,
  "income_verified": true,
  "previous_evictions": 0,
  "rental_history_years": 5,
  "on_time_payments_percent": 95,
  "late_payments_count": 1,
  "security_deposit": 1500,
  "lease_term_months": 12,
  "bedrooms": 2,
  "market_median_rent": 1800,
  "local_unemployment_rate": 4.5,
  "inflation_rate": 3.2
}
```
4. Click **"Execute"**

**Expected response**:
```json
{
  "applicant_id": "TEST001",
  "risk_score": 25,
  "risk_category": "LOW",
  "recommendation": "APPROVE",
  "confidence": 0.85,
  "reasoning": "Good credit score (720), stable income...",
  "rent_to_income_ratio": 0.30,
  "model_version": "honest_v1"
}
```

---

### **STEP 5: Connect Lovable Dashboard** ✅

#### **5.1: Update Lovable API Configuration**

In your Lovable project settings:

**API Base URL**:
```
https://leaseth-mvp.onrender.com
```

**Score Endpoint**:
```
POST /api/score
```

#### **5.2: Configure Lovable Frontend**

In your Lovable dashboard code (JavaScript/React):

```javascript
const API_URL = "https://leaseth-mvp.onrender.com";

async function scoreApplicant(applicantData) {
  const response = await fetch(`${API_URL}/api/score`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(applicantData)
  });
  
  return await response.json();
}
```

#### **5.3: Test from Lovable**

1. Open your Lovable dashboard
2. Fill in applicant form
3. Click "Score Applicant" or "Submit"
4. Wait for response (2-3 seconds)
5. See risk score, category, recommendation

---

### **STEP 6: Monitor & Maintain** ✅

#### **Wake up Render (Free Tier)**

Render free tier sleeps after 15 minutes of inactivity.

**First request after sleep**: ~30-60 seconds (cold start)  
**Subsequent requests**: ~1-2 seconds

**To keep it awake**:
- Use a monitoring service (e.g., UptimeRobot, cron-job.org)
- Ping health endpoint every 10 minutes:
  ```
  https://leaseth-mvp.onrender.com/health
  ```

#### **Check Logs on Render**

On Render Dashboard:
1. Go to your service: `leaseth-mvp`
2. Click **"Logs"** tab
3. See real-time requests:
   ```
   INFO: Model loaded successfully
   INFO: 127.0.0.1 - "POST /api/score HTTP/1.1" 200 OK
   INFO: Scored applicant: APPROVE (Risk: 25%)
   ```

#### **Update Model (When needed)**

```powershell
# Retrain model
python honest_model.py

# Commit new model files
git add models/honest_model.pkl
git commit -m "Updated model with new training data"
git push origin new_stratergies

# Render auto-redeploys (if enabled)
# Or manually trigger deploy on Render dashboard
```

---

## 🎯 QUICK REFERENCE

### **Initial Setup (One-time)**
```powershell
1. python honest_model.py              # Train model (2-5 min)
2. python test_lovable_api.py          # Test locally (optional)
3. git push origin new_stratergies     # Push to GitHub
4. Deploy on Render dashboard          # Wait 5-10 min
5. Test: https://leaseth-mvp.onrender.com/health
6. Connect Lovable to API URL
```

### **Daily Development**
```powershell
# Quick local testing (no Render needed)
python run_scoring_api.py
# Open: http://127.0.0.1:8002/docs
```

### **Retrain & Redeploy**
```powershell
python honest_model.py                 # Retrain
git add models/ ; git commit -m "Update model" ; git push
# Render auto-redeploys
```

---

## ✅ SUCCESS CHECKLIST

- [ ] Model trained: `models/honest_model.pkl` exists (91KB)
- [ ] Local test passes: `python test_lovable_api.py` shows ✓
- [ ] GitHub updated: Latest code pushed
- [ ] Render deployed: Service status = "Live"
- [ ] Health check works: `/health` returns status OK
- [ ] API docs accessible: `/docs` shows Swagger UI
- [ ] Test scoring works: Sample applicant returns valid score
- [ ] Lovable connected: Dashboard can call API
- [ ] Dashboard shows results: Risk score displayed correctly

---

## 🔥 TROUBLESHOOTING

### **Issue: Model not found**
```
Solution: Ensure models/honest_model.pkl is in git repo and pushed
```

### **Issue: Render cold start (slow first request)**
```
Solution: Normal behavior on free tier. Use uptime monitor to keep warm.
```

### **Issue: CORS error in Lovable**
```
Solution: simple_api.py has CORS enabled with allow_origins=["*"]
Check Lovable is using correct API URL
```

### **Issue: 503 Service Unavailable**
```
Solution: Check Render logs. Model might have failed to load.
Verify all model files were deployed.
```

---

## 📝 FILE SUMMARY

**Required for Lovable**:
- ✅ `simple_api.py` - Production API
- ✅ `models/honest_model.pkl` - Trained model
- ✅ `models/honest_features.pkl` - Feature list (if used)
- ✅ `Procfile` - Render start command
- ✅ `requirements.txt` or `requirements_render.txt`

**Training**:
- ✅ `honest_model.py` - Training script
- ✅ `data/clean_tenant_dataset.csv` - Training data

**Testing**:
- ✅ `test_lovable_api.py` - Test Render deployment

---

**Now you have the complete path from training to live Lovable dashboard!** 🚀
