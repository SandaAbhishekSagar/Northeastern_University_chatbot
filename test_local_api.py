#!/usr/bin/env python3
"""
Test script to verify the fixed API works locally
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required imports work"""
    print("🔍 Testing imports...")
    
    try:
        # Test basic imports
        import fastapi
        print("✅ FastAPI imported successfully")
        
        import uvicorn
        print("✅ Uvicorn imported successfully")
        
        # Test our fixed API
        sys.path.append('.')
        from services.chat_service.fixed_api import app
        print("✅ Fixed API imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    
    try:
        from services.chat_service.fixed_api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint"""
    print("🔍 Testing chat endpoint...")
    
    try:
        from services.chat_service.fixed_api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.post("/chat", json={
            "message": "Hello, what is Northeastern University?",
            "session_id": "test_session"
        })
        
        if response.status_code == 200:
            print("✅ Chat endpoint working")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat endpoint test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Fixed Northeastern University Chatbot API")
    print("=" * 60)
    
    # Check environment
    if not Path("services").exists():
        print("❌ Error: services directory not found")
        print(f"   Current directory: {os.getcwd()}")
        sys.exit(1)
    
    # Create basic .env if it doesn't exist
    if not Path(".env").exists():
        print("⚠️  Creating basic .env file...")
        with open(".env", "w") as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        print("✅ Created basic .env file")
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_imports():
        tests_passed += 1
    
    if test_health_endpoint():
        tests_passed += 1
    
    if test_chat_endpoint():
        tests_passed += 1
    
    print("=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The API is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
