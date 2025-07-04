from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import sys
import os
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import config
from shared.chroma_service import ChromaService

class UniversityRAGChatbot:
    def __init__(self, model_name: str = "llama2:7b"):
        # Initialize ChromaDB service
        self.chroma_service = ChromaService()
        
        # Initialize local embeddings (no API key needed)
        print("Loading local embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}  # Use 'cuda' if you have GPU
        )
        
        # Initialize local LLM with Ollama
        print(f"Loading local LLM: {model_name}")
        self.llm = Ollama(
            model=model_name,
            temperature=0.7
        )
        
        # Test if model is available
        try:
            test_response = self.llm("Hello")
            print(f"[OK] Local LLM {model_name} is working!")
        except Exception as e:
            print(f"[ERROR] Error with local LLM: {e}")
            print(f"Make sure to run: ollama pull {model_name}")
            raise
        
        # Create custom prompt template for university context
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful university information assistant. Use the provided context to answer the student's question accurately and concisely.

Context from university documents:
{context}

Student Question: {question}

Instructions:
- Answer based only on the provided context
- If the context doesn't contain enough information, say "I don't have enough information to answer that question completely"
- Be helpful and direct
- Include relevant details like requirements, deadlines, or contact information when available

Answer:"""
        )
    
    def search_similar_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity"""
        try:
            # Generate embedding for the query using local model
            query_embedding = self.embeddings.embed_query(query)
            
            # Search for similar documents using ChromaDB
            results = self.chroma_service.search_documents(
                query=query,
                embedding=query_embedding,
                n_results=k
            )
            
            documents = []
            for doc, distance in results:
                # Convert distance to similarity (ChromaDB returns distance, we want similarity)
                similarity = 1.0 - distance
                documents.append({
                    'id': doc.id,
                    'title': doc.title,
                    'content': doc.content,
                    'source_url': doc.source_url,
                    'metadata': doc.extra_data,
                    'similarity': similarity
                })
            
            return documents
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def generate_response(self, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a response to a user question using local LLM"""
        try:
            # Search for relevant documents
            relevant_docs = self.search_similar_documents(question, k=3)
            
            if not relevant_docs:
                return {
                    'answer': "I don't have enough information in my knowledge base to answer that question. Please try asking about specific university programs, admissions, courses, or academic policies.",
                    'sources': [],
                    'confidence': 0.0
                }
            
            # Prepare context from relevant documents
            context_parts = []
            sources = []
            
            for doc in relevant_docs:
                # Limit context length to prevent overwhelming the model
                content_preview = doc['content'][:800] + "..." if len(doc['content']) > 800 else doc['content']
                context_parts.append(f"Document: {doc['title']}\nContent: {content_preview}")
                sources.append({
                    'title': doc['title'],
                    'url': doc['source_url'],
                    'similarity': doc['similarity']
                })
            
            context = "\n\n".join(context_parts)
            
            # Generate answer using local LLM
            prompt = self.prompt_template.format(context=context, question=question)
            
            print(f"Generating response for: {question[:50]}...")
            answer = self.llm(prompt)
            
            # Calculate confidence based on similarity scores
            avg_similarity = sum(doc['similarity'] for doc in relevant_docs) / len(relevant_docs)
            confidence = min(avg_similarity * 1.2, 1.0)  # Boost confidence slightly
            
            # Store conversation if session_id provided
            if session_id:
                self.store_conversation(session_id, question, answer, sources)
            
            return {
                'answer': answer.strip(),
                'sources': sources,
                'confidence': confidence
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                'answer': "I'm sorry, I encountered an error while processing your question. Please try rephrasing your question or try again in a moment.",
                'sources': [],
                'confidence': 0.0
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
            
            # Store assistant message
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

def create_chatbot(model_type: str = "llama2"):
    """Factory function to create chatbot with specified model"""
    model_name = f"{model_type}:7b" if ":" not in model_type else model_type
    return UniversityRAGChatbot(model_name=model_name)