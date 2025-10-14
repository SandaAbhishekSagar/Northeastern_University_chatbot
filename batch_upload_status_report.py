#!/usr/bin/env python3
"""
Comprehensive batch upload status report
Analyzes local and cloud collections to identify missing batches
"""

import os
import sys
import subprocess
from typing import List, Dict, Tuple

def get_local_collection_info():
    """Get information about local collections"""
    print("🔍 Analyzing Local ChromaDB Collections")
    print("=" * 50)
    
    try:
        import chromadb
        
        # Connect to local ChromaDB
        client = chromadb.PersistentClient(path="./chroma_data")
        collections = client.list_collections()
        
        collection_info = {}
        batch_collections = []
        main_collections = []
        
        for collection in collections:
            name = collection.name
            count = collection.count()
            collection_info[name] = count
            
            print(f"📋 {name}: {count:,} documents")
            
            if "batch" in name.lower():
                batch_collections.append((name, count))
            else:
                main_collections.append((name, count))
        
        # Focus on documents_ultra_optimized
        ultra_optimized_count = 0
        for name, count in main_collections:
            if "ultra_optimized" in name:
                ultra_optimized_count = count
                break
        
        print(f"\n📊 Collection Summary:")
        print(f"  Main collections: {len(main_collections)}")
        print(f"  Batch collections: {len(batch_collections)}")
        print(f"  Ultra-optimized documents: {ultra_optimized_count:,}")
        
        return ultra_optimized_count, batch_collections, collection_info
        
    except Exception as e:
        print(f"❌ Error analyzing local collections: {e}")
        return 0, [], {}

def check_cloud_collections():
    """Check what's in ChromaDB Cloud"""
    print("\n🌐 Analyzing ChromaDB Cloud Collections")
    print("=" * 50)
    
    try:
        from chroma_cloud_config import get_chroma_cloud_client
        
        client = get_chroma_cloud_client()
        collections = client.list_collections()
        
        cloud_info = {}
        batch_collections = []
        main_collections = []
        
        for collection in collections:
            name = collection.name
            count = collection.count()
            cloud_info[name] = count
            
            print(f"🌐 {name}: {count:,} documents")
            
            if "batch" in name.lower():
                batch_collections.append((name, count))
            else:
                main_collections.append((name, count))
        
        print(f"\n📊 Cloud Collection Summary:")
        print(f"  Main collections: {len(main_collections)}")
        print(f"  Batch collections: {len(batch_collections)}")
        
        return cloud_info, batch_collections, main_collections
        
    except Exception as e:
        print(f"❌ Error analyzing cloud collections: {e}")
        return {}, [], []

def analyze_batch_upload_status(ultra_count, local_batches, cloud_info, cloud_batches):
    """Analyze the batch upload status"""
    print("\n📊 Batch Upload Status Analysis")
    print("=" * 50)
    
    if ultra_count == 0:
        print("❌ No ultra-optimized documents found locally")
        return
    
    # Calculate expected batches
    batch_size = 25  # From batch_upload_to_cloud.py
    expected_batches = (ultra_count + batch_size - 1) // batch_size
    
    print(f"📈 Expected batches: {expected_batches}")
    print(f"📦 Batch size: {batch_size}")
    print(f"📊 Total documents: {ultra_count:,}")
    
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
    
    print(f"\n📦 Local batch collections: {sorted(local_batch_nums)}")
    print(f"🌐 Cloud batch collections: {sorted(cloud_batch_nums)}")
    
    # Find missing batches
    expected_batch_nums = list(range(1, expected_batches + 1))
    missing_from_cloud = [num for num in expected_batch_nums if num not in cloud_batch_nums]
    missing_from_local = [num for num in expected_batch_nums if num not in local_batch_nums]
    
    print(f"\n❌ Missing from cloud: {missing_from_cloud}")
    print(f"⚠️  Missing from local: {missing_from_local}")
    
    # Check main collection in cloud
    ultra_in_cloud = False
    ultra_cloud_count = 0
    for name, count in cloud_info.items():
        if "ultra_optimized" in name and "batch" not in name:
            ultra_in_cloud = True
            ultra_cloud_count = count
            print(f"\n📋 Main ultra_optimized collection in cloud: {count:,} documents")
            break
    
    if not ultra_in_cloud:
        print(f"\n⚠️  No main ultra_optimized collection found in cloud")
    
    # Calculate success rate
    uploaded_batches = len(cloud_batch_nums)
    success_rate = (uploaded_batches / expected_batches) * 100 if expected_batches > 0 else 0
    
    print(f"\n📊 Upload Statistics:")
    print(f"  Expected batches: {expected_batches}")
    print(f"  Uploaded batches: {uploaded_batches}")
    print(f"  Missing batches: {len(missing_from_cloud)}")
    print(f"  Success rate: {success_rate:.1f}%")
    
    return {
        'expected_batches': expected_batches,
        'uploaded_batches': uploaded_batches,
        'missing_batches': missing_from_cloud,
        'success_rate': success_rate,
        'ultra_count': ultra_count,
        'ultra_cloud_count': ultra_cloud_count
    }

def generate_missing_batch_report(missing_batches, ultra_count, batch_size=25):
    """Generate detailed report of missing batches"""
    print(f"\n📋 Missing Batch Details")
    print("=" * 50)
    
    if not missing_batches:
        print("🎉 No missing batches! All batches uploaded successfully.")
        return
    
    print(f"❌ {len(missing_batches)} batches are missing from cloud:")
    print()
    
    for batch_num in missing_batches:
        start_doc = (batch_num - 1) * batch_size + 1
        end_doc = min(batch_num * batch_size, ultra_count)
        doc_count = end_doc - start_doc + 1
        
        print(f"  Batch {batch_num}:")
        print(f"    Documents: {start_doc}-{end_doc} ({doc_count} documents)")
        print(f"    Collection name: documents_ultra_optimized_batch_{batch_num}")
        print()
    
    print(f"💡 To upload missing batches:")
    print(f"  1. Run: python batch_upload_to_cloud.py")
    print(f"  2. Or manually upload specific batches using chroma CLI")
    print(f"  3. Check logs for any error details")

def check_upload_logs():
    """Check for any upload logs or error files"""
    print(f"\n🔍 Checking for Upload Logs")
    print("=" * 50)
    
    # Look for log files
    log_files = []
    for file in os.listdir("."):
        if any(keyword in file.lower() for keyword in ["log", "batch", "upload", "error"]):
            log_files.append(file)
    
    if log_files:
        print(f"📄 Found potential log files: {log_files}")
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "batch" in content.lower() or "upload" in content.lower():
                        print(f"  📋 {log_file}: Contains batch/upload references")
            except:
                pass
    else:
        print("📄 No obvious log files found")

def main():
    """Main function to generate comprehensive batch upload status report"""
    print("🔍 ChromaDB Batch Upload Status Report")
    print("=" * 60)
    
    # Analyze local collections
    ultra_count, local_batches, local_info = get_local_collection_info()
    
    # Analyze cloud collections
    cloud_info, cloud_batches, cloud_main = check_cloud_collections()
    
    # Analyze batch upload status
    if ultra_count > 0:
        status = analyze_batch_upload_status(ultra_count, local_batches, cloud_info, cloud_batches)
        
        # Generate missing batch report
        generate_missing_batch_report(
            status['missing_batches'], 
            ultra_count, 
            batch_size=25
        )
        
        # Check for logs
        check_upload_logs()
        
        # Final summary
        print(f"\n🎯 Final Summary")
        print("=" * 50)
        print(f"📊 Total documents: {ultra_count:,}")
        print(f"📦 Expected batches: {status['expected_batches']}")
        print(f"✅ Uploaded batches: {status['uploaded_batches']}")
        print(f"❌ Missing batches: {len(status['missing_batches'])}")
        print(f"📈 Success rate: {status['success_rate']:.1f}%")
        
        if status['missing_batches']:
            print(f"\n⚠️  Action Required:")
            print(f"  {len(status['missing_batches'])} batches need to be uploaded to cloud")
            print(f"  Missing batches: {status['missing_batches']}")
        else:
            print(f"\n🎉 All batches successfully uploaded!")
    else:
        print(f"\n❌ No ultra-optimized documents found to analyze")

if __name__ == "__main__":
    main()

