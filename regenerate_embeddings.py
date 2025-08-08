#!/usr/bin/env python3
"""
Script to regenerate embeddings for all documents in embedded ChromaDB
This will significantly improve search quality and confidence scores
"""

import sys
import os
from pathlib import Path
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from services.shared.database import get_chroma_client, get_collection
from services.shared.chroma_service import ChromaService
from langchain.embeddings import HuggingFaceEmbeddings

def regenerate_embeddings():
    """Regenerate embeddings for all documents in ChromaDB"""
    print("🔄 Regenerating Embeddings for ChromaDB")
    print("=" * 50)
    
    try:
        # Initialize ChromaDB client
        print("Connecting to ChromaDB...")
        client = get_chroma_client()
        print("✅ ChromaDB connected")
        
        # Get documents collection
        documents_collection = get_collection('documents')
        
        # Get all documents
        print("Retrieving all documents...")
        result = documents_collection.get()
        
        if not result or not result.get('ids'):
            print("❌ No documents found in ChromaDB!")
            return False
        
        total_documents = len(result['ids'])
        print(f"📊 Found {total_documents} documents to process")
        
        # Initialize embedding model
        print("Loading embedding model...")
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("✅ Embedding model loaded")
        
        # Process documents in batches
        batch_size = 10
        processed = 0
        failed = 0
        
        print(f"\n🔄 Processing documents in batches of {batch_size}...")
        
        for i in range(0, total_documents, batch_size):
            batch_end = min(i + batch_size, total_documents)
            batch_ids = result['ids'][i:batch_end]
            batch_documents = result['documents'][i:batch_end]
            batch_metadatas = result['metadatas'][i:batch_end]
            
            print(f"\nProcessing batch {i//batch_size + 1}/{(total_documents + batch_size - 1)//batch_size}")
            print(f"Documents {i+1}-{batch_end} of {total_documents}")
            
            # Generate embeddings for this batch
            try:
                batch_embeddings = embeddings.embed_documents(batch_documents)
                
                # Update documents with new embeddings
                for j, doc_id in enumerate(batch_ids):
                    try:
                        # Update the document with new embedding
                        documents_collection.update(
                            ids=[doc_id],
                            embeddings=[batch_embeddings[j]]
                        )
                        processed += 1
                        print(f"  ✅ Updated document {i+j+1}: {batch_metadatas[j].get('title', 'No title')[:50]}...")
                    except Exception as e:
                        print(f"  ❌ Failed to update document {i+j+1}: {e}")
                        failed += 1
                
            except Exception as e:
                print(f"  ❌ Failed to generate embeddings for batch: {e}")
                failed += batch_size
                continue
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.1)
        
        print(f"\n" + "=" * 50)
        print("📊 Embedding Regeneration Complete!")
        print(f"✅ Successfully processed: {processed} documents")
        print(f"❌ Failed: {failed} documents")
        print(f"📈 Success rate: {processed/(processed+failed)*100:.1f}%")
        
        # Verify embeddings were created
        print(f"\n🔍 Verifying embeddings...")
        verification_result = documents_collection.get()
        if verification_result.get('embeddings'):
            embedding_count = len([e for e in verification_result['embeddings'] if e])
            print(f"✅ {embedding_count} documents now have embeddings")
            print(f"📊 Embedding dimension: {len(verification_result['embeddings'][0]) if verification_result['embeddings'] else 'N/A'}")
        else:
            print("❌ No embeddings found after regeneration")
            return False
        
        print(f"\n🎉 Embedding regeneration successful!")
        print(f"Your chatbot should now have much better search quality and confidence scores.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during embedding regeneration: {e}")
        return False

def clean_duplicate_documents():
    """Remove duplicate documents from ChromaDB"""
    print(f"\n🧹 Cleaning Duplicate Documents")
    print("=" * 50)
    
    try:
        # Get documents collection
        documents_collection = get_collection('documents')
        result = documents_collection.get()
        
        if not result or not result.get('ids'):
            print("❌ No documents found!")
            return False
        
        documents = result.get('documents', [])
        ids = result.get('ids', [])
        metadatas = result.get('metadatas', [])
        
        # Find duplicates
        seen_contents = {}
        duplicates_to_remove = []
        
        for i, content in enumerate(documents):
            content_hash = hash(content.strip())
            if content_hash in seen_contents:
                duplicates_to_remove.append(ids[i])
                print(f"  🗑️  Duplicate found: {metadatas[i].get('title', 'No title')[:50]}...")
            else:
                seen_contents[content_hash] = ids[i]
        
        if duplicates_to_remove:
            print(f"\n🗑️  Removing {len(duplicates_to_remove)} duplicate documents...")
            documents_collection.delete(ids=duplicates_to_remove)
            print(f"✅ Removed {len(duplicates_to_remove)} duplicates")
        else:
            print("✅ No duplicates found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning duplicates: {e}")
        return False

def main():
    """Main function to regenerate embeddings and clean duplicates"""
    print("🚀 ChromaDB Optimization Script")
    print("=" * 50)
    
    # Step 1: Clean duplicates
    if not clean_duplicate_documents():
        print("❌ Failed to clean duplicates")
        return
    
    # Step 2: Regenerate embeddings
    if not regenerate_embeddings():
        print("❌ Failed to regenerate embeddings")
        return
    
    print(f"\n🎉 All optimizations complete!")
    print(f"Your chatbot should now have:")
    print(f"  ✅ Better search quality")
    print(f"  ✅ Higher confidence scores")
    print(f"  ✅ Faster response times")
    print(f"  ✅ More accurate answers")
    
    print(f"\n📝 Next steps:")
    print(f"1. Test the chatbot: python test_confidence_fix.py")
    print(f"2. Start the API: python run.py api")
    print(f"3. Test with real questions")

if __name__ == "__main__":
    main() 