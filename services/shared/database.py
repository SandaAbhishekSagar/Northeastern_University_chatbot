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

# Check if using Pinecone
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT", "us-east-1-aws")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "northeastern-university")

# Global client instances
chroma_client = None
pinecone_index = None
database_type = None

def get_database_type():
    """Determine which database to use based on environment variables"""
    global database_type
    
    if database_type is None:
        if PINECONE_API_KEY:
            database_type = "pinecone"
            print("🌲 Using Pinecone Vector Database")
        elif CHROMA_CLOUD_TOKEN:
            database_type = "chromadb_cloud"
            print("☁️  Using ChromaDB Cloud")
        else:
            database_type = "chromadb_local"
            print("📁 Using Local ChromaDB")
    
    return database_type

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
            chroma_data_path.mkdir(exist_ok=True)
            chroma_client = chromadb.PersistentClient(
                path=str(chroma_data_path),
                settings=Settings(anonymized_telemetry=False)
            )
            print("✅ Connected to local ChromaDB")
        
        return chroma_client
        
    except Exception as e:
        print(f"❌ Failed to connect to ChromaDB: {e}")
        raise

def get_pinecone_index():
    """Get Pinecone index"""
    global pinecone_index
    
    if pinecone_index is not None:
        return pinecone_index
    
    try:
        from pinecone import Pinecone
        
        # Initialize Pinecone with newer API
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index exists, create if not
        if PINECONE_INDEX_NAME not in pc.list_indexes().names():
            print(f"📊 Creating Pinecone index: {PINECONE_INDEX_NAME}")
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=384,  # For all-MiniLM-L6-v2 embeddings
                metric="cosine"
            )
            print("✅ Pinecone index created")
        else:
            print(f"✅ Using existing Pinecone index: {PINECONE_INDEX_NAME}")
        
        # Get the index
        pinecone_index = pc.Index(PINECONE_INDEX_NAME)
        return pinecone_index
        
    except Exception as e:
        print(f"❌ Failed to connect to Pinecone: {e}")
        raise

def get_collection(collection_name):
    """Get collection - works with both ChromaDB and Pinecone"""
    db_type = get_database_type()
    
    if db_type == "pinecone":
        # For Pinecone, we use a single index with metadata filtering
        return get_pinecone_index()
    else:
        # For ChromaDB
        client = get_chroma_client()
        try:
            return client.get_collection(name=collection_name)
        except:
            return client.create_collection(name=collection_name)

def init_db():
    """Initialize database collections"""
    db_type = get_database_type()
    
    if db_type == "pinecone":
        # Pinecone uses a single index, no need to create collections
        get_pinecone_index()
        print("✅ Pinecone database initialized")
    else:
        # ChromaDB collections
        client = get_chroma_client()
        collections = ["universities", "documents", "scrape_logs", "chat_sessions", "chat_messages", "feedback"]
        
        for collection_name in collections:
            try:
                client.get_collection(name=collection_name)
                print(f"[OK] Retrieved collection: {collection_name}")
            except:
                client.create_collection(name=collection_name)
                print(f"[INFO] Collection {collection_name} not found, creating...")

def add_documents_to_pinecone(documents, metadatas=None, ids=None, collection_name="documents"):
    """Add documents to Pinecone with proper metadata"""
    try:
        from sentence_transformers import SentenceTransformer
        
        # Load embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Generate embeddings
        embeddings = model.encode(documents).tolist()
        
        # Prepare vectors for Pinecone
        vectors = []
        for i, (doc_id, embedding, document) in enumerate(zip(ids, embeddings, documents)):
            # Optimize metadata to stay within Pinecone's 40KB limit
            optimized_metadata = {
                'collection': collection_name
            }
            
            # Add essential metadata fields only
            if metadatas and i < len(metadatas):
                metadata = metadatas[i]
                for key, value in metadata.items():
                    if isinstance(value, str) and len(value) > 500:
                        # Truncate long text fields
                        optimized_metadata[key] = value[:500] + "..."
                    elif isinstance(value, (str, int, float, bool)) and len(str(value)) < 1000:
                        # Keep reasonable-sized fields
                        optimized_metadata[key] = value
            
            vectors.append({
                'id': doc_id,
                'values': embedding,
                'metadata': optimized_metadata
            })
        
        # Add to Pinecone
        index = get_pinecone_index()
        index.upsert(vectors=vectors)
        
        return len(vectors)
        
    except Exception as e:
        print(f"❌ Failed to add documents to Pinecone: {e}")
        raise

def query_pinecone(query_text, n_results=10, collection_name="documents"):
    """Query Pinecone with text similarity search"""
    try:
        from sentence_transformers import SentenceTransformer
        
        # Load embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Generate query embedding
        query_embedding = model.encode([query_text]).tolist()[0]
        
        # Query Pinecone
        index = get_pinecone_index()
        results = index.query(
            vector=query_embedding,
            top_k=n_results,
            include_metadata=True
        )
        
        # Format results to match ChromaDB format
        formatted_results = {
            'ids': [match['id'] for match in results['matches']],
            'documents': [match['metadata'].get('text', '') for match in results['matches']],  # Note: text is not stored in metadata anymore
            'metadatas': [{k: v for k, v in match['metadata'].items() if k != 'text'} for match in results['matches']],
            'distances': [match['score'] for match in results['matches']]
        }
        
        return formatted_results
        
    except Exception as e:
        print(f"❌ Failed to query Pinecone: {e}")
        raise

def get_pinecone_count(collection_name="documents"):
    """Get document count from Pinecone"""
    try:
        index = get_pinecone_index()
        stats = index.describe_index_stats()
        
        # Count documents in specific collection
        total_count = 0
        if 'namespaces' in stats:
            for namespace, details in stats['namespaces'].items():
                if namespace == collection_name or collection_name == "documents":
                    total_count += details.get('vector_count', 0)
        
        return total_count
        
    except Exception as e:
        print(f"❌ Failed to get Pinecone count: {e}")
        return 0

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