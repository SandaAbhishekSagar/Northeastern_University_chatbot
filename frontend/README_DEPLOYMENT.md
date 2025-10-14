# 🎨 Frontend Deployment - Vercel

Quick guide to deploy this frontend to Vercel.

---

## ⚡ **Quick Deploy (2 Minutes)**

### **Step 1: Get Your Railway API URL**

From Railway dashboard → Your service → Settings → Domains

Example: `https://university-chatbot-production.up.railway.app`

### **Step 2: Update config.js**

```javascript
window.API_BASE_URL = "https://your-railway-url.railway.app";
```

### **Step 3: Deploy to Vercel**

**Via Website (Easiest):**
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. **Root Directory:** `frontend`
4. **Framework:** Other
5. Click "Deploy"

**Via CLI:**
```bash
npm install -g vercel
cd frontend
vercel --prod
```

---

## 📁 **What Gets Deployed**

- ✅ `index.html` - Main chat interface
- ✅ `script.js` - Chat functionality
- ✅ `styles.css` - Beautiful UI
- ✅ `config.js` - API configuration
- ✅ `vercel.json` - Vercel settings

**Not deployed:**
- ❌ `server.py` (development only)
- ❌ `test_*.html` (testing files)
- ❌ `README.md` (documentation)

---

## ✅ **Verify Deployment**

1. Visit your Vercel URL
2. Open console (F12)
3. Look for:
   ```
   Health response status: 200
   ✅ ChromaDB connected successfully
   ```
4. Ask a test question
5. **Success!** 🎉

---

## 🔧 **Configuration**

### **config.js**
```javascript
// Production API URL
window.API_BASE_URL = "https://your-railway-url.railway.app";
```

### **vercel.json**
```json
{
  "version": 2,
  "builds": [{"src": "**/*", "use": "@vercel/static"}]
}
```

---

## 🐛 **Troubleshooting**

### **CORS Error?**
- Check Railway backend is running
- Verify URL in `config.js` (no trailing slash)

### **404 Error?**
- Verify Railway deployment succeeded
- Test: `curl https://your-app.railway.app/health/enhanced`

### **Blank Page?**
- Check browser console for errors
- Verify `config.js` is loaded before `script.js`

---

## 🔄 **Updates**

```bash
# Make changes to HTML/CSS/JS
git add .
git commit -m "Update frontend"
git push origin main

# Vercel auto-deploys in ~30 seconds!
```

---

## 📊 **Features**

- ✅ Beautiful modern UI
- ✅ Markdown rendering
- ✅ Source citations
- ✅ Confidence scores
- ✅ Response time tracking
- ✅ Mobile responsive
- ✅ Dark mode ready

---

## 💰 **Cost**

**Vercel Free Tier:**
- 100GB bandwidth/month
- Unlimited deployments
- Free SSL certificate
- Global CDN

**Perfect for this chatbot! $0/month** 🎉

---

## 🎯 **Your Live Frontend**

**URL:** `https://your-project.vercel.app`

**Share it with anyone to try your chatbot! 🚀**

---

## 📞 **Support**

- **Vercel Docs:** https://vercel.com/docs
- **Vercel Support:** https://vercel.com/support

**For detailed instructions, see `VERCEL_DEPLOYMENT_GUIDE.md`**

