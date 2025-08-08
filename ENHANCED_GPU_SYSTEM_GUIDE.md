# Enhanced GPU System Startup Guide

## 🚀 What is `start_enhanced_gpu_system.py`?

This script launches the **Enhanced GPU Optimized Chatbot System** - a high-performance version of your university chatbot that uses:

- **GPU Acceleration** for faster processing
- **Enhanced RAG Pipeline** with advanced features
- **Query Expansion** for better search results
- **Hybrid Search** (semantic + keyword)
- **Optimized Embeddings** for better performance

## 📋 Prerequisites

Before running the enhanced GPU system, ensure you have:

### 1. Virtual Environment
```bash
# Check if virtual environment exists
ls env_py3.9/
```

### 2. Required Files
- ✅ `services/chat_service/enhanced_gpu_api.py`
- ✅ `frontend/server.py`
- ✅ `enhanced_embeddings_cache.pkl` (368MB - recommended)

### 3. GPU Support (Optional but Recommended)
- NVIDIA GPU with CUDA support
- CUDA drivers installed
- PyTorch with CUDA support

## 🎯 How to Run

### Method 1: Simple Command
```bash
python start_enhanced_gpu_system.py
```

### Method 2: With Virtual Environment
```bash
# Activate virtual environment first
env_py3.9\Scripts\activate  # Windows
source env_py3.9/bin/activate  # Linux/Mac

# Then run the system
python start_enhanced_gpu_system.py
```

### Method 3: Direct Execution
```bash
# Make executable (Linux/Mac)
chmod +x start_enhanced_gpu_system.py

# Run directly
./start_enhanced_gpu_system.py
```

## 🔧 What the Script Does

### 1. System Check
- ✅ Verifies virtual environment exists
- ✅ Checks for required API and frontend files
- ✅ Validates dependencies

### 2. Starts API Server
- 🚀 Launches Enhanced GPU API on port 8001
- 🔧 Uses GPU-optimized embeddings
- 📊 Enables advanced RAG features

### 3. Starts Frontend Server
- 🌐 Launches frontend on port 3000
- 🔗 Connects to the enhanced API
- 📱 Provides chat interface

### 4. Monitoring
- 👀 Monitors both servers
- 🔄 Auto-restart on failure
- 📈 Performance tracking

## 🌟 Features of Enhanced GPU System

### Performance Features
- **GPU Acceleration**: Uses CUDA for faster processing
- **Optimized Embeddings**: Pre-computed embeddings for speed
- **Query Expansion**: Generates multiple search queries
- **Hybrid Search**: Combines semantic and keyword search
- **Smart Caching**: Reduces redundant computations

### RAG Pipeline Features
- **Enhanced Context Preparation**: Better document selection
- **Confidence Scoring**: Multi-factor confidence assessment
- **Source Attribution**: Links to original documents
- **Conversation History**: Maintains chat context
- **Response Validation**: Quality checks on answers

### System Features
- **Auto-restart**: Recovers from failures
- **Process Monitoring**: Tracks server health
- **Graceful Shutdown**: Clean termination
- **Error Handling**: Comprehensive error management

## 📊 Expected Performance

| Metric | Enhanced GPU System | Standard System |
|--------|-------------------|-----------------|
| Response Time | 5-15 seconds | 10-30 seconds |
| Documents Analyzed | 10 per query | 5 per query |
| Context Length | ~12,000 chars | ~6,000 chars |
| Search Quality | High (hybrid) | Medium (semantic) |
| GPU Utilization | Yes | No |

## 🔗 Access Points

Once running, you can access:

### Web Interface
- **Chat Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

### API Endpoints
- **Chat**: `POST http://localhost:8001/chat`
- **Health**: `GET http://localhost:8001/health`
- **Stats**: `GET http://localhost:8001/stats`

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Virtual environment not found"
```bash
# Create virtual environment
python -m venv env_py3.9

# Activate it
env_py3.9\Scripts\activate  # Windows
source env_py3.9/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

#### 2. "Enhanced GPU API not found"
```bash
# Check if the file exists
ls services/chat_service/enhanced_gpu_api.py

# If missing, you may need to use the standard system instead
python start_system.py
```

#### 3. "Port already in use"
```bash
# Kill existing processes
lsof -ti:8001 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8001   # Windows
```

#### 4. "GPU not available"
```bash
# The system will fall back to CPU mode
# Check GPU availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Debug Mode

Run with verbose logging:
```bash
# Set debug environment variable
set DEBUG=1  # Windows
export DEBUG=1  # Linux/Mac

# Run the system
python start_enhanced_gpu_system.py
```

## 🔄 Alternative Startup Methods

### 1. Manual Startup (Two Terminals)

**Terminal 1 (API Server):**
```bash
cd services/chat_service
python enhanced_gpu_api.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
python server.py
```

### 2. Using the Standard System
```bash
# If enhanced GPU system fails, use standard system
python start_system.py
```

### 3. Using OpenAI System
```bash
# For OpenAI-based system
python run_openai_frontend.py
```

## 📈 Performance Monitoring

### Check System Status
```bash
# Health check
curl http://localhost:8001/health

# Get statistics
curl http://localhost:8001/stats
```

### Monitor Logs
The script provides real-time logging:
- API server logs
- Frontend server logs
- Error messages
- Performance metrics

### Performance Indicators
- ✅ Response times under 15 seconds
- ✅ GPU utilization (if available)
- ✅ Successful document retrieval
- ✅ High confidence scores

## 🎯 Best Practices

### 1. System Requirements
- **RAM**: 8GB+ recommended
- **GPU**: NVIDIA GPU with 4GB+ VRAM (optional)
- **Storage**: 2GB+ free space
- **Network**: Stable internet connection

### 2. Optimization Tips
- Use the enhanced embeddings cache (368MB)
- Ensure GPU drivers are up to date
- Close unnecessary applications
- Monitor system resources

### 3. Usage Tips
- Start with simple questions
- Check the API documentation
- Monitor response times
- Use the health check endpoint

## 🆘 Getting Help

### If the System Won't Start
1. Check prerequisites
2. Verify file paths
3. Check port availability
4. Review error messages
5. Try alternative startup methods

### If Performance is Poor
1. Check GPU availability
2. Monitor system resources
3. Use the enhanced cache
4. Restart the system
5. Check network connectivity

### Support Resources
- Check the logs for error messages
- Review the API documentation
- Test individual components
- Use the troubleshooting guide

## 🎉 Success Indicators

You'll know the system is working correctly when:

- ✅ Both servers start without errors
- ✅ You can access http://localhost:3000
- ✅ Chat interface responds to questions
- ✅ Response times are reasonable (5-15 seconds)
- ✅ GPU utilization is shown (if available)
- ✅ No error messages in the logs

The Enhanced GPU System provides the best performance and features for your university chatbot! 