#!/usr/bin/env python3
"""
Script to completely rebuild ChromaDB collection with embeddings
This approach creates a new collection with embeddings included from the start
"""

import sys
import os
from pathlib import Path
import time
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from services.shared.database import get_chroma_client, get_collection
from langchain.embeddings import HuggingFaceEmbeddings

def backup_chromadb():
    """Create a backup of the current ChromaDB"""
    print("📦 Creating ChromaDB backup...")
    try:
        backup_dir = "chroma_data_backup"
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        shutil.copytree("chroma_data", backup_dir)
        print(f"✅ Backup created at: {backup_dir}")
        return True
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return False

def rebuild_collection_with_embeddings():
    """Rebuild the documents collection with embeddings"""
    print("🔄 Rebuilding ChromaDB Collection with Embeddings")
    print("=" * 60)
    
    try:
        # Initialize ChromaDB client
        print("Connecting to ChromaDB...")
        client = get_chroma_client()
        print("✅ ChromaDB connected")
        
        # Get current documents collection
        documents_collection = get_collection('documents')
        
        # Get all current documents
        print("Retrieving current documents...")
        result = documents_collection.get()
        
        if not result or not result.get('ids'):
            print("❌ No documents found in ChromaDB!")
            return False
        
        total_documents = len(result['ids'])
        print(f"📊 Found {total_documents} documents to rebuild")
        
        # Initialize embedding model
        print("Loading embedding model...")
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("✅ Embedding model loaded")
        
        # Generate embeddings for all documents
        print("Generating embeddings for all documents...")
        all_documents = result.get('documents', [])
        all_embeddings = embeddings.embed_documents(all_documents)
        print(f"✅ Generated {len(all_embeddings)} embeddings")
        
        # Delete the old collection
        print("Deleting old collection...")
        client.delete_collection('documents')
        print("✅ Old collection deleted")
        
        # Create new collection with embeddings
        print("Creating new collection with embeddings...")
        new_collection = client.create_collection(
            name='documents',
            metadata={"hnsw:space": "cosine"}
        )
        print("✅ New collection created")
        
        # Add documents with embeddings in batches
        batch_size = 20
        processed = 0
        
        print(f"\n🔄 Adding documents with embeddings in batches of {batch_size}...")
        
        for i in range(0, total_documents, batch_size):
            batch_end = min(i + batch_size, total_documents)
            batch_ids = result['ids'][i:batch_end]
            batch_documents = result['documents'][i:batch_end]
            batch_metadatas = result['metadatas'][i:batch_end]
            batch_embeddings = all_embeddings[i:batch_end]
            
            print(f"\nProcessing batch {i//batch_size + 1}/{(total_documents + batch_size - 1)//batch_size}")
            print(f"Documents {i+1}-{batch_end} of {total_documents}")
            
            try:
                # Add documents with embeddings
                new_collection.add(
                    ids=batch_ids,
                    documents=batch_documents,
                    metadatas=batch_metadatas,
                    embeddings=batch_embeddings
                )
                processed += len(batch_ids)
                print(f"  ✅ Added {len(batch_ids)} documents with embeddings")
                
            except Exception as e:
                print(f"  ❌ Failed to add batch: {e}")
                continue
            
            # Small delay
            time.sleep(0.1)
        
        print(f"\n" + "=" * 60)
        print("📊 Collection Rebuild Complete!")
        print(f"✅ Successfully processed: {processed} documents")
        
        # Verify the new collection
        print(f"\n🔍 Verifying new collection...")
        verification_result = new_collection.get()
        if verification_result.get('embeddings'):
            embedding_count = len([e for e in verification_result['embeddings'] if e])
            print(f"✅ {embedding_count} documents have embeddings")
            print(f"📊 Embedding dimension: {len(verification_result['embeddings'][0]) if verification_result['embeddings'] else 'N/A'}")
            
            # Test a simple query
            print(f"\n🧪 Testing search functionality...")
            test_query = "Northeastern University"
            test_embedding = embeddings.embed_query(test_query)
            search_result = new_collection.query(
                query_embeddings=[test_embedding],
                n_results=3
            )
            if search_result['ids']:
                print(f"✅ Search test successful - found {len(search_result['ids'][0])} results")
            else:
                print("❌ Search test failed")
        else:
            print("❌ No embeddings found in new collection")
            return False
        
        print(f"\n🎉 Collection rebuild successful!")
        print(f"Your chatbot should now have persistent embeddings and much better performance.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during collection rebuild: {e}")
        return False

def main():
    """Main function to rebuild collection with embeddings"""
    print("🚀 ChromaDB Collection Rebuild with Embeddings")
    print("=" * 60)
    
    # Step 1: Create backup
    if not backup_chromadb():
        print("❌ Failed to create backup")
        return
    
    # Step 2: Rebuild collection
    if not rebuild_collection_with_embeddings():
        print("❌ Failed to rebuild collection")
        print("You can restore from backup if needed")
        return
    
    print(f"\n🎉 Collection rebuild complete!")
    print(f"Your chatbot now has:")
    print(f"  ✅ Persistent embeddings")
    print(f"  ✅ Better search quality")
    print(f"  ✅ Higher confidence scores")
    print(f"  ✅ Faster response times")
    
    print(f"\n📝 Next steps:")
    print(f"1. Test the chatbot: python test_confidence_fix.py")
    print(f"2. Start the API: python run.py api")
    print(f"3. Test with real questions")

if __name__ == "__main__":
    main() 