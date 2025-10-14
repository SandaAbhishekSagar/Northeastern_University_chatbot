#!/usr/bin/env python3
"""
Quick batch upload status check
Works without full environment setup
"""

import os
import sqlite3
import json

def check_sqlite_collections():
    """Check collections in SQLite database"""
    print("🔍 Checking SQLite Database for Collections")
    print("=" * 50)
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect("chroma_data/chroma.sqlite3")
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 Found {len(tables)} tables in database:")
        
        batch_tables = []
        collection_tables = []
        
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            if "batch" in table_name.lower():
                batch_tables.append(table_name)
            elif "collection" in table_name.lower():
                collection_tables.append(table_name)
        
        # Check for collections table
        if collection_tables:
            print(f"\n📊 Collections in database:")
            for table in collection_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"  - {table}: {count} records")
        
        # Check for batch tables
        if batch_tables:
            print(f"\n📦 Batch tables found:")
            for table in batch_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"  - {table}: {count} records")
        else:
            print(f"\n❌ No batch tables found")
        
        conn.close()
        return batch_tables, collection_tables
        
    except Exception as e:
        print(f"❌ Error checking SQLite database: {e}")
        return [], []

def check_file_system_batches():
    """Check for batch collections in file system"""
    print(f"\n🔍 Checking File System for Batch Collections")
    print("=" * 50)
    
    try:
        # Look for batch collection directories
        batch_dirs = []
        for item in os.listdir("chroma_data"):
            if "batch" in item.lower():
                batch_dirs.append(item)
        
        if batch_dirs:
            print(f"📦 Found {len(batch_dirs)} batch directories:")
            for batch_dir in batch_dirs:
                print(f"  - {batch_dir}")
        else:
            print(f"❌ No batch directories found")
        
        return batch_dirs
        
    except Exception as e:
        print(f"❌ Error checking file system: {e}")
        return []

def estimate_expected_batches():
    """Estimate expected batches based on file count"""
    print(f"\n📊 Estimating Expected Batches")
    print("=" * 50)
    
    try:
        # Count files in chroma_data (excluding sqlite file)
        files = os.listdir("chroma_data")
        collection_dirs = [f for f in files if os.path.isdir(os.path.join("chroma_data", f)) and f != "chroma.sqlite3"]
        
        print(f"📁 Collection directories: {len(collection_dirs)}")
        
        # Estimate documents based on directory count
        # Each directory typically represents a document
        estimated_docs = len(collection_dirs)
        batch_size = 25
        expected_batches = (estimated_docs + batch_size - 1) // batch_size
        
        print(f"📈 Estimated documents: {estimated_docs:,}")
        print(f"📦 Batch size: {batch_size}")
        print(f"📊 Expected batches: {expected_batches}")
        
        return estimated_docs, expected_batches
        
    except Exception as e:
        print(f"❌ Error estimating batches: {e}")
        return 0, 0

def check_cloud_connection():
    """Check if cloud connection is possible"""
    print(f"\n🌐 Checking Cloud Connection")
    print("=" * 50)
    
    try:
        # Check if chroma CLI is available
        result = os.system("chroma --version > nul 2>&1")
        if result == 0:
            print("✅ Chroma CLI is available")
            
            # Try to list cloud collections
            result = os.system("chroma list --db newtest > nul 2>&1")
            if result == 0:
                print("✅ Cloud connection successful")
                return True
            else:
                print("❌ Cloud connection failed")
                return False
        else:
            print("❌ Chroma CLI not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking cloud connection: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Quick Batch Upload Status Check")
    print("=" * 60)
    
    # Check SQLite database
    batch_tables, collection_tables = check_sqlite_collections()
    
    # Check file system
    batch_dirs = check_file_system_batches()
    
    # Estimate expected batches
    estimated_docs, expected_batches = estimate_expected_batches()
    
    # Check cloud connection
    cloud_connected = check_cloud_connection()
    
    # Summary
    print(f"\n📊 Summary")
    print("=" * 50)
    print(f"📈 Estimated documents: {estimated_docs:,}")
    print(f"📦 Expected batches: {expected_batches}")
    print(f"📋 Batch tables in DB: {len(batch_tables)}")
    print(f"📁 Batch directories: {len(batch_dirs)}")
    print(f"🌐 Cloud connection: {'✅ Connected' if cloud_connected else '❌ Failed'}")
    
    # Analysis
    if expected_batches > 0:
        if len(batch_tables) == 0 and len(batch_dirs) == 0:
            print(f"\n⚠️  No batch collections found locally")
            print(f"   This suggests batch upload has not been attempted yet")
            print(f"   Expected batches: {list(range(1, expected_batches + 1))}")
        elif len(batch_tables) > 0 or len(batch_dirs) > 0:
            print(f"\n📦 Some batch collections found locally")
            print(f"   This suggests batch upload was attempted")
            print(f"   Check cloud for uploaded batches")
        else:
            print(f"\n❓ Unable to determine batch status")
    
    if not cloud_connected:
        print(f"\n💡 To check cloud status:")
        print(f"  1. Ensure Chroma CLI is installed")
        print(f"  2. Check cloud credentials")
        print(f"  3. Try: chroma list --db newtest")
    
    print(f"\n🎯 Next Steps:")
    if expected_batches > 0 and len(batch_tables) == 0:
        print(f"  1. Run batch upload script: python batch_upload_to_cloud.py")
        print(f"  2. Monitor upload progress")
        print(f"  3. Check cloud for uploaded batches")
    elif cloud_connected:
        print(f"  1. Check cloud collections: chroma list --db newtest")
        print(f"  2. Compare with expected batches")
    else:
        print(f"  1. Fix cloud connection first")
        print(f"  2. Then check batch upload status")

if __name__ == "__main__":
    main()

