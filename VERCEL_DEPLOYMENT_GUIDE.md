# Vercel Deployment Guide - Leaseth Frontend

## Overview
This guide will help you deploy your new React + Vite frontend to Vercel and connect it seamlessly with your Hugging Face backend.

## Prerequisites

- GitHub account
- Vercel account (free tier works fine) - sign up at https://vercel.com
- Your Hugging Face backend URL: `https://sreejithm-leaseth-mvp.hf.space`

---

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

#### 1.1 Create a `.gitignore` file (if not exists)
Create or update `frontend/.gitignore`:

```
# Dependencies
node_modules
.pnp
.pnp.js

# Testing
coverage

# Production
dist
build

# Misc
.DS_Store
*.pem

# Debug logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Local env files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Vercel
.vercel
```

#### 1.2 Create Environment Variable Template
Create `frontend/.env.example`:

```
VITE_API_URL=https://sreejithm-leaseth-mvp.hf.space
```

#### 1.3 Initialize Git Repository (if not already done)

```powershell
# In your project root
git init
git add .
git commit -m "Initial commit - Leaseth frontend"
```

#### 1.4 Push to GitHub

```powershell
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/leaseth-frontend.git
git branch -M main
git push -u origin main
```

---

### Step 2: Configure Vercel Project Settings

#### 2.1 Update `vercel.json` Configuration

Your `frontend/vercel.json` should look like this:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" },
        { 
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://sreejithm-leaseth-mvp.hf.space;"
        }
      ]
    }
  ],
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "installCommand": "npm install"
}
```

---

### Step 3: Deploy to Vercel

#### Option A: Deploy via Vercel Dashboard (Recommended for First Time)

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Click **"Add New..."** → **"Project"**

2. **Import Git Repository**
   - Click **"Import Git Repository"**
   - Select your GitHub repository: `leaseth-frontend`
   - Click **"Import"**

3. **Configure Project**
   - **Framework Preset**: Vite (should auto-detect)
   - **Root Directory**: Click **"Edit"** → Select `frontend`
   - **Build Command**: `npm run build` (should auto-fill)
   - **Output Directory**: `dist` (should auto-fill)
   - **Install Command**: `npm install` (should auto-fill)

4. **Add Environment Variables**
   - Click **"Environment Variables"**
   - Add the following:
     ```
     Name: VITE_API_URL
     Value: https://sreejithm-leaseth-mvp.hf.space
     ```
   - Select all environments: Production, Preview, Development

5. **Deploy**
   - Click **"Deploy"**
   - Wait 2-3 minutes for build to complete
   - You'll get a URL like: `https://leaseth-frontend-xyz.vercel.app`

#### Option B: Deploy via Vercel CLI

```powershell
# Install Vercel CLI globally
npm install -g vercel

# Navigate to frontend directory
cd frontend

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts:
# - Set up and deploy? Y
# - Which scope? Select your account
# - Link to existing project? N
# - Project name? leaseth-frontend
# - Directory? ./ (current directory)
# - Override settings? N

# Deploy to production
vercel --prod
```

---

### Step 4: Verify Deployment

#### 4.1 Test the Deployment

1. **Visit your Vercel URL** (e.g., `https://leaseth-frontend-xyz.vercel.app`)

2. **Test API Connection**
   - Open browser DevTools (F12)
   - Go to Console tab
   - The app should load without errors
   - Try submitting a test applicant

3. **Check Network Requests**
   - Go to Network tab
   - Submit an applicant
   - Verify request goes to: `https://sreejithm-leaseth-mvp.hf.space/api/score`
   - Should return 200 OK with scoring results

#### 4.2 Common Issues & Fixes

**Issue: "Could not reach server"**
- Check Hugging Face Space is awake (visit the Space URL)
- Verify `VITE_API_URL` environment variable is set correctly
- Check browser console for CORS errors

**Issue: "404 on page refresh"**
- Ensure `vercel.json` has the rewrites configuration (see Step 2.1)

**Issue: Build fails**
- Check build logs in Vercel dashboard
- Verify `package.json` scripts are correct
- Ensure all dependencies are in `package.json` (not just devDependencies)

---

### Step 5: Custom Domain (Optional)

1. **Add Custom Domain**
   - Go to Vercel project → Settings → Domains
   - Click **"Add"**
   - Enter your domain (e.g., `app.leaseth.com`)
   - Follow DNS configuration instructions

2. **Update Environment Variable (if needed)**
   - If you want different API URLs per environment:
     ```
     Production: VITE_API_URL=https://api.leaseth.com
     Preview: VITE_API_URL=https://staging-api.leaseth.com
     Development: VITE_API_URL=http://localhost:8000
     ```

---

### Step 6: Continuous Deployment

Once connected to GitHub, Vercel will automatically:
- **Deploy on every push to `main` branch** (Production)
- **Create preview deployments for PRs** (Preview)
- **Generate unique URLs for each deployment**

To trigger a deployment:
```powershell
git add .
git commit -m "Update frontend"
git push origin main
```

Vercel will automatically build and deploy within 2-3 minutes.

---

## Project Structure Reference

Your deployed frontend structure:
```
frontend/
├── dist/                    # Build output (auto-generated)
├── node_modules/            # Dependencies (gitignored)
├── public/                  # Static assets
├── src/
│   ├── components/          # React components
│   ├── hooks/               # Custom React hooks
│   ├── pages/               # Page components
│   ├── services/            # API service (api.ts)
│   ├── types/               # TypeScript types
│   ├── utils/               # Utilities
│   ├── App.tsx              # Root component
│   └── main.tsx             # Entry point
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
├── index.html               # HTML template
├── package.json             # Dependencies
├── postcss.config.js        # PostCSS config
├── tailwind.config.js       # Tailwind config
├── tsconfig.json            # TypeScript config
├── vercel.json              # Vercel config
└── vite.config.ts           # Vite config
```

---

## Environment Variables Explained

### VITE_API_URL
- **Purpose**: Backend API endpoint
- **Production Value**: `https://sreejithm-leaseth-mvp.hf.space`
- **Local Development**: `http://localhost:8000` (if running backend locally)
- **Used in**: `frontend/src/services/api.ts`

**Important**: 
- Vite requires env vars to start with `VITE_` to be exposed to client
- Changes require rebuild: `npm run build`
- In development, changes require restart: `npm run dev`

---

## Monitoring & Analytics

### Vercel Analytics (Optional)

1. **Enable Analytics**
   - Go to Vercel project → Analytics
   - Enable Web Analytics (free for hobby projects)
   - Add `<script>` tag if prompted

2. **Monitor Performance**
   - Track page views, load times
   - Monitor API success/failure rates
   - View geographic distribution

---

## Rollback & Versioning

### Rollback to Previous Deployment

1. Go to Vercel Dashboard → Your Project → Deployments
2. Find the working deployment
3. Click **"..."** → **"Promote to Production"**

### View Deployment Logs

1. Go to Vercel Dashboard → Your Project → Deployments
2. Click on any deployment
3. View build logs and runtime logs

---

## Security Best Practices

✅ **Already Implemented:**
- Security headers in `vercel.json`
- HTTPS enforced by default
- Environment variables encrypted at rest

🔒 **Additional Recommendations:**
- Don't commit `.env` files (already gitignored)
- Rotate API keys regularly (if you add authentication)
- Use Vercel's Environment Variable encryption
- Enable "Preview Deployment Protection" for private projects

---

## Cost Estimate

**Vercel Hobby Plan (Free):**
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Preview deployments
- ✅ Edge network (CDN)
- ✅ Sufficient for MVP and moderate traffic

**Upgrade to Pro ($20/month) when:**
- Traffic exceeds 100 GB/month
- Need password protection for previews
- Want advanced analytics
- Need team collaboration features

---

## Quick Commands Reference

```powershell
# Local development
cd frontend
npm install
npm run dev          # Start dev server (http://localhost:5173)

# Production build (test locally)
npm run build        # Build to dist/
npm run preview      # Preview production build

# Deploy to Vercel
vercel              # Deploy to preview
vercel --prod       # Deploy to production

# Check deployment status
vercel ls           # List deployments
vercel logs         # View logs
```

---

## Next Steps After Deployment

1. ✅ **Test thoroughly** - Submit multiple applicants
2. ✅ **Share the URL** - Get user feedback
3. ✅ **Monitor errors** - Check Vercel logs daily
4. ✅ **Set up custom domain** - Professional branding
5. ✅ **Enable analytics** - Track usage patterns
6. ✅ **Plan backend migration** - Consider moving from HuggingFace to dedicated hosting if traffic grows

---

## Support & Resources

- **Vercel Docs**: https://vercel.com/docs
- **Vite Docs**: https://vitejs.dev/
- **React Docs**: https://react.dev/
- **Vercel Community**: https://github.com/vercel/vercel/discussions

---

## Troubleshooting

### Build Fails with TypeScript Errors

```powershell
# Check for errors locally
cd frontend
npm run build

# Fix TypeScript errors, then redeploy
git add .
git commit -m "Fix TypeScript errors"
git push
```

### API Requests Fail (CORS)

Check Hugging Face backend CORS settings. Should allow:
```python
# In your FastAPI backend
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-url.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Hugging Face Space Sleeps

- Free HF Spaces sleep after inactivity
- First request may take 30-60 seconds to wake
- Consider upgrading to persistent Space or moving backend

---

**You're all set! 🚀**

Your frontend will be live at `https://your-project-name.vercel.app` within minutes of deployment.
