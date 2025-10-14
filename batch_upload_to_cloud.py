#!/usr/bin/env python3
"""
Upload large collections to Chroma Cloud in small batches
"""

import chromadb
import json
import subprocess
import time
from typing import List, Dict, Any

def upload_collection_in_batches(collection_name: str, batch_size: int = 50, local_path: str = "./chroma_data"):
    """Upload a collection to Chroma Cloud in small batches"""
    
    print(f"🚀 Starting batch upload of {collection_name} to Chroma Cloud...")
    print(f"📦 Batch size: {batch_size} documents")
    
    # Connect to local ChromaDB
    local_client = chromadb.PersistentClient(path=local_path)
    local_collection = local_client.get_collection(collection_name)
    
    # Get total count
    total_docs = local_collection.count()
    print(f"📊 Total documents to upload: {total_docs}")
    
    # Calculate number of batches
    num_batches = (total_docs + batch_size - 1) // batch_size
    print(f"📦 Number of batches: {num_batches}")
    
    successful_batches = 0
    failed_batches = 0
    
    for batch_num in range(num_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, total_docs)
        
        print(f"\n🔄 Processing batch {batch_num + 1}/{num_batches} (documents {start_idx + 1}-{end_idx})")
        
        # Create batch collection name
        batch_collection_name = f"{collection_name}_batch_{batch_num + 1}"
        
        try:
            # Get batch data
            batch_data = local_collection.get(
                limit=batch_size,
                offset=start_idx,
                include=['embeddings', 'documents', 'metadatas']
            )
            
            # Create batch collection
            try:
                local_client.delete_collection(batch_collection_name)
            except:
                pass
            
            batch_collection = local_client.create_collection(batch_collection_name)
            
            # Add batch data
            batch_collection.add(
                ids=batch_data['ids'],
                documents=batch_data['documents'],
                metadatas=batch_data['metadatas'],
                embeddings=batch_data['embeddings']
            )
            
            print(f"  💾 Created batch collection: {batch_collection_name}")
            
            # Upload to cloud
            print(f"  🌐 Uploading to Chroma Cloud...")
            result = subprocess.run([
                'chroma', 'copy',
                '--collections', batch_collection_name,
                '--from-local',
                '--to-cloud',
                '--db', 'newtest',
                '--path', local_path
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"  ✅ Batch {batch_num + 1} uploaded successfully!")
                successful_batches += 1
            else:
                print(f"  ❌ Batch {batch_num + 1} failed:")
                print(f"     Error: {result.stderr}")
                failed_batches += 1
            
            # Clean up batch collection
            try:
                local_client.delete_collection(batch_collection_name)
            except:
                pass
            
            # Small delay between batches
            time.sleep(2)
            
        except Exception as e:
            print(f"  ❌ Batch {batch_num + 1} failed with exception: {e}")
            failed_batches += 1
    
    print(f"\n🎉 Batch upload completed!")
    print(f"✅ Successful batches: {successful_batches}")
    print(f"❌ Failed batches: {failed_batches}")
    print(f"📊 Success rate: {(successful_batches / num_batches) * 100:.1f}%")
    
    return successful_batches, failed_batches

if __name__ == "__main__":
    print("🔧 Starting batch upload to Chroma Cloud...")
    print("=" * 60)
    
    # Upload the ultra-optimized collection in small batches
    successful, failed = upload_collection_in_batches("documents_ultra_optimized", batch_size=25)
    
    if failed == 0:
        print("\n🎉 All batches uploaded successfully!")
        print("🌐 Your data is now available in Chroma Cloud!")
    else:
        print(f"\n⚠️  {failed} batches failed. You may need to retry those batches.")
    
    print("\n" + "=" * 60)

