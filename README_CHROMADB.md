# University Chatbot - ChromaDB Version

This is the ChromaDB-based version of the University Chatbot system, which has been migrated from PostgreSQL to use ChromaDB as the vector database.

## What Changed

### Database Migration
- **From**: PostgreSQL + pgvector + SQLAlchemy ORM
- **To**: ChromaDB (vector database) with Python client

### Key Benefits
- **Simplified Setup**: No need for PostgreSQL configuration
- **Better Vector Search**: Native vector similarity search
- **Easier Scaling**: ChromaDB handles vector operations efficiently
- **Reduced Dependencies**: Fewer database-related packages

## Architecture

### New Components
- `services/shared/database.py` - ChromaDB client setup
- `services/shared/models.py` - Data models (dataclasses instead of SQLAlchemy ORM)
- `services/shared/chroma_service.py` - Service layer for ChromaDB operations
- `setup_chromadb.py` - Setup script for ChromaDB

### Collections
ChromaDB uses collections instead of tables:
- `universities` - University information
- `documents` - Scraped documents with embeddings
- `scrape_logs` - Scraping activity logs
- `chat_sessions` - Chat session data
- `chat_messages` - Individual chat messages

## Quick Start

### 1. Prerequisites
- Docker and Docker Compose
- Python 3.8+
- Virtual environment (recommended)

### 2. Setup
```bash
# Clone the repository
git clone <repository-url>
cd university_chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the setup script
python setup_chromadb.py
```

### 3. Start Services
```bash
# Start ChromaDB (if not already running)
docker-compose up -d chromadb

# Start all services (in separate terminals)
python run.py worker    # Celery worker
python run.py beat      # Celery scheduler
python run.py api       # FastAPI server
python run.py scrape    # Web scraper
```

### 4. Test the System
```bash
python test_system.py
```

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# ChromaDB Settings
CHROMADB_HOST=localhost
CHROMADB_HTTP_PORT=8000

# Redis Settings
REDIS_URL=redis://localhost:6379/0

# LLM Settings
LOCAL_LLM_MODEL=llama2:7b
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Scraping Settings
SCRAPING_DELAY=3
MAX_CONCURRENT_REQUESTS=2
UNIVERSITY_URLS=https://www.northeastern.edu,https://catalog.northeastern.edu
```

## API Endpoints

The API endpoints remain the same:

- `GET /` - Health check
- `POST /chat` - Chat with the bot
- `GET /search` - Search documents
- `GET /universities` - List universities
- `GET /documents` - List documents

## Data Models

### University
```python
@dataclass
class University:
    id: Optional[str] = None
    name: str = ""
    base_url: str = ""
    scraping_enabled: bool = True
    last_scraped: Optional[str] = None
    created_at: Optional[str] = None
```

### DocumentVersion
```python
@dataclass
class DocumentVersion:
    id: Optional[str] = None
    document_id: Optional[str] = None
    version_number: int = 0
    source_url: str = ""
    title: Optional[str] = None
    content: str = ""
    embedding: Optional[List[float]] = None
    university_id: Optional[str] = None
    # ... other fields
```

## Usage Examples

### Using the ChromaDB Service
```python
from services.shared.chroma_service import chroma_service

# Create a university
university = chroma_service.create_university(
    name="Northeastern University",
    base_url="https://www.northeastern.edu"
)

# Create a document
doc = chroma_service.create_document(
    source_url="https://example.edu/page",
    title="Computer Science Program",
    content="The computer science program offers...",
    university_id=university.id,
    embedding=[0.1, 0.2, 0.3, ...]  # Vector embedding
)

# Search documents
results = chroma_service.search_documents(
    query="computer science",
    n_results=5,
    university_id=university.id
)
```

## Troubleshooting

### ChromaDB Connection Issues
1. Check if Docker is running: `docker ps`
2. Check ChromaDB logs: `docker-compose logs chromadb`
3. Verify port 8000 is available
4. Restart ChromaDB: `docker-compose restart chromadb`

### Python Import Errors
1. Install dependencies: `pip install -r requirements.txt`
2. Check virtual environment is activated
3. Verify Python path includes project root

### Vector Search Issues
1. Ensure documents have embeddings
2. Check embedding model is working
3. Verify ChromaDB collections exist

## Migration from PostgreSQL

If you're migrating from the PostgreSQL version:

1. **Backup Data**: Export any important data from PostgreSQL
2. **Install ChromaDB**: Run `python setup_chromadb.py`
3. **Re-scrape Data**: Run `python run.py scrape` to populate ChromaDB
4. **Test System**: Run `python test_system.py`

## Performance

### ChromaDB Advantages
- **Fast Vector Search**: Optimized for similarity queries
- **Memory Efficient**: Better memory usage for large datasets
- **Scalable**: Can handle millions of vectors efficiently

### Monitoring
- Check collection sizes: `chroma_service.get_collection_count('documents')`
- Monitor ChromaDB logs: `docker-compose logs -f chromadb`
- Use ChromaDB dashboard (if available)

## Development

### Adding New Collections
1. Add collection name to `COLLECTIONS` in `models.py`
2. Create data model in `models.py`
3. Add service methods in `chroma_service.py`
4. Update `database.py` initialization

### Testing
```bash
# Test individual components
python services/shared/models.py
python services/shared/chroma_service.py
python services/shared/database.py

# Test full system
python test_system.py
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review ChromaDB documentation
3. Check Docker logs for container issues
4. Verify all dependencies are installed

---

**Note**: This version is optimized for vector search and document similarity, making it ideal for RAG (Retrieval-Augmented Generation) applications. 