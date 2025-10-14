#!/usr/bin/env python3
"""
Debug the quota issue by examining the actual data being uploaded
"""

import chromadb
import json

def debug_collection_sizes(collection_name: str, local_path: str = "./chroma_data"):
    """Debug the actual sizes of documents in the ultra-optimized collection"""
    
    client = chromadb.PersistentClient(path=local_path)
    collection = client.get_collection(collection_name)
    
    print(f"🔍 Debugging {collection_name} collection...")
    
    # Get a sample of documents
    sample_data = collection.get(limit=1000, include=['documents', 'metadatas'])
    
    total_docs = len(sample_data['ids'])
    print(f"📊 Sample size: {total_docs} documents")
    
    # Check sizes
    sizes = []
    large_docs = []
    
    for i, (doc_id, document, metadata) in enumerate(zip(
        sample_data['ids'], sample_data['documents'], sample_data['metadatas']
    )):
        if i % 100 == 0:
            print(f"🔄 Checking document {i+1}/{total_docs}")
        
        # Calculate total size (document + metadata)
        doc_size = len(document.encode('utf-8')) if document else 0
        meta_size = len(json.dumps(metadata).encode('utf-8')) if metadata else 0
        total_size = doc_size + meta_size
        
        sizes.append(total_size)
        
        if total_size > 16384:  # Chroma Cloud limit
            large_docs.append({
                'id': doc_id,
                'doc_size': doc_size,
                'meta_size': meta_size,
                'total_size': total_size,
                'metadata_keys': list(metadata.keys()) if metadata else []
            })
    
    # Statistics
    if sizes:
        avg_size = sum(sizes) / len(sizes)
        max_size = max(sizes)
        min_size = min(sizes)
        
        print(f"\n📊 Size Statistics:")
        print(f"  Average: {avg_size:.0f} bytes")
        print(f"  Maximum: {max_size} bytes")
        print(f"  Minimum: {min_size} bytes")
        print(f"  Large docs (>16KB): {len(large_docs)}")
        
        if large_docs:
            print(f"\n🔍 Documents exceeding 16KB:")
            # Sort by size and show top 10
            large_docs.sort(key=lambda x: x['total_size'], reverse=True)
            for i, doc in enumerate(large_docs[:10]):
                print(f"  {i+1}. ID: {doc['id'][:50]}...")
                print(f"     Total: {doc['total_size']} bytes (doc: {doc['doc_size']}, meta: {doc['meta_size']})")
                print(f"     Metadata keys: {doc['metadata_keys']}")
                print()
        
        # Check if there are any documents close to the limit
        close_to_limit = [s for s in sizes if s > 15000]
        print(f"📊 Documents close to limit (>15KB): {len(close_to_limit)}")
        
        if close_to_limit:
            print(f"  Sizes: {sorted(close_to_limit, reverse=True)[:10]}")
    
    return large_docs

if __name__ == "__main__":
    print("🔍 Debugging quota issue in ultra-optimized collection...")
    print("=" * 60)
    
    # Debug the ultra-optimized collection
    large_docs = debug_collection_sizes("documents_ultra_optimized")
    
    if large_docs:
        print(f"\n⚠️  Found {len(large_docs)} documents still exceeding Chroma Cloud limits")
        print("💡 These documents need even more aggressive optimization")
    else:
        print("\n✅ All sample documents are within Chroma Cloud size limits")
        print("🤔 The quota error might be due to other factors")
    
    print("\n" + "=" * 60)

