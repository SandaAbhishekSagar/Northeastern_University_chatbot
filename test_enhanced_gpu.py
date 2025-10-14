#!/usr/bin/env python3
"""
Test script for Enhanced GPU Chatbot System
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path.cwd()))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        print("  - Testing basic imports...")
        import fastapi
        import uvicorn
        import langchain
        print("  ✅ Basic imports successful")
        
        print("  - Testing enhanced GPU chatbot...")
        from services.chat_service.enhanced_gpu_chatbot import EnhancedGPUUniversityRAGChatbot
        print("  ✅ Enhanced GPU chatbot imported")
        
        print("  - Testing API...")
        from services.chat_service.enhanced_gpu_api import app
        print("  ✅ Enhanced GPU API imported")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_chatbot_initialization():
    """Test if the chatbot can be initialized"""
    print("\n🤖 Testing chatbot initialization...")
    
    try:
        from services.chat_service.enhanced_gpu_chatbot import EnhancedGPUUniversityRAGChatbot
        chatbot = EnhancedGPUUniversityRAGChatbot()
        print("  ✅ Enhanced GPU chatbot initialized successfully")
        print(f"  📱 Device: {chatbot.embedding_manager.device}")
        return True
        
    except Exception as e:
        print(f"  ❌ Chatbot initialization failed: {e}")
        return False

def test_api_initialization():
    """Test if the API can be initialized"""
    print("\n🌐 Testing API initialization...")
    
    try:
        from services.chat_service.enhanced_gpu_api import app
        print("  ✅ Enhanced GPU API initialized successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ API initialization failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Enhanced GPU Chatbot System Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check dependencies.")
        return False
    
    # Test chatbot initialization
    if not test_chatbot_initialization():
        print("\n❌ Chatbot initialization failed.")
        return False
    
    # Test API initialization
    if not test_api_initialization():
        print("\n❌ API initialization failed.")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Enhanced GPU system is ready.")
    print("=" * 50)
    print("You can now run:")
    print("  python -m uvicorn services.chat_service.enhanced_gpu_api:app --host 0.0.0.0 --port 8001")
    print("  python frontend/server.py")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

