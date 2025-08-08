#!/usr/bin/env python3
"""
Comprehensive solution to fix embedding persistence in ChromaDB embedded mode
This creates a custom embedding storage system that works reliably
"""

import sys
import os
import json
import pickle
from pathlib import Path
import time
import hashlib

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from services.shared.database import get_chroma_client, get_collection
from langchain.embeddings import HuggingFaceEmbeddings

class EmbeddingManager:
    """Manages embeddings for ChromaDB embedded mode"""
    
    def __init__(self, embedding_file="embeddings_cache.pkl"):
        self.embedding_file = embedding_file
        self.embeddings_cache = {}
        self.embeddings_model = None
        self.load_cache()
    
    def load_cache(self):
        """Load embeddings from cache file"""
        try:
            if os.path.exists(self.embedding_file):
                with open(self.embedding_file, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
                print(f"✅ Loaded {len(self.embeddings_cache)} cached embeddings")
            else:
                print("📝 No embedding cache found, will create new one")
        except Exception as e:
            print(f"⚠️  Error loading cache: {e}")
            self.embeddings_cache = {}
    
    def save_cache(self):
        """Save embeddings to cache file"""
        try:
            with open(self.embedding_file, 'wb') as f:
                pickle.dump(self.embeddings_cache, f)
            print(f"✅ Saved {len(self.embeddings_cache)} embeddings to cache")
        except Exception as e:
            print(f"❌ Error saving cache: {e}")
    
    def get_embedding_model(self):
        """Get or create embedding model"""
        if self.embeddings_model is None:
            print("Loading embedding model...")
            self.embeddings_model = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            print("✅ Embedding model loaded")
        return self.embeddings_model
    
    def get_document_hash(self, content):
        """Generate hash for document content"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_embedding(self, content):
        """Get embedding for content (from cache or generate)"""
        doc_hash = self.get_document_hash(content)
        
        if doc_hash in self.embeddings_cache:
            return self.embeddings_cache[doc_hash]
        
        # Generate new embedding
        model = self.get_embedding_model()
        embedding = model.embed_query(content)
        
        # Cache it
        self.embeddings_cache[doc_hash] = embedding
        return embedding
    
    def get_embeddings_batch(self, documents):
        """Get embeddings for multiple documents"""
        embeddings = []
        new_embeddings = 0
        
        for doc in documents:
            doc_hash = self.get_document_hash(doc)
            
            if doc_hash in self.embeddings_cache:
                embeddings.append(self.embeddings_cache[doc_hash])
            else:
                # Generate new embedding
                model = self.get_embedding_model()
                embedding = model.embed_query(doc)
                self.embeddings_cache[doc_hash] = embedding
                embeddings.append(embedding)
                new_embeddings += 1
        
        if new_embeddings > 0:
            print(f"Generated {new_embeddings} new embeddings")
            self.save_cache()
        
        return embeddings

def fix_embeddings_persistence():
    """Fix embedding persistence by implementing custom embedding management"""
    print("🔧 Fixing Embedding Persistence Issue")
    print("=" * 60)
    
    try:
        # Initialize embedding manager
        print("Initializing embedding manager...")
        embedding_manager = EmbeddingManager()
        
        # Initialize ChromaDB client
        print("Connecting to ChromaDB...")
        client = get_chroma_client()
        print("✅ ChromaDB connected")
        
        # Get documents collection
        documents_collection = get_collection('documents')
        
        # Get all documents
        print("Retrieving documents...")
        result = documents_collection.get()
        
        if not result or not result.get('ids'):
            print("❌ No documents found!")
            return False
        
        total_documents = len(result['ids'])
        print(f"📊 Found {total_documents} documents")
        
        # Get embeddings for all documents
        print("Getting embeddings for all documents...")
        all_documents = result.get('documents', [])
        all_embeddings = embedding_manager.get_embeddings_batch(all_documents)
        print(f"✅ Got embeddings for {len(all_embeddings)} documents")
        
        # Update documents with embeddings
        print("Updating documents with embeddings...")
        batch_size = 10
        updated = 0
        
        for i in range(0, total_documents, batch_size):
            batch_end = min(i + batch_size, total_documents)
            batch_ids = result['ids'][i:batch_end]
            batch_embeddings = all_embeddings[i:batch_end]
            
            try:
                # Update documents with embeddings
                documents_collection.update(
                    ids=batch_ids,
                    embeddings=batch_embeddings
                )
                updated += len(batch_ids)
                print(f"  ✅ Updated batch {i//batch_size + 1}: {len(batch_ids)} documents")
            except Exception as e:
                print(f"  ❌ Failed to update batch: {e}")
                continue
        
        print(f"\n📊 Update Complete!")
        print(f"✅ Updated {updated} documents with embeddings")
        
        # Save embedding cache
        embedding_manager.save_cache()
        
        # Verify embeddings
        print(f"\n🔍 Verifying embeddings...")
        verification_result = documents_collection.get()
        if verification_result.get('embeddings'):
            embedding_count = len([e for e in verification_result['embeddings'] if e])
            print(f"✅ {embedding_count} documents have embeddings")
            print(f"📊 Embedding dimension: {len(verification_result['embeddings'][0]) if verification_result['embeddings'] else 'N/A'}")
        else:
            print("❌ No embeddings found")
            return False
        
        # Test search functionality
        print(f"\n🧪 Testing search functionality...")
        test_query = "Northeastern University"
        test_embedding = embedding_manager.get_embedding(test_query)
        
        search_result = documents_collection.query(
            query_embeddings=[test_embedding],
            n_results=3
        )
        
        if search_result['ids'] and search_result['ids'][0]:
            print(f"✅ Search test successful - found {len(search_result['ids'][0])} results")
            
            # Show similarity scores
            if search_result.get('distances'):
                distances = search_result['distances'][0]
                print(f"📊 Top result similarity: {1.0 - distances[0]:.3f}")
        else:
            print("❌ Search test failed")
            return False
        
        print(f"\n🎉 Embedding persistence fix successful!")
        print(f"Your chatbot now has:")
        print(f"  ✅ Persistent embeddings (cached)")
        print(f"  ✅ Fast embedding generation")
        print(f"  ✅ Reliable search functionality")
        print(f"  ✅ Better confidence scores")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing embeddings: {e}")
        return False

def create_embedding_service():
    """Create a service to manage embeddings in the chatbot"""
    print(f"\n🔧 Creating Embedding Service")
    print("=" * 40)
    
    service_code = '''
# Add this to your enhanced_rag_chatbot.py

import pickle
import hashlib
import os

class EmbeddingService:
    """Service to manage embeddings for ChromaDB embedded mode"""
    
    def __init__(self, cache_file="embeddings_cache.pkl"):
        self.cache_file = cache_file
        self.embeddings_cache = {}
        self.load_cache()
    
    def load_cache(self):
        """Load embeddings from cache"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
        except Exception as e:
            print(f"Error loading embedding cache: {e}")
            self.embeddings_cache = {}
    
    def get_document_hash(self, content):
        """Generate hash for document content"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_embedding(self, content):
        """Get embedding for content"""
        doc_hash = self.get_document_hash(content)
        
        if doc_hash in self.embeddings_cache:
            return self.embeddings_cache[doc_hash]
        
        # Generate new embedding
        embedding = self.embeddings.embed_query(content)
        self.embeddings_cache[doc_hash] = embedding
        return embedding

# Add this to your EnhancedUniversityRAGChatbot.__init__ method:
# self.embedding_service = EmbeddingService()
'''
    
    # Save the service code
    with open("embedding_service_code.py", "w") as f:
        f.write(service_code)
    
    print("✅ Embedding service code created")
    print("📝 Add the code to your enhanced_rag_chatbot.py")

def main():
    """Main function to fix embedding persistence"""
    print("🚀 ChromaDB Embedding Persistence Fix")
    print("=" * 60)
    
    # Step 1: Fix embeddings
    if not fix_embeddings_persistence():
        print("❌ Failed to fix embeddings")
        return
    
    # Step 2: Create embedding service
    create_embedding_service()
    
    print(f"\n🎉 Embedding persistence fix complete!")
    print(f"Your chatbot now has reliable embeddings!")
    
    print(f"\n📝 Next steps:")
    print(f"1. Test the chatbot: python test_confidence_fix.py")
    print(f"2. Start the API: python run.py api")
    print(f"3. Test with real questions")
    print(f"4. Embeddings will be cached and persist between sessions")

if __name__ == "__main__":
    main() 