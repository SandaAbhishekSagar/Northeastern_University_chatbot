# ☁️ ChromaDB Cloud Setup Guide

## 🎯 **Overview**

This guide will help you migrate from local ChromaDB to **ChromaDB Cloud**, which provides:
- ✅ **Managed hosting** - No more local database management
- ✅ **Automatic backups** - Data is always safe
- ✅ **Scalability** - Handles large datasets easily
- ✅ **Reliability** - 99.9% uptime guarantee
- ✅ **Security** - Enterprise-grade security

---

## 🚀 **Step 1: Get ChromaDB Cloud Account**

1. **Visit**: https://cloud.chromadb.com
2. **Sign up** for a free account
3. **Create a new project**
4. **Get your API token** from the dashboard

---

## 🔧 **Step 2: Setup Environment**

### **Local Development**

1. **Create `.env` file** (if not exists):
```bash
# ChromaDB Cloud Configuration
CHROMA_CLOUD_TOKEN=your_token_here
CHROMA_CLOUD_HOST=https://api.chromadb.com
```

2. **Set environment variables**:
```bash
# Windows
set CHROMA_CLOUD_TOKEN=your_token_here

# macOS/Linux
export CHROMA_CLOUD_TOKEN=your_token_here
```

### **Railway Deployment**

1. **Go to Railway Dashboard**
2. **Select your project**
3. **Go to Variables tab**
4. **Add these environment variables**:
   - `CHROMA_CLOUD_TOKEN` = `your_token_here`
   - `CHROMA_CLOUD_HOST` = `https://api.chromadb.com`

---

## 📦 **Step 3: Migrate Your Data**

### **Option A: Use Migration Script (Recommended)**

```bash
# Run the migration script
python migrate_to_chromadb_cloud.py
```

**What it does:**
- Connects to your local ChromaDB
- Connects to ChromaDB Cloud
- Migrates all collections and documents
- Verifies the migration

### **Option B: Manual Migration**

If you prefer to migrate manually:

1. **Export from local ChromaDB**:
```python
from services.shared.database import get_chroma_client
client = get_chroma_client()
collection = client.get_collection('documents')
data = collection.get()
```

2. **Import to ChromaDB Cloud**:
```python
import chromadb
cloud_client = chromadb.HttpClient(
    host="https://api.chromadb.com",
    headers={"Authorization": "Bearer your_token"}
)
collection = cloud_client.create_collection('documents')
collection.add(
    documents=data['documents'],
    metadatas=data['metadatas'],
    ids=data['ids']
)
```

---

## 🧪 **Step 4: Test the Setup**

### **Test Connection**

```bash
# Test the connection
python -c "
from services.shared.database import get_chroma_client, get_collection
client = get_chroma_client()
collection = get_collection('documents')
result = collection.get()
print(f'Connected! Found {len(result.get(\"ids\", []))} documents')
"
```

### **Expected Output**
```
☁️  Connecting to ChromaDB Cloud at https://api.chromadb.com
✅ Connected to ChromaDB Cloud
[OK] Retrieved collection: documents
Connected! Found 110086 documents
```

---

## 🚀 **Step 5: Deploy to Railway**

1. **Commit your changes**:
```bash
git add .
git commit -m "feat: migrate to ChromaDB Cloud"
git push
```

2. **Railway will automatically deploy** with the new configuration

3. **Check the logs** for successful connection:
```
☁️  Connecting to ChromaDB Cloud at https://api.chromadb.com
✅ Connected to ChromaDB Cloud
✅ ChromaDB connected successfully - 110086 documents available
```

---

## 💰 **Pricing**

### **Free Tier**
- ✅ **1GB storage**
- ✅ **1,000 queries/month**
- ✅ **Perfect for development**

### **Paid Plans**
- **Starter**: $25/month - 10GB, 100K queries
- **Professional**: $100/month - 100GB, 1M queries
- **Enterprise**: Custom pricing

---

## 🔍 **Troubleshooting**

### **Connection Issues**

**Error**: `Failed to connect to ChromaDB Cloud`
**Solution**: Check your API token and network connection

**Error**: `Unauthorized`
**Solution**: Verify your `CHROMA_CLOUD_TOKEN` is correct

### **Migration Issues**

**Error**: `Collection not found`
**Solution**: Collections are created automatically, this is normal

**Error**: `Timeout`
**Solution**: Large datasets may take time, be patient

---

## 📊 **Benefits After Migration**

### **Before (Local ChromaDB)**
- ❌ Complex backup management
- ❌ Schema version issues
- ❌ File locking problems
- ❌ Storage limitations
- ❌ Manual maintenance

### **After (ChromaDB Cloud)**
- ✅ Automatic backups
- ✅ No schema issues
- ✅ No file locking
- ✅ Unlimited scaling
- ✅ Zero maintenance

---

## 🎯 **Next Steps**

1. **Test your chatbot** - Should work exactly the same
2. **Monitor usage** - Check ChromaDB Cloud dashboard
3. **Scale as needed** - Upgrade plan if required
4. **Enjoy reliability** - No more database issues!

---

## 📞 **Support**

- **ChromaDB Cloud Docs**: https://docs.chromadb.com
- **Community**: https://discord.gg/chromadb
- **Email**: support@chromadb.com

---

**🎉 Congratulations! Your chatbot now uses ChromaDB Cloud!** 