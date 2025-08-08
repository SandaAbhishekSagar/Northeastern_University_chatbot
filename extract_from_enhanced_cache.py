#!/usr/bin/env python3
"""
Extract documents from enhanced_embeddings_cache.pkl
"""

import pickle
import os
import json
from pathlib import Path
import chromadb
from chromadb.config import Settings
import time

def extract_from_enhanced_cache():
    """Extract documents from the enhanced embeddings cache"""
    print("🔍 Extracting Documents from Enhanced Embeddings Cache")
    print("=" * 60)
    
    cache_file = "enhanced_embeddings_cache.pkl"
    
    if not os.path.exists(cache_file):
        print(f"❌ {cache_file} not found!")
        return None
    
    try:
        print(f"📊 Loading {cache_file}...")
        with open(cache_file, 'rb') as f:
            cache_data = pickle.load(f)
        
        print(f"📋 Cache keys: {list(cache_data.keys())}")
        
        if 'document_embeddings' in cache_data:
            doc_embeddings = cache_data['document_embeddings']
            print(f"📊 Document embeddings type: {type(doc_embeddings)}")
            
            if isinstance(doc_embeddings, dict):
                print(f"📊 Number of document embeddings: {len(doc_embeddings)}")
                
                # Look for document content
                doc_data = []
                
                for key, value in doc_embeddings.items():
                    if isinstance(value, dict):
                        # Check if this contains document content
                        if 'content' in value or 'text' in value or 'document' in value:
                            content = value.get('content') or value.get('text') or value.get('document')
                            if content and len(str(content)) > 50:
                                doc_data.append({
                                    'id': key,
                                    'content': content,
                                    'metadata': {k: v for k, v in value.items() if k not in ['content', 'text', 'document']}
                                })
                    elif isinstance(value, str) and len(value) > 50:
                        # Direct string content
                        doc_data.append({
                            'id': key,
                            'content': value,
                            'metadata': {'source': 'enhanced_cache'}
                        })
                
                print(f"📊 Found {len(doc_data)} documents with content")
                
                if doc_data:
                    # Show sample documents
                    print(f"\n📋 Sample documents:")
                    for i, doc in enumerate(doc_data[:3]):
                        print(f"  {i+1}. ID: {doc['id'][:20]}...")
                        print(f"     Content: {doc['content'][:100]}...")
                        print(f"     Metadata: {doc['metadata']}")
                        print()
                
                return doc_data
            else:
                print(f"📊 Document embeddings is not a dict: {type(doc_embeddings)}")
                return None
        else:
            print("❌ No 'document_embeddings' found in cache")
            return None
            
    except Exception as e:
        print(f"❌ Error loading cache: {e}")
        return None

def rebuild_chromadb_with_extracted_docs(doc_data):
    """Rebuild ChromaDB with extracted documents"""
    if not doc_data:
        print("❌ No document data to rebuild with")
        return False
    
    print(f"\n🔧 Rebuilding ChromaDB with {len(doc_data)} Documents")
    print("=" * 60)
    
    try:
        # Create new ChromaDB client
        client = chromadb.PersistentClient(
            path="chroma_data_restored_from_cache",
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
        total_docs = len(doc_data)
        
        print(f"📋 Adding {total_docs:,} documents in batches of {batch_size}...")
        
        for i in range(0, total_docs, batch_size):
            batch = doc_data[i:i + batch_size]
            
            # Prepare batch data
            ids = [doc['id'] for doc in batch]
            documents = [doc['content'] for doc in batch]
            metadatas = [doc['metadata'] for doc in batch]
            
            # Add to collection
            collection.add(
                ids=ids,
                documents=documents,
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
        backup_path = Path(f"chroma_data_backup_before_cache_restore_{int(time.time())}")
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
        if Path("chroma_data_restored_from_cache").exists():
            Path("chroma_data_restored_from_cache").rename("chroma_data")
            print("✅ Replaced with restored ChromaDB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error replacing ChromaDB: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Document Recovery from Enhanced Cache")
    print("=" * 60)
    
    # Extract documents from enhanced cache
    doc_data = extract_from_enhanced_cache()
    
    if not doc_data:
        print("❌ No document data found in enhanced cache!")
        return
    
    print(f"\n📊 Summary:")
    print(f"   Total documents found: {len(doc_data):,}")
    
    # Rebuild ChromaDB with extracted documents
    if rebuild_chromadb_with_extracted_docs(doc_data):
        # Replace old ChromaDB
        if replace_chromadb():
            print("\n🎉 Document recovery successful!")
            print(f"\n📊 Final Results:")
            print(f"   ✅ Restored {len(doc_data):,} documents")
            print(f"   ✅ ChromaDB rebuilt successfully")
            print(f"   ✅ All documents available for search")
        else:
            print("\n❌ ChromaDB replacement failed!")
    else:
        print("\n❌ ChromaDB rebuild failed!")

if __name__ == "__main__":
    main() 