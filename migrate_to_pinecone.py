#!/usr/bin/env python3
"""
Migrate to Pinecone Vector Database
Alternative to ChromaDB Cloud with better reliability
"""

import os
import sys
from pathlib import Path
import chromadb
from chromadb.config import Settings

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def setup_pinecone():
    """Setup Pinecone as an alternative vector database"""
    print("🌲 Setting up Pinecone Vector Database...")
    
    try:
        # Install pinecone if not available
        try:
            import pinecone
        except ImportError:
            print("📦 Installing pinecone-client...")
            os.system("pip install pinecone-client==3.0.0")
            import pinecone
        
        # Check for Pinecone API key
        api_key = os.environ.get("PINECONE_API_KEY")
        if not api_key:
            print("❌ PINECONE_API_KEY environment variable not set")
            print("💡 Get your API key from: https://app.pinecone.io/")
            print("💡 Set it with: $env:PINECONE_API_KEY='your_key_here'")
            return False
        
        # Initialize Pinecone with older API
        pinecone.init(api_key=api_key, environment="us-east-1-aws")
        
        # Create index if it doesn't exist
        index_name = "northeastern-university"
        if index_name not in pinecone.list_indexes():
            print(f"📊 Creating Pinecone index: {index_name}")
            pinecone.create_index(
                name=index_name,
                dimension=384,  # For all-MiniLM-L6-v2 embeddings
                metric="cosine"
            )
            print("✅ Pinecone index created")
        else:
            print(f"✅ Using existing Pinecone index: {index_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup Pinecone: {e}")
        return False

def migrate_to_pinecone():
    """Migrate local ChromaDB data to Pinecone"""
    
    if not setup_pinecone():
        return False
    
    try:
        import pinecone
        from sentence_transformers import SentenceTransformer
        
        # Initialize Pinecone
        api_key = os.environ.get("PINECONE_API_KEY")
        pc = pinecone.Index("northeastern-university")
        
        # Load embedding model
        print("🤖 Loading embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Connect to local ChromaDB
        local_data_path = project_root / "chroma_data"
        print(f"📁 Connecting to local ChromaDB at {local_data_path}")
        local_client = chromadb.PersistentClient(
            path=str(local_data_path),
            settings=Settings(anonymized_telemetry=False)
        )
        print("✅ Connected to local ChromaDB")
        
        # Get documents collection
        try:
            collection = local_client.get_collection(name="documents")
            local_data = collection.get()
            
            if not local_data.get('ids') or len(local_data['ids']) == 0:
                print("⚠️  No documents found in local ChromaDB")
                return False
                
        except Exception as e:
            print(f"❌ Could not get documents collection: {e}")
            return False
        
        # Migrate documents to Pinecone
        documents = local_data.get('documents', [])
        metadatas = local_data.get('metadatas', [])
        ids = local_data.get('ids', [])
        
        if not documents or not ids:
            print("⚠️  No documents to migrate")
            return False
        
        print(f"🔄 Migrating {len(documents)} documents to Pinecone...")
        
        # Process in batches
        batch_size = 100
        total_migrated = 0
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size] if metadatas else [{}] * len(batch_docs)
            
            # Generate embeddings
            print(f"📊 Generating embeddings for batch {i//batch_size + 1}...")
            embeddings = model.encode(batch_docs).tolist()
            
            # Prepare vectors for Pinecone
            vectors = []
            for j, (doc_id, embedding, metadata) in enumerate(zip(batch_ids, embeddings, batch_metadatas)):
                # Create a hash of the document content for efficient storage
                import hashlib
                doc_hash = hashlib.md5(batch_docs[j].encode()).hexdigest()
                
                # Optimize metadata to stay within Pinecone's 40KB limit
                optimized_metadata = {
                    'collection': 'documents',
                    'doc_hash': doc_hash,
                    'doc_length': len(batch_docs[j])
                }
                
                # Add essential metadata fields only
                if metadata:
                    # Keep only essential fields and truncate long values
                    for key, value in metadata.items():
                        if key in ['title', 'url', 'source', 'type']:  # Keep important fields
                            if isinstance(value, str) and len(value) > 200:
                                # Truncate long text fields
                                optimized_metadata[key] = value[:200] + "..."
                            elif isinstance(value, (str, int, float, bool)) and len(str(value)) < 500:
                                # Keep reasonable-sized fields
                                optimized_metadata[key] = value
                
                vectors.append({
                    'id': doc_id,
                    'values': embedding,
                    'metadata': optimized_metadata
                })
            
            # Upsert to Pinecone
            pc.upsert(vectors=vectors)
            total_migrated += len(vectors)
            print(f"✅ Migrated batch {i//batch_size + 1}: {len(vectors)} documents")
        
        print(f"\n🎉 Migration completed!")
        print(f"📊 Total documents migrated to Pinecone: {total_migrated}")
        print(f"🌲 Data is now available in Pinecone")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def setup_environment():
    """Setup environment for Pinecone"""
    print("🔧 Setting up Pinecone environment...")
    
    # Check if .env file exists
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("# Pinecone Configuration\n")
            f.write("PINECONE_API_KEY=your_api_key_here\n")
        print("✅ Created .env file")
        print("💡 Please edit .env file and add your Pinecone API key")
    else:
        print("✅ .env file already exists")
    
    print("\n📋 Next steps:")
    print("1. Get your Pinecone API key from: https://app.pinecone.io/")
    print("2. Add it to your .env file: PINECONE_API_KEY=your_key_here")
    print("3. Run this script again to migrate your data")

if __name__ == "__main__":
    print("🌲 Pinecone Migration Tool")
    print("=" * 50)
    
    # Check if API key is set
    if not os.environ.get("PINECONE_API_KEY"):
        print("❌ PINECONE_API_KEY not found in environment")
        setup_environment()
    else:
        print("✅ PINECONE_API_KEY found, starting migration...")
        success = migrate_to_pinecone()
        
        if success:
            print("\n🎯 Migration successful! Your app can now use Pinecone.")
            print("💡 Update your Railway environment variables:")
            print("   - PINECONE_API_KEY=your_api_key_here")
        else:
            print("\n❌ Migration failed. Please check the errors above.") 