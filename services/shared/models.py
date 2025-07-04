from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class University:
    """University data model for ChromaDB"""
    id: Optional[str] = None
    name: str = ""
    base_url: str = ""
    scraping_enabled: bool = True
    last_scraped: Optional[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for ChromaDB storage"""
        data = asdict(self)
        # Filter out None values as ChromaDB doesn't accept them
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'University':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class DocumentVersion:
    """Document version data model for ChromaDB"""
    id: Optional[str] = None
    document_id: Optional[str] = None
    version_number: int = 0
    source_url: str = ""
    title: Optional[str] = None
    content: str = ""
    content_hash: Optional[str] = None
    embedding: Optional[List[float]] = None
    extra_data: Optional[Dict[str, Any]] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    created_at: Optional[str] = None
    university_id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.document_id is None:
            self.document_id = str(uuid.uuid4())
        if self.content_hash is None and self.content:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.valid_from is None:
            self.valid_from = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for ChromaDB storage"""
        data = asdict(self)
        # Filter out None values as ChromaDB doesn't accept them
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentVersion':
        """Create from dictionary"""
        # Filter out fields that don't belong to the class
        valid_fields = {
            'id', 'document_id', 'version_number', 'source_url', 'title', 
            'content', 'content_hash', 'embedding', 'extra_data', 'valid_from', 
            'valid_to', 'created_at', 'university_id'
        }
        
        # Extract valid fields
        valid_data = {k: v for k, v in data.items() if k in valid_fields}
        
        # Put remaining fields into extra_data
        extra_fields = {k: v for k, v in data.items() if k not in valid_fields}
        if extra_fields and 'extra_data' not in valid_data:
            valid_data['extra_data'] = extra_fields
        elif extra_fields and 'extra_data' in valid_data:
            # Merge with existing extra_data
            if isinstance(valid_data['extra_data'], dict):
                valid_data['extra_data'].update(extra_fields)
            else:
                valid_data['extra_data'] = extra_fields
        
        return cls(**valid_data)

@dataclass
class ScrapeLog:
    """Scrape log data model for ChromaDB"""
    id: Optional[str] = None
    university_id: str = ""
    url: str = ""
    status: str = ""  # success, failed, unchanged
    pages_scraped: int = 0
    changes_detected: int = 0
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.started_at is None:
            self.started_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for ChromaDB storage"""
        data = asdict(self)
        # Filter out None values as ChromaDB doesn't accept them
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScrapeLog':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class ChatSession:
    """Chat session data model for ChromaDB"""
    id: Optional[str] = None
    user_id: Optional[str] = None
    started_at: Optional[str] = None
    last_interaction: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.started_at is None:
            self.started_at = datetime.now().isoformat()
        if self.last_interaction is None:
            self.last_interaction = datetime.now().isoformat()
        if self.context is None:
            self.context = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for ChromaDB storage"""
        data = asdict(self)
        # Filter out None values as ChromaDB doesn't accept them
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class ChatMessage:
    """Chat message data model for ChromaDB"""
    id: Optional[str] = None
    session_id: str = ""
    message_type: str = ""  # user, assistant
    content: str = ""
    sources: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.sources is None:
            self.sources = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for ChromaDB storage"""
        data = asdict(self)
        # Filter out None values as ChromaDB doesn't accept them
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create from dictionary"""
        return cls(**data)

# ChromaDB Collection Names
COLLECTIONS = {
    'universities': 'universities',
    'documents': 'documents',
    'scrape_logs': 'scrape_logs', 
    'chat_sessions': 'chat_sessions',
    'chat_messages': 'chat_messages',
    'feedback': 'feedback'
}

def test_models():
    """Test that all models can be created and serialized"""
    try:
        # Test University model
        university = University(
            name="Test University",
            base_url="https://example.edu"
        )
        print(f"[OK] University model: {university.name}")
        
        # Test DocumentVersion model
        doc = DocumentVersion(
            version_number=1,
            source_url="https://example.edu/page",
            title="Test Document",
            content="This is test content"
        )
        print(f"[OK] DocumentVersion model: {doc.title}")
        
        # Test ScrapeLog model
        log = ScrapeLog(
            university_id=str(uuid.uuid4()),
            url="https://example.edu",
            status="success"
        )
        print(f"[OK] ScrapeLog model: {log.status}")
        
        # Test ChatSession model
        session = ChatSession(user_id="test_user")
        print(f"[OK] ChatSession model: {session.id}")
        
        # Test ChatMessage model
        message = ChatMessage(
            session_id=str(session.id),
            message_type="user",
            content="Hello, world!"
        )
        print(f"[OK] ChatMessage model: {message.message_type}")
        
        # Test serialization
        models = [university, doc, log, session, message]
        for model in models:
            data = model.to_dict()
            print(f"[OK] {model.__class__.__name__} serialized to dict")
        
        print("[OK] All models created and serialized successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Model test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing ChromaDB Data Models")
    print("=" * 30)
    test_models()