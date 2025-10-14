# ⚡ Quick Vercel Deployment (2 Minutes)

## 🎯 **3 Simple Steps**

### **Step 1: Get Railway URL**

Go to Railway dashboard → Your service → Settings → Domains

Copy your URL (looks like: `https://xxx.railway.app`)

---

### **Step 2: Update config.js**

Open `frontend/config.js` and replace:

```javascript
window.API_BASE_URL = "https://YOUR_RAILWAY_URL.railway.app";
```

**Example:**
```javascript
window.API_BASE_URL = "https://university-chatbot-production.up.railway.app";
```

Save the file.

---

### **Step 3: Deploy to Vercel**

#### **Via Vercel Website (Easiest):**

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click "Import Git Repository"
3. Select your repository
4. **Important Settings:**
   - **Root Directory:** `frontend`
   - **Framework Preset:** Other
   - **Build Command:** (leave empty)
   - **Output Directory:** `.`
5. Click "Deploy"

**Done! Your frontend is live in ~30 seconds!** 🎉

---

#### **Via Vercel CLI (Alternative):**

```bash
# Install Vercel CLI (one-time)
npm install -g vercel

# Navigate to frontend folder
cd frontend

# Deploy
vercel --prod

# Follow prompts, accept defaults
```

---

## ✅ **Verify Deployment**

1. Visit your Vercel URL (shown after deployment)
2. Open browser console (F12)
3. Look for:
   ```
   Health response status: 200
   ✅ ChromaDB connected successfully - X documents available
   ```
4. Ask a test question
5. **Success!** 🚀

---

## 🔗 **Your Live URLs**

- **Frontend:** `https://your-project.vercel.app`
- **Backend:** `https://your-app.railway.app`

---

## 🐛 **If Something Goes Wrong**

### **CORS Error?**
- Check Railway is running: `curl https://your-app.railway.app/health/enhanced`
- Verify URL in `config.js` has no trailing slash

### **404 Error?**
- Verify Railway deployment succeeded
- Check Railway logs for errors

### **Slow/Timeout?**
- Check Railway environment variables (OPENAI_API_KEY, etc.)
- View Railway logs for OpenAI API errors

---

## 🎉 **That's It!**

**Your chatbot is now live and accessible worldwide!**

Share your Vercel URL with anyone to try it out! 🌍

