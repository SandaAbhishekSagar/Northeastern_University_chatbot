#!/usr/bin/env python3
"""
Simple health check test script
"""

import requests
import time
import sys

def test_health():
    """Test the health endpoint"""
    try:
        print("🔍 Testing health endpoint...")
        response = requests.get("http://localhost:8001/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Health endpoint working!")
            print(f"   Status: {response.json().get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health test failed: {e}")
        return False

if __name__ == "__main__":
    # Wait a moment for server to be ready
    print("⏳ Waiting for server...")
    time.sleep(5)
    
    success = test_health()
    sys.exit(0 if success else 1)
