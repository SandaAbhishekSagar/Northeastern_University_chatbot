"""
Enhanced CPU API for University Chatbot - Optimized for Cloud Deployment
Features:
- CPU-optimized for cloud platforms
- Reduced memory usage
- Faster startup times
- Optimized for serverless environments
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

from services.chat_service.enhanced_gpu_chatbot import EnhancedGPUUniversityRAGChatbot

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced CPU Northeastern University Chatbot API",
    description="Cloud-optimized chatbot API with CPU acceleration",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize enhanced CPU chatbot
print("[ENHANCED CPU API] Initializing enhanced CPU chatbot...")
enhanced_cpu_chatbot = EnhancedGPUUniversityRAGChatbot()
print("[ENHANCED CPU API] Enhanced CPU chatbot initialized successfully!")

# Request/Response models
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    response_time: float
    session_id: str
    device: str

class HealthResponse(BaseModel):
    status: str
    message: str
    device: str
    features: Dict[str, str]

@app.get("/health/enhanced", response_model=HealthResponse)
async def enhanced_health_check():
    """Enhanced health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Enhanced CPU Northeastern University Chatbot API is running",
        device=enhanced_cpu_chatbot.embedding_manager.device,
        features={
            "gpu_acceleration": "disabled",
            "cpu_optimization": "enabled",
            "cloud_optimized": "enabled"
        }
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Enhanced chat endpoint with CPU optimization"""
    start_time = time.time()
    
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        result = enhanced_cpu_chatbot.process_question(
            request.question,
            session_id=session_id,
            max_documents=8,
            use_gpu=False
        )
        
        response_time = time.time() - start_time
        
        return ChatResponse(
            answer=result['answer'],
            sources=result['sources'],
            confidence=result['confidence'],
            response_time=response_time,
            session_id=session_id,
            device=enhanced_cpu_chatbot.embedding_manager.device
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Enhanced CPU Northeastern University Chatbot API",
        "version": "2.0.0",
        "status": "running",
        "device": enhanced_cpu_chatbot.embedding_manager.device
    } 