#!/usr/bin/env python3
"""
Full Northeastern University Chatbot for Railway deployment
Includes Pinecone, ChatGPT, and document retrieval functionality
"""

import os
import sys
import time
import uuid
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add current directory to Python path
sys.path.append('.')

# Create FastAPI app
app = FastAPI(
    title="Northeastern University Chatbot",
    description="Full-featured chatbot with Pinecone, ChatGPT, and document retrieval",
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

class ReviewRequest(BaseModel):
    session_id: str
    rating: int
    feedback_type: str = "general"
    feedback_text: Optional[str] = ""
    email: Optional[str] = None
    timestamp: str
    user_agent: Optional[str] = None
    page_url: Optional[str] = None

# Global chatbot instance
chatbot = None

def initialize_chatbot():
    """Initialize the chatbot with fallback handling"""
    global chatbot
    
    try:
        print("🤖 Initializing Northeastern University Chatbot...")
        
        # Try to import the enhanced OpenAI chatbot (optimized for cloud and speed)
        from services.chat_service.enhanced_openai_chatbot import EnhancedOpenAIUniversityRAGChatbot
        
        # Set optimized defaults if not already set
        if not os.getenv('OPENAI_MODEL'):
            os.environ['OPENAI_MODEL'] = 'gpt-4o-mini'
        if not os.getenv('OPENAI_TEMPERATURE'):
            os.environ['OPENAI_TEMPERATURE'] = '0.2'
        if not os.getenv('OPENAI_MAX_TOKENS'):
            os.environ['OPENAI_MAX_TOKENS'] = '300'
        if not os.getenv('OPENAI_STREAMING'):
            os.environ['OPENAI_STREAMING'] = 'true'
        
        chatbot = EnhancedOpenAIUniversityRAGChatbot()
        print("✅ Enhanced OpenAI chatbot initialized with optimized settings!")
        return True
        
    except ImportError as e:
        print(f"⚠️  Failed to import full chatbot: {e}")
        print("🔄 Using fallback chatbot...")
        
        # Create a fallback chatbot
        class FallbackChatbot:
            def __init__(self):
                self.llm = None
                self.embedding_model = None
                self.db_type = "fallback"
                
            def chat(self, question: str, session_id: str = None) -> Dict[str, Any]:
                """Fallback chat method"""
                start_time = time.time()
                
                # Simple keyword-based responses
                question_lower = question.lower()
                
                if any(word in question_lower for word in ['admission', 'admit', 'apply', 'requirement']):
                    answer = """Northeastern University has specific admission requirements that vary by program. 
                    Generally, you'll need:
                    - Completed application form
                    - Official transcripts
                    - Standardized test scores (SAT/ACT)
                    - Letters of recommendation
                    - Personal statement
                    - Application fee
                    
                    For specific requirements, please visit the Northeastern University admissions website or contact the admissions office directly."""
                    
                elif any(word in question_lower for word in ['co-op', 'coop', 'internship', 'work']):
                    answer = """Northeastern University is renowned for its co-op program, which provides students with real-world work experience. 
                    The co-op program allows students to:
                    - Work in their field of study
                    - Gain practical experience
                    - Build professional networks
                    - Earn money while learning
                    
                    Co-op experiences typically last 6 months and are integrated into the academic curriculum."""
                    
                elif any(word in question_lower for word in ['program', 'major', 'degree', 'course']):
                    answer = """Northeastern University offers a wide range of undergraduate and graduate programs across various disciplines including:
                    - Engineering and Computer Science
                    - Business and Management
                    - Health Sciences
                    - Arts and Sciences
                    - Law and Public Policy
                    
                    Each program has specific requirements and curriculum. Please visit the university website for detailed information about specific programs."""
                    
                else:
                    answer = """I'm the Northeastern University Chatbot. I can help you with information about:
                    - Admission requirements and application process
                    - Academic programs and majors
                    - Co-op and internship opportunities
                    - Campus life and student services
                    - Financial aid and scholarships
                    
                    Please ask me a specific question about Northeastern University!"""
                
                return {
                    'answer': answer,
                    'sources': [],
                    'confidence': 0.7,
                    'session_id': session_id or f"fallback_{int(time.time())}",
                    'response_time': time.time() - start_time,
                    'documents_analyzed': 0
                }
        
        chatbot = FallbackChatbot()
        print("✅ Fallback chatbot initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize chatbot on startup"""
    initialize_chatbot()

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "Northeastern University Chatbot API is running",
        "chatbot_initialized": chatbot is not None,
        "chatbot_type": "full" if hasattr(chatbot, 'llm') else "fallback"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Northeastern University Chatbot",
        "status": "running",
        "chatbot_initialized": chatbot is not None,
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "review": "/review",
            "reviews": "/reviews",
            "reviews/stats": "/reviews/stats",
            "docs": "/docs"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with full functionality"""
    try:
        if not chatbot:
            raise HTTPException(status_code=500, detail="Chatbot not initialized")
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Process the question using the chatbot
        result = chatbot.chat(request.question, session_id)
        
        return ChatResponse(
            answer=result['answer'],
            sources=result['sources'],
            confidence=result['confidence'],
            session_id=session_id,
            response_time=result.get('response_time', 0.0),
            documents_analyzed=result.get('documents_analyzed', 0)
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/search")
async def search_documents(query: str, k: int = 5):
    """Search for similar documents"""
    try:
        if not chatbot:
            raise HTTPException(status_code=500, detail="Chatbot not initialized")
        
        if hasattr(chatbot, 'search_documents'):
            documents = chatbot.search_documents(query, k)
            
            # Format results for API response
            results = []
            for doc in documents:
                metadata = doc.get('metadata', {})
                results.append({
                    'content': doc.get('content', '')[:200] + '...' if len(doc.get('content', '')) > 200 else doc.get('content', ''),
                    'title': metadata.get('title', 'Unknown'),
                    'url': metadata.get('source_url', ''),
                    'score': doc.get('score', 0.0)
                })
            
            return {"query": query, "results": results}
        else:
            return {"query": query, "results": [], "message": "Search not available in fallback mode"}
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@app.post("/review")
async def submit_review(request: ReviewRequest):
    """Submit user review/feedback"""
    try:
        # Validate rating
        if not 1 <= request.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Import review storage (JSON-based, not ChromaDB)
        from services.shared.review_storage import review_storage
        from datetime import datetime
        
        # Prepare review data for storage
        review_data = {
            'session_id': request.session_id,
            'rating': request.rating,
            'feedback_type': request.feedback_type,
            'feedback_text': request.feedback_text or '',
            'email': request.email or '',
            'timestamp': request.timestamp,
            'user_agent': request.user_agent or '',
            'page_url': request.page_url or '',
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
        print(f"❌ Error submitting review: {e}")
        raise HTTPException(status_code=500, detail=f"Error submitting review: {str(e)}")

@app.get("/reviews")
async def get_all_reviews(limit: int = 100, offset: int = 0):
    """Get all reviews (for admin viewing)"""
    try:
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
    except Exception as e:
        print(f"❌ Error getting reviews: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting reviews: {str(e)}")

@app.get("/reviews/stats")
async def get_review_stats():
    """Get review statistics"""
    try:
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
    except Exception as e:
        print(f"❌ Error getting review stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting review stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
