#!/usr/bin/env python3
"""
Start the Fixed Northeastern University Chatbot
- Restores data from backups
- Uses ChatGPT instead of Ollama
- Fixes URL handling issues
- Provides better error handling
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    print("🔍 Checking requirements...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "openai",
        "langchain-openai",
        "sentence-transformers",
        "chromadb",
        "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All requirements satisfied!")
    return True

def check_env_file():
    """Check if .env file exists and has required keys"""
    print("\n🔍 Checking .env file...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please run: python restore_and_fix_system.py")
        return False
    
    # Check for OpenAI API key
    with open('.env', 'r') as f:
        content = f.read()
        
    if 'your_openai_api_key_here' in content:
        print("⚠️  Please add your OpenAI API key to the .env file")
        print("Get your API key from: https://platform.openai.com/api-keys")
        return False
    
    print("✅ .env file configured!")
    return True

def check_database():
    """Check if database has data"""
    print("\n🔍 Checking database...")
    
    try:
        # Import database functions
        sys.path.append('services/shared')
        from database import get_database_type, get_pinecone_count
        
        db_type = get_database_type()
        print(f"📊 Database type: {db_type}")
        
        if db_type == "pinecone":
            count = get_pinecone_count()
            print(f"📄 Documents in Pinecone: {count}")
        else:
            # Check ChromaDB
            if os.path.exists('chroma_data/chroma.sqlite3'):
                print("✅ ChromaDB database found")
            else:
                print("⚠️  ChromaDB database not found")
                print("Run: python restore_and_fix_system.py")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def start_api_server():
    """Start the fixed API server"""
    print("\n🚀 Starting Fixed Chatbot API...")
    
    try:
        # Start the API server
        cmd = [sys.executable, "-m", "uvicorn", "services.chat_service.fixed_api:app", "--host", "0.0.0.0", "--port", "8001"]
        
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")

def main():
    print("🎓 Northeastern University Chatbot - Fixed Version")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements not met. Please install missing packages.")
        return
    
    # Check .env file
    if not check_env_file():
        print("\n❌ Environment not configured. Please set up your .env file.")
        return
    
    # Check database
    if not check_database():
        print("\n❌ Database not ready. Please restore data from backups.")
        return
    
    print("\n✅ All checks passed!")
    print("\n🌐 Starting the fixed chatbot...")
    print("📱 Frontend will be available at: http://localhost:3000")
    print("🔧 API will be available at: http://localhost:8001")
    print("📚 Documentation: http://localhost:8001/docs")
    print("\n💡 The chatbot now uses ChatGPT for better responses!")
    print("🔗 URLs are now properly handled and displayed!")
    print("\nPress Ctrl+C to stop the server")
    
    # Start the API server
    start_api_server()

if __name__ == "__main__":
    main()
