#!/usr/bin/env python3
"""
Extract a small sample of data from the backup database
"""

import sqlite3
import json
import os

def extract_sample_documents(backup_file: str, limit: int = 100):
    """Extract a small sample of documents"""
    print(f"📖 Extracting {limit} sample documents from: {backup_file}")
    
    documents = []
    
    try:
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        
        # Get sample documents from embeddings table
        cursor.execute("""
            SELECT id, vector, metadata, document 
            FROM embeddings
            WHERE document IS NOT NULL AND document != ''
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        print(f"📄 Found {len(rows)} sample documents")
        
        for i, row in enumerate(rows):
            doc_id, vector, metadata_json, content = row
            
            if not content or len(content.strip()) < 10:
                continue
            
            # Parse metadata
            try:
                metadata = json.loads(metadata_json) if metadata_json else {}
            except:
                metadata = {}
            
            # Extract URL and title
            url = metadata.get('source_url', '') or metadata.get('url', '')
            title = metadata.get('title', '') or metadata.get('file_name', '')
            
            # Filter for Northeastern University content
            content_lower = content.lower()
            title_lower = title.lower()
            url_lower = url.lower()
            
            if any(term in content_lower or term in title_lower or term in url_lower for term in [
                'northeastern', 'neu', 'northeastern.edu'
            ]):
                doc = {
                    'id': doc_id,
                    'content': content,
                    'metadata': {
                        'title': title,
                        'url': url,
                        'source_url': url,
                        'original_metadata': metadata
                    }
                }
                documents.append(doc)
                
                # Show progress
                if len(documents) % 10 == 0:
                    print(f"📝 Found {len(documents)} Northeastern documents so far...")
        
        conn.close()
        print(f"✅ Extracted {len(documents)} Northeastern University documents")
        return documents
        
    except Exception as e:
        print(f"❌ Error extracting documents: {e}")
        return []

def main():
    print("🔄 Extracting Sample Data from Backup")
    print("=" * 40)
    
    backup_file = "chroma_backups/chroma_backup_20250809_112404/chroma.sqlite3"
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return
    
    # Extract sample documents
    documents = extract_sample_documents(backup_file, 1000)
    
    if documents:
        print(f"\n📊 Sample Results:")
        print(f"Total documents found: {len(documents)}")
        
        # Show first few documents
        for i, doc in enumerate(documents[:5]):
            print(f"\n📄 Document {i+1}:")
            print(f"  Title: {doc['metadata']['title']}")
            print(f"  URL: {doc['metadata']['url']}")
            print(f"  Content preview: {doc['content'][:100]}...")
        
        # Save sample to file for inspection
        with open('sample_documents.json', 'w', encoding='utf-8') as f:
            json.dump(documents[:10], f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved first 10 documents to sample_documents.json")
        
    else:
        print("❌ No documents found")

if __name__ == "__main__":
    main()
