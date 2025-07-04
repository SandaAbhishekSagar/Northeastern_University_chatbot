from celery import Celery
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import config
from shared.chroma_service import chroma_service
from .text_processor import TextProcessor
from .embeddings_generator import EmbeddingsGenerator

# Initialize Celery
app = Celery('processing_service')
app.conf.broker_url = 'pyamqp://admin:password@localhost:5672//'
app.conf.result_backend = config.REDIS_URL

# Initialize processors
text_processor = TextProcessor()
embeddings_generator = EmbeddingsGenerator()

@app.task(bind=True, max_retries=3)
def process_document(self, document_id: str):
    """Process a document: generate embeddings and extract metadata"""
    try:
        # Get document from ChromaDB
        document = chroma_service.get_document(document_id)
        if not document:
            raise ValueError(f"Document with id {document_id} not found")
        
        # Process text
        cleaned_content = text_processor.clean_text(document.content)
        
        # Split into chunks for better embedding quality
        chunks = text_processor.split_into_chunks(cleaned_content)
        
        # Generate embeddings for chunks
        chunk_embeddings = embeddings_generator.generate_embeddings(chunks)
        
        # Compute average embedding (simple approach)
        if chunk_embeddings:
            avg_embedding = [
                sum(dim_values) / len(dim_values) 
                for dim_values in zip(*chunk_embeddings)
            ]
        else:
            avg_embedding = [0.0] * embeddings_generator.embedding_dim
        
        # Extract additional metadata
        entities = text_processor.extract_entities(cleaned_content)
        keywords = text_processor.extract_keywords(cleaned_content)
        
        # Update document with embeddings and metadata
        extra_data = document.extra_data or {}
        extra_data.update({
            'entities': entities,
            'keywords': keywords,
            'chunk_count': len(chunks),
            'processed_at': datetime.now().isoformat()
        })
        
        # Update document in ChromaDB
        collection = chroma_service.client.get_collection('documents')
        collection.update(
            ids=[document_id],
            embeddings=[avg_embedding],
            metadatas=[{
                **document.to_dict(),
                'embedding': avg_embedding,
                'extra_data': extra_data
            }]
        )
        
        print(f"Successfully processed document {document_id}")
        return f"Processed document {document_id}"
        
    except Exception as exc:
        print(f"Error processing document {document_id}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@app.task
def scrape_university_websites():
    """Trigger scraping of all university websites"""
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    
    # Import here to avoid circular imports
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scraping_service'))
    from spiders.university_spider import UniversitySpider
    
    # Get university URLs from ChromaDB
    try:
        universities = chroma_service.get_all_universities()
        university_urls = ','.join([uni.base_url for uni in universities if uni.scraping_enabled])
        
        if not university_urls:
            university_urls = ','.join(config.UNIVERSITY_URLS)
        
        # Configure and run spider
        settings = get_project_settings()
        process = CrawlerProcess(settings)
        
        process.crawl(UniversitySpider, university_urls=university_urls)
        process.start()
        
    except Exception as e:
        print(f"Error in scraping task: {e}")

@app.task
def update_embeddings_for_new_documents():
    """Process any documents that don't have embeddings yet"""
    try:
        # Get all documents from ChromaDB
        collection = chroma_service.client.get_collection('documents')
        result = collection.get()
        
        unprocessed_docs = []
        for i, doc_id in enumerate(result['ids']):
            metadata = result['metadatas'][i]
            # Check if document has embedding
            if not metadata.get('embedding'):
                unprocessed_docs.append(doc_id)
        
        print(f"Found {len(unprocessed_docs)} unprocessed documents")
        
        # Process each document
        for doc_id in unprocessed_docs:
            process_document.delay(doc_id)
        
        return f"Queued {len(unprocessed_docs)} documents for processing"
        
    except Exception as e:
        print(f"Error in update embeddings task: {e}")

# Periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    # Scrape websites daily at 2 AM
    'daily-scrape': {
        'task': 'processing_service.tasks.scrape_university_websites',
        'schedule': crontab(hour=2, minute=0),
    },
    # Process new documents every hour
    'process-documents': {
        'task': 'processing_service.tasks.update_embeddings_for_new_documents',
        'schedule': crontab(minute=0),
    },
}

app.conf.timezone = 'UTC'

if __name__ == '__main__':
    app.start()