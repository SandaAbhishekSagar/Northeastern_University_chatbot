# 🎨 Vercel Frontend Deployment Guide

Complete guide to deploy your Northeastern University Chatbot frontend to Vercel.

---

## 📋 **Prerequisites**

1. ✅ Railway backend deployed and running
2. ✅ Railway API URL (e.g., `https://your-app.railway.app`)
3. ✅ Vercel account (free tier works great!)
4. ✅ Git repository with your code

---

## 🚀 **Quick Deploy (3 Steps)**

### **Step 1: Get Your Railway API URL**

1. Go to your Railway dashboard
2. Click on your deployed service
3. Go to "Settings" → "Domains"
4. Copy the public URL (e.g., `https://university-chatbot-production.up.railway.app`)

### **Step 2: Update `config.js`**

Open `frontend/config.js` and replace with your Railway URL:

```javascript
window.API_BASE_URL = "https://your-railway-url.railway.app";
```

**Example:**
```javascript
window.API_BASE_URL = "https://university-chatbot-production.up.railway.app";
```

### **Step 3: Deploy to Vercel**

#### **Option A: Deploy via Vercel Dashboard (Easiest)**

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New" → "Project"
3. Import your Git repository
4. Configure:
   - **Framework Preset:** Other
   - **Root Directory:** `frontend`
   - **Build Command:** (leave empty)
   - **Output Directory:** `.` (current directory)
5. Click "Deploy"

#### **Option B: Deploy via Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend directory
cd frontend

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: northeastern-chatbot-frontend
# - Directory: ./ (current)
# - Override settings? No

# For production deployment
vercel --prod
```

---

## 📁 **Files Created for Vercel**

### **1. `vercel.json`**
```json
{
  "version": 2,
  "name": "northeastern-chatbot-frontend",
  "builds": [
    {
      "src": "**/*",
      "use": "@vercel/static"
    }
  ]
}
```

**Purpose:** Tells Vercel to deploy as a static site.

### **2. `.vercelignore`**
```
server.py
test_*.html
README.md
```

**Purpose:** Excludes development files from deployment.

### **3. `config.production.js`**
Template for production API configuration.

---

## 🔧 **Configuration Details**

### **How API Connection Works:**

1. **`config.js`** sets `window.API_BASE_URL`
2. **`script.js`** reads this value:
   ```javascript
   if (window.API_BASE_URL && window.API_BASE_URL.trim().length > 0) {
       this.apiBaseUrl = window.API_BASE_URL.trim();
   }
   ```
3. **All API calls** use `this.apiBaseUrl`

### **CORS Configuration:**

Your Railway backend already has CORS enabled in `enhanced_openai_api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**This allows your Vercel frontend to communicate with Railway backend!**

---

## 🎯 **After Deployment**

### **Your URLs:**

- **Frontend (Vercel):** `https://your-project.vercel.app`
- **Backend (Railway):** `https://your-app.railway.app`

### **Test Your Deployment:**

1. Visit your Vercel URL
2. Open browser console (F12)
3. Check for API connection:
   ```
   Health response status: 200
   ✅ ChromaDB connected successfully
   ```
4. Ask a test question
5. Verify response appears

---

## 🐛 **Troubleshooting**

### **Issue 1: "Failed to fetch" or CORS Error**

**Symptoms:**
```
Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS
```

**Solution:**
1. Verify Railway backend is running
2. Check Railway logs for CORS middleware
3. Ensure Railway URL in `config.js` is correct (no trailing slash)

### **Issue 2: "API_BASE_URL is undefined"**

**Symptoms:**
```
Cannot read property 'trim' of undefined
```

**Solution:**
1. Ensure `config.js` is loaded BEFORE `script.js` in `index.html`:
   ```html
   <script src="config.js"></script>  <!-- First -->
   <script src="script.js"></script>  <!-- Second -->
   ```
2. Clear browser cache (Ctrl+Shift+R)

### **Issue 3: 404 on API Endpoints**

**Symptoms:**
```
GET https://your-app.railway.app/health/enhanced 404
```

**Solution:**
1. Verify Railway deployment is successful
2. Check Railway logs for startup messages
3. Test API directly: `curl https://your-app.railway.app/health/enhanced`

### **Issue 4: Slow Response Times**

**Symptoms:**
- Queries take 30+ seconds
- Timeout errors

**Solution:**
1. Check Railway logs for OpenAI API timeouts
2. Verify `OPENAI_API_KEY` is set in Railway environment variables
3. Check ChromaDB Cloud connection

---

## 🔄 **Updating Your Deployment**

### **Update Frontend:**

```bash
cd frontend

# Make your changes to HTML/CSS/JS

# Commit changes
git add .
git commit -m "Update frontend"
git push origin main

# Vercel auto-deploys on push!
```

### **Update API URL:**

If your Railway URL changes:

1. Update `frontend/config.js`
2. Commit and push
3. Vercel will redeploy automatically

---

## 📊 **Vercel Dashboard**

After deployment, you can:

- **View deployment logs**
- **See analytics** (page views, performance)
- **Configure custom domain** (e.g., `chatbot.yourdomain.com`)
- **Set environment variables** (if needed)
- **Enable preview deployments** (for branches)

---

## 🎨 **Custom Domain (Optional)**

### **Add Your Own Domain:**

1. Go to Vercel project settings
2. Click "Domains"
3. Add your domain (e.g., `chatbot.northeastern.edu`)
4. Follow DNS configuration instructions
5. Vercel automatically provisions SSL certificate

---

## 💰 **Cost Breakdown**

### **Vercel Free Tier:**
- ✅ **Bandwidth:** 100GB/month
- ✅ **Deployments:** Unlimited
- ✅ **SSL:** Free
- ✅ **Custom domains:** Unlimited
- ✅ **Preview deployments:** Unlimited

**Perfect for your chatbot! No cost expected.**

---

## 🔒 **Security Best Practices**

### **1. Environment Variables**

If you need to store sensitive data in frontend:

```bash
# In Vercel dashboard → Settings → Environment Variables
NEXT_PUBLIC_API_KEY=your_key_here
```

**Note:** Frontend env vars are PUBLIC. Never store secrets here!

### **2. API Key Protection**

Your OpenAI API key is safe because:
- ✅ It's stored in Railway (backend only)
- ✅ Frontend never sees it
- ✅ Users can't access it

### **3. Rate Limiting**

Consider adding rate limiting to your Railway backend:

```python
# In enhanced_openai_api.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat/enhanced")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def chat(request: ChatRequest):
    ...
```

---

## 🎉 **Success Checklist**

After deployment, verify:

- [ ] Frontend loads on Vercel URL
- [ ] API connection shows "healthy" status
- [ ] Document count displays correctly
- [ ] Test query returns response
- [ ] Markdown rendering works
- [ ] Stats modal displays data
- [ ] Clear chat button works
- [ ] Mobile responsive design works

---

## 📞 **Support Resources**

- **Vercel Docs:** https://vercel.com/docs
- **Vercel Discord:** https://vercel.com/discord
- **Railway Docs:** https://docs.railway.app

---

## 🚀 **You're All Set!**

Your architecture:

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         │ HTTPS
         ▼
┌─────────────────┐
│  Vercel Frontend│  ← Static HTML/CSS/JS
│  (Free Tier)    │
└────────┬────────┘
         │
         │ API Calls
         ▼
┌─────────────────┐
│ Railway Backend │  ← FastAPI + OpenAI
│  (Paid Tier)    │
└────────┬────────┘
         │
         │ Vector Search
         ▼
┌─────────────────┐
│ ChromaDB Cloud  │  ← 80,000 documents
│  (Paid Tier)    │
└─────────────────┘
```

**Fast, scalable, and production-ready! 🎉**

