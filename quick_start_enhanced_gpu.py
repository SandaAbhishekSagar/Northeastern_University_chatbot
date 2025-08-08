#!/usr/bin/env python3
"""
Quick Start Script for Enhanced GPU System
This script provides an easy way to start the enhanced GPU chatbot system
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_system_requirements():
    """Check if system meets requirements for enhanced GPU system"""
    print("🔍 Checking System Requirements")
    print("=" * 40)
    
    requirements_met = True
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        print(f"❌ Python 3.9+ required, found {python_version.major}.{python_version.minor}")
        requirements_met = False
    else:
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check virtual environment
    venv_path = Path("env_py3.9")
    if venv_path.exists():
        print("✅ Virtual environment found")
    else:
        print("❌ Virtual environment not found")
        requirements_met = False
    
    # Check required files
    required_files = [
        "start_enhanced_gpu_system.py",
        "services/chat_service/enhanced_gpu_api.py",
        "frontend/server.py"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} not found")
            requirements_met = False
    
    # Check GPU availability (optional)
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU available: {gpu_name} ({gpu_count} device(s))")
        else:
            print("⚠️  GPU not available (will use CPU)")
    except ImportError:
        print("⚠️  PyTorch not installed (GPU check skipped)")
    
    # Check embedding cache
    cache_files = [
        "enhanced_embeddings_cache.pkl",
        "embeddings_cache.pkl"
    ]
    
    cache_found = False
    for cache_file in cache_files:
        if Path(cache_file).exists():
            size_mb = Path(cache_file).stat().st_size / (1024 * 1024)
            print(f"✅ Cache found: {cache_file} ({size_mb:.1f} MB)")
            cache_found = True
            break
    
    if not cache_found:
        print("⚠️  No embedding cache found (will be created on first run)")
    
    return requirements_met

def check_ports():
    """Check if required ports are available"""
    print("\n🔌 Checking Port Availability")
    print("=" * 30)
    
    import socket
    
    ports_to_check = [8001, 3000]
    available_ports = []
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            print(f"✅ Port {port} available")
            available_ports.append(port)
        except OSError:
            print(f"❌ Port {port} in use")
        finally:
            sock.close()
    
    return len(available_ports) == len(ports_to_check)

def start_enhanced_gpu_system():
    """Start the enhanced GPU system"""
    print("\n🚀 Starting Enhanced GPU System")
    print("=" * 40)
    
    try:
        # Run the enhanced GPU system
        process = subprocess.Popen([
            sys.executable, "start_enhanced_gpu_system.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Wait a moment for startup
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Enhanced GPU system started successfully")
            print("\n🌐 Access Points:")
            print("   • Chat Interface: http://localhost:3000")
            print("   • API Documentation: http://localhost:8001/docs")
            print("   • Health Check: http://localhost:8001/health")
            print("\n⏹️  Press Ctrl+C to stop the system")
            
            # Monitor the process
            try:
                while process.poll() is None:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping Enhanced GPU System...")
                process.terminate()
                process.wait()
                print("✅ System stopped")
        else:
            print("❌ Failed to start Enhanced GPU system")
            return False
            
    except Exception as e:
        print(f"❌ Error starting system: {e}")
        return False
    
    return True

def show_alternatives():
    """Show alternative startup options"""
    print("\n🔄 Alternative Startup Options")
    print("=" * 35)
    
    alternatives = [
        ("Standard System", "python start_system.py"),
        ("OpenAI System", "python run_openai_frontend.py"),
        ("Manual API + Frontend", "See guide for manual startup")
    ]
    
    for i, (name, command) in enumerate(alternatives, 1):
        print(f"{i}. {name}: {command}")
    
    print("\n💡 If Enhanced GPU system fails, try one of these alternatives")

def main():
    """Main function"""
    print("🚀 Enhanced GPU System Quick Start")
    print("=" * 50)
    print("This script will help you start the enhanced GPU chatbot system")
    print("with all the advanced features and optimizations.")
    print()
    
    # Check system requirements
    if not check_system_requirements():
        print("\n❌ System requirements not met!")
        print("Please fix the issues above before continuing.")
        show_alternatives()
        return
    
    # Check port availability
    if not check_ports():
        print("\n❌ Required ports are not available!")
        print("Please stop any services using ports 8001 and 3000.")
        print("Or use alternative startup methods.")
        show_alternatives()
        return
    
    # Ask user if they want to proceed
    print("\n" + "=" * 50)
    print("🎯 Ready to start Enhanced GPU System!")
    print("=" * 50)
    print("Features you'll get:")
    print("   • GPU acceleration (if available)")
    print("   • Enhanced RAG pipeline")
    print("   • Query expansion")
    print("   • Hybrid search")
    print("   • Optimized embeddings")
    print("   • Better performance")
    print()
    
    response = input("Start the Enhanced GPU System? (y/n): ").strip().lower()
    
    if response in ['y', 'yes']:
        success = start_enhanced_gpu_system()
        if not success:
            print("\n❌ Failed to start Enhanced GPU System")
            show_alternatives()
    else:
        print("\n👋 Enhanced GPU System startup cancelled")
        show_alternatives()

if __name__ == "__main__":
    main() 