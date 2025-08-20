#!/usr/bin/env python3
"""
Test Pinecone Integration
Verify that the Pinecone database is working correctly
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def test_pinecone_connection():
    """Test basic Pinecone connection"""
    print("🌲 Testing Pinecone Connection...")
    
    try:
        from services.shared.database import get_database_type, get_pinecone_index, get_pinecone_count
        
        # Check database type
        db_type = get_database_type()
        print(f"✅ Database type: {db_type}")
        
        if db_type != "pinecone":
            print("❌ Not using Pinecone - check PINECONE_API_KEY environment variable")
            return False
        
        # Test index connection
        index = get_pinecone_index()
        print("✅ Pinecone index connection successful")
        
        # Get document count
        count = get_pinecone_count()
        print(f"✅ Document count: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return False

def test_pinecone_query():
    """Test Pinecone query functionality"""
    print("\n🔍 Testing Pinecone Query...")
    
    try:
        from services.shared.database import query_pinecone
        
        # Test query
        test_query = "northeastern university courses"
        results = query_pinecone(test_query, n_results=5)
        
        print(f"✅ Query successful for: '{test_query}'")
        print(f"📊 Found {len(results['ids'])} results")
        
        if results['ids']:
            print("📄 Sample results:")
            for i, (doc_id, distance) in enumerate(zip(results['ids'][:3], results['distances'][:3])):
                print(f"  {i+1}. ID: {doc_id[:20]}... (score: {distance:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Pinecone query failed: {e}")
        return False

def test_api_integration():
    """Test API integration with Pinecone"""
    print("\n🚀 Testing API Integration...")
    
    try:
        from services.chat_service.enhanced_gpu_api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health/enhanced")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check successful")
            print(f"📊 Database type: {data['features']['database_type']}")
            print(f"📄 Document count: {data['features']['document_count']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Pinecone Integration Test Suite")
    print("=" * 50)
    
    # Check if API key is set
    if not os.environ.get("PINECONE_API_KEY"):
        print("❌ PINECONE_API_KEY not found in environment")
        print("💡 Set it with: $env:PINECONE_API_KEY='your_key_here'")
        return
    
    # Run tests
    tests = [
        ("Connection", test_pinecone_connection),
        ("Query", test_pinecone_query),
        ("API Integration", test_api_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔧 Running {test_name} Test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test passed")
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Pinecone integration is working correctly.")
        print("🚀 Ready for deployment to Railway!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 