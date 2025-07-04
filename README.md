# Northeastern University Chatbot

A comprehensive AI-powered chatbot system specifically designed for Northeastern University, featuring advanced RAG (Retrieval-Augmented Generation), confidence scoring, user feedback, and web scraping capabilities.

## 🎯 Project Overview

This project is a full-stack AI chatbot system that provides accurate, contextual information about Northeastern University. It combines web scraping, semantic search, local LLM processing, and user feedback to deliver reliable university information.

### Key Features

- **🤖 Enhanced RAG System**: Hybrid search combining semantic and keyword matching
- **🎯 Confidence Scoring**: Multi-factor confidence assessment with dynamic thresholds
- **📊 User Feedback Loop**: Rating system with analytics for continuous improvement
- **🕷️ Web Scraping**: Automated scraping of Northeastern University websites
- **💾 ChromaDB Integration**: Vector database for efficient document storage and retrieval
- **🌐 Modern Frontend**: Northeastern-themed responsive web interface
- **🔧 RESTful API**: Comprehensive API with health monitoring and analytics

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [System Components](#system-components)
6. [API Documentation](#api-documentation)
7. [Usage Examples](#usage-examples)
8. [Troubleshooting](#troubleshooting)
9. [Development](#development)
10. [Deployment](#deployment)

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Server    │    │   ChromaDB      │
│   (Port 8080)   │◄──►│   (Port 8001)   │◄──►│   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Ollama LLM    │
                       │   (Local)       │
                       └─────────────────┘
```

### Component Overview

- **Frontend**: React-like interface with Northeastern branding
- **API Server**: FastAPI backend with enhanced RAG capabilities
- **ChromaDB**: Vector database for document storage and similarity search
- **Ollama**: Local LLM (llama2:7b) for answer generation
- **Scraping Service**: Scrapy-based web crawler for data collection

## 📋 Prerequisites

### System Requirements

- **OS**: Windows 10/11, macOS, or Linux
- **Python**: 3.9+ (recommended: 3.9.13)
- **RAM**: 8GB+ (16GB recommended for LLM)
- **Storage**: 10GB+ free space
- **Network**: Internet connection for initial setup

### Required Software

1. **Python 3.9+**
   ```bash
   # Download from python.org or use conda
   conda create -n env_py3.9 python=3.9
   ```

2. **Ollama**
   ```bash
   # Download from https://ollama.ai
   # Install and run: ollama serve
   # Pull model: ollama pull llama2:7b
   ```

3. **Git** (for cloning the repository)

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd university_chatbot
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv env_py3.9

# Activate environment
# Windows:
env_py3.9\Scripts\activate
# macOS/Linux:
source env_py3.9/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Ollama

```bash
# Start Ollama server
ollama serve

# In another terminal, pull the model
ollama pull llama2:7b
```

### Step 5: Environment Configuration

Create a `.env` file in the project root:

```env
# ChromaDB Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8000

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001

# Frontend Configuration
FRONTEND_PORT=8080

# Logging
LOG_LEVEL=INFO
```

## ⚡ Quick Start

### Automated Startup

```bash
# Activate environment
env_py3.9\Scripts\activate

# Start all services
python start_system.py
```

This will automatically:
- ✅ Start ChromaDB server
- ✅ Launch the enhanced API server
- ✅ Start the frontend server
- ✅ Open your browser to the application

### Manual Startup

```bash
# Terminal 1: Start ChromaDB
chroma run --host localhost --port 8000

# Terminal 2: Start API Server
cd services/chat_service
python -m uvicorn api:app --host 0.0.0.0 --port 8001

# Terminal 3: Start Frontend
cd frontend
python -m http.server 8080
```

## 🧩 System Components

### 1. Enhanced RAG Chatbot (`services/chat_service/enhanced_rag_chatbot.py`)

**Purpose**: Core AI engine with advanced retrieval and generation capabilities.

**Key Functions**:

```python
# Initialize chatbot
chatbot = EnhancedUniversityRAGChatbot(model_name="llama2:7b")

# Generate enhanced response with confidence scoring
response = chatbot.generate_enhanced_response(question, session_id)

# Hybrid search combining semantic and keyword matching
results = chatbot.hybrid_search(query, k=10)

# Query expansion for better retrieval
expanded_queries = chatbot.expand_query(query)

# Confidence scoring based on multiple factors
confidence = chatbot.calculate_confidence(relevant_docs, question, answer)

# User feedback storage and analytics
chatbot.store_user_feedback(session_id, question, answer, rating, feedback_text)
analytics = chatbot.get_feedback_analytics()
```

**Features**:
- Multi-factor confidence scoring (document similarity, answer quality, source diversity)
- Dynamic confidence thresholds based on question type
- Query expansion with Northeastern-specific terms
- Hybrid search (semantic + keyword)
- User feedback collection and analytics

### 2. API Server (`services/chat_service/api.py`)

**Purpose**: RESTful API providing access to chatbot functionality.

**Endpoints**:

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/chat` | POST | Main chat endpoint with confidence filtering | `question`, `session_id` |
| `/feedback` | POST | Submit user feedback | `session_id`, `question`, `answer`, `rating`, `feedback_text` |
| `/feedback/analytics` | GET | Get feedback analytics | None |
| `/search` | GET | Hybrid document search | `query`, `k` |
| `/search/semantic` | GET | Semantic search only | `query`, `k` |
| `/search/expand` | GET | Query expansion | `query` |
| `/chat/history/{session_id}` | GET | Get conversation history | `session_id`, `limit` |
| `/health/enhanced` | GET | Enhanced health check | None |

### 3. ChromaDB Service (`services/shared/chroma_service.py`)

**Purpose**: Database operations for documents, conversations, and feedback.

**Key Functions**:

```python
# Document operations
chroma_service.create_document(source_url, title, content, university_id)
chroma_service.search_documents(query, embedding, n_results=5)
chroma_service.get_all_documents(university_id=None, limit=1000)

# Chat operations
chroma_service.create_chat_session(user_id)
chroma_service.create_chat_message(session_id, message_type, content, sources)
chroma_service.get_chat_messages(session_id, limit=50)

# Feedback operations
chroma_service.store_feedback(feedback_data)
chroma_service.get_all_feedback()
chroma_service.get_feedback_by_session(session_id)
```

### 4. Web Scraping Service (`services/scraping_service/`)

**Purpose**: Automated collection of Northeastern University website data.

**Components**:
- `spiders/university_spider.py`: Scrapy spider for crawling university websites
- `items.py`: Data models for scraped content
- `pipelines.py`: Data processing pipelines

**Usage**:

```bash
# Navigate to scraping service
cd services/scraping_service

# Run spider with specific URLs
scrapy crawl university -a university_urls="https://northeastern.edu,https://catalog.northeastern.edu"

# Run with all Northeastern URLs
scrapy crawl university -a university_urls="$(cat ../../northeastern_urls.txt | tr '\n' ',')"
```

### 5. Frontend (`frontend/`)

**Purpose**: User interface for interacting with the chatbot.

**Features**:
- Northeastern University branding
- Real-time chat interface
- Confidence indicators
- Source attribution
- Feedback collection
- Responsive design

## 📚 API Documentation

### Chat Endpoint

**POST** `/chat`

Generate a response with confidence scoring and filtering.

**Request Body**:
```json
{
  "question": "What is the tuition cost for Northeastern University?",
  "session_id": "optional_session_id"
}
```

**Response**:
```json
{
  "answer": "The tuition cost for Northeastern University varies by program...",
  "sources": [
    {
      "title": "Tuition and Fees",
      "url": "https://studentfinance.northeastern.edu/billing-payments/tuition-and-fees/",
      "similarity": 0.85,
      "search_type": "hybrid"
    }
  ],
  "confidence": 0.75,
  "session_id": "session_id",
  "should_show": true,
  "feedback_requested": false
}
```

### Feedback Endpoint

**POST** `/feedback`

Submit user feedback for answer quality.

**Request Body**:
```json
{
  "session_id": "user_session_123",
  "question": "What is the tuition cost?",
  "answer": "The tuition is approximately $54,676...",
  "rating": 4,
  "feedback_text": "Good information but could be more specific"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Feedback submitted successfully"
}
```

### Analytics Endpoint

**GET** `/feedback/analytics`

Get comprehensive feedback analytics.

**Response**:
```json
{
  "total_feedback": 25,
  "average_rating": 3.8,
  "confidence_correlation": 0.65,
  "common_issues": [
    {
      "issue": "no_information",
      "count": 5,
      "percentage": 20.0
    }
  ],
  "improvement_suggestions": [
    "Consider expanding knowledge base with more specific Northeastern information"
  ],
  "recent_feedback": [...]
}
```

## 💡 Usage Examples

### 1. Basic Chat Interaction

```python
import requests

# Send a question
response = requests.post("http://localhost:8001/chat", json={
    "question": "What is Northeastern University?",
    "session_id": "user_123"
})

data = response.json()
print(f"Answer: {data['answer']}")
print(f"Confidence: {data['confidence']:.2%}")
print(f"Should Show: {data['should_show']}")
```

### 2. Submit Feedback

```python
# Submit feedback
feedback_response = requests.post("http://localhost:8001/feedback", json={
    "session_id": "user_123",
    "question": "What is Northeastern University?",
    "answer": data['answer'],
    "rating": 5,
    "feedback_text": "Excellent overview!"
})
```

### 3. Get Analytics

```python
# Get feedback analytics
analytics = requests.get("http://localhost:8001/feedback/analytics").json()
print(f"Average Rating: {analytics['average_rating']}/5")
print(f"Total Feedback: {analytics['total_feedback']}")
```

### 4. Document Search

```python
# Search for documents
search_response = requests.get("http://localhost:8001/search", params={
    "query": "admission requirements",
    "k": 5
})

documents = search_response.json()['documents']
for doc in documents:
    print(f"Title: {doc['title']}")
    print(f"Similarity: {doc['similarity']:.3f}")
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. API Server Won't Start

**Error**: `[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8001)`

**Solution**:
```bash
# Check if port is in use
netstat -ano | findstr :8001

# Kill processes using the port
taskkill /f /im python.exe
taskkill /f /im python3.9.exe

# Restart the system
python start_system.py
```

#### 2. Ollama Connection Issues

**Error**: `Error with local LLM: Connection refused`

**Solution**:
```bash
# Start Ollama server
ollama serve

# In another terminal, check if model is available
ollama list

# Pull model if not available
ollama pull llama2:7b
```

#### 3. ChromaDB Connection Issues

**Error**: `ChromaDB failed to start`

**Solution**:
```bash
# Check if ChromaDB is running
curl http://localhost:8000/api/v1/heartbeat

# Start ChromaDB manually
chroma run --host localhost --port 8000
```

#### 4. Import Errors

**Error**: `ImportError: attempted relative import with no known parent package`

**Solution**:
```bash
# Run from correct directory
cd services/chat_service
python -m uvicorn api:app --host 0.0.0.0 --port 8001
```

#### 5. Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'tokenizers'`

**Solution**:
```bash
# Activate correct environment
env_py3.9\Scripts\activate

# Install missing package
pip install tokenizers

# Or reinstall all requirements
pip install -r requirements.txt --force-reinstall
```

### Health Checks

#### API Health Check
```bash
curl http://localhost:8001/health/enhanced
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Enhanced University Chatbot API is running",
  "features": {
    "hybrid_search": "enabled",
    "query_expansion": "enabled",
    "confidence_scoring": "enabled",
    "confidence_filtering": "enabled",
    "user_feedback": "enabled",
    "feedback_analytics": "enabled"
  }
}
```

#### ChromaDB Health Check
```bash
curl http://localhost:8000/api/v1/heartbeat
```

#### Ollama Health Check
```bash
curl http://localhost:11434/api/tags
```

### Log Analysis

#### API Logs
Check for errors in the API server output:
- Look for `[ERROR]` messages
- Check for import errors
- Verify model loading

#### ChromaDB Logs
Monitor ChromaDB for:
- Connection issues
- Collection creation errors
- Query performance

#### Frontend Logs
Check browser console for:
- API connection errors
- JavaScript errors
- CORS issues

## 🧪 Testing

### Run All Tests

```bash
# Test enhanced features
python test_enhanced_system.py

# Test confidence and feedback
python test_confidence_and_feedback.py

# Test basic system
python test_system.py
```

### Individual Component Tests

```bash
# Test ChromaDB service
python -c "from services.shared.chroma_service import test_chroma_service; test_chroma_service()"

# Test API endpoints
python test_confidence_and_feedback.py

# Test scraping
cd services/scraping_service
scrapy crawl university -a university_urls="https://northeastern.edu"
```

## 🔄 Development

### Project Structure

```
university_chatbot/
├── services/
│   ├── chat_service/
│   │   ├── api.py                    # FastAPI server
│   │   ├── enhanced_rag_chatbot.py   # Core AI engine
│   │   └── __init__.py
│   ├── scraping_service/
│   │   ├── spiders/
│   │   │   └── university_spider.py  # Web scraper
│   │   ├── items.py                  # Data models
│   │   ├── pipelines.py              # Data processing
│   │   └── scrapy.cfg
│   ├── processing_service/
│   │   ├── embeddings_generator.py   # Embedding generation
│   │   └── tasks.py                  # Background tasks
│   └── shared/
│       ├── chroma_service.py         # Database operations
│       ├── config.py                 # Configuration
│       ├── database.py               # Database setup
│       └── models.py                 # Data models
├── frontend/
│   ├── index.html                    # Main page
│   ├── script.js                     # Frontend logic
│   └── style.css                     # Styling
├── start_system.py                   # System startup
├── requirements.txt                  # Dependencies
├── northeastern_urls.txt             # URLs to scrape
└── README.md                         # This file
```

### Adding New Features

#### 1. New API Endpoint

```python
# In services/chat_service/api.py
@app.get("/new-endpoint")
async def new_endpoint():
    """New endpoint description"""
    try:
        # Your logic here
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2. New Chatbot Feature

```python
# In services/chat_service/enhanced_rag_chatbot.py
def new_feature(self, parameter):
    """New feature description"""
    try:
        # Implementation
        return result
    except Exception as e:
        print(f"Error in new feature: {e}")
        return None
```

#### 3. New Database Model

```python
# In services/shared/models.py
@dataclass
class NewModel:
    """New data model"""
    id: Optional[str] = None
    field1: str = ""
    field2: int = 0
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
```

### Code Style

- Follow PEP 8 for Python code
- Use type hints for function parameters and return values
- Add docstrings for all functions and classes
- Handle exceptions gracefully with proper error messages
- Use meaningful variable and function names

## 🚀 Deployment

### Local Development

```bash
# Development mode with auto-reload
cd services/chat_service
uvicorn api:app --host 0.0.0.0 --port 8001 --reload
```

### Production Deployment

#### Using Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["uvicorn", "services.chat_service.api:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### Using Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  chromadb:
    image: chromadb/chroma
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma

  api:
    build: .
    ports:
      - "8001:8001"
    depends_on:
      - chromadb
    environment:
      - CHROMA_HOST=chromadb
      - CHROMA_PORT=8000

  frontend:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./frontend:/usr/share/nginx/html

volumes:
  chroma_data:
```

### Environment Variables

```env
# Production environment variables
CHROMA_HOST=your-chromadb-host
CHROMA_PORT=8000
API_HOST=0.0.0.0
API_PORT=8001
FRONTEND_PORT=8080
LOG_LEVEL=INFO
OLLAMA_HOST=your-ollama-host
OLLAMA_PORT=11434
```

## 📊 Monitoring and Analytics

### System Metrics

- **API Response Time**: Monitor `/health/enhanced` endpoint
- **Confidence Distribution**: Track confidence scores over time
- **User Satisfaction**: Monitor feedback ratings
- **Error Rates**: Track API error responses

### Performance Optimization

- **ChromaDB**: Optimize collection size and query performance
- **LLM**: Monitor Ollama response times
- **API**: Use connection pooling and caching
- **Frontend**: Optimize bundle size and loading times

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help

1. **Check the documentation**: This README and other .md files
2. **Run health checks**: Use the provided health check endpoints
3. **Check logs**: Monitor system output for error messages
4. **Test components**: Use the provided test scripts

### Common Commands Reference

```bash
# System management
python start_system.py                    # Start all services
python start_system.bat                   # Windows batch startup

# Testing
python test_enhanced_system.py            # Test enhanced features
python test_confidence_and_feedback.py    # Test confidence & feedback
python test_system.py                     # Test basic functionality

# Database management
python reset_chromadb.py                  # Reset ChromaDB
python purge_to_northeastern_only.py      # Keep only Northeastern data

# Scraping
cd services/scraping_service
scrapy crawl university -a university_urls="https://northeastern.edu"

# API testing
curl http://localhost:8001/health/enhanced
curl -X POST http://localhost:8001/chat -H "Content-Type: application/json" -d '{"question": "What is Northeastern?"}'
```

---

**🎓 Northeastern University Chatbot** - Providing intelligent, reliable information about Northeastern University with advanced AI capabilities and continuous learning through user feedback. 