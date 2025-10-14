# 🔧 OpenAI Integration Troubleshooting

## Issue: System Hangs or Loads Forever

### Symptoms
- Chat interface shows "Loading..." for 30+ minutes
- Console shows repeated "Loading system status..." messages
- No response from the API

### Root Causes & Solutions

#### 1. **OpenAI API Timeout**

**Problem**: OpenAI API calls can sometimes hang or timeout.

**Solution**: Updated code now includes:
- ✅ 30-second timeout on API calls
- ✅ Automatic retries (2 attempts)
- ✅ Fallback to simple queries if expansion fails
- ✅ Better error handling

**Fixed in**: `services/chat_service/enhanced_openai_chatbot.py`

#### 2. **Query Expansion Hanging**

**Problem**: Query expansion calls OpenAI and can hang.

**Solution**:
```python
# Now has timeout protection
self.llm = ChatOpenAI(
    model=model_name,
    request_timeout=30,  # ← Added
    max_retries=2        # ← Added
)
```

#### 3. **Network Issues**

**Check**:
```bash
# Test OpenAI connectivity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Solutions**:
- Check internet connection
- Verify OpenAI API is not down: https://status.openai.com
- Check firewall/proxy settings

#### 4. **API Key Issues**

**Check**:
```bash
# Verify API key is set
python -c "from services.shared.config import config; print('Key:', config.OPENAI_API_KEY[:10])"
```

**Solutions**:
- Ensure API key is valid
- Check API key has sufficient credits
- Verify no typos in `.env` file

---

## Quick Fixes

### Fix 1: Restart with Updated Code

```bash
# Stop current process (Ctrl+C)
# Restart with updated code
python quick_start_openai.py
```

### Fix 2: Use Simpler Model

Switch to GPT-3.5-Turbo (faster, less likely to timeout):

**.env file**:
```env
OPENAI_MODEL=gpt-3.5-turbo
```

### Fix 3: Test API Directly

```bash
# Test if OpenAI is responding
python -c "
from langchain_openai import ChatOpenAI
from services.shared.config import config

llm = ChatOpenAI(
    model='gpt-3.5-turbo',
    temperature=0.1,
    openai_api_key=config.OPENAI_API_KEY,
    request_timeout=10
)

response = llm.invoke('Say hello')
print('Response:', response.content)
"
```

### Fix 4: Fallback to Ollama

If OpenAI continues to have issues:

```bash
# Use local Ollama instead (always works)
python quick_start_enhanced_gpu.py
```

---

## Prevention

### 1. Monitor OpenAI Status

Before starting, check: https://status.openai.com

### 2. Set Reasonable Timeouts

In `.env`:
```env
OPENAI_REQUEST_TIMEOUT=30
```

### 3. Use Rate Limiting

For production, implement request queuing to avoid rate limits.

### 4. Cache Common Queries

Future enhancement: Cache frequently asked questions.

---

## Debugging Steps

### Step 1: Check Logs

```bash
# Check API logs
tail -f chroma.log
```

### Step 2: Test Components

```bash
# Test chatbot directly
python services/chat_service/enhanced_openai_chatbot.py
```

### Step 3: Verify Configuration

```bash
# Check all settings
python services/shared/config.py
```

### Step 4: Test with Simple Question

Use frontend, ask: "Hello"

Should respond quickly (3-5 seconds).

---

## Performance Tips

### 1. Use GPT-3.5-Turbo for Speed

- **GPT-4**: ~10-15 seconds per query
- **GPT-3.5-Turbo**: ~3-5 seconds per query

Change in `.env`:
```env
OPENAI_MODEL=gpt-3.5-turbo
```

### 2. Disable Query Expansion (if needed)

Edit `enhanced_openai_chatbot.py`:
```python
# In hybrid_search method, change:
expanded_queries = [query]  # Skip expansion
```

### 3. Reduce Documents Analyzed

Change `k=10` to `k=5` in `generate_enhanced_openai_response()`:
```python
relevant_docs = self.hybrid_search(question, k=5)  # Instead of 10
```

---

## Error Messages

### "OpenAI API key not found"

**Fix**:
```bash
export OPENAI_API_KEY=sk-your-key-here
```

### "Rate limit exceeded"

**Fix**: Wait a few minutes or upgrade OpenAI plan

### "Insufficient quota"

**Fix**: Add credits to OpenAI account

### "Connection timeout"

**Fix**: Check internet connection, try GPT-3.5-Turbo

---

## Updated Features

### ✅ Now Includes:

1. **30-second timeouts** on all OpenAI calls
2. **Automatic retries** (2 attempts)
3. **Better error messages** with specific issues
4. **Graceful fallbacks** if expansion fails
5. **Progress logging** to track what's happening

### Example Output:

```
[ENHANCED OPENAI] Expanding query: What programs does...
[ENHANCED OPENAI] Generated 3 query variations
[ENHANCED OPENAI] Hybrid search completed in 2.34 seconds
[ENHANCED OPENAI] Generating answer with GPT...
[ENHANCED OPENAI] Response generated in 8.45s
```

---

## Still Having Issues?

### Option 1: Use Ollama (Local)

```bash
# Guaranteed to work, no API issues
python quick_start_enhanced_gpu.py
```

### Option 2: Check OpenAI Status

Visit: https://status.openai.com

### Option 3: Contact Support

- OpenAI Support: https://help.openai.com
- Check API usage: https://platform.openai.com/usage

---

## Success Indicators

✅ **Working Correctly**:
```
[ENHANCED OPENAI] Expanding query...
[ENHANCED OPENAI] Generated 3 query variations
[ENHANCED OPENAI] Generating answer with GPT...
[ENHANCED OPENAI] Response generated in 8.45s
```

❌ **Not Working**:
```
[ENHANCED OPENAI] Query expansion error: timeout
[ENHANCED OPENAI] Error generating answer: ...
(no response after 30+ seconds)
```

---

## Quick Reference

| Problem | Quick Fix |
|---------|-----------|
| Timeout | Use GPT-3.5-Turbo |
| Rate limit | Wait or upgrade plan |
| No credits | Add payment method |
| Slow | Use Ollama instead |
| Hanging | Restart, check network |

---

**Remember**: Ollama version always works as fallback! 🚀
