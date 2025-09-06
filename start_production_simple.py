#!/usr/bin/env python3
"""
Simple production startup script for the Fixed Northeastern University Chatbot
This script starts the API server with minimal dependencies
"""

import os
import sys
import time
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🚀 Northeastern University Chatbot - Production Mode")
    print("=" * 60)
    print("✅ Using Fixed ChatGPT Integration")
    print("✅ Enhanced URL Handling")
    print("✅ Fallback Database Support")
    print("=" * 60)

def create_basic_env():
    """Create a basic .env file for production"""
    if not Path(".env").exists():
        env_content = """# Northeastern University Chatbot Environment Variables
# Add your OpenAI API key here for ChatGPT integration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
CHROMADB_HOST=localhost
CHROMADB_PORT=8000

# Pinecone Configuration (optional)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment

# University Configuration
UNIVERSITY_NAME=Northeastern University
UNIVERSITY_URL=https://www.northeastern.edu

# Model Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-3.5-turbo

# Server Configuration
HOST=0.0.0.0
PORT=8001
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Created basic .env file")

def start_api_server():
    """Start the API server"""
    print("🌐 Starting API server...")
    
    try:
        # Create basic .env if it doesn't exist
        create_basic_env()
        
        # Start the fixed API server
        import uvicorn
        
        # Try to import the app
        try:
            from services.chat_service.fixed_api import app
            print("✅ Successfully imported fixed API")
        except ImportError as e:
            print(f"❌ Failed to import fixed API: {e}")
            print("🔄 Trying alternative import...")
            
            # Try alternative import
            sys.path.append('.')
            from services.chat_service.fixed_api import app
            print("✅ Successfully imported fixed API (alternative)")
        
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
        print(f"❌ Failed to start API server: {e}")
        print("🔍 Debug information:")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Python path: {sys.path}")
        print(f"   Files in current directory: {list(Path('.').iterdir())}")
        
        # Try to start a simple health check server
        print("🔄 Starting fallback health check server...")
        start_fallback_server()

def start_fallback_server():
    """Start a simple fallback server for health checks"""
    try:
        from fastapi import FastAPI
        import uvicorn
        
        app = FastAPI(title="Northeastern Chatbot - Fallback Mode")
        
        @app.get("/health")
        async def health_check():
            return {"status": "ok", "message": "Fallback server running"}
        
        @app.get("/")
        async def root():
            return {"message": "Northeastern University Chatbot - Fallback Mode"}
        
        print("🚀 Starting fallback server on http://0.0.0.0:8001")
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
        
    except Exception as e:
        print(f"❌ Even fallback server failed: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print_banner()
    
    # Check if we're in the right directory
    if not Path("services").exists():
        print("❌ Error: services directory not found")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Contents: {list(Path('.').iterdir())}")
        sys.exit(1)
    
    print("✅ Environment check passed")
    
    # Start API server
    print("🎯 Starting production server...")
    start_api_server()

if __name__ == "__main__":
    main()