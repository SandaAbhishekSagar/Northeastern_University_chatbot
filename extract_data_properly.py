#!/usr/bin/env python3
"""
Extract data properly from the backup database
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any

# Add services to path
sys.path.append('services/shared')

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    print("✅ Required modules imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def extract_documents_from_backup(backup_file: str) -> List[Dict[str, Any]]:
    """Extract documents from backup SQLite file"""
    print(f"📖 Extracting documents from: {backup_file}")
    
    documents = []
    
    try:
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        
        # Get documents from embeddings table
        print("🔍 Extracting from embeddings table...")
        cursor.execute("""
            SELECT id, vector, metadata, document 
            FROM embeddings
            WHERE document IS NOT NULL AND document != ''
        """)
        
        rows = cursor.fetchall()
        print(f"📄 Found {len(rows)} documents in embeddings table")
        
        for i, row in enumerate(rows):
            if i % 1000 == 0:
                print(f"📝 Processing document {i+1}/{len(rows)}")
            
            doc_id, vector, metadata_json, content = row
            
            if not content or len(content.strip()) < 10:
                continue
            
            # Parse metadata
            try:
                metadata = json.loads(metadata_json) if metadata_json else {}
            except:
                metadata = {}
            
            # Extract URL and title
            url = metadata.get('source_url', '') or metadata.get('url', '')
            title = metadata.get('title', '') or metadata.get('file_name', '')
            
            # Filter for Northeastern University content
            content_lower = content.lower()
            title_lower = title.lower()
            url_lower = url.lower()
            
            if any(term in content_lower or term in title_lower or term in url_lower for term in [
                'northeastern', 'neu', 'northeastern.edu'
            ]):
                doc = {
                    'id': doc_id,
                    'content': content,
                    'metadata': {
                        'title': title,
                        'url': url,
                        'source_url': url,
                        'original_metadata': metadata
                    }
                }
                documents.append(doc)
        
        conn.close()
        print(f"✅ Extracted {len(documents)} Northeastern University documents")
        return documents
        
    except Exception as e:
        print(f"❌ Error extracting documents: {e}")
        return []

def load_documents_to_chromadb(documents: List[Dict[str, Any]]):
    """Load documents into ChromaDB"""
    if not documents:
        print("❌ No documents to load")
        return False
    
    print(f"📚 Loading {len(documents)} documents to ChromaDB...")
    
    try:
        # Connect to ChromaDB
        client = chromadb.PersistentClient(
            path="chroma_data",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create documents collection
        try:
            collection = client.get_collection(name="documents")
        except:
            collection = client.create_collection(name="documents")
        
        # Load embedding model
        print("🔄 Loading embedding model...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Process documents in batches
        batch_size = 100
        total_loaded = 0
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            print(f"📝 Processing batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
            
            # Prepare batch data
            ids = []
            documents_text = []
            metadatas = []
            embeddings = []
            
            for doc in batch:
                ids.append(doc['id'])
                documents_text.append(doc['content'])
                metadatas.append(doc['metadata'])
                
                # Generate embedding
                embedding = embedding_model.encode([doc['content']])[0].tolist()
                embeddings.append(embedding)
            
            # Add batch to ChromaDB
            collection.add(
                ids=ids,
                documents=documents_text,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            total_loaded += len(batch)
            print(f"✅ Loaded {total_loaded}/{len(documents)} documents")
        
        print(f"🎉 Successfully loaded {len(documents)} documents to ChromaDB")
        return True
        
    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        return False

def test_loaded_data():
    """Test that the data was loaded correctly"""
    print("🧪 Testing loaded data...")
    
    try:
        client = chromadb.PersistentClient(
            path="chroma_data",
            settings=Settings(anonymized_telemetry=False)
        )
        
        collection = client.get_collection(name="documents")
        
        # Test query
        results = collection.query(
            query_texts=["Northeastern University admissions"],
            n_results=5
        )
        
        if results['ids'] and results['ids'][0]:
            print(f"✅ Found {len(results['ids'][0])} results for test query")
            
            # Show first few results
            for i, (doc_id, metadata) in enumerate(zip(results['ids'][0][:3], results['metadatas'][0][:3])):
                print(f"📄 {i+1}. {metadata.get('title', 'No title')}")
                print(f"   URL: {metadata.get('url', 'No URL')}")
                print(f"   ID: {doc_id}")
            
            return True
        else:
            print("❌ No results found for test query")
            return False
            
    except Exception as e:
        print(f"❌ Error testing data: {e}")
        return False

def main():
    print("🔄 Loading Data from Backups to Fresh ChromaDB (Proper Method)")
    print("=" * 70)
    
    # Find backup
    backup_file = "chroma_backups/chroma_backup_20250809_112404/chroma.sqlite3"
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return
    
    # Extract documents
    documents = extract_documents_from_backup(backup_file)
    if not documents:
        print("❌ No documents extracted from backup")
        return
    
    # Load to ChromaDB
    if load_documents_to_chromadb(documents):
        # Test the loaded data
        if test_loaded_data():
            print("\n🎉 Data loading completed successfully!")
            print("✅ ChromaDB now contains Northeastern University documents")
            print("✅ URLs are preserved and accessible")
            print("✅ Ready to use with the fixed chatbot")
        else:
            print("\n⚠️  Data loaded but test failed")
    else:
        print("\n❌ Data loading failed")

if __name__ == "__main__":
    main()
