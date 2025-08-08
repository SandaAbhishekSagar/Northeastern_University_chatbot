#!/usr/bin/env python3
"""
Practical Script for Using Embedding Cache Files
This script helps you analyze, use, and manage your embedding cache files
"""

import os
import pickle
import sys
from pathlib import Path
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def analyze_all_cache_files():
    """Analyze all embedding cache files in the project"""
    print("🔍 Analyzing All Embedding Cache Files")
    print("=" * 50)
    
    cache_files = [
        "embeddings_cache.pkl",
        "enhanced_embeddings_cache.pkl",
        "enhanced_gpu_embeddings_cache.pkl",
        "optimized_gpu_embeddings_cache.pkl",
        "robust_gpu_embeddings_cache.pkl",
        "fast_embeddings_cache.pkl",
        "enhanced_llm_embeddings_cache.pkl"
    ]
    
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            size_mb = os.path.getsize(cache_file) / (1024 * 1024)
            print(f"📁 {cache_file}")
            print(f"   Size: {size_mb:.2f} MB")
            
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                if isinstance(cache_data, dict):
                    print(f"   Type: Dictionary with {len(cache_data)} keys")
                    for key, value in cache_data.items():
                        if isinstance(value, dict):
                            print(f"     {key}: {len(value)} entries")
                        elif isinstance(value, list):
                            print(f"     {key}: {len(value)} items")
                        else:
                            print(f"     {key}: {type(value)}")
                elif isinstance(cache_data, list):
                    print(f"   Type: List with {len(cache_data)} items")
                else:
                    print(f"   Type: {type(cache_data)}")
                    
            except Exception as e:
                print(f"   ❌ Error loading: {e}")
        else:
            print(f"📁 {cache_file} - ❌ Not found")
        
        print()

def test_cache_usage():
    """Test using different cache files"""
    print("🧪 Testing Cache Usage")
    print("=" * 30)
    
    # Test basic cache
    if os.path.exists("embeddings_cache.pkl"):
        print("Testing basic cache...")
        try:
            with open("embeddings_cache.pkl", 'rb') as f:
                cache_data = pickle.load(f)
            print(f"✅ Basic cache loaded: {len(cache_data)} entries")
        except Exception as e:
            print(f"❌ Basic cache error: {e}")
    
    # Test enhanced cache
    if os.path.exists("enhanced_embeddings_cache.pkl"):
        print("Testing enhanced cache...")
        try:
            with open("enhanced_embeddings_cache.pkl", 'rb') as f:
                cache_data = pickle.load(f)
            print(f"✅ Enhanced cache loaded: {len(cache_data)} entries")
        except Exception as e:
            print(f"❌ Enhanced cache error: {e}")

def load_enhanced_embedding_manager():
    """Load the enhanced embedding manager with the best available cache"""
    print("🚀 Loading Enhanced Embedding Manager")
    print("=" * 40)
    
    try:
        from enhanced_embedding_solution import EnhancedEmbeddingManager
        
        # Try different cache files in order of preference
        cache_files = [
            "enhanced_embeddings_cache.pkl",  # Best for production
            "enhanced_gpu_embeddings_cache.pkl",  # Good for GPU
            "embeddings_cache.pkl",  # Basic fallback
        ]
        
        for cache_file in cache_files:
            if os.path.exists(cache_file):
                print(f"📁 Using cache: {cache_file}")
                embedding_manager = EnhancedEmbeddingManager(cache_file)
                
                # Test the manager
                print("🧪 Testing search functionality...")
                start_time = time.time()
                results = embedding_manager.search_documents("test query", n_results=1)
                search_time = time.time() - start_time
                
                print(f"✅ Search test successful: {len(results)} results in {search_time:.3f}s")
                return embedding_manager
        
        print("❌ No suitable cache files found")
        return None
        
    except ImportError:
        print("❌ Enhanced embedding solution not available")
        return None
    except Exception as e:
        print(f"❌ Error loading embedding manager: {e}")
        return None

def search_with_cache(query, n_results=5):
    """Perform a search using the best available cache"""
    print(f"🔍 Searching for: '{query}'")
    print("=" * 40)
    
    embedding_manager = load_enhanced_embedding_manager()
    
    if embedding_manager:
        try:
            start_time = time.time()
            results = embedding_manager.search_documents(query, n_results)
            search_time = time.time() - start_time
            
            print(f"✅ Found {len(results)} results in {search_time:.3f}s")
            print()
            
            for i, doc in enumerate(results, 1):
                print(f"{i}. {doc.get('title', 'No title')}")
                print(f"   Similarity: {doc.get('similarity', 0):.3f}")
                print(f"   Content: {doc.get('content', 'No content')[:100]}...")
                print()
            
            return results
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    else:
        print("❌ No embedding manager available")
        return []

def create_cache_summary():
    """Create a summary of all cache files"""
    print("📊 Cache Files Summary")
    print("=" * 30)
    
    cache_info = []
    
    cache_files = [
        ("embeddings_cache.pkl", "Basic"),
        ("enhanced_embeddings_cache.pkl", "Enhanced"),
        ("enhanced_gpu_embeddings_cache.pkl", "GPU Optimized"),
        ("optimized_gpu_embeddings_cache.pkl", "Optimized GPU"),
        ("robust_gpu_embeddings_cache.pkl", "Robust GPU"),
        ("fast_embeddings_cache.pkl", "Fast"),
        ("enhanced_llm_embeddings_cache.pkl", "LLM Enhanced")
    ]
    
    for cache_file, description in cache_files:
        if os.path.exists(cache_file):
            size_mb = os.path.getsize(cache_file) / (1024 * 1024)
            cache_info.append({
                'file': cache_file,
                'description': description,
                'size_mb': size_mb,
                'status': 'Available'
            })
        else:
            cache_info.append({
                'file': cache_file,
                'description': description,
                'size_mb': 0,
                'status': 'Missing'
            })
    
    # Sort by size (largest first)
    cache_info.sort(key=lambda x: x['size_mb'], reverse=True)
    
    print(f"{'File':<30} {'Description':<15} {'Size (MB)':<10} {'Status':<10}")
    print("-" * 70)
    
    for info in cache_info:
        print(f"{info['file']:<30} {info['description']:<15} {info['size_mb']:<10.2f} {info['status']:<10}")
    
    return cache_info

def recommend_best_cache():
    """Recommend the best cache file to use"""
    print("💡 Cache Recommendation")
    print("=" * 25)
    
    cache_info = create_cache_summary()
    
    # Find the best available cache
    available_caches = [c for c in cache_info if c['status'] == 'Available']
    
    if not available_caches:
        print("❌ No cache files available")
        return None
    
    # Recommend based on size and type
    best_cache = None
    
    # Prefer enhanced cache for production
    for cache in available_caches:
        if 'enhanced' in cache['file'] and 'gpu' not in cache['file']:
            best_cache = cache
            break
    
    # Fallback to largest cache
    if not best_cache:
        best_cache = available_caches[0]
    
    print(f"🎯 Recommended: {best_cache['file']}")
    print(f"   Description: {best_cache['description']}")
    print(f"   Size: {best_cache['size_mb']:.2f} MB")
    print(f"   Reason: {'Best for production use' if 'enhanced' in best_cache['file'] else 'Largest available cache'}")
    
    return best_cache

def main():
    """Main function with interactive menu"""
    print("🔧 Embedding Cache Usage Tool")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Analyze all cache files")
        print("2. Test cache usage")
        print("3. Search with cache")
        print("4. Create cache summary")
        print("5. Get cache recommendation")
        print("6. Load enhanced embedding manager")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == "1":
            analyze_all_cache_files()
        elif choice == "2":
            test_cache_usage()
        elif choice == "3":
            query = input("Enter search query: ").strip()
            if query:
                search_with_cache(query)
            else:
                print("❌ Please enter a valid query")
        elif choice == "4":
            create_cache_summary()
        elif choice == "5":
            recommend_best_cache()
        elif choice == "6":
            embedding_manager = load_enhanced_embedding_manager()
            if embedding_manager:
                print("✅ Enhanced embedding manager loaded successfully")
            else:
                print("❌ Failed to load embedding manager")
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 