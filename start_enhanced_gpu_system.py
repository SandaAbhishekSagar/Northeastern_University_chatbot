#!/usr/bin/env python3
"""
Enhanced GPU Chatbot System Startup Script
Launches the enhanced GPU chatbot API and frontend server
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

class EnhancedGPUSystem:
    def __init__(self):
        self.api_process = None
        self.frontend_process = None
        self.running = False
        
        # Get project root directory
        self.project_root = Path(__file__).parent.absolute()
        self.api_path = self.project_root / "services" / "chat_service" / "enhanced_gpu_api.py"
        self.frontend_path = self.project_root / "frontend" / "server.py"
        
        # Check if virtual environment exists
        self.venv_path = self.project_root / "env_py3.9"
        self.venv_activate = self.venv_path / "Scripts" / "activate"
        
    def check_dependencies(self):
        """Check if required dependencies are available"""
        print("🔍 Checking system dependencies...")
        
        # Check if virtual environment exists
        if not self.venv_path.exists():
            print("❌ Virtual environment not found. Please run setup first.")
            return False
            
        # Check if API file exists
        if not self.api_path.exists():
            print(f"❌ Enhanced GPU API not found at: {self.api_path}")
            return False
            
        # Check if frontend exists
        if not self.frontend_path.exists():
            print(f"❌ Frontend server not found at: {self.frontend_path}")
            return False
            
        print("✅ All dependencies found")
        return True
    
    def start_api_server(self):
        """Start the enhanced GPU API server"""
        print("\n🚀 Starting Enhanced GPU API Server...")
        print("=" * 60)
        
        try:
            # Activate virtual environment and start API
            if os.name == 'nt':  # Windows
                cmd = [
                    str(self.venv_path / "Scripts" / "python.exe"),
                    "-c",
                    f"import sys; sys.path.append('{self.project_root}'); import uvicorn; import enhanced_gpu_api; uvicorn.run('enhanced_gpu_api:app', host='0.0.0.0', port=8001, reload=False)"
                ]
                cwd = str(self.project_root / "services" / "chat_service")
            else:  # Unix/Linux
                cmd = [
                    str(self.venv_path / "bin" / "python"),
                    "-c",
                    f"import sys; sys.path.append('{self.project_root}'); import uvicorn; import enhanced_gpu_api; uvicorn.run('enhanced_gpu_api:app', host='0.0.0.0', port=8001, reload=False)"
                ]
                cwd = str(self.project_root / "services" / "chat_service")
            
            self.api_process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Wait a moment for the server to start
            time.sleep(3)
            
            if self.api_process.poll() is None:
                print("✅ Enhanced GPU API Server started successfully")
                print(f"🌐 API URL: http://localhost:8001")
                return True
            else:
                print("❌ Failed to start Enhanced GPU API Server")
                return False
                
        except Exception as e:
            print(f"❌ Error starting API server: {e}")
            return False
    
    def start_frontend_server(self):
        """Start the frontend server"""
        print("\n🌐 Starting Frontend Server...")
        print("=" * 60)
        
        try:
            # Start frontend server
            cmd = [
                sys.executable,
                str(self.frontend_path)
            ]
            cwd = str(self.project_root / "frontend")
            
            self.frontend_process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Wait a moment for the server to start
            time.sleep(5)
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend Server started successfully")
                print(f"📋 Frontend URL: http://localhost:3000")
                return True
            else:
                # Check if there was an error
                stdout, stderr = self.frontend_process.communicate()
                if stdout:
                    print(f"Frontend server output: {stdout}")
                if stderr:
                    print(f"Frontend server error: {stderr}")
                print("❌ Failed to start Frontend Server")
                return False
                
        except Exception as e:
            print(f"❌ Error starting frontend server: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor running processes and display output"""
        def monitor_api():
            if self.api_process:
                for line in iter(self.api_process.stdout.readline, ''):
                    if line:
                        print(f"[API] {line.rstrip()}")
        
        def monitor_frontend():
            if self.frontend_process:
                for line in iter(self.frontend_process.stdout.readline, ''):
                    if line:
                        print(f"[Frontend] {line.rstrip()}")
        
        # Start monitoring threads
        api_thread = threading.Thread(target=monitor_api, daemon=True)
        frontend_thread = threading.Thread(target=monitor_frontend, daemon=True)
        
        api_thread.start()
        frontend_thread.start()
    
    def stop_servers(self):
        """Stop all running servers"""
        print("\n🛑 Stopping servers...")
        
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                print("✅ API Server stopped")
            except subprocess.TimeoutExpired:
                self.api_process.kill()
                print("⚠️ API Server force stopped")
            except Exception as e:
                print(f"❌ Error stopping API server: {e}")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                print("✅ Frontend Server stopped")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                print("⚠️ Frontend Server force stopped")
            except Exception as e:
                print(f"❌ Error stopping frontend server: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.running = False
        self.stop_servers()
        sys.exit(0)
    
    def run(self):
        """Main run method"""
        print("🚀 Enhanced GPU Chatbot System Startup")
        print("=" * 60)
        print("📊 Chatbot Type: Enhanced GPU Optimized")
        print("🎯 Target Response Time: 5-15 seconds (with GPU)")
        print("📚 Documents Analyzed: 10 per query")
        print("🔧 Features: GPU acceleration, query expansion, hybrid search")
        print("=" * 60)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Start API server
        if not self.start_api_server():
            return False
        
        # Start frontend server
        if not self.start_frontend_server():
            self.stop_servers()
            return False
        
        # Start monitoring
        self.monitor_processes()
        
        # Display success message
        print("\n" + "=" * 60)
        print("🎉 Enhanced GPU Chatbot System Started Successfully!")
        print("=" * 60)
        print("📊 System Information:")
        print("   • Chatbot: Enhanced GPU Optimized")
        print("   • API Server: http://localhost:8001")
        print("   • Frontend: http://localhost:3000")
        print("   • Documents: 10 per query")
        print("   • Context: ~12,000 characters")
        print("   • Features: GPU acceleration, query expansion, hybrid search")
        print("")
        print("🔗 Quick Links:")
        print("   • Chat Interface: http://localhost:3000")
        print("   • API Documentation: http://localhost:8001/docs")
        print("   • Health Check: http://localhost:8001/health")
        print("")
        print("⏹️  Press Ctrl+C to stop all servers")
        print("=" * 60)
        
        # Keep running
        self.running = True
        try:
            while self.running:
                time.sleep(1)
                
                # Check if processes are still running
                if self.api_process and self.api_process.poll() is not None:
                    print("❌ API Server stopped unexpectedly")
                    break
                    
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend Server stopped unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested by user")
        finally:
            self.stop_servers()
            print("✅ Enhanced GPU Chatbot System stopped")

def main():
    """Main entry point"""
    system = EnhancedGPUSystem()
    
    try:
        success = system.run()
        if not success:
            print("❌ Failed to start Enhanced GPU Chatbot System")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 