#!/usr/bin/env python3
"""
Check batch upload status to ChromaDB Cloud
Identifies which batches were not uploaded successfully
"""

import chromadb
import subprocess
import json
from typing import List, Dict, Any, Tuple
from chroma_cloud_config import get_chroma_cloud_client, CHROMA_CLOUD_CONFIG

def get_local_collections(local_path: str = "./chroma_data") -> Dict[str, int]:
    """Get all collections from local ChromaDB with document counts"""
    try:
        local_client = chromadb.PersistentClient(path=local_path)
        collections = local_client.list_collections()
        
        collection_info = {}
        for collection in collections:
            count = collection.count()
            collection_info[collection.name] = count
            print(f"📋 Local collection '{collection.name}': {count} documents")
        
        return collection_info
    except Exception as e:
        print(f"❌ Error accessing local ChromaDB: {e}")
        return {}

def get_cloud_collections() -> Dict[str, int]:
    """Get all collections from ChromaDB Cloud with document counts"""
    try:
        cloud_client = get_chroma_cloud_client()
        collections = cloud_client.list_collections()
        
        collection_info = {}
        for collection in collections:
            count = collection.count()
            collection_info[collection.name] = count
            print(f"🌐 Cloud collection '{collection.name}': {count} documents")
        
        return collection_info
    except Exception as e:
        print(f"❌ Error accessing ChromaDB Cloud: {e}")
        return {}

def check_batch_collections_in_cloud() -> List[str]:
    """Check for batch collections in cloud (documents_ultra_optimized_batch_X)"""
    try:
        cloud_client = get_chroma_cloud_client()
        collections = cloud_client.list_collections()
        
        batch_collections = []
        for collection in collections:
            if collection.name.startswith("documents_ultra_optimized_batch_"):
                batch_num = collection.name.split("_")[-1]
                batch_collections.append(batch_num)
        
        return sorted(batch_collections, key=int)
    except Exception as e:
        print(f"❌ Error checking batch collections in cloud: {e}")
        return []

def calculate_expected_batches(total_docs: int, batch_size: int = 25) -> int:
    """Calculate expected number of batches based on total documents"""
    return (total_docs + batch_size - 1) // batch_size

def check_missing_batches():
    """Check which batches are missing from cloud upload"""
    print("🔍 Checking Batch Upload Status to ChromaDB Cloud")
    print("=" * 60)
    
    # Get local collection info
    print("\n📊 Local ChromaDB Collections:")
    local_collections = get_local_collections()
    
    if "documents_ultra_optimized" not in local_collections:
        print("❌ No 'documents_ultra_optimized' collection found locally!")
        return
    
    total_docs = local_collections["documents_ultra_optimized"]
    print(f"\n📈 Total documents in 'documents_ultra_optimized': {total_docs}")
    
    # Calculate expected batches
    batch_size = 25  # From the batch_upload_to_cloud.py script
    expected_batches = calculate_expected_batches(total_docs, batch_size)
    print(f"📦 Expected number of batches: {expected_batches}")
    
    # Get cloud collections
    print("\n🌐 ChromaDB Cloud Collections:")
    cloud_collections = get_cloud_collections()
    
    # Check for batch collections in cloud
    print("\n🔍 Checking for batch collections in cloud...")
    uploaded_batches = check_batch_collections_in_cloud()
    
    if uploaded_batches:
        print(f"✅ Found {len(uploaded_batches)} batch collections in cloud:")
        for batch_num in uploaded_batches:
            print(f"  - documents_ultra_optimized_batch_{batch_num}")
    else:
        print("❌ No batch collections found in cloud!")
    
    # Calculate missing batches
    expected_batch_numbers = [str(i) for i in range(1, expected_batches + 1)]
    missing_batches = [batch for batch in expected_batch_numbers if batch not in uploaded_batches]
    
    print(f"\n📊 Upload Status Summary:")
    print(f"  📈 Total documents: {total_docs}")
    print(f"  📦 Expected batches: {expected_batches}")
    print(f"  ✅ Uploaded batches: {len(uploaded_batches)}")
    print(f"  ❌ Missing batches: {len(missing_batches)}")
    
    if missing_batches:
        print(f"\n❌ Missing Batches:")
        for batch_num in missing_batches:
            start_doc = (int(batch_num) - 1) * batch_size + 1
            end_doc = min(int(batch_num) * batch_size, total_docs)
            print(f"  - Batch {batch_num}: documents {start_doc}-{end_doc}")
        
        print(f"\n🔄 To retry missing batches, you can:")
        print(f"  1. Run the batch upload script again")
        print(f"  2. Manually upload specific batches")
        print(f"  3. Check the batch upload logs for error details")
    else:
        print(f"\n🎉 All batches uploaded successfully!")
    
    # Check if there's a main collection in cloud
    if "documents_ultra_optimized" in cloud_collections:
        cloud_count = cloud_collections["documents_ultra_optimized"]
        print(f"\n📋 Main collection in cloud: {cloud_count} documents")
        if cloud_count == total_docs:
            print("✅ Main collection has all documents!")
        else:
            print(f"⚠️  Main collection missing {total_docs - cloud_count} documents")
    
    return missing_batches, uploaded_batches, expected_batches

def get_batch_upload_logs():
    """Try to find any logs from batch upload attempts"""
    print("\n🔍 Checking for batch upload logs...")
    
    # Check if there are any log files
    import os
    log_files = []
    for file in os.listdir("."):
        if "log" in file.lower() or "batch" in file.lower():
            log_files.append(file)
    
    if log_files:
        print(f"📄 Found potential log files: {log_files}")
    else:
        print("📄 No obvious log files found")

if __name__ == "__main__":
    try:
        missing, uploaded, expected = check_missing_batches()
        get_batch_upload_logs()
        
        print(f"\n" + "=" * 60)
        print(f"📊 Final Summary:")
        print(f"  Expected batches: {expected}")
        print(f"  Uploaded batches: {len(uploaded)}")
        print(f"  Missing batches: {len(missing)}")
        
        if missing:
            print(f"\n⚠️  Action needed: {len(missing)} batches need to be uploaded")
        else:
            print(f"\n🎉 All batches successfully uploaded!")
            
    except Exception as e:
        print(f"❌ Error during batch status check: {e}")
        import traceback
        traceback.print_exc()

