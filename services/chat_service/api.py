from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
try:
    from .enhanced_rag_chatbot import EnhancedUniversityRAGChatbot
except ImportError:
    from enhanced_rag_chatbot import EnhancedUniversityRAGChatbot

# Initialize FastAPI app
app = FastAPI(title="Enhanced University Chatbot API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize enhanced chatbot
chatbot = EnhancedUniversityRAGChatbot()

# Pydantic models
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    session_id: str
    should_show: bool = True
    feedback_requested: bool = False

class FeedbackRequest(BaseModel):
    session_id: str
    question: str
    answer: str
    rating: int  # 1-5 scale
    feedback_text: Optional[str] = ""

class HealthResponse(BaseModel):
    status: str
    message: str

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(status="healthy", message="University Chatbot API is running")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with confidence filtering"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Generate enhanced response
        response = chatbot.generate_enhanced_response(request.question, session_id)
        
        return ChatResponse(
            answer=response['answer'],
            sources=response['sources'],
            confidence=response['confidence'],
            session_id=session_id,
            should_show=response.get('should_show', True),
            feedback_requested=response.get('feedback_requested', False)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 10):
    """Get conversation history for a session"""
    try:
        history = chatbot.get_conversation_history(session_id, limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

@app.get("/search")
async def search_documents(query: str, k: int = 5):
    """Search for similar documents using enhanced hybrid search"""
    try:
        documents = chatbot.hybrid_search(query, k)
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@app.get("/search/semantic")
async def semantic_search(query: str, k: int = 5):
    """Semantic search only"""
    try:
        documents = chatbot.semantic_search(query, k)
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in semantic search: {str(e)}")

@app.get("/search/expand")
async def expand_query(query: str):
    """Expand a query using synonyms and related terms"""
    try:
        expanded_queries = chatbot.expand_query(query)
        return {"original_query": query, "expanded_queries": expanded_queries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error expanding query: {str(e)}")

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for answer quality"""
    try:
        # Validate rating
        if not 1 <= request.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Store feedback
        chatbot.store_user_feedback(
            session_id=request.session_id,
            question=request.question,
            answer=request.answer,
            rating=request.rating,
            feedback_text=request.feedback_text or ""
        )
        
        return {"status": "success", "message": "Feedback submitted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@app.get("/feedback/analytics")
async def get_feedback_analytics():
    """Get analytics on user feedback for system improvement"""
    try:
        analytics = chatbot.get_feedback_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analytics: {str(e)}")

@app.get("/health/enhanced")
async def enhanced_health():
    """Enhanced health check with system status"""
    try:
        # Test basic functionality
        test_query = "Northeastern University"
        expanded = chatbot.expand_query(test_query)
        
        return {
            "status": "healthy",
            "message": "Enhanced University Chatbot API is running",
            "features": {
                "hybrid_search": "enabled",
                "query_expansion": "enabled",
                "confidence_scoring": "enabled",
                "conversation_history": "enabled",
                "confidence_filtering": "enabled",
                "user_feedback": "enabled",
                "feedback_analytics": "enabled"
            },
            "test": {
                "query_expansion_working": len(expanded) > 1
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"System error: {str(e)}",
            "features": {
                "hybrid_search": "unknown",
                "query_expansion": "unknown",
                "confidence_scoring": "unknown",
                "conversation_history": "unknown",
                "confidence_filtering": "unknown",
                "user_feedback": "unknown",
                "feedback_analytics": "unknown"
            }
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)