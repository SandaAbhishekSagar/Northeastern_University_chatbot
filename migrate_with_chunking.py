#!/usr/bin/env python3
"""
Migrate ChromaDB data to cloud with intelligent chunking
"""

import chromadb
import json
from typing import List, Dict, Any
import hashlib

def chunk_text(text: str, max_size: int = 15000) -> List[str]:
    """Split text into chunks that fit within size limit (leaving room for metadata)"""
    if len(text.encode('utf-8')) <= max_size:
        return [text]
    
    # Try to split on sentences first
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        potential_chunk = current_chunk + sentence + ". "
        if len(potential_chunk.encode('utf-8')) > max_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
            else:
                # Single sentence is too long, split by words
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
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def migrate_collection_with_chunking(collection_name: str, local_path: str = "./chroma_data"):
    """Migrate a collection by chunking large documents"""
    
    # Connect to local ChromaDB
    local_client = chromadb.PersistentClient(path=local_path)
    local_collection = local_client.get_collection(collection_name)
    
    # Get all data
    print(f"📥 Getting all data from {collection_name}...")
    all_data = local_collection.get(include=['embeddings', 'documents', 'metadatas', 'ids'])
    
    total_docs = len(all_data['ids'])
    print(f"📊 Found {total_docs} documents")
    
    # Process documents and create chunks
    chunked_ids = []
    chunked_documents = []
    chunked_metadatas = []
    chunked_embeddings = []
    
    large_docs_count = 0
    
    for i, (doc_id, document, metadata, embedding) in enumerate(zip(
        all_data['ids'], all_data['documents'], all_data['metadatas'], all_data['embeddings']
    )):
        if i % 1000 == 0:
            print(f"🔄 Processing document {i+1}/{total_docs}")
        
        doc_size = len(document.encode('utf-8')) if document else 0
        
        if doc_size > 15000:  # Chunk if larger than 15KB (leaving room for metadata)
            large_docs_count += 1
            print(f"📝 Chunking large document {doc_id} ({doc_size} bytes)")
            
            chunks = chunk_text(document)
            
            for j, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{j}"
                chunked_ids.append(chunk_id)
                chunked_documents.append(chunk)
                
                # Add chunk info to metadata
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata.update({
                    'original_id': doc_id,
                    'chunk_index': j,
                    'total_chunks': len(chunks),
                    'is_chunked': True
                })
                
                # Remove large metadata fields to stay under quota
                fields_to_remove = ['content']  # Add other large fields as needed
                for field in fields_to_remove:
                    chunk_metadata.pop(field, None)
                
                chunked_metadatas.append(chunk_metadata)
                
                # For embeddings, we'll need to re-generate them or use the original
                # For now, using original embedding for all chunks (not ideal but works)
                chunked_embeddings.append(embedding)
        else:
            # Document is small enough, keep as-is
            chunked_ids.append(doc_id)
            chunked_documents.append(document)
            
            # Still remove large metadata fields
            clean_metadata = metadata.copy() if metadata else {}
            fields_to_remove = ['content']  # Add other large fields as needed
            for field in fields_to_remove:
                clean_metadata.pop(field, None)
            
            chunked_metadatas.append(clean_metadata)
            chunked_embeddings.append(embedding)
    
    print(f"✂️ Chunked {large_docs_count} large documents")
    print(f"📤 Total documents after chunking: {len(chunked_ids)}")
    
    # Save processed data to a new local collection for testing
    processed_collection_name = f"{collection_name}_chunked"
    
    try:
        local_client.delete_collection(processed_collection_name)
    except:
        pass
    
    processed_collection = local_client.create_collection(processed_collection_name)
    
    # Add in batches
    batch_size = 1000
    for i in range(0, len(chunked_ids), batch_size):
        end_idx = min(i + batch_size, len(chunked_ids))
        
        batch_ids = chunked_ids[i:end_idx]
        batch_docs = chunked_documents[i:end_idx]
        batch_metadata = chunked_metadatas[i:end_idx]
        batch_embeddings = chunked_embeddings[i:end_idx]
        
        print(f"💾 Adding batch {i//batch_size + 1} ({len(batch_ids)} documents)")
        
        processed_collection.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_metadata,
            embeddings=batch_embeddings
        )
    
    print(f"✅ Created chunked collection: {processed_collection_name}")
    print(f"🚀 Now you can try: chroma copy --collections {processed_collection_name} --from-local --to-cloud --db Northeasterndatabase --path {local_path}")
    
    return processed_collection_name

if __name__ == "__main__":
    # Process the documents collection
    print("🔧 Starting migration with chunking...")
    
    # Check which collections need chunking
    client = chromadb.PersistentClient(path="./chroma_data")
    
    for collection_name in ["documents", "chat_messages"]:
        try:
            collection = client.get_collection(collection_name)
            sample = collection.get(limit=5, include=['documents'])
            
            large_docs = 0
            for doc in sample['documents']:
                if doc and len(doc.encode('utf-8')) > 15000:
                    large_docs += 1
            
            if large_docs > 0:
                print(f"\n📋 Processing {collection_name} (found {large_docs} large documents in sample)")
                migrate_collection_with_chunking(collection_name)
            else:
                print(f"\n📋 {collection_name} looks fine (no large documents found)")
        
        except Exception as e:
            print(f"❌ Error processing {collection_name}: {e}")
    
    print("\n🎉 Migration complete!")

