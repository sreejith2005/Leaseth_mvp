# Deploy to Hugging Face Spaces - FREE 24/7 (ACTUALLY WORKS!)

**No credit card, built for ML models, deploys in 5 minutes!**

---

## 🎯 WHY HUGGING FACE?

| Feature | Railway | Hugging Face | Fly.io |
|---------|---------|--------------|--------|
| **Card Required** | ❌ NO | ❌ NO | ✅ YES |
| **GitHub Works** | ❌ BROKEN | ✅ WORKS | ✅ Works |
| **24/7 Uptime** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Built for ML** | ❌ No | ✅ YES | ❌ No |
| **Setup Time** | ❌ 2 hours fighting | ✅ 5 minutes | ⚠️ 15 min |
| **File Upload** | ❌ No | ✅ YES | ❌ No |

**Winner: Hugging Face** - It just works! 🏆

---

## 📋 WHAT YOU GET FREE

- ✅ **2 vCPU**
- ✅ **16GB RAM**
- ✅ **50GB storage**
- ✅ **24/7 uptime**
- ✅ **NO CREDIT CARD**
- ✅ **Built-in GPU option** (for future)
- ✅ **Automatic HTTPS**
- ✅ **Custom domains**

---

## 🚀 DEPLOYMENT STEPS

### **STEP 1: Sign Up**

1. Go to: https://huggingface.co/join
2. Click **"Sign up with GitHub"** (one click!)
3. Authorize Hugging Face
4. **Done!** No card needed

---

### **STEP 2: Create a Space**

1. Go to: https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in:
   - **Owner**: Your username
   - **Space name**: `leaseth-scoring-api`
   - **License**: Apache 2.0
   - **Select SDK**: **Docker** (important!)
   - **Space hardware**: CPU basic - 2 vCPU - 16GB (FREE)
   - **Visibility**: Public (required for free tier)
4. Click **"Create Space"**

---

### **STEP 3: Prepare Files Locally**

We need these files in your project:

#### **A. Create Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY simple_api.py app.py
COPY models/ models/

# Hugging Face expects port 7860
EXPOSE 7860

# Run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

**Save as**: `Dockerfile`

#### **B. Create README for Space**

```markdown
---
title: Leaseth Scoring API
emoji: 🏠
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Leaseth Tenant Risk Scoring API

Fast, reliable tenant risk assessment API powered by XGBoost.

## Endpoints

- **POST /api/score** - Score a tenant applicant
- **GET /health** - Health check
- **GET /docs** - API documentation

## Model

- XGBoost honest model
- 72.26% AUC
- 21 engineered features
- Real-time scoring

Built for Leaseth MVP - 24/7 tenant screening.
```

**Save as**: `README.md` (this will show on your Space page)

#### **C. Verify requirements.txt**

Make sure it's clean:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
scikit-learn==1.3.2
xgboost==2.0.2
numpy==1.26.2
pandas==2.1.3
```

---

### **STEP 4: Upload Files**

**Option A: Direct Upload (Easiest)**

1. Go to your Space: https://huggingface.co/spaces/YOUR_USERNAME/leaseth-scoring-api
2. Click **"Files"** tab
3. Click **"Add file"** → **"Upload files"**
4. Drag and drop:
   - `Dockerfile`
   - `README.md`
   - `requirements.txt`
   - `app.py` (or `simple_api.py` - rename to `app.py`)
   - `models/honest_model.pkl`
5. Click **"Commit changes to main"**
6. **Automatic build starts!**

**Option B: GitHub Sync (If you want auto-updates)**

1. In your Space, click **"Settings"**
2. Scroll to **"Linked repositories"**
3. Click **"Link a GitHub repository"**
4. Select `Leaseth_mvp`
5. Choose sync mode: **"Pull changes from GitHub"**
6. Click **"Link repository"**
7. Every push to GitHub auto-deploys!

---

### **STEP 5: Wait for Build**

**What happens**:
1. Hugging Face builds Docker image (~3-5 minutes)
2. Starts container
3. Runs health checks
4. Shows **"Running"** status

**Watch build logs**:
- Click **"Logs"** tab
- See real-time build progress

**Expected at end of logs**:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7860
```

---

### **STEP 6: Test Your API**

**Your URL**:
```
https://YOUR_USERNAME-leaseth-scoring-api.hf.space
```

**Test endpoints**:
```
https://YOUR_USERNAME-leaseth-scoring-api.hf.space/
https://YOUR_USERNAME-leaseth-scoring-api.hf.space/health
https://YOUR_USERNAME-leaseth-scoring-api.hf.space/docs
```

**Try it**:
```powershell
# Health check
curl https://YOUR_USERNAME-leaseth-scoring-api.hf.space/health

# Or open in browser
start https://YOUR_USERNAME-leaseth-scoring-api.hf.space/docs
```

---

### **STEP 7: Update Lovable Dashboard**

Point your frontend to Hugging Face URL.

#### **In your Lovable project**:

Update API URL to:
```javascript
const API_URL = 'https://YOUR_USERNAME-leaseth-scoring-api.hf.space';
```

Or in `.env.production`:
```env
VITE_API_URL=https://YOUR_USERNAME-leaseth-scoring-api.hf.space
```

#### **Redeploy frontend**:
```powershell
npm run deploy  # If using GitHub Pages
# Or just push to GitHub if using Vercel
```

---

## 🎉 COMPLETE ARCHITECTURE

```
Frontend (Lovable Dashboard):
├── Hosted: GitHub Pages
├── URL: https://sreejith2005.github.io/leaseth-dashboard/
└── Calls → Hugging Face API

Backend (Scoring API):
├── Hosted: Hugging Face Spaces ✅ 24/7
├── URL: https://USERNAME-leaseth-scoring-api.hf.space
├── Resources: 2 vCPU, 16GB RAM, FREE
├── Endpoints:
│   ├── GET  /health
│   ├── GET  /docs
│   └── POST /api/score
└── Model: honest_model.pkl (72MB XGBoost)
```

---

## 🔄 UPDATING YOUR API

**Method 1: Direct Upload**

1. Edit code locally
2. Test: `python simple_api.py`
3. Go to Space → Files → Upload files
4. Upload updated files
5. Auto-redeploys in ~2 minutes

**Method 2: GitHub Sync (if linked)**

```powershell
# 1. Make changes
# edit simple_api.py or app.py

# 2. Commit and push
git add .
git commit -m "Update API"
git push origin main

# 3. Hugging Face auto-deploys!
```

---

## 🛠️ USEFUL FEATURES

### **View Logs**
Space page → **"Logs"** tab → See real-time application logs

### **Restart Space**
Settings → **"Factory reboot"** → Restart container

### **Change Hardware**
Settings → **"Space hardware"** → Upgrade (costs money) or keep free tier

### **Add Secrets**
Settings → **"Repository secrets"** → Add environment variables

### **Custom Domain**
Settings → **"Custom domains"** → Add your domain (free!)

### **Embed Space**
Get embed code to show Space on your website

---

## 🚨 TROUBLESHOOTING

### **Issue: Build fails - "Model not found"**
**Solution**: Make sure you uploaded `models/honest_model.pkl`

Check Files tab - should see:
```
Dockerfile
README.md
requirements.txt
app.py
models/
  └── honest_model.pkl
```

### **Issue: Port error**
**Solution**: Hugging Face expects **port 7860**. Check Dockerfile:
```dockerfile
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

### **Issue: Application not starting**
**Solution**: Check Logs tab for errors. Common issues:
- Missing dependency in requirements.txt
- Python syntax error
- Model file path wrong

### **Issue: CORS errors**
**Solution**: Update `app.py` CORS settings:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Upload updated file.

### **Issue: Space keeps rebuilding**
**Solution**: Don't edit files directly on HF - use local edits + upload to avoid conflicts

---

## ✅ DEPLOYMENT CHECKLIST

**Initial Setup**:
- [ ] Sign up: https://huggingface.co/join (use GitHub)
- [ ] Create new Space (SDK: Docker, Hardware: CPU basic)
- [ ] Create `Dockerfile` (port 7860)
- [ ] Create `README.md` (Space description)
- [ ] Verify `requirements.txt`
- [ ] Copy `simple_api.py` to `app.py`
- [ ] Upload all files to Space
- [ ] Wait for build (~5 minutes)
- [ ] Test URL: `/health`, `/docs`, `/api/score`
- [ ] Update Lovable frontend URL
- [ ] Test end-to-end integration

**Every Update**:
- [ ] Edit code locally
- [ ] Test: `python app.py`
- [ ] Upload to Space or push to GitHub
- [ ] Wait for auto-rebuild
- [ ] Verify: Check Logs and test endpoints

---

## 💰 COST COMPARISON

| Service | Monthly Cost | Setup Time | Reliability |
|---------|--------------|------------|-------------|
| **Hugging Face** | **$0** | **5 min** | **✅ High** |
| Railway | $0 (if working) | 2+ hours | ❌ Broken |
| Render | $0 | 10 min | ⚠️ Sleeps |
| Fly.io | $0 | 15 min | ✅ High (needs card) |

**Hugging Face = Best choice for your situation!** 🎉

---

## 🆚 WHY HUGGING FACE > RAILWAY

| Aspect | Railway | Hugging Face |
|--------|---------|--------------|
| **GitHub Integration** | ❌ Broken for you | ✅ Works perfectly |
| **File Upload** | ❌ No | ✅ Yes (drag & drop!) |
| **Setup Complexity** | ❌ High (wasted 2 hours) | ✅ Low (5 minutes) |
| **ML Model Support** | ⚠️ Generic | ✅ Built for it |
| **Documentation** | ⚠️ Okay | ✅ Excellent |
| **Community** | Small | Huge (ML community) |
| **Free Tier** | $5/month | 2 vCPU + 16GB RAM |
| **Card Required** | ❌ No | ❌ No |

**Verdict: Stop fighting Railway, use Hugging Face!** 🏆

---

## 📊 MONITORING

### **Check Status**
Space page → Top shows: **"Running"** (green) or **"Building"** (yellow)

### **View Metrics**
Space page → **"Logs"** tab → See CPU/Memory usage at bottom

### **Request Count**
Space page → Shows total requests served

---

## 🎊 SUCCESS!

Your API is now live 24/7 at:
```
https://YOUR_USERNAME-leaseth-scoring-api.hf.space
```

**Test it**:
```powershell
curl https://YOUR_USERNAME-leaseth-scoring-api.hf.space/health
```

**Benefits**:
- ✅ **No credit card** (unlike Fly.io)
- ✅ **Actually works** (unlike Railway for you)
- ✅ **24/7 uptime** (unlike Render)
- ✅ **Built for ML models** (perfect for XGBoost)
- ✅ **File upload** (no fighting with git)
- ✅ **2 vCPU + 16GB RAM free**
- ✅ **5 minute setup**

---

## 📝 QUICK COMMANDS

```powershell
# Test locally
python app.py

# Copy simple_api to app.py
Copy-Item simple_api.py app.py

# Open Space in browser
start https://huggingface.co/spaces/YOUR_USERNAME/leaseth-scoring-api

# Test live API
curl https://YOUR_USERNAME-leaseth-scoring-api.hf.space/health
```

---

## 🔗 USEFUL LINKS

- Your Spaces: https://huggingface.co/spaces
- HF Docs: https://huggingface.co/docs/hub/spaces
- Docker SDK Guide: https://huggingface.co/docs/hub/spaces-sdks-docker
- Community Forum: https://discuss.huggingface.co

---

**Your MVP is now live with ZERO hassle!** 🚀

**NO CARD + WORKS PERFECTLY + 5 MINUTES = Perfect Solution!** 🎉
