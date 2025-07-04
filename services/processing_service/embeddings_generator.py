from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.config import config

class EmbeddingsGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with local sentence transformer model
        Options:
        - all-MiniLM-L6-v2: Fast, good quality (384 dimensions)
        - all-mpnet-base-v2: Better quality, slower (768 dimensions)  
        - multi-qa-MiniLM-L6-cos-v1: Optimized for Q&A (384 dimensions)
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Embedding dimension: {self.embedding_dim}")
    
    def generate_embeddings(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Generate embeddings for text(s)"""
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            # Generate embeddings
            embeddings = self.model.encode(texts, show_progress_bar=len(texts) > 10)
            
            # Convert to list format
            if len(texts) == 1:
                return embeddings[0].tolist()
            else:
                return embeddings.tolist()
                
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Return zero embeddings as fallback
            if len(texts) == 1:
                return [0.0] * self.embedding_dim
            else:
                return [[0.0] * self.embedding_dim] * len(texts)
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Compute cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def find_most_similar(self, query_embedding: List[float], 
                         document_embeddings: List[List[float]], 
                         top_k: int = 5) -> List[tuple]:
        """Find most similar documents to query"""
        similarities = []
        
        for i, doc_embedding in enumerate(document_embeddings):
            similarity = self.compute_similarity(query_embedding, doc_embedding)
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]