#!/usr/bin/env python3
"""
Simple script to check Chroma Cloud newtest database collections
- Count total collections
- Verify retrieval completeness
- Analyze collection sizes
"""

import os
import sys
import time
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from chroma_cloud_config import get_chroma_cloud_client
    print("ChromaDB cloud modules imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def check_newtest_collections():
    """
    Check newtest database collections
    """
    print("=" * 80)
    print("COMPREHENSIVE NEWTEST DATABASE COLLECTION ANALYSIS")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Get cloud client for newtest database
        print("Connecting to Chroma Cloud newtest database...")
        client = get_chroma_cloud_client()
        print("Connected successfully")
        print()
        
        # Get all collections
        print("Retrieving all collections...")
        start_time = time.time()
        collections = client.list_collections()
        retrieval_time = time.time() - start_time
        
        print(f"Retrieved {len(collections)} collections in {retrieval_time:.2f} seconds")
        print()
        
        # Basic collection info
        print("BASIC COLLECTION INFORMATION:")
        print("-" * 50)
        print(f"Total Collections Found: {len(collections)}")
        print(f"Retrieval Time: {retrieval_time:.2f} seconds")
        print(f"Average Time per Collection: {retrieval_time/len(collections):.3f} seconds")
        print()
        
        # Detailed analysis
        print("DETAILED COLLECTION ANALYSIS:")
        print("-" * 50)
        
        total_documents = 0
        batch_collections = []
        document_collections = []
        other_collections = []
        
        collection_details = []
        
        for i, collection in enumerate(collections):
            try:
                # Get collection name and basic info
                collection_name = collection.name
                doc_count = collection.count()
                
                total_documents += doc_count
                
                # Categorize collections
                if 'batch_' in collection_name.lower():
                    batch_collections.append(collection_name)
                elif 'document' in collection_name.lower():
                    document_collections.append(collection_name)
                else:
                    other_collections.append(collection_name)
                
                collection_details.append({
                    'name': collection_name,
                    'documents': doc_count
                })
                
                # Print every 100th collection for progress
                if (i + 1) % 100 == 0:
                    print(f"  Processed {i + 1}/{len(collections)} collections...")
                    
            except Exception as e:
                print(f"Error processing collection {i}: {e}")
                continue
        
        print(f"Processed all {len(collections)} collections")
        print()
        
        # Summary statistics
        print("SUMMARY STATISTICS:")
        print("-" * 50)
        print(f"Total Collections: {len(collections):,}")
        print(f"Total Documents: {total_documents:,}")
        print(f"Average Documents per Collection: {total_documents/len(collections):.1f}")
        print()
        
        # Collection type breakdown
        print("COLLECTION TYPE BREAKDOWN:")
        print("-" * 50)
        print(f"Batch Collections: {len(batch_collections)}")
        print(f"Document Collections: {len(document_collections)}")
        print(f"Other Collections: {len(other_collections)}")
        print()
        
        # Top 10 largest collections
        print("TOP 10 LARGEST COLLECTIONS:")
        print("-" * 50)
        sorted_collections = sorted(collection_details, key=lambda x: x['documents'], reverse=True)
        for i, col in enumerate(sorted_collections[:10]):
            print(f"{i+1:2d}. {col['name']:<40} {col['documents']:>8,} docs")
        print()
        
        # Empty collections check
        empty_collections = [col for col in collection_details if col['documents'] == 0]
        if empty_collections:
            print("EMPTY COLLECTIONS:")
            print("-" * 50)
            print(f"Found {len(empty_collections)} empty collections:")
            for col in empty_collections[:10]:  # Show first 10
                print(f"  - {col['name']}")
            if len(empty_collections) > 10:
                print(f"  ... and {len(empty_collections) - 10} more")
            print()
        
        # Batch collection analysis
        if batch_collections:
            print("BATCH COLLECTION ANALYSIS:")
            print("-" * 50)
            batch_docs = sum(col['documents'] for col in collection_details if 'batch_' in col['name'].lower())
            print(f"Total Batch Collections: {len(batch_collections)}")
            print(f"Total Batch Documents: {batch_docs:,}")
            print(f"Average Batch Size: {batch_docs/len(batch_collections):.1f} docs")
            
            # Show batch size distribution
            batch_sizes = [col['documents'] for col in collection_details if 'batch_' in col['name'].lower()]
            if batch_sizes:
                print(f"Largest Batch: {max(batch_sizes):,} docs")
                print(f"Smallest Batch: {min(batch_sizes):,} docs")
            print()
        
        # Retrieval completeness check
        print("RETRIEVAL COMPLETENESS CHECK:")
        print("-" * 50)
        print(f"Collections Retrieved: {len(collections)}")
        print(f"Collections Processed: {len(collection_details)}")
        print(f"Success Rate: {len(collection_details)/len(collections)*100:.1f}%")
        
        if len(collection_details) == len(collections):
            print("All collections retrieved and processed successfully!")
        else:
            print(f"{len(collections) - len(collection_details)} collections failed to process")
        print()
        
        # Performance metrics
        print("PERFORMANCE METRICS:")
        print("-" * 50)
        print(f"Total Retrieval Time: {retrieval_time:.2f} seconds")
        print(f"Collections per Second: {len(collections)/retrieval_time:.1f}")
        print(f"Documents per Second: {total_documents/retrieval_time:.0f}")
        print()
        
        # Storage estimate
        print("STORAGE ESTIMATES:")
        print("-" * 50)
        estimated_storage_mb = total_documents * 0.015  # Rough estimate
        estimated_storage_gb = estimated_storage_mb / 1024
        print(f"Estimated Storage: ~{estimated_storage_mb:.1f} MB ({estimated_storage_gb:.2f} GB)")
        print()
        
        return {
            'total_collections': len(collections),
            'total_documents': total_documents,
            'retrieval_time': retrieval_time,
            'success_rate': len(collection_details)/len(collections)*100,
            'collection_details': collection_details
        }
        
    except Exception as e:
        print(f"Error during collection analysis: {e}")
        return None

def test_collection_access():
    """
    Test collection access and retrieval
    """
    print("TESTING COLLECTION ACCESS:")
    print("-" * 50)
    
    try:
        client = get_chroma_cloud_client()
        
        # Test 1: Basic list_collections()
        print("Test 1: Basic list_collections()")
        start_time = time.time()
        collections = client.list_collections()
        basic_time = time.time() - start_time
        print(f"  Retrieved {len(collections)} collections in {basic_time:.2f}s")
        
        # Test 2: Check sample collection access
        print("\nTest 2: Sample collection access")
        sample_collections = collections[:5]  # Test first 5
        for i, collection in enumerate(sample_collections):
            try:
                count = collection.count()
                print(f"  Collection {i+1}: {collection.name} - {count:,} documents")
            except Exception as e:
                print(f"  Collection {i+1}: {collection.name} - count error: {e}")
        
        print(f"\nAll access tests completed successfully")
        print(f"Total collections accessible: {len(collections)}")
        
    except Exception as e:
        print(f"Error during access tests: {e}")

def main():
    """
    Main function to run collection analysis
    """
    print("Starting comprehensive newtest database collection analysis...")
    print()
    
    # Run comprehensive analysis
    results = check_newtest_collections()
    
    if results:
        print("=" * 80)
        print("FINAL SUMMARY:")
        print("=" * 80)
        print(f"Total Collections: {results['total_collections']:,}")
        print(f"Total Documents: {results['total_documents']:,}")
        print(f"Retrieval Time: {results['retrieval_time']:.2f} seconds")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print()
        
        # Test collection access
        test_collection_access()
        
        print()
        print("Analysis completed successfully!")
        
        # Recommendations
        print("\nRECOMMENDATIONS:")
        print("-" * 30)
        if results['success_rate'] == 100:
            print("All collections retrieved successfully - database is healthy")
        else:
            print("Some collections failed to process - check for corrupted data")
        
        if results['total_collections'] > 1000:
            print("Large number of collections - consider batch processing for operations")
        
        print("Regular monitoring recommended to track collection growth")
        
    else:
        print("Analysis failed - check connection and permissions")

if __name__ == "__main__":
    main()
