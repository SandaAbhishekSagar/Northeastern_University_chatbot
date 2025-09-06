"""
Fixed API for Northeastern University Chatbot
- Uses the fixed chatbot with ChatGPT integration
- Properly handles URLs and sources
- Enhanced error handling
- Works with both ChromaDB and Pinecone
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import uuid
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the fixed chatbot
from services.chat_service.fixed_chatbot import chatbot
from services.shared.database import get_database_type, get_pinecone_count

# Initialize FastAPI app
app = FastAPI(
    title="Fixed Northeastern University Chatbot API",
    description="ChatGPT-powered chatbot with proper URL handling",
    version="2.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    session_id: str
    response_time: float
    documents_analyzed: int

class HealthResponse(BaseModel):
    status: str
    message: str
    database_type: str
    document_count: int
    features: Dict[str, str]

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    try:
        # Get document count
        db_type = get_database_type()
        if db_type == "pinecone":
            doc_count = get_pinecone_count()
        else:
            # For ChromaDB, we'll estimate or get from collection
            doc_count = 76428  # Fallback estimate
        
        return HealthResponse(
            status="healthy",
            message="Fixed Northeastern University Chatbot API is running",
            database_type=db_type,
            document_count=doc_count,
            features={
                "chatgpt_integration": "enabled",
                "url_handling": "fixed",
                "source_attribution": "enabled",
                "confidence_scoring": "enabled",
                "fallback_mode": "enabled"
            }
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            message=f"System error: {str(e)}",
            database_type="unknown",
            document_count=0,
            features={}
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with fixed URL handling"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Process the question using the fixed chatbot
        result = chatbot.chat(request.question, session_id)
        
        return ChatResponse(
            answer=result['answer'],
            sources=result['sources'],
            confidence=result['confidence'],
            session_id=session_id,
            response_time=result['response_time'],
            documents_analyzed=result['documents_analyzed']
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/search")
async def search_documents(query: str, k: int = 5):
    """Search for similar documents"""
    try:
        documents = chatbot.search_documents(query, k)
        
        # Format results for API response
        results = []
        for doc in documents:
            metadata = doc.get('metadata', {})
            result = {
                'id': doc['id'],
                'title': metadata.get('title', 'Document'),
                'url': metadata.get('source_url', '') or metadata.get('url', ''),
                'content': doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'],
                'score': doc.get('score', 0.0)
            }
            results.append(result)
        
        return {"documents": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@app.get("/documents")
async def get_document_stats():
    """Get document statistics"""
    try:
        db_type = get_database_type()
        
        if db_type == "pinecone":
            doc_count = get_pinecone_count()
        else:
            # For ChromaDB, we'll use an estimate
            doc_count = 76428  # Based on your system status
        
        return {
            "total_documents": doc_count,
            "total_universities": 1,
            "database_type": db_type,
            "status": "active"
        }
        
    except Exception as e:
        return {
            "total_documents": 76428,
            "total_universities": 1,
            "database_type": "unknown",
            "status": "error",
            "error": str(e)
        }

@app.get("/health/enhanced")
async def enhanced_health():
    """Enhanced health check with system status"""
    try:
        # Test basic functionality
        test_result = chatbot.chat("test", "health_check")
        
        return {
            "status": "healthy",
            "message": "Fixed Northeastern University Chatbot API is running",
            "database_type": get_database_type(),
            "features": {
                "chatgpt_integration": "enabled" if chatbot.llm else "fallback",
                "url_handling": "fixed",
                "source_attribution": "enabled",
                "confidence_scoring": "enabled",
                "fallback_mode": "enabled"
            },
            "test": {
                "chat_functionality": "working" if test_result else "error"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"System error: {str(e)}",
            "database_type": "unknown",
            "features": {
                "chatgpt_integration": "unknown",
                "url_handling": "unknown",
                "source_attribution": "unknown",
                "confidence_scoring": "unknown",
                "fallback_mode": "unknown"
            }
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Fixed Northeastern University Chatbot API...")
    print("📊 Database type:", get_database_type())
    print("🤖 ChatGPT integration:", "enabled" if chatbot.llm else "fallback mode")
    uvicorn.run(app, host="0.0.0.0", port=8001)
