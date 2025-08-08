#!/usr/bin/env python3
"""
Production Startup Script for Enhanced GPU Chatbot
Optimized for cloud deployment with environment variable configuration
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def main():
    """Start the production server with cloud-optimized settings"""
    
    # Get configuration from environment variables
    port = int(os.environ.get("PORT", 8001))
    host = os.environ.get("HOST", "0.0.0.0")
    workers = int(os.environ.get("WORKERS", 1))
    log_level = os.environ.get("LOG_LEVEL", "info")
    
    print(f"🚀 Starting Enhanced GPU Chatbot in production mode...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"👥 Workers: {workers}")
    print(f"📝 Log Level: {log_level}")
    
    # Import the FastAPI app
    try:
        from services.chat_service.enhanced_gpu_api import app
        print("✅ Enhanced GPU API imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Enhanced GPU API: {e}")
        print("💡 Make sure all dependencies are installed")
        sys.exit(1)
    
    # Start the server
    uvicorn.run(
        "services.chat_service.enhanced_gpu_api:app",
        host=host,
        port=port,
        workers=workers,
        log_level=log_level,
        access_log=True,
        reload=False,  # Disable reload in production
        server_header=False,  # Security: don't expose server info
        date_header=False,    # Security: don't expose date info
    )

if __name__ == "__main__":
    main() 