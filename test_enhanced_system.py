#!/usr/bin/env python3
"""
Test Enhanced University Chatbot System
Demonstrates the improved semantic search and answer generation features
"""

import requests
import json
import time
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8001"  # Updated port

def test_enhanced_health():
    """Test enhanced health endpoint"""
    print("🔍 Testing Enhanced Health Check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health/enhanced")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Status: {data['status']}")
            print(f"📋 Message: {data['message']}")
            print("🚀 Features:")
            for feature, status in data['features'].items():
                print(f"   - {feature}: {status}")
            if 'test' in data:
                print(f"🧪 Query Expansion Test: {data['test']['query_expansion_working']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_query_expansion():
    """Test query expansion feature"""
    print("\n🔍 Testing Query Expansion...")
    test_queries = [
        "admission requirements",
        "co-op program",
        "tuition fees",
        "graduate programs"
    ]
    
    for query in test_queries:
        try:
            response = requests.get(f"{API_BASE_URL}/search/expand", params={"query": query})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Query: '{data['original_query']}'")
                print(f"   Expanded to {len(data['expanded_queries'])} queries:")
                for i, expanded in enumerate(data['expanded_queries'], 1):
                    print(f"   {i}. {expanded}")
            else:
                print(f"❌ Query expansion failed for '{query}': {response.status_code}")
        except Exception as e:
            print(f"❌ Query expansion error for '{query}': {e}")

def test_hybrid_search():
    """Test hybrid search functionality"""
    print("\n🔍 Testing Hybrid Search...")
    test_queries = [
        "computer science admission",
        "cooperative education program",
        "financial aid scholarships",
        "campus housing options"
    ]
    
    for query in test_queries:
        try:
            response = requests.get(f"{API_BASE_URL}/search", params={"query": query, "k": 3})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Query: '{query}'")
                print(f"   Found {len(data['documents'])} documents:")
                for i, doc in enumerate(data['documents'], 1):
                    similarity = doc.get('combined_score', doc.get('similarity', 0))
                    search_type = doc.get('search_type', 'unknown')
                    print(f"   {i}. {doc['title'][:50]}... (score: {similarity:.3f}, type: {search_type})")
            else:
                print(f"❌ Hybrid search failed for '{query}': {response.status_code}")
        except Exception as e:
            print(f"❌ Hybrid search error for '{query}': {e}")

def test_semantic_search():
    """Test semantic search only"""
    print("\n🔍 Testing Semantic Search...")
    test_queries = [
        "machine learning courses",
        "international student services",
        "research opportunities"
    ]
    
    for query in test_queries:
        try:
            response = requests.get(f"{API_BASE_URL}/search/semantic", params={"query": query, "k": 2})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Query: '{query}'")
                print(f"   Found {len(data['documents'])} documents:")
                for i, doc in enumerate(data['documents'], 1):
                    similarity = doc.get('similarity', 0)
                    print(f"   {i}. {doc['title'][:50]}... (similarity: {similarity:.3f})")
            else:
                print(f"❌ Semantic search failed for '{query}': {response.status_code}")
        except Exception as e:
            print(f"❌ Semantic search error for '{query}': {e}")

def test_enhanced_chat():
    """Test enhanced chat functionality"""
    print("\n🔍 Testing Enhanced Chat...")
    test_questions = [
        "What are the admission requirements for computer science?",
        "How does the co-op program work at Northeastern?",
        "What is the tuition for international students?",
        "Tell me about campus housing options"
    ]
    
    session_id = f"test_session_{int(time.time())}"
    
    for i, question in enumerate(test_questions, 1):
        try:
            print(f"\n💬 Question {i}: {question}")
            
            response = requests.post(f"{API_BASE_URL}/chat", json={
                "question": question,
                "session_id": session_id
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Answer: {data['answer'][:200]}...")
                print(f"📊 Confidence: {data['confidence']:.3f}")
                print(f"📚 Sources: {len(data['sources'])} documents")
                
                # Show top source
                if data['sources']:
                    top_source = data['sources'][0]
                    print(f"   Top source: {top_source['title'][:50]}... (similarity: {top_source['similarity']:.3f})")
                
                # Show search queries if available
                if 'search_queries' in data:
                    print(f"🔍 Search queries used: {len(data['search_queries'])}")
                    for j, query in enumerate(data['search_queries'][:2], 1):
                        print(f"   {j}. {query}")
                
            else:
                print(f"❌ Chat failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Chat error: {e}")
        
        # Small delay between requests
        time.sleep(1)

def test_conversation_history():
    """Test conversation history"""
    print("\n🔍 Testing Conversation History...")
    session_id = f"history_test_{int(time.time())}"
    
    # Send a few messages
    questions = [
        "What programs does Northeastern offer?",
        "Tell me more about the computer science program",
        "What are the admission requirements?"
    ]
    
    for question in questions:
        try:
            response = requests.post(f"{API_BASE_URL}/chat", json={
                "question": question,
                "session_id": session_id
            })
            if response.status_code != 200:
                print(f"❌ Failed to send message: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending message: {e}")
        time.sleep(0.5)
    
    # Get conversation history
    try:
        response = requests.get(f"{API_BASE_URL}/chat/history/{session_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conversation history retrieved: {len(data['history'])} messages")
            for msg in data['history'][-3:]:  # Show last 3 messages
                role = "👤 User" if msg['type'] == 'user' else "🤖 Assistant"
                print(f"   {role}: {msg['content'][:100]}...")
        else:
            print(f"❌ Failed to get history: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting history: {e}")

def main():
    """Run all enhanced system tests"""
    print("🚀 Enhanced University Chatbot System Test")
    print("=" * 50)
    
    # Test health first
    if not test_enhanced_health():
        print("❌ Health check failed. Make sure the API server is running on port 8001")
        return
    
    # Run all tests
    test_query_expansion()
    test_hybrid_search()
    test_semantic_search()
    test_enhanced_chat()
    test_conversation_history()
    
    print("\n" + "=" * 50)
    print("✅ Enhanced system test completed!")
    print("\n🎯 Key Improvements Demonstrated:")
    print("   • Query expansion with synonyms and related terms")
    print("   • Hybrid search combining semantic and keyword matching")
    print("   • Enhanced confidence scoring")
    print("   • Conversation history tracking")
    print("   • Better source attribution")
    print("   • Northeastern University-specific optimizations")

if __name__ == "__main__":
    main() 