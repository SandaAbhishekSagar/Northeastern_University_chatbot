import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime

# Add the project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")

try:
    import chromadb
    from chromadb.config import Settings
    print("[OK] ChromaDB imported successfully")
except ImportError as e:
    print(f"[ERROR] ChromaDB import error: {e}")
    print("Run: pip install chromadb")
    exit(1)

# Import config
try:
    from services.shared.config import config
    print("[OK] Config imported successfully")
except ImportError as e:
    print(f"[ERROR] Config import error: {e}")
    print("Creating default config...")
    
    # Create a basic config if import fails
    class DefaultConfig:
        CHROMADB_HOST = "localhost"
        CHROMADB_PORT = 8000
        CHROMADB_HTTP_PORT = 8000
    config = DefaultConfig()

# ChromaDB configuration
chroma_data_path = Path(__file__).parent.parent.parent / "chroma_data"

# Check if using ChromaDB Cloud
CHROMA_CLOUD_TOKEN = os.environ.get("CHROMA_CLOUD_TOKEN")
CHROMA_CLOUD_HOST = os.environ.get("CHROMA_CLOUD_HOST", "https://api.chromadb.com")

# Global client instance
chroma_client = None

def get_chroma_client():
    """Get ChromaDB client - supports both local and cloud"""
    global chroma_client
    
    if chroma_client is not None:
        return chroma_client
    
    try:
        if CHROMA_CLOUD_TOKEN:
            # Use ChromaDB Cloud
            print(f"☁️  Connecting to ChromaDB Cloud at {CHROMA_CLOUD_HOST}")
            chroma_client = chromadb.HttpClient(
                host=CHROMA_CLOUD_HOST,
                port=443,
                ssl=True,
                headers={"Authorization": f"Bearer {CHROMA_CLOUD_TOKEN}"}
            )
            print("✅ Connected to ChromaDB Cloud")
        else:
            # Use local ChromaDB
            print(f"📁 Using local ChromaDB at {chroma_data_path}")
            chroma_client = chromadb.PersistentClient(
                path=str(chroma_data_path),
                settings=Settings(anonymized_telemetry=False)
            )
            print("✅ Connected to local ChromaDB")
        
        return chroma_client
        
    except Exception as e:
        print(f"❌ Failed to connect to ChromaDB: {e}")
        raise

def get_collection(collection_name: str):
    """Get a ChromaDB collection"""
    client = get_chroma_client()
    
    try:
        collection = client.get_collection(name=collection_name)
        print(f"[OK] Retrieved collection: {collection_name}")
        return collection
    except Exception as e:
        print(f"[INFO] Collection {collection_name} not found, creating...")
        collection = client.create_collection(name=collection_name)
        print(f"[OK] Created collection: {collection_name}")
        return collection

def init_db():
    """Initialize database with required collections"""
    collections = [
        "universities",
        "documents", 
        "scrape_logs",
        "chat_sessions",
        "chat_messages",
        "feedback"
    ]
    
    for collection_name in collections:
        get_collection(collection_name)
    
    print("✅ Database initialized with all collections")

def test_connection():
    """Test ChromaDB connection"""
    try:
        client = get_chroma_client()
        # Try to list collections to test connection
        collections = client.list_collections()
        print("[OK] ChromaDB connection successful")
        print(f"   Available collections: {[col.name for col in collections]}")
        return True
    except Exception as e:
        print(f"[ERROR] ChromaDB connection failed: {e}")
        return False

def check_collections():
    """Check what collections exist"""
    try:
        client = get_chroma_client()
        collections = client.list_collections()
        collection_names = [col.name for col in collections]
        
        if collection_names:
            print(f"[OK] Existing collections: {', '.join(collection_names)}")
        else:
            print("[INFO] No collections found - this is normal for first run")
        return collection_names
    except Exception as e:
        print(f"[ERROR] Error checking collections: {e}")
        return []

def reset_db():
    """Reset all ChromaDB collections (WARNING: This deletes all data)"""
    print("WARNING: This will delete all data in ChromaDB!")
    response = input("Are you sure? Type 'yes' to continue: ")
    
    if response.lower() == 'yes':
        try:
            client = get_chroma_client()
            collections = client.list_collections()
            
            for collection in collections:
                client.delete_collection(name=collection.name)
                print(f"[OK] Deleted collection: {collection.name}")
            
            print("All collections deleted successfully!")
        except Exception as e:
            print(f"[ERROR] Error resetting database: {e}")
    else:
        print("Reset cancelled.")

if __name__ == "__main__":
    print("ChromaDB Setup")
    print("=" * 30)
    
    # Test connection first
    if test_connection():
        print("\nChecking existing collections...")
        existing_collections = check_collections()
        
        print("\nCreating/updating collections...")
        init_db()
        
        print("\nFinal collection check...")
        final_collections = check_collections()
        
        print(f"\n[OK] Setup complete! ChromaDB has {len(final_collections)} collections.")
        
        # Debug: List number of documents in each collection
        print("\n[DEBUG] Document counts per collection:")
        client = get_chroma_client()
        for name in final_collections:
            try:
                col = client.get_collection(name=name)
                # Try to count documents (if API supports it)
                try:
                    count = len(col.get()['ids'])
                except Exception:
                    count = 'unknown'
                print(f"  - {name}: {count} documents")
            except Exception as e:
                print(f"  - {name}: error ({e})")
    else:
        print("\n[ERROR] Cannot connect to ChromaDB.")
        print("\nTroubleshooting:")
        print("1. Make sure Docker is running: docker-compose ps")
        print("2. Check if ChromaDB container is healthy:")
        print("   docker-compose logs chromadb")
        print("3. Try restarting Docker containers:")
        print("   docker-compose down")
        print("   docker-compose up -d")
        print("4. Wait a few seconds for ChromaDB to start up")