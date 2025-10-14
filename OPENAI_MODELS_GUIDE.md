# 🤖 OpenAI Models Guide

## Available OpenAI Models

### ⚡ GPT-4o-mini (RECOMMENDED DEFAULT)

**Model**: `gpt-4o-mini`

**Specifications**:
- **Speed**: ⚡⚡⚡⚡⚡ Fastest (2-4 seconds)
- **Cost**: 💰 Cheapest (~$0.0015/query)
- **Accuracy**: 📊 Excellent (85-92%)
- **Context**: 128K tokens
- **Best for**: Production, high-volume use

**Pricing**:
- Input: $0.00015 per 1K tokens
- Output: $0.0006 per 1K tokens
- **~$0.0015 per query** (typical)

**Monthly Cost Estimate**:
- 10 queries/day = ~$0.45/month
- 100 queries/day = ~$4.50/month
- 1000 queries/day = ~$45/month

✅ **This is the RECOMMENDED DEFAULT model for chatbots**

---

### 🧠 o4-mini-2025-04-16 (Reasoning Model)

**Model**: `o4-mini-2025-04-16`

**Specifications**:
- **Type**: Reasoning model (like o1-mini)
- **Speed**: ⚡⚡⚡ Moderate (5-15 seconds, chain-of-thought)
- **Cost**: 💰 Same as gpt-4o-mini (~$0.0015/query)
- **Accuracy**: 📊 Excellent for reasoning (90-95%)
- **Context**: 128K tokens
- **Best for**: Math, logic, complex multi-step reasoning

⚠️ **Important Restrictions**:
- **Temperature MUST be 1.0** (no custom temperature)
- Cannot use temperature=0.1 (will error)
- Uses internal chain-of-thought
- Slower than chat models

**Use Cases**:
- Mathematical problems
- Complex logic puzzles
- Multi-step reasoning
- Scientific calculations

**NOT ideal for**:
- Simple Q&A (use gpt-4o-mini)
- Chatbots needing deterministic responses
- Fast information retrieval

---

### 🎯 GPT-4o (Balanced)

**Model**: `gpt-4o`

**Specifications**:
- **Speed**: ⚡⚡⚡⚡ Fast (3-6 seconds)
- **Cost**: 💰💰 Moderate (~$0.015/query)
- **Accuracy**: 📊 Excellent (90-95%)
- **Context**: 128K tokens
- **Best for**: Complex queries, high accuracy needs

**Pricing**:
- Input: $0.0025 per 1K tokens
- Output: $0.01 per 1K tokens
- **~$0.015 per query**

**Monthly Cost Estimate**:
- 10 queries/day = ~$4.50/month
- 100 queries/day = ~$45/month

---

### 🏆 GPT-4 (Highest Quality)

**Model**: `gpt-4` or `gpt-4-turbo`

**Specifications**:
- **Speed**: ⚡⚡⚡ Good (5-10 seconds)
- **Cost**: 💰💰💰 Higher (~$0.15/query)
- **Accuracy**: 📊 Best (92-98%)
- **Context**: 8K-128K tokens
- **Best for**: Critical accuracy requirements

**Pricing**:
- Input: $0.03 per 1K tokens
- Output: $0.06 per 1K tokens
- **~$0.15 per query**

**Monthly Cost Estimate**:
- 10 queries/day = ~$45/month
- 100 queries/day = ~$450/month

---

### 💨 GPT-3.5-Turbo (Budget)

**Model**: `gpt-3.5-turbo`

**Specifications**:
- **Speed**: ⚡⚡⚡⚡⚡ Very Fast (2-3 seconds)
- **Cost**: 💰 Very Cheap (~$0.002/query)
- **Accuracy**: 📊 Good (75-85%)
- **Context**: 16K tokens
- **Best for**: Simple queries, testing

**Pricing**:
- Input: $0.0005 per 1K tokens
- Output: $0.0015 per 1K tokens
- **~$0.002 per query**

**Monthly Cost Estimate**:
- 10 queries/day = ~$0.60/month
- 100 queries/day = ~$6/month

---

## 🎯 Which Model to Choose?

### Use **gpt-4o-mini** (RECOMMENDED) if:
✅ You want the **best value** (speed + cost + quality)
✅ You need **fast responses** (2-4 seconds)
✅ You have **moderate-high volume** (100-1000 queries/day)
✅ Budget is important but quality matters
✅ **Recommended for most chatbots** ⭐

### Use **o4-mini-2025-04-16** (Reasoning) if:
✅ You need **advanced reasoning** capabilities
✅ Mathematical or logical problems
✅ Multi-step problem solving
✅ Can accept **temperature=1.0** (required)
⚠️ **NOT for simple Q&A or chatbots**

### Use **GPT-4o** if:
✅ You need **better accuracy** than mini
✅ You handle **complex queries**
✅ Budget allows for ~10x cost of mini
✅ Response time 3-6 seconds is acceptable

### Use **GPT-4** if:
✅ You need **absolute best accuracy**
✅ Critical use case (legal, medical, etc.)
✅ Budget allows for ~100x cost of mini
✅ Quality > Speed/Cost

### Use **GPT-3.5-Turbo** if:
✅ You're **just testing**
✅ Simple questions only
✅ Extremely budget-constrained
✅ Speed is critical

---

## 🔧 How to Change Models

### Method 1: Environment Variable (Recommended)

**.env file**:
```env
OPENAI_MODEL=gpt-4o-mini
```

**Or in terminal**:
```bash
# Linux/Mac
export OPENAI_MODEL=gpt-4o-mini

# Windows PowerShell
$env:OPENAI_MODEL="gpt-4o-mini"
```

### Method 2: Direct in Code

Edit `services/chat_service/enhanced_openai_chatbot.py`:
```python
def __init__(self, model_name: str = "gpt-4o-mini", ...):
```

### Method 3: Runtime Parameter

```python
from services.chat_service.enhanced_openai_chatbot import create_enhanced_openai_chatbot

# Use specific model
chatbot = create_enhanced_openai_chatbot(model_type="gpt-4")
```

---

## 📊 Performance Comparison

| Model | Speed | Cost/Query | Accuracy | Best For |
|-------|-------|-----------|----------|----------|
| **gpt-4o-mini** ⭐ | 2-4s | $0.0015 | 85-92% | Chatbots/Production |
| **o4-mini-2025-04-16** | 5-15s | $0.0015 | 90-95% reasoning | Math/Logic tasks |
| **gpt-4o** | 3-6s | $0.015 | 90-95% | Complex queries |
| **gpt-4** | 5-10s | $0.15 | 92-98% | Critical accuracy |
| **gpt-3.5-turbo** | 2-3s | $0.002 | 75-85% | Testing/Simple |

---

## 💰 Cost Examples

### Low Volume (10 queries/day)

| Model | Daily | Monthly | Yearly |
|-------|-------|---------|--------|
| gpt-4o-mini | $0.015 | $0.45 | $5.40 |
| o4-mini-2025-04-16 | $0.015 | $0.45 | $5.40 |
| gpt-4o | $0.15 | $4.50 | $54 |
| gpt-4 | $1.50 | $45 | $540 |
| gpt-3.5-turbo | $0.02 | $0.60 | $7.20 |

### Medium Volume (100 queries/day)

| Model | Daily | Monthly | Yearly |
|-------|-------|---------|--------|
| gpt-4o-mini | $0.15 | $4.50 | $54 |
| o4-mini-2025-04-16 | $0.15 | $4.50 | $54 |
| gpt-4o | $1.50 | $45 | $540 |
| gpt-4 | $15 | $450 | $5,400 |
| gpt-3.5-turbo | $0.20 | $6 | $72 |

### High Volume (1000 queries/day)

| Model | Daily | Monthly | Yearly |
|-------|-------|---------|--------|
| gpt-4o-mini | $1.50 | $45 | $540 |
| o4-mini-2025-04-16 | $1.50 | $45 | $540 |
| gpt-4o | $15 | $450 | $5,400 |
| gpt-4 | $150 | $4,500 | $54,000 |
| gpt-3.5-turbo | $2 | $60 | $720 |

---

## 🎯 Recommendation

### For Your Use Case (University Chatbot):

**Best Choice: gpt-4o-mini** ⭐

**Reasons**:
1. **Excellent accuracy** (85-92%) - good enough for university Q&A
2. **Fast responses** (2-4 seconds) - great user experience
3. **Affordable** (~$4.50/month for 100 queries/day)
4. **Latest model** - includes recent improvements
5. **128K context** - handles long documents well

**Cost-Benefit Analysis**:
- **100x cheaper** than GPT-4
- **Only slightly less accurate** (85-92% vs 92-98%)
- **2-3x faster** than GPT-4
- **Better than GPT-3.5-Turbo** in accuracy
- **Supports temperature=0.1** for deterministic responses

**Why not o4-mini-2025-04-16?**
- o4-mini is a **reasoning model** (like o1-mini)
- Designed for **complex reasoning**, not simple Q&A
- **Requires temperature=1.0** (less deterministic)
- **Slower** (5-15 seconds due to chain-of-thought)
- **Overkill** for university information queries

---

## 🔄 Migration Path

If you're currently using GPT-4:

```bash
# Step 1: Update .env
OPENAI_MODEL=gpt-4o-mini

# Step 2: Restart
python quick_start_openai.py

# Step 3: Test
# Ask a few questions to verify quality
```

**Expected Changes**:
- ✅ **Faster**: 5-10s → 2-4s
- ✅ **Cheaper**: $0.15 → $0.0015 per query (100x cheaper!)
- ⚠️ **Slightly less accurate**: 92-98% → 85-92%

For most university chatbot queries, the accuracy difference is negligible!

---

## 🧪 Testing Different Models

```bash
# Test gpt-4o-mini (recommended for chatbots)
export OPENAI_MODEL=gpt-4o-mini
python quick_start_openai.py

# Test o4-mini (for reasoning tasks)
export OPENAI_MODEL=o4-mini-2025-04-16
python quick_start_openai.py

# Test GPT-4o (if you need more accuracy)
export OPENAI_MODEL=gpt-4o
python quick_start_openai.py

# Test GPT-4 (if cost is not a concern)
export OPENAI_MODEL=gpt-4
python quick_start_openai.py

# Test GPT-3.5-Turbo (for comparison)
export OPENAI_MODEL=gpt-3.5-turbo
python quick_start_openai.py
```

---

## ✅ Current Default

**As of this update**: `gpt-4o-mini`

**Why**: Best balance of speed, cost, and quality for chatbot use cases.

**Note**: o4-mini-2025-04-16 is also supported but is a reasoning model better suited for complex logic tasks, not simple Q&A.

---

## 📚 Model Naming Reference

### Correct Model Names (Chat Models):
✅ `gpt-4o-mini` - Recommended for chatbots ⭐
✅ `gpt-4o` - GPT-4 Optimized
✅ `gpt-4` - Standard GPT-4
✅ `gpt-4-turbo` - GPT-4 Turbo
✅ `gpt-4-turbo-preview` - Preview version
✅ `gpt-3.5-turbo` - GPT-3.5

### Reasoning Models:
✅ `o4-mini-2025-04-16` - Reasoning model (temp=1.0 required)
✅ `o1-mini` - Reasoning model
✅ `o1-preview` - Reasoning model

### Common Mistakes:
❌ `o4-mini` - Incomplete (use o4-mini-2025-04-16)
❌ `gpt4-mini` - Wrong format
❌ `gpt-4-mini` - Doesn't exist (use gpt-4o-mini)

---

## 🎉 Quick Summary

**RECOMMENDED DEFAULT**: `gpt-4o-mini`

**Why**: 
- 100x cheaper than GPT-4
- Fast responses (2-4 seconds)
- Deterministic (temperature=0.1 supported)
- Perfect for Q&A chatbots!

**Update Now**:
```bash
# Add to .env (or update if you have o4-mini)
OPENAI_MODEL=gpt-4o-mini

# Restart
python quick_start_openai.py
```

**Note on o4-mini-2025-04-16**:
- This is a **reasoning model** (like o1-mini)
- Good for: Math, logic, complex reasoning
- NOT ideal for: Simple Q&A, chatbots
- Requires: temperature=1.0 (less deterministic)
- Use gpt-4o-mini for chatbots instead!

**Enjoy faster responses and lower costs!** 🚀

