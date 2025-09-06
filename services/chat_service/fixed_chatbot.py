"""
Fixed Northeastern University Chatbot with ChatGPT Integration
- Uses OpenAI ChatGPT API instead of Ollama
- Properly handles URLs from scraped content
- Works with both ChromaDB and Pinecone
- Enhanced error handling and fallbacks
"""

import os
import sys
import time
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database functions
from services.shared.database import (
    get_database_type, get_collection, add_documents_to_pinecone, 
    query_pinecone, get_pinecone_count
)

# Import OpenAI
try:
    from openai import OpenAI
    from langchain_openai import ChatOpenAI
    from langchain.prompts import PromptTemplate
    OPENAI_AVAILABLE = True
except ImportError:
    print("⚠️  OpenAI not installed. Install with: pip install openai langchain-openai")
    OPENAI_AVAILABLE = False

# Import embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    print("⚠️  SentenceTransformers not installed")
    EMBEDDINGS_AVAILABLE = False

class FixedUniversityChatbot:
    def __init__(self):
        """Initialize the fixed chatbot with ChatGPT integration"""
        print("🤖 Initializing Fixed Northeastern University Chatbot...")
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Initialize OpenAI client
        self.openai_client = None
        self.llm = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key != "your_openai_api_key_here":
                try:
                    self.openai_client = OpenAI(api_key=api_key)
                    self.llm = ChatOpenAI(
                        model="gpt-3.5-turbo",
                        temperature=0.1,
                        openai_api_key=api_key
                    )
                    print("✅ ChatGPT API initialized successfully")
                except Exception as e:
                    print(f"❌ Failed to initialize ChatGPT: {e}")
                    self.openai_client = None
                    self.llm = None
            else:
                print("⚠️  OpenAI API key not found in .env file")
        
        # Initialize embeddings
        self.embedding_model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Embeddings model loaded")
            except Exception as e:
                print(f"❌ Failed to load embeddings: {e}")
        
        # Database configuration
        self.db_type = get_database_type()
        print(f"📊 Using database: {self.db_type}")
        
        # Test database connection
        try:
            if self.db_type == "pinecone":
                # Test Pinecone connection
                from services.shared.database import get_pinecone_index
                index = get_pinecone_index()
                print("✅ Pinecone connection successful")
            else:
                # Test ChromaDB connection
                from services.shared.database import get_collection
                collection = get_collection("documents")
                print("✅ ChromaDB connection successful")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            # Fallback to ChromaDB
            if self.db_type == "pinecone":
                print("🔄 Falling back to ChromaDB...")
                self.db_type = "chromadb_local"
                # Update the global database type
                import services.shared.database as db_module
                db_module.database_type = "chromadb_local"
        
        # Configuration
        self.max_documents = 10
        self.confidence_threshold = 0.3
        
        print("✅ Fixed chatbot initialized successfully!")
    
    def search_documents(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search for relevant documents using the appropriate database"""
        # Use the current database type (may have been updated during initialization)
        current_db_type = get_database_type()
        
        if current_db_type == "pinecone":
            # Try Pinecone first
            documents = self._search_pinecone(query, n_results)
            # If Pinecone fails or returns no results, fall back to ChromaDB
            if not documents:
                print("🔄 Pinecone returned no results, falling back to ChromaDB...")
                documents = self._search_chromadb(query, n_results)
            return documents
        else:
            return self._search_chromadb(query, n_results)
    
    def _search_pinecone(self, query: str, n_results: int) -> List[Dict[str, Any]]:
        """Search Pinecone database"""
        try:
            results = query_pinecone(query, n_results=n_results, collection_name="documents")
            
            if not results or not results.get('ids'):
                print("⚠️  Pinecone returned empty results")
                return []
            
            documents = []
            for i in range(len(results.get('ids', []))):
                doc = {
                    'id': results['ids'][i],
                    'content': results['documents'][i] if i < len(results.get('documents', [])) else '',
                    'metadata': results['metadatas'][i] if i < len(results.get('metadatas', [])) else {},
                    'score': results['distances'][i] if i < len(results.get('distances', [])) else 1.0
                }
                documents.append(doc)
            
            print(f"✅ Pinecone returned {len(documents)} documents")
            return documents
        except Exception as e:
            print(f"❌ Pinecone search error: {e}")
            return []
    
    def _search_chromadb(self, query: str, n_results: int) -> List[Dict[str, Any]]:
        """Search ChromaDB database"""
        try:
            collection = get_collection("documents")
            
            # Generate query embedding if available
            if self.embedding_model:
                query_embedding = self.embedding_model.encode([query])[0].tolist()
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    include=['documents', 'metadatas', 'distances']
                )
            else:
                # Fallback to text search
                results = collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    include=['documents', 'metadatas', 'distances']
                )
            
            documents = []
            if results and results.get('ids') and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    doc = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i] if results.get('documents') and results['documents'][0] else '',
                        'metadata': results['metadatas'][0][i] if results.get('metadatas') and results['metadatas'][0] else {},
                        'score': results['distances'][0][i] if results.get('distances') and results['distances'][0] else 0.0
                    }
                    documents.append(doc)
            
            print(f"✅ ChromaDB returned {len(documents)} documents")
            return documents
        except Exception as e:
            print(f"❌ ChromaDB search error: {e}")
            return []
    
    def generate_answer(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Generate answer using ChatGPT or fallback method"""
        if not documents:
            return "I don't have enough information in my knowledge base to answer that question. Please try asking about specific Northeastern University programs, admissions, courses, or academic policies."
        
        # Prepare context from documents
        context_parts = []
        for doc in documents[:5]:  # Use top 5 documents
            title = doc.get('metadata', {}).get('title', 'Document')
            content = doc['content']
            url = doc.get('metadata', {}).get('source_url', '')
            
            # Create context entry
            context_entry = f"Title: {title}"
            if url:
                context_entry += f"\nURL: {url}"
            context_entry += f"\nContent: {content[:500]}..."
            context_parts.append(context_entry)
        
        context = "\n\n".join(context_parts)
        
        # Use ChatGPT if available
        if self.llm and self.openai_client:
            try:
                prompt = f"""You are a helpful Northeastern University assistant. Use the provided context to answer the student's question accurately and concisely.

Context from university documents:
{context}

Student Question: {query}

Instructions:
- Answer based only on the provided context
- If the context doesn't contain enough information, say "I don't have enough information to answer that question completely"
- Be helpful and direct
- Include relevant details like requirements, deadlines, or contact information when available
- If you mention specific URLs from the context, make sure they are accurate

Answer:"""
                
                response = self.llm.invoke(prompt)
                return response.content if hasattr(response, 'content') else str(response)
                
            except Exception as e:
                print(f"❌ ChatGPT error: {e}")
                return self._generate_fallback_answer(query, documents)
        else:
            return self._generate_fallback_answer(query, documents)
    
    def _generate_fallback_answer(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Generate fallback answer when ChatGPT is not available"""
        if not documents:
            return "I don't have enough information to answer that question."
        
        # Extract key information based on query
        query_lower = query.lower()
        relevant_info = []
        
        for doc in documents[:3]:
            title = doc.get('metadata', {}).get('title', '')
            content = doc['content']
            url = doc.get('metadata', {}).get('source_url', '')
            
            # Check if document is relevant to query
            if any(term in query_lower for term in ['admission', 'apply', 'requirement']):
                if 'admission' in title.lower() or 'admission' in content.lower():
                    relevant_info.append(f"Based on {title}: Northeastern University has specific admission requirements and application processes.")
            elif any(term in query_lower for term in ['co-op', 'coop', 'internship']):
                if 'co-op' in title.lower() or 'coop' in title.lower():
                    relevant_info.append(f"Based on {title}: Northeastern University's co-op program provides real-world experience through paid internships.")
            elif any(term in query_lower for term in ['tuition', 'cost', 'financial', 'fee']):
                if any(word in title.lower() for word in ['tuition', 'cost', 'financial']):
                    relevant_info.append(f"Based on {title}: Northeastern University offers various tuition and financial aid options.")
            elif any(term in query_lower for term in ['housing', 'campus', 'residence']):
                if any(word in title.lower() for word in ['housing', 'campus', 'residence']):
                    relevant_info.append(f"Based on {title}: Northeastern University provides on-campus housing and residence options.")
            else:
                # General information
                if title:
                    relevant_info.append(f"Based on {title}: This document contains relevant information about your question.")
        
        if relevant_info:
            return " ".join(relevant_info[:2])  # Use up to 2 relevant pieces of info
        else:
            # Fallback to document titles
            titles = [doc.get('metadata', {}).get('title', '') for doc in documents[:2]]
            return f"Based on the available information: I found relevant documents including {', '.join(titles)}. These contain information related to your question about Northeastern University."
    
    def prepare_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare source information with proper URLs"""
        sources = []
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            title = metadata.get('title', 'Document')
            url = metadata.get('source_url', '') or metadata.get('url', '')
            
            # Ensure URL is properly formatted
            if url and not url.startswith('http'):
                url = 'https://' + url.lstrip('/')
            
            # Calculate relevance score
            score = doc.get('score', 0.0)
            if score <= 1.0:  # Cosine similarity
                relevance = (1.0 - score) * 100
            else:  # Distance
                relevance = max(0, 100 - (score * 100))
            
            source = {
                'title': title,
                'url': url,
                'relevance': f"{relevance:.1f}%",
                'content': doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
            }
            sources.append(source)
        
        return sources
    
    def chat(self, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Main chat method"""
        start_time = time.time()
        
        # Generate session ID if not provided
        if not session_id:
            session_id = f"session_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}"
        
        print(f"🤖 Processing question: {question[:50]}...")
        
        # Search for relevant documents
        documents = self.search_documents(question, self.max_documents)
        
        if not documents:
            return {
                'answer': "I don't have enough information in my knowledge base to answer that question. Please try asking about specific Northeastern University programs, admissions, courses, or academic policies.",
                'sources': [],
                'confidence': 0.0,
                'session_id': session_id,
                'response_time': time.time() - start_time,
                'documents_analyzed': 0
            }
        
        # Generate answer
        answer = self.generate_answer(question, documents)
        
        # Prepare sources
        sources = self.prepare_sources(documents)
        
        # Calculate confidence
        scores = [doc.get('score', 0.0) for doc in documents]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        confidence = max(0.0, min(1.0, 1.0 - avg_score)) if avg_score <= 1.0 else 0.0
        
        response_time = time.time() - start_time
        
        print(f"✅ Response generated in {response_time:.2f}s with {len(documents)} documents")
        
        return {
            'answer': answer,
            'sources': sources,
            'confidence': confidence,
            'session_id': session_id,
            'response_time': response_time,
            'documents_analyzed': len(documents)
        }

# Create global instance
chatbot = FixedUniversityChatbot()
