#!/usr/bin/env python3
"""
OpenAI RAG API Server for University Chatbot
Provides RESTful API endpoints for the OpenAI-based RAG pipeline
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from services.chat_service.openai_rag_chatbot import OpenAIUniversityRAGChatbot
    from services.chat_service.unified_rag_api import UnifiedRAGAPI, RAGProvider
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback imports
    try:
        from openai_rag_chatbot import OpenAIUniversityRAGChatbot
        from unified_rag_api import UnifiedRAGAPI, RAGProvider
    except ImportError:
        print("Could not import OpenAI RAG modules. Please ensure they are properly installed.")
        raise

# Initialize FastAPI app
app = FastAPI(
    title="OpenAI University Chatbot API", 
    version="1.0.0",
    description="RESTful API for OpenAI-based RAG pipeline"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI RAG chatbot
try:
    # Get OpenAI API key from environment
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("[WARNING] OPENAI_API_KEY not found in environment variables")
        print("[INFO] You can set it with: export OPENAI_API_KEY='your-api-key'")
        openai_api_key = None
    
    # Initialize the unified RAG API with OpenAI provider
    rag_api = UnifiedRAGAPI(
        provider=RAGProvider.OPENAI,
        model_name="o4-mini-2025-04-16-2024-07-18",
        openai_api_key=openai_api_key
    )
    
    print(f"[OK] OpenAI RAG API initialized successfully")
    print(f"[INFO] Using model: {rag_api.model_name}")
    print(f"[INFO] Provider: {rag_api.provider.value}")
    
except Exception as e:
    print(f"[ERROR] Failed to initialize OpenAI RAG API: {e}")
    rag_api = None

# Pydantic models
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    use_openai: bool = True  # Default to OpenAI

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None
    session_id: str
    response_time: Optional[float] = None
    documents_analyzed: Optional[int] = None
    model_used: Optional[str] = None
    provider: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    provider: str
    model: str
    api_key_configured: bool

class StatsResponse(BaseModel):
    total_documents: int
    total_universities: int
    total_conversations: int
    average_response_time: float
    provider: str
    model: str

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health information"""
    api_key_configured = bool(os.getenv('OPENAI_API_KEY'))
    
    return HealthResponse(
        status="healthy" if rag_api else "unhealthy",
        message="OpenAI University Chatbot API is running",
        provider="openai",
        model=rag_api.model_name if rag_api else "unknown",
        api_key_configured=api_key_configured
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint using OpenAI RAG pipeline"""
    try:
        if not rag_api:
            raise HTTPException(status_code=500, detail="OpenAI RAG API not initialized")
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        print(f"[OPENAI API] Processing question: {request.question[:50]}...")
        print(f"[OPENAI API] Session ID: {session_id}")
        print(f"[OPENAI API] Provider: {rag_api.provider.value}")
        
        # Generate response using OpenAI RAG pipeline
        response = rag_api.generate_response(
            question=request.question,
            session_id=session_id
        )
        
        # Add session ID and provider info to response
        response['session_id'] = session_id
        response['provider'] = rag_api.provider.value
        response['model_used'] = rag_api.model_name
        
        print(f"[OPENAI API] Response generated in {response.get('response_time', 0):.2f}s")
        print(f"[OPENAI API] Documents analyzed: {response.get('documents_analyzed', 0)}")
        print(f"[OPENAI API] Confidence: {response.get('confidence', 0):.2f}")
        
        return ChatResponse(**response)
        
    except Exception as e:
        print(f"[OPENAI API] Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 10):
    """Get conversation history for a session"""
    try:
        if not rag_api:
            raise HTTPException(status_code=500, detail="OpenAI RAG API not initialized")
        
        history = rag_api.chatbot.get_conversation_history(session_id, limit)
        return {"session_id": session_id, "history": history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get OpenAI chatbot statistics"""
    try:
        if not rag_api:
            raise HTTPException(status_code=500, detail="OpenAI RAG API not initialized")
        
        # Get basic stats from the chatbot
        stats = {
            "total_documents": 0,
            "total_universities": 0,
            "total_conversations": 0,
            "average_response_time": 0.0,
            "provider": rag_api.provider.value,
            "model": rag_api.model_name
        }
        
        # Try to get more detailed stats if available
        try:
            # This would depend on your specific implementation
            # stats.update(rag_api.chatbot.get_statistics())
            pass
        except:
            pass
        
        return StatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    api_key_configured = bool(os.getenv('OPENAI_API_KEY'))
    
    return HealthResponse(
        status="healthy" if rag_api else "unhealthy",
        message="OpenAI RAG API health check",
        provider="openai",
        model=rag_api.model_name if rag_api else "unknown",
        api_key_configured=api_key_configured
    )

@app.post("/switch-provider")
async def switch_provider(provider: str):
    """Switch between RAG providers (OpenAI/Ollama)"""
    try:
        if provider.lower() == "openai":
            new_provider = RAGProvider.OPENAI
        elif provider.lower() == "ollama":
            new_provider = RAGProvider.OLLAMA
        else:
            raise HTTPException(status_code=400, detail="Invalid provider. Use 'openai' or 'ollama'")
        
        rag_api.switch_provider(new_provider)
        
        return {
            "message": f"Switched to {provider} provider",
            "provider": rag_api.provider.value,
            "model": rag_api.model_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error switching provider: {str(e)}")

@app.get("/provider-info")
async def get_provider_info():
    """Get current provider information"""
    try:
        if not rag_api:
            raise HTTPException(status_code=500, detail="RAG API not initialized")
        
        return rag_api.get_provider_info()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting provider info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    print("[START] Starting OpenAI University Chatbot API Server")
    print(f"[INFO] Provider: OpenAI")
    print(f"[INFO] Model: {rag_api.model_name if rag_api else 'Unknown'}")
    print(f"[INFO] API Key configured: {bool(os.getenv('OPENAI_API_KEY'))}")
    print(f"[URL] API URL: http://localhost:8001")
    print(f"[STOP] Press Ctrl+C to stop the server")
    print("-" * 60)
    
    uvicorn.run(
        "openai_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 