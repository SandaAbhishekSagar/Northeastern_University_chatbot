#!/usr/bin/env python3
"""
Retrieve ALL collections from ChromaDB Cloud using pagination
The API has a 1,000 collection limit per call, so we need to use offset/limit
"""

import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chroma_cloud_config import get_chroma_cloud_client

def get_all_collections_with_pagination():
    """
    Get all collections using pagination (offset/limit)
    """
    print("=" * 80)
    print("RETRIEVING ALL COLLECTIONS WITH PAGINATION")
    print("=" * 80)
    print()
    
    try:
        client = get_chroma_cloud_client()
        
        all_collections = []
        offset = 0
        limit = 1000  # Max allowed per request
        batch_num = 1
        
        print("Starting pagination retrieval...")
        print("-" * 50)
        
        while True:
            print(f"Batch {batch_num}: Fetching collections {offset} to {offset + limit}...")
            start_time = time.time()
            
            try:
                # Get collections with offset and limit
                batch_collections = client.list_collections(offset=offset, limit=limit)
                batch_time = time.time() - start_time
                
                if not batch_collections or len(batch_collections) == 0:
                    print(f"  No more collections found. Stopping.")
                    break
                
                print(f"  Retrieved {len(batch_collections)} collections in {batch_time:.2f}s")
                all_collections.extend(batch_collections)
                
                # If we got fewer than limit, we've reached the end
                if len(batch_collections) < limit:
                    print(f"  Retrieved {len(batch_collections)} < {limit}, reached end of data.")
                    break
                
                offset += limit
                batch_num += 1
                
                # Safety check - don't go beyond reasonable limits
                if batch_num > 10:  # Max 10,000 collections
                    print("  Safety limit reached (10 batches). Stopping.")
                    break
                    
            except Exception as e:
                if "Quota exceeded" in str(e):
                    print(f"  Quota limit hit: {e}")
                    break
                else:
                    print(f"  Error: {e}")
                    break
        
        print()
        print("=" * 80)
        print("RETRIEVAL COMPLETE")
        print("=" * 80)
        print(f"Total Collections Retrieved: {len(all_collections)}")
        print(f"Total Batches: {batch_num}")
        print()
        
        return all_collections
        
    except Exception as e:
        print(f"Error during pagination: {e}")
        import traceback
        traceback.print_exc()
        return []

def analyze_all_collections(collections):
    """
    Analyze all retrieved collections
    """
    if not collections:
        print("No collections to analyze")
        return
    
    print("=" * 80)
    print("ANALYZING ALL COLLECTIONS")
    print("=" * 80)
    print()
    
    total_documents = 0
    collection_details = []
    
    print("Counting documents in all collections...")
    print("-" * 50)
    
    for i, collection in enumerate(collections):
        try:
            doc_count = collection.count()
            total_documents += doc_count
            
            collection_details.append({
                'name': collection.name,
                'documents': doc_count
            })
            
            # Progress update every 100 collections
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(collections)} collections...")
                
        except Exception as e:
            print(f"  Error counting collection {collection.name}: {e}")
    
    print(f"Completed processing {len(collections)} collections")
    print()
    
    # Summary
    print("=" * 80)
    print("COMPLETE DATABASE SUMMARY")
    print("=" * 80)
    print(f"Total Collections: {len(collections):,}")
    print(f"Total Documents: {total_documents:,}")
    print(f"Average Documents per Collection: {total_documents/len(collections):.1f}")
    print()
    
    # Top 10 largest collections
    print("TOP 10 LARGEST COLLECTIONS:")
    print("-" * 50)
    sorted_collections = sorted(collection_details, key=lambda x: x['documents'], reverse=True)
    for i, col in enumerate(sorted_collections[:10]):
        print(f"{i+1:2d}. {col['name']:<50} {col['documents']:>10,} docs")
    print()
    
    # Empty collections
    empty_collections = [col for col in collection_details if col['documents'] == 0]
    if empty_collections:
        print(f"EMPTY COLLECTIONS: {len(empty_collections)}")
        print("-" * 50)
        for col in empty_collections[:20]:
            print(f"  - {col['name']}")
        if len(empty_collections) > 20:
            print(f"  ... and {len(empty_collections) - 20} more")
        print()
    
    # Storage estimate
    estimated_storage_mb = total_documents * 0.015
    estimated_storage_gb = estimated_storage_mb / 1024
    print("STORAGE ESTIMATE:")
    print("-" * 50)
    print(f"Estimated Storage: ~{estimated_storage_mb:.1f} MB ({estimated_storage_gb:.2f} GB)")
    print()

def main():
    print("Fetching ALL collections from ChromaDB Cloud...")
    print("(This may take a few seconds due to pagination)")
    print()
    
    # Get all collections
    all_collections = get_all_collections_with_pagination()
    
    if all_collections:
        # Analyze them
        analyze_all_collections(all_collections)
        
        print("=" * 80)
        print("EXPLANATION:")
        print("=" * 80)
        print("ChromaDB Cloud API has a limit of 1,000 collections per API call.")
        print("Your dashboard shows the TOTAL count (server-side).")
        print("Our script uses pagination to retrieve ALL collections in batches.")
        print()
        print(f"Retrieved {len(all_collections):,} collections successfully!")
        print()
    else:
        print("Failed to retrieve collections. Check the errors above.")

if __name__ == "__main__":
    main()

