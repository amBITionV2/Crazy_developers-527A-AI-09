# RaktaKosh Connect - Vercel Deployment Guide

## 🚀 Frontend Deployment to Vercel

### Prerequisites
1. **GitHub Account** - Your code is already on GitHub
2. **Vercel Account** - Sign up at [vercel.com](https://vercel.com)
3. **Backend Deployment** - Deploy your backend first (see Backend section below)

### Step 1: Deploy Frontend to Vercel

#### Option A: GitHub Integration (Recommended)
1. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Sign up/Login with your GitHub account
   - Click "New Project"
   - Import your repository: `Santhosh121805/raktakosh-connect`

2. **Configure Build Settings:**
   - Framework Preset: `Vite`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

3. **Environment Variables:**
   Copy all variables from `.env.production` to Vercel:
   ```
   VITE_API_BASE_URL=https://your-backend-url.com/api/v1
   VITE_WS_BASE_URL=wss://your-backend-url.com/ws
   VITE_FIREBASE_API_KEY=AIzaSyBRDWkb1SNPy0Qa1uWJTLLxLfLYNPPE9hY
   VITE_FIREBASE_AUTH_DOMAIN=raktkosh-connect.firebaseapp.com
   ... (all other VITE_ variables)
   ```

4. **Deploy:**
   - Click "Deploy"
   - Vercel will automatically build and deploy your app
   - You'll get a URL like: `https://raktakosh-connect.vercel.app`

#### Option B: Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### Step 2: Deploy Backend (Required)

Since Vercel is primarily for frontend/serverless functions, you need to deploy your FastAPI backend elsewhere:

#### Option A: Railway (Recommended)
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Select the `bloodaid-backend` folder
4. Railway will auto-detect Python and deploy
5. Get your deployment URL: `https://your-app.railway.app`

#### Option B: Render
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repo
4. Root Directory: `bloodaid-backend`
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Option C: Heroku
```bash
# In bloodaid-backend directory
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile
git add Procfile
git commit -m "Add Procfile for Heroku"
heroku create your-app-name
git push heroku main
```

### Step 3: Update Frontend Configuration

Once your backend is deployed, update the environment variables in Vercel:

1. Go to your Vercel project dashboard
2. Go to Settings → Environment Variables
3. Update these variables:
   ```
   VITE_API_BASE_URL=https://your-actual-backend-url.com/api/v1
   VITE_WS_BASE_URL=wss://your-actual-backend-url.com/ws
   ```
4. Redeploy your frontend

### Step 4: Domain Configuration (Optional)

1. **Custom Domain:**
   - Go to Settings → Domains in Vercel
   - Add your custom domain
   - Configure DNS records

2. **SSL Certificate:**
   - Vercel automatically provides SSL certificates
   - Your app will be available at `https://your-domain.com`

## 🔧 Post-Deployment Configuration

### CORS Configuration
Make sure your backend allows requests from your Vercel domain:

```python
# In your FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://raktakosh-connect.vercel.app",
        "https://your-custom-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Database Configuration
- Ensure your database is accessible from your backend deployment
- Update connection strings for production

### Firebase Configuration
- Update Firebase project settings to allow your new domain
- Add your Vercel domain to authorized domains in Firebase Console

## 🧪 Testing Your Deployment

1. **Frontend:** Visit your Vercel URL
2. **Backend:** Test API endpoints: `https://your-backend-url.com/docs`
3. **Full Integration:** Test login, registration, and SOS features

## 🚨 Important Notes

1. **Environment Variables:** Never commit real API keys to GitHub
2. **HTTPS:** Always use HTTPS in production
3. **Rate Limiting:** Implement rate limiting for API endpoints
4. **Error Monitoring:** Set up error tracking (Sentry, LogRocket)
5. **Analytics:** Configure Google Analytics if needed

## 📞 Support

If you encounter issues:
1. Check Vercel build logs
2. Check backend deployment logs
3. Verify environment variables
4. Test API endpoints individually

## 🎉 Success!

Once deployed, your RaktaKosh Connect platform will be live with:
- ✅ Patient and Donor portals
- ✅ AI-powered chat assistant
- ✅ Emergency SOS system
- ✅ Real-time notifications
- ✅ Location-based donor matching
- ✅ eRaktkosh integration

Your app will be accessible worldwide at your Vercel URL!