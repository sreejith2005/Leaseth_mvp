# Deploy Lovable Dashboard to GitHub Pages

**Complete guide for hosting your dashboard on GitHub Pages (FREE)**

---

## 🎯 PREREQUISITES

- ✅ Lovable code exported to a GitHub repository
- ✅ Node.js installed (check: `node --version`)
- ✅ Git installed and configured

---

## 📋 STEP-BY-STEP DEPLOYMENT

### **STEP 1: Locate Your Lovable Export**

Your Lovable dashboard should be in a separate GitHub repository from your API.

**Example structure**:
```
GitHub Repos:
├── Leaseth_mvp (API - already deployed on Render)
└── leaseth-dashboard (Frontend - to deploy on GitHub Pages)
```

```powershell
# Clone your Lovable export repo (if not local)
git clone https://github.com/sreejith2005/leaseth-dashboard.git
cd leaseth-dashboard

# Or navigate to existing folder
cd path/to/leaseth-dashboard
```

---

### **STEP 2: Install Dependencies**

```powershell
# Install project dependencies
npm install

# Install gh-pages package (for deployment)
npm install --save-dev gh-pages
```

---

### **STEP 3: Configure package.json**

Open `package.json` and add/modify these fields:

#### **Add homepage URL**:
```json
{
  "name": "leaseth-dashboard",
  "version": "1.0.0",
  "homepage": "https://sreejith2005.github.io/leaseth-dashboard",
  ...
}
```

**Replace**:
- `sreejith2005` with your GitHub username
- `leaseth-dashboard` with your repository name

#### **Add deploy scripts**:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "predeploy": "npm run build",
    "deploy": "gh-pages -d dist"
  }
}
```

**Note**: 
- If using Next.js, change `dist` to `out` or `build`
- If using Create React App, change to `build`
- Most Lovable exports use **Vite**, so `dist` is correct

---

### **STEP 4: Configure API URL**

#### **Option A: Environment Variable (Recommended)**

Create `.env.production` file in project root:
```env
VITE_API_URL=https://leaseth-mvp.onrender.com
```

Then update your API client to use it:
```javascript
// src/lib/api.js or src/api/client.js
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

export async function scoreApplicant(data) {
  const response = await fetch(`${API_URL}/api/score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
}
```

#### **Option B: Direct in Code**

Find your API client file (usually `src/lib/api.js` or similar) and update:
```javascript
// Before
const API_URL = 'http://localhost:8001';

// After
const API_URL = import.meta.env.MODE === 'production' 
  ? 'https://leaseth-mvp.onrender.com'
  : 'http://localhost:8001';
```

---

### **STEP 5: Configure Base Path for GitHub Pages**

Create/edit `vite.config.js` (or `vite.config.ts`):

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/leaseth-dashboard/', // Must match your repo name
})
```

**Important**: The `base` must be `/your-repo-name/`

If using **Next.js**, edit `next.config.js`:
```javascript
module.exports = {
  basePath: '/leaseth-dashboard',
  assetPrefix: '/leaseth-dashboard/',
  output: 'export',
}
```

---

### **STEP 6: Test Build Locally**

```powershell
# Build the project
npm run build

# Preview the build
npm run preview
```

Open http://localhost:4173 (or shown URL) and verify:
- ✅ Dashboard loads correctly
- ✅ API calls work (to Render)
- ✅ No console errors

---

### **STEP 7: Deploy to GitHub Pages**

```powershell
# Deploy!
npm run deploy
```

**What happens**:
1. Runs `npm run build` (creates production build)
2. Creates/updates `gh-pages` branch
3. Pushes build files to GitHub
4. GitHub Pages auto-publishes

**Expected output**:
```
> leaseth-dashboard@1.0.0 predeploy
> npm run build

> leaseth-dashboard@1.0.0 build
> vite build

✓ built in 3.45s

> leaseth-dashboard@1.0.0 deploy
> gh-pages -d dist

Published
```

---

### **STEP 8: Enable GitHub Pages (First time only)**

1. Go to GitHub repo: `https://github.com/sreejith2005/leaseth-dashboard`
2. Click **Settings** tab
3. Scroll to **Pages** section (left sidebar)
4. Under **Source**:
   - Branch: `gh-pages`
   - Folder: `/ (root)`
5. Click **Save**
6. Wait 1-2 minutes

**Your live URL**:
```
https://sreejith2005.github.io/leaseth-dashboard/
```

---

### **STEP 9: Update API CORS Settings**

Your API needs to allow requests from GitHub Pages domain.

Edit `simple_api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all (for testing)
        # Or be specific:
        "https://sreejith2005.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Commit and redeploy API on Render**:
```powershell
cd C:\Users\LENOVO\Downloads\leaseth_mvp_working_backup_3
git add simple_api.py
git commit -m "Update CORS for GitHub Pages"
git push origin new_stratergies
```

Wait for Render to redeploy (~2 minutes).

---

### **STEP 10: Verify Deployment**

Open your GitHub Pages URL:
```
https://sreejith2005.github.io/leaseth-dashboard/
```

**Test**:
- ✅ Dashboard loads
- ✅ Fill in applicant form
- ✅ Submit scoring request
- ✅ See results from API
- ✅ No CORS errors in console (F12)

---

## 🔄 UPDATING YOUR DASHBOARD

### **Method 1: Make changes and redeploy**

```powershell
# Make code changes
# Test locally
npm run dev

# Build and deploy
npm run deploy
```

**That's it!** Changes go live in ~1 minute.

### **Method 2: From Lovable**

If you keep editing in Lovable:

```powershell
# 1. Export from Lovable → Download ZIP
# 2. Extract and copy files to your local repo
# 3. Commit changes
git add .
git commit -m "Updated from Lovable"
git push origin main

# 4. Deploy
npm run deploy
```

---

## ⚙️ CONFIGURATION SUMMARY

### **package.json** (key parts):
```json
{
  "homepage": "https://sreejith2005.github.io/leaseth-dashboard",
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d dist"
  },
  "devDependencies": {
    "gh-pages": "^6.1.0"
  }
}
```

### **vite.config.js**:
```javascript
export default defineConfig({
  base: '/leaseth-dashboard/',
})
```

### **.env.production**:
```env
VITE_API_URL=https://leaseth-mvp.onrender.com
```

---

## 🚨 TROUBLESHOOTING

### **Issue: Blank page after deployment**
**Solution**: Check `base` in `vite.config.js` matches your repo name exactly

### **Issue: 404 on page refresh**
**Solution**: GitHub Pages doesn't support SPA routing. Add `404.html` that redirects:
```html
<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="refresh" content="0;url=/">
</head>
</html>
```

Or use hash router in React:
```javascript
import { HashRouter } from 'react-router-dom';
// Use HashRouter instead of BrowserRouter
```

### **Issue: CORS error**
**Solution**: 
1. Check API CORS settings in `simple_api.py`
2. Verify API is deployed and running on Render
3. Check browser console for exact error

### **Issue: API calls fail**
**Solution**:
1. Check `.env.production` has correct API URL
2. Verify API URL in code uses environment variable
3. Test API directly: `https://leaseth-mvp.onrender.com/health`

### **Issue: CSS/Images not loading**
**Solution**: Ensure `base` in vite.config.js is set correctly

---

## 📊 COMPLETE ARCHITECTURE

```
Frontend (Lovable Dashboard):
├── Hosted: GitHub Pages
├── URL: https://sreejith2005.github.io/leaseth-dashboard/
├── Cost: FREE (unlimited)
├── Deploy: npm run deploy
└── Updates: Push to gh-pages branch

Backend (Scoring API):
├── Hosted: Render
├── URL: https://leaseth-mvp.onrender.com
├── Cost: FREE (with sleep)
├── Deploy: git push → auto-redeploy
└── CORS: Allows GitHub Pages domain
```

---

## ✅ DEPLOYMENT CHECKLIST

**Initial Setup**:
- [ ] Clone/navigate to Lovable export repo
- [ ] Install dependencies: `npm install`
- [ ] Install gh-pages: `npm install --save-dev gh-pages`
- [ ] Add `homepage` to package.json
- [ ] Add `deploy` scripts to package.json
- [ ] Set `base` in vite.config.js
- [ ] Configure API URL in .env.production
- [ ] Test build: `npm run build && npm run preview`
- [ ] Deploy: `npm run deploy`
- [ ] Enable GitHub Pages in repo settings
- [ ] Update API CORS settings
- [ ] Test live URL

**Every Update**:
- [ ] Make changes locally or export from Lovable
- [ ] Test: `npm run dev`
- [ ] Deploy: `npm run deploy`
- [ ] Verify: Check live URL

---

## 🎉 SUCCESS!

Your dashboard is now live at:
```
https://sreejith2005.github.io/leaseth-dashboard/
```

**Benefits**:
- ✅ 100% FREE hosting
- ✅ Automatic HTTPS
- ✅ Fast CDN delivery
- ✅ Easy updates (one command)
- ✅ No server maintenance
- ✅ Unlimited traffic
- ✅ Version control via git

---

## 📝 QUICK COMMANDS REFERENCE

```powershell
# First time setup
npm install
npm install --save-dev gh-pages
npm run deploy

# Every update
npm run deploy

# Test locally
npm run dev          # Development
npm run build        # Production build
npm run preview      # Preview production build

# Deploy
npm run deploy       # Build + Deploy to GitHub Pages
```

---

**Your complete MVP is now live with ZERO hosting costs!** 🚀
