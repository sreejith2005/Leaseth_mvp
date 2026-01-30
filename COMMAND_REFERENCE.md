# 🚀 Vercel Deployment - Command Reference

## Quick Deploy (2 Minutes)

```powershell
# 1. Navigate to frontend
cd frontend

# 2. Install Vercel CLI
npm install -g vercel

# 3. Login to Vercel
vercel login

# 4. Deploy to production
vercel --prod

# 5. Set environment variable
vercel env add VITE_API_URL
# Enter: https://sreejithm-leaseth-mvp.hf.space
# Select: Production, Preview, Development (all)

# 6. Redeploy with environment variable
vercel --prod
```

**Done!** Your app is live at the URL shown.

---

## GitHub Auto-Deploy (Recommended)

```powershell
# 1. Initialize git (if not already)
git init
git add .
git commit -m "Deploy Leaseth frontend"

# 2. Create GitHub repo at: https://github.com/new
# Name: leaseth-frontend

# 3. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/leaseth-frontend.git
git branch -M main
git push -u origin main

# 4. Import to Vercel
# Visit: https://vercel.com/new
# - Import your GitHub repository
# - Root Directory: frontend
# - Framework: Vite (auto-detected)
# - Add Environment Variable:
#   VITE_API_URL = https://sreejithm-leaseth-mvp.hf.space
# - Click Deploy

# 5. Future updates (auto-deploy)
git add .
git commit -m "Update"
git push
# Vercel auto-deploys in 2-3 minutes
```

---

## Essential Commands

### Local Development
```powershell
cd frontend
npm install              # Install dependencies
npm run dev              # Start dev server (port 5173)
npm run build            # Build for production
npm run preview          # Preview production build
npm run lint             # Check for errors
```

### Vercel CLI
```powershell
vercel                   # Deploy to preview
vercel --prod            # Deploy to production
vercel ls                # List all deployments
vercel logs              # View deployment logs
vercel env ls            # List environment variables
vercel env add           # Add environment variable
vercel env rm            # Remove environment variable
vercel domains ls        # List domains
vercel rollback          # Rollback to previous deployment
vercel --help            # Show all commands
```

### Git Workflow
```powershell
git status               # Check changes
git add .                # Stage all changes
git commit -m "message"  # Commit changes
git push                 # Push to GitHub (triggers auto-deploy)
git pull                 # Pull latest changes
git log --oneline        # View commit history
```

---

## Environment Variables

### Required
```bash
VITE_API_URL=https://sreejithm-leaseth-mvp.hf.space
```

### Set in Vercel Dashboard
1. Go to: Project → Settings → Environment Variables
2. Click "Add New"
3. Name: `VITE_API_URL`
4. Value: `https://sreejithm-leaseth-mvp.hf.space`
5. Select: All environments (Production, Preview, Development)
6. Click "Save"
7. **Redeploy** (changes require rebuild)

### Set via CLI
```powershell
vercel env add VITE_API_URL
# Enter value when prompted
# Select environments

# View all env vars
vercel env ls

# Remove env var
vercel env rm VITE_API_URL
```

---

## Test Checklist

### ✅ After Deployment

1. **Visit URL** - Homepage loads
2. **Navigation** - Click "Get Started"
3. **Submit Form** - Test applicant:
   ```
   Name: John Doe
   Age: 30
   Employment: employed
   Income: 5000
   Credit Score: 720
   Rent: 1500
   ```
4. **View Results** - Risk score displays
5. **Dashboard** - Previous assessments show
6. **Mobile** - Test responsive design
7. **Console** - No errors (F12)

---

## Troubleshooting

### Build Fails
```powershell
# Test locally first
cd frontend
npm install
npm run build
# Fix any errors, then redeploy
```

### API Not Working
- Check HuggingFace Space is awake: https://sreejithm-leaseth-mvp.hf.space/health
- Verify env var: `vercel env ls`
- Check browser console (F12) for errors

### 404 on Refresh
- Ensure `vercel.json` exists with rewrites config
- Already configured ✅

### Environment Variable Changes Not Applied
```powershell
# MUST redeploy after env var changes
vercel --prod
```

---

## URLs

### Your Deployed App
- Production: `https://your-project-name.vercel.app`
- Check in Vercel dashboard or terminal output

### Backend API
- HuggingFace: `https://sreejithm-leaseth-mvp.hf.space`
- Health check: `https://sreejithm-leaseth-mvp.hf.space/health`
- API endpoint: `https://sreejithm-leaseth-mvp.hf.space/api/score`

### Vercel Dashboard
- Projects: https://vercel.com/dashboard
- Deployments: https://vercel.com/[your-username]/[project-name]/deployments
- Settings: https://vercel.com/[your-username]/[project-name]/settings

---

## Files Created

- ✅ `VERCEL_DEPLOYMENT_GUIDE.md` - Full deployment guide
- ✅ `QUICKSTART_VERCEL.md` - Quick start (5 min)
- ✅ `DEPLOYMENT_CHECKLIST.md` - Pre-deployment checklist
- ✅ `MIGRATION_GUIDE.md` - LOVABLE → React migration
- ✅ `COMMAND_REFERENCE.md` - This file
- ✅ `frontend/.env.example` - Environment template
- ✅ `frontend/vercel.json` - Vercel config (updated)

---

## Support

**Documentation:**
- [Full Guide](VERCEL_DEPLOYMENT_GUIDE.md)
- [Quick Start](QUICKSTART_VERCEL.md)
- [Checklist](DEPLOYMENT_CHECKLIST.md)
- [Migration](MIGRATION_GUIDE.md)

**External:**
- Vercel Docs: https://vercel.com/docs
- Vite Docs: https://vitejs.dev/
- React Docs: https://react.dev/

---

**Ready to deploy!** Start with [QUICKSTART_VERCEL.md](QUICKSTART_VERCEL.md) 🚀
