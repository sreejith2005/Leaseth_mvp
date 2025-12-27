# Deploy to Railway - FREE 24/7 (No Credit Card Required!)

**Deploy your Leaseth API to Railway - TRUE 24/7 uptime with NO CARD NEEDED!**

---

## 🎯 WHY RAILWAY?

| Feature | Railway | Render (Free) | Fly.io |
|---------|---------|---------------|--------|
| **Credit Card Required** | ❌ NO | ❌ NO | ✅ YES |
| **Uptime** | ✅ 24/7 | ❌ Sleeps | ✅ 24/7 |
| **Free Credit** | $5/month | N/A | N/A |
| **Cold Starts** | ✅ None | ❌ 30-60s | ✅ None |
| **Memory** | 512MB-8GB | 512MB | 256MB |
| **Easy Setup** | ✅✅✅ | ✅✅ | ✅ |

**Winner: Railway** - No card + 24/7 + Easy! 🏆

---

## 📋 PREREQUISITES

1. ✅ GitHub account
2. ✅ Python FastAPI app (`simple_api.py`)
3. ✅ Model file (`models/honest_model.pkl`)
4. ❌ **NO CREDIT CARD NEEDED!**

---

## 🚀 STEP-BY-STEP DEPLOYMENT

### **STEP 1: Push Code to GitHub**

First, ensure your code is on GitHub:

```powershell
# Navigate to project
cd C:\Users\LENOVO\Downloads\leaseth_mvp_working_backup_3

# Check git status
git status

# Add and commit changes
git add .
git commit -m "Prepare for Railway deployment"

# Push to GitHub
git push origin main
```

---

### **STEP 2: Create Railway Account**

1. Go to: https://railway.app
2. Click **"Start a New Project"**
3. Sign up with **GitHub** (no card needed!)
4. Authorize Railway to access your repos

---

### **STEP 3: Create Necessary Files**

#### **A. Create `Procfile`**

Create a file named `Procfile` (no extension) in your project root:

```
web: uvicorn simple_api:app --host 0.0.0.0 --port $PORT
```

**Save as**: `Procfile`

#### **B. Create `runtime.txt`** (Optional but recommended)

```
python-3.12.0
```

**Save as**: `runtime.txt`

#### **C. Verify `requirements.txt`**

Make sure it has all dependencies:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
scikit-learn==1.3.2
xgboost==2.0.2
numpy==1.26.2
pandas==2.1.3
```

#### **D. Update `simple_api.py`**

Make sure the port uses environment variable:

```python
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

---

### **STEP 4: Commit New Files**

```powershell
# Add new files
git add Procfile runtime.txt requirements.txt simple_api.py

# Commit
git commit -m "Add Railway configuration"

# Push
git push origin main
```

---

### **STEP 5: Deploy on Railway**

1. **Go to Railway Dashboard**: https://railway.app/dashboard

2. **Click "New Project"**

3. **Select "Deploy from GitHub repo"**

4. **Choose your repository**: `Leaseth_mvp` (or whatever you named it)

5. **Railway auto-detects Python** and shows configuration

6. **Click "Deploy Now"**

**Railway will**:
- Detect Python project
- Install dependencies from `requirements.txt`
- Run `Procfile` command
- Assign a URL

**Deployment takes ~2-3 minutes**

---

### **STEP 6: Configure Environment (if needed)**

In Railway dashboard:

1. Click on your service
2. Go to **"Variables"** tab
3. Add any environment variables (usually not needed for simple_api.py)

---

### **STEP 7: Get Your URL**

1. Click on your deployed service
2. Go to **"Settings"** tab
3. Scroll to **"Domains"**
4. Click **"Generate Domain"**

**Your URL will be something like**:
```
https://leaseth-scoring-api-production.up.railway.app
```

---

### **STEP 8: Test Deployment**

```powershell
# Test health endpoint (replace with your URL)
curl https://leaseth-scoring-api-production.up.railway.app/health

# Or open in browser
start https://leaseth-scoring-api-production.up.railway.app/docs
```

**Expected response**:
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

---

## 🔄 UPDATE YOUR LOVABLE DASHBOARD

Update your Lovable frontend to use the Railway URL.

### **Option A: Environment Variable**

In `.env.production`:
```env
VITE_API_URL=https://leaseth-scoring-api-production.up.railway.app
```

### **Option B: Direct in Code**

```javascript
const API_URL = 'https://leaseth-scoring-api-production.up.railway.app';
```

### **Redeploy Frontend**

```powershell
# If using GitHub Pages
npm run deploy

# If using Vercel - just push
git add .
git commit -m "Update API URL to Railway"
git push origin main
```

---

## 🎉 COMPLETE ARCHITECTURE

```
Frontend (Lovable Dashboard):
├── Hosted: GitHub Pages
├── URL: https://sreejith2005.github.io/leaseth-dashboard/
└── Calls → Railway API

Backend (Scoring API):
├── Hosted: Railway ✅ 24/7 NO SLEEP
├── URL: https://leaseth-scoring-api-production.up.railway.app
├── Free Credit: $5/month (~500 hours)
├── Endpoints:
│   ├── GET  /health
│   ├── GET  /docs
│   └── POST /api/score
└── Model: honest_model.pkl
```

---

## 🔄 UPDATING YOUR API

**Every time you make changes**:

```powershell
# 1. Edit code locally
# (edit simple_api.py, etc.)

# 2. Test locally
python simple_api.py

# 3. Commit and push
git add .
git commit -m "Update API logic"
git push origin main

# 4. Railway auto-deploys!
# Live in ~2 minutes ✅
```

**Railway watches your GitHub repo and auto-deploys on every push!**

---

## 💰 RAILWAY FREE TIER

**What you get FREE (no card required)**:
- ✅ $5 execution credit/month
- ✅ ~500 hours of runtime (24/7 for a month!)
- ✅ 512MB RAM (expandable)
- ✅ Automatic deployments from GitHub
- ✅ Custom domains
- ✅ SSL certificates
- ✅ No sleep/cold starts

**After free credit runs out**:
- Railway will notify you
- Add a card later if needed (only pay for what you use)
- Or use a different free service

**Your app uses**: ~$2-3/month worth = Well within free tier! 🎉

---

## 🛠️ USEFUL RAILWAY FEATURES

### **View Logs**
1. Go to Railway dashboard
2. Click your service
3. Click **"Deployments"** tab
4. Click latest deployment
5. See real-time logs

### **Metrics**
1. Click **"Metrics"** tab
2. See CPU, memory, network usage

### **Custom Domain**
1. Go to **"Settings"** → **"Domains"**
2. Click **"Custom Domain"**
3. Add your domain (e.g., `api.leaseth.com`)

### **Environment Variables**
1. Go to **"Variables"** tab
2. Add key-value pairs
3. Auto-redeploys on change

---

## 🚨 TROUBLESHOOTING

### **Issue: Build fails**
**Solution**: Check Railway logs:
1. Dashboard → Your Service → Deployments
2. Look for Python errors
3. Common issues:
   - Missing package in `requirements.txt`
   - Syntax error in code
   - Model file not committed to GitHub

### **Issue: Model file missing**
**Solution**: Ensure `models/honest_model.pkl` is in GitHub:
```powershell
# Check if file is tracked
git ls-files models/

# If not, add it
git add models/honest_model.pkl
git commit -m "Add model file"
git push origin main
```

### **Issue: Port error**
**Solution**: Make sure `simple_api.py` uses `$PORT`:
```python
port = int(os.getenv("PORT", 8000))
```

### **Issue: CORS errors**
**Solution**: Update CORS in `simple_api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push to redeploy.

### **Issue: App crashes after deployment**
**Solution**: Check Railway logs for errors. Common fixes:
```powershell
# Update Procfile to correct format
web: uvicorn simple_api:app --host 0.0.0.0 --port $PORT

# Not:
# web: python simple_api.py  ← Wrong!
```

---

## ✅ DEPLOYMENT CHECKLIST

**Initial Setup**:
- [ ] Create Railway account (with GitHub - no card!)
- [ ] Create `Procfile`
- [ ] Create `runtime.txt`
- [ ] Update `simple_api.py` to use `$PORT`
- [ ] Verify `requirements.txt`
- [ ] Commit and push to GitHub
- [ ] Create new Railway project
- [ ] Connect GitHub repo
- [ ] Deploy
- [ ] Generate domain
- [ ] Test endpoints
- [ ] Update Lovable frontend URL
- [ ] Test end-to-end

**Every Update**:
- [ ] Make code changes locally
- [ ] Test locally
- [ ] Commit: `git commit -m "message"`
- [ ] Push: `git push origin main`
- [ ] Railway auto-deploys ✅

---

## 🆚 COMPARISON: All Free Options

| Platform | Card Required | 24/7 Uptime | Auto-Deploy | Ease |
|----------|---------------|-------------|-------------|------|
| **Railway** | ❌ NO | ✅ Yes | ✅ Yes | ⭐⭐⭐⭐⭐ |
| **Hugging Face** | ❌ NO | ✅ Yes | ✅ Yes | ⭐⭐⭐⭐ |
| Render | ❌ NO | ❌ Sleeps | ✅ Yes | ⭐⭐⭐⭐⭐ |
| Fly.io | ✅ YES | ✅ Yes | ❌ Manual | ⭐⭐⭐ |
| Vercel | ❌ NO | ✅ Yes | ✅ Yes | ⭐⭐⭐ (Node.js only) |

**Best for you: Railway** (No card + Easy + 24/7) 🏆

---

## 📊 MONITORING

### **Check Deployment Status**
Railway Dashboard → Your Service → Deployments

### **View Real-Time Logs**
Railway Dashboard → Deployments → Latest → View Logs

### **Check Resource Usage**
Railway Dashboard → Metrics → CPU/Memory/Network

### **Monitor Free Credit**
Railway Dashboard → Account → Usage

---

## 🎊 SUCCESS!

Your API is now live 24/7 at:
```
https://leaseth-scoring-api-production.up.railway.app
```

**Test it**:
```powershell
# Health check
curl https://leaseth-scoring-api-production.up.railway.app/health

# Docs
start https://leaseth-scoring-api-production.up.railway.app/docs
```

**Benefits**:
- ✅ **No credit card required**
- ✅ 24/7 uptime (no sleep)
- ✅ Auto-deploy from GitHub
- ✅ Free $5 credit monthly
- ✅ Easy to use
- ✅ Perfect for MVP

---

## 📝 QUICK COMMANDS

```powershell
# Deploy update
git add .
git commit -m "Update"
git push origin main
# Railway auto-deploys! ✅

# Test locally
python simple_api.py

# View in browser
start https://YOUR-URL.up.railway.app/docs
```

---

## 🔗 USEFUL LINKS

- Railway Dashboard: https://railway.app/dashboard
- Railway Docs: https://docs.railway.app
- Your Deployments: https://railway.app/project/YOUR-PROJECT-ID

---

**Your complete MVP is now 24/7 with NO CARD REQUIRED!** 🚀

**NO SLEEP + NO CARD + EASY UPDATES = Perfect Solution!** 🎉
