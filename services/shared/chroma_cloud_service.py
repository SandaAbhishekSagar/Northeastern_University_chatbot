"""
Enhanced ChromaDB Service with Cloud Support
Handles both local and cloud ChromaDB operations
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import uuid
from datetime import datetime
import hashlib

# Add the project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from chromadb import CloudClient, PersistentClient
    from chromadb.config import Settings
except ImportError:
    print("❌ ChromaDB not installed. Please install with: pip install chromadb")
    sys.exit(1)

from services.shared.models import (
    University, DocumentVersion, ScrapeLog, ChatSession, ChatMessage,
    COLLECTIONS
)

class ChromaCloudService:
    """Enhanced service class for ChromaDB operations with cloud support"""
    
    def __init__(self, use_cloud: bool = False, cloud_database: str = "newtest"):
        """
        Initialize ChromaDB service
        
        Args:
            use_cloud: Whether to use Chroma Cloud (True) or local (False)
            cloud_database: Name of the cloud database to use
        """
        self.use_cloud = use_cloud
        self.cloud_database = cloud_database
        
        if use_cloud:
            self.client = self._get_cloud_client()
            print(f"🌐 Using Chroma Cloud database: {cloud_database}")
        else:
            self.client = self._get_local_client()
            print("💾 Using local ChromaDB")
    
    def _get_cloud_client(self) -> CloudClient:
        """Get Chroma Cloud client"""
        try:
            # Chroma Cloud Configuration
            api_key = 'ck-4RLZskGk7sxLbFNvMZCQY4xASn4WPReJ1W4CSf9tvhUW'
            tenant = '28757e4a-f042-4b0c-ad7c-9257cd36b130'
            
            return CloudClient(
                api_key=api_key,
                tenant=tenant,
                database=self.cloud_database
            )
        except Exception as e:
            print(f"❌ Failed to connect to Chroma Cloud: {e}")
            print("🔄 Falling back to local ChromaDB...")
            return self._get_local_client()
    
    def _get_local_client(self) -> PersistentClient:
        """Get local ChromaDB client"""
        chroma_data_path = project_root / "chroma_data"
        chroma_data_path.mkdir(exist_ok=True)
        
        return PersistentClient(
            path=str(chroma_data_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
    
    def get_collection(self, collection_name: str):
        """Get or create a collection"""
        try:
            return self.client.get_collection(collection_name)
        except Exception:
            # Collection doesn't exist, create it
            return self.client.create_collection(collection_name)
    
    def test_connection(self) -> bool:
        """Test the database connection"""
        try:
            collections = self.client.list_collections()
            print(f"✅ Connection successful! Found {len(collections)} collections")
            
            for collection in collections:
                count = collection.count()
                print(f"  📋 {collection.name}: {count} documents")
            
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get the number of documents in a collection"""
        try:
            collection = self.get_collection(collection_name)
            return collection.count()
        except Exception as e:
            print(f"❌ Error getting count for {collection_name}: {e}")
            return 0
    
    def search_documents(self, query: str, collection_name: str = "documents", n_results: int = 10) -> List[Dict[str, Any]]:
        """Search documents in the specified collection"""
        try:
            collection = self.get_collection(collection_name)
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0
                    })
            
            return formatted_results
        except Exception as e:
            print(f"❌ Error searching documents: {e}")
            return []
    
    def add_document(self, collection_name: str, document: str, metadata: Dict[str, Any], doc_id: str = None) -> str:
        """Add a document to the specified collection"""
        try:
            collection = self.get_collection(collection_name)
            
            if doc_id is None:
                doc_id = str(uuid.uuid4())
            
            collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            
            return doc_id
        except Exception as e:
            print(f"❌ Error adding document: {e}")
            return None
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the current database"""
        try:
            collections = self.client.list_collections()
            
            info = {
                'type': 'cloud' if self.use_cloud else 'local',
                'database': self.cloud_database if self.use_cloud else 'local',
                'collections': {}
            }
            
            for collection in collections:
                count = collection.count()
                info['collections'][collection.name] = {
                    'count': count,
                    'id': collection.id
                }
            
            return info
        except Exception as e:
            print(f"❌ Error getting database info: {e}")
            return {'type': 'unknown', 'error': str(e)}

# Convenience function to get the service
def get_chroma_service(use_cloud: bool = False) -> ChromaCloudService:
    """Get a ChromaDB service instance"""
    return ChromaCloudService(use_cloud=use_cloud)

if __name__ == "__main__":
    # Test both local and cloud connections
    print("🔍 Testing ChromaDB Services...")
    print("=" * 50)
    
    # Test local
    print("\n💾 Testing Local ChromaDB...")
    local_service = ChromaCloudService(use_cloud=False)
    local_service.test_connection()
    
    # Test cloud
    print("\n🌐 Testing Chroma Cloud...")
    cloud_service = ChromaCloudService(use_cloud=True)
    cloud_service.test_connection()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")

