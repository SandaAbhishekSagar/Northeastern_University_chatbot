"""
Quick Start Script for Enhanced OpenAI Chatbot System
Starts the OpenAI GPT-powered chatbot with 10-document analysis
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

# Store process references for cleanup
processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n[SHUTDOWN] Shutting down Enhanced OpenAI System...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
    print("[SHUTDOWN] All services stopped.")
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

def check_openai_key():
    """Check if OpenAI API key is configured"""
    # Check environment variable
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI API key found in environment variables")
        return True
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip().startswith("OPENAI_API_KEY=") and len(line.strip()) > 15:
                    print("✅ OpenAI API key found in .env file")
                    return True
    
    return False

def start_enhanced_openai_system():
    """Start the Enhanced OpenAI chatbot system"""
    
    print("="*70)
    print("🚀 ENHANCED OPENAI NORTHEASTERN UNIVERSITY CHATBOT")
    print("="*70)
    print("Features:")
    print("  ✅ OpenAI GPT-4/GPT-3.5 for answer generation")
    print("  ✅ GPU-accelerated embeddings (automatic detection)")
    print("  ✅ 10 document analysis per query")
    print("  ✅ Query expansion (3 variations)")
    print("  ✅ Hybrid search (semantic + keyword)")
    print("  ✅ Conversation history integration")
    print("  ✅ Multi-factor confidence scoring")
    print("  ✅ Response time: 3-10 seconds")
    print("="*70)
    
    # Check OpenAI API key
    print("\n📋 Checking Prerequisites...")
    if not check_openai_key():
        print("\n❌ ERROR: OpenAI API key not found!")
        print("\nPlease set your OpenAI API key in one of these ways:")
        print("\n1. Create a .env file in the project root with:")
        print("   OPENAI_API_KEY=your-api-key-here")
        print("\n2. Set environment variable:")
        print("   export OPENAI_API_KEY=your-api-key-here  # Linux/Mac")
        print("   set OPENAI_API_KEY=your-api-key-here     # Windows CMD")
        print("   $env:OPENAI_API_KEY=\"your-api-key-here\"  # Windows PowerShell")
        print("\n3. Get your API key from: https://platform.openai.com/api-keys")
        return False
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        print(f"❌ Python 3.9+ required (you have {python_version.major}.{python_version.minor})")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if virtual environment is activated
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment activated")
    else:
        print("⚠️  Warning: Virtual environment not detected")
        print("   Consider activating: env_py3.9\\Scripts\\activate (Windows)")
    
    print("\n🔧 Starting Services...")
    print("-"*70)
    
    # Start Enhanced OpenAI API Server
    print("\n[1/2] Starting Enhanced OpenAI API Server...")
    print("      Port: 8001")
    print("      Endpoint: http://localhost:8001")
    
    try:
        api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", 
             "services.chat_service.enhanced_openai_api:app",
             "--host", "0.0.0.0",
             "--port", "8001",
             "--log-level", "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        processes.append(api_process)
        
        # Give API time to start
        time.sleep(3)
        
        if api_process.poll() is None:
            print("      ✅ Enhanced OpenAI API Server started successfully")
        else:
            print("      ❌ Failed to start Enhanced OpenAI API Server")
            print("      Check output above for errors")
            return False
            
    except Exception as e:
        print(f"      ❌ Error starting API server: {e}")
        return False
    
    # Start Frontend Server
    print("\n[2/2] Starting Frontend Server...")
    print("      Port: 3000")
    print("      Endpoint: http://localhost:3000")
    
    try:
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            print("      ⚠️  Frontend directory not found, skipping")
        else:
            os.chdir(frontend_dir)
            frontend_process = subprocess.Popen(
                [sys.executable, "server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            processes.append(frontend_process)
            os.chdir("..")
            
            # Give frontend time to start
            time.sleep(2)
            
            if frontend_process.poll() is None:
                print("      ✅ Frontend Server started successfully")
            else:
                print("      ⚠️  Frontend server may have failed (check server.py)")
        
    except Exception as e:
        print(f"      ⚠️  Error starting frontend: {e}")
    
    # Display success message
    print("\n" + "="*70)
    print("✅ ENHANCED OPENAI SYSTEM IS RUNNING!")
    print("="*70)
    print("\n🌐 Access Points:")
    print("   • Frontend:        http://localhost:3000")
    print("   • API:             http://localhost:8001")
    print("   • API Docs:        http://localhost:8001/docs")
    print("   • Health Check:    http://localhost:8001/health/enhanced")
    
    print("\n📊 System Information:")
    print("   • LLM Provider:    OpenAI")
    print("   • Model:           GPT-4 (default) or GPT-3.5-Turbo")
    print("   • Documents:       10 per query")
    print("   • Response Time:   3-10 seconds")
    
    print("\n💡 Quick Test:")
    print("   Open your browser to http://localhost:3000")
    print("   Try asking: 'What are the admission requirements?'")
    
    print("\n⚠️  Press Ctrl+C to stop all services")
    print("="*70)
    
    # Keep script running and monitor processes
    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            for process in processes:
                if process.poll() is not None:
                    print(f"\n⚠️  A service has stopped unexpectedly (exit code: {process.returncode})")
                    print("   Press Ctrl+C to stop all services")
    except KeyboardInterrupt:
        pass
    
    return True

if __name__ == "__main__":
    success = start_enhanced_openai_system()
    if not success:
        print("\n❌ Failed to start Enhanced OpenAI System")
        print("   Please check the error messages above")
        sys.exit(1)

