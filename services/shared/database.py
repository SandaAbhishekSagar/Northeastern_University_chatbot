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

# Global ChromaDB client
chroma_client: Optional[chromadb.HttpClient] = None

def get_chroma_client() -> chromadb.HttpClient:
    """Get or create ChromaDB client"""
    global chroma_client
    
    if chroma_client is None:
        try:
            # Use a simpler configuration to avoid tenant issues
            chroma_client = chromadb.HttpClient(
                host=getattr(config, 'CHROMADB_HOST', 'localhost'),
                port=getattr(config, 'CHROMADB_HTTP_PORT', 8000)
            )
            print(f"[OK] ChromaDB client connected to {getattr(config, 'CHROMADB_HOST', 'localhost')}:{getattr(config, 'CHROMADB_HTTP_PORT', 8000)}")
        except Exception as e:
            print(f"[ERROR] ChromaDB client connection failed: {e}")
            # Try alternative connection method
            try:
                print("[INFO] Trying alternative connection method...")
                chroma_client = chromadb.Client(
                    chromadb.config.Settings(
                        chroma_api_impl="rest",
                        chroma_server_host=getattr(config, 'CHROMADB_HOST', 'localhost'),
                        chroma_server_http_port=getattr(config, 'CHROMADB_HTTP_PORT', 8000)
                    )
                )
                print(f"[OK] ChromaDB client connected using alternative method")
            except Exception as e2:
                print(f"[ERROR] Alternative connection also failed: {e2}")
                raise
    
    return chroma_client

def get_collection(name: str, create_if_not_exists: bool = True) -> chromadb.Collection:
    """Get a ChromaDB collection by name"""
    client = get_chroma_client()
    
    try:
        collection = client.get_collection(name=name)
        print(f"[OK] Retrieved collection: {name}")
        return collection
    except Exception as e:
        if create_if_not_exists:
            print(f"[INFO] Collection {name} not found, creating...")
            collection = client.create_collection(name=name)
            print(f"[OK] Created collection: {name}")
            return collection
        else:
            raise

def init_db():
    """Initialize ChromaDB collections"""
    print("Initializing ChromaDB collections...")
    
    try:
        client = get_chroma_client()
        
        # Create collections for different data types
        collections = [
            "universities",
            "documents", 
            "scrape_logs",
            "chat_sessions",
            "chat_messages"
        ]
        
        for collection_name in collections:
            try:
                collection = client.get_collection(name=collection_name)
                print(f"[OK] Collection exists: {collection_name}")
            except:
                collection = client.create_collection(name=collection_name)
                print(f"[OK] Created collection: {collection_name}")
        
        print("ChromaDB collections initialized successfully!")
        
    except Exception as e:
        print(f"[ERROR] Error initializing collections: {e}")
        raise

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