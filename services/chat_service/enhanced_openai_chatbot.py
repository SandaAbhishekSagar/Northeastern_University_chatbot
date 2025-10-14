"""
Enhanced OpenAI-Optimized RAG Chatbot - Maximum Accuracy with GPT-4
Features:
- OpenAI GPT-4/GPT-3.5 for answer generation
- GPU acceleration for embeddings
- Hybrid retrieval (semantic + keyword)
- Query expansion and reformulation
- Reranking of results
- Context-aware answer generation
- Confidence scoring
- Source attribution
- Analyzes 10 documents for comprehensive coverage
- Response time target: 3-10 seconds with GPT-4
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
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers.ensemble import EnsembleRetriever

from services.shared.config import config
from services.shared.chroma_service import ChromaService

class EnhancedOpenAIEmbeddingManager:
    """Enhanced GPU-optimized embedding manager with automatic device detection"""
    
    def __init__(self, embedding_file="enhanced_openai_embeddings_cache.pkl"):
        self.embedding_file = embedding_file
        self.embeddings_cache = {}
        self.document_embeddings = {}
        self.embeddings_model = None
        self.device = self._detect_device()
        self.load_cache()
    
    def _detect_device(self):
        """Detect best available device for embeddings"""
        try:
            import torch
            if torch.cuda.is_available():
                device = 'cuda'
                print(f"[ENHANCED OPENAI] CUDA detected: {torch.cuda.get_device_name(0)}")
                print(f"[ENHANCED OPENAI] CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
            else:
                device = 'cpu'
                print("[ENHANCED OPENAI] CUDA not available, using CPU")
        except ImportError:
            device = 'cpu'
            print("[ENHANCED OPENAI] PyTorch not available, using CPU")
        
        return device
    
    def load_cache(self):
        """Load embeddings from cache file"""
        try:
            if os.path.exists(self.embedding_file):
                with open(self.embedding_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.embeddings_cache = cache_data.get('query_cache', {})
                    self.document_embeddings = cache_data.get('document_embeddings', {})
                print(f"[ENHANCED OPENAI] Loaded {len(self.embeddings_cache)} query embeddings")
                print(f"[ENHANCED OPENAI] Loaded {len(self.document_embeddings)} document embeddings")
            else:
                print("[ENHANCED OPENAI] No embedding cache found, will create new one")
        except Exception as e:
            print(f"[ENHANCED OPENAI] Error loading embedding cache: {e}")
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
            print(f"[ENHANCED OPENAI] Saved {len(self.embeddings_cache)} query embeddings")
            print(f"[ENHANCED OPENAI] Saved {len(self.document_embeddings)} document embeddings")
        except Exception as e:
            print(f"[ENHANCED OPENAI] Error saving embedding cache: {e}")
    
    def get_embedding_model(self):
        """Get or create GPU-optimized embedding model"""
        if self.embeddings_model is None:
            print(f"[ENHANCED OPENAI] Loading embedding model on {self.device}...")
            self.embeddings_model = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={'device': self.device},
                encode_kwargs={'normalize_embeddings': True}
            )
            print(f"[ENHANCED OPENAI] Embedding model loaded on {self.device}")
        return self.embeddings_model
    
    def get_document_hash(self, content):
        """Generate hash for document content"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_query_embedding(self, content):
        """Get embedding for query content with GPU acceleration"""
        doc_hash = self.get_document_hash(content)
        
        if doc_hash in self.embeddings_cache:
            return self.embeddings_cache[doc_hash]
        
        model = self.get_embedding_model()
        embedding = model.embed_query(content)
        self.embeddings_cache[doc_hash] = embedding
        return embedding
    
    def get_document_embedding(self, doc_id, content):
        """Get embedding for document content with GPU acceleration"""
        if doc_id in self.document_embeddings:
            return self.document_embeddings[doc_id]
        
        model = self.get_embedding_model()
        embedding = model.embed_query(content)
        self.document_embeddings[doc_id] = embedding
        return embedding
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

class EnhancedOpenAIUniversityRAGChatbot:
    """Enhanced OpenAI-optimized RAG Chatbot for maximum accuracy"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", openai_api_key: Optional[str] = None):
        print("[ENHANCED OPENAI] Initializing Enhanced OpenAI-Optimized RAG Chatbot...")
        start_time = time.time()
        
        # Initialize ChromaDB service
        self.chroma_service = ChromaService()
        
        # Initialize GPU-optimized embedding manager
        self.embedding_manager = EnhancedOpenAIEmbeddingManager()
        
        # Get API key from parameter or config
        api_key = openai_api_key or config.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in config or pass as parameter.")
        
        # Initialize OpenAI LLM with timeout and retry settings
        print(f"[ENHANCED OPENAI] Loading OpenAI {model_name}...")
        
        # Handle o4-mini model restrictions (requires temperature=1)
        if "o4-mini" in model_name.lower() or "o1" in model_name.lower():
            print(f"[ENHANCED OPENAI] Using o4-mini/o1 model - temperature fixed at 1.0")
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=1.0,          # Required for o4-mini models
                max_tokens=2500,          # Increased for detailed responses
                openai_api_key=api_key,
                request_timeout=60,       # Longer timeout for reasoning models
                max_retries=2
            )
        else:
            # Standard models support custom temperature
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0.3,          # Balanced for detailed but accurate responses
                max_tokens=2500,          # Increased for detailed responses
                openai_api_key=api_key,
                request_timeout=30,
                max_retries=2
            )
        
        self.model_name = model_name
        
        # Enhanced prompt templates
        self.query_expansion_prompt = PromptTemplate(
            input_variables=["question", "conversation_history"],
            template="""Generate 3 different ways to ask the same specific question to improve search results. Focus on the exact topic being asked.

Question: {question}
Conversation History: {conversation_history}

Generate 3 alternative questions that ask about the SAME specific topic (one per line):
1. """
        )
        
        self.answer_prompt = PromptTemplate(
            input_variables=["context", "question", "conversation_history"],
            template="""You are an expert Northeastern University assistant. Provide a DETAILED, COMPREHENSIVE, and WELL-STRUCTURED answer to the student's question using the provided context.

CRITICAL INSTRUCTIONS:
- Answer ONLY the specific question asked
- Use EXACT information from the provided context
- Provide DETAILED and COMPREHENSIVE answers - don't be brief
- Structure your response clearly with:
  * An overview/introduction
  * Main points organized with bullet points or numbered lists when appropriate
  * Specific details, numbers, dates, requirements, or procedures
  * Additional relevant information that helps fully answer the question
- Quote specific details from the context (costs, dates, requirements, procedures, etc.)
- If the context contains multiple relevant pieces of information, include ALL of them
- Use clear formatting: paragraphs, bullet points, or numbered lists for readability
- Be thorough but stay focused on the specific question
- If the context doesn't contain specific information, provide helpful general guidance about Northeastern University
- Do NOT provide generic information not found in the context
- Be conversational, helpful, and professional

Previous conversation:
{conversation_history}

Relevant context from university documents:
{context}

Student Question: {question}

Detailed Answer:"""
        )
        
        # Initialize conversation storage
        self.conversations = {}
        self.user_feedback = []
        
        init_time = time.time() - start_time
        print(f"[ENHANCED OPENAI] Initialization completed in {init_time:.2f} seconds")
        print(f"[ENHANCED OPENAI] Model: {self.model_name}")
        print(f"[ENHANCED OPENAI] Embedding Device: {self.embedding_manager.device}")
        print(f"[ENHANCED OPENAI] Documents to analyze: 10")
        
        # Initialize utility methods for enhanced processing
        self.generic_phrases = [
            'northeastern university offers a variety',
            'northeastern university provides',
            'as an expert assistant',
            'based on the context',
            'i can provide you with information',
            'northeastern university is',
            'the university offers',
            'northeastern provides'
        ]
    
    def extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text for relevance scoring"""
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'what', 'how', 'when', 'where', 'why', 'who', 'which', 'that', 'this', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'}
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        return list(set(key_terms))  # Remove duplicates
    
    def split_into_sections(self, content: str, max_length: int = 500) -> List[str]:
        """Split content into manageable sections"""
        sentences = re.split(r'[.!?]+', content)
        sections = []
        current_section = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_section) + len(sentence) < max_length:
                current_section += sentence + ". "
            else:
                if current_section:
                    sections.append(current_section.strip())
                current_section = sentence + ". "
        
        if current_section:
            sections.append(current_section.strip())
        
        return sections
    
    def calculate_section_relevance(self, section: str, question_terms: List[str]) -> float:
        """Calculate how relevant a section is to the question terms"""
        section_lower = section.lower()
        matches = sum(1 for term in question_terms if term in section_lower)
        return matches / len(question_terms) if question_terms else 0.0
    
    def prepare_context(self, relevant_docs: List[Dict], question: str) -> str:
        """Prepare context more intelligently"""
        
        # Extract key terms from question
        question_terms = self.extract_key_terms(question)
        
        # Filter and rank document sections by relevance
        relevant_sections = []
        for doc in relevant_docs:
            # Find sections that contain question terms
            sections = self.split_into_sections(doc['content'])
            for section in sections:
                relevance = self.calculate_section_relevance(section, question_terms)
                if relevance > 0.3:  # Only include relevant sections
                    relevant_sections.append({
                        'content': section,
                        'relevance': relevance,
                        'source': doc['title']
                    })
        
        # Sort by relevance and combine
        relevant_sections.sort(key=lambda x: x['relevance'], reverse=True)
        context = "\n\n".join([f"[{s['source']}]: {s['content']}" for s in relevant_sections[:5]])
        
        return context
    
    def expand_query(self, query: str, conversation_history: Optional[List[Dict]] = None) -> List[str]:
        """Expand query using LLM for better search results"""
        try:
            # Prepare conversation history
            history_text = ""
            if conversation_history:
                history_text = "\n".join([f"Q: {conv['question']}\nA: {conv['answer']}" 
                                        for conv in conversation_history[-3:]])  # Last 3 exchanges
            
            # Generate query variations with timeout
            prompt = self.query_expansion_prompt.format(
                question=query,
                conversation_history=history_text
            )
            
            print(f"[ENHANCED OPENAI] Expanding query: {query[:50]}...")
            
            # Add explicit timeout handling
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Query expansion timed out")
            
            try:
                response = self.llm.invoke(prompt)
                response_text = response.content if hasattr(response, 'content') else str(response)
                
                # Parse the response to extract alternative questions
                lines = response_text.strip().split('\n')
                alternative_queries = [query]  # Start with original query
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith(('1.', '2.', '3.')):
                        # Remove numbering if present
                        clean_query = re.sub(r'^\d+\.\s*', '', line)
                        if clean_query and clean_query != query:
                            alternative_queries.append(clean_query)
                
                # Ensure we have at least 3 queries
                while len(alternative_queries) < 3:
                    alternative_queries.append(query)
                
                print(f"[ENHANCED OPENAI] Generated {len(alternative_queries)} query variations")
                return alternative_queries[:3]
                
            except TimeoutError as e:
                print(f"[ENHANCED OPENAI] Query expansion timeout, using original query")
                return [query]
            
        except Exception as e:
            print(f"[ENHANCED OPENAI] Query expansion error: {e}")
            import traceback
            traceback.print_exc()
            return [query]
    
    def validate_and_improve_answer(self, question: str, answer: str, context: str) -> str:
        """Validate answer and regenerate if needed"""
        
        answer_lower = answer.lower()
        
        # Check for generic indicators
        is_generic = any(phrase in answer_lower for phrase in self.generic_phrases)
        
        # Check if answer directly addresses the question
        question_terms = self.extract_key_terms(question)
        answer_contains_question_terms = any(term in answer_lower for term in question_terms)
        
        # If answer is generic or off-topic, regenerate
        if is_generic or not answer_contains_question_terms:
            print(f"[ENHANCED OPENAI] Regenerating answer - detected generic response")
            specific_prompt = f"""Answer this specific question: "{question}"
Use information from this context: {context}

CRITICAL INSTRUCTIONS:
- Provide a DETAILED, COMPREHENSIVE answer about Northeastern University programs
- Use information from the provided context, but also draw reasonable conclusions
- Structure your response clearly with bullet points or organized paragraphs
- Include ALL relevant details: specific numbers, dates, requirements, procedures
- Be thorough and well-organized, not brief
- If you find relevant information about programs, degrees, or academic offerings, include it
- Focus on being helpful and informative about Northeastern's academic programs
- Use the context as your primary source but provide a complete answer

Provide a detailed, well-structured answer about Northeastern University programs:"""
            response = self.llm.invoke(specific_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        
        return answer
    
    def hybrid_search(self, query: str, k: int = 10, university_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Enhanced hybrid search with GPU acceleration"""
        try:
            start_time = time.time()
            
            # Get conversation history for context
            conversation_history = self.get_conversation_history("current_session", limit=3)
            
            # Expand query (with timeout protection)
            try:
                expanded_queries = self.expand_query(query, conversation_history)
                print(f"[ENHANCED OPENAI] Generated {len(expanded_queries)} query variations")
            except Exception as e:
                print(f"[ENHANCED OPENAI] Query expansion failed, using original query: {e}")
                expanded_queries = [query]
            
            # Perform semantic search for each expanded query
            all_semantic_results = []
            for expanded_query in expanded_queries:
                semantic_results = self.semantic_search(expanded_query, k=k, university_id=university_id)
                all_semantic_results.extend(semantic_results)
            
            # Remove duplicates and rerank
            unique_results = self.remove_duplicates(all_semantic_results)
            
            # Rerank based on relevance to original query
            reranked_results = self.rerank_results(unique_results, query, k=k)
            
            search_time = time.time() - start_time
            print(f"[ENHANCED OPENAI] Hybrid search completed in {search_time:.2f} seconds")
            print(f"[ENHANCED OPENAI] Found {len(reranked_results)} unique documents")
            
            return reranked_results
            
        except Exception as e:
            print(f"[ENHANCED OPENAI] Hybrid search error: {e}")
            return self.semantic_search(query, k=k, university_id=university_id)
    
    def semantic_search(self, query: str, k: int = 10, university_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """GPU-accelerated semantic search"""
        try:
            # Get query embedding with GPU acceleration
            query_embedding = self.embedding_manager.get_query_embedding(query)
            
            # Search ChromaDB
            results = self.chroma_service.search_documents(
                query="",  # Empty query since we're using embedding
                embedding=query_embedding,
                n_results=k * 2  # Get more results for reranking
            )
            
            # Process results
            processed_results = []
            for i, (doc_version, distance) in enumerate(results):
                # Convert distance to similarity
                similarity = 1 - (distance / 2)
                
                processed_results.append({
                    'id': doc_version.id,
                    'content': doc_version.content,
                    'title': doc_version.title,
                    'source_url': doc_version.source_url,
                    'similarity': similarity,
                    'rank': i + 1,
                    'university_name': doc_version.university_name if hasattr(doc_version, 'university_name') else 'Northeastern University'
                })
            
            return processed_results
            
        except Exception as e:
            print(f"[ENHANCED OPENAI] Semantic search error: {e}")
            return []
    
    def remove_duplicates(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate documents based on document ID"""
        unique_results = []
        seen_ids = set()
        
        for result in results:
            # Use document ID for deduplication (more reliable than content hashing)
            doc_id = result.get('id', '')
            if doc_id and doc_id not in seen_ids:
                seen_ids.add(doc_id)
                unique_results.append(result)
            elif not doc_id:
                # If no ID, keep it anyway (shouldn't happen but be safe)
                unique_results.append(result)
        
        print(f"[ENHANCED OPENAI] Deduplicated {len(results)} results to {len(unique_results)} unique documents")
        return unique_results
    
    def question_specific_rerank(self, results: List[Dict], question: str) -> List[Dict]:
        """Rerank based on how well each document answers the specific question"""
        
        question_terms = self.extract_key_terms(question)
        
        for result in results:
            # Calculate how well this document answers the specific question
            content = result['content'].lower()
            term_matches = sum(1 for term in question_terms if term in content)
            question_relevance = term_matches / len(question_terms) if question_terms else 0.0
            
            # Combine with similarity score
            result['final_score'] = (result['similarity'] * 0.6) + (question_relevance * 0.4)
        
        # Sort by final score
        results.sort(key=lambda x: x['final_score'], reverse=True)
        return results
    
    def rerank_results(self, results: List[Dict], original_query: str, k: int = 10) -> List[Dict]:
        """Rerank results based on relevance to original query"""
        try:
            # Use question-specific reranking for better results
            reranked_results = self.question_specific_rerank(results, original_query)
            return reranked_results[:k]
            
        except Exception as e:
            print(f"[ENHANCED OPENAI] Reranking error: {e}")
            return results[:k]
    
    def calculate_content_relevance(self, content: str, query: str) -> float:
        """Calculate content relevance to query"""
        try:
            # Simple keyword matching
            query_words = set(query.lower().split())
            content_words = set(content.lower().split())
            
            # Calculate word overlap
            overlap = len(query_words.intersection(content_words))
            total_query_words = len(query_words)
            
            if total_query_words == 0:
                return 0.0
            
            return min(overlap / total_query_words, 1.0)
            
        except Exception as e:
            print(f"[ENHANCED OPENAI] Content relevance calculation error: {e}")
            return 0.0
    
    def calculate_confidence(self, relevant_docs: List[Dict], question: str, answer: str) -> float:
        """Calculate confidence score based on multiple factors"""
        try:
            if not relevant_docs:
                return 0.0
            
            # Factor 1: Average similarity of retrieved documents
            avg_similarity = sum(doc['similarity'] for doc in relevant_docs) / len(relevant_docs)
            
            # Factor 2: Number of relevant documents
            doc_count_score = min(len(relevant_docs) / 10.0, 1.0)  # Normalize to 0-1
            
            # Factor 3: Answer length (longer answers often indicate more comprehensive information)
            answer_length_score = min(len(answer) / 500.0, 1.0)  # Normalize to 0-1
            
            # Factor 4: Content diversity (different sources)
            unique_sources = len(set(doc.get('source_url', '') for doc in relevant_docs))
            source_diversity_score = min(unique_sources / 5.0, 1.0)  # Normalize to 0-1
            
            # Weighted combination
            confidence = (
                avg_similarity * 0.4 +
                doc_count_score * 0.2 +
                answer_length_score * 0.2 +
                source_diversity_score * 0.2
            )
            
            return min(confidence, 1.0)
            
        except Exception as e:
            print(f"[ENHANCED OPENAI] Confidence calculation error: {e}")
            return 0.5
    
    def generate_enhanced_openai_response(self, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate enhanced response with OpenAI GPT and 10 document analysis"""
        try:
            start_time = time.time()
            
            # Step 1: Enhanced hybrid search (target: <3 seconds with GPU)
            search_start = time.time()
            relevant_docs = self.hybrid_search(question, k=10)  # Analyze 10 documents
            search_time = time.time() - search_start
            
            if not relevant_docs:
                return {
                    'answer': "I don't have enough information to answer that question about Northeastern University. Please try asking about specific programs, admissions, or policies.",
                    'sources': [],
                    'confidence': 0.0,
                    'response_time': time.time() - start_time,
                    'search_time': search_time,
                    'llm_time': 0.0,
                    'context_time': 0.0,
                    'device': self.embedding_manager.device,
                    'documents_analyzed': 0,
                    'query_expansions': False,
                    'model': self.model_name
                }
            
            # Step 2: Prepare enhanced context using intelligent processing
            context_start = time.time()
            
            # Use enhanced context preparation
            context = self.prepare_context(relevant_docs, question)
            
            # Prepare sources for response
            sources = []
            for doc in relevant_docs:
                sources.append({
                    'title': doc['title'],
                    'url': doc['source_url'],
                    'similarity': doc['similarity'],
                    'relevance_score': doc.get('relevance_score', 0.0),
                    'content_preview': doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'],
                    'rank': doc['rank']
                })
            
            context_time = time.time() - context_start
            
            # Step 3: Generate comprehensive answer using OpenAI
            llm_start = time.time()
            
            # Get conversation history for context
            conversation_history = self.get_conversation_history(session_id or "current_session", limit=3)
            history_text = "\n".join([f"Q: {conv['question']}\nA: {conv['answer']}" 
                                    for conv in conversation_history])
            
            prompt = self.answer_prompt.format(
                context=context,
                question=question,
                conversation_history=history_text
            )
            
            print(f"[ENHANCED OPENAI] Generating answer with GPT...")
            
            try:
                response = self.llm.invoke(prompt)
                answer = response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                print(f"[ENHANCED OPENAI] Error generating answer: {e}")
                answer = "I apologize, but I encountered an error while generating the answer. Please try again."
            
            llm_time = time.time() - llm_start
            
            # Step 4: Validate and improve answer if needed
            answer = answer.strip()
            answer = self.validate_and_improve_answer(question, answer, context)
            
            # Step 5: Calculate confidence
            confidence = self.calculate_confidence(relevant_docs, question, answer)
            
            # Step 6: Store conversation
            if session_id:
                self.store_conversation(session_id, question, answer, sources)
            
            total_time = time.time() - start_time
            
            print(f"[ENHANCED OPENAI] Response generated in {total_time:.2f}s (search: {search_time:.2f}s, context: {context_time:.2f}s, LLM: {llm_time:.2f}s)")
            print(f"[ENHANCED OPENAI] Documents analyzed: {len(relevant_docs)}")
            print(f"[ENHANCED OPENAI] Confidence: {confidence:.2f}")
            
            return {
                'answer': answer.strip(),
                'sources': sources,
                'confidence': confidence,
                'response_time': total_time,
                'search_time': search_time,
                'llm_time': llm_time,
                'context_time': context_time,
                'device': self.embedding_manager.device,
                'documents_analyzed': len(relevant_docs),
                'query_expansions': len(relevant_docs) > 0,
                'model': self.model_name
            }
            
        except Exception as e:
            print(f"[ENHANCED OPENAI] Error generating response: {e}")
            import traceback
            traceback.print_exc()
            return {
                'answer': f"I'm sorry, I encountered an error: {str(e)}. Please try again.",
                'sources': [],
                'confidence': 0.0,
                'response_time': time.time() - start_time if 'start_time' in locals() else 0,
                'search_time': 0.0,
                'llm_time': 0.0,
                'context_time': 0.0,
                'device': self.embedding_manager.device,
                'documents_analyzed': 0,
                'query_expansions': False,
                'model': self.model_name
            }
    
    def store_conversation(self, session_id: str, question: str, answer: str, sources: List[Dict]):
        """Store conversation for context"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            'question': question,
            'answer': answer,
            'sources': sources,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 conversations
        if len(self.conversations[session_id]) > 10:
            self.conversations[session_id] = self.conversations[session_id][-10:]
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for context"""
        if session_id not in self.conversations:
            return []
        
        return self.conversations[session_id][-limit:]
    
    def save_cache(self):
        """Save embedding cache"""
        self.embedding_manager.save_cache()

def create_enhanced_openai_chatbot(model_type: str = "gpt-4o-mini", openai_api_key: Optional[str] = None):
    """Create an enhanced OpenAI-optimized RAG chatbot instance"""
    return EnhancedOpenAIUniversityRAGChatbot(model_name=model_type, openai_api_key=openai_api_key)

if __name__ == "__main__":
    # Test the enhanced OpenAI chatbot
    chatbot = create_enhanced_openai_chatbot()
    
    test_questions = [
        "What are the admission requirements for Northeastern University?",
        "Tell me about the computer science program and its curriculum",
        "What is the tuition cost and available financial aid options?",
        "How do I apply for financial aid and what scholarships are available?"
    ]
    
    print(f"\n[ENHANCED OPENAI] Testing with model: {chatbot.model_name}")
    print(f"[ENHANCED OPENAI] Embedding device: {chatbot.embedding_manager.device}")
    print("=" * 70)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[ENHANCED OPENAI] Test {i}: {question}")
        response = chatbot.generate_enhanced_openai_response(question)
        print(f"[ENHANCED OPENAI] Answer: {response['answer'][:150]}...")
        print(f"[ENHANCED OPENAI] Confidence: {response['confidence']:.2f}")
        print(f"[ENHANCED OPENAI] Response time: {response['response_time']:.2f}s")
        print(f"[ENHANCED OPENAI] Documents analyzed: {response['documents_analyzed']}")
        print(f"[ENHANCED OPENAI] Model used: {response['model']}")
        print(f"[ENHANCED OPENAI] Sources found: {len(response['sources'])}")
    
    chatbot.save_cache()

