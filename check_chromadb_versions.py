#!/usr/bin/env python3
"""
Check all ChromaDB versions and database formats
"""

import os
import sqlite3
import json
from pathlib import Path
import chromadb
from chromadb.config import Settings

def check_chromadb_package_versions():
    """Check ChromaDB package versions"""
    print("🔍 ChromaDB Package Versions")
    print("=" * 60)
    
    try:
        import chromadb
        print(f"📋 ChromaDB: {chromadb.__version__}")
    except Exception as e:
        print(f"❌ Error getting ChromaDB version: {e}")
    
    try:
        import chroma_hnswlib
        print(f"📋 Chroma HNSWLib: {chroma_hnswlib.__version__}")
    except Exception as e:
        print(f"❌ Error getting HNSWLib version: {e}")
    
    try:
        import llama_index_vector_stores_chroma
        print(f"📋 LlamaIndex Chroma: {llama_index_vector_stores_chroma.__version__}")
    except Exception as e:
        print(f"❌ Error getting LlamaIndex Chroma version: {e}")

def check_database_versions():
    """Check database versions in all ChromaDB directories"""
    print("\n🔍 ChromaDB Database Versions")
    print("=" * 60)
    
    chroma_dirs = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and 'chroma' in item.lower():
            chroma_dirs.append(item)
    
    print(f"📊 Found {len(chroma_dirs)} ChromaDB directories:")
    
    for chroma_dir in sorted(chroma_dirs):
        print(f"\n📋 Directory: {chroma_dir}")
        
        # Check if it's a valid ChromaDB directory
        sqlite_file = os.path.join(chroma_dir, 'chroma.sqlite3')
        if os.path.exists(sqlite_file):
            try:
                conn = sqlite3.connect(sqlite_file)
                cursor = conn.cursor()
                
                # Check migrations table for version info
                try:
                    cursor.execute("SELECT version FROM migrations ORDER BY version DESC LIMIT 1")
                    latest_migration = cursor.fetchone()
                    if latest_migration:
                        print(f"  📊 Latest migration: {latest_migration[0]}")
                except:
                    print(f"  ❌ No migrations table found")
                
                # Check collections table
                try:
                    cursor.execute("SELECT COUNT(*) FROM collections")
                    collection_count = cursor.fetchone()[0]
                    print(f"  📊 Collections: {collection_count}")
                except:
                    print(f"  ❌ No collections table found")
                
                # Check embeddings table
                try:
                    cursor.execute("SELECT COUNT(*) FROM embeddings")
                    embedding_count = cursor.fetchone()[0]
                    print(f"  📊 Embeddings: {embedding_count:,}")
                except:
                    print(f"  ❌ No embeddings table found")
                
                # Check fulltext search table
                try:
                    cursor.execute("SELECT COUNT(*) FROM embedding_fulltext_search_content")
                    content_count = cursor.fetchone()[0]
                    print(f"  📊 Fulltext content: {content_count:,}")
                except:
                    print(f"  ❌ No fulltext search table found")
                
                conn.close()
                
            except Exception as e:
                print(f"  ❌ Error reading database: {e}")
        else:
            print(f"  ❌ No chroma.sqlite3 file found")

def check_chromadb_client_versions():
    """Check ChromaDB client versions by testing connections"""
    print("\n🔍 ChromaDB Client Compatibility")
    print("=" * 60)
    
    chroma_dirs = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and 'chroma_data' in item.lower():
            chroma_dirs.append(item)
    
    for chroma_dir in sorted(chroma_dirs):
        print(f"\n📋 Testing: {chroma_dir}")
        
        try:
            client = chromadb.PersistentClient(
                path=chroma_dir,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Try to get collections
            collections = client.list_collections()
            print(f"  ✅ Connected successfully")
            print(f"  📊 Collections: {len(collections)}")
            
            for collection in collections:
                try:
                    count = collection.count()
                    print(f"    - {collection.name}: {count:,} documents")
                except Exception as e:
                    print(f"    - {collection.name}: Error getting count - {e}")
                    
        except Exception as e:
            print(f"  ❌ Connection failed: {e}")

def check_file_sizes():
    """Check file sizes of ChromaDB directories"""
    print("\n🔍 ChromaDB Directory Sizes")
    print("=" * 60)
    
    chroma_dirs = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and 'chroma' in item.lower():
            chroma_dirs.append(item)
    
    for chroma_dir in sorted(chroma_dirs):
        try:
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(chroma_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            size_mb = total_size / (1024 * 1024)
            print(f"📋 {chroma_dir}: {size_mb:.2f} MB ({file_count:,} files)")
            
        except Exception as e:
            print(f"❌ Error calculating size for {chroma_dir}: {e}")

def main():
    """Main function"""
    print("🚀 ChromaDB Version Analysis")
    print("=" * 60)
    
    # Check package versions
    check_chromadb_package_versions()
    
    # Check database versions
    check_database_versions()
    
    # Check client compatibility
    check_chromadb_client_versions()
    
    # Check file sizes
    check_file_sizes()
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 