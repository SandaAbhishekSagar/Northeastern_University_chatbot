#!/usr/bin/env python3
"""
Test script to verify the chatbot fixes work
"""

import sys
import os
sys.path.append('.')

def test_chatbot():
    """Test the chatbot functionality"""
    print("🧪 Testing Fixed Chatbot...")
    
    try:
        from services.chat_service.fixed_chatbot import chatbot
        print("✅ Chatbot imported successfully")
        
        # Test a simple question
        print("🤖 Testing chat functionality...")
        result = chatbot.chat("Tell me about Northeastern University admissions")
        
        print(f"📝 Answer: {result.get('answer', 'No answer')[:100]}...")
        print(f"📊 Sources: {len(result.get('sources', []))}")
        print(f"🎯 Confidence: {result.get('confidence', 0.0)}")
        print(f"📚 Documents analyzed: {result.get('documents_analyzed', 0)}")
        print(f"⏱️  Response time: {result.get('response_time', 0.0):.2f}s")
        
        # Check if all required fields are present
        required_fields = ['answer', 'sources', 'confidence', 'session_id', 'response_time', 'documents_analyzed']
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        else:
            print("✅ All required fields present")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_chatbot()
    if success:
        print("🎉 Chatbot test passed!")
    else:
        print("💥 Chatbot test failed!")
        sys.exit(1)
