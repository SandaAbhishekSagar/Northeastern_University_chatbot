#!/usr/bin/env python3
"""
Extract all documents from embedding_fulltext_search_content table
"""

import sqlite3
import os
import json
from pathlib import Path
import chromadb
from chromadb.config import Settings
import time

def extract_all_documents_from_content_table():
    """Extract all documents from the largest backup database"""
    print("🔍 Extracting All Documents from Content Table")
    print("=" * 60)
    
    # Use the largest backup database
    db_path = "chroma_data_backup_before_efficient_restore_1754159955/chroma.sqlite3"
    
    if not os.path.exists(db_path):
        print(f"❌ {db_path} not found!")
        return None
    
    try:
        print(f"📊 Connecting to: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM embedding_fulltext_search_content")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total documents in table: {total_count:,}")
        
        # Extract all documents
        print("📋 Extracting all documents...")
        cursor.execute("SELECT id, c0 FROM embedding_fulltext_search_content ORDER BY id")
        
        documents = []
        batch_size = 1000
        processed = 0
        
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            
            for row in rows:
                doc_id, content = row
                if content and len(str(content)) > 10:  # Filter out empty or very short content
                    documents.append({
                        'id': f"doc_{doc_id}",
                        'content': content,
                        'source': 'embedding_fulltext_search_content',
                        'original_id': doc_id
                    })
            
            processed += len(rows)
            progress = (processed / total_count) * 100
            print(f"📋 Progress: {progress:.1f}% ({processed:,}/{total_count:,} documents)")
        
        conn.close()
        
        print(f"📊 Successfully extracted {len(documents):,} documents")
        
        # Show sample documents
        print(f"\n📋 Sample documents:")
        for i, doc in enumerate(documents[:3]):
            print(f"  {i+1}. ID: {doc['id']}")
            print(f"     Content: {doc['content'][:200]}...")
            print(f"     Length: {len(doc['content'])} characters")
            print()
        
        return documents
        
    except Exception as e:
        print(f"❌ Error extracting documents: {e}")
        return None

def rebuild_chromadb_with_documents(documents):
    """Rebuild ChromaDB with extracted documents"""
    if not documents:
        print("❌ No documents to rebuild with")
        return False
    
    print(f"\n🔧 Rebuilding ChromaDB with {len(documents):,} Documents")
    print("=" * 60)
    
    try:
        # Create new ChromaDB client
        client = chromadb.PersistentClient(
            path="chroma_data_restored_from_content",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Delete existing collection if it exists
        try:
            client.delete_collection("documents")
            print("🗑️  Deleted existing documents collection")
        except:
            pass
        
        # Create new collection
        collection = client.create_collection("documents")
        print("✅ Created new documents collection")
        
        # Add documents in batches
        batch_size = 100
        total_docs = len(documents)
        
        print(f"📋 Adding {total_docs:,} documents in batches of {batch_size}...")
        
        for i in range(0, total_docs, batch_size):
            batch = documents[i:i + batch_size]
            
            # Prepare batch data
            ids = [doc['id'] for doc in batch]
            docs = [doc['content'] for doc in batch]
            metadatas = [{
                'source': doc['source'],
                'original_id': doc['original_id']
            } for doc in batch]
            
            # Add to collection
            collection.add(
                ids=ids,
                documents=docs,
                metadatas=metadatas
            )
            
            progress = (i + len(batch)) / total_docs * 100
            print(f"📋 Progress: {progress:.1f}% ({i + len(batch):,}/{total_docs:,} documents)")
        
        # Verify the collection
        count = collection.count()
        print(f"📊 Final collection count: {count:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error rebuilding ChromaDB: {e}")
        return False

def replace_chromadb():
    """Replace the old ChromaDB with the restored version"""
    print(f"\n🔄 Replacing ChromaDB")
    print("=" * 60)
    
    try:
        # Create backup of current ChromaDB
        backup_path = Path(f"chroma_data_backup_before_content_restore_{int(time.time())}")
        if Path("chroma_data").exists():
            import shutil
            shutil.copytree("chroma_data", backup_path)
            print(f"💾 Created backup: {backup_path}")
        
        # Remove old ChromaDB
        if Path("chroma_data").exists():
            import shutil
            shutil.rmtree("chroma_data")
            print("🗑️  Removed old ChromaDB")
        
        # Rename new ChromaDB
        if Path("chroma_data_restored_from_content").exists():
            Path("chroma_data_restored_from_content").rename("chroma_data")
            print("✅ Replaced with restored ChromaDB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error replacing ChromaDB: {e}")
        return False

def verify_restoration():
    """Verify that the restoration was successful"""
    print(f"\n🔍 Verifying Restoration")
    print("=" * 60)
    
    try:
        client = chromadb.PersistentClient(
            path="chroma_data",
            settings=Settings(anonymized_telemetry=False)
        )
        
        collection = client.get_collection("documents")
        count = collection.count()
        
        print(f"📊 Documents in restored ChromaDB: {count:,}")
        
        if count > 0:
            # Test a query
            results = collection.query(
                query_texts=["Northeastern University admission requirements"],
                n_results=3
            )
            
            print(f"📋 Test query results:")
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                print(f"  {i+1}. {doc[:100]}...")
                print(f"     Metadata: {metadata}")
                print()
        
        return count > 0
        
    except Exception as e:
        print(f"❌ Error verifying restoration: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Complete Document Recovery from Content Table")
    print("=" * 60)
    
    # Extract all documents from content table
    documents = extract_all_documents_from_content_table()
    
    if not documents:
        print("❌ No documents found in content table!")
        return
    
    print(f"\n📊 Summary:")
    print(f"   Total documents found: {len(documents):,}")
    
    # Rebuild ChromaDB with extracted documents
    if rebuild_chromadb_with_documents(documents):
        # Replace old ChromaDB
        if replace_chromadb():
            # Verify restoration
            if verify_restoration():
                print("\n🎉 Document recovery successful!")
                print(f"\n📊 Final Results:")
                print(f"   ✅ Restored {len(documents):,} documents")
                print(f"   ✅ ChromaDB rebuilt successfully")
                print(f"   ✅ All documents available for search")
                print(f"   ✅ Test query working")
            else:
                print("\n❌ Restoration verification failed!")
        else:
            print("\n❌ ChromaDB replacement failed!")
    else:
        print("\n❌ ChromaDB rebuild failed!")

if __name__ == "__main__":
    main() 