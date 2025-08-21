"""
Enhanced GPU API for University Chatbot - Maximum Accuracy with GPU Acceleration
Features:
- GPU acceleration for embeddings and LLM
- 10 document analysis for comprehensive coverage
- Query expansion and hybrid search
- Conversation history integration
- Response time target: 5-15 seconds with GPU
- VERSION: 2.1.0 - Improved fallback response generation
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import uuid
from datetime import datetime

# Import the enhanced chatbot
from services.chat_service.enhanced_gpu_chatbot import EnhancedGPUChatbot

# Import database functions
from services.shared.database import (
    get_database_type, get_collection, add_documents_to_pinecone, 
    query_pinecone, get_pinecone_count, init_db
)

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced GPU Northeastern University Chatbot API v2.1.0",
    description="Advanced RAG chatbot with GPU acceleration and multiple database support - FIXED VERSION",
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

# Initialize chatbot
print("[ENHANCED GPU API] Initializing enhanced GPU chatbot...")
chatbot = EnhancedGPUChatbot()
print("[ENHANCED GPU API] Enhanced GPU chatbot initialized successfully!")

# Initialize database
print("[ENHANCED GPU API] Initializing database...")
init_db()
print("[ENHANCED GPU API] Database initialized successfully!")

# Pydantic models
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    response_time: float
    search_time: float
    documents_analyzed: int
    session_id: str
    device: str

class HealthResponse(BaseModel):
    status: str
    message: str
    response_time: float
    device: str
    features: Dict[str, Any]

class DocumentsResponse(BaseModel):
    total_documents: int
    total_universities: int
    documents_analyzed_per_query: int
    context_size: str
    status: str

# Health check endpoint
@app.get("/health/enhanced", response_model=HealthResponse)
async def health_check():
    start_time = time.time()
    
    # Check database connection
    db_type = get_database_type()
    
    # Get document count
    try:
        if db_type == "pinecone":
            doc_count = get_pinecone_count()
        else:
            collection = get_collection('documents')
            result = collection.get()
            doc_count = len(result.get('ids', [])) if result else 0
    except Exception as e:
        print(f"Error getting document count: {e}")
        doc_count = 0
    
    response_time = time.time() - start_time
    
    features = {
        "gpu_acceleration": chatbot.device == "cuda",
        "llm_available": chatbot.llm_type != "fallback",
        "database_type": db_type,
        "document_count": doc_count,
        "query_expansion": True,  # Always available
        "hybrid_search": True,  # Always available
        "confidence_scoring": True  # Always available
    }
    
    # Calculate active features count
    active_features = sum([
        features["gpu_acceleration"],
        features["llm_available"], 
        features["query_expansion"],
        features["hybrid_search"]
    ])
    
    features["active_features"] = active_features
    features["total_features"] = 4
    
    # Debug print for Railway deployment verification
    print(f"[ENHANCED GPU API] Enhanced Features: {active_features}/4 Active")
    print(f"[ENHANCED GPU API] GPU Acceleration: {features['gpu_acceleration']}")
    print(f"[ENHANCED GPU API] LLM Available: {features['llm_available']}")
    print(f"[ENHANCED GPU API] Query Expansion: {features['query_expansion']}")
    print(f"[ENHANCED GPU API] Hybrid Search: {features['hybrid_search']}")
    
    return HealthResponse(
        status="healthy",
        message="Enhanced GPU Northeastern University Chatbot API is running",
        response_time=response_time,
        device=chatbot.device,
        features=features
    )

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        print(f"[ENHANCED GPU API] Processing question: {request.question}...")
        
        # Generate session ID if not provided
        session_id = request.session_id or f"session_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}"
        print(f"[ENHANCED GPU API] Session ID: {session_id}")
        print(f"[ENHANCED GPU API] Device: {chatbot.device}")
        
        # Get response from chatbot
        response = chatbot.chat(request.question, session_id)
        
        return ChatResponse(**response)
        
    except Exception as e:
        print(f"[ENHANCED GPU API] Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Documents endpoint
@app.get("/documents", response_model=DocumentsResponse)
async def get_documents_info():
    try:
        db_type = get_database_type()
        
        # Get document count
        if db_type == "pinecone":
            total_documents = get_pinecone_count()
        else:
            collection = get_collection('documents')
            result = collection.get()
            total_documents = len(result.get('ids', [])) if result else 0
        
        return DocumentsResponse(
            total_documents=total_documents,
            total_universities=1,  # Northeastern University
            documents_analyzed_per_query=chatbot.documents_to_analyze,
            context_size=chatbot.context_size,
            status="loaded"
        )
        
    except Exception as e:
        print(f"Error getting count for collection documents: {e}")
        return DocumentsResponse(
            total_documents=0,
            total_universities=1,
            documents_analyzed_per_query=chatbot.documents_to_analyze,
            context_size=chatbot.context_size,
            status="error"
        )

# Upload documents endpoint (for Pinecone)
@app.post("/upload-documents")
async def upload_documents(data: Dict[str, Any]):
    try:
        db_type = get_database_type()
        
        if db_type != "pinecone":
            raise HTTPException(status_code=400, detail="Upload endpoint only available for Pinecone")
        
        documents = data.get('documents', [])
        metadatas = data.get('metadatas', [])
        ids = data.get('ids', [])
        
        if not documents or not ids:
            raise HTTPException(status_code=400, detail="Documents and IDs are required")
        
        # Add documents to Pinecone
        uploaded_count = add_documents_to_pinecone(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            collection_name="documents"
        )
        
        return {
            "status": "success",
            "uploaded": uploaded_count,
            "message": f"Successfully uploaded {uploaded_count} documents to Pinecone"
        }
        
    except Exception as e:
        print(f"Error uploading documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Enhanced GPU Northeastern University Chatbot API",
        "version": "2.0.0",
        "database": get_database_type(),
        "device": chatbot.device,
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 