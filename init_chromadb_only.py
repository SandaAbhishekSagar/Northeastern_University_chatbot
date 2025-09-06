#!/usr/bin/env python3
"""
Initialize ChromaDB only (without Pinecone)
"""

import os
import sys
from pathlib import Path

# Remove Pinecone environment variables
os.environ.pop('PINECONE_API_KEY', None)
os.environ.pop('PINECONE_ENVIRONMENT', None)
os.environ.pop('PINECONE_INDEX_NAME', None)

# Add services to path
sys.path.append('services/shared')

try:
    import chromadb
    from chromadb.config import Settings
    print("✅ ChromaDB imported successfully")
except ImportError as e:
    print(f"❌ ChromaDB import error: {e}")
    sys.exit(1)

def init_chromadb():
    """Initialize ChromaDB with fresh collections"""
    print("🔄 Initializing ChromaDB...")
    
    # Create chroma_data directory
    chroma_data_path = Path("chroma_data")
    chroma_data_path.mkdir(exist_ok=True)
    
    try:
        # Create ChromaDB client
        client = chromadb.PersistentClient(
            path=str(chroma_data_path),
            settings=Settings(anonymized_telemetry=False)
        )
        print("✅ Connected to ChromaDB")
        
        # Create collections
        collections = ["universities", "documents", "scrape_logs", "chat_sessions", "chat_messages", "feedback"]
        
        for collection_name in collections:
            try:
                client.get_collection(name=collection_name)
                print(f"✅ Collection {collection_name} already exists")
            except:
                client.create_collection(name=collection_name)
                print(f"✅ Created collection: {collection_name}")
        
        print("🎉 ChromaDB initialization completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("🎓 Northeastern University Chatbot - ChromaDB Initialization")
    print("=" * 60)
    
    if init_chromadb():
        print("\n✅ ChromaDB is ready!")
        print("📁 Database location: chroma_data/")
        print("📊 Collections created: universities, documents, scrape_logs, chat_sessions, chat_messages, feedback")
        print("\n💡 You can now run the chatbot with ChromaDB backend")
    else:
        print("\n❌ ChromaDB initialization failed")
        sys.exit(1)
