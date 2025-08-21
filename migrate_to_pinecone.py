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
            from pinecone import Pinecone
        except ImportError:
            print("📦 Installing pinecone-client...")
            os.system("pip install pinecone-client==3.0.0")
            from pinecone import Pinecone
        
        # Check for Pinecone API key
        api_key = os.environ.get("PINECONE_API_KEY")
        if not api_key:
            print("❌ PINECONE_API_KEY environment variable not set")
            print("💡 Get your API key from: https://app.pinecone.io/")
            print("💡 Set it with: $env:PINECONE_API_KEY='your_key_here'")
            return False
        
        # Initialize Pinecone with newer API
        pc = Pinecone(api_key=api_key)
        
        # Create index if it doesn't exist
        index_name = "northeastern-university"
        if index_name not in pc.list_indexes().names():
            print(f"📊 Creating Pinecone index: {index_name}")
            pc.create_index(
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
        from pinecone import Pinecone
        from sentence_transformers import SentenceTransformer
        
        # Initialize Pinecone
        api_key = os.environ.get("PINECONE_API_KEY")
        pc = Pinecone(api_key=api_key)
        index = pc.Index("northeastern-university")
        
        # Load embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get documents from ChromaDB
        chroma_client = get_chroma_client()
        collection = chroma_client.get_collection(name="documents")
        
        # Get all documents
        results = collection.get()
        documents = results['documents']
        metadatas = results['metadatas']
        ids = results['ids']
        
        print(f"📊 Found {len(documents)} documents to migrate")
        
        # Migrate in batches
        batch_size = 100
        total_migrated = 0
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size] if metadatas else [{}] * len(batch_docs)
            batch_ids = ids[i:i+batch_size]
            
            # Generate embeddings
            embeddings = model.encode(batch_docs).tolist()
            
            # Prepare vectors for Pinecone
            vectors = []
            for doc_id, embedding, document, metadata in zip(batch_ids, embeddings, batch_docs, batch_metadatas):
                # Optimize metadata to stay within Pinecone's 40KB limit
                optimized_metadata = {
                    'collection': 'documents',
                    'doc_hash': str(hash(document)),
                    'doc_length': len(document)
                }
                
                # Add essential metadata fields only
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
            
            # Upsert to Pinecone
            index.upsert(vectors=vectors)
            total_migrated += len(vectors)
            print(f"✅ Migrated batch {i//batch_size + 1}: {len(vectors)} documents")
        
        print(f"\n🎉 Migration complete! {total_migrated} documents migrated to Pinecone")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
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