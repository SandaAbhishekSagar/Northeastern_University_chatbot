#!/usr/bin/env python3
"""
Simple test script to verify the health endpoint works
"""

import requests
import time
import sys

def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    
    try:
        # Test local endpoint
        response = requests.get("http://localhost:8001/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Health endpoint working!")
            print(f"   Status: {response.json().get('status', 'unknown')}")
            print(f"   Message: {response.json().get('message', 'no message')}")
            print(f"   Database: {response.json().get('database_type', 'unknown')}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running?")
        print("   Try: python -m uvicorn services.chat_service.fixed_api:app --host 0.0.0.0 --port 8001")
        return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("🔍 Testing root endpoint...")
    
    try:
        response = requests.get("http://localhost:8001/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Root endpoint working!")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Root endpoint test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Health Endpoints")
    print("=" * 40)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    tests_passed = 0
    total_tests = 2
    
    if test_health_endpoint():
        tests_passed += 1
    
    if test_root_endpoint():
        tests_passed += 1
    
    print("=" * 40)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All health endpoint tests passed!")
        return True
    else:
        print("❌ Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
