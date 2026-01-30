# ✅ Vercel Deployment - Complete Checklist

## 📋 Pre-Deployment Checklist

- [x] Frontend built with React + Vite + TypeScript
- [x] Backend running on Hugging Face: `https://sreejithm-leaseth-mvp.hf.space`
- [x] `vercel.json` configured with build settings
- [x] `.env.example` created for environment variables
- [x] `.gitignore` updated to exclude `node_modules`, `dist`, `.vercel`
- [x] Security headers configured in `vercel.json`
- [x] API service configured in `frontend/src/services/api.ts`

## 🚀 Deployment Methods

### Method 1: Vercel CLI (Fastest - 2 minutes)

```powershell
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd frontend

# Login
vercel login

# Deploy to production
vercel --prod

# Set environment variable
vercel env add VITE_API_URL
# Enter: https://sreejithm-leaseth-mvp.hf.space
# Select: All environments

# Redeploy with env var
vercel --prod
```

### Method 2: GitHub + Vercel (Recommended for continuous deployment)

```powershell
# Step 1: Push to GitHub
git init
git add .
git commit -m "Deploy Leaseth frontend to Vercel"
git remote add origin https://github.com/YOUR_USERNAME/leaseth-frontend.git
git branch -M main
git push -u origin main

# Step 2: Import to Vercel
# 1. Visit https://vercel.com/new
# 2. Import your GitHub repository
# 3. Configure:
#    - Root Directory: frontend
#    - Build Command: npm run build
#    - Output Directory: dist
#    - Framework: Vite
# 4. Add Environment Variable:
#    - VITE_API_URL = https://sreejithm-leaseth-mvp.hf.space
# 5. Deploy

# Step 3: Auto-deploy on every push
git add .
git commit -m "Update"
git push  # Auto-deploys to Vercel
```

## 🔧 Configuration Files

### ✅ vercel.json
Location: `frontend/vercel.json`
- ✅ Rewrites for SPA routing
- ✅ Security headers
- ✅ Build configuration
- ✅ CSP with HuggingFace backend allowed

### ✅ .env.example
Location: `frontend/.env.example`
- ✅ Template for environment variables
- ✅ Documents VITE_API_URL usage

### ✅ .gitignore
Locations: Root and `frontend/.gitignore`
- ✅ Excludes `node_modules`
- ✅ Excludes `dist` build folder
- ✅ Excludes `.env` files
- ✅ Excludes `.vercel` folder

## 🌐 Environment Variables

### Required Variable

**VITE_API_URL**
- **Description**: Backend API endpoint
- **Production Value**: `https://sreejithm-leaseth-mvp.hf.space`
- **Local Dev Value**: `http://localhost:8000` (if running backend locally)
- **Where to set in Vercel**: 
  - Dashboard → Your Project → Settings → Environment Variables
  - OR via CLI: `vercel env add VITE_API_URL`

### How Environment Variables Work

1. **In Code**: Used in `frontend/src/services/api.ts`
   ```typescript
   const API_URL = import.meta.env.VITE_API_URL || 'https://sreejithm-leaseth-mvp.hf.space'
   ```

2. **During Build**: Vite replaces `import.meta.env.VITE_API_URL` with actual value
3. **At Runtime**: Value is embedded in built JavaScript (not fetched dynamically)

**Important**: Changes to env vars require a rebuild/redeploy!

## 📊 Post-Deployment Testing

### ✅ Test Checklist

1. **Homepage Loads**
   - Visit your Vercel URL
   - Landing page displays correctly
   - No console errors (F12)

2. **Navigation Works**
   - Click "Get Started"
   - Navigate to Dashboard
   - URL changes without page reload (SPA routing)

3. **API Connection**
   - Fill out scoring form
   - Submit test applicant
   - Network tab shows request to HuggingFace backend
   - Results display correctly

4. **Dashboard Features**
   - View previous assessments (local storage)
   - Charts render
   - Export/download works

5. **Mobile Responsive**
   - Test on mobile device or DevTools mobile view
   - Layout adjusts properly

### Test Applicant Data

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "employment_status": "employed",
  "monthly_income": 5000,
  "credit_score": 720,
  "monthly_rent": 1500,
  "previous_evictions": 0,
  "rental_history_years": 5,
  "lease_term_months": 12,
  "employment_verified": true,
  "income_verified": true,
  "on_time_payments_percent": 95
}
```

Expected Result:
- Risk Score: ~25-35 (LOW)
- Recommendation: APPROVE
- Confidence: High

## 🔍 Troubleshooting Guide

### Issue: Build Fails

**Symptoms**: Deployment shows "Build Failed"

**Solutions**:
```powershell
# Test build locally first
cd frontend
npm install
npm run build

# Check for errors
# Fix TypeScript/lint errors
npm run lint

# Push fix
git add .
git commit -m "Fix build errors"
git push
```

### Issue: API Requests Fail (CORS)

**Symptoms**: Console shows "CORS policy blocked"

**Solution**: Check HuggingFace Space CORS settings
```python
# Backend needs:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-url.vercel.app", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: 404 on Page Refresh

**Symptoms**: Refreshing `/dashboard` shows 404

**Solution**: Verify `vercel.json` has rewrites:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

### Issue: Environment Variable Not Working

**Symptoms**: API calls go to wrong URL

**Solution**:
```powershell
# Check env var is set
vercel env ls

# Add if missing
vercel env add VITE_API_URL

# MUST redeploy after adding env var
vercel --prod
```

### Issue: HuggingFace Backend Slow/Timeout

**Symptoms**: First request takes 30-60 seconds

**Reason**: Free HF Spaces sleep after inactivity

**Solutions**:
1. Wait for space to wake up (automatic)
2. Keep space awake with periodic pings
3. Upgrade to persistent HF Space
4. Migrate backend to always-on hosting (Render, Railway, etc.)

## 📱 Your Deployment URL Structure

After deployment, you'll get:

- **Production URL**: `https://leaseth-frontend-xyz123.vercel.app`
- **Preview URLs** (if using GitHub): Unique URL per branch/PR
- **Custom Domain** (optional): `https://app.leaseth.com`

## 🔄 Continuous Deployment Workflow

### Automatic Deployments (GitHub Method)

```
Local Changes → Git Push → GitHub → Vercel Auto-Deploy → Live in 2-3 min
```

**Branches**:
- `main` branch → Production deployment
- Other branches → Preview deployments (unique URLs)
- Pull requests → Preview deployments (with comments)

### Manual Deployments (CLI Method)

```powershell
# Preview deployment
cd frontend
vercel

# Production deployment
vercel --prod

# Rollback to previous version
vercel rollback
```

## 📈 Monitoring & Analytics

### Vercel Analytics (Free)

1. Enable in Vercel dashboard
2. Track:
   - Page views
   - Performance metrics
   - Geographic distribution
   - Real user monitoring

### Browser Console Monitoring

Monitor for errors:
```javascript
// Open DevTools (F12) → Console
// Look for:
// ✅ No red errors
// ✅ API requests succeed (200 OK)
// ✅ No CORS warnings
```

## 🔒 Security Checklist

- [x] HTTPS enforced (automatic with Vercel)
- [x] Security headers configured (`X-Frame-Options`, `X-Content-Type-Options`, etc.)
- [x] Content Security Policy (CSP) set
- [x] Environment variables encrypted at rest
- [x] `.env` files gitignored (never committed)
- [x] API URL configurable via environment variable

## 💰 Cost & Limits

### Vercel Hobby (Free Tier)
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ 100 GB-hrs build time/month
- ✅ Serverless function executions: 100,000/month
- ✅ Custom domains: 100
- ✅ Preview deployments: Unlimited

**Sufficient for:**
- MVP testing
- Small to medium traffic
- Personal projects
- ~10,000-50,000 page views/month

### When to Upgrade to Pro ($20/month)
- Traffic exceeds 100 GB/month
- Need password-protected previews
- Team collaboration required
- Advanced analytics needed

## 🎯 Next Steps After Deployment

1. **Test thoroughly** ✅
   - Submit multiple test applicants
   - Test on different devices/browsers
   - Verify all features work

2. **Share and gather feedback** 📢
   - Share URL with stakeholders
   - Collect user feedback
   - Monitor for errors

3. **Set up custom domain** 🌐
   - Purchase domain (e.g., Namecheap, GoDaddy)
   - Configure DNS in Vercel
   - Professional branding

4. **Enable analytics** 📊
   - Vercel Analytics (free)
   - Google Analytics (optional)
   - Track usage patterns

5. **Plan backend scaling** 🚀
   - Monitor HuggingFace Space uptime
   - Consider dedicated backend hosting
   - Options: Render, Railway, Fly.io, AWS

6. **Implement monitoring** 🔔
   - Set up error alerts
   - Monitor API success rates
   - Track performance metrics

## 📚 Documentation Links

- **This Project**:
  - [Full Deployment Guide](VERCEL_DEPLOYMENT_GUIDE.md)
  - [Quick Start](QUICKSTART_VERCEL.md)
  
- **External Resources**:
  - [Vercel Docs](https://vercel.com/docs)
  - [Vite Docs](https://vitejs.dev/)
  - [React Router](https://reactrouter.com/)

## 🆘 Support

**Issues?** Check:
1. Build logs in Vercel dashboard
2. Browser console (F12)
3. Network tab for failed requests
4. Vercel deployment logs

**Common Commands**:
```powershell
vercel --help          # Show all commands
vercel logs            # View deployment logs
vercel ls              # List deployments
vercel env ls          # List environment variables
vercel domains ls      # List domains
vercel --version       # Check CLI version
```

---

## ✨ You're Ready to Deploy!

Choose your method:
- **Quick & Simple**: Use [QUICKSTART_VERCEL.md](QUICKSTART_VERCEL.md)
- **Detailed Guide**: Use [VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md)

**Estimated time**: 5-10 minutes to live deployment! 🚀
