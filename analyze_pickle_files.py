#!/usr/bin/env python3
"""
Analyze pickle files in the project to understand their contents
"""

import pickle
import os
import sys
from pathlib import Path
import numpy as np

def analyze_pickle_file(file_path):
    """Analyze a pickle file and return information about its contents"""
    print(f"\n🔍 Analyzing: {file_path}")
    print("=" * 60)
    
    try:
        # Get file size
        file_size = os.path.getsize(file_path)
        print(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        # Load the pickle file
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        # Analyze the data
        print(f"📋 Data type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"📋 Dictionary keys: {list(data.keys())}")
            print(f"📋 Number of items: {len(data)}")
            
            # Show some sample data
            for key, value in list(data.items())[:5]:
                print(f"  - {key}: {type(value)} (size: {len(str(value)) if hasattr(value, '__len__') else 'N/A'})")
                
        elif isinstance(data, list):
            print(f"📋 List length: {len(data)}")
            if len(data) > 0:
                print(f"📋 First item type: {type(data[0])}")
                print(f"📋 Sample first item: {str(data[0])[:200]}...")
                
        elif isinstance(data, np.ndarray):
            print(f"📋 NumPy array shape: {data.shape}")
            print(f"📋 Data type: {data.dtype}")
            print(f"📋 Memory usage: {data.nbytes:,} bytes")
            
        elif hasattr(data, '__len__'):
            print(f"📋 Length: {len(data)}")
            print(f"📋 Sample data: {str(data)[:200]}...")
            
        else:
            print(f"📋 Data: {str(data)[:200]}...")
            
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing {file_path}: {e}")
        return False

def analyze_embedding_caches():
    """Analyze embedding cache files"""
    print("🔍 Analyzing Embedding Cache Files")
    print("=" * 60)
    
    cache_files = [
        "embeddings_cache.pkl",
        "enhanced_embeddings_cache.pkl", 
        "enhanced_gpu_embeddings_cache.pkl",
        "enhanced_llm_embeddings_cache.pkl",
        "fast_embeddings_cache.pkl",
        "optimized_gpu_embeddings_cache.pkl",
        "robust_gpu_embeddings_cache.pkl"
    ]
    
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            analyze_pickle_file(cache_file)
        else:
            print(f"❌ {cache_file}: Not found")

def analyze_index_metadata():
    """Analyze index metadata files"""
    print("\n🔍 Analyzing Index Metadata Files")
    print("=" * 60)
    
    # Find all index_metadata.pickle files
    metadata_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == 'index_metadata.pickle':
                metadata_files.append(os.path.join(root, file))
    
    print(f"📋 Found {len(metadata_files)} index_metadata.pickle files")
    
    for metadata_file in metadata_files[:5]:  # Analyze first 5
        analyze_pickle_file(metadata_file)

def check_for_document_data():
    """Check if any pickle files contain document data"""
    print("\n🔍 Checking for Document Data in Pickle Files")
    print("=" * 60)
    
    pickle_files = [
        "embeddings_cache.pkl",
        "enhanced_embeddings_cache.pkl",
        "enhanced_gpu_embeddings_cache.pkl"
    ]
    
    for pickle_file in pickle_files:
        if not os.path.exists(pickle_file):
            continue
            
        try:
            with open(pickle_file, 'rb') as f:
                data = pickle.load(f)
            
            # Look for document-related data
            if isinstance(data, dict):
                doc_keys = [k for k in data.keys() if 'doc' in str(k).lower() or 'content' in str(k).lower()]
                if doc_keys:
                    print(f"📋 {pickle_file}: Found document-related keys: {doc_keys}")
                    
                    # Check if any of these contain actual document content
                    for key in doc_keys[:3]:  # Check first 3
                        value = data[key]
                        if isinstance(value, (list, str)) and len(str(value)) > 100:
                            print(f"  - {key}: Contains substantial data ({len(str(value))} chars)")
                            
        except Exception as e:
            print(f"❌ Error checking {pickle_file}: {e}")

def main():
    """Main function"""
    print("🚀 Pickle File Analysis")
    print("=" * 60)
    
    # Analyze embedding caches
    analyze_embedding_caches()
    
    # Analyze index metadata
    analyze_index_metadata()
    
    # Check for document data
    check_for_document_data()
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 