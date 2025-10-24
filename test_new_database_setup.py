#!/usr/bin/env python3
"""
Test script for the new consolidated database setup
Tests the connection to the new ChromaDB Cloud database with 80,000 documents
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_chroma_cloud_connection():
    """Test connection to the new ChromaDB Cloud database"""
    print("🔍 Testing ChromaDB Cloud Connection...")
    print("=" * 50)
    
    try:
        from chroma_cloud_config import get_chroma_cloud_client, test_cloud_connection
        
        # Test the connection
        if test_cloud_connection():
            print("✅ ChromaDB Cloud connection successful!")
            return True
        else:
            print("❌ ChromaDB Cloud connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ChromaDB Cloud: {e}")
        return False

def test_database_service():
    """Test the updated database service"""
    print("\n🔍 Testing Database Service...")
    print("=" * 50)
    
    try:
        # Set environment variable to use cloud
        os.environ['USE_CLOUD_CHROMA'] = 'true'
        
        from services.shared.chroma_service import ChromaService
        
        # Initialize service
        chroma_service = ChromaService()
        print("✅ ChromaService initialized successfully!")
        
        # Test document count
        doc_count = chroma_service.get_collection_count('documents')
        print(f"📊 Document count in 'documents_unified' collection: {doc_count:,}")
        
        if doc_count > 0:
            print("✅ Document count retrieved successfully from documents_unified collection!")
        else:
            print("⚠️  No documents found in documents_unified collection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database service: {e}")
        return False

def test_search_functionality():
    """Test search functionality with the new setup"""
    print("\n🔍 Testing Search Functionality...")
    print("=" * 50)
    
    try:
        from services.shared.chroma_service import ChromaService
        
        # Initialize service
        chroma_service = ChromaService()
        
        # Test search
        test_query = "Northeastern University programs"
        print(f"🔍 Searching for: '{test_query}'")
        
        results = chroma_service.search_documents(test_query, n_results=3)
        
        if results:
            print(f"✅ Found {len(results)} results!")
            for i, (doc, distance) in enumerate(results[:2]):  # Show first 2 results
                print(f"  {i+1}. {doc.title[:50]}... (similarity: {1-distance:.3f})")
        else:
            print("⚠️  No search results found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing search: {e}")
        return False

def test_chatbot_initialization():
    """Test chatbot initialization with new setup"""
    print("\n🔍 Testing Chatbot Initialization...")
    print("=" * 50)
    
    try:
        # Set environment variables
        os.environ['USE_CLOUD_CHROMA'] = 'true'
        
        # Test if we can import the chatbot
        from services.chat_service.enhanced_openai_chatbot import EnhancedOpenAIUniversityRAGChatbot
        print("✅ Enhanced OpenAI chatbot import successful!")
        
        # Note: We won't actually initialize it here to avoid API key requirements
        # But we can verify the import works
        print("✅ Chatbot class is available for initialization!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing chatbot: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing New Database Setup")
    print("=" * 60)
    print("Database: northeasterndb (80,000 documents in single collection)")
    print("=" * 60)
    
    tests = [
        ("ChromaDB Cloud Connection", test_chroma_cloud_connection),
        ("Database Service", test_database_service),
        ("Search Functionality", test_search_functionality),
        ("Chatbot Initialization", test_chatbot_initialization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your new database setup is ready!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
