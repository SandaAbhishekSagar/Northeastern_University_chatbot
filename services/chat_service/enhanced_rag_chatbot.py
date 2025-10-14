"""
Enhanced RAG Chatbot with Improved Semantic Search and Answer Generation
Features:
- Hybrid retrieval (semantic + keyword)
- Query expansion and reformulation
- Reranking of results
- Context-aware answer generation
- Confidence scoring
- Source attribution
"""

import sys
import os
import re
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
from datetime import datetime
import hashlib

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import BM25Retriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers.ensemble import EnsembleRetriever

from shared.config import config
from shared.chroma_service import ChromaService

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
                print(f"[OK] Loaded {len(self.embeddings_cache)} query embeddings")
                print(f"[OK] Loaded {len(self.document_embeddings)} document embeddings")
            else:
                print("[INFO] No enhanced embedding cache found, will create new one")
        except Exception as e:
            print(f"[ERROR] Error loading embedding cache: {e}")
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
            print(f"[OK] Saved {len(self.embeddings_cache)} query embeddings")
            print(f"[OK] Saved {len(self.document_embeddings)} document embeddings")
        except Exception as e:
            print(f"[ERROR] Error saving embedding cache: {e}")
    
    def get_embedding_model(self):
        """Get or create embedding model"""
        if self.embeddings_model is None:
            print("Loading embedding model...")
            self.embeddings_model = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            print("[OK] Embedding model loaded")
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
            
            from services.shared.database import get_collection
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

class EmbeddingService:
    """Service to manage embeddings for ChromaDB embedded mode"""
    
    def __init__(self, cache_file="embeddings_cache.pkl"):
        self.cache_file = cache_file
        self.embeddings_cache = {}
        self.embeddings_model = None
        self.load_cache()
    
    def load_cache(self):
        """Load embeddings from cache"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
                print(f"✅ Loaded {len(self.embeddings_cache)} cached embeddings")
            else:
                print("📝 No embedding cache found, will create new one")
        except Exception as e:
            print(f"⚠️  Error loading embedding cache: {e}")
            self.embeddings_cache = {}
    
    def save_cache(self):
        """Save embeddings to cache"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.embeddings_cache, f)
            print(f"✅ Saved {len(self.embeddings_cache)} embeddings to cache")
        except Exception as e:
            print(f"❌ Error saving embedding cache: {e}")
    
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

class EnhancedUniversityRAGChatbot:
    def __init__(self, model_name: str = "llama2:7b"):
        # Initialize ChromaDB service
        self.chroma_service = ChromaService()
        
        # Initialize enhanced embedding manager for persistence
        print("Initializing enhanced embedding manager...")
        self.enhanced_embedding_manager = EnhancedEmbeddingManager()
        
        # Initialize enhanced embeddings (for backward compatibility)
        print("Loading enhanced embedding model...")
        self.embeddings = self.enhanced_embedding_manager.get_embedding_model()
        
        # Initialize local LLM
        print(f"Loading local LLM: {model_name}")
        self.llm = Ollama(
            model=model_name,
            temperature=0.3,  # Lower temperature for more consistent answers
            top_p=0.9,
            top_k=40
        )
        
        # Test LLM
        try:
            test_response = self.llm("Hello")
            print(f"[OK] Local LLM {model_name} is working!")
        except Exception as e:
            print(f"[ERROR] Error with local LLM: {e}")
            print(f"Make sure to run: ollama pull {model_name}")
            raise
        
        # Initialize text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Query expansion patterns for Northeastern University
        self.query_expansions = {
            "admission": ["admissions", "apply", "application", "enrollment", "acceptance"],
            "program": ["programs", "majors", "degrees", "courses", "curriculum"],
            "tuition": ["cost", "fees", "financial aid", "scholarship", "payment"],
            "housing": ["dorm", "residence", "accommodation", "living", "campus housing"],
            "campus": ["university", "college", "school", "institution", "facilities"],
            "northeastern": ["NEU", "Northeastern University", "Boston campus", "university"],
            "co-op": ["cooperative education", "internship", "work experience", "professional experience"],
            "graduate": ["masters", "PhD", "doctoral", "postgraduate", "advanced degree"],
            "undergraduate": ["bachelors", "bachelor's", "college", "freshman", "sophomore", "junior", "senior"]
        }
        
        # Enhanced prompt templates
        self.answer_prompt = PromptTemplate(
            input_variables=["context", "question", "conversation_history"],
            template="""You are a knowledgeable Northeastern University assistant. Use the provided context to answer the student's question accurately and helpfully.

Previous conversation:
{conversation_history}

Relevant context from university documents:
{context}

Student Question: {question}

Instructions:
- Answer based primarily on the provided context
- If the context doesn't contain enough information, acknowledge this and provide general guidance
- Be specific about Northeastern University policies, programs, and procedures
- Include relevant details like requirements, deadlines, contact information, or URLs when available
- If mentioning costs, programs, or policies, specify they are for Northeastern University
- Be conversational but professional
- If you're unsure about specific details, suggest contacting the relevant department

Answer:"""
        )
        
        self.query_reformulation_prompt = PromptTemplate(
            input_variables=["original_query", "conversation_history"],
            template="""Given the original query and conversation history, create 2-3 alternative search queries that might help find relevant information.

Original Query: {original_query}
Conversation History: {conversation_history}

Generate alternative queries that:
- Use different but related terms
- Include Northeastern University specific terms
- Cover different aspects of the question
- Use synonyms and related concepts

Alternative queries (one per line):"""
        )
        
        # Confidence thresholds
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
    
    def expand_query(self, query: str, conversation_history: Optional[List[Dict]] = None) -> List[str]:
        """Expand query using synonyms and related terms"""
        expanded_queries = [query]
        
        # Add query expansion based on patterns
        query_lower = query.lower()
        for pattern, expansions in self.query_expansions.items():
            if pattern in query_lower:
                for expansion in expansions:
                    if expansion not in query_lower:
                        expanded_query = query.replace(pattern, expansion, 1)
                        expanded_queries.append(expanded_query)
        
        # Add Northeastern-specific context if not present
        if "northeastern" not in query_lower and "neu" not in query_lower:
            expanded_queries.append(f"Northeastern University {query}")
        
        # Use LLM for query reformulation
        try:
            history_text = ""
            if conversation_history:
                recent_history = conversation_history[-3:]  # Last 3 exchanges
                history_text = "\n".join([
                    f"{'User' if msg['type'] == 'user' else 'Assistant'}: {msg['content']}"
                    for msg in recent_history
                ])
            
            reformulation_prompt = self.query_reformulation_prompt.format(
                original_query=query,
                conversation_history=history_text
            )
            
            reformulated = self.llm(reformulation_prompt)
            if reformulated and reformulated.strip():
                # Parse reformulated queries
                lines = [line.strip() for line in reformulated.split('\n') if line.strip()]
                for line in lines[:3]:  # Take up to 3 reformulated queries
                    if line and line not in expanded_queries:
                        expanded_queries.append(line)
        
        except Exception as e:
            print(f"Query reformulation failed: {e}")
        
        return list(set(expanded_queries))  # Remove duplicates
    
    def hybrid_search(self, query: str, k: int = 10, university_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Perform hybrid search combining semantic and keyword matching"""
        try:
            # Get all documents for keyword search
            all_docs = self.chroma_service.get_all_documents(university_id=university_id)
            
            # Create document texts for keyword search
            doc_texts = []
            doc_metadata = []
            
            for doc in all_docs:
                # Extract file_name from extra_data if present
                file_name = None
                if doc.extra_data and isinstance(doc.extra_data, dict):
                    file_name = doc.extra_data.get('file_name')
                if not file_name and hasattr(doc, 'file_name'):
                    file_name = getattr(doc, 'file_name', None)
                doc_texts.append(doc.content)
                doc_metadata.append({
                    'id': doc.id,
                    'title': doc.title,
                    'source_url': doc.source_url,
                    'university_id': doc.university_id,
                    'extra_data': doc.extra_data,
                    'file_name': file_name
                })
            
            # Perform semantic search
            semantic_results = self.semantic_search(query, k=k, university_id=university_id)
            
            # Perform keyword search using BM25-like approach
            keyword_results = self.keyword_search(query, doc_texts, doc_metadata, k=k)
            
            # Combine and rerank results
            combined_results = self.combine_and_rerank(
                semantic_results, keyword_results, query, k=k
            )
            
            return combined_results
            
        except Exception as e:
            print(f"Error in hybrid search: {e}")
            # Fallback to semantic search only
            return self.semantic_search(query, k=k, university_id=university_id)
    
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
                # Extract file name from metadata or extra_data
                file_name = None
                if result['metadata'].get('extra_data'):
                    file_name = result['metadata']['extra_data'].get('file_name')
                if not file_name and result['metadata'].get('file_name'):
                    file_name = result['metadata']['file_name']
                documents.append({
                    'id': result['id'],
                    'title': result['metadata'].get('title', ''),
                    'content': result['content'],
                    'source_url': result['metadata'].get('source_url', ''),
                    'metadata': result['metadata'],
                    'similarity': result['similarity'],
                    'search_type': 'semantic',
                    'file_name': file_name
                })
            return documents
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def keyword_search(self, query: str, doc_texts: List[str], doc_metadata: List[Dict], k: int = 10) -> List[Dict[str, Any]]:
        """Simple keyword-based search using TF-IDF-like scoring"""
        try:
            query_terms = set(re.findall(r'\b\w+\b', query.lower()))
            results = []
            for i, (text, metadata) in enumerate(zip(doc_texts, doc_metadata)):
                text_lower = text.lower()
                text_terms = set(re.findall(r'\b\w+\b', text_lower))
                # Calculate keyword overlap
                overlap = len(query_terms.intersection(text_terms))
                total_terms = len(query_terms)
                if total_terms > 0:
                    keyword_score = overlap / total_terms
                    # Boost score for exact phrase matches
                    if query.lower() in text_lower:
                        keyword_score += 0.3
                    # Boost score for title matches
                    if metadata.get('title'):
                        title_lower = metadata['title'].lower()
                        title_overlap = len(query_terms.intersection(set(re.findall(r'\b\w+\b', title_lower))))
                        if title_overlap > 0:
                            keyword_score += 0.2
                    if keyword_score > 0:
                        # Extract file name from both metadata and extra_data
                        file_name = None
                        if metadata.get('file_name'):
                            file_name = metadata['file_name']
                        if not file_name and metadata.get('extra_data'):
                            file_name = metadata['extra_data'].get('file_name')
                        results.append({
                            'id': metadata['id'],
                            'title': metadata['title'],
                            'content': text,
                            'source_url': metadata['source_url'],
                            'metadata': metadata.get('extra_data', {}),
                            'similarity': min(keyword_score, 1.0),
                            'search_type': 'keyword',
                            'file_name': file_name
                        })
            # Sort by similarity and return top k
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:k]
        except Exception as e:
            print(f"Error in keyword search: {e}")
            return []
    
    def combine_and_rerank(self, semantic_results: List[Dict], keyword_results: List[Dict], 
                          query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Combine and rerank search results"""
        try:
            # Create a combined dictionary
            combined = {}
            
            # Add semantic results
            for doc in semantic_results:
                combined[doc['id']] = {
                    **doc,
                    'semantic_score': doc['similarity'],
                    'keyword_score': 0.0,
                    'combined_score': doc['similarity'] * 0.7  # Weight semantic search more
                }
            
            # Add keyword results
            for doc in keyword_results:
                if doc['id'] in combined:
                    combined[doc['id']]['keyword_score'] = doc['similarity']
                    combined[doc['id']]['combined_score'] += doc['similarity'] * 0.3
                else:
                    combined[doc['id']] = {
                        **doc,
                        'semantic_score': 0.0,
                        'keyword_score': doc['similarity'],
                        'combined_score': doc['similarity'] * 0.3
                    }
            
            # Apply content-based reranking
            reranked_results = []
            for doc_id, doc_data in combined.items():
                # Boost score for documents with more relevant content
                content_relevance = self.calculate_content_relevance(doc_data['content'], query)
                doc_data['combined_score'] *= (1 + content_relevance * 0.2)
                
                # Boost score for recent or important documents
                if doc_data.get('metadata', {}).get('last_updated'):
                    # Boost recent documents slightly
                    doc_data['combined_score'] *= 1.05
                
                reranked_results.append(doc_data)
            
            # Sort by combined score and return top k
            reranked_results.sort(key=lambda x: x['combined_score'], reverse=True)
            return reranked_results[:k]
            
        except Exception as e:
            print(f"Error in combine and rerank: {e}")
            # Fallback to semantic results
            return semantic_results[:k]
    
    def calculate_content_relevance(self, content: str, query: str) -> float:
        """Calculate content relevance score based on query terms"""
        try:
            query_terms = set(re.findall(r'\b\w+\b', query.lower()))
            content_lower = content.lower()
            content_terms = set(re.findall(r'\b\w+\b', content_lower))
            
            # Calculate term frequency
            term_freq = {}
            for term in query_terms:
                if term in content_terms:
                    term_freq[term] = content_lower.count(term)
            
            if not term_freq:
                return 0.0
            
            # Calculate relevance score
            total_freq = sum(term_freq.values())
            avg_freq = total_freq / len(term_freq)
            
            # Normalize by content length
            content_length = len(content.split())
            if content_length > 0:
                normalized_freq = avg_freq / content_length
                return min(normalized_freq * 100, 1.0)  # Cap at 1.0
            
            return 0.0
            
        except Exception as e:
            print(f"Error calculating content relevance: {e}")
            return 0.0
    
    def calculate_confidence(self, relevant_docs: List[Dict], question: str, answer: str) -> float:
        """Calculate enhanced confidence score based on multiple factors"""
        try:
            # Convert ChromaDB distance scores to similarity scores (distance is 0-2, similarity should be 0-1)
            def distance_to_similarity(distance):
                # ChromaDB uses cosine distance: 0 = identical, 2 = opposite
                # Convert to similarity: 1 = identical, 0 = opposite
                return max(0.0, 1.0 - (distance / 2.0))
            
            # Factor 1: Average similarity of retrieved documents (weighted by rank)
            weighted_similarities = []
            for i, doc in enumerate(relevant_docs):
                weight = 1.0 / (i + 1)  # Higher weight for top-ranked documents
                # Handle both distance and similarity scores
                if 'distance' in doc:
                    similarity = distance_to_similarity(doc['distance'])
                elif 'similarity' in doc:
                    similarity = doc['similarity']
                else:
                    similarity = doc.get('combined_score', 0.5)  # Default fallback
                weighted_similarities.append(similarity * weight)
            
            avg_weighted_similarity = sum(weighted_similarities) / len(weighted_similarities) if weighted_similarities else 0
            
            # Factor 2: Top document similarity (most important)
            if relevant_docs:
                if 'distance' in relevant_docs[0]:
                    top_doc_similarity = distance_to_similarity(relevant_docs[0]['distance'])
                elif 'similarity' in relevant_docs[0]:
                    top_doc_similarity = relevant_docs[0]['similarity']
                else:
                    top_doc_similarity = relevant_docs[0].get('combined_score', 0.5)
            else:
                top_doc_similarity = 0
            
            # Factor 3: Number of relevant documents with good similarity (lowered threshold)
            good_docs = []
            for doc in relevant_docs:
                if 'distance' in doc:
                    similarity = distance_to_similarity(doc['distance'])
                elif 'similarity' in doc:
                    similarity = doc['similarity']
                else:
                    similarity = doc.get('combined_score', 0.5)
                if similarity > 0.4:  # Lowered from 0.6 to 0.4
                    good_docs.append(doc)
            doc_coverage_score = min(len(good_docs) / 2.0, 1.0)  # Lowered from 3.0 to 2.0
            
            # Factor 4: Answer quality indicators (more lenient)
            answer_length = len(answer.split())
            length_score = 1.0
            if answer_length < 10:  # Lowered from 15
                length_score = 0.6  # Increased from 0.4
            elif answer_length < 20:  # Lowered from 30
                length_score = 0.8  # Increased from 0.7
            elif answer_length > 1000:  # Increased from 800
                length_score = 0.9  # Increased from 0.8
            
            # Factor 5: Presence of uncertainty indicators in answer (less penalizing)
            uncertainty_indicators = [
                "i don't know", "i'm not sure", "i don't have", "not enough information",
                "unclear", "uncertain", "i cannot", "unable to", "no information available"
            ]
            uncertainty_score = 1.0
            answer_lower = answer.lower()
            uncertainty_count = sum(1 for indicator in uncertainty_indicators if indicator in answer_lower)
            uncertainty_score = max(0.5, 1.0 - (uncertainty_count * 0.1))  # Less penalizing
            
            # Factor 6: Source diversity and quality
            unique_sources = len(set(doc.get('source_url', '') for doc in relevant_docs))
            source_diversity_score = min(unique_sources / 2.0, 1.0)  # Lowered from 3.0
            
            # Factor 7: Question-answer relevance (simple keyword matching)
            question_words = set(question.lower().split())
            answer_words = set(answer.lower().split())
            common_words = question_words.intersection(answer_words)
            relevance_score = len(common_words) / max(len(question_words), 1)
            
            # Factor 8: Presence of specific Northeastern information (more generous)
            northeastern_indicators = [
                "northeastern", "neu", "boston", "co-op", "cooperative education",
                "snell library", "husky", "registrar", "admissions", "housing", "university", "college"
            ]
            northeastern_score = 0.6  # Increased base score from 0.5
            for indicator in northeastern_indicators:
                if indicator in answer_lower:
                    northeastern_score += 0.05  # Reduced increment from 0.1
            northeastern_score = min(northeastern_score, 1.0)
            
            # Combine all factors with adjusted weights (more emphasis on similarity)
            confidence = (
                top_doc_similarity * 0.35 +  # Increased from 0.25
                avg_weighted_similarity * 0.25 +  # Increased from 0.20
                doc_coverage_score * 0.15 +
                length_score * 0.08 +  # Reduced from 0.10
                uncertainty_score * 0.10 +  # Reduced from 0.15
                source_diversity_score * 0.02 +  # Reduced from 0.05
                relevance_score * 0.03 +  # Reduced from 0.05
                northeastern_score * 0.02  # Reduced from 0.05
            )
            
            # Boost confidence if we have good top document similarity
            if top_doc_similarity > 0.6:
                confidence = min(1.0, confidence * 1.2)  # 20% boost
            
            return min(max(confidence, 0.0), 1.0)
            
        except Exception as e:
            print(f"Error calculating confidence: {e}")
            return 0.5  # Increased default confidence from 0.3
    
    def should_show_answer(self, confidence: float, question: str, answer: str) -> Tuple[bool, str]:
        """Determine if answer should be shown based on confidence threshold"""
        # Lower base threshold for more lenient filtering
        base_threshold = 0.25  # Lowered from 0.4
        
        # Lower threshold for general questions
        if any(word in question.lower() for word in ['what', 'how', 'when', 'where', 'why']):
            threshold = base_threshold - 0.05  # Reduced from 0.1
        # Higher threshold for specific factual questions
        elif any(word in question.lower() for word in ['cost', 'deadline', 'requirement', 'policy', 'fee']):
            threshold = base_threshold + 0.15  # Reduced from 0.2
        else:
            threshold = base_threshold
        
        if confidence < threshold:
            return False, f"I don't have enough confident information to answer that question about Northeastern University. My confidence level is {confidence:.1%}. Please try rephrasing your question or contact the relevant department directly."
        
        return True, answer
    
    def store_user_feedback(self, session_id: str, question: str, answer: str, 
                          rating: int, feedback_text: str = "", sources: Optional[List[Dict]] = None):
        """Store user feedback for continuous improvement"""
        try:
            # Create feedback record
            feedback_data = {
                'session_id': session_id,
                'question': question,
                'answer': answer,
                'rating': rating,  # 1-5 scale
                'feedback_text': feedback_text,
                'sources': sources or [],
                'timestamp': datetime.now().isoformat(),
                'confidence': self.calculate_confidence(sources if sources else [], question, answer)
            }
            
            # Store in ChromaDB (we'll use a special collection for feedback)
            self.chroma_service.store_feedback(feedback_data)
            
            # Log for analysis
            print(f"Feedback stored - Rating: {rating}/5, Confidence: {feedback_data['confidence']:.2f}")
            
        except Exception as e:
            print(f"Error storing user feedback: {e}")
    
    def get_feedback_analytics(self) -> Dict[str, Any]:
        """Get analytics on user feedback for improvement"""
        try:
            feedback_data = self.chroma_service.get_all_feedback()
            
            if not feedback_data:
                return {
                    'total_feedback': 0,
                    'average_rating': 0,
                    'confidence_correlation': 0,
                    'common_issues': [],
                    'improvement_suggestions': []
                }
            
            # Calculate analytics
            total_feedback = len(feedback_data)
            ratings = [f['rating'] for f in feedback_data]
            average_rating = sum(ratings) / len(ratings)
            
            # Confidence correlation
            confidences = [f['confidence'] for f in feedback_data]
            if len(confidences) > 1:
                confidence_correlation = np.corrcoef(ratings, confidences)[0, 1]
            else:
                confidence_correlation = 0
            
            # Identify common issues
            low_rated_feedback = [f for f in feedback_data if f['rating'] <= 2]
            common_issues = []
            if low_rated_feedback:
                # Analyze patterns in low-rated feedback
                issue_patterns = {
                    'no_information': ['no information', 'not found', 'don\'t have'],
                    'incorrect_info': ['wrong', 'incorrect', 'outdated'],
                    'unclear_answer': ['unclear', 'confusing', 'vague'],
                    'missing_details': ['more details', 'specific', 'contact']
                }
                
                for pattern_name, keywords in issue_patterns.items():
                    count = sum(1 for f in low_rated_feedback 
                              if any(kw in f['feedback_text'].lower() for kw in keywords))
                    if count > 0:
                        common_issues.append({
                            'issue': pattern_name,
                            'count': count,
                            'percentage': count / len(low_rated_feedback) * 100
                        })
            
            # Generate improvement suggestions
            improvement_suggestions = []
            if average_rating < 3.5:
                improvement_suggestions.append("Consider expanding knowledge base with more specific Northeastern information")
            if confidence_correlation < 0.5:
                improvement_suggestions.append("Review confidence scoring algorithm - may not align with user satisfaction")
            if len(low_rated_feedback) > total_feedback * 0.3:
                improvement_suggestions.append("High number of low ratings - consider improving answer generation")
            
            return {
                'total_feedback': total_feedback,
                'average_rating': round(average_rating, 2),
                'confidence_correlation': round(confidence_correlation, 3),
                'common_issues': common_issues,
                'improvement_suggestions': improvement_suggestions,
                'recent_feedback': feedback_data[-5:]  # Last 5 feedback entries
            }
            
        except Exception as e:
            print(f"Error getting feedback analytics: {e}")
            return {
                'total_feedback': 0,
                'average_rating': 0,
                'confidence_correlation': 0,
                'common_issues': [],
                'improvement_suggestions': ['Error retrieving analytics']
            }
    
    def generate_enhanced_response(self, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate enhanced response with confidence filtering"""
        try:
            # Get conversation history
            conversation_history = []
            if session_id:
                conversation_history = self.get_conversation_history(session_id)
            
            # Expand query for better retrieval
            expanded_queries = self.expand_query(question, conversation_history)
            
            # Perform hybrid search with expanded queries
            all_results = []
            for query in expanded_queries[:3]:  # Use top 3 expanded queries
                results = self.hybrid_search(query, k=5)
                all_results.extend(results)
            
            # Remove duplicates and get top results
            unique_results = {}
            for result in all_results:
                if result['id'] not in unique_results:
                    unique_results[result['id']] = result
                else:
                    # Keep the one with higher combined score
                    if result.get('combined_score', result['similarity']) > unique_results[result['id']].get('combined_score', unique_results[result['id']]['similarity']):
                        unique_results[result['id']] = result
            
            relevant_docs = sorted(
                unique_results.values(),
                key=lambda x: x.get('combined_score', x['similarity']),
                reverse=True
            )[:5]
            
            if not relevant_docs:
                return {
                    'answer': "I don't have enough information in my knowledge base to answer that question about Northeastern University. Please try asking about specific programs, admissions, courses, or policies.",
                    'sources': [],
                    'confidence': 0.0,
                    'search_queries': expanded_queries,
                    'should_show': False,
                    'feedback_requested': True
                }
            
            # Prepare context with better formatting and enhanced source information
            context_parts = []
            sources = []
            
            # Filter and prioritize high similarity sources
            high_similarity_threshold = 0.6
            high_similarity_docs = [doc for doc in relevant_docs if doc.get('combined_score', doc.get('similarity', 0)) >= high_similarity_threshold]
            other_docs = [doc for doc in relevant_docs if doc.get('combined_score', doc.get('similarity', 0)) < high_similarity_threshold]
            
            # Prioritize high similarity documents first
            prioritized_docs = high_similarity_docs + other_docs
            
            for i, doc in enumerate(prioritized_docs):
                # Create a more structured context
                content_preview = doc['content'][:1000] + "..." if len(doc['content']) > 1000 else doc['content']
                # Use title and source, but no numbering
                if doc['title'] and doc['source_url']:
                    context_part = f"{doc['title']} ({doc['source_url']}):\n{content_preview}"
                elif doc['title']:
                    context_part = f"{doc['title']}:\n{content_preview}"
                elif doc['source_url']:
                    context_part = f"Source: {doc['source_url']}\n{content_preview}"
                else:
                    context_part = content_preview
                context_parts.append(context_part)
                
                # Enhanced source information
                similarity_score = doc.get('combined_score', doc.get('similarity', 0))
                search_type = doc.get('search_type', 'combined')
                
                # Get file_name directly from metadata since it's flattened
                file_name = doc.get('file_name', '')
                
                # Determine source quality indicator
                if similarity_score >= 0.8:
                    quality_indicator = "excellent"
                elif similarity_score >= 0.6:
                    quality_indicator = "good"
                elif similarity_score >= 0.4:
                    quality_indicator = "moderate"
                else:
                    quality_indicator = "low"
                
                sources.append({
                    'title': doc['title'],
                    'url': doc['source_url'],
                    'file_name': file_name,
                    'similarity': similarity_score,
                    'search_type': search_type,
                    'quality': quality_indicator,
                    'content_preview': content_preview[:200] + "..." if len(content_preview) > 200 else content_preview,
                    'rank': i + 1
                })
            
            context = "\n\n".join(context_parts)
            
            # Format conversation history for the prompt
            history_text = ""
            if conversation_history:
                history_lines = []
                for msg in conversation_history[-4:]:  # Last 4 messages
                    role = "Student" if msg['type'] == 'user' else "Assistant"
                    history_lines.append(f"{role}: {msg['content']}")
                history_text = "\n".join(history_lines)
            
            # Generate answer with enhanced prompt
            prompt = self.answer_prompt.format(
                context=context,
                question=question,
                conversation_history=history_text
            )
            
            print(f"Generating enhanced response for: {question[:50]}...")
            answer = self.llm(prompt)
            
            # Calculate confidence based on multiple factors
            confidence = self.calculate_confidence(relevant_docs, question, answer)
            
            # Apply confidence filtering
            should_show, final_answer = self.should_show_answer(confidence, question, answer)
            
            # Store conversation if session_id provided
            if session_id:
                self.store_conversation(session_id, question, final_answer, sources)
            
            return {
                'answer': final_answer.strip(),
                'sources': sources,
                'confidence': confidence,
                'search_queries': expanded_queries,
                'retrieval_method': 'hybrid',
                'should_show': should_show,
                'feedback_requested': not should_show or confidence < 0.6
            }
            
        except Exception as e:
            print(f"Error generating enhanced response: {e}")
            return {
                'answer': "I'm sorry, I encountered an error while processing your question. Please try rephrasing your question or try again in a moment.",
                'sources': [],
                'confidence': 0.0,
                'search_queries': [],
                'retrieval_method': 'error',
                'should_show': False,
                'feedback_requested': True
            }
    
    def store_conversation(self, session_id: str, question: str, answer: str, sources: List[Dict]):
        """Store conversation in ChromaDB"""
        try:
            # Get or create chat session
            chat_session = self.chroma_service.get_chat_session(session_id)
            if not chat_session:
                chat_session = self.chroma_service.create_chat_session()
                chat_session.id = session_id
            
            # Store user message
            self.chroma_service.create_chat_message(
                session_id=session_id,
                message_type='user',
                content=question
            )
            
            # Store assistant message with sources
            self.chroma_service.create_chat_message(
                session_id=session_id,
                message_type='assistant',
                content=answer,
                sources=sources
            )
            
        except Exception as e:
            print(f"Error storing conversation: {e}")
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history from ChromaDB"""
        try:
            messages = self.chroma_service.get_chat_messages(session_id, limit=limit)
            history = []
            
            for msg in messages:
                history.append({
                    'type': msg.message_type,
                    'content': msg.content,
                    'timestamp': msg.created_at,
                    'sources': msg.sources if hasattr(msg, 'sources') else None
                })
            
            return history
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []

def create_enhanced_chatbot(model_type: str = "llama2"):
    """Factory function to create enhanced chatbot with specified model"""
    model_name = f"{model_type}:7b" if ":" not in model_type else model_type
    return EnhancedUniversityRAGChatbot(model_name=model_name) 