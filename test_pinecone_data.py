#!/usr/bin/env python3
"""
Test Pinecone data and search functionality
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append('.')

def test_pinecone_search():
    """Test Pinecone search functionality"""
    print("🔍 Testing Pinecone search...")
    
    try:
        from pinecone import Pinecone
        
        # Get API key
        api_key = os.environ.get('PINECONE_API_KEY')
        if not api_key:
            print("❌ PINECONE_API_KEY not found")
            return False
        
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        index = pc.Index("northeastern-university")
        
        # Get index stats
        stats = index.describe_index_stats()
        print(f"📊 Index stats: {stats}")
        
        # Test search
        from sentence_transformers import SentenceTransformer
        
        # Load embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Test queries
        test_queries = [
            "Northeastern University admissions requirements",
            "co-op program information",
            "graduate programs",
            "financial aid",
            "student life"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            
            # Generate embedding
            embedding = model.encode([query])[0].tolist()
            
            # Search
            results = index.query(
                vector=embedding,
                top_k=3,
                include_metadata=True
            )
            
            if results.matches:
                print(f"✅ Found {len(results.matches)} results:")
                for i, match in enumerate(results.matches):
                    print(f"  {i+1}. Score: {match.score:.3f}")
                    print(f"     URL: {match.metadata.get('url', 'N/A')}")
                    print(f"     Title: {match.metadata.get('title', 'N/A')}")
                    print(f"     Content: {match.metadata.get('content', 'N/A')[:100]}...")
            else:
                print("❌ No results found")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Pinecone Data Test")
    print("=" * 40)
    
    if test_pinecone_search():
        print("\n🎉 Pinecone data test completed successfully!")
    else:
        print("\n❌ Pinecone data test failed")

if __name__ == "__main__":
    main()
