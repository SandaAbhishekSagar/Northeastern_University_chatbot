#!/usr/bin/env python3
"""
Check Chroma Cloud Database Status
Simple script to verify cloud database connection and count documents
"""

import os
import sys

# Chroma Cloud Configuration
CHROMA_CLOUD_CONFIG = {
    'api_key': 'ck-4RLZskGk7sxLbFNvMZCQY4xASn4WPReJ1W4CSf9tvhUW',
    'tenant': '28757e4a-f042-4b0c-ad7c-9257cd36b130',
    'database': 'newtest'
}

def check_cloud_database():
    """Check the Chroma Cloud database status"""
    print("=" * 60)
    print("CHROMA CLOUD DATABASE CHECK")
    print("=" * 60)
    
    try:
        from chromadb import CloudClient
        
        print(f"\nConnecting to Chroma Cloud...")
        print(f"  Database: {CHROMA_CLOUD_CONFIG['database']}")
        print(f"  Tenant: {CHROMA_CLOUD_CONFIG['tenant']}")
        
        client = CloudClient(
            api_key=CHROMA_CLOUD_CONFIG['api_key'],
            tenant=CHROMA_CLOUD_CONFIG['tenant'],
            database=CHROMA_CLOUD_CONFIG['database']
        )
        
        print("\n[SUCCESS] Connected to Chroma Cloud!")
        
        # List all collections
        collections = client.list_collections()
        
        print(f"\n{'='*60}")
        print(f"COLLECTIONS FOUND: {len(collections)}")
        print(f"{'='*60}\n")
        
        total_documents = 0
        batch_collections = []
        main_collections = []
        
        for collection in collections:
            name = collection.name
            count = collection.count()
            total_documents += count
            
            # Categorize collections
            if 'batch' in name.lower():
                batch_collections.append((name, count))
            else:
                main_collections.append((name, count))
            
            print(f"  - {name}")
            print(f"    Documents: {count:,}")
            print()
        
        # Summary
        print(f"{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"  Total Collections: {len(collections)}")
        print(f"  Main Collections: {len(main_collections)}")
        print(f"  Batch Collections: {len(batch_collections)}")
        print(f"  Total Documents: {total_documents:,}")
        
        # Detailed breakdown
        if main_collections:
            print(f"\n{'='*60}")
            print(f"MAIN COLLECTIONS")
            print(f"{'='*60}")
            for name, count in main_collections:
                print(f"  {name}: {count:,} documents")
        
        if batch_collections:
            print(f"\n{'='*60}")
            print(f"BATCH COLLECTIONS")
            print(f"{'='*60}")
            for name, count in batch_collections:
                print(f"  {name}: {count:,} documents")
            
            # Check batch sequence
            batch_nums = []
            for name, count in batch_collections:
                if 'batch_' in name:
                    try:
                        num = int(name.split('_')[-1])
                        batch_nums.append(num)
                    except:
                        pass
            
            if batch_nums:
                batch_nums.sort()
                print(f"\n  Batch numbers: {batch_nums}")
                print(f"  Min batch: {min(batch_nums)}")
                print(f"  Max batch: {max(batch_nums)}")
                
                # Check for gaps
                expected = list(range(min(batch_nums), max(batch_nums) + 1))
                missing = [x for x in expected if x not in batch_nums]
                if missing:
                    print(f"  WARNING: Missing batches: {missing}")
                else:
                    print(f"  All batches present (no gaps)")
        
        print(f"\n{'='*60}")
        print("[SUCCESS] Cloud database check completed!")
        print(f"{'='*60}\n")
        
        return True
        
    except ImportError as e:
        print(f"\n[ERROR] ChromaDB not installed: {e}")
        print("Please install with: pip install chromadb")
        return False
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to Chroma Cloud: {e}")
        print("\nPossible issues:")
        print("  1. Invalid API key or tenant")
        print("  2. Network connection problem")
        print("  3. Database does not exist")
        return False

if __name__ == "__main__":
    success = check_cloud_database()
    sys.exit(0 if success else 1)

