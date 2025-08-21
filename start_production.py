#!/usr/bin/env python3
"""
Production Startup Script for Enhanced GPU Chatbot
Optimized for cloud deployment with ChromaDB Cloud or Pinecone
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def check_database_connection():
    """Check database connection (ChromaDB or Pinecone)"""
    try:
        from services.shared.database import get_database_type, init_db
        
        # Get database type
        db_type = get_database_type()
        print(f"🌐 Using database type: {db_type}")
        
        # Initialize database
        init_db()
        
        if db_type == "pinecone":
            # For Pinecone, just check if we can connect
            from services.shared.database import get_pinecone_count
            doc_count = get_pinecone_count()
            print(f"✅ Pinecone connected successfully - {doc_count} documents available")
            return True
        else:
            # For ChromaDB, test a simple query
            from services.shared.database import get_collection
            collection = get_collection('documents')
            result = collection.get()
            
            doc_count = len(result.get('ids', [])) if result else 0
            print(f"✅ ChromaDB connected successfully - {doc_count} documents available")
            return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure your database configuration is set correctly")
        return False

def main():
    """Start the production server with cloud-optimized settings"""
    
    # Check database connection
    if not check_database_connection():
        print("❌ Cannot start without database connection")
        sys.exit(1)
    
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