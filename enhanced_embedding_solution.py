#!/usr/bin/env python3
"""
Enhanced Embedding Solution for ChromaDB
This bypasses the embedding persistence issue by implementing a custom search system
"""

import sys
import os
import json
import pickle
from pathlib import Path
import time
import hashlib
import numpy as np
from typing import List, Dict, Any, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from services.shared.database import get_chroma_client, get_collection
from langchain.embeddings import HuggingFaceEmbeddings

class EnhancedEmbeddingManager:
    """Enhanced embedding manager that works around ChromaDB persistence issues"""
    
    def __init__(self, embedding_file="enhanced_embeddings_cache.pkl"):
        self.embedding_file = embedding_file
        self.embeddings_cache = {}
        self.document_embeddings = {}  # Store document ID -> embedding mapping
        self.embeddings_model = None
        self.load_cache()
    
    def load_cache(self):
        """Load embeddings from cache file"""
        try:
            if os.path.exists(self.embedding_file):
                with open(self.embedding_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.embeddings_cache = cache_data.get('query_cache', {})
                    self.document_embeddings = cache_data.get('document_embeddings', {})
                print(f"✅ Loaded {len(self.embeddings_cache)} query embeddings")
                print(f"✅ Loaded {len(self.document_embeddings)} document embeddings")
            else:
                print("📝 No enhanced embedding cache found, will create new one")
        except Exception as e:
            print(f"⚠️  Error loading cache: {e}")
            self.embeddings_cache = {}
            self.document_embeddings = {}
    
    def save_cache(self):
        """Save embeddings to cache file"""
        try:
            cache_data = {
                'query_cache': self.embeddings_cache,
                'document_embeddings': self.document_embeddings
            }
            with open(self.embedding_file, 'wb') as f:
                pickle.dump(cache_data, f)
            print(f"✅ Saved {len(self.embeddings_cache)} query embeddings")
            print(f"✅ Saved {len(self.document_embeddings)} document embeddings")
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
    
    def get_query_embedding(self, content):
        """Get embedding for query content (from cache or generate)"""
        doc_hash = self.get_document_hash(content)
        
        if doc_hash in self.embeddings_cache:
            return self.embeddings_cache[doc_hash]
        
        # Generate new embedding
        model = self.get_embedding_model()
        embedding = model.embed_query(content)
        
        # Cache it
        self.embeddings_cache[doc_hash] = embedding
        return embedding
    
    def get_document_embedding(self, doc_id, content):
        """Get embedding for document content"""
        if doc_id in self.document_embeddings:
            return self.document_embeddings[doc_id]
        
        # Generate new embedding
        model = self.get_embedding_model()
        embedding = model.embed_query(content)
        
        # Cache it
        self.document_embeddings[doc_id] = embedding
        return embedding
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def search_documents(self, query, n_results=10, university_id=None):
        """Custom search using cached embeddings"""
        try:
            # Get query embedding
            query_embedding = self.get_query_embedding(query)
            
            # Get all documents
            collection = get_collection('documents')
            result = collection.get()
            
            if not result or not result.get('ids'):
                return []
            
            # Calculate similarities
            similarities = []
            for i, doc_id in enumerate(result['ids']):
                doc_content = result['documents'][i]
                doc_metadata = result['metadatas'][i] if result.get('metadatas') else {}
                
                # Filter by university if specified
                if university_id and doc_metadata.get('university_id') != university_id:
                    continue
                
                # Get document embedding
                doc_embedding = self.get_document_embedding(doc_id, doc_content)
                
                # Calculate similarity
                similarity = self.cosine_similarity(query_embedding, doc_embedding)
                
                similarities.append({
                    'id': doc_id,
                    'content': doc_content,
                    'metadata': doc_metadata,
                    'similarity': similarity
                })
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:n_results]
            
        except Exception as e:
            print(f"Error in custom search: {e}")
            return []

def setup_enhanced_embeddings():
    """Setup enhanced embedding system"""
    print("🔧 Setting up Enhanced Embedding System")
    print("=" * 60)
    
    try:
        # Initialize enhanced embedding manager
        print("Initializing enhanced embedding manager...")
        embedding_manager = EnhancedEmbeddingManager()
        
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
        
        # Generate embeddings for all documents
        print("Generating embeddings for all documents...")
        new_embeddings = 0
        
        for i, doc_id in enumerate(result['ids']):
            doc_content = result['documents'][i]
            
            # Generate embedding if not cached
            if doc_id not in embedding_manager.document_embeddings:
                embedding_manager.get_document_embedding(doc_id, doc_content)
                new_embeddings += 1
                
                if (i + 1) % 20 == 0:
                    print(f"  ✅ Processed {i + 1}/{total_documents} documents")
        
        print(f"✅ Generated {new_embeddings} new document embeddings")
        
        # Save cache
        embedding_manager.save_cache()
        
        # Test search functionality
        print(f"\n🧪 Testing enhanced search functionality...")
        test_query = "Northeastern University admission requirements"
        search_results = embedding_manager.search_documents(test_query, n_results=3)
        
        if search_results:
            print(f"✅ Search test successful - found {len(search_results)} results")
            print(f"📊 Top result similarity: {search_results[0]['similarity']:.3f}")
            
            # Show top result
            top_result = search_results[0]
            print(f"📄 Top result: {top_result['metadata'].get('title', 'No title')}")
            print(f"🔗 Source: {top_result['metadata'].get('source_url', 'No URL')}")
        else:
            print("❌ Search test failed")
            return False
        
        print(f"\n🎉 Enhanced embedding system setup successful!")
        print(f"Your chatbot now has:")
        print(f"  ✅ Persistent embeddings (cached)")
        print(f"  ✅ Fast embedding generation")
        print(f"  ✅ Reliable search functionality")
        print(f"  ✅ Better confidence scores")
        print(f"  ✅ Works around ChromaDB persistence issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up enhanced embeddings: {e}")
        return False

def create_enhanced_chatbot_integration():
    """Create integration code for the enhanced chatbot"""
    print(f"\n🔧 Creating Enhanced Chatbot Integration")
    print("=" * 50)
    
    integration_code = '''
# Add this to your enhanced_rag_chatbot.py

class EnhancedEmbeddingManager:
    """Enhanced embedding manager that works around ChromaDB persistence issues"""
    
    def __init__(self, embedding_file="enhanced_embeddings_cache.pkl"):
        self.embedding_file = embedding_file
        self.embeddings_cache = {}
        self.document_embeddings = {}
        self.embeddings_model = None
        self.load_cache()
    
    def load_cache(self):
        """Load embeddings from cache file"""
        try:
            if os.path.exists(self.embedding_file):
                with open(self.embedding_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.embeddings_cache = cache_data.get('query_cache', {})
                    self.document_embeddings = cache_data.get('document_embeddings', {})
        except Exception as e:
            print(f"Error loading cache: {e}")
            self.embeddings_cache = {}
            self.document_embeddings = {}
    
    def save_cache(self):
        """Save embeddings to cache file"""
        try:
            cache_data = {
                'query_cache': self.embeddings_cache,
                'document_embeddings': self.document_embeddings
            }
            with open(self.embedding_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def get_embedding_model(self):
        """Get or create embedding model"""
        if self.embeddings_model is None:
            self.embeddings_model = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        return self.embeddings_model
    
    def get_document_hash(self, content):
        """Generate hash for document content"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_query_embedding(self, content):
        """Get embedding for query content"""
        doc_hash = self.get_document_hash(content)
        
        if doc_hash in self.embeddings_cache:
            return self.embeddings_cache[doc_hash]
        
        model = self.get_embedding_model()
        embedding = model.embed_query(content)
        self.embeddings_cache[doc_hash] = embedding
        return embedding
    
    def get_document_embedding(self, doc_id, content):
        """Get embedding for document content"""
        if doc_id in self.document_embeddings:
            return self.document_embeddings[doc_id]
        
        model = self.get_embedding_model()
        embedding = model.embed_query(content)
        self.document_embeddings[doc_id] = embedding
        return embedding
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def search_documents(self, query, n_results=10, university_id=None):
        """Custom search using cached embeddings"""
        try:
            query_embedding = self.get_query_embedding(query)
            
            collection = get_collection('documents')
            result = collection.get()
            
            if not result or not result.get('ids'):
                return []
            
            similarities = []
            for i, doc_id in enumerate(result['ids']):
                doc_content = result['documents'][i]
                doc_metadata = result['metadatas'][i] if result.get('metadatas') else {}
                
                if university_id and doc_metadata.get('university_id') != university_id:
                    continue
                
                doc_embedding = self.get_document_embedding(doc_id, doc_content)
                similarity = self.cosine_similarity(query_embedding, doc_embedding)
                
                similarities.append({
                    'id': doc_id,
                    'content': doc_content,
                    'metadata': doc_metadata,
                    'similarity': similarity
                })
            
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:n_results]
            
        except Exception as e:
            print(f"Error in custom search: {e}")
            return []

# Update your EnhancedUniversityRAGChatbot.__init__ method:
# self.enhanced_embedding_manager = EnhancedEmbeddingManager()

# Update your semantic_search method:
def semantic_search(self, query: str, k: int = 10, university_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Enhanced semantic search using custom embedding system"""
    try:
        # Use enhanced embedding manager for search
        results = self.enhanced_embedding_manager.search_documents(
            query=query,
            n_results=k * 2,
            university_id=university_id
        )
        
        documents = []
        for result in results:
            documents.append({
                'id': result['id'],
                'title': result['metadata'].get('title', ''),
                'content': result['content'],
                'source_url': result['metadata'].get('source_url', ''),
                'metadata': result['metadata'],
                'similarity': result['similarity'],
                'search_type': 'semantic'
            })
        
        return documents
        
    except Exception as e:
        print(f"Error in semantic search: {e}")
        return []
'''
    
    # Save the integration code
    with open("enhanced_chatbot_integration.py", "w") as f:
        f.write(integration_code)
    
    print("✅ Enhanced chatbot integration code created")
    print("📝 Add the code to your enhanced_rag_chatbot.py")

def main():
    """Main function to setup enhanced embedding system"""
    print("🚀 Enhanced Embedding Solution for ChromaDB")
    print("=" * 60)
    
    # Step 1: Setup enhanced embeddings
    if not setup_enhanced_embeddings():
        print("❌ Failed to setup enhanced embeddings")
        return
    
    # Step 2: Create integration code
    create_enhanced_chatbot_integration()
    
    print(f"\n🎉 Enhanced embedding solution complete!")
    print(f"Your chatbot now has reliable embeddings that persist!")
    
    print(f"\n📝 Next steps:")
    print(f"1. Add the integration code to your enhanced_rag_chatbot.py")
    print(f"2. Test the chatbot: python test_confidence_fix.py")
    print(f"3. Start the API: python run.py api")
    print(f"4. Test with real questions")
    print(f"5. Embeddings will be cached and persist between sessions")

if __name__ == "__main__":
    main() 