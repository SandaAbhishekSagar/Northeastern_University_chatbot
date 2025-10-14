#!/usr/bin/env python3
"""
Check ChromaDB data and migrate to Pinecone
"""

import os
import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.append('.')

def check_chromadb_data():
    """Check what data is available in ChromaDB"""
    print("🔍 Checking ChromaDB data...")
    
    try:
        from services.shared.database import get_chroma_client, get_collection
        
        # Get ChromaDB client
        client = get_chroma_client()
        print("✅ Connected to ChromaDB")
        
        # List all collections
        collections = client.list_collections()
        print(f"📊 Found {len(collections)} collections:")
        
        for collection in collections:
            print(f"  - {collection.name}")
        
        # Check documents collection specifically
        try:
            documents_collection = client.get_collection("documents")
            count = documents_collection.count()
            print(f"📄 Documents collection has {count} documents")
            
            if count > 0:
                # Get a sample document
                sample = documents_collection.get(limit=1)
                if sample['documents']:
                    print(f"📝 Sample document: {sample['documents'][0][:100]}...")
                    if sample['metadatas']:
                        print(f"🏷️  Sample metadata: {sample['metadatas'][0]}")
            
            return count
            
        except Exception as e:
            print(f"❌ Error checking documents collection: {e}")
            return 0
            
    except Exception as e:
        print(f"❌ Error connecting to ChromaDB: {e}")
        return 0

def check_pinecone_status():
    """Check Pinecone connection and data"""
    print("\n🌲 Checking Pinecone status...")
    
    try:
        from services.shared.database import get_pinecone_index, get_pinecone_count
        
        # Check if we can connect to Pinecone
        index = get_pinecone_index()
        print("✅ Connected to Pinecone")
        
        # Get document count
        count = get_pinecone_count()
        print(f"📊 Pinecone has {count} documents")
        
        return count
        
    except Exception as e:
        print(f"❌ Error connecting to Pinecone: {e}")
        return 0

def migrate_chromadb_to_pinecone():
    """Migrate data from ChromaDB to Pinecone"""
    print("\n🔄 Starting migration from ChromaDB to Pinecone...")
    
    try:
        from services.shared.database import get_chroma_client, add_documents_to_pinecone
        
        # Get ChromaDB client
        client = get_chroma_client()
        documents_collection = client.get_collection("documents")
        
        # Get all documents
        print("📥 Fetching documents from ChromaDB...")
        all_docs = documents_collection.get()
        
        if not all_docs['documents']:
            print("❌ No documents found in ChromaDB")
            return False
        
        print(f"📄 Found {len(all_docs['documents'])} documents to migrate")
        
        # Process in batches
        batch_size = 100
        total_docs = len(all_docs['documents'])
        
        for i in range(0, total_docs, batch_size):
            batch_end = min(i + batch_size, total_docs)
            batch_docs = all_docs['documents'][i:batch_end]
            batch_ids = all_docs['ids'][i:batch_end]
            batch_metadatas = all_docs['metadatas'][i:batch_end] if all_docs['metadatas'] else [{}] * len(batch_docs)
            
            print(f"📤 Migrating batch {i//batch_size + 1}/{(total_docs + batch_size - 1)//batch_size} ({len(batch_docs)} documents)")
            
            # Add to Pinecone
            add_documents_to_pinecone(
                documents=batch_docs,
                metadatas=batch_metadatas,
                ids=batch_ids,
                collection_name="documents"
            )
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def test_pinecone_search():
    """Test Pinecone search functionality"""
    print("\n🔍 Testing Pinecone search...")
    
    try:
        from services.shared.database import query_pinecone
        
        # Test search
        results = query_pinecone("Northeastern University admissions", n_results=3, collection_name="documents")
        
        if results and results.get('documents'):
            print(f"✅ Search successful! Found {len(results['documents'])} results")
            for i, doc in enumerate(results['documents'][:2]):
                print(f"  {i+1}. {doc[:100]}...")
        else:
            print("❌ No search results found")
            
    except Exception as e:
        print(f"❌ Search test failed: {e}")

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 ChromaDB to Pinecone Migration Tool")
    print("=" * 60)
    
    # Check ChromaDB data
    chromadb_count = check_chromadb_data()
    
    # Check Pinecone status
    pinecone_count = check_pinecone_status()
    
    # If ChromaDB has data but Pinecone doesn't, migrate
    if chromadb_count > 0 and pinecone_count == 0:
        print(f"\n🔄 ChromaDB has {chromadb_count} documents, Pinecone has {pinecone_count}")
        print("Starting migration...")
        
        if migrate_chromadb_to_pinecone():
            # Test the migration
            test_pinecone_search()
        else:
            print("❌ Migration failed")
    elif chromadb_count > 0 and pinecone_count > 0:
        print(f"\n✅ Both databases have data: ChromaDB ({chromadb_count}), Pinecone ({pinecone_count})")
        print("Testing Pinecone search...")
        test_pinecone_search()
    elif chromadb_count == 0:
        print("\n❌ No data found in ChromaDB to migrate")
    else:
        print(f"\n✅ Pinecone already has {pinecone_count} documents")

if __name__ == "__main__":
    main()
