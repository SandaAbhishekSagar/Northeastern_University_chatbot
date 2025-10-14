#!/usr/bin/env python3
"""
Copy data from local ChromaDB to Chroma Cloud
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from services.shared.chroma_cloud_service import ChromaCloudService

def copy_collection_data(local_service, cloud_service, collection_name, batch_size=100):
    """Copy data from local to cloud collection in batches"""
    try:
        print(f"\n📋 Copying {collection_name} collection...")
        
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
        
        # Copy in batches
        copied = 0
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
            
            # Add batch to cloud
            cloud_collection.add(
                ids=batch['ids'],
                documents=batch['documents'],
                metadatas=batch['metadatas']
            )
            
            copied += len(batch['ids'])
            offset += batch_size
            
            print(f"  📤 Copied {copied}/{local_count} documents...")
        
        # Verify
        final_cloud_count = cloud_collection.count()
        print(f"  📊 Cloud documents (after): {final_cloud_count}")
        print(f"  ✅ Successfully copied {copied} documents")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error copying {collection_name}: {e}")
        return False

def main():
    """Main function to copy all collections"""
    print("🚀 Copying Local ChromaDB to Cloud...")
    print("=" * 50)
    
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
    
    # Collections to copy
    collections_to_copy = ['documents', 'universities', 'chat_messages']
    
    success_count = 0
    for collection_name in collections_to_copy:
        if copy_collection_data(local_service, cloud_service, collection_name):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 Copy completed! {success_count}/{len(collections_to_copy)} collections copied successfully")
    
    # Final verification
    print("\n🔍 Final verification...")
    cloud_service.test_connection()

if __name__ == "__main__":
    main()

