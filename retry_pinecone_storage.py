#!/usr/bin/env python3
"""
Retry storing the scraped documents in Pinecone with proper batch processing
"""

import os
import sys
import time
import json
from pathlib import Path

# Add current directory to path
sys.path.append('.')

def setup_pinecone():
    """Set up Pinecone connection"""
    print("🌲 Setting up Pinecone...")
    
    try:
        from pinecone import Pinecone
        
        # Get API key from environment
        api_key = os.environ.get('PINECONE_API_KEY')
        if not api_key:
            print("⚠️  PINECONE_API_KEY not found in environment variables")
            return None
        
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        
        # Get index
        index_name = "northeastern-university"
        if index_name not in pc.list_indexes().names():
            print(f"❌ Index {index_name} not found")
            return None
        
        print(f"✅ Using existing Pinecone index: {index_name}")
        return pc.Index(index_name)
        
    except Exception as e:
        print(f"❌ Failed to setup Pinecone: {e}")
        return None

def get_embedding(text):
    """Get embedding for text"""
    try:
        from sentence_transformers import SentenceTransformer
        
        # Load model (cache it globally to avoid reloading)
        if not hasattr(get_embedding, 'model'):
            print("🔄 Loading embedding model...")
            get_embedding.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Embedding model loaded")
        
        # Generate embedding
        embedding = get_embedding.model.encode([text])[0].tolist()
        return embedding
        
    except Exception as e:
        print(f"❌ Failed to generate embedding: {e}")
        return None

def store_in_pinecone_batches(docs, index, batch_size=50):
    """Store documents in Pinecone in small batches"""
    print(f"📤 Storing {len(docs)} documents in Pinecone (batch size: {batch_size})...")
    
    try:
        total_stored = 0
        total_batches = (len(docs) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(docs))
            batch_docs = docs[start_idx:end_idx]
            
            print(f"📦 Processing batch {batch_num + 1}/{total_batches} ({len(batch_docs)} documents)...")
            
            # Prepare vectors for this batch
            vectors = []
            
            for i, doc in enumerate(batch_docs):
                print(f"  🔄 Generating embedding {i+1}/{len(batch_docs)}...")
                
                # Generate embedding
                embedding = get_embedding(doc['content'])
                if not embedding:
                    print(f"  ⚠️  Skipping document {i+1} - embedding failed")
                    continue
                
                # Create vector
                vector = {
                    'id': doc['id'],
                    'values': embedding,
                    'metadata': doc['metadata']
                }
                vectors.append(vector)
            
            # Upsert this batch to Pinecone
            if vectors:
                print(f"  📤 Uploading {len(vectors)} vectors to Pinecone...")
                index.upsert(vectors=vectors)
                total_stored += len(vectors)
                print(f"  ✅ Stored batch {batch_num + 1}/{total_batches} ({len(vectors)} documents)")
            else:
                print(f"  ⚠️  No valid embeddings in batch {batch_num + 1}")
            
            # Small delay between batches
            if batch_num < total_batches - 1:
                time.sleep(1)
        
        print(f"🎉 Successfully stored {total_stored} documents in Pinecone")
        return True
            
    except Exception as e:
        print(f"❌ Failed to store in Pinecone: {e}")
        return False

def create_sample_documents():
    """Create sample documents for testing"""
    print("📝 Creating sample documents for testing...")
    
    sample_docs = []
    for i in range(10):
        doc = {
            'id': f"test_doc_{i}",
            'content': f"This is a test document {i} about Northeastern University. It contains information about admissions, programs, and student life. This content is designed to test the Pinecone storage functionality.",
            'metadata': {
                'url': f'https://www.northeastern.edu/test-{i}',
                'title': f'Test Document {i}',
                'scraped_at': time.time()
            }
        }
        sample_docs.append(doc)
    
    return sample_docs

def main():
    """Main function to retry Pinecone storage"""
    print("=" * 60)
    print("🔄 Retry Pinecone Storage with Batch Processing")
    print("=" * 60)
    
    # Setup Pinecone
    index = setup_pinecone()
    if not index:
        print("❌ Failed to setup Pinecone")
        return
    
    # Create sample documents for testing
    docs = create_sample_documents()
    
    print(f"🧪 Testing with {len(docs)} sample documents...")
    
    # Store in Pinecone with batch processing
    success = store_in_pinecone_batches(docs, index, batch_size=5)
    
    if success:
        print("🎉 Test storage successful!")
        print("✅ The batch processing fix works correctly")
        print("🚀 You can now run the full scraper again")
    else:
        print("❌ Test storage failed")
        print("🔍 Please check your Pinecone API key and connection")

if __name__ == "__main__":
    main()

