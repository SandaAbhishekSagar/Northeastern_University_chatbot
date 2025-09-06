#!/usr/bin/env python3
"""
Production startup script for the Fixed Northeastern University Chatbot
This script initializes the system and starts the API server
"""

import os
import sys
import time
import subprocess
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

def check_environment():
    """Check environment setup"""
    print("🔍 Checking environment...")
    
    # Check if we're in the right directory
    if not Path("services").exists():
        print("❌ Error: services directory not found")
        return False
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  Warning: .env file not found, creating basic one...")
        create_basic_env()
    
    print("✅ Environment check passed")
    return True

def create_basic_env():
    """Create a basic .env file for production"""
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

def initialize_database():
    """Initialize the database"""
    print("🗄️  Initializing database...")
    
    try:
        # Import and initialize the database
        from services.shared.database import init_db
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
        print("🔄 Continuing with fallback mode...")
        return True

def start_api_server():
    """Start the API server"""
    print("🌐 Starting API server...")
    
    try:
        # Start the fixed API server
        import uvicorn
        from services.chat_service.fixed_api import app
        
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
        return False

def main():
    """Main startup function"""
    print_banner()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("⚠️  Database initialization failed, but continuing...")
    
    # Start API server
    print("🎯 Starting production server...")
    start_api_server()

if __name__ == "__main__":
    main()
