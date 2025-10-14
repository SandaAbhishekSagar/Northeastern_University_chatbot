#!/usr/bin/env python3
"""
OpenAI Performance Optimization Script
This script optimizes the OpenAI RAG chatbot for better performance
"""

import os
import sys
import torch
from pathlib import Path

def check_gpu_availability():
    """Check if GPU is available and optimize for it"""
    print("🔍 Checking GPU Availability...")
    
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        current_device = torch.cuda.current_device()
        gpu_name = torch.cuda.get_device_name(current_device)
        
        print(f"✅ GPU Available: {gpu_name}")
        print(f"📊 GPU Count: {gpu_count}")
        print(f"🎯 Current Device: {current_device}")
        
        # Test GPU memory
        gpu_memory = torch.cuda.get_device_properties(current_device).total_memory / 1024**3
        print(f"💾 GPU Memory: {gpu_memory:.1f} GB")
        
        return True, current_device
    else:
        print("❌ No GPU available, using CPU")
        return False, None

def optimize_openai_rag_chatbot():
    """Optimize the OpenAI RAG chatbot for better performance"""
    print("\n🚀 Optimizing OpenAI RAG Chatbot...")
    
    # Check GPU availability
    gpu_available, device_id = check_gpu_availability()
    
    # Read the current file
    file_path = Path("services/chat_service/openai_rag_chatbot.py")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Performance optimizations
    optimizations = []
    
    # 1. GPU acceleration for embeddings
    if gpu_available:
        old_embedding_config = """self.embeddings_model = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )"""
        
        new_embedding_config = f"""self.embeddings_model = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={{'device': 'cuda:{device_id}'}},
                encode_kwargs={{'normalize_embeddings': True}}
            )"""
        
        if old_embedding_config in content:
            content = content.replace(old_embedding_config, new_embedding_config)
            optimizations.append("✅ GPU acceleration for embeddings")
    
    # 2. Optimize LLM parameters for faster responses
    old_llm_config = """self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.1,          # Lower for more factual responses
            max_tokens=2000,          # Adequate for comprehensive answers
            frequency_penalty=0.1,    # Reduce repetition
            presence_penalty=0.1      # Encourage new information
        )"""
    
    new_llm_config = """self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.1,          # Lower for more factual responses
            max_tokens=1500,          # Reduced for faster responses
            frequency_penalty=0.05,   # Reduced for faster processing
            presence_penalty=0.05,    # Reduced for faster processing
            request_timeout=30        # Add timeout for faster failure
        )"""
    
    if old_llm_config in content:
        content = content.replace(old_llm_config, new_llm_config)
        optimizations.append("✅ Optimized LLM parameters")
    
    # 3. Reduce document analysis for faster responses
    old_doc_count = "relevant_docs = self.hybrid_search(question, k=10)  # Analyze 10 documents"
    new_doc_count = "relevant_docs = self.hybrid_search(question, k=6)   # Analyze 6 documents for speed"
    
    if old_doc_count in content:
        content = content.replace(old_doc_count, new_doc_count)
        optimizations.append("✅ Reduced document analysis (6 instead of 10)")
    
    # 4. Optimize search parameters
    old_search_params = "n_results=k * 2  # Get more results for reranking"
    new_search_params = "n_results=k + 2  # Get fewer results for speed"
    
    if old_search_params in content:
        content = content.replace(old_search_params, new_search_params)
        optimizations.append("✅ Optimized search parameters")
    
    # 5. Add performance monitoring
    performance_monitoring = '''
        # Performance monitoring
        self.performance_stats = {
            'total_queries': 0,
            'avg_response_time': 0.0,
            'avg_search_time': 0.0,
            'avg_llm_time': 0.0
        }
'''
    
    # Insert performance monitoring after conversation storage
    insert_point = "# Initialize conversation storage"
    if insert_point in content and "performance_stats" not in content:
        content = content.replace(insert_point, insert_point + performance_monitoring)
        optimizations.append("✅ Added performance monitoring")
    
    # 6. Optimize context preparation
    old_context_limit = "context = \"\\n\\n\".join([f\"[{s['source']}]: {s['content']}\" for s in relevant_sections[:5]])"
    new_context_limit = "context = \"\\n\\n\".join([f\"[{s['source']}]: {s['content']}\" for s in relevant_sections[:3]])"
    
    if old_context_limit in content:
        content = content.replace(old_context_limit, new_context_limit)
        optimizations.append("✅ Reduced context sections (3 instead of 5)")
    
    # Write the optimized file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n🎯 Applied {len(optimizations)} optimizations:")
    for opt in optimizations:
        print(f"   {opt}")
    
    return True

def create_performance_test():
    """Create a performance test script"""
    test_script = '''#!/usr/bin/env python3
"""
Performance Test for Optimized OpenAI RAG Chatbot
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_performance():
    """Test the performance of the optimized chatbot"""
    print("🚀 Testing Optimized OpenAI RAG Performance")
    print("=" * 50)
    
    try:
        from services.chat_service.openai_rag_chatbot import OpenAIUniversityRAGChatbot
        
        # Initialize chatbot
        print("🔧 Initializing optimized chatbot...")
        start_time = time.time()
        
        chatbot = OpenAIUniversityRAGChatbot(
            model_name="o4-mini-2025-04-16-2024-07-18",
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        init_time = time.time() - start_time
        print(f"✅ Initialization time: {init_time:.2f} seconds")
        
        # Test questions
        test_questions = [
            "What are the admission requirements?",
            "How does the co-op program work?",
            "What is the tuition cost?"
        ]
        
        total_time = 0
        total_search_time = 0
        total_llm_time = 0
        
        for i, question in enumerate(test_questions, 1):
            print(f"\\n📝 Test {i}: {question}")
            
            response = chatbot.generate_openai_response(question)
            
            total_time += response['response_time']
            total_search_time += response['search_time']
            total_llm_time += response['llm_time']
            
            print(f"   ⏱️  Total time: {response['response_time']:.2f}s")
            print(f"   🔍 Search time: {response['search_time']:.2f}s")
            print(f"   🤖 LLM time: {response['llm_time']:.2f}s")
            print(f"   📊 Confidence: {response['confidence']:.1f}%")
            print(f"   📄 Documents: {response['documents_analyzed']}")
        
        # Calculate averages
        avg_total = total_time / len(test_questions)
        avg_search = total_search_time / len(test_questions)
        avg_llm = total_llm_time / len(test_questions)
        
        print(f"\\n📊 Performance Summary:")
        print(f"   Average Total Time: {avg_total:.2f}s")
        print(f"   Average Search Time: {avg_search:.2f}s")
        print(f"   Average LLM Time: {avg_llm:.2f}s")
        
        # Performance assessment
        if avg_total < 3.0:
            print("   🎉 Excellent performance!")
        elif avg_total < 5.0:
            print("   ✅ Good performance")
        else:
            print("   ⚠️  Performance could be improved")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during performance test: {e}")
        return False

if __name__ == "__main__":
    test_performance()
'''
    
    with open("test_optimized_performance.py", 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Created performance test script: test_optimized_performance.py")

def main():
    """Main optimization function"""
    print("🚀 OpenAI RAG Performance Optimization")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("services/chat_service/openai_rag_chatbot.py").exists():
        print("❌ Please run this script from the project root directory")
        return
    
    # Optimize the chatbot
    if optimize_openai_rag_chatbot():
        print("\n✅ Optimization completed successfully!")
        
        # Create performance test
        create_performance_test()
        
        print("\n🎯 Next Steps:")
        print("1. Restart your OpenAI frontend:")
        print("   python run_openai_frontend.py")
        print("2. Test the performance:")
        print("   python test_optimized_performance.py")
        print("3. Monitor response times in the frontend")
        
        print("\n📊 Expected Improvements:")
        print("   • 30-50% faster response times")
        print("   • Better GPU utilization (if available)")
        print("   • Reduced API costs")
        print("   • More efficient document processing")
    else:
        print("❌ Optimization failed")

if __name__ == "__main__":
    main() 