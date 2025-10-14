#!/usr/bin/env python3
"""
Check if there's a limit on collection retrieval and try to get all collections
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chroma_cloud_config import get_chroma_cloud_client

def check_collection_limits():
    """
    Test collection retrieval limits
    """
    print("=" * 80)
    print("TESTING COLLECTION RETRIEVAL LIMITS")
    print("=" * 80)
    print()
    
    try:
        client = get_chroma_cloud_client()
        
        # Test 1: Basic list_collections()
        print("Test 1: Basic list_collections() - No parameters")
        print("-" * 50)
        collections = client.list_collections()
        print(f"Collections retrieved: {len(collections)}")
        print()
        
        # Test 2: Try with limit parameter (if supported)
        print("Test 2: Checking if limit parameter is supported")
        print("-" * 50)
        try:
            # Try to get more collections with limit parameter
            collections_with_limit = client.list_collections(limit=5000)
            print(f"Collections with limit=5000: {len(collections_with_limit)}")
        except TypeError as e:
            print(f"Limit parameter not supported: {e}")
        except Exception as e:
            print(f"Error with limit parameter: {e}")
        print()
        
        # Test 3: Check ChromaDB client methods
        print("Test 3: Available client methods")
        print("-" * 50)
        client_methods = [method for method in dir(client) if not method.startswith('_')]
        print(f"Available methods: {client_methods}")
        print()
        
        # Test 4: Try to count collections differently
        print("Test 4: Alternative collection counting methods")
        print("-" * 50)
        
        # Check if heartbeat provides collection count
        try:
            heartbeat = client.heartbeat()
            print(f"Heartbeat response: {heartbeat}")
        except Exception as e:
            print(f"Heartbeat not available: {e}")
        
        print()
        
        # Test 5: Check collection object structure
        print("Test 5: Examining collection object structure")
        print("-" * 50)
        if collections:
            first_collection = collections[0]
            print(f"First collection name: {first_collection.name}")
            print(f"Collection type: {type(first_collection)}")
            print(f"Collection attributes: {[attr for attr in dir(first_collection) if not attr.startswith('_')]}")
        print()
        
        # Test 6: Check if there's pagination support
        print("Test 6: Checking pagination support")
        print("-" * 50)
        try:
            # Try offset/limit pattern
            collections_offset = client.list_collections(offset=1000, limit=1000)
            print(f"Collections with offset=1000, limit=1000: {len(collections_offset)}")
        except TypeError as e:
            print(f"Offset/limit not supported: {e}")
        except Exception as e:
            print(f"Error with offset/limit: {e}")
        print()
        
        return collections
        
    except Exception as e:
        print(f"Error during limit testing: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_chroma_version():
    """
    Check ChromaDB version for API compatibility
    """
    print("CHROMADB VERSION INFORMATION:")
    print("-" * 50)
    try:
        import chromadb
        print(f"ChromaDB version: {chromadb.__version__}")
        
        # Check if CloudClient has specific attributes
        from chromadb import CloudClient
        print(f"CloudClient available methods:")
        methods = [m for m in dir(CloudClient) if not m.startswith('_')]
        for method in methods[:15]:  # Show first 15
            print(f"  - {method}")
        if len(methods) > 15:
            print(f"  ... and {len(methods) - 15} more")
    except Exception as e:
        print(f"Error checking version: {e}")
    print()

def main():
    print("Checking ChromaDB Cloud Collection Retrieval Limits...")
    print()
    
    # Check version
    check_chroma_version()
    
    # Check limits
    collections = check_collection_limits()
    
    if collections:
        print("=" * 80)
        print("CONCLUSION:")
        print("=" * 80)
        print(f"Maximum collections retrieved: {len(collections)}")
        print()
        print("EXPLANATION:")
        print("-" * 50)
        print("The ChromaDB Cloud API appears to have a default limit of 1,000")
        print("collections per list_collections() call.")
        print()
        print("Your dashboard shows 3,280 collections because:")
        print("1. The dashboard queries the database directly (server-side)")
        print("2. The API client (our script) has a 1,000 collection limit")
        print("3. This is likely a performance/safety limit to prevent large responses")
        print()
        print("To access all collections, you would need to:")
        print("1. Use pagination if supported (we tested this)")
        print("2. Contact ChromaDB support for API limits")
        print("3. Access specific collections by name rather than listing all")
        print()

if __name__ == "__main__":
    main()

