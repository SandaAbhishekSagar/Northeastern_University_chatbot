#!/usr/bin/env python3
"""
Simple script to run the Enhanced GPU Chatbot System
"""

import sys
import os
import subprocess
import time
import threading
from pathlib import Path

def start_api_server():
    """Start the API server"""
    print("🚀 Starting Enhanced GPU API Server...")
    
    # Add current directory to Python path
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path.cwd())
    
    try:
        # Start the API server
        process = subprocess.Popen([
            sys.executable, "-c",
            """
import sys
sys.path.append('.')
from services.chat_service.enhanced_gpu_api import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8001, log_level='info')
"""
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Wait a moment for startup
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Enhanced GPU API Server started successfully")
            print("🌐 API URL: http://localhost:8001")
            return process
        else:
            print("❌ Failed to start Enhanced GPU API Server")
            return None
            
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return None

def start_frontend_server():
    """Start the frontend server"""
    print("\n🌐 Starting Frontend Server...")
    
    try:
        # Start frontend server
        process = subprocess.Popen([
            sys.executable, "frontend/server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Wait a moment for startup
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Frontend Server started successfully")
            print("📋 Frontend URL: http://localhost:3000")
            return process
        else:
            print("❌ Failed to start Frontend Server")
            return None
            
    except Exception as e:
        print(f"❌ Error starting frontend server: {e}")
        return None

def monitor_process(process, name):
    """Monitor a process and display output"""
    if process:
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[{name}] {line.rstrip()}")

def main():
    """Main function"""
    print("🚀 Enhanced GPU Chatbot System")
    print("=" * 50)
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Cannot start system without API server")
        return
    
    # Start frontend server
    frontend_process = start_frontend_server()
    if not frontend_process:
        print("❌ Cannot start system without frontend server")
        if api_process:
            api_process.terminate()
        return
    
    # Display success message
    print("\n" + "=" * 50)
    print("🎉 Enhanced GPU Chatbot System Started!")
    print("=" * 50)
    print("📊 System Information:")
    print("   • API Server: http://localhost:8001")
    print("   • Frontend: http://localhost:3000")
    print("   • Chat Interface: http://localhost:3000")
    print("   • API Documentation: http://localhost:8001/docs")
    print("   • Health Check: http://localhost:8001/health")
    print("")
    print("⏹️  Press Ctrl+C to stop all servers")
    print("=" * 50)
    
    # Start monitoring threads
    api_thread = threading.Thread(target=monitor_process, args=(api_process, "API"), daemon=True)
    frontend_thread = threading.Thread(target=monitor_process, args=(frontend_process, "Frontend"), daemon=True)
    
    api_thread.start()
    frontend_thread.start()
    
    try:
        # Keep running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API Server stopped unexpectedly")
                break
                
            if frontend_process.poll() is not None:
                print("❌ Frontend Server stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Enhanced GPU Chatbot System...")
        
        # Stop processes
        if api_process:
            api_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        print("✅ Enhanced GPU Chatbot System stopped")

if __name__ == "__main__":
    main()

