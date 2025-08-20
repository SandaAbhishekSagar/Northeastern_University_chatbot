# 🌲 Pinecone Vector Database Setup Guide

## 🎯 **Overview**

This guide will help you set up **Pinecone** as your vector database, providing:
- ✅ **Enterprise-grade reliability** - 99.9% uptime
- ✅ **Automatic scaling** - Handles millions of vectors
- ✅ **Fast search** - Sub-second query times
- ✅ **Free tier** - 1 index, 100K vectors, 10GB storage
- ✅ **Simple setup** - No complex configuration

---

## 🚀 **Step 1: Get Pinecone Account**

1. **Visit**: https://app.pinecone.io/
2. **Sign up** for a free account
3. **Create a new project**
4. **Get your API key** from the dashboard

---

## 🔧 **Step 2: Setup Environment**

### **Local Development**

1. **Set environment variable**:
```bash
# Windows PowerShell
$env:PINECONE_API_KEY="your_api_key_here"

# Windows Command Prompt
set PINECONE_API_KEY=your_api_key_here

# macOS/Linux
export PINECONE_API_KEY=your_api_key_here
```

2. **Or add to `.env` file**:
```bash
# Pinecone Configuration
PINECONE_API_KEY=your_api_key_here
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=northeastern-university
```

### **Railway Deployment**

1. **Go to Railway Dashboard**
2. **Select your project**
3. **Go to Variables tab**
4. **Add these environment variables**:
   - `PINECONE_API_KEY` = `your_api_key_here`
   - `PINECONE_ENVIRONMENT` = `us-east-1-aws`
   - `PINECONE_INDEX_NAME` = `northeastern-university`

---

## 📦 **Step 3: Migrate Your Data**

### **Run Migration Script**

```bash
# Set your API key
$env:PINECONE_API_KEY="your_api_key_here"

# Run migration
python migrate_to_pinecone.py
```

**What the migration does:**
- Connects to your local ChromaDB
- Connects to Pinecone
- Creates index if needed
- Migrates all documents with embeddings
- Verifies the migration

### **Expected Output**
```
🌲 Pinecone Migration Tool
==================================================
✅ PINECONE_API_KEY found, starting migration...
🌲 Setting up Pinecone Vector Database...
✅ Using existing Pinecone index: northeastern-university
📁 Connecting to local ChromaDB at ...
✅ Connected to local ChromaDB
🤖 Loading embedding model...
🔄 Migrating 110086 documents to Pinecone...
📊 Generating embeddings for batch 1...
✅ Migrated batch 1: 100 documents
...
🎉 Migration completed!
📊 Total documents migrated to Pinecone: 110086
🌲 Data is now available in Pinecone
```

---

## 🧪 **Step 4: Test the Setup**

### **Test Connection**

```bash
# Test the connection
python -c "
from services.shared.database import get_database_type, get_pinecone_count
print(f'Database type: {get_database_type()}')
print(f'Document count: {get_pinecone_count()}')
"
```

### **Expected Output**
```
🌲 Using Pinecone Vector Database
Database type: pinecone
Document count: 110086
```

---

## 🚀 **Step 5: Deploy to Railway**

1. **Commit your changes**:
```bash
git add .
git commit -m "feat: migrate to Pinecone vector database"
git push
```

2. **Railway will automatically deploy** with the new configuration

3. **Check the logs** for successful connection:
```
🌲 Using Pinecone Vector Database
✅ Pinecone database initialized
✅ Enhanced GPU API imported successfully
```

---

## 💰 **Pricing**

### **Free Tier**
- ✅ **1 index**
- ✅ **100,000 vectors**
- ✅ **10GB storage**
- ✅ **Perfect for development**

### **Paid Plans**
- **Starter**: $0.01 per 1K operations - 1M vectors, 100GB
- **Standard**: $0.01 per 1K operations - 10M vectors, 1TB
- **Enterprise**: Custom pricing

---

## 🔍 **Troubleshooting**

### **Connection Issues**

**Error**: `Failed to connect to Pinecone`
**Solution**: Check your API key and environment

**Error**: `Index not found`
**Solution**: Index is created automatically, this is normal

**Error**: `Dimension mismatch`
**Solution**: Index dimension is set to 384 for all-MiniLM-L6-v2

### **Migration Issues**

**Error**: `No documents found`
**Solution**: Make sure your local ChromaDB has data

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

### **After (Pinecone)**
- ✅ Automatic backups
- ✅ No schema issues
- ✅ No file locking
- ✅ Unlimited scaling
- ✅ Zero maintenance
- ✅ Enterprise reliability

---

## 🎯 **Next Steps**

1. **Test your chatbot** - Should work exactly the same
2. **Monitor usage** - Check Pinecone dashboard
3. **Scale as needed** - Upgrade plan if required
4. **Enjoy reliability** - No more database issues!

---

## 📞 **Support**

- **Pinecone Docs**: https://docs.pinecone.io/
- **Community**: https://discord.gg/pinecone
- **Email**: support@pinecone.io

---

**🎉 Congratulations! Your chatbot now uses Pinecone!** 