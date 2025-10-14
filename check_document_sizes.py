#!/usr/bin/env python3
"""
Check actual document sizes in ChromaDB collections
"""

import chromadb
import json

def check_collection_sizes(collection_name: str, local_path: str = "./chroma_data"):
    """Check the actual sizes of documents in a collection"""
    
    client = chromadb.PersistentClient(path=local_path)
    collection = client.get_collection(collection_name)
    
    print(f"🔍 Checking {collection_name} collection...")
    
    # Get all documents
    all_data = collection.get(include=['documents', 'metadatas'])
    
    total_docs = len(all_data['ids'])
    print(f"📊 Total documents: {total_docs}")
    
    # Check sizes
    sizes = []
    large_docs = []
    
    for i, (doc_id, document, metadata) in enumerate(zip(
        all_data['ids'], all_data['documents'], all_data['metadatas']
    )):
        if i % 1000 == 0:
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
            print(f"\n🔍 Largest documents:")
            # Sort by size and show top 5
            large_docs.sort(key=lambda x: x['total_size'], reverse=True)
            for i, doc in enumerate(large_docs[:5]):
                print(f"  {i+1}. ID: {doc['id'][:50]}...")
                print(f"     Total: {doc['total_size']} bytes (doc: {doc['doc_size']}, meta: {doc['meta_size']})")
                print(f"     Metadata keys: {doc['metadata_keys']}")
                print()
    
    return large_docs

if __name__ == "__main__":
    print("🔍 Checking document sizes in ChromaDB collections...")
    print("=" * 60)
    
    # Check documents collection
    large_docs = check_collection_sizes("documents")
    
    if large_docs:
        print(f"\n⚠️  Found {len(large_docs)} documents exceeding Chroma Cloud limits")
        print("💡 These documents need to be chunked or optimized")
    else:
        print("\n✅ All documents are within Chroma Cloud size limits")
    
    print("\n" + "=" * 60)

