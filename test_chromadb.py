#!/usr/bin/env python3
"""
Simple test script to verify ChromaDB status after restore
"""

import os
import sys

def test_chromadb():
    try:
        print("🔍 Testing ChromaDB Status...")
        print("=" * 50)
        
        # Check if chroma_data directory exists
        if os.path.exists('chroma_data'):
            print("✅ chroma_data directory exists")
            
            # List contents
            contents = os.listdir('chroma_data')
            print(f"📁 Contents: {contents}")
            
            # Check for key files
            if 'chroma.sqlite3' in contents:
                print("✅ chroma.sqlite3 found")
            else:
                print("❌ chroma.sqlite3 not found")
                
            if 'embeddings' in contents:
                print("✅ embeddings directory found")
                embeddings_dir = os.path.join('chroma_data', 'embeddings')
                if os.path.isdir(embeddings_dir):
                    embedding_collections = os.listdir(embeddings_dir)
                    print(f"📊 Embedding collections: {len(embedding_collections)}")
                    for collection in embedding_collections:
                        print(f"   - {collection}")
            else:
                print("❌ embeddings directory not found")
                
        else:
            print("❌ chroma_data directory does not exist")
            
        # Try to import and test ChromaDB
        try:
            import chromadb
            print("✅ ChromaDB imported successfully")
            
            client = chromadb.PersistentClient(path='chroma_data')
            collections = client.list_collections()
            print(f"📚 Collections found: {len(collections)}")
            
            for collection in collections:
                try:
                    count = collection.count()
                    print(f"   - {collection.name}: {count} documents")
                except Exception as e:
                    print(f"   - {collection.name}: Error getting count - {e}")
                    
        except ImportError as e:
            print(f"❌ Failed to import ChromaDB: {e}")
        except Exception as e:
            print(f"❌ ChromaDB error: {e}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chromadb()
