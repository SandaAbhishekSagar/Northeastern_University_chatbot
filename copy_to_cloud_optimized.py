#!/usr/bin/env python3
"""
Copy data from local ChromaDB to Chroma Cloud with size optimization
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from services.shared.chroma_cloud_service import ChromaCloudService

def optimize_document_for_cloud(document, metadata, max_size=15000):
    """Optimize document and metadata for cloud upload"""
    # Convert to string to check size
    doc_str = str(document)
    metadata_str = str(metadata)
    
    total_size = len(doc_str.encode('utf-8')) + len(metadata_str.encode('utf-8'))
    
    if total_size <= max_size:
        return document, metadata
    
    # If too large, truncate document content
    if 'content' in metadata:
        # Truncate content in metadata
        content = metadata['content']
        if len(content) > 5000:  # Limit content to 5000 chars
            metadata['content'] = content[:5000] + "... [truncated]"
    
    # Truncate main document if still too large
    if len(doc_str) > 8000:  # Limit document to 8000 chars
        document = doc_str[:8000] + "... [truncated]"
    
    return document, metadata

def copy_collection_data_optimized(local_service, cloud_service, collection_name, batch_size=50):
    """Copy data from local to cloud collection with size optimization"""
    try:
        print(f"\n📋 Copying {collection_name} collection (optimized)...")
        
        # Get local collection
        local_collection = local_service.get_collection(collection_name)
        local_count = local_collection.count()
        
        print(f"  📊 Local documents: {local_count}")
        
        if local_count == 0:
            print(f"  ⚠️  No documents to copy in {collection_name}")
            return True
        
        # Get cloud collection
        cloud_collection = cloud_service.get_collection(collection_name)
        cloud_count = cloud_collection.count()
        
        print(f"  📊 Cloud documents (before): {cloud_count}")
        
        # Copy in smaller batches with optimization
        copied = 0
        failed = 0
        offset = 0
        
        while offset < local_count:
            # Get batch from local
            batch = local_collection.get(
                limit=batch_size,
                offset=offset,
                include=['documents', 'metadatas']
            )
            
            if not batch['ids']:
                break
            
            # Process each document in the batch
            optimized_ids = []
            optimized_documents = []
            optimized_metadatas = []
            
            for i, (doc_id, document, metadata) in enumerate(zip(
                batch['ids'], 
                batch['documents'], 
                batch['metadatas']
            )):
                try:
                    # Optimize document for cloud
                    opt_doc, opt_meta = optimize_document_for_cloud(document, metadata)
                    
                    optimized_ids.append(doc_id)
                    optimized_documents.append(opt_doc)
                    optimized_metadatas.append(opt_meta)
                    
                except Exception as e:
                    print(f"    ⚠️  Skipping document {doc_id}: {e}")
                    failed += 1
                    continue
            
            # Add optimized batch to cloud
            if optimized_ids:
                try:
                    cloud_collection.add(
                        ids=optimized_ids,
                        documents=optimized_documents,
                        metadatas=optimized_metadatas
                    )
                    copied += len(optimized_ids)
                except Exception as e:
                    print(f"    ❌ Batch failed: {e}")
                    failed += len(optimized_ids)
            
            offset += batch_size
            
            if copied % 1000 == 0 or offset >= local_count:
                print(f"  📤 Processed {offset}/{local_count}, Copied: {copied}, Failed: {failed}")
        
        # Verify
        final_cloud_count = cloud_collection.count()
        print(f"  📊 Cloud documents (after): {final_cloud_count}")
        print(f"  ✅ Successfully copied {copied} documents")
        if failed > 0:
            print(f"  ⚠️  Failed to copy {failed} documents")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error copying {collection_name}: {e}")
        return False

def main():
    """Main function to copy all collections with optimization"""
    print("🚀 Copying Local ChromaDB to Cloud (Optimized)...")
    print("=" * 60)
    
    # Initialize services
    local_service = ChromaCloudService(use_cloud=False)
    cloud_service = ChromaCloudService(use_cloud=True)
    
    # Test connections
    print("🔍 Testing connections...")
    if not local_service.test_connection():
        print("❌ Local connection failed")
        return
    
    if not cloud_service.test_connection():
        print("❌ Cloud connection failed")
        return
    
    # Copy documents collection with optimization
    print("\n📋 Copying documents collection (this may take a while)...")
    if copy_collection_data_optimized(local_service, cloud_service, 'documents', batch_size=25):
        print("✅ Documents collection copied successfully")
    else:
        print("❌ Documents collection copy failed")
    
    # Final verification
    print("\n🔍 Final verification...")
    cloud_service.test_connection()
    
    print("\n" + "=" * 60)
    print("🎉 Copy process completed!")
    print("💡 Note: Documents were optimized for cloud storage (content truncated if needed)")

if __name__ == "__main__":
    main()

