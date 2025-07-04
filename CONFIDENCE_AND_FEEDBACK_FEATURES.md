# Confidence Scoring and User Feedback Features

## Overview

The Northeastern University Chatbot now includes advanced confidence scoring and user feedback systems to improve answer quality and provide better user experience.

## 🎯 Confidence Scoring System

### How It Works

The confidence scoring system evaluates answer quality based on multiple factors:

#### 1. **Document Similarity (40% weight)**
- **Top document similarity**: Most important factor (25%)
- **Weighted average similarity**: Considers rank of retrieved documents (20%)

#### 2. **Document Coverage (15% weight)**
- Number of relevant documents with good similarity (>0.6)
- More documents = higher confidence

#### 3. **Answer Quality (25% weight)**
- **Length score**: Optimal answer length (15-800 words)
- **Uncertainty detection**: Penalizes uncertain language (15%)

#### 4. **Source Quality (10% weight)**
- **Source diversity**: Multiple unique sources
- **Northeastern specificity**: Presence of university-specific terms

#### 5. **Relevance (10% weight)**
- **Question-answer keyword overlap**
- **Northeastern indicators**: Co-op, Boston, Husky, etc.

### Dynamic Confidence Thresholds

The system uses different confidence thresholds based on question type:

| Question Type | Threshold | Examples |
|---------------|-----------|----------|
| **Specific Factual** | 0.6 | "What is the tuition cost?", "When is the deadline?" |
| **General Questions** | 0.3 | "What is Northeastern?", "How does co-op work?" |
| **Process Questions** | 0.4 | "How do I apply?", "What are the requirements?" |

### Confidence Levels

- **High Confidence (≥70%)**: Green indicator, full answer shown
- **Medium Confidence (50-69%)**: Yellow indicator, answer shown with caution
- **Low Confidence (<50%)**: Red indicator, answer filtered or shown with warning

## 📊 User Feedback System

### Feedback Collection

Users can rate answers on a 1-5 scale and provide text feedback:

```json
{
  "session_id": "user_session_123",
  "question": "What is the tuition cost?",
  "answer": "The tuition is approximately $60,000...",
  "rating": 4,
  "feedback_text": "Good information but could be more specific"
}
```

### Feedback Analytics

The system provides comprehensive analytics:

#### **Basic Metrics**
- Total feedback count
- Average rating
- Confidence correlation with user satisfaction

#### **Issue Analysis**
- **No Information**: "no information", "not found", "don't have"
- **Incorrect Info**: "wrong", "incorrect", "outdated"
- **Unclear Answer**: "unclear", "confusing", "vague"
- **Missing Details**: "more details", "specific", "contact"

#### **Improvement Suggestions**
- Automatic suggestions based on feedback patterns
- Confidence algorithm tuning recommendations
- Knowledge base expansion suggestions

## 🔧 API Endpoints

### Enhanced Chat Endpoint

```http
POST /chat
Content-Type: application/json

{
  "question": "What is the tuition cost?",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "answer": "The tuition cost for Northeastern University...",
  "sources": [...],
  "confidence": 0.75,
  "session_id": "session_id",
  "should_show": true,
  "feedback_requested": false
}
```

### Feedback Submission

```http
POST /feedback
Content-Type: application/json

{
  "session_id": "user_session_123",
  "question": "What is the tuition cost?",
  "answer": "The tuition is approximately $60,000...",
  "rating": 4,
  "feedback_text": "Good information but could be more specific"
}
```

### Feedback Analytics

```http
GET /feedback/analytics
```

**Response:**
```json
{
  "total_feedback": 25,
  "average_rating": 3.8,
  "confidence_correlation": 0.65,
  "common_issues": [
    {
      "issue": "no_information",
      "count": 5,
      "percentage": 20.0
    }
  ],
  "improvement_suggestions": [
    "Consider expanding knowledge base with more specific Northeastern information"
  ],
  "recent_feedback": [...]
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_confidence_and_feedback.py
```

This will test:
- Confidence scoring with different question types
- Answer filtering behavior
- Feedback submission and analytics
- Enhanced search features

## 📈 Monitoring and Improvement

### Key Metrics to Monitor

1. **Confidence Distribution**
   - Percentage of high/medium/low confidence answers
   - Correlation between confidence and user ratings

2. **Feedback Trends**
   - Average rating over time
   - Common issues and their frequency
   - User satisfaction trends

3. **System Performance**
   - Answer filtering rate
   - Feedback collection rate
   - Knowledge base coverage

### Continuous Improvement

1. **Threshold Tuning**
   - Adjust confidence thresholds based on user feedback
   - Fine-tune for different question types

2. **Knowledge Base Expansion**
   - Identify low-confidence topics
   - Add more specific Northeastern information

3. **Algorithm Refinement**
   - Improve confidence scoring weights
   - Enhance uncertainty detection

## 🎨 Frontend Integration

### Confidence Indicators

```javascript
// Display confidence level
if (response.confidence >= 0.7) {
    showConfidenceIndicator('high', 'green');
} else if (response.confidence >= 0.5) {
    showConfidenceIndicator('medium', 'yellow');
} else {
    showConfidenceIndicator('low', 'red');
}

// Handle filtered answers
if (!response.should_show) {
    showFilteredAnswer(response.answer);
    showFeedbackRequest();
}
```

### Feedback UI

```javascript
// Show feedback form for low confidence or user request
if (response.feedback_requested) {
    showFeedbackForm({
        sessionId: response.session_id,
        question: userQuestion,
        answer: response.answer
    });
}

// Submit feedback
async function submitFeedback(data) {
    const response = await fetch('/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return response.json();
}
```

## 🔒 Data Privacy

- Feedback is stored with session IDs for analysis
- No personally identifiable information is collected
- Feedback data is used only for system improvement
- Users can request feedback deletion

## 🚀 Future Enhancements

1. **Machine Learning Integration**
   - Train models on feedback data
   - Predict answer quality before generation

2. **Advanced Analytics**
   - Topic-based feedback analysis
   - Temporal trends and seasonality

3. **Personalization**
   - User-specific confidence thresholds
   - Personalized answer filtering

4. **Real-time Monitoring**
   - Live feedback dashboard
   - Alert system for quality issues

## 📞 Support

For questions about confidence scoring or feedback features:

1. Check the test script: `test_confidence_and_feedback.py`
2. Review API documentation: `http://localhost:8001/docs`
3. Monitor feedback analytics: `http://localhost:8001/feedback/analytics`

---

*This system continuously improves based on user feedback to provide the best possible Northeastern University information.* 