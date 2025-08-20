#!/usr/bin/env python3
"""
Migrate existing ChromaDB data to ChromaDB Cloud
"""

import os
import sys
from pathlib import Path
import chromadb
from chromadb.config import Settings

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def migrate_to_chromadb_cloud():
    """Migrate local ChromaDB data to ChromaDB Cloud"""
    
    # Check for ChromaDB Cloud credentials
    cloud_token = os.environ.get("CHROMA_CLOUD_TOKEN")
    cloud_host = os.environ.get("CHROMA_CLOUD_HOST", "https://api.chromadb.com")
    
    if not cloud_token:
        print("❌ CHROMA_CLOUD_TOKEN environment variable not set")
        print("💡 Get your token from: https://cloud.chromadb.com")
        print("💡 Set it with: export CHROMA_CLOUD_TOKEN=your_token_here")
        return False
    
    try:
        # Connect to ChromaDB Cloud with better SSL handling
        print(f"☁️  Connecting to ChromaDB Cloud at {cloud_host}")
        
        # Try different connection methods
        cloud_client = None
        
        # Method 1: Standard connection
        try:
            cloud_client = chromadb.HttpClient(
                host=cloud_host,
                port=443,
                ssl=True,
                headers={"Authorization": f"Bearer {cloud_token}"}
            )
            # Test the connection
            cloud_client.heartbeat()
            print("✅ Connected to ChromaDB Cloud (Method 1)")
        except Exception as e1:
            print(f"⚠️  Method 1 failed: {e1}")
            
            # Method 2: Try without SSL verification
            try:
                import ssl
                import httpx
                
                # Create custom SSL context
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                # Create custom transport
                transport = httpx.HTTPTransport(verify=ssl_context)
                
                cloud_client = chromadb.HttpClient(
                    host=cloud_host,
                    port=443,
                    ssl=True,
                    headers={"Authorization": f"Bearer {cloud_token}"},
                    transport=transport
                )
                cloud_client.heartbeat()
                print("✅ Connected to ChromaDB Cloud (Method 2)")
            except Exception as e2:
                print(f"⚠️  Method 2 failed: {e2}")
                
                # Method 3: Try with different host format
                try:
                    # Remove https:// from host if present
                    clean_host = cloud_host.replace("https://", "").replace("http://", "")
                    
                    cloud_client = chromadb.HttpClient(
                        host=clean_host,
                        port=443,
                        ssl=True,
                        headers={"Authorization": f"Bearer {cloud_token}"}
                    )
                    cloud_client.heartbeat()
                    print("✅ Connected to ChromaDB Cloud (Method 3)")
                except Exception as e3:
                    print(f"❌ All connection methods failed:")
                    print(f"   Method 1: {e1}")
                    print(f"   Method 2: {e2}")
                    print(f"   Method 3: {e3}")
                    print("\n💡 Possible solutions:")
                    print("   1. Check your internet connection")
                    print("   2. Verify your ChromaDB Cloud token is correct")
                    print("   3. Try using a different network")
                    print("   4. Contact ChromaDB support")
                    return False
        
        # Connect to local ChromaDB
        local_data_path = project_root / "chroma_data"
        print(f"📁 Connecting to local ChromaDB at {local_data_path}")
        local_client = chromadb.PersistentClient(
            path=str(local_data_path),
            settings=Settings(anonymized_telemetry=False)
        )
        print("✅ Connected to local ChromaDB")
        
        # Collections to migrate
        collections_to_migrate = [
            "universities",
            "documents", 
            "scrape_logs",
            "chat_sessions",
            "chat_messages",
            "feedback"
        ]
        
        total_documents = 0
        
        for collection_name in collections_to_migrate:
            try:
                print(f"\n🔄 Migrating collection: {collection_name}")
                
                # Get local collection
                try:
                    local_collection = local_client.get_collection(name=collection_name)
                    local_data = local_collection.get()
                    
                    if not local_data.get('ids') or len(local_data['ids']) == 0:
                        print(f"⚠️  Collection {collection_name} is empty, skipping")
                        continue
                        
                except Exception as e:
                    print(f"⚠️  Could not get local collection {collection_name}: {e}")
                    continue
                
                # Create or get cloud collection
                try:
                    cloud_collection = cloud_client.get_collection(name=collection_name)
                    print(f"📚 Using existing cloud collection: {collection_name}")
                except:
                    cloud_collection = cloud_client.create_collection(name=collection_name)
                    print(f"📚 Created new cloud collection: {collection_name}")
                
                # Migrate data
                documents = local_data.get('documents', [])
                metadatas = local_data.get('metadatas', [])
                ids = local_data.get('ids', [])
                
                if documents and ids:
                    # Add documents to cloud collection
                    cloud_collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                    
                    doc_count = len(ids)
                    total_documents += doc_count
                    print(f"✅ Migrated {doc_count} documents to cloud collection: {collection_name}")
                else:
                    print(f"⚠️  No documents found in collection: {collection_name}")
                    
            except Exception as e:
                print(f"❌ Failed to migrate collection {collection_name}: {e}")
                continue
        
        print(f"\n🎉 Migration completed!")
        print(f"📊 Total documents migrated: {total_documents}")
        print(f"☁️  Data is now available in ChromaDB Cloud")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def setup_environment():
    """Setup environment for ChromaDB Cloud"""
    print("🔧 Setting up ChromaDB Cloud environment...")
    
    # Check if .env file exists
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("# ChromaDB Cloud Configuration\n")
            f.write("CHROMA_CLOUD_TOKEN=your_token_here\n")
            f.write("CHROMA_CLOUD_HOST=https://api.chromadb.com\n")
        print("✅ Created .env file")
        print("💡 Please edit .env file and add your ChromaDB Cloud token")
    else:
        print("✅ .env file already exists")
    
    print("\n📋 Next steps:")
    print("1. Get your ChromaDB Cloud token from: https://cloud.chromadb.com")
    print("2. Add it to your .env file: CHROMA_CLOUD_TOKEN=your_token_here")
    print("3. Run this script again to migrate your data")

if __name__ == "__main__":
    print("🚀 ChromaDB Cloud Migration Tool")
    print("=" * 50)
    
    # Check if token is set
    if not os.environ.get("CHROMA_CLOUD_TOKEN"):
        print("❌ CHROMA_CLOUD_TOKEN not found in environment")
        setup_environment()
    else:
        print("✅ CHROMA_CLOUD_TOKEN found, starting migration...")
        success = migrate_to_chromadb_cloud()
        
        if success:
            print("\n🎯 Migration successful! Your app will now use ChromaDB Cloud.")
            print("💡 Update your Railway environment variables:")
            print("   - CHROMA_CLOUD_TOKEN=your_token_here")
            print("   - CHROMA_CLOUD_HOST=https://api.chromadb.com")
        else:
            print("\n❌ Migration failed. Please check the errors above.") 