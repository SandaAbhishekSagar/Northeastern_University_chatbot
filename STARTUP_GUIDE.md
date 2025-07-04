# Northeastern University Chatbot - Complete Startup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Ollama installed and running
- ChromaDB (included in requirements)
- All dependencies installed

### 1. Environment Setup
```bash
# Activate the correct Python environment
# On Windows:
env_py3.9\Scripts\activate

# On macOS/Linux:
source env_py3.9/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Pull Ollama Model
```bash
ollama pull llama2:7b
```

## 🏃‍♂️ Running the Complete System

### Option 1: Automated Startup Script
```bash
# Run the complete system with one command
python run.py
```

### Option 2: Manual Step-by-Step

#### Step 1: Start ChromaDB
```bash
# Start ChromaDB server (if not already running)
chroma run --host localhost --port 8000
```

#### Step 2: Start the API Server
```bash
# Start the enhanced chatbot API
cd services/chat_service
python api.py
```
The API will run on `http://localhost:8001`

#### Step 3: Start the Frontend
```bash
# In a new terminal, start the frontend server
cd frontend
python -m http.server 8080
```
The frontend will be available at `http://localhost:8080`

## 📊 System Components

### 1. Enhanced RAG Chatbot API
- **Location**: `services/chat_service/api.py`
- **Port**: 8001
- **Features**: 
  - Hybrid search (semantic + keyword)
  - Query expansion
  - Confidence scoring
  - Conversation history

### 2. Northeastern-Themed Frontend
- **Location**: `frontend/`
- **Port**: 8080
- **Features**:
  - Northeastern University branding
  - Real-time chat interface
  - Enhanced features display
  - System status monitoring

### 3. ChromaDB Vector Database
- **Port**: 8000
- **Purpose**: Stores university documents and embeddings

## 🧪 Testing the System

### Test Enhanced Features
```bash
# Run comprehensive system tests
python test_enhanced_system.py
```

### Test Basic Functionality
```bash
# Run basic system tests
python test_system.py
```

## 🔧 Configuration

### API Configuration
The API automatically uses:
- **LLM**: Ollama with llama2:7b
- **Embeddings**: all-MiniLM-L6-v2
- **Database**: ChromaDB on localhost:8000

### Frontend Configuration
The frontend connects to:
- **API**: http://localhost:8001
- **Features**: Enhanced RAG capabilities

## 📁 Project Structure

```
university_chatbot/
├── services/
│   ├── chat_service/
│   │   ├── api.py                    # Enhanced API server
│   │   ├── enhanced_rag_chatbot.py   # Enhanced RAG implementation
│   │   └── rag_chatbot.py           # Basic RAG implementation
│   ├── scraping_service/             # Web scraping for university data
│   ├── processing_service/           # Data processing tasks
│   └── shared/                       # Shared utilities and models
├── frontend/
│   ├── index.html                   # Northeastern-themed UI
│   ├── styles.css                   # Northeastern styling
│   └── script.js                    # Frontend functionality
├── run.py                           # Automated startup script
├── test_enhanced_system.py          # Enhanced features testing
├── test_system.py                   # Basic system testing
└── requirements.txt                 # Python dependencies
```

## 🎯 Usage Examples

### 1. Start Everything Automatically
```bash
python run.py
```
This will:
- Start ChromaDB
- Start the API server
- Start the frontend server
- Open your browser to the application

### 2. Manual Control
```bash
# Terminal 1: Start ChromaDB
chroma run --host localhost --port 8000

# Terminal 2: Start API
cd services/chat_service
python api.py

# Terminal 3: Start Frontend
cd frontend
python -m http.server 8080
```

### 3. Test the System
```bash
# Test enhanced features
python test_enhanced_system.py

# Test basic functionality
python test_system.py
```

## 🌐 Access Points

Once running, you can access:

- **Frontend**: http://localhost:8080
- **API**: http://localhost:8001
- **API Health**: http://localhost:8001/health/enhanced
- **ChromaDB**: http://localhost:8000

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8001
# Kill the process if needed
taskkill /PID <process_id> /F
```

#### 2. Ollama Not Running
```bash
# Start Ollama
ollama serve
# Pull the model
ollama pull llama2:7b
```

#### 3. ChromaDB Connection Issues
```bash
# Restart ChromaDB
chroma run --host localhost --port 8000
```

#### 4. Python Environment Issues
```bash
# Ensure you're using the correct environment
env_py3.9\Scripts\activate
pip install -r requirements.txt
```

### Health Checks

#### API Health
```bash
curl http://localhost:8001/health/enhanced
```

#### Frontend Status
Open http://localhost:8080 and check the sidebar for system status.

## 📈 Monitoring

### System Status
The frontend sidebar shows:
- API Status (Online/Offline)
- Document Count
- University Count
- Enhanced Features Status

### Performance Metrics
- Response times
- Confidence scores
- Search query expansion
- Retrieval methods used

## 🚀 Production Deployment

For production deployment, consider:
- Using a production WSGI server (Gunicorn)
- Setting up a reverse proxy (Nginx)
- Using a production ChromaDB setup
- Implementing proper logging and monitoring

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all services are running on correct ports
3. Ensure Ollama is running with the correct model
4. Check the console logs for error messages

---

## 🎯 Quick Commands Summary

```bash
# Complete startup
python run.py

# Manual startup
chroma run --host localhost --port 8000 &
cd services/chat_service && python api.py &
cd frontend && python -m http.server 8080 &

# Testing
python test_enhanced_system.py
python test_system.py

# Health checks
curl http://localhost:8001/health/enhanced
```

The system is now ready to provide Northeastern University information with enhanced AI capabilities! 🎓 