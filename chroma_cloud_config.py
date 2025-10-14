#!/usr/bin/env python3
"""
Chroma Cloud Configuration
Configuration for connecting to Chroma Cloud database
"""

import os
from chromadb import CloudClient

# Chroma Cloud Configuration
CHROMA_CLOUD_CONFIG = {
    'api_key': 'ck-4RLZskGk7sxLbFNvMZCQY4xASn4WPReJ1W4CSf9tvhUW',
    'tenant': '28757e4a-f042-4b0c-ad7c-9257cd36b130',
    'database': 'newtest'  # Your existing database
}

def get_chroma_cloud_client():
    """Get a Chroma Cloud client instance"""
    return CloudClient(
        api_key=CHROMA_CLOUD_CONFIG['api_key'],
        tenant=CHROMA_CLOUD_CONFIG['tenant'],
        database=CHROMA_CLOUD_CONFIG['database']
    )

def test_cloud_connection():
    """Test the connection to Chroma Cloud"""
    try:
        client = get_chroma_cloud_client()
        
        # Test connection by listing collections
        collections = client.list_collections()
        
        print("✅ Chroma Cloud connection successful!")
        print(f"📊 Database: {CHROMA_CLOUD_CONFIG['database']}")
        print(f"📋 Collections found: {len(collections)}")
        
        for collection in collections:
            print(f"  - {collection.name} ({collection.count()} documents)")
        
        return True
        
    except Exception as e:
        print(f"❌ Chroma Cloud connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Chroma Cloud Connection...")
    print("=" * 50)
    test_cloud_connection()

