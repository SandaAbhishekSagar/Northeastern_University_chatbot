#!/usr/bin/env python3
"""
Test script for the University Chatbot System
"""

import requests
import json
import time

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get("http://localhost:8001/")
        print(f"API Health: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"API Health Check Failed: {e}")
        return False

def test_chat():
    """Test the chat functionality"""
    try:
        chat_data = {
            "question": "What programs does Northeastern University offer?",
            "session_id": "test-session-123"
        }
        
        response = requests.post("http://localhost:8001/chat", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Chat Response: {result['answer']}")
            print(f"Sources: {len(result['sources'])} documents found")
            print(f"Confidence: {result['confidence']:.2f}")
            return True
        else:
            print(f"Chat request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Chat test failed: {e}")
        return False

def test_search():
    """Test document search"""
    try:
        response = requests.get("http://localhost:8001/search?query=northeastern university&k=3")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Search found {len(result['documents'])} documents")
            for doc in result['documents']:
                print(f"  - {doc['title']} (similarity: {doc['similarity']:.3f})")
            return True
        else:
            print(f"Search request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Search test failed: {e}")
        return False

def main():
    print("Testing University Chatbot System")
    print("=" * 40)
    
    # Test API health
    print("\n1. Testing API Health...")
    if not test_api_health():
        print("❌ API is not running. Please start it with: python run.py api")
        return
    print("✅ API is healthy")
    
    # Test search functionality
    print("\n2. Testing Document Search...")
    if test_search():
        print("✅ Search is working")
    else:
        print("❌ Search failed - may need to scrape and process documents first")
    
    # Test chat functionality
    print("\n3. Testing Chat...")
    if test_chat():
        print("✅ Chat is working")
    else:
        print("❌ Chat failed - may need to scrape and process documents first")
    
    print("\n" + "=" * 40)
    print("Testing complete!")

if __name__ == "__main__":
    main()