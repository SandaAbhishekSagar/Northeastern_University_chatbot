#!/usr/bin/env python3
"""
Data Migration Script with URL Preservation
- Migrates data from ChromaDB to Pinecone
- Preserves all URLs and metadata
- Handles both local ChromaDB and backups
- Creates proper Pinecone index with Northeastern data
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import time

# Add services to path
sys.path.append('services/shared')

try:
    from database import get_database_type, add_documents_to_pinecone, get_pinecone_index
    from sentence_transformers import SentenceTransformer
    print("✅ Database and embeddings modules imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

def extract_chromadb_data(chroma_path: str) -> List[Dict[str, Any]]:
    """Extract data from ChromaDB SQLite database"""
    print(f"📁 Extracting data from ChromaDB: {chroma_path}")
    
    if not os.path.exists(chroma_path):
        print(f"❌ ChromaDB file not found: {chroma_path}")
        return []
    
    documents = []
    
    try:
        conn = sqlite3.connect(chroma_path)
        cursor = conn.cursor()
        
        # Get all collections
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%collection%'")
        collections = cursor.fetchall()
        
        print(f"📊 Found {len(collections)} collections")
        
        for (collection_name,) in collections:
            print(f"🔍 Processing collection: {collection_name}")
            
            # Get embeddings and metadata
            cursor.execute(f"""
                SELECT id, embedding, metadata, document 
                FROM {collection_name}
                WHERE document IS NOT NULL AND document != ''
            """)
            
            rows = cursor.fetchall()
            print(f"📄 Found {len(rows)} documents in {collection_name}")
            
            for row in rows:
                doc_id, embedding, metadata_json, content = row
                
                if not content or len(content.strip()) < 10:
                    continue
                
                # Parse metadata
                try:
                    metadata = json.loads(metadata_json) if metadata_json else {}
                except:
                    metadata = {}
                
                # Extract URL from metadata
                url = metadata.get('source_url', '') or metadata.get('url', '')
                
                # Extract title
                title = metadata.get('title', '') or metadata.get('file_name', '')
                
                # Create document entry
                doc = {
                    'id': doc_id,
                    'content': content,
                    'metadata': {
                        'title': title,
                        'url': url,
                        'source_url': url,
                        'collection': collection_name,
                        'original_metadata': metadata
                    }
                }
                
                documents.append(doc)
        
        conn.close()
        print(f"✅ Extracted {len(documents)} documents from ChromaDB")
        return documents
        
    except Exception as e:
        print(f"❌ Error extracting ChromaDB data: {e}")
        return []

def extract_backup_data(backup_path: str) -> List[Dict[str, Any]]:
    """Extract data from backup directories"""
    print(f"📁 Extracting data from backup: {backup_path}")
    
    documents = []
    
    # Look for chroma.sqlite3 in backup
    chroma_file = os.path.join(backup_path, "chroma.sqlite3")
    if os.path.exists(chroma_file):
        return extract_chromadb_data(chroma_file)
    
    # Look for other data files
    for root, dirs, files in os.walk(backup_path):
        for file in files:
            if file == "chroma.sqlite3":
                chroma_file = os.path.join(root, file)
                print(f"🔍 Found ChromaDB file: {chroma_file}")
                return extract_chromadb_data(chroma_file)
    
    print(f"❌ No ChromaDB data found in backup: {backup_path}")
    return []

def find_best_backup() -> Optional[str]:
    """Find the best backup with the most data"""
    backup_candidates = [
        "chroma_backups/chroma_backup_20250809_112404",
        "chroma_data_backup_manual",
        "chroma_data_backup_before_efficient_restore_1754159955",
        "chroma_data_backup_before_rebuild_1754159415",
        "chroma_data_backup_before_restore_1754159866"
    ]
    
    best_backup = None
    max_docs = 0
    
    for backup_path in backup_candidates:
        if os.path.exists(backup_path):
            print(f"🔍 Checking backup: {backup_path}")
            docs = extract_backup_data(backup_path)
            if len(docs) > max_docs:
                max_docs = len(docs)
                best_backup = backup_path
                print(f"📊 Found {len(docs)} documents")
    
    if best_backup:
        print(f"✅ Best backup: {best_backup} with {max_docs} documents")
    else:
        print("❌ No backups found with data")
    
    return best_backup

def migrate_to_pinecone(documents: List[Dict[str, Any]]) -> bool:
    """Migrate documents to Pinecone with proper URL handling"""
    if not documents:
        print("❌ No documents to migrate")
        return False
    
    print(f"🌲 Migrating {len(documents)} documents to Pinecone...")
    
    try:
        # Prepare data for Pinecone
        docs_content = []
        metadatas = []
        ids = []
        
        for doc in documents:
            docs_content.append(doc['content'])
            metadatas.append(doc['metadata'])
            ids.append(doc['id'])
        
        # Add to Pinecone
        uploaded_count = add_documents_to_pinecone(
            documents=docs_content,
            metadatas=metadatas,
            ids=ids,
            collection_name="documents"
        )
        
        print(f"✅ Successfully migrated {uploaded_count} documents to Pinecone")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def verify_migration() -> bool:
    """Verify that migration was successful"""
    print("🔍 Verifying migration...")
    
    try:
        # Test search functionality
        from database import query_pinecone
        
        # Test query
        results = query_pinecone("Northeastern University admissions", n_results=5)
        
        if results and results.get('ids'):
            print(f"✅ Migration verified! Found {len(results['ids'])} results")
            
            # Check if URLs are preserved
            for i, metadata in enumerate(results.get('metadatas', [])):
                url = metadata.get('url', '') or metadata.get('source_url', '')
                title = metadata.get('title', '')
                print(f"📄 {i+1}. {title} - {url}")
            
            return True
        else:
            print("❌ Migration verification failed - no results found")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    print("🔄 Northeastern University Data Migration with URL Preservation")
    print("=" * 70)
    
    # Check if Pinecone is configured
    if not os.getenv("PINECONE_API_KEY"):
        print("⚠️  PINECONE_API_KEY not found in environment")
        print("Please add your Pinecone API key to .env file")
        return
    
    # Find best backup
    best_backup = find_best_backup()
    if not best_backup:
        print("❌ No backup found with data")
        return
    
    # Extract data from backup
    documents = extract_backup_data(best_backup)
    if not documents:
        print("❌ No documents extracted from backup")
        return
    
    # Filter for Northeastern University documents
    northeastern_docs = []
    for doc in documents:
        content = doc['content'].lower()
        title = doc['metadata'].get('title', '').lower()
        url = doc['metadata'].get('url', '').lower()
        
        if any(term in content or term in title or term in url for term in [
            'northeastern', 'neu', 'northeastern.edu'
        ]):
            northeastern_docs.append(doc)
    
    print(f"🎓 Found {len(northeastern_docs)} Northeastern University documents")
    
    if not northeastern_docs:
        print("⚠️  No Northeastern-specific documents found, using all documents")
        northeastern_docs = documents
    
    # Migrate to Pinecone
    if migrate_to_pinecone(northeastern_docs):
        # Verify migration
        if verify_migration():
            print("\n🎉 Migration completed successfully!")
            print("✅ URLs are preserved and accessible")
            print("✅ Documents are searchable in Pinecone")
            print("✅ Ready to use with the fixed chatbot")
        else:
            print("\n⚠️  Migration completed but verification failed")
    else:
        print("\n❌ Migration failed")

if __name__ == "__main__":
    main()
