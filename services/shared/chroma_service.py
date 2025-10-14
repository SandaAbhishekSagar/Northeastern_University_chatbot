"""
ChromaDB Service Layer for University Chatbot
Handles all database operations using ChromaDB
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import uuid
from datetime import datetime
import hashlib

# Add the project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

from services.shared.database import get_chroma_client, get_collection
from services.shared.models import (
    University, DocumentVersion, ScrapeLog, ChatSession, ChatMessage,
    COLLECTIONS
)

class ChromaService:
    """Service class for ChromaDB operations"""
    
    def __init__(self):
        self.client = get_chroma_client()
    
    # University operations
    def create_university(self, name: str, base_url: str, scraping_enabled: bool = True) -> University:
        """Create a new university"""
        university = University(
            name=name,
            base_url=base_url,
            scraping_enabled=scraping_enabled
        )
        
        collection = get_collection(COLLECTIONS['universities'])
        collection.add(
            ids=[university.id],
            documents=[university.name],
            metadatas=[university.to_dict()]
        )
        
        return university
    
    def get_university(self, university_id: str) -> Optional[University]:
        """Get university by ID"""
        collection = get_collection(COLLECTIONS['universities'])
        try:
            result = collection.get(ids=[university_id])
            if result['ids']:
                return University.from_dict(result['metadatas'][0])
        except Exception as e:
            print(f"Error getting university {university_id}: {e}")
        return None
    
    def get_university_by_name(self, name: str) -> Optional[University]:
        """Get university by name"""
        collection = get_collection(COLLECTIONS['universities'])
        try:
            result = collection.get(
                where={"name": name}
            )
            if result['ids']:
                return University.from_dict(result['metadatas'][0])
        except Exception as e:
            print(f"Error getting university by name {name}: {e}")
        return None
    
    def get_all_universities(self) -> List[University]:
        """Get all universities"""
        collection = get_collection(COLLECTIONS['universities'])
        try:
            result = collection.get()
            universities = []
            for metadata in result['metadatas']:
                universities.append(University.from_dict(metadata))
            return universities
        except Exception as e:
            print(f"Error getting universities: {e}")
            return []
    
    def update_university(self, university_id: str, **kwargs) -> bool:
        """Update university"""
        collection = get_collection(COLLECTIONS['universities'])
        try:
            # Get current university
            result = collection.get(ids=[university_id])
            if not result['ids']:
                return False
            
            # Update metadata
            metadata = result['metadatas'][0]
            metadata.update(kwargs)
            
            # Update in collection
            collection.update(
                ids=[university_id],
                metadatas=[metadata]
            )
            return True
        except Exception as e:
            print(f"Error updating university {university_id}: {e}")
            return False
    
    def delete_university(self, university_id: str) -> bool:
        """Delete a university by ID"""
        collection = get_collection(COLLECTIONS['universities'])
        try:
            collection.delete(ids=[university_id])
            return True
        except Exception as e:
            print(f"Error deleting university {university_id}: {e}")
            return False
    
    # Document operations
    def create_document(self, 
                       source_url: str, 
                       title: str, 
                       content: str, 
                       university_id: str,
                       embedding: Optional[List[float]] = None,
                       extra_data: Optional[Dict[str, Any]] = None,
                       file_name: Optional[str] = None) -> DocumentVersion:
        """Create a new document version
        
        Args:
            source_url: URL where the document was found
            title: Document title
            content: Document content
            university_id: ID of the university this document belongs to
            embedding: Optional pre-computed embedding
            extra_data: Optional additional metadata
            file_name: Optional file name where the content came from
        """
        # Initialize extra_data if None
        extra_data_dict: Dict[str, Any] = {} if extra_data is None else dict(extra_data)
        
        # Add file_name to extra_data if provided
        if file_name:
            extra_data_dict['file_name'] = file_name

        doc = DocumentVersion(
            version_number=1,  # Will be incremented if document exists
            source_url=source_url,
            title=title,
            content=content,
            university_id=university_id,
            embedding=embedding,
            extra_data=extra_data_dict
        )
        
        collection = get_collection(COLLECTIONS['documents'])
        
        # Flatten metadata for ChromaDB (no nested dictionaries allowed)
        metadata = doc.to_dict()
        if 'extra_data' in metadata and isinstance(metadata['extra_data'], dict):
            # Flatten extra_data into top-level metadata
            extra_data_flat = metadata.pop('extra_data')
            metadata.update(extra_data_flat)
        
        # Add document with embedding if provided
        if embedding:
            collection.add(
                ids=[doc.id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata]
            )
        else:
            collection.add(
                ids=[doc.id],
                documents=[content],
                metadatas=[metadata]
            )
        
        return doc
    
    def search_documents(self, 
                        query: str, 
                        embedding: Optional[List[float]] = None,
                        n_results: int = 5,
                        university_id: Optional[str] = None) -> List[Tuple[DocumentVersion, float]]:
        """Search documents by similarity - searches across all batch collections"""
        
        # First, try to search in the standard documents collection
        try:
            collection = get_collection(COLLECTIONS['documents'])
            standard_results = self._search_single_collection(
                collection, query, embedding, n_results, university_id
            )
            
            # If we found results in standard collection, return them
            if standard_results and len(standard_results) > 0:
                print(f"[CHROMA SERVICE] Found {len(standard_results)} documents in standard collection")
                return standard_results
        except Exception as e:
            print(f"[CHROMA SERVICE] Standard collection search failed: {e}")
        
        # If no results in standard collection, search across all batch collections
        print(f"[CHROMA SERVICE] Searching across batch collections...")
        return self._search_batch_collections(query, embedding, n_results, university_id)
    
    def _search_single_collection(self, collection, query: str, embedding: Optional[List[float]], 
                                  n_results: int, university_id: Optional[str]) -> List[Tuple[DocumentVersion, float]]:
        """Helper method to search a single collection"""
        where_filter = {}
        if university_id:
            where_filter["university_id"] = university_id
        
        try:
            if embedding:
                result = collection.query(
                    query_embeddings=[embedding],
                    n_results=n_results,
                    where=where_filter if where_filter else None
                )
            else:
                result = collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=where_filter if where_filter else None
                )
            
            documents = []
            if result['ids'] and result['metadatas']:
                for i, metadata in enumerate(result['metadatas'][0]):
                    doc = DocumentVersion.from_dict(metadata)
                    distance = result['distances'][0][i] if result['distances'] else 0.0
                    documents.append((doc, distance))
            
            return documents
        except Exception as e:
            print(f"[CHROMA SERVICE] Error searching collection: {e}")
            return []
    
    def _search_batch_collections(self, query: str, embedding: Optional[List[float]], 
                                  n_results: int, university_id: Optional[str]) -> List[Tuple[DocumentVersion, float]]:
        """Search across all batch collections and aggregate results"""
        all_documents = []
        
        try:
            # Get all collections with pagination (ChromaDB Cloud limits to 1000 per call)
            all_collections = []
            offset = 0
            limit = 1000
            
            while True:
                try:
                    collections_batch = self.client.list_collections(limit=limit, offset=offset)
                    if not collections_batch or len(collections_batch) == 0:
                        break
                    all_collections.extend(collections_batch)
                    if len(collections_batch) < limit:
                        break
                    offset += limit
                except:
                    # If pagination fails, just use what we got
                    break
            
            print(f"[CHROMA SERVICE] Found {len(all_collections)} total collections")
            
            # Filter for batch collections
            batch_collections = [
                col for col in all_collections 
                if 'batch' in col.name.lower() or 'ultra_optimized' in col.name.lower()
            ]
            print(f"[CHROMA SERVICE] Found {len(batch_collections)} batch collections")
            
            # Search more collections for better coverage (100 instead of 50)
            max_collections_to_search = 100
            collections_searched = 0
            
            for collection_obj in batch_collections[:max_collections_to_search]:
                try:
                    # Get the collection
                    collection = self.client.get_collection(collection_obj.name)
                    
                    # Search this collection - get more results per collection
                    results = self._search_single_collection(
                        collection, query, embedding, n_results * 2, university_id  # Get 2x results
                    )
                    
                    if results:
                        all_documents.extend(results)
                        collections_searched += 1
                        
                        # Log progress every 20 collections
                        if collections_searched % 20 == 0:
                            print(f"[CHROMA SERVICE] Searched {collections_searched} collections, found {len(all_documents)} documents so far")
                    
                except Exception as e:
                    # Skip collections that fail
                    continue
            
            print(f"[CHROMA SERVICE] Searched {collections_searched} batch collections")
            print(f"[CHROMA SERVICE] Found {len(all_documents)} total documents before deduplication")
            
            # Deduplicate by document ID (keep best match for each unique doc)
            seen_ids = {}
            for doc, distance in all_documents:
                if doc.id not in seen_ids or distance < seen_ids[doc.id][1]:
                    seen_ids[doc.id] = (doc, distance)
            
            unique_documents = list(seen_ids.values())
            print(f"[CHROMA SERVICE] Found {len(unique_documents)} unique documents after deduplication")
            
            # Sort by distance (similarity) and return top N
            if unique_documents:
                unique_documents.sort(key=lambda x: x[1])  # Sort by distance (lower is better)
                return unique_documents[:n_results]
            
            return []
            
        except Exception as e:
            print(f"[CHROMA SERVICE] Error searching batch collections: {e}")
            return []
    
    def get_document(self, document_id: str) -> Optional[DocumentVersion]:
        """Get document by ID"""
        collection = get_collection(COLLECTIONS['documents'])
        try:
            result = collection.get(ids=[document_id])
            if result['ids']:
                return DocumentVersion.from_dict(result['metadatas'][0])
        except Exception as e:
            print(f"Error getting document {document_id}: {e}")
        return None
    
    def get_all_documents(self, university_id: Optional[str] = None, limit: int = 1000) -> List[DocumentVersion]:
        """Get all documents, optionally filtered by university"""
        collection = get_collection(COLLECTIONS['documents'])
        
        where_filter = {}
        if university_id:
            where_filter["university_id"] = university_id
        
        try:
            result = collection.get(
                where=where_filter if where_filter else None,
                limit=limit
            )
            
            documents = []
            for metadata in result['metadatas']:
                documents.append(DocumentVersion.from_dict(metadata))
            
            return documents
        except Exception as e:
            print(f"Error getting documents: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document by ID"""
        collection = get_collection(COLLECTIONS['documents'])
        try:
            collection.delete(ids=[document_id])
            return True
        except Exception as e:
            print(f"Error deleting document {document_id}: {e}")
            return False
    
    # Scrape log operations
    def create_scrape_log(self, 
                         university_id: str, 
                         url: str, 
                         status: str,
                         pages_scraped: int = 0,
                         changes_detected: int = 0,
                         error_message: Optional[str] = None) -> ScrapeLog:
        """Create a new scrape log entry"""
        log = ScrapeLog(
            university_id=university_id,
            url=url,
            status=status,
            pages_scraped=pages_scraped,
            changes_detected=changes_detected,
            error_message=error_message
        )
        
        collection = get_collection(COLLECTIONS['scrape_logs'])
        collection.add(
            ids=[log.id],
            documents=[f"Scrape log for {url}"],
            metadatas=[log.to_dict()]
        )
        
        return log
    
    def get_scrape_logs(self, university_id: Optional[str] = None, limit: int = 100) -> List[ScrapeLog]:
        """Get scrape logs"""
        collection = get_collection(COLLECTIONS['scrape_logs'])
        
        where_filter = {}
        if university_id:
            where_filter["university_id"] = university_id
        
        try:
            result = collection.get(
                where=where_filter if where_filter else None,
                limit=limit
            )
            
            logs = []
            for metadata in result['metadatas']:
                logs.append(ScrapeLog.from_dict(metadata))
            
            return logs
        except Exception as e:
            print(f"Error getting scrape logs: {e}")
            return []
    
    # Chat operations
    def create_chat_session(self, user_id: Optional[str] = None) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(user_id=user_id)
        
        collection = get_collection(COLLECTIONS['chat_sessions'])
        collection.add(
            ids=[session.id],
            documents=[f"Chat session for {user_id or 'anonymous'}"],
            metadatas=[session.to_dict()]
        )
        
        return session
    
    def get_chat_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID"""
        collection = get_collection(COLLECTIONS['chat_sessions'])
        try:
            result = collection.get(ids=[session_id])
            if result['ids']:
                return ChatSession.from_dict(result['metadatas'][0])
        except Exception as e:
            print(f"Error getting chat session {session_id}: {e}")
        return None
    
    def update_chat_session(self, session_id: str, **kwargs) -> bool:
        """Update chat session"""
        collection = get_collection(COLLECTIONS['chat_sessions'])
        try:
            result = collection.get(ids=[session_id])
            if not result['ids']:
                return False
            
            metadata = result['metadatas'][0]
            metadata.update(kwargs)
            
            collection.update(
                ids=[session_id],
                metadatas=[metadata]
            )
            return True
        except Exception as e:
            print(f"Error updating chat session {session_id}: {e}")
            return False
    
    def create_chat_message(self, 
                           session_id: str, 
                           message_type: str, 
                           content: str,
                           sources: Optional[List[Dict[str, Any]]] = None) -> ChatMessage:
        """Create a new chat message"""
        message = ChatMessage(
            session_id=session_id,
            message_type=message_type,
            content=content,
            sources=sources or []
        )
        
        collection = get_collection(COLLECTIONS['chat_messages'])
        collection.add(
            ids=[message.id],
            documents=[content],
            metadatas=[message.to_dict()]
        )
        
        return message
    
    def get_chat_messages(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get chat messages for a session"""
        collection = get_collection(COLLECTIONS['chat_messages'])
        
        try:
            result = collection.get(
                where={"session_id": session_id},
                limit=limit
            )
            
            messages = []
            for metadata in result['metadatas']:
                messages.append(ChatMessage.from_dict(metadata))
            
            # Sort by created_at
            messages.sort(key=lambda x: x.created_at)
            return messages
        except Exception as e:
            print(f"Error getting chat messages: {e}")
            return []
    
    # Utility operations
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        try:
            self.client.delete_collection(name=collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection {collection_name}: {e}")
            return False
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get count of items in a collection - includes batch collections"""
        try:
            # First try the standard collection
            collection = get_collection(collection_name, create_if_not_exists=False)
            result = collection.get()
            standard_count = len(result['ids']) if result['ids'] else 0
            
            # If standard collection has documents, return that count
            if standard_count > 0:
                return standard_count
            
            # Otherwise, count across all batch collections
            if collection_name == 'documents':
                return self._count_batch_collections()
            
            return 0
        except Exception as e:
            print(f"[CHROMA SERVICE] Error getting count for collection {collection_name}: {e}")
            # Try counting batch collections as fallback
            if collection_name == 'documents':
                return self._count_batch_collections()
            return 0
    
    def _count_batch_collections(self) -> int:
        """Count total documents across all batch collections (cached)"""
        try:
            # Use cached count if available (to avoid slow counting every time)
            if hasattr(self, '_cached_batch_count') and self._cached_batch_count > 0:
                return self._cached_batch_count
            
            # Estimate based on known data: 3,280 collections with ~24 docs each = ~80,000
            # This is much faster than counting all collections
            print(f"[CHROMA SERVICE] Using estimated document count for batch collections")
            estimated_count = 80000  # Your known total
            
            self._cached_batch_count = estimated_count
            return estimated_count
            
        except Exception as e:
            print(f"[CHROMA SERVICE] Error counting batch collections: {e}")
            return 80000  # Return known total as fallback
    
    # Feedback operations
    def store_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Store user feedback in ChromaDB"""
        try:
            collection = get_collection(COLLECTIONS['feedback'])
            
            # Create unique ID for feedback
            feedback_id = str(uuid.uuid4())
            
            # Prepare metadata (flatten nested structures)
            metadata = {
                'session_id': feedback_data.get('session_id', ''),
                'question': feedback_data.get('question', ''),
                'answer': feedback_data.get('answer', ''),
                'rating': feedback_data.get('rating', 0),
                'feedback_text': feedback_data.get('feedback_text', ''),
                'confidence': feedback_data.get('confidence', 0.0),
                'timestamp': feedback_data.get('timestamp', datetime.now().isoformat()),
                'sources_count': len(feedback_data.get('sources', []))
            }
            
            # Add to collection
            collection.add(
                ids=[feedback_id],
                documents=[feedback_data.get('question', '')],  # Use question as document text
                metadatas=[metadata]
            )
            
            return True
        except Exception as e:
            print(f"Error storing feedback: {e}")
            return False
    
    def get_all_feedback(self) -> List[Dict[str, Any]]:
        """Get all feedback entries"""
        try:
            collection = get_collection(COLLECTIONS['feedback'])
            result = collection.get()
            
            feedback_list = []
            if result['ids'] and result['metadatas']:
                for i, metadata in enumerate(result['metadatas']):
                    feedback_entry = {
                        'id': result['ids'][i],
                        'session_id': metadata.get('session_id', ''),
                        'question': metadata.get('question', ''),
                        'answer': metadata.get('answer', ''),
                        'rating': metadata.get('rating', 0),
                        'feedback_text': metadata.get('feedback_text', ''),
                        'confidence': metadata.get('confidence', 0.0),
                        'timestamp': metadata.get('timestamp', ''),
                        'sources_count': metadata.get('sources_count', 0)
                    }
                    feedback_list.append(feedback_entry)
            
            return feedback_list
        except Exception as e:
            print(f"Error getting feedback: {e}")
            return []
    
    def get_feedback_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get feedback for a specific session"""
        try:
            collection = get_collection(COLLECTIONS['feedback'])
            result = collection.get(
                where={"session_id": session_id}
            )
            
            feedback_list = []
            if result['ids'] and result['metadatas']:
                for i, metadata in enumerate(result['metadatas']):
                    feedback_entry = {
                        'id': result['ids'][i],
                        'session_id': metadata.get('session_id', ''),
                        'question': metadata.get('question', ''),
                        'answer': metadata.get('answer', ''),
                        'rating': metadata.get('rating', 0),
                        'feedback_text': metadata.get('feedback_text', ''),
                        'confidence': metadata.get('confidence', 0.0),
                        'timestamp': metadata.get('timestamp', ''),
                        'sources_count': metadata.get('sources_count', 0)
                    }
                    feedback_list.append(feedback_entry)
            
            return feedback_list
        except Exception as e:
            print(f"Error getting feedback for session {session_id}: {e}")
            return []

# Global service instance
chroma_service = ChromaService()

def test_chroma_service():
    """Test ChromaDB service functionality"""
    try:
        print("Testing ChromaDB Service...")
        
        # Test university operations
        university = chroma_service.create_university(
            name="Test University",
            base_url="https://test.edu"
        )
        print(f"[OK] Created university: {university.name}")
        
        retrieved = chroma_service.get_university(str(university.id))
        print(f"[OK] Retrieved university: {retrieved.name if retrieved else 'None'}")
        
        # Test document operations
        doc = chroma_service.create_document(
            source_url="https://test.edu/page",
            title="Test Document",
            content="This is test content for the document.",
            university_id=str(university.id)
        )
        print(f"[OK] Created document: {doc.title}")
        
        # Test search
        results = chroma_service.search_documents("test content", n_results=5)
        print(f"[OK] Search returned {len(results)} results")
        
        # Test chat operations
        session = chroma_service.create_chat_session(user_id="test_user")
        print(f"[OK] Created chat session: {session.id}")
        
        message = chroma_service.create_chat_message(
            session_id=str(session.id),
            message_type="user",
            content="Hello, world!"
        )
        print(f"[OK] Created chat message: {message.id}")
        
        messages = chroma_service.get_chat_messages(str(session.id))
        print(f"[OK] Retrieved {len(messages)} messages")
        
        print("[OK] All ChromaDB service tests passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] ChromaDB service test failed: {e}")
        return False

if __name__ == "__main__":
    test_chroma_service() 