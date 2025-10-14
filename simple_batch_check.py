#!/usr/bin/env python3
"""
Simple script to check batch upload status
"""

import os
import sys

def check_local_data():
    """Check local ChromaDB data"""
    print("🔍 Checking Local ChromaDB Data")
    print("=" * 40)
    
    # Check if chroma_data directory exists
    if os.path.exists("./chroma_data"):
        print("✅ Local ChromaDB data directory exists")
        
        # List files in chroma_data
        files = os.listdir("./chroma_data")
        print(f"📁 Files in chroma_data: {len(files)}")
        
        # Check for sqlite file
        if "chroma.sqlite3" in files:
            print("✅ chroma.sqlite3 found")
        else:
            print("❌ chroma.sqlite3 not found")
            
        # Check for collection directories
        collection_dirs = [f for f in files if os.path.isdir(os.path.join("./chroma_data", f))]
        print(f"📂 Collection directories: {len(collection_dirs)}")
        for dir_name in collection_dirs:
            print(f"  - {dir_name}")
    else:
        print("❌ Local ChromaDB data directory not found")

def check_batch_upload_script():
    """Check the batch upload script"""
    print("\n🔍 Checking Batch Upload Script")
    print("=" * 40)
    
    if os.path.exists("batch_upload_to_cloud.py"):
        print("✅ batch_upload_to_cloud.py exists")
        
        # Read the script to understand batch size
        with open("batch_upload_to_cloud.py", "r") as f:
            content = f.read()
            
        if "batch_size=25" in content:
            print("📦 Batch size: 25 documents")
        if "documents_ultra_optimized" in content:
            print("📋 Target collection: documents_ultra_optimized")
    else:
        print("❌ batch_upload_to_cloud.py not found")

def estimate_batches():
    """Estimate how many batches should exist"""
    print("\n🔍 Estimating Expected Batches")
    print("=" * 40)
    
    # Try to get document count from existing scripts
    try:
        # Import and run the ultra optimized count script
        sys.path.append(".")
        from check_ultra_optimized_count import check_ultra_optimized_count
        
        total_docs = check_ultra_optimized_count()
        
        if total_docs > 0:
            batch_size = 25
            expected_batches = (total_docs + batch_size - 1) // batch_size
            
            print(f"📊 Total documents: {total_docs:,}")
            print(f"📦 Batch size: {batch_size}")
            print(f"📈 Expected batches: {expected_batches}")
            
            # Calculate document ranges for each batch
            print(f"\n📋 Expected batch ranges:")
            for i in range(1, min(expected_batches + 1, 11)):  # Show first 10 batches
                start_doc = (i - 1) * batch_size + 1
                end_doc = min(i * batch_size, total_docs)
                print(f"  Batch {i}: documents {start_doc}-{end_doc}")
            
            if expected_batches > 10:
                print(f"  ... and {expected_batches - 10} more batches")
                
            return expected_batches, total_docs
        else:
            print("❌ Could not determine document count")
            return 0, 0
            
    except Exception as e:
        print(f"❌ Error estimating batches: {e}")
        return 0, 0

def check_cloud_connection():
    """Check if we can connect to cloud"""
    print("\n🔍 Checking Cloud Connection")
    print("=" * 40)
    
    try:
        # Try to import and test cloud connection
        from chroma_cloud_config import test_cloud_connection
        
        if test_cloud_connection():
            print("✅ Cloud connection successful")
            return True
        else:
            print("❌ Cloud connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing cloud connection: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Batch Upload Status Checker")
    print("=" * 50)
    
    # Check local data
    check_local_data()
    
    # Check batch upload script
    check_batch_upload_script()
    
    # Estimate batches
    expected_batches, total_docs = estimate_batches()
    
    # Check cloud connection
    cloud_connected = check_cloud_connection()
    
    # Summary
    print("\n📊 Summary")
    print("=" * 40)
    print(f"📈 Total documents: {total_docs:,}")
    print(f"📦 Expected batches: {expected_batches}")
    print(f"🌐 Cloud connection: {'✅ Connected' if cloud_connected else '❌ Failed'}")
    
    if expected_batches > 0:
        print(f"\n💡 Next steps:")
        if cloud_connected:
            print("  1. Run batch_upload_to_cloud.py to upload batches")
            print("  2. Check cloud for uploaded batch collections")
        else:
            print("  1. Fix cloud connection first")
            print("  2. Then run batch upload script")
    else:
        print("\n⚠️  No documents found to upload")

if __name__ == "__main__":
    main()

