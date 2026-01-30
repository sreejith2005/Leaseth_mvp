# Quick Start - Vercel Deployment

## 🚀 Fast Track Deployment (5 Minutes)

### Step 1: Install Vercel CLI
```powershell
npm install -g vercel
```

### Step 2: Navigate to Frontend
```powershell
cd frontend
```

### Step 3: Login to Vercel
```powershell
vercel login
```
Follow the browser prompt to authenticate.

### Step 4: Deploy
```powershell
vercel --prod
```

Answer the prompts:
- **Set up and deploy?** → `Y`
- **Which scope?** → Select your account
- **Link to existing project?** → `N`
- **Project name?** → `leaseth-frontend` (or your preferred name)
- **In which directory is your code located?** → `./`
- **Want to override settings?** → `N`

### Step 5: Set Environment Variable

After deployment, set the backend URL:

```powershell
vercel env add VITE_API_URL
```

When prompted:
- **Value:** `https://sreejithm-leaseth-mvp.hf.space`
- **Environments:** Select all (Production, Preview, Development)

### Step 6: Redeploy with Environment Variable

```powershell
vercel --prod
```

**Done!** Your app is now live at the URL shown in the terminal.

---

## 🌐 Alternative: Deploy via GitHub (Recommended)

### Step 1: Push to GitHub

```powershell
# In project root
git init
git add .
git commit -m "Deploy Leaseth frontend"

# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/leaseth-frontend.git
git branch -M main
git push -u origin main
```

### Step 2: Import to Vercel

1. Visit https://vercel.com/new
2. Click **"Import Git Repository"**
3. Select your `leaseth-frontend` repository
4. **Configure:**
   - Root Directory: `frontend`
   - Framework: Vite (auto-detected)
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. **Add Environment Variable:**
   - Name: `VITE_API_URL`
   - Value: `https://sreejithm-leaseth-mvp.hf.space`
6. Click **"Deploy"**

**Automatic deployments enabled!** Every push to `main` will redeploy.

---

## ✅ Verify Deployment

Visit your Vercel URL and test:

1. **Homepage loads** - Should see Leaseth landing page
2. **Navigation works** - Click "Get Started" → Scoring form
3. **API connection** - Submit a test applicant:
   ```
   Name: John Doe
   Age: 30
   Employment: employed
   Monthly Income: 5000
   Credit Score: 720
   Monthly Rent: 1500
   ```
4. **Results display** - Should see risk score and recommendation

---

## 📱 Share Your App

Your public URL will be:
```
https://leaseth-frontend-[random].vercel.app
```

You can also set up a custom domain in Vercel settings.

---

## 🔧 Update Your App

```powershell
# Make changes to your code
git add .
git commit -m "Update feature"
git push

# Vercel auto-deploys within 2 minutes
```

---

## 🆘 Troubleshooting

**Build fails?**
```powershell
cd frontend
npm install
npm run build
# Fix any errors, then push again
```

**API not connecting?**
- Check Hugging Face Space is awake: https://sreejithm-leaseth-mvp.hf.space/health
- Verify environment variable is set in Vercel dashboard
- Check browser console (F12) for CORS errors

**Page refresh shows 404?**
- Ensure `vercel.json` exists with rewrites configuration (already set)

---

**Need help?** See the full guide: [VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md)
