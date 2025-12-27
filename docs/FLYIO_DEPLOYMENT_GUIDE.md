# Deploy to Fly.io - FREE 24/7 Hosting

**Deploy your Leaseth API to Fly.io for TRUE 24/7 uptime (no sleep!)**

---

## 🎯 WHY FLY.IO?

| Feature | Render (Free) | Fly.io (Free) |
|---------|---------------|---------------|
| **Uptime** | ❌ Sleeps after 15 min | ✅ 24/7 Always On |
| **Cold Starts** | ❌ 30-60 seconds | ✅ None |
| **Memory** | 512 MB | 256 MB (3 VMs) |
| **Storage** | Ephemeral | Persistent volumes |
| **ML Models** | ✅ Yes | ✅ Yes |
| **Custom Domains** | ✅ Yes | ✅ Yes |
| **Cost** | $0 | $0 |

**Winner: Fly.io** - No sleep, always responsive! 🏆

---

## 📋 PREREQUISITES

1. ✅ Python FastAPI app (`simple_api.py`)
2. ✅ Model file (`models/honest_model.pkl`)
3. ✅ GitHub account
4. ✅ Credit card (for verification only - **NO CHARGES**)

---

## 🚀 STEP-BY-STEP DEPLOYMENT

### **STEP 1: Install Fly.io CLI**

**Windows (PowerShell)**:
```powershell
# Install Fly CLI
iwr https://fly.io/install.ps1 -useb | iex

# Verify installation
fly version
```

**Expected output**:
```
fly v0.x.x windows/amd64
```

---

### **STEP 2: Sign Up & Login**

```powershell
# Sign up (opens browser)
fly auth signup

# Or login if you have account
fly auth login
```

**Follow browser prompts**:
1. Create account (use GitHub or email)
2. Add credit card (for verification only - you won't be charged)
3. Return to terminal

---

### **STEP 3: Create Dockerfile**

Create `Dockerfile` in your project root:

```dockerfile
# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY simple_api.py .
COPY models/ models/

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "simple_api:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Save as**: `Dockerfile` (no extension)

---

### **STEP 4: Create .dockerignore**

Create `.dockerignore` file:

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.env
.venv
venv/
env/
.git/
.github/
.vscode/
*.log
data/
docs/
tests/
frontend/
catboost_info/
logs/
*.csv
.dockerignore
Dockerfile
docker-compose.yml
README.md
```

---

### **STEP 5: Update requirements.txt**

Make sure `requirements.txt` has all needed packages:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
scikit-learn==1.3.2
xgboost==2.0.2
numpy==1.26.2
pandas==2.1.3
```

**Verify your file**:
```powershell
cat requirements.txt
```

---

### **STEP 6: Update simple_api.py Port**

Fly.io uses **port 8080** by default. Update the file:

```python
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8080))  # Use PORT env var or default 8080
    uvicorn.run(app, host="0.0.0.0", port=port)
```

---

### **STEP 7: Initialize Fly App**

```powershell
# Navigate to project
cd C:\Users\LENOVO\Downloads\leaseth_mvp_working_backup_3

# Launch Fly.io setup
fly launch
```

**Interactive prompts** (answer as shown):

```
? Choose an app name (leave blank to generate one): leaseth-scoring-api
? Choose a region for deployment: ord (Chicago) or closest to you
? Would you like to set up a Postgresql database now? No
? Would you like to set up an Upstash Redis database now? No
? Would you like to deploy now? No (we'll configure first)
```

**This creates**: `fly.toml` configuration file

---

### **STEP 8: Configure fly.toml**

Edit the generated `fly.toml`:

```toml
app = "leaseth-scoring-api"
primary_region = "ord"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256

[env]
  PORT = "8080"
```

**Key settings**:
- `auto_stop_machines = false` - **Prevents sleep!**
- `min_machines_running = 1` - **Always keep 1 VM running**
- `memory_mb = 256` - Free tier size

---

### **STEP 9: Deploy to Fly.io**

```powershell
# Deploy!
fly deploy
```

**What happens**:
1. Builds Docker image (~2-3 minutes)
2. Uploads to Fly.io
3. Starts your app
4. Runs health checks
5. Assigns URL

**Expected output**:
```
==> Building image
==> Pushing image to fly
==> Deploying leaseth-scoring-api
--> v0 deployed successfully

Visit your newly deployed app at https://leaseth-scoring-api.fly.dev/
```

---

### **STEP 10: Verify Deployment**

```powershell
# Check app status
fly status

# Open in browser
fly open

# View logs
fly logs
```

**Test your API**:
```
https://leaseth-scoring-api.fly.dev/
https://leaseth-scoring-api.fly.dev/health
https://leaseth-scoring-api.fly.dev/docs
```

---

## 🔄 UPDATE YOUR LOVABLE DASHBOARD

Now point your Lovable frontend to the new Fly.io URL.

### **Option A: Environment Variable (Recommended)**

In your Lovable project, update `.env.production`:

```env
VITE_API_URL=https://leaseth-scoring-api.fly.dev
```

### **Option B: Direct in Code**

Find your API client file (usually `src/lib/api.js`):

```javascript
// Before
const API_URL = 'https://leaseth-mvp.onrender.com';

// After
const API_URL = 'https://leaseth-scoring-api.fly.dev';
```

### **Redeploy Lovable Dashboard**

```powershell
# If using GitHub Pages
npm run deploy

# If using Vercel
git add .
git commit -m "Update API URL to Fly.io"
git push origin main
# Vercel auto-deploys
```

---

## 🎉 COMPLETE ARCHITECTURE

```
Frontend (Lovable Dashboard):
├── Hosted: GitHub Pages / Vercel
├── URL: https://sreejith2005.github.io/leaseth-dashboard/
└── Calls → Fly.io API

Backend (Scoring API):
├── Hosted: Fly.io ✅ 24/7 NO SLEEP
├── URL: https://leaseth-scoring-api.fly.dev
├── Endpoints:
│   ├── GET  /health
│   ├── GET  /docs
│   └── POST /api/score
└── Model: honest_model.pkl (loaded at startup)
```

---

## 🛠️ USEFUL FLY.IO COMMANDS

```powershell
# Check app status
fly status

# View logs (real-time)
fly logs

# SSH into your app
fly ssh console

# Check resource usage
fly scale show

# Restart app
fly apps restart

# Open app in browser
fly open

# View dashboard
fly dashboard

# Deploy updates
fly deploy
```

---

## 🔄 UPDATING YOUR API

Every time you make changes:

```powershell
# 1. Update code locally (edit simple_api.py, etc.)

# 2. Test locally
python simple_api.py

# 3. Deploy to Fly.io
fly deploy

# That's it! Live in ~2 minutes
```

---

## 💰 FLY.IO FREE TIER LIMITS

**What you get FREE:**
- ✅ 3 shared-cpu-1x VMs (256MB RAM each)
- ✅ 3GB persistent storage
- ✅ 160GB outbound data transfer/month
- ✅ Unlimited inbound data
- ✅ Custom domains
- ✅ SSL certificates
- ✅ TRUE 24/7 uptime

**Your app uses**: 1 VM = Well within free limits! 🎉

**Monitor usage**:
```powershell
fly dashboard
```

---

## 🚨 TROUBLESHOOTING

### **Issue: Build fails - "No space left on device"**
**Solution**: Clean up Docker:
```powershell
docker system prune -a
```

### **Issue: App won't start - "Model not found"**
**Solution**: Ensure `models/honest_model.pkl` is NOT in `.dockerignore`:
```powershell
# Check .dockerignore doesn't have:
# models/  ← Remove this line if present
```

### **Issue: 502 Bad Gateway**
**Solution**: Check logs:
```powershell
fly logs
```
Look for Python errors. Common issues:
- Missing dependency in `requirements.txt`
- Port mismatch (must be 8080)
- Model file missing

### **Issue: CORS errors from Lovable**
**Solution**: Update CORS in `simple_api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all
        # Or specific:
        "https://sreejith2005.github.io",
        "https://your-lovable-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy:
```powershell
fly deploy
```

### **Issue: App is slow**
**Solution**: Fly.io free tier is shared CPU. If you need faster:
```powershell
# Upgrade to dedicated CPU (costs money)
fly scale vm dedicated-cpu-1x
```

---

## 📊 MONITORING

### **Check if app is running**:
```powershell
fly status
```

**Expected output**:
```
ID       NAME     STATUS  CHECKS  REGION  HEALTH
abc123   machine  started  passed  ord     healthy
```

### **Real-time logs**:
```powershell
fly logs
```

### **Resource usage**:
```powershell
fly scale show
```

---

## ✅ DEPLOYMENT CHECKLIST

**Initial Setup**:
- [ ] Install Fly CLI: `iwr https://fly.io/install.ps1 -useb | iex`
- [ ] Sign up: `fly auth signup`
- [ ] Create `Dockerfile`
- [ ] Create `.dockerignore`
- [ ] Update `simple_api.py` port to 8080
- [ ] Verify `requirements.txt`
- [ ] Initialize app: `fly launch`
- [ ] Configure `fly.toml` (set `auto_stop_machines = false`)
- [ ] Deploy: `fly deploy`
- [ ] Test endpoints: `/health`, `/docs`, `/api/score`
- [ ] Update Lovable dashboard API URL
- [ ] Test end-to-end integration

**Every Update**:
- [ ] Make code changes
- [ ] Test locally
- [ ] Deploy: `fly deploy`
- [ ] Verify: `fly status` and `fly logs`

---

## 🆚 COMPARISON: Render vs Fly.io

| Aspect | Render | Fly.io |
|--------|--------|--------|
| **Sleep** | ❌ Yes (15 min) | ✅ No |
| **Cold Start** | 30-60 seconds | None |
| **Always Available** | ❌ No | ✅ Yes |
| **Lovable Integration** | Works (with delays) | Works (instant) |
| **Free Tier** | 512MB, sleeps | 256MB, 24/7 |
| **ML Models** | ✅ Yes | ✅ Yes |
| **Ease of Deployment** | Very Easy | Easy |
| **Dashboard** | ✅ Good | ✅ Good |
| **Custom Domain** | ✅ Yes | ✅ Yes |

**Verdict**: Fly.io wins for 24/7 availability! 🏆

---

## 🎊 SUCCESS!

Your API is now live 24/7 at:
```
https://leaseth-scoring-api.fly.dev
```

**Test it**:
```powershell
# Health check
curl https://leaseth-scoring-api.fly.dev/health

# Or open in browser
start https://leaseth-scoring-api.fly.dev/docs
```

**Benefits**:
- ✅ No sleep - instant responses
- ✅ Free forever (within limits)
- ✅ Professional URL
- ✅ Easy updates
- ✅ Perfect for Lovable integration

---

## 📝 QUICK REFERENCE

```powershell
# Deploy
fly deploy

# Status
fly status

# Logs
fly logs

# Restart
fly apps restart

# Open dashboard
fly dashboard

# Open app
fly open

# SSH into app
fly ssh console
```

---

**Your complete MVP is now 24/7 with ZERO sleep!** 🚀
