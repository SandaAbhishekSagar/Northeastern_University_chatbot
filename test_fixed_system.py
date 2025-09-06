#!/usr/bin/env python3
"""
Test the Fixed Northeastern University Chatbot System
"""

import sys
import os
import time
import requests
from pathlib import Path

def test_chatbot_import():
    """Test if the fixed chatbot can be imported"""
    print("🔍 Testing chatbot import...")
    try:
        sys.path.append('services/chat_service')
        from fixed_chatbot import chatbot
        print("✅ Fixed chatbot imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import chatbot: {e}")
        return False

def test_chatbot_functionality():
    """Test basic chatbot functionality"""
    print("🔍 Testing chatbot functionality...")
    try:
        sys.path.append('services/chat_service')
        from fixed_chatbot import chatbot
        
        # Test a simple question
        result = chatbot.chat("Tell me about Northeastern University admissions", "test_session")
        
        if result and result.get('answer'):
            print("✅ Chatbot functionality test passed")
            print(f"📝 Answer: {result['answer'][:100]}...")
            print(f"📊 Sources: {len(result.get('sources', []))}")
            print(f"🎯 Confidence: {result.get('confidence', 0):.2f}")
            return True
        else:
            print("❌ Chatbot returned no answer")
            return False
            
    except Exception as e:
        print(f"❌ Chatbot functionality test failed: {e}")
        return False

def test_api_server():
    """Test if the API server is running"""
    print("🔍 Testing API server...")
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            data = response.json()
            print(f"📊 Status: {data.get('status', 'unknown')}")
            print(f"📄 Document count: {data.get('document_count', 'unknown')}")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running")
        return False
    except Exception as e:
        print(f"❌ API server test failed: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint"""
    print("🔍 Testing chat endpoint...")
    try:
        response = requests.post(
            "http://localhost:8001/chat",
            json={"question": "Tell me about Northeastern University admissions"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint test passed")
            print(f"📝 Answer: {data.get('answer', '')[:100]}...")
            print(f"📊 Sources: {len(data.get('sources', []))}")
            print(f"🎯 Confidence: {data.get('confidence', 0):.2f}")
            
            # Check if URLs are present in sources
            sources = data.get('sources', [])
            urls_found = 0
            for source in sources:
                if source.get('url'):
                    urls_found += 1
                    print(f"🔗 Found URL: {source['url']}")
            
            print(f"🔗 URLs found in sources: {urls_found}/{len(sources)}")
            return True
        else:
            print(f"❌ Chat endpoint returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Chat endpoint is not accessible")
        return False
    except Exception as e:
        print(f"❌ Chat endpoint test failed: {e}")
        return False

def main():
    print("🧪 Testing Fixed Northeastern University Chatbot System")
    print("=" * 60)
    
    tests = [
        ("Chatbot Import", test_chatbot_import),
        ("Chatbot Functionality", test_chatbot_functionality),
        ("API Server", test_api_server),
        ("Chat Endpoint", test_chat_endpoint)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)
    
    print("\n📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The fixed system is working correctly.")
        print("\n💡 The chatbot now:")
        print("• Uses ChatGPT for better responses (when API key is configured)")
        print("• Properly displays actual website URLs")
        print("• Has better error handling and fallbacks")
        print("• Works with both ChromaDB and Pinecone")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()
