#!/usr/bin/env python3
"""
Direct test of the fixed chatbot without API
"""

import sys
import os

# Add services to path
sys.path.append('services/chat_service')

def test_chatbot():
    print("🧪 Testing Fixed Chatbot Directly")
    print("=" * 40)
    
    try:
        from fixed_chatbot import chatbot
        
        print("✅ Chatbot imported successfully")
        print(f"📊 Database type: {chatbot.db_type}")
        
        # Test a question
        question = "Tell me about Northeastern University admissions"
        print(f"\n🤖 Testing question: {question}")
        
        result = chatbot.chat(question, "test_session")
        
        print(f"📝 Answer: {result['answer']}")
        print(f"📊 Sources: {len(result.get('sources', []))}")
        print(f"🎯 Confidence: {result.get('confidence', 0):.2f}")
        print(f"⏱️  Response time: {result.get('response_time', 0):.2f}s")
        print(f"📄 Documents analyzed: {result.get('documents_analyzed', 0)}")
        
        # Show sources if any
        sources = result.get('sources', [])
        if sources:
            print(f"\n📚 Sources found:")
            for i, source in enumerate(sources[:3]):  # Show first 3
                print(f"  {i+1}. {source.get('title', 'No title')}")
                print(f"     URL: {source.get('url', 'No URL')}")
                print(f"     Relevance: {source.get('relevance', 'N/A')}")
        else:
            print("\n⚠️  No sources found - this indicates the database is empty or not accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chatbot()
    if success:
        print("\n🎉 Direct chatbot test completed!")
    else:
        print("\n❌ Direct chatbot test failed!")
