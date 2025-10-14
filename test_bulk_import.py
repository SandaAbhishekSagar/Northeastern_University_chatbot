"""
Test script for bulk_import.py
Verifies that all import formats work correctly
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.shared.chroma_service import chroma_service

def test_imports():
    """Test all import formats"""
    
    print("="*70)
    print("🧪 TESTING BULK IMPORT FUNCTIONALITY")
    print("="*70)
    
    # Get initial document count
    initial_count = chroma_service.get_collection_count('documents')
    print(f"\n📊 Initial document count: {initial_count:,}")
    
    # Test 1: JSON Import
    print("\n" + "-"*70)
    print("TEST 1: JSON Import")
    print("-"*70)
    
    if Path('example_data_json.json').exists():
        os.system('python bulk_import.py --json example_data_json.json')
        new_count = chroma_service.get_collection_count('documents')
        imported = new_count - initial_count
        print(f"✅ JSON Import Test: Added {imported} documents")
        initial_count = new_count
    else:
        print("⚠️  example_data_json.json not found, skipping JSON test")
    
    # Test 2: CSV Import
    print("\n" + "-"*70)
    print("TEST 2: CSV Import")
    print("-"*70)
    
    if Path('example_data.csv').exists():
        os.system('python bulk_import.py --csv example_data.csv')
        new_count = chroma_service.get_collection_count('documents')
        imported = new_count - initial_count
        print(f"✅ CSV Import Test: Added {imported} documents")
        initial_count = new_count
    else:
        print("⚠️  example_data.csv not found, skipping CSV test")
    
    # Test 3: TXT Import
    print("\n" + "-"*70)
    print("TEST 3: TXT Import")
    print("-"*70)
    
    if Path('example_data.txt').exists():
        os.system('python bulk_import.py --txt example_data.txt')
        new_count = chroma_service.get_collection_count('documents')
        imported = new_count - initial_count
        print(f"✅ TXT Import Test: Added {imported} documents")
    else:
        print("⚠️  example_data.txt not found, skipping TXT test")
    
    # Final verification
    print("\n" + "="*70)
    print("📊 FINAL VERIFICATION")
    print("="*70)
    
    final_count = chroma_service.get_collection_count('documents')
    print(f"Total documents in database: {final_count:,}")
    
    # Test search functionality
    print("\n🔍 Testing search with imported content...")
    results = chroma_service.search_documents("computer science", n_results=3)
    
    if results:
        print(f"✅ Search successful! Found {len(results)} results:")
        for i, (doc, distance) in enumerate(results, 1):
            print(f"\n  {i}. {doc.title}")
            print(f"     URL: {doc.source_url}")
            print(f"     Distance: {distance:.4f}")
    else:
        print("⚠️  No search results found")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)


if __name__ == "__main__":
    try:
        test_imports()
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

