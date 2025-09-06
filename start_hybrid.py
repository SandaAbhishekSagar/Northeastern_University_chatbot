#!/usr/bin/env python3
"""
Hybrid startup script that tries the full API first, then falls back to minimal
"""

import os
import sys
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🚀 Northeastern University Chatbot - Hybrid Mode")
    print("=" * 60)
    print("✅ Trying Full API First")
    print("✅ Fallback to Minimal Mode")
    print("✅ Robust Error Handling")
    print("=" * 60)

def create_minimal_app():
    """Create a minimal FastAPI app as fallback"""
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(
            title="Northeastern University Chatbot - Minimal Mode",
            description="Simple chatbot API with health checks",
            version="1.0.0"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/health")
        async def health():
            """Simple health check endpoint"""
            return {"status": "healthy", "message": "API is running (minimal mode)"}
        
        @app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "message": "Northeastern University Chatbot - Minimal Mode",
                "status": "running",
                "mode": "minimal",
                "endpoints": {
                    "health": "/health",
                    "chat": "/chat"
                }
            }
        
        @app.post("/chat")
        async def chat():
            """Placeholder chat endpoint"""
            return {
                "answer": "Chat functionality is being initialized. Please try again in a moment.",
                "sources": [],
                "confidence": 0.0,
                "session_id": "minimal_mode",
                "response_time": 0.0,
                "documents_analyzed": 0
            }
        
        return app
        
    except ImportError as e:
        print(f"❌ Failed to import FastAPI: {e}")
        return None

def try_full_api():
    """Try to import and use the full API"""
    print("🔍 Attempting to import full API...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, '.')
        
        # Try to import the full API
        from services.chat_service.fixed_api import app
        print("✅ Successfully imported full API")
        return app
        
    except ImportError as e:
        print(f"⚠️  Failed to import full API: {e}")
        return None
    except Exception as e:
        print(f"⚠️  Error importing full API: {e}")
        return None

def start_server():
    """Start the server with fallback"""
    print("🌐 Starting server...")
    
    # Try full API first
    app = try_full_api()
    
    if not app:
        print("🔄 Falling back to minimal API...")
        app = create_minimal_app()
    
    if not app:
        print("❌ Failed to create any app")
        return False
    
    print("✅ App created successfully")
    
    try:
        import uvicorn
        
        print("🚀 Starting server on http://0.0.0.0:8001")
        print("📚 API Documentation: http://0.0.0.0:8001/docs")
        print("💬 Chat Endpoint: http://0.0.0.0:8001/chat")
        print("❤️  Health Check: http://0.0.0.0:8001/health")
        print("=" * 60)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def main():
    """Main startup function"""
    print_banner()
    
    # Check if we're in the right directory
    print(f"🔍 Current directory: {os.getcwd()}")
    print(f"🔍 Python path: {sys.path}")
    
    # Create basic .env if it doesn't exist
    if not Path(".env").exists():
        print("⚠️  Creating basic .env file...")
        with open(".env", "w") as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        print("✅ Created basic .env file")
    
    print("✅ Environment check passed")
    
    # Start server
    print("🎯 Starting hybrid server...")
    start_server()

if __name__ == "__main__":
    main()
