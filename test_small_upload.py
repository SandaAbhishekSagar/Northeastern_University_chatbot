#!/usr/bin/env python3
"""
Test uploading a very small batch to Chroma Cloud
"""

import chromadb
import json

def test_small_upload():
    """Test uploading a very small batch to see if it works"""
    
    print("🧪 Testing small upload to Chroma Cloud...")
    
    # Connect to local ChromaDB
    local_client = chromadb.PersistentClient(path="./chroma_data")
    local_collection = local_client.get_collection("documents_ultra_optimized")
    
    # Get just 10 documents
    sample_data = local_collection.get(limit=10, include=['embeddings', 'documents', 'metadatas'])
    
    print(f"📊 Testing with {len(sample_data['ids'])} documents")
    
    # Check sizes
    for i, (doc_id, document, metadata, embedding) in enumerate(zip(
        sample_data['ids'], sample_data['documents'], sample_data['metadatas'], sample_data['embeddings']
    )):
        doc_size = len(document.encode('utf-8')) if document else 0
        meta_size = len(json.dumps(metadata).encode('utf-8')) if metadata else 0
        embedding_size = len(str(embedding).encode('utf-8')) if embedding is not None else 0
        total_size = doc_size + meta_size + embedding_size
        
        print(f"  Doc {i+1}: {total_size} bytes (doc: {doc_size}, meta: {meta_size}, emb: {embedding_size})")
    
    # Create a test collection
    test_collection_name = "test_small_upload"
    
    try:
        local_client.delete_collection(test_collection_name)
    except:
        pass
    
    test_collection = local_client.create_collection(test_collection_name)
    
    # Add the small batch
    test_collection.add(
        ids=sample_data['ids'],
        documents=sample_data['documents'],
        metadatas=sample_data['metadatas'],
        embeddings=sample_data['embeddings']
    )
    
    print(f"✅ Created test collection: {test_collection_name}")
    print(f"🚀 Try uploading this small collection:")
    print(f"chroma copy --collections {test_collection_name} --from-local --to-cloud --db Northeasterndatabase --path ./chroma_data")

if __name__ == "__main__":
    test_small_upload()
