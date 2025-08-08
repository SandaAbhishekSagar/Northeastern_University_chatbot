# Northeastern University Chatbot - Enhanced GPU Edition

A comprehensive AI-powered chatbot system specifically designed for Northeastern University, featuring **GPU-accelerated RAG (Retrieval-Augmented Generation)**, confidence scoring, user feedback, and web scraping capabilities.

## 🚀 **Enhanced GPU Features**

- **🎮 GPU Acceleration**: NVIDIA CUDA support for lightning-fast processing
- **⚡ Optimized Performance**: 5-15 second response times with GPU
- **🔍 Enhanced RAG Pipeline**: GPU-accelerated embeddings and search
- **🔄 Query Expansion**: Automatic query enhancement for better results
- **🎯 Hybrid Search**: Semantic + keyword search with GPU optimization
- **📊 Confidence Scoring**: Multi-factor confidence assessment
- **🕷️ Web Scraping**: Automated scraping of Northeastern University websites
- **💾 ChromaDB Integration**: Vector database for efficient document storage
- **🌐 Modern Frontend**: Northeastern-themed responsive web interface

## 📋 Table of Contents

1. [Quick Start - Enhanced GPU](#quick-start---enhanced-gpu)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Running the Application](#running-the-application)
5. [GPU Acceleration Setup](#gpu-acceleration-setup)
6. [System Architecture](#system-architecture)
7. [API Documentation](#api-documentation)
8. [Troubleshooting](#troubleshooting)
9. [Alternative Deployment Options](#alternative-deployment-options)

## ⚡ Quick Start - Enhanced GPU

### 🎯 **One-Command Startup (Recommended)**

```bash
# Clone and setup
git clone <repository-url>
cd university_chatbot

# Activate virtual environment
env_py3.9\Scripts\activate  # Windows
source env_py3.9/bin/activate  # macOS/Linux

# Start Enhanced GPU System
python quick_start_enhanced_gpu.py
```

### 🌐 **Access Your Application**

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health/enhanced

## 💻 System Requirements

### **Minimum Requirements**
- **OS**: Windows 10/11, macOS, or Linux
- **Python**: 3.9+ (recommended: 3.9.13)
- **RAM**: 8GB+ (16GB recommended)
- **Storage**: 10GB+ free space
- **Network**: Internet connection

### **Enhanced GPU Requirements**
- **GPU**: NVIDIA GPU with CUDA support (RTX 3060+ recommended)
- **CUDA**: Version 11.0+ installed
- **VRAM**: 6GB+ for optimal performance
- **RAM**: 16GB+ for GPU operations

### **Software Dependencies**
1. **Python 3.9+**
2. **Ollama** (for local LLM)
3. **Git** (for repository cloning)

## 🛠️ Installation

### **Step 1: Clone Repository**
```bash
git clone <repository-url>
cd university_chatbot
```

### **Step 2: Setup Python Environment**
```bash
# Create virtual environment
python -m venv env_py3.9

# Activate environment
# Windows:
env_py3.9\Scripts\activate
# macOS/Linux:
source env_py3.9/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 3: Setup Ollama (Local LLM)**
```bash
# Download from https://ollama.ai
# Install and start Ollama service
ollama serve

# Pull the required model
ollama pull llama2:7b
```

## 🚀 Running the Application

### **Option 1: Enhanced GPU System (Recommended)**

```bash
# Activate environment
env_py3.9\Scripts\activate

# Start Enhanced GPU System
python quick_start_enhanced_gpu.py
```

**Features:**
- ✅ GPU acceleration (if available)
- ✅ Enhanced RAG pipeline
- ✅ Query expansion
- ✅ Hybrid search
- ✅ Optimized performance

### **Option 2: Manual Startup**

```bash
# Terminal 1: Start Enhanced GPU API
python -m uvicorn services.chat_service.enhanced_gpu_api:app --host 0.0.0.0 --port 8001

# Terminal 2: Start Frontend
cd frontend
python server.py
```

### **Option 3: Standard System (No GPU)**

```bash
# Start standard API
python -m uvicorn services.chat_service.api:app --host 0.0.0.0 --port 8001

# Start frontend
cd frontend
python -m http.server 8080
```

## 🎮 GPU Acceleration Setup

### **NVIDIA GPU Setup**

1. **Install NVIDIA Drivers**
   ```bash
   # Download from https://www.nvidia.com/drivers/
   # Install latest drivers for your GPU
   ```

2. **Install CUDA Toolkit**
   ```bash
   # Download from https://developer.nvidia.com/cuda-downloads
   # Install CUDA 11.0+ for your OS
   ```

3. **Install PyTorch with CUDA**
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

4. **Verify GPU Detection**
   ```bash
   python test_gpu_detection.py
   ```

### **GPU Performance Optimization**

- **VRAM Management**: Ensure 6GB+ VRAM available
- **Batch Processing**: GPU processes multiple queries efficiently
- **Memory Optimization**: Automatic GPU memory management
- **Fallback**: Automatic CPU fallback if GPU unavailable

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │ Enhanced GPU    │    │   ChromaDB      │
│   (Port 3000)   │◄──►│   API Server    │◄──►│   (Port 8000)   │
│                 │    │   (Port 8001)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Ollama LLM    │
                       │   (Local)       │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   NVIDIA GPU    │
                       │   (CUDA)        │
                       └─────────────────┘
```

### **Enhanced GPU Components**

- **Frontend**: React-like interface with Northeastern branding
- **Enhanced GPU API**: FastAPI backend with GPU acceleration
- **ChromaDB**: Vector database for document storage
- **Ollama**: Local LLM (llama2:7b) for answer generation
- **NVIDIA GPU**: CUDA acceleration for embeddings and processing

## 📚 API Documentation

### **Enhanced GPU Endpoints**

#### **Health Check**
```bash
GET http://localhost:8001/health/enhanced
```
**Response:**
```json
{
  "status": "healthy",
  "message": "Enhanced GPU Northeastern University Chatbot API is running",
  "device": "cuda",
  "features": {
    "gpu_acceleration": "enabled",
    "query_expansion": "enabled",
    "hybrid_search": "enabled"
  }
}
```

#### **Chat Endpoint**
```bash
POST http://localhost:8001/chat
Content-Type: application/json

{
  "question": "What programs does Northeastern offer?",
  "session_id": "user123"
}
```

#### **Document Count**
```bash
GET http://localhost:8001/documents
```

### **Performance Metrics**

- **Response Time**: 5-15 seconds (GPU accelerated)
- **Documents Analyzed**: 10 per query
- **Search Type**: Hybrid (semantic + keyword)
- **GPU Utilization**: Real-time monitoring

## 🔧 Troubleshooting

### **Common Issues**

#### **GPU Not Detected**
```bash
# Check GPU availability
python test_gpu_detection.py

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### **Port Already in Use**
```bash
# Kill existing processes
taskkill /f /im python.exe  # Windows
pkill -f python  # macOS/Linux

# Check ports
netstat -ano | findstr ":8001\|:3000"  # Windows
lsof -i :8001,3000  # macOS/Linux
```

#### **Ollama Not Running**
```bash
# Start Ollama service
ollama serve

# Pull required model
ollama pull llama2:7b
```

#### **Memory Issues**
```bash
# Check available memory
nvidia-smi  # GPU memory
free -h     # System memory (Linux)
```

### **Performance Optimization**

1. **GPU Memory**: Ensure sufficient VRAM (6GB+)
2. **System RAM**: 16GB+ recommended
3. **Storage**: SSD for faster I/O
4. **Network**: Stable internet connection

## 🔄 Alternative Deployment Options

### **Standard System (No GPU)**
```bash
python -m uvicorn services.chat_service.api:app --host 0.0.0.0 --port 8001
cd frontend && python -m http.server 8080
```

### **OpenAI System**
```bash
python run_openai_frontend.py
```

### **Production Deployment**
```bash
python start_production.py
```

## 📊 Performance Comparison

| Feature | Standard | Enhanced GPU |
|---------|----------|--------------|
| Response Time | 15-30s | 5-15s |
| GPU Acceleration | ❌ | ✅ |
| Query Expansion | ❌ | ✅ |
| Hybrid Search | Basic | Enhanced |
| Document Analysis | 5 docs | 10 docs |
| Confidence Scoring | Basic | Advanced |

## 🎯 Usage Examples

### **Basic Questions**
- "What is Northeastern University?"
- "What programs does Northeastern offer?"
- "How do I apply to Northeastern?"

### **Advanced Queries**
- "What are the co-op opportunities in computer science?"
- "Tell me about Northeastern's research facilities"
- "What are the admission requirements for international students?"

## 📈 Monitoring and Analytics

### **Real-time Metrics**
- GPU utilization
- Response times
- Document retrieval accuracy
- User satisfaction scores

### **Health Monitoring**
```bash
# Check system health
curl http://localhost:8001/health/enhanced

# Monitor GPU usage
nvidia-smi -l 1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check system requirements
4. Open an issue on GitHub

---

**🎮 Ready to experience GPU-accelerated AI chat? Start with the Enhanced GPU System for the best performance!** 