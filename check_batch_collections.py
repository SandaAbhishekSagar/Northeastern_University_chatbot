#!/usr/bin/env python3
"""
Check for existing batch collections in local ChromaDB
"""

import os
import sys

def check_local_collections():
    """Check what collections exist in local ChromaDB"""
    print("🔍 Checking Local ChromaDB Collections")
    print("=" * 50)
    
    try:
        import chromadb
        
        # Connect to local ChromaDB
        client = chromadb.PersistentClient(path="./chroma_data")
        collections = client.list_collections()
        
        print(f"📋 Found {len(collections)} collections:")
        
        batch_collections = []
        main_collections = []
        
        for collection in collections:
            name = collection.name
            count = collection.count()
            print(f"  - {name}: {count:,} documents")
            
            if "batch" in name.lower():
                batch_collections.append((name, count))
            else:
                main_collections.append((name, count))
        
        print(f"\n📊 Collection Summary:")
        print(f"  Main collections: {len(main_collections)}")
        print(f"  Batch collections: {len(batch_collections)}")
        
        if batch_collections:
            print(f"\n📦 Batch Collections Found:")
            for name, count in batch_collections:
                print(f"  - {name}: {count:,} documents")
        
        # Check for documents_ultra_optimized
        ultra_optimized_count = 0
        for name, count in main_collections:
            if "ultra_optimized" in name:
                ultra_optimized_count = count
                break
        
        if ultra_optimized_count > 0:
            batch_size = 25
            expected_batches = (ultra_optimized_count + batch_size - 1) // batch_size
            print(f"\n📈 Ultra-optimized Collection Analysis:")
            print(f"  Total documents: {ultra_optimized_count:,}")
            print(f"  Expected batches: {expected_batches}")
            print(f"  Batch size: {batch_size}")
            
            # Check which batches exist
            existing_batch_nums = []
            for name, count in batch_collections:
                if "documents_ultra_optimized_batch_" in name:
                    try:
                        batch_num = int(name.split("_")[-1])
                        existing_batch_nums.append(batch_num)
                    except:
                        pass
            
            if existing_batch_nums:
                existing_batch_nums.sort()
                print(f"\n✅ Existing batch collections: {existing_batch_nums}")
                
                # Find missing batches
                expected_batch_nums = list(range(1, expected_batches + 1))
                missing_batches = [num for num in expected_batch_nums if num not in existing_batch_nums]
                
                if missing_batches:
                    print(f"❌ Missing batches: {missing_batches}")
                    print(f"\n📋 Missing batch details:")
                    for batch_num in missing_batches:
                        start_doc = (batch_num - 1) * batch_size + 1
                        end_doc = min(batch_num * batch_size, ultra_optimized_count)
                        print(f"  Batch {batch_num}: documents {start_doc}-{end_doc}")
                else:
                    print(f"🎉 All expected batches exist locally!")
            else:
                print(f"❌ No batch collections found for documents_ultra_optimized")
                print(f"   Expected batches: {list(range(1, expected_batches + 1))}")
        
        return ultra_optimized_count, batch_collections
        
    except Exception as e:
        print(f"❌ Error checking collections: {e}")
        return 0, []

def check_cloud_collections():
    """Check what collections exist in ChromaDB Cloud"""
    print("\n🌐 Checking ChromaDB Cloud Collections")
    print("=" * 50)
    
    try:
        from chroma_cloud_config import get_chroma_cloud_client
        
        client = get_chroma_cloud_client()
        collections = client.list_collections()
        
        print(f"📋 Found {len(collections)} collections in cloud:")
        
        batch_collections = []
        main_collections = []
        
        for collection in collections:
            name = collection.name
            count = collection.count()
            print(f"  - {name}: {count:,} documents")
            
            if "batch" in name.lower():
                batch_collections.append((name, count))
            else:
                main_collections.append((name, count))
        
        print(f"\n📊 Cloud Collection Summary:")
        print(f"  Main collections: {len(main_collections)}")
        print(f"  Batch collections: {len(batch_collections)}")
        
        if batch_collections:
            print(f"\n📦 Batch Collections in Cloud:")
            for name, count in batch_collections:
                print(f"  - {name}: {count:,} documents")
        
        return batch_collections, main_collections
        
    except Exception as e:
        print(f"❌ Error checking cloud collections: {e}")
        return [], []

def main():
    """Main function"""
    print("🔍 Batch Collection Status Checker")
    print("=" * 60)
    
    # Check local collections
    ultra_count, local_batches = check_local_collections()
    
    # Check cloud collections
    cloud_batches, cloud_main = check_cloud_collections()
    
    # Compare local vs cloud
    print(f"\n📊 Local vs Cloud Comparison")
    print("=" * 50)
    
    if ultra_count > 0:
        batch_size = 25
        expected_batches = (ultra_count + batch_size - 1) // batch_size
        
        # Get batch numbers from local
        local_batch_nums = []
        for name, count in local_batches:
            if "documents_ultra_optimized_batch_" in name:
                try:
                    batch_num = int(name.split("_")[-1])
                    local_batch_nums.append(batch_num)
                except:
                    pass
        
        # Get batch numbers from cloud
        cloud_batch_nums = []
        for name, count in cloud_batches:
            if "documents_ultra_optimized_batch_" in name:
                try:
                    batch_num = int(name.split("_")[-1])
                    cloud_batch_nums.append(batch_num)
                except:
                    pass
        
        print(f"📈 Expected batches: {expected_batches}")
        print(f"📦 Local batches: {sorted(local_batch_nums)}")
        print(f"🌐 Cloud batches: {sorted(cloud_batch_nums)}")
        
        # Find missing batches
        expected_batch_nums = list(range(1, expected_batches + 1))
        missing_from_cloud = [num for num in expected_batch_nums if num not in cloud_batch_nums]
        missing_from_local = [num for num in expected_batch_nums if num not in local_batch_nums]
        
        if missing_from_cloud:
            print(f"\n❌ Missing from cloud: {missing_from_cloud}")
            print(f"   These batches need to be uploaded to cloud")
        else:
            print(f"\n✅ All batches are in cloud!")
        
        if missing_from_local:
            print(f"\n⚠️  Missing from local: {missing_from_local}")
            print(f"   These batches may have been cleaned up after upload")
        
        # Check main collection
        ultra_in_cloud = False
        for name, count in cloud_main:
            if "ultra_optimized" in name:
                ultra_in_cloud = True
                print(f"\n📋 Main collection in cloud: {name} ({count:,} documents)")
                break
        
        if not ultra_in_cloud:
            print(f"\n⚠️  No main ultra_optimized collection found in cloud")
    
    print(f"\n🎯 Summary:")
    print(f"  Total documents: {ultra_count:,}")
    print(f"  Expected batches: {expected_batches if ultra_count > 0 else 0}")
    print(f"  Local batches: {len(local_batch_nums)}")
    print(f"  Cloud batches: {len(cloud_batch_nums)}")
    print(f"  Missing from cloud: {len(missing_from_cloud) if ultra_count > 0 else 0}")

if __name__ == "__main__":
    main()

