#!/usr/bin/env python3
"""
Script to inspect ChromaDB data and understand document quality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.shared.database import get_chroma_client, get_collection
from services.shared.config import config

def inspect_chromadb_data():
    """Inspect ChromaDB data to understand document quality and content"""
    print("ChromaDB Data Inspection")
    print("=" * 50)
    
    try:
        # Get ChromaDB client
        client = get_chroma_client()
        print("✅ ChromaDB client connected")
        
        # Get documents collection
        documents_collection = get_collection('documents')
        
        # Get all documents
        result = documents_collection.get()
        
        if not result or not result.get('ids'):
            print("❌ No documents found in ChromaDB!")
            return
        
        print(f"\n📊 Document Statistics:")
        print(f"   Total Documents: {len(result['ids'])}")
        
        # Analyze document content
        print(f"\n📄 Document Content Analysis:")
        
        # Sample a few documents
        sample_size = min(5, len(result['ids']))
        print(f"   Showing {sample_size} sample documents:")
        
        for i in range(sample_size):
            doc_id = result['ids'][i]
            content = result['documents'][i]
            metadata = result['metadatas'][i]
            
            print(f"\n   Document {i+1}:")
            print(f"   ID: {doc_id}")
            print(f"   Title: {metadata.get('title', 'No title')}")
            print(f"   Source: {metadata.get('source_url', 'No source')}")
            print(f"   Content Length: {len(content)} characters")
            print(f"   Word Count: {len(content.split())} words")
            
            # Show first 200 characters of content
            preview = content[:200] + "..." if len(content) > 200 else content
            print(f"   Content Preview: {preview}")
            
            # Check for Northeastern-specific content
            content_lower = content.lower()
            northeastern_terms = ['northeastern', 'neu', 'boston', 'co-op', 'cooperative']
            term_count = sum(1 for term in northeastern_terms if term in content_lower)
            print(f"   Northeastern Terms: {term_count}")
        
        # Check universities collection
        print(f"\n🏫 Universities Collection:")
        universities_collection = get_collection('universities')
        univ_result = universities_collection.get()
        
        if univ_result and univ_result.get('ids'):
            print(f"   Universities Found: {len(univ_result['ids'])}")
            for i, univ_id in enumerate(univ_result['ids']):
                univ_metadata = univ_result['metadatas'][i]
                print(f"   {i+1}. {univ_metadata.get('name', 'Unknown')} - {univ_metadata.get('base_url', 'No URL')}")
        else:
            print("   ❌ No universities found")
        
        # Check for embeddings
        print(f"\n🔍 Embedding Analysis:")
        if result.get('embeddings'):
            embedding_dim = len(result['embeddings'][0])
            print(f"   Embeddings Found: ✅")
            print(f"   Embedding Dimension: {embedding_dim}")
            print(f"   Documents with Embeddings: {len([e for e in result['embeddings'] if e])}")
        else:
            print("   ❌ No embeddings found - this may affect search quality!")
        
        # Content quality indicators
        print(f"\n📈 Content Quality Indicators:")
        
        # Check for very short documents
        documents = result.get('documents', [])
        short_docs = [doc for doc in documents if len(doc.split()) < 10]
        print(f"   Very Short Documents (<10 words): {len(short_docs)}")
        
        # Check for very long documents
        long_docs = [doc for doc in documents if len(doc.split()) > 1000]
        print(f"   Very Long Documents (>1000 words): {len(long_docs)}")
        
        # Check for duplicate content
        unique_contents = set(documents)
        print(f"   Unique Documents: {len(unique_contents)}")
        print(f"   Duplicate Documents: {len(documents) - len(unique_contents)}")
        
        # Check for empty or near-empty documents
        empty_docs = [doc for doc in documents if len(doc.strip()) < 5]
        print(f"   Empty/Near-Empty Documents: {len(empty_docs)}")
        
        print(f"\n✅ Data inspection complete!")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if len(short_docs) > len(result['documents']) * 0.1:
            print("   ⚠️  Many short documents - consider filtering out very short content")
        if len(empty_docs) > 0:
            print("   ⚠️  Empty documents found - consider cleaning the database")
        if not result['embeddings']:
            print("   ⚠️  No embeddings found - regenerate embeddings for better search")
        if len(unique_contents) < len(result['documents']) * 0.8:
            print("   ⚠️  Many duplicate documents - consider deduplication")
        
        print("   ✅ Data looks good for chatbot use!")
        
    except Exception as e:
        print(f"❌ Error inspecting ChromaDB data: {e}")

if __name__ == "__main__":
    inspect_chromadb_data() 