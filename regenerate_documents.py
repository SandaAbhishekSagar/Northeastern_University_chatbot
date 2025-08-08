#!/usr/bin/env python3
"""
Script to regenerate documents with file names in metadata
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

# Add project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent
sys.path.insert(0, str(project_root))

from services.shared.chroma_service import ChromaService
from services.shared.config import config

def extract_file_name(url: str) -> str:
    """Extract file name from URL"""
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    file_name = path_parts[-1] if path_parts else 'index.html'
    if not file_name or file_name.isspace():
        file_name = 'index.html'
    if not '.' in file_name:
        file_name += '.html'
    return file_name

def clean_metadata_value(value: Any) -> str:
    """Convert metadata value to string or default value"""
    if value is None:
        return ''
    return str(value)

def regenerate_documents():
    """Regenerate all documents with file names in metadata"""
    print("\nRegenerating Documents with File Names")
    print("=" * 40)
    
    chroma_service = ChromaService()
    
    # Get all documents
    print("Fetching all documents...")
    all_docs = chroma_service.get_all_documents()
    total_docs = len(all_docs)
    print(f"Found {total_docs} documents")
    
    # Process each document
    for i, doc in enumerate(all_docs, 1):
        try:
            # Skip documents without required fields
            if not doc.source_url or not doc.title or not doc.content or not doc.university_id:
                print(f"[{i}/{total_docs}] Skipping document {doc.id} - missing required fields")
                continue
            
            # Extract file name from URL
            file_name = extract_file_name(doc.source_url)
            
            # Create metadata dictionary with cleaned values
            metadata = {
                'file_name': file_name,
                'content_hash': clean_metadata_value(doc.extra_data.get('content_hash') if doc.extra_data else None),
                'status_code': clean_metadata_value(doc.extra_data.get('status_code') if doc.extra_data else None),
                'content_length': clean_metadata_value(doc.extra_data.get('content_length') if doc.extra_data else None),
                'page_type': clean_metadata_value(doc.extra_data.get('page_type') if doc.extra_data else None),
                'scraped_at': clean_metadata_value(doc.extra_data.get('scraped_at') if doc.extra_data else datetime.now().isoformat())
            }
            
            # Create new document version
            chroma_service.create_document(
                source_url=doc.source_url,
                title=doc.title,
                content=doc.content,
                university_id=doc.university_id,
                file_name=file_name,
                extra_data=metadata
            )
            
            print(f"[{i}/{total_docs}] Regenerated document: {doc.title} [{file_name}]")
            
        except Exception as e:
            print(f"Error processing document {doc.id}: {e}")
    
    print("\nDocument regeneration complete!")

if __name__ == "__main__":
    regenerate_documents() 