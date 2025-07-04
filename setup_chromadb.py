#!/usr/bin/env python3
"""
Setup script for ChromaDB-based University Chatbot
"""

import sys
import subprocess
import time
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a command and handle output"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True
        )
        if check and result.returncode != 0:
            print(f"Error running command: {command}")
            print(f"Error output: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running command {command}: {e}")
        return False

def check_docker():
    """Check if Docker is running"""
    print("Checking Docker...")
    if run_command("docker --version", check=False):
        print("✅ Docker is available")
        return True
    else:
        print("❌ Docker not found. Please install Docker first.")
        return False

def start_chromadb():
    """Start ChromaDB using Docker Compose"""
    print("Starting ChromaDB...")
    if run_command("docker-compose up -d chromadb"):
        print("✅ ChromaDB started")
        # Wait a bit for ChromaDB to be ready
        print("Waiting for ChromaDB to be ready...")
        time.sleep(5)
        return True
    else:
        print("❌ Failed to start ChromaDB")
        return False

def test_chromadb_connection():
    """Test ChromaDB connection"""
    print("Testing ChromaDB connection...")
    try:
        # Import and test ChromaDB connection
        sys.path.insert(0, str(Path(__file__).parent))
        from services.shared.database import test_connection
        
        if test_connection():
            print("✅ ChromaDB connection successful")
            return True
        else:
            print("❌ ChromaDB connection failed")
            return False
    except Exception as e:
        print(f"❌ Error testing ChromaDB: {e}")
        return False

def setup_collections():
    """Initialize ChromaDB collections"""
    print("Setting up ChromaDB collections...")
    if run_command("python services/shared/database.py"):
        print("✅ Collections initialized")
        return True
    else:
        print("❌ Failed to initialize collections")
        return False

def test_models():
    """Test the data models"""
    print("Testing data models...")
    if run_command("python services/shared/models.py"):
        print("✅ Models test passed")
        return True
    else:
        print("❌ Models test failed")
        return False

def test_service():
    """Test the ChromaDB service"""
    print("Testing ChromaDB service...")
    if run_command("python services/shared/chroma_service.py"):
        print("✅ Service test passed")
        return True
    else:
        print("❌ Service test failed")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    if run_command("pip install -r requirements.txt"):
        print("✅ Dependencies installed")
        return True
    else:
        print("❌ Failed to install dependencies")
        return False

def main():
    print("ChromaDB University Chatbot Setup")
    print("=" * 40)
    
    # Check Docker
    if not check_docker():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Start ChromaDB
    if not start_chromadb():
        return
    
    # Test connection
    if not test_chromadb_connection():
        print("\nTroubleshooting:")
        print("1. Make sure Docker is running")
        print("2. Check if port 8000 is available")
        print("3. Try: docker-compose logs chromadb")
        return
    
    # Setup collections
    if not setup_collections():
        return
    
    # Test models
    if not test_models():
        return
    
    # Test service
    if not test_service():
        return
    
    print("\n" + "=" * 40)
    print("✅ Setup complete! ChromaDB is ready to use.")
    print("\nNext steps:")
    print("1. Start the API server: python run.py api")
    print("2. Start the worker: python run.py worker")
    print("3. Start the scheduler: python run.py beat")
    print("4. Run the scraper: python run.py scrape")
    print("5. Test the system: python test_system.py")

if __name__ == "__main__":
    main() 