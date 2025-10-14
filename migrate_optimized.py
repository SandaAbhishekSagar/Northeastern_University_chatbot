#!/usr/bin/env python3
"""
Optimized migration to Chroma Cloud with proper chunking and metadata cleanup
"""

import chromadb
import json
from typing import List, Dict, Any
import hashlib

def chunk_text(text: str, max_size: int = 12000) -> List[str]:
    """Split text into chunks that fit within size limit"""
    if len(text.encode('utf-8')) <= max_size:
        return [text]
    
    # Try to split on paragraphs first
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        potential_chunk = current_chunk + paragraph + "\n\n"
        if len(potential_chunk.encode('utf-8')) > max_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
            else:
                # Single paragraph is too long, split by sentences
                sentences = paragraph.split('. ')
                for sentence in sentences:
                    potential_chunk = current_chunk + sentence + ". "
                    if len(potential_chunk.encode('utf-8')) > max_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = sentence + ". "
                        else:
                            # Single sentence too long, split by words
                            words = sentence.split()
                            for word in words:
                                potential_chunk = current_chunk + word + " "
                                if len(potential_chunk.encode('utf-8')) > max_size:
                                    if current_chunk:
                                        chunks.append(current_chunk.strip())
                                        current_chunk = word + " "
                                    else:
                                        # Single word too long, truncate
                                        chunks.append(word[:max_size])
                                        current_chunk = ""
                                else:
                                    current_chunk = potential_chunk
                    else:
                        current_chunk = potential_chunk
        else:
            current_chunk = potential_chunk
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def clean_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Clean metadata by removing large fields and keeping only essential ones"""
    if not metadata:
        return {}
    
    # Keep only essential metadata fields
    essential_fields = [
        'id', 'title', 'source_url', 'page_type', 'university_id', 
        'document_id', 'version_number', 'created_at', 'scraped_at',
        'content_hash', 'status_code', 'file_name'
    ]
    
    cleaned = {}
    for field in essential_fields:
        if field in metadata:
            cleaned[field] = metadata[field]
    
    # Remove the large 'content' field that's duplicating the document
    # Remove 'content_length' as it's not essential
    # Keep other small fields that might be useful
    
    return cleaned

def migrate_collection_optimized(collection_name: str, local_path: str = "./chroma_data"):
    """Migrate a collection with optimized chunking and metadata cleanup"""
    
    print(f"🚀 Starting optimized migration of {collection_name}...")
    
    # Connect to local ChromaDB
    local_client = chromadb.PersistentClient(path=local_path)
    local_collection = local_client.get_collection(collection_name)
    
    # Get all data
    print(f"📥 Getting all data from {collection_name}...")
    all_data = local_collection.get(include=['embeddings', 'documents', 'metadatas'])
    
    total_docs = len(all_data['ids'])
    print(f"📊 Found {total_docs} documents")
    
    # Process documents and create optimized chunks
    optimized_ids = []
    optimized_documents = []
    optimized_metadatas = []
    optimized_embeddings = []
    
    large_docs_count = 0
    chunked_docs_count = 0
    
    for i, (doc_id, document, metadata, embedding) in enumerate(zip(
        all_data['ids'], all_data['documents'], all_data['metadatas'], all_data['embeddings']
    )):
        if i % 1000 == 0:
            print(f"🔄 Processing document {i+1}/{total_docs}")
        
        # Clean metadata first
        clean_meta = clean_metadata(metadata)
        
        # Calculate size with cleaned metadata
        doc_size = len(document.encode('utf-8')) if document else 0
        meta_size = len(json.dumps(clean_meta).encode('utf-8'))
        total_size = doc_size + meta_size
        
        if total_size > 15000:  # Chunk if still too large
            large_docs_count += 1
            print(f"📝 Chunking large document {doc_id} ({total_size} bytes)")
            
            chunks = chunk_text(document)
            chunked_docs_count += len(chunks)
            
            for j, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{j}"
                optimized_ids.append(chunk_id)
                optimized_documents.append(chunk)
                
                # Add chunk info to metadata
                chunk_metadata = clean_meta.copy()
                chunk_metadata.update({
                    'original_id': doc_id,
                    'chunk_index': j,
                    'total_chunks': len(chunks),
                    'is_chunked': True
                })
                
                optimized_metadatas.append(chunk_metadata)
                optimized_embeddings.append(embedding)
        else:
            # Document is small enough, keep as-is
            optimized_ids.append(doc_id)
            optimized_documents.append(document)
            optimized_metadatas.append(clean_meta)
            optimized_embeddings.append(embedding)
    
    print(f"✂️ Chunked {large_docs_count} large documents into {chunked_docs_count} chunks")
    print(f"📤 Total documents after optimization: {len(optimized_ids)}")
    
    # Save optimized data to a new local collection
    optimized_collection_name = f"{collection_name}_optimized"
    
    try:
        local_client.delete_collection(optimized_collection_name)
    except:
        pass
    
    optimized_collection = local_client.create_collection(optimized_collection_name)
    
    # Add in batches
    batch_size = 500  # Smaller batches for cloud upload
    for i in range(0, len(optimized_ids), batch_size):
        end_idx = min(i + batch_size, len(optimized_ids))
        
        batch_ids = optimized_ids[i:end_idx]
        batch_docs = optimized_documents[i:end_idx]
        batch_metadata = optimized_metadatas[i:end_idx]
        batch_embeddings = optimized_embeddings[i:end_idx]
        
        print(f"💾 Adding batch {i//batch_size + 1} ({len(batch_ids)} documents)")
        
        optimized_collection.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_metadata,
            embeddings=batch_embeddings
        )
    
    print(f"✅ Created optimized collection: {optimized_collection_name}")
    
    # Test a few documents to verify sizes
    test_sample = optimized_collection.get(limit=10, include=['documents', 'metadatas'])
    test_sizes = []
    for doc, meta in zip(test_sample['documents'], test_sample['metadatas']):
        doc_size = len(doc.encode('utf-8')) if doc else 0
        meta_size = len(json.dumps(meta).encode('utf-8'))
        test_sizes.append(doc_size + meta_size)
    
    if test_sizes:
        avg_size = sum(test_sizes) / len(test_sizes)
        max_size = max(test_sizes)
        print(f"📊 Test sample - Average size: {avg_size:.0f} bytes, Max size: {max_size} bytes")
        
        if max_size > 16384:
            print(f"⚠️  Warning: Some documents still exceed 16KB limit")
        else:
            print(f"✅ All test documents are within 16KB limit")
    
    return optimized_collection_name

if __name__ == "__main__":
    print("🔧 Starting optimized migration to Chroma Cloud...")
    print("=" * 60)
    
    # Process the documents collection
    optimized_name = migrate_collection_optimized("documents")
    
    print(f"\n🚀 Ready to upload to cloud!")
    print(f"📋 Use this command to copy to cloud:")
    print(f"chroma copy --collections {optimized_name} --from-local --to-cloud --db Northeasterndatabase --path ./chroma_data")
    
    print("\n🎉 Optimization complete!")
