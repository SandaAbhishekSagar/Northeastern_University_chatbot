#!/usr/bin/env python3
"""
Northeastern University Chatbot - System Startup Script
Automatically starts all components of the chatbot system
"""

import os
import sys
import time
import subprocess
import webbrowser
import requests
from pathlib import Path

def check_python_environment():
    """Check if we're in the correct Python environment"""
    print("🔍 Checking Python environment...")
    
    # Check if we're in the env_py3.9 environment
    if 'env_py3.9' not in sys.executable:
        print("⚠️  Warning: Not using env_py3.9 environment")
        print("   Consider activating: env_py3.9\\Scripts\\activate")
    
    print(f"✅ Python: {sys.version}")
    return True

def check_ollama():
    """Check if Ollama is running and has the required model"""
    print("🔍 Checking Ollama...")
    
    try:
        # Check if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            has_llama = any('llama2:7b' in model.get('name', '') for model in models)
            
            if has_llama:
                print("✅ Ollama running with llama2:7b model")
                return True
            else:
                print("⚠️  Ollama running but llama2:7b not found")
                print("   Run: ollama pull llama2:7b")
                return False
        else:
            print("❌ Ollama not responding")
            return False
    except requests.exceptions.RequestException:
        print("❌ Ollama not running")
        print("   Start Ollama with: ollama serve")
        return False

def start_chromadb():
    """Start ChromaDB server"""
    print("🚀 Starting ChromaDB...")
    
    try:
        # Check if ChromaDB is already running
        response = requests.get("http://localhost:8000/api/v1/heartbeat", timeout=5)
        if response.status_code == 200:
            print("✅ ChromaDB already running")
            return True
    except requests.exceptions.RequestException:
        pass
    
    # Start ChromaDB
    try:
        chroma_process = subprocess.Popen(
            ["chroma", "run", "--host", "localhost", "--port", "8000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait a moment for ChromaDB to start
        time.sleep(3)
        
        # Check if it's running
        try:
            response = requests.get("http://localhost:8000/api/v1/heartbeat", timeout=5)
            if response.status_code == 200:
                print("✅ ChromaDB started successfully")
                return True
            else:
                print("❌ ChromaDB failed to start")
                return False
        except requests.exceptions.RequestException:
            print("❌ ChromaDB failed to start")
            return False
            
    except FileNotFoundError:
        print("❌ ChromaDB not found. Install with: pip install chromadb")
        return False

def start_api_server():
    """Start the enhanced chatbot API server"""
    print("🚀 Starting Enhanced Chatbot API...")
    
    try:
        # Change to the chat service directory
        api_dir = Path("services/chat_service")
        if not api_dir.exists():
            print("❌ API directory not found")
            return False
        
        # Start the API server using uvicorn directly
        api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"],
            cwd=api_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for API to start
        time.sleep(8)
        
        # Check if API is running
        try:
            response = requests.get("http://localhost:8001/health/enhanced", timeout=10)
            if response.status_code == 200:
                print("✅ Enhanced API started successfully")
                return True
            else:
                print("❌ API failed to start")
                return False
        except requests.exceptions.RequestException:
            print("❌ API failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        return False

def start_frontend():
    """Start the Northeastern-themed frontend"""
    print("🚀 Starting Northeastern Frontend...")
    
    try:
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            print("❌ Frontend directory not found")
            return False
        
        # Start the frontend server
        frontend_process = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8080"],
            cwd=frontend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for frontend to start
        time.sleep(3)
        
        # Check if frontend is running
        try:
            response = requests.get("http://localhost:8080", timeout=5)
            if response.status_code == 200:
                print("✅ Frontend started successfully")
                return True
            else:
                print("❌ Frontend failed to start")
                return False
        except requests.exceptions.RequestException:
            print("❌ Frontend failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return False

def open_browser():
    """Open the browser to the frontend"""
    print("🌐 Opening browser...")
    try:
        webbrowser.open("http://localhost:8080")
        print("✅ Browser opened to Northeastern University Assistant")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("   Please open: http://localhost:8080")

def run_tests():
    """Run system tests"""
    print("🧪 Running system tests...")
    
    try:
        # Run enhanced system tests
        result = subprocess.run([sys.executable, "test_enhanced_system.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Enhanced system tests passed")
        else:
            print("⚠️  Enhanced system tests failed")
            print(result.stdout)
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def main():
    """Main startup function"""
    print("🎓 Northeastern University Chatbot - System Startup")
    print("=" * 60)
    
    # Check environment
    if not check_python_environment():
        return
    
    # Check Ollama
    if not check_ollama():
        print("\n⚠️  Please ensure Ollama is running with llama2:7b model")
        print("   Commands:")
        print("   ollama serve")
        print("   ollama pull llama2:7b")
        return
    
    # Start ChromaDB
    if not start_chromadb():
        print("\n❌ Failed to start ChromaDB")
        return
    
    # Start API server
    if not start_api_server():
        print("\n❌ Failed to start API server")
        return
    
    # Start frontend
    if not start_frontend():
        print("\n❌ Failed to start frontend")
        return
    
    print("\n" + "=" * 60)
    print("🎉 Northeastern University Chatbot is ready!")
    print("\n📊 System Status:")
    print("   • ChromaDB: http://localhost:8000")
    print("   • API Server: http://localhost:8001")
    print("   • Frontend: http://localhost:8080")
    print("   • Health Check: http://localhost:8001/health/enhanced")
    
    # Open browser
    open_browser()
    
    print("\n🔧 Available Commands:")
    print("   • Test Enhanced Features: python test_enhanced_system.py")
    print("   • Test Basic System: python test_system.py")
    print("   • View Documentation: STARTUP_GUIDE.md")
    
    print("\n💡 Tips:")
    print("   • The system uses enhanced RAG with hybrid search")
    print("   • Query expansion improves search results")
    print("   • Confidence scoring helps identify reliable answers")
    print("   • All responses are Northeastern University focused")
    
    print("\n🚀 Enjoy your Northeastern University Assistant!")

if __name__ == "__main__":
    main() 