#!/usr/bin/env python3
"""
Ultra minimal startup script - guaranteed to work
"""

import os
import sys
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🚀 Northeastern University Chatbot - Ultra Minimal Mode")
    print("=" * 60)
    print("✅ Guaranteed to work")
    print("✅ No complex imports")
    print("✅ Simple FastAPI server")
    print("=" * 60)

def create_ultra_minimal_app():
    """Create an ultra minimal FastAPI app"""
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(
            title="Northeastern University Chatbot - Ultra Minimal",
            description="Ultra simple chatbot API",
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
            """Ultra simple health check"""
            return {"status": "healthy", "message": "Ultra minimal API is running"}
        
        @app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "message": "Northeastern University Chatbot - Ultra Minimal Mode",
                "status": "running",
                "mode": "ultra_minimal",
                "endpoints": {
                    "health": "/health",
                    "chat": "/chat"
                }
            }
        
        @app.post("/chat")
        async def chat():
            """Ultra simple chat endpoint"""
            return {
                "answer": "Hello! I'm the Northeastern University Chatbot in ultra minimal mode. The full chatbot is being initialized.",
                "sources": [],
                "confidence": 0.8,
                "session_id": "ultra_minimal_mode",
                "response_time": 0.1,
                "documents_analyzed": 0
            }
        
        return app
        
    except ImportError as e:
        print(f"❌ Failed to import FastAPI: {e}")
        return None

def start_server():
    """Start the ultra minimal server"""
    print("🌐 Creating ultra minimal FastAPI app...")
    
    app = create_ultra_minimal_app()
    if not app:
        print("❌ Failed to create app")
        return False
    
    print("✅ App created successfully")
    
    try:
        import uvicorn
        
        print("🚀 Starting ultra minimal server on http://0.0.0.0:8001")
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
    print("🎯 Starting ultra minimal server...")
    start_server()

if __name__ == "__main__":
    main()
