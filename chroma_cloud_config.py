#!/usr/bin/env python3
"""
Chroma Cloud Configuration
Configuration for connecting to Chroma Cloud database
"""

import os
from chromadb import CloudClient

# Chroma Cloud Configuration - Updated for Northeastern Database
CHROMA_CLOUD_CONFIG = {
    'api_key': 'ck-7Kx6tSBSNJgdk4W1w5muQUbfqt7n1QjfxNgQdSiLyQa4',
    'tenant': '6b132689-6807-45c8-8d18-1a07edafc2d7',
    'database': 'northeasterndb'  # Your new consolidated database
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

