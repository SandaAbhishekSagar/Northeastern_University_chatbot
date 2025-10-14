
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
