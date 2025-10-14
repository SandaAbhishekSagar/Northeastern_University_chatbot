#!/usr/bin/env python3
"""
Deep analysis of pickle files to find document content
"""

import pickle
import os
import json
from pathlib import Path

def deep_analyze_pickle(file_path, max_depth=3, current_depth=0):
    """Recursively analyze pickle file contents"""
    if current_depth >= max_depth:
        return
    
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        print(f"{'  ' * current_depth}📋 Type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"{'  ' * current_depth}📋 Keys: {list(data.keys())}")
            print(f"{'  ' * current_depth}📋 Size: {len(data)} items")
            
            # Look for document-related keys
            doc_keys = [k for k in data.keys() if any(word in str(k).lower() for word in ['doc', 'content', 'text', 'label', 'id'])]
            if doc_keys:
                print(f"{'  ' * current_depth}🎯 Document-related keys: {doc_keys}")
                
                # Analyze document-related keys
                for key in doc_keys[:3]:  # Analyze first 3
                    value = data[key]
                    print(f"{'  ' * (current_depth + 1)}📋 {key}: {type(value)}")
                    
                    if isinstance(value, dict) and current_depth < max_depth - 1:
                        print(f"{'  ' * (current_depth + 1)}📋 Sub-keys: {list(value.keys())[:10]}")
                        if len(value) > 0:
                            sample_key = list(value.keys())[0]
                            sample_value = value[sample_key]
                            print(f"{'  ' * (current_depth + 1)}📋 Sample {sample_key}: {type(sample_value)}")
                            if isinstance(sample_value, str) and len(sample_value) > 50:
                                print(f"{'  ' * (current_depth + 1)}📋 Sample content: {sample_value[:100]}...")
                    
                    elif isinstance(value, str) and len(value) > 50:
                        print(f"{'  ' * (current_depth + 1)}📋 Content: {value[:100]}...")
                        
        elif isinstance(data, list):
            print(f"{'  ' * current_depth}📋 Length: {len(data)}")
            if len(data) > 0:
                print(f"{'  ' * current_depth}📋 First item type: {type(data[0])}")
                if isinstance(data[0], str) and len(data[0]) > 50:
                    print(f"{'  ' * current_depth}📋 Sample content: {data[0][:100]}...")
                    
    except Exception as e:
        print(f"{'  ' * current_depth}❌ Error: {e}")

def analyze_largest_metadata_file():
    """Analyze the largest index_metadata.pickle file"""
    print("🔍 Analyzing Largest Index Metadata File")
    print("=" * 60)
    
    # Find the largest index_metadata.pickle file
    largest_file = None
    largest_size = 0
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == 'index_metadata.pickle':
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                if file_size > largest_size:
                    largest_size = file_size
                    largest_file = file_path
    
    if largest_file:
        print(f"📊 Largest file: {largest_file}")
        print(f"📊 Size: {largest_size:,} bytes ({largest_size/1024/1024:.2f} MB)")
        
        deep_analyze_pickle(largest_file, max_depth=4)
    else:
        print("❌ No index_metadata.pickle files found")

def analyze_enhanced_cache_structure():
    """Analyze the structure of enhanced embeddings cache"""
    print("\n🔍 Analyzing Enhanced Cache Structure")
    print("=" * 60)
    
    cache_file = "enhanced_embeddings_cache.pkl"
    if not os.path.exists(cache_file):
        print(f"❌ {cache_file} not found")
        return
    
    deep_analyze_pickle(cache_file, max_depth=3)

def search_for_document_content():
    """Search for document content in all pickle files"""
    print("\n🔍 Searching for Document Content")
    print("=" * 60)
    
    pickle_files = [
        "enhanced_embeddings_cache.pkl",
        "embeddings_cache.pkl"
    ]
    
    # Also find index_metadata.pickle files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == 'index_metadata.pickle':
                pickle_files.append(os.path.join(root, file))
    
    for pickle_file in pickle_files:
        if not os.path.exists(pickle_file):
            continue
            
        print(f"\n🔍 Searching in: {pickle_file}")
        try:
            with open(pickle_file, 'rb') as f:
                data = pickle.load(f)
            
            # Search for document content recursively
            found_content = search_recursive(data, max_depth=3)
            if found_content:
                print(f"✅ Found document content in {pickle_file}")
                for content in found_content[:3]:  # Show first 3
                    print(f"📋 Content: {content[:100]}...")
            else:
                print(f"❌ No document content found in {pickle_file}")
                
        except Exception as e:
            print(f"❌ Error reading {pickle_file}: {e}")

def search_recursive(data, max_depth=3, current_depth=0):
    """Recursively search for document content"""
    if current_depth >= max_depth:
        return []
    
    found_content = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 100:
                # Check if it looks like document content
                if any(word in value.lower() for word in ['northeastern', 'university', 'admission', 'program', 'course']):
                    found_content.append(value)
            
            elif isinstance(value, (dict, list)) and current_depth < max_depth - 1:
                found_content.extend(search_recursive(value, max_depth, current_depth + 1))
                
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str) and len(item) > 100:
                if any(word in item.lower() for word in ['northeastern', 'university', 'admission', 'program', 'course']):
                    found_content.append(item)
            elif isinstance(item, (dict, list)) and current_depth < max_depth - 1:
                found_content.extend(search_recursive(item, max_depth, current_depth + 1))
    
    return found_content

def main():
    """Main function"""
    print("🚀 Deep Pickle File Analysis")
    print("=" * 60)
    
    # Analyze largest metadata file
    analyze_largest_metadata_file()
    
    # Analyze enhanced cache structure
    analyze_enhanced_cache_structure()
    
    # Search for document content
    search_for_document_content()
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 