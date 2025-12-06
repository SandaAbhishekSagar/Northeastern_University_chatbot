"""
Enhanced OpenAI API for University Chatbot - Maximum Accuracy with GPT-4
Features:
- OpenAI GPT-4/GPT-3.5 for answer generation
- GPU acceleration for embeddings
- 10 document analysis for comprehensive coverage
- Query expansion and hybrid search
- Conversation history integration
- Response time target: 3-10 seconds with GPT-4
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import uuid
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.chat_service.enhanced_openai_chatbot import EnhancedOpenAIUniversityRAGChatbot

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced OpenAI Northeastern University Chatbot API",
    description="Maximum accuracy chatbot API with OpenAI GPT and 10 document analysis",
    version="2.0.0"
)

# Add CORS middleware with security restrictions
# Get allowed origins from environment variable (comma-separated)
# IMPORTANT: Add your Vercel frontend URL to ALLOWED_ORIGINS in Railway environment variables
# Example: https://your-project.vercel.app,https://northeasternuniversitychatbot-production.up.railway.app
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "https://northeastern-university-chatbot.vercel.app,http://localhost:3000,http://localhost:8080,https://northeasternuniversitychatbot-production.up.railway.app"
).split(",")

# Clean and validate origins
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()]

# Log allowed origins for debugging (without exposing full URLs)
print(f"[CORS] Configured {len(ALLOWED_ORIGINS)} allowed origin(s)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Restricted to specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only allow necessary methods
    allow_headers=["Content-Type", "Authorization"],  # Only allow necessary headers
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Initialize enhanced OpenAI chatbot
print("[ENHANCED OPENAI API] Initializing enhanced OpenAI chatbot...")
try:
    enhanced_openai_chatbot = EnhancedOpenAIUniversityRAGChatbot()
    print("[ENHANCED OPENAI API] Enhanced OpenAI chatbot initialized successfully!")
except Exception as e:
    print(f"[ENHANCED OPENAI API] Error initializing chatbot: {e}")
    print("[ENHANCED OPENAI API] Please ensure OPENAI_API_KEY is set in environment or .env file")
    enhanced_openai_chatbot = None

# Request/Response models
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    response_time: float
    search_time: float
    llm_time: float
    context_time: float
    session_id: str
    documents_analyzed: int
    device: str
    query_expansions: bool
    model: str

class HealthResponse(BaseModel):
    status: str
    message: str
    response_time: float
    model: str
    device: str
    features: Dict[str, str]

class StatsResponse(BaseModel):
    status: str
    chatbot_type: str
    model: str
    target_response_time: str
    documents_analyzed: int
    total_documents: int
    device: str
    features: List[str]

class ReviewRequest(BaseModel):
    session_id: str
    rating: int
    feedback_type: str = "general"
    feedback_text: Optional[str] = ""
    email: Optional[str] = None
    timestamp: str
    user_agent: Optional[str] = None
    page_url: Optional[str] = None

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    start_time = time.time()
    response_time = time.time() - start_time
    
    if not enhanced_openai_chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized. Check OpenAI API key configuration.")
    
    return HealthResponse(
        status="healthy",
        message="Enhanced OpenAI Northeastern University Chatbot API is running",
        response_time=response_time,
        model=enhanced_openai_chatbot.model_name,
        device=enhanced_openai_chatbot.embedding_manager.device,
        features={
            "llm_provider": "OpenAI",
            "gpu_embeddings": "enabled" if enhanced_openai_chatbot.embedding_manager.device == 'cuda' else "disabled",
            "query_expansion": "enabled",
            "hybrid_search": "enabled",
            "conversation_history": "enabled"
        }
    )

@app.get("/health/enhanced", response_model=HealthResponse)
async def enhanced_health_check():
    """Enhanced health check for frontend compatibility"""
    start_time = time.time()
    response_time = time.time() - start_time
    
    if not enhanced_openai_chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized. Check OpenAI API key configuration.")
    
    return HealthResponse(
        status="healthy",
        message="Enhanced OpenAI Northeastern University Chatbot API is running",
        response_time=response_time,
        model=enhanced_openai_chatbot.model_name,
        device=enhanced_openai_chatbot.embedding_manager.device,
        features={
            "llm_provider": "OpenAI",
            "gpu_embeddings": "enabled" if enhanced_openai_chatbot.embedding_manager.device == 'cuda' else "disabled",
            "query_expansion": "enabled",
            "hybrid_search": "enabled",
            "conversation_history": "enabled"
        }
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Enhanced OpenAI chat endpoint with maximum accuracy"""
    try:
        if not enhanced_openai_chatbot:
            raise HTTPException(
                status_code=500, 
                detail="Service temporarily unavailable. Please try again later."
            )
        
        # Validate and sanitize input
        sanitized_question = sanitize_question(request.question)
        if not sanitized_question or len(sanitized_question) < 3:
            raise HTTPException(
                status_code=400, 
                detail="Please provide a valid question (at least 3 characters)."
            )
        
        # Validate session ID format
        import re
        if request.session_id:
            session_id = re.sub(r'[^a-zA-Z0-9\-_]', '', request.session_id)[:100]
            if not session_id:
                session_id = str(uuid.uuid4())
        else:
            session_id = str(uuid.uuid4())
        
        print(f"[ENHANCED OPENAI API] Processing question: {sanitized_question[:50]}...")
        print(f"[ENHANCED OPENAI API] Session ID: {session_id[:20]}...")
        print(f"[ENHANCED OPENAI API] Model: {enhanced_openai_chatbot.model_name}")
        print(f"[ENHANCED OPENAI API] Embedding Device: {enhanced_openai_chatbot.embedding_manager.device}")
        
        # Generate enhanced OpenAI response (with sanitized input)
        response = enhanced_openai_chatbot.generate_enhanced_openai_response(
            question=sanitized_question,
            session_id=session_id
        )
        
        # Add session ID to response
        response['session_id'] = session_id
        
        print(f"[ENHANCED OPENAI API] Response generated in {response['response_time']:.2f}s")
        print(f"[ENHANCED OPENAI API] Documents analyzed: {response['documents_analyzed']}")
        print(f"[ENHANCED OPENAI API] Confidence: {response['confidence']:.2f}")
        
        return ChatResponse(**response)
        
    except HTTPException:
        raise
    except Exception as e:
        # Log full error for debugging (server-side only)
        print(f"[ENHANCED OPENAI API] Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        # Return generic error message to client (don't leak system details)
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while processing your request. Please try again later."
        )

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get enhanced OpenAI chatbot statistics"""
    try:
        if not enhanced_openai_chatbot:
            raise HTTPException(status_code=500, detail="Chatbot not initialized.")
        
        # Get actual document count from ChromaDB
        total_documents = 0
        try:
            from services.shared.chroma_service import ChromaService
            chroma_service = ChromaService()
            total_documents = chroma_service.get_collection_count('documents')
        except Exception as e:
            print(f"[ENHANCED OPENAI API] Error getting document count: {e}")
            total_documents = 80000  # Updated for new consolidated database
        
        return StatsResponse(
            status="operational",
            chatbot_type="enhanced_openai",
            model=enhanced_openai_chatbot.model_name,
            target_response_time="3-10 seconds (with GPT-4)",
            documents_analyzed=6,
            total_documents=total_documents,
            device=enhanced_openai_chatbot.embedding_manager.device,
            features=[
                f"OpenAI {enhanced_openai_chatbot.model_name}",
                "GPU-accelerated embeddings (automatic detection)",
                "6 document analysis",
                "Query expansion (3 variations)",
                "Hybrid search (semantic + keyword)",
                "Reranking and deduplication",
                "Conversation history integration",
                "Multi-factor confidence scoring",
                "1,200 characters per document",
                "~7,200 total context characters"
            ]
        )
    except Exception as e:
        print(f"[ENHANCED OPENAI API] Error in stats endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/documents")
async def get_document_count():
    """Get document count for frontend compatibility"""
    try:
        # Get actual document count from ChromaDB
        total_documents = 0
        try:
            from services.shared.chroma_service import ChromaService
            chroma_service = ChromaService()
            total_documents = chroma_service.get_collection_count('documents')
        except Exception as e:
            print(f"[ENHANCED OPENAI API] Error getting document count: {e}")
            total_documents = 80000  # Updated for new consolidated database
        
        return {
            "total_documents": total_documents,
            "total_universities": 1,  # Northeastern only
            "documents_analyzed_per_query": 6,
            "context_size": "~7,200 characters",
            "status": "loaded"
        }
    except Exception as e:
        print(f"[ENHANCED OPENAI API] Error in documents endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/search")
async def search_documents(request: ChatRequest):
    """Search documents endpoint for frontend compatibility"""
    try:
        if not enhanced_openai_chatbot:
            raise HTTPException(status_code=500, detail="Chatbot not initialized.")
        
        # Use the enhanced OpenAI chatbot's search functionality
        documents = enhanced_openai_chatbot.hybrid_search(request.question, k=10)
        
        # Format for frontend with validated URLs
        formatted_docs = []
        for doc in documents:
            # Extract URL from multiple possible locations
            source_url = doc.get('source_url', '') or doc.get('url', '')
            if not source_url and isinstance(doc.get('extra_data'), dict):
                source_url = doc.get('extra_data', {}).get('source_url') or doc.get('extra_data', {}).get('url', '')
            
            # Validate URL (basic validation - ensure it starts with http/https)
            if source_url and not source_url.startswith(('http://', 'https://')):
                if source_url.startswith('/'):
                    source_url = 'https://www.northeastern.edu' + source_url
                elif '.' in source_url:
                    source_url = 'https://' + source_url
            
            formatted_docs.append({
                "title": doc.get('title', 'Document'),
                "content": doc.get('content', '')[:300] + "..." if len(doc.get('content', '')) > 300 else doc.get('content', ''),
                "url": source_url,
                "similarity": doc.get('similarity', 0.0),
                "rank": doc.get('rank', 0)
            })
        
        return {
            "query": request.question,
            "documents": formatted_docs,
            "total_found": len(formatted_docs),
            "model": enhanced_openai_chatbot.model_name,
            "device": enhanced_openai_chatbot.embedding_manager.device
        }
        
    except Exception as e:
        print(f"[ENHANCED OPENAI API] Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def sanitize_question(question: str, max_length: int = 2000) -> str:
    """Sanitize user question input to prevent injection attacks"""
    if not question:
        return ""
    
    # Remove control characters except newlines and tabs
    import re
    question = ''.join(char for char in question if ord(char) >= 32 or char in '\n\r\t')
    
    # Limit length to prevent DoS
    question = question[:max_length].strip()
    
    # Remove excessive whitespace
    question = re.sub(r'\s+', ' ', question)
    
    return question

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    import html
    text = html.escape(text)  # Escape HTML entities
    
    # Limit length
    text = text[:max_length]
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    return text.strip()

def validate_email(email: Optional[str]) -> Optional[str]:
    """Validate and sanitize email address"""
    if not email:
        return None
    
    import re
    email = email.strip().lower()
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return None
    
    # Limit length
    if len(email) > 254:  # RFC 5321 limit
        return None
    
    return email

@app.post("/review")
async def submit_review(request: ReviewRequest):
    """Submit user review/feedback with input validation"""
    try:
        # Validate rating
        if not 1 <= request.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Validate feedback type
        valid_feedback_types = ["general", "improvement", "bug", "feature", "praise"]
        if request.feedback_type not in valid_feedback_types:
            request.feedback_type = "general"
        
        # Sanitize inputs
        sanitized_feedback = sanitize_input(request.feedback_text or '', max_length=1000)
        validated_email = validate_email(request.email)
        
        # Sanitize session ID (prevent injection)
        import re
        session_id = re.sub(r'[^a-zA-Z0-9\-_]', '', request.session_id or '')[:100]
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Sanitize user agent and page URL (limit length, remove sensitive data)
        user_agent = sanitize_input(request.user_agent or '', max_length=200)
        page_url = sanitize_input(request.page_url or '', max_length=500)
        
        # Import review storage (JSON-based, not ChromaDB)
        from services.shared.review_storage import review_storage
        from datetime import datetime
        
        # Prepare review data for storage (with sanitized inputs)
        review_data = {
            'session_id': session_id,
            'rating': request.rating,
            'feedback_type': request.feedback_type,
            'feedback_text': sanitized_feedback,
            'email': validated_email,  # Only store if valid
            'timestamp': request.timestamp,
            'user_agent': user_agent[:200] if user_agent else '',  # Limit length
            'page_url': page_url[:500] if page_url else '',  # Limit length
            'created_at': datetime.now().isoformat()
        }
        
        # Store in JSON file (appropriate for structured review data)
        review_id = review_storage.store_review(review_data)
        
        return {
            "status": "success",
            "message": "Thank you for your feedback!",
            "review_id": review_id
        }
            
    except HTTPException:
        raise
    except Exception as e:
        # Log error but don't expose details to client
        print(f"[ENHANCED OPENAI API] Error submitting review: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while submitting your feedback. Please try again later."
        )

@app.get("/reviews")
async def get_all_reviews(
    limit: int = Query(100, ge=1, le=1000, description="Number of reviews to return (1-1000)"), 
    offset: int = Query(0, ge=0, description="Number of reviews to skip"),
    api_key: Optional[str] = Query(None, description="Admin API key required")
):
    """Get all reviews (for admin viewing only - requires API key)"""
    try:
        # Verify API key
        from services.shared.auth import verify_admin_key_query
        verify_admin_key_query(api_key)
        
        from services.shared.review_storage import review_storage
        
        # Get reviews from JSON storage
        reviews = review_storage.get_all_reviews(limit=limit, offset=offset)
        all_reviews = review_storage.get_all_reviews()  # Get all for total count
        total = len(all_reviews)
        
        return {
            "status": "success",
            "total": total,
            "limit": limit,
            "offset": offset,
            "reviews": reviews
        }
    except HTTPException:
        raise
    except Exception as e:
        # Log error but don't expose details
        print(f"[ENHANCED OPENAI API] Error getting reviews: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while retrieving reviews. Please try again later."
        )

@app.get("/reviews/stats")
async def get_review_stats(
    api_key: Optional[str] = Query(None, description="Admin API key required")
):
    """Get review statistics (admin only - requires API key)"""
    try:
        # Verify API key
        from services.shared.auth import verify_admin_key_query
        verify_admin_key_query(api_key)
        
        from services.shared.review_storage import review_storage
        
        # Get stats from JSON storage
        stats = review_storage.get_review_stats()
        
        return {
            "status": "success",
            "total_reviews": stats['total_reviews'],
            "average_rating": stats['average_rating'],
            "rating_distribution": stats['rating_distribution'],
            "feedback_types": stats['feedback_types']
        }
    except HTTPException:
        raise
    except Exception as e:
        # Log error but don't expose details
        print(f"[ENHANCED OPENAI API] Error getting review stats: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while retrieving statistics. Please try again later."
        )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    if not enhanced_openai_chatbot:
        return {
            "message": "Enhanced OpenAI Northeastern University Chatbot API (Not Initialized)",
            "error": "Chatbot not initialized. Check OpenAI API key configuration.",
            "version": "2.0.0"
        }
    
    return {
        "message": "Enhanced OpenAI Northeastern University Chatbot API",
        "version": "2.0.0",
        "description": "Maximum accuracy chatbot with OpenAI GPT and 10 document analysis",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "stats": "/stats",
            "documents": "/documents",
            "search": "/search",
            "review": "/review",
            "reviews": "/reviews",
            "reviews/stats": "/reviews/stats"
        },
        "model": enhanced_openai_chatbot.model_name,
        "device": enhanced_openai_chatbot.embedding_manager.device,
        "features": [
            f"OpenAI {enhanced_openai_chatbot.model_name}",
            "GPU-accelerated embeddings",
            "10 document analysis",
            "Query expansion",
            "Hybrid search",
            "Conversation history"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Use environment variables for deployment
    PORT = int(os.environ.get("PORT", 8001))
    HOST = os.environ.get("HOST", "0.0.0.0")
    
    print("[START] Starting Enhanced OpenAI Chatbot API Server")
    print("=" * 60)
    print(f"[INFO] Chatbot Type: Enhanced OpenAI")
    if enhanced_openai_chatbot:
        print(f"[INFO] Model: {enhanced_openai_chatbot.model_name}")
        print(f"[INFO] Embedding Device: {enhanced_openai_chatbot.embedding_manager.device}")
    print(f"[INFO] Target Response Time: 3-10 seconds")
    print(f"[INFO] Documents Analyzed: 10 per query")
    print(f"[INFO] API URL: http://{HOST}:{PORT}")
    print("=" * 60)
    
    uvicorn.run(
        "enhanced_openai_api:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )

