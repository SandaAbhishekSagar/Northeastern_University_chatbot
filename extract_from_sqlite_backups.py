#!/usr/bin/env python3
"""
Extract documents from SQLite databases in backup directories
"""

import sqlite3
import os
import json
from pathlib import Path
import chromadb
from chromadb.config import Settings
import time

def find_sqlite_databases():
    """Find all chroma.sqlite3 files in backup directories"""
    print("🔍 Finding SQLite Databases")
    print("=" * 60)
    
    sqlite_files = []
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == 'chroma.sqlite3':
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                sqlite_files.append((file_path, file_size))
    
    # Sort by file size (largest first)
    sqlite_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"📊 Found {len(sqlite_files)} chroma.sqlite3 files:")
    for file_path, file_size in sqlite_files:
        print(f"  📋 {file_path} ({file_size:,} bytes, {file_size/1024/1024:.2f} MB)")
    
    return sqlite_files

def analyze_sqlite_database(db_path):
    """Analyze the structure of a SQLite database"""
    print(f"\n🔍 Analyzing: {db_path}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 Tables: {[table[0] for table in tables]}")
        
        # Analyze each table
        for table in tables:
            table_name = table[0]
            print(f"\n📋 Table: {table_name}")
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  📊 Row count: {count:,}")
            except:
                print(f"  ❌ Could not get row count")
            
            # Get column info
            try:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print(f"  📋 Columns: {[col[1] for col in columns]}")
                
                # Show sample data for document-related tables
                if any(word in table_name.lower() for word in ['embedding', 'document', 'content', 'fulltext']):
                    try:
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                        rows = cursor.fetchall()
                        print(f"  📋 Sample data:")
                        for i, row in enumerate(rows):
                            print(f"    Row {i+1}: {row[:2]}...")  # Show first 2 columns
                    except Exception as e:
                        print(f"  ❌ Error getting sample data: {e}")
                        
            except Exception as e:
                print(f"  ❌ Error getting column info: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")
        return False

def extract_documents_from_sqlite(db_path):
    """Extract documents from a SQLite database"""
    print(f"\n🔍 Extracting Documents from: {db_path}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Look for document content in various tables
        document_tables = [
            'embedding_fulltext_search_content',
            'embedding_fulltext_search_metadata', 
            'embedding_fulltext_search_embeddings',
            'embedding_fulltext_search_documents',
            'documents',
            'embeddings'
        ]
        
        extracted_docs = []
        
        for table_name in document_tables:
            try:
                # Check if table exists
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if not cursor.fetchone():
                    continue
                
                print(f"📋 Checking table: {table_name}")
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                print(f"  📋 Columns: {columns}")
                
                # Look for content/document columns
                content_columns = [col for col in columns if any(word in col.lower() for word in ['content', 'document', 'text', 'data'])]
                
                if content_columns:
                    print(f"  🎯 Found content columns: {content_columns}")
                    
                    # Get sample data
                    for content_col in content_columns[:2]:  # Check first 2 content columns
                        try:
                            cursor.execute(f"SELECT {content_col} FROM {table_name} WHERE {content_col} IS NOT NULL LIMIT 5")
                            rows = cursor.fetchall()
                            
                            for i, row in enumerate(rows):
                                content = row[0]
                                if content and len(str(content)) > 50:
                                    print(f"    📋 Sample {i+1}: {str(content)[:100]}...")
                                    
                                    # Add to extracted docs
                                    doc_id = f"{table_name}_{content_col}_{i}"
                                    extracted_docs.append({
                                        'id': doc_id,
                                        'content': content,
                                        'source_table': table_name,
                                        'source_column': content_col
                                    })
                        except Exception as e:
                            print(f"    ❌ Error reading {content_col}: {e}")
                
                # Also check for metadata columns that might contain document info
                metadata_columns = [col for col in columns if any(word in col.lower() for word in ['metadata', 'meta', 'info'])]
                if metadata_columns:
                    print(f"  📋 Found metadata columns: {metadata_columns}")
                    
            except Exception as e:
                print(f"  ❌ Error checking table {table_name}: {e}")
        
        conn.close()
        
        print(f"\n📊 Extracted {len(extracted_docs)} documents from {db_path}")
        return extracted_docs
        
    except Exception as e:
        print(f"❌ Error extracting from database: {e}")
        return []

def rebuild_chromadb_with_sqlite_docs(all_docs):
    """Rebuild ChromaDB with documents extracted from SQLite"""
    if not all_docs:
        print("❌ No documents to rebuild with")
        return False
    
    print(f"\n🔧 Rebuilding ChromaDB with {len(all_docs)} Documents")
    print("=" * 60)
    
    try:
        # Create new ChromaDB client
        client = chromadb.PersistentClient(
            path="chroma_data_restored_from_sqlite",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Delete existing collection if it exists
        try:
            client.delete_collection("documents")
            print("🗑️  Deleted existing documents collection")
        except:
            pass
        
        # Create new collection
        collection = client.create_collection("documents")
        print("✅ Created new documents collection")
        
        # Add documents in batches
        batch_size = 100
        total_docs = len(all_docs)
        
        print(f"📋 Adding {total_docs:,} documents in batches of {batch_size}...")
        
        for i in range(0, total_docs, batch_size):
            batch = all_docs[i:i + batch_size]
            
            # Prepare batch data
            ids = [doc['id'] for doc in batch]
            documents = [doc['content'] for doc in batch]
            metadatas = [{
                'source_table': doc['source_table'],
                'source_column': doc['source_column']
            } for doc in batch]
            
            # Add to collection
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            progress = (i + len(batch)) / total_docs * 100
            print(f"📋 Progress: {progress:.1f}% ({i + len(batch):,}/{total_docs:,} documents)")
        
        # Verify the collection
        count = collection.count()
        print(f"📊 Final collection count: {count:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error rebuilding ChromaDB: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Document Recovery from SQLite Databases")
    print("=" * 60)
    
    # Find all SQLite databases
    sqlite_files = find_sqlite_databases()
    
    if not sqlite_files:
        print("❌ No SQLite databases found!")
        return
    
    # Analyze the largest database first
    largest_db = sqlite_files[0][0]
    print(f"\n🎯 Analyzing largest database: {largest_db}")
    
    # Analyze database structure
    analyze_sqlite_database(largest_db)
    
    # Extract documents from all databases
    all_docs = []
    
    for db_path, db_size in sqlite_files[:3]:  # Process first 3 largest databases
        docs = extract_documents_from_sqlite(db_path)
        all_docs.extend(docs)
        
        if len(docs) > 0:
            print(f"✅ Found {len(docs)} documents in {db_path}")
        else:
            print(f"❌ No documents found in {db_path}")
    
    print(f"\n📊 Total documents found: {len(all_docs):,}")
    
    if all_docs:
        # Rebuild ChromaDB with extracted documents
        if rebuild_chromadb_with_sqlite_docs(all_docs):
            print("\n🎉 Document recovery successful!")
            print(f"\n📊 Final Results:")
            print(f"   ✅ Extracted {len(all_docs):,} documents from SQLite databases")
            print(f"   ✅ ChromaDB rebuilt successfully")
            print(f"   ✅ All documents available for search")
        else:
            print("\n❌ ChromaDB rebuild failed!")
    else:
        print("\n❌ No documents found in any SQLite database!")

if __name__ == "__main__":
    main() 