#!/usr/bin/env python3
"""
Minimal startup script that creates a simple FastAPI server
This bypasses all the complex imports that might be failing
"""

import os
import sys
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🚀 Northeastern University Chatbot - Minimal Mode")
    print("=" * 60)
    print("✅ Simple FastAPI Server")
    print("✅ Basic Health Check")
    print("✅ Fallback Mode")
    print("=" * 60)

def create_simple_app():
    """Create a simple FastAPI app"""
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
            return {"status": "healthy", "message": "API is running"}
        
        @app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "message": "Northeastern University Chatbot - Minimal Mode",
                "status": "running",
                "endpoints": {
                    "health": "/health",
                    "chat": "/chat (coming soon)"
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

def start_server():
    """Start the server"""
    print("🌐 Creating simple FastAPI app...")
    
    app = create_simple_app()
    if not app:
        print("❌ Failed to create app")
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
    print("🎯 Starting minimal server...")
    start_server()

if __name__ == "__main__":
    main()
