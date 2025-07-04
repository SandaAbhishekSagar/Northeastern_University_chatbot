#!/usr/bin/env python3
"""
Test Confidence Scoring and User Feedback Features
Demonstrates the enhanced confidence scoring, filtering, and feedback system
"""

import requests
import json
import time
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8001"

def test_confidence_scoring():
    """Test confidence scoring with different types of questions"""
    print("🧪 Testing Confidence Scoring and Filtering")
    print("=" * 50)
    
    # Test questions with varying confidence levels
    test_questions = [
        {
            "question": "What is the tuition cost for Northeastern University?",
            "expected_confidence": "high",  # Specific factual question
            "description": "Specific factual question (should have high confidence threshold)"
        },
        {
            "question": "How do I apply to Northeastern?",
            "expected_confidence": "medium",  # Process question
            "description": "Process question (should have medium confidence threshold)"
        },
        {
            "question": "What is Northeastern University?",
            "expected_confidence": "low",  # General question
            "description": "General question (should have lower confidence threshold)"
        },
        {
            "question": "What is the exact deadline for spring 2025 applications?",
            "expected_confidence": "high",  # Very specific question
            "description": "Very specific question (should have high confidence threshold)"
        },
        {
            "question": "Tell me about the weather in Boston",
            "expected_confidence": "low",  # Unrelated question
            "description": "Unrelated question (should have low confidence)"
        }
    ]
    
    session_id = f"test_session_{int(time.time())}"
    
    for i, test_case in enumerate(test_questions, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Question: {test_case['question']}")
        
        try:
            response = requests.post(f"{API_BASE_URL}/chat", json={
                "question": test_case['question'],
                "session_id": session_id
            })
            
            if response.status_code == 200:
                data = response.json()
                confidence = data['confidence']
                should_show = data['should_show']
                feedback_requested = data['feedback_requested']
                
                print(f"   Confidence: {confidence:.2%}")
                print(f"   Should Show: {should_show}")
                print(f"   Feedback Requested: {feedback_requested}")
                
                # Analyze confidence level
                if confidence >= 0.7:
                    confidence_level = "high"
                elif confidence >= 0.5:
                    confidence_level = "medium"
                else:
                    confidence_level = "low"
                
                print(f"   Confidence Level: {confidence_level}")
                
                if not should_show:
                    print(f"   ⚠️  Answer filtered due to low confidence")
                    print(f"   Filtered Answer: {data['answer'][:100]}...")
                else:
                    print(f"   ✅ Answer shown")
                    print(f"   Answer Preview: {data['answer'][:100]}...")
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)  # Rate limiting

def test_user_feedback():
    """Test user feedback submission and analytics"""
    print("\n\n📊 Testing User Feedback System")
    print("=" * 50)
    
    session_id = f"feedback_test_{int(time.time())}"
    
    # Test feedback submissions
    test_feedback = [
        {
            "question": "What is the tuition cost for Northeastern?",
            "answer": "The tuition cost for Northeastern University varies by program. For undergraduate students, the annual tuition is approximately $60,000. However, specific costs depend on your program and whether you're an in-state or out-of-state student.",
            "rating": 4,
            "feedback_text": "Good information but could be more specific about different programs"
        },
        {
            "question": "How do I apply to Northeastern?",
            "answer": "I don't have enough information about the application process for Northeastern University. Please contact the admissions office directly.",
            "rating": 2,
            "feedback_text": "No useful information provided"
        },
        {
            "question": "What is Northeastern University?",
            "answer": "Northeastern University is a private research university located in Boston, Massachusetts. It's known for its cooperative education program and strong emphasis on experiential learning.",
            "rating": 5,
            "feedback_text": "Excellent overview of the university"
        }
    ]
    
    print("Submitting test feedback...")
    
    for i, feedback in enumerate(test_feedback, 1):
        print(f"\n{i}. Submitting feedback for: {feedback['question'][:50]}...")
        
        try:
            response = requests.post(f"{API_BASE_URL}/feedback", json={
                "session_id": session_id,
                "question": feedback['question'],
                "answer": feedback['answer'],
                "rating": feedback['rating'],
                "feedback_text": feedback['feedback_text']
            })
            
            if response.status_code == 200:
                print(f"   ✅ Feedback submitted successfully (Rating: {feedback['rating']}/5)")
            else:
                print(f"   ❌ Error submitting feedback: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.5)
    
    # Test analytics
    print("\n📈 Testing Feedback Analytics...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/feedback/analytics")
        
        if response.status_code == 200:
            analytics = response.json()
            
            print(f"   Total Feedback: {analytics['total_feedback']}")
            print(f"   Average Rating: {analytics['average_rating']}/5")
            print(f"   Confidence Correlation: {analytics['confidence_correlation']:.3f}")
            
            if analytics['common_issues']:
                print("   Common Issues:")
                for issue in analytics['common_issues']:
                    print(f"     - {issue['issue']}: {issue['count']} occurrences ({issue['percentage']:.1f}%)")
            
            if analytics['improvement_suggestions']:
                print("   Improvement Suggestions:")
                for suggestion in analytics['improvement_suggestions']:
                    print(f"     - {suggestion}")
            
            if analytics['recent_feedback']:
                print("   Recent Feedback:")
                for feedback in analytics['recent_feedback'][-3:]:  # Last 3
                    print(f"     - Rating {feedback['rating']}/5: {feedback['question'][:40]}...")
            
        else:
            print(f"   ❌ Error getting analytics: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_enhanced_features():
    """Test enhanced features like query expansion and search"""
    print("\n\n🔍 Testing Enhanced Features")
    print("=" * 50)
    
    # Test query expansion
    test_queries = [
        "admission requirements",
        "co-op program",
        "housing options"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        try:
            response = requests.get(f"{API_BASE_URL}/search/expand", params={"query": query})
            
            if response.status_code == 200:
                data = response.json()
                expanded = data['expanded_queries']
                
                print(f"   Original: {data['original_query']}")
                print(f"   Expanded: {expanded}")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.5)
    
    # Test hybrid search
    print(f"\nTesting Hybrid Search...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/search", params={
            "query": "Northeastern University admission",
            "k": 3
        })
        
        if response.status_code == 200:
            data = response.json()
            documents = data['documents']
            
            print(f"   Found {len(documents)} documents:")
            for i, doc in enumerate(documents[:3], 1):
                print(f"     {i}. {doc['title'][:50]}... (Score: {doc.get('similarity', 0):.3f})")
                
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Run all tests"""
    print("🎓 Northeastern University Chatbot - Confidence & Feedback Test")
    print("=" * 70)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health/enhanced", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API is running - Status: {health['status']}")
            print(f"   Features: {', '.join(health['features'].keys())}")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure the API server is running on port 8001")
        return
    
    # Run tests
    test_confidence_scoring()
    test_user_feedback()
    test_enhanced_features()
    
    print("\n" + "=" * 70)
    print("🎉 All tests completed!")
    print("\n💡 Key Features Demonstrated:")
    print("   • Confidence scoring based on multiple factors")
    print("   • Dynamic confidence thresholds by question type")
    print("   • Answer filtering for low-confidence responses")
    print("   • User feedback collection and storage")
    print("   • Feedback analytics and improvement suggestions")
    print("   • Query expansion and hybrid search")
    
    print("\n🔧 Next Steps:")
    print("   • Check the frontend for feedback UI integration")
    print("   • Monitor feedback analytics for system improvement")
    print("   • Adjust confidence thresholds based on user satisfaction")

if __name__ == "__main__":
    main() 