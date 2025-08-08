# Enhanced GPU Chatbot Frontend Integration Guide

## 🚀 Running Enhanced GPU Chatbot with Frontend

This guide shows you how to run the enhanced GPU chatbot (10 document analysis) with the web frontend for the best user experience.

---

## 📋 Prerequisites

### **System Requirements**
- Python 3.9+ with virtual environment
- ChromaDB running with Northeastern University data
- Ollama with llama2:7b model
- GPU (optional, will fallback to CPU)

### **Required Files**
- ✅ `services/chat_service/enhanced_gpu_chatbot.py` - Enhanced GPU chatbot
- ✅ `services/chat_service/enhanced_gpu_api.py` - API server
- ✅ `frontend/` - Web interface
- ✅ `start_enhanced_gpu_system.py` - Startup script

---

## 🚀 Quick Start

### **Method 1: Automated Startup (Recommended)**

```bash
# 1. Activate virtual environment
.\\env_py3.9\\Scripts\\activate

# 2. Run the enhanced GPU system
python start_enhanced_gpu_system.py
```

This will automatically:
- ✅ Start the Enhanced GPU API server on port 8001
- ✅ Start the frontend server on port 3000
- ✅ Monitor both servers
- ✅ Display real-time logs

### **Method 2: Manual Startup**

#### **Step 1: Start Enhanced GPU API**
```bash
# Activate virtual environment
.\\env_py3.9\\Scripts\\activate

# Start API server
python services/chat_service/enhanced_gpu_api.py
```

#### **Step 2: Start Frontend (New Terminal)**
```bash
# Start frontend server
python frontend/server.py
```

---

## 🌐 Access Points

Once running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main chat interface |
| **API Docs** | http://localhost:8001/docs | Interactive API documentation |
| **Health Check** | http://localhost:8001/health | System health status |
| **API Root** | http://localhost:8001/ | API information |

---

## 🎯 Frontend Features

### **Enhanced Chat Interface**
- **Real-time Chat**: Send questions and get responses
- **Session Management**: Persistent conversation history
- **Source Attribution**: View document sources for each answer
- **Confidence Scoring**: See confidence levels for responses
- **Response Time**: Monitor performance metrics

### **Advanced Features**
- **Quick Search**: Search documents directly
- **System Status**: Monitor API health and features
- **Statistics**: View usage statistics
- **Enhanced Status**: GPU acceleration status

### **Enhanced GPU Indicators**
- **Device Status**: Shows if GPU (CUDA) is being used
- **Document Count**: Displays 10 documents analyzed
- **Feature Status**: Shows enabled enhanced features
- **Performance Metrics**: Response times and confidence scores

---

## 🔧 Configuration

### **API Configuration**
The enhanced GPU API automatically:
- ✅ Detects GPU availability
- ✅ Uses CUDA if available, falls back to CPU
- ✅ Analyzes 10 documents per query
- ✅ Uses 1,200 characters per document
- ✅ Enables query expansion and hybrid search

### **Frontend Configuration**
The frontend automatically:
- ✅ Connects to API on localhost:8001
- ✅ Displays enhanced features status
- ✅ Shows GPU acceleration status
- ✅ Provides comprehensive chat interface

---

## 📊 System Information

### **Enhanced GPU Chatbot Features**
- **Documents Analyzed**: 10 (vs 3-5 in other versions)
- **Content per Document**: 1,200 characters
- **Total Context**: ~12,000 characters
- **Response Time**: 5-15 seconds (with GPU)
- **GPU Acceleration**: Automatic detection and usage
- **Query Expansion**: 3 alternative query variations
- **Hybrid Search**: Semantic + keyword + reranking
- **Conversation History**: Context-aware responses

### **Performance Comparison**

| Version | Documents | Context | Response Time | Use Case |
|---------|-----------|---------|---------------|----------|
| **Fast (CPU)** | 3 | ~1,500 chars | 8-10s | Real-time |
| **GPU Optimized** | 3 | ~1,800 chars | 2-5s | Fast real-time |
| **Enhanced GPU** | **10** | **~12,000 chars** | **5-15s** | **Maximum accuracy** |
| **Enhanced (CPU)** | 5 | ~5,000+ chars | 90-120s | Research |

---

## 🎮 Using the Frontend

### **1. Start a Conversation**
1. Open http://localhost:3000
2. Type your question in the chat input
3. Press Enter or click Send
4. Wait for the enhanced response (5-15 seconds)

### **2. View Enhanced Information**
- **Answer**: Comprehensive response from 10 documents
- **Sources**: Click to view source documents
- **Confidence**: See confidence score (0-1)
- **Response Time**: Monitor performance
- **Device**: Check if GPU is being used

### **3. Use Quick Search**
1. Use the search bar in the sidebar
2. Search for specific topics
3. View document results directly

### **4. Monitor System Status**
- **API Status**: Online/Offline indicator
- **Enhanced Features**: Shows enabled features
- **Document Count**: Total documents available
- **GPU Status**: CUDA availability

---

## 🔍 Troubleshooting

### **Common Issues**

#### **API Server Won't Start**
```bash
# Check if port 8001 is available
netstat -an | findstr :8001

# Kill process using port 8001 (Windows)
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

#### **Frontend Server Won't Start**
```bash
# Check if port 3000 is available
netstat -an | findstr :3000

# Kill process using port 3000 (Windows)
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

#### **GPU Not Detected**
```python
# Check CUDA installation
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device count: {torch.cuda.device_count()}")
```

#### **ChromaDB Connection Issues**
```bash
# Check if ChromaDB is running
python check_chromadb_data.py
```

### **Performance Issues**

#### **Slow Response Times**
- Check if GPU is being used (should show 'cuda' in device)
- Verify Ollama is running with llama2:7b model
- Check system resources (CPU, memory, GPU)

#### **Memory Issues**
- Reduce context size in enhanced_gpu_chatbot.py
- Close other applications
- Restart the system

---

## 📈 Monitoring and Analytics

### **Real-time Monitoring**
The startup script provides:
- ✅ API server logs
- ✅ Frontend server logs
- ✅ System status updates
- ✅ Performance metrics

### **Performance Metrics**
- **Response Time**: 5-15 seconds target
- **Documents Analyzed**: 10 per query
- **GPU Utilization**: Automatic detection
- **Confidence Scores**: Quality indicators

### **Health Checks**
- **API Health**: http://localhost:8001/health
- **Enhanced Health**: http://localhost:8001/health/enhanced
- **System Stats**: http://localhost:8001/stats

---

## 🎯 Advanced Usage

### **Custom Configuration**
You can modify the enhanced GPU chatbot settings in `services/chat_service/enhanced_gpu_chatbot.py`:

```python
# Adjust document count
relevant_docs = self.hybrid_search(question, k=10)  # Change 10 to desired number

# Adjust content per document
content_preview = doc['content'][:1200]  # Change 1200 to desired length

# Adjust LLM parameters
self.llm = Ollama(
    model=model_name,
    temperature=0.3,  # Adjust creativity
    num_ctx=4096,     # Adjust context window
    # ... other parameters
)
```

### **API Endpoints**
- `POST /chat` - Send questions and get responses
- `GET /health` - System health check
- `GET /stats` - System statistics
- `GET /documents` - Document information
- `POST /search` - Search documents

---

## 🚀 Performance Optimization

### **For Maximum Speed**
1. **Enable GPU**: Install CUDA and PyTorch with GPU support
2. **Use SSD**: Store ChromaDB on fast storage
3. **Optimize Memory**: Close unnecessary applications
4. **Network**: Use localhost for minimal latency

### **For Maximum Accuracy**
1. **Use Enhanced GPU**: Already configured for maximum accuracy
2. **10 Documents**: Comprehensive coverage
3. **Query Expansion**: Multiple search variations
4. **Hybrid Search**: Semantic + keyword search

---

## 🎉 Success Indicators

### **System Running Successfully**
- ✅ Frontend accessible at http://localhost:3000
- ✅ API responding at http://localhost:8001
- ✅ GPU detected (if available)
- ✅ 10 documents being analyzed
- ✅ Response times 5-15 seconds

### **Enhanced Features Working**
- ✅ Query expansion generating variations
- ✅ Hybrid search finding relevant documents
- ✅ Conversation history maintained
- ✅ Confidence scores calculated
- ✅ Source attribution displayed

---

## 📚 Summary

The Enhanced GPU Chatbot with Frontend provides:

- **🎯 Maximum Accuracy**: 10 documents, 12,000 character context
- **🚀 Optimal Performance**: 5-15 seconds with GPU acceleration
- **🌐 Beautiful Interface**: Modern web-based chat interface
- **📊 Real-time Monitoring**: Live system status and metrics
- **🔧 Easy Management**: Automated startup and monitoring

This setup represents the pinnacle of the Northeastern University chatbot system, offering the best possible user experience with maximum accuracy and reasonable response times. 