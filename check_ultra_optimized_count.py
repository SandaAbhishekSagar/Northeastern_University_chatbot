#!/usr/bin/env python3
"""
Check the count of ultra-optimized documents
"""

import chromadb

def check_ultra_optimized_count():
    """Check how many ultra-optimized documents we have"""
    
    try:
        # Connect to local ChromaDB
        client = chromadb.PersistentClient(path="./chroma_data")
        
        # Get the ultra-optimized collection
        collection = client.get_collection("documents_ultra_optimized")
        
        # Get count
        count = collection.count()
        
        print(f"📊 Ultra-optimized documents in local ChromaDB: {count:,}")
        
        # Also check the original documents collection for comparison
        try:
            original_collection = client.get_collection("documents")
            original_count = original_collection.count()
            print(f"📊 Original documents collection: {original_count:,}")
            print(f"📈 Increase due to chunking: {count - original_count:,} documents")
        except:
            print("📊 Original documents collection not found")
        
        return count
        
    except Exception as e:
        print(f"❌ Error checking collection: {e}")
        return 0

if __name__ == "__main__":
    print("🔍 Checking ultra-optimized documents count...")
    print("=" * 50)
    count = check_ultra_optimized_count()
    print("=" * 50)
