# 🚀 OpenAI ChatGPT Quick Start

## 3-Step Setup

### 1️⃣ Get OpenAI API Key
Get your key from: https://platform.openai.com/api-keys

### 2️⃣ Set API Key
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY=sk-your-api-key-here
```

### 3️⃣ Run
```bash
python quick_start_openai.py
```

## Access
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8001

## Features
✅ OpenAI GPT-4/GPT-3.5  
✅ 3-10 second responses  
✅ 85-95% accuracy  
✅ No Ollama installation needed  

## Full Documentation
See `OPENAI_SETUP_GUIDE.md` for complete details.

## Cost
- **GPT-4**: ~$0.15/query (~$450/month for 100 queries/day)
- **GPT-3.5**: ~$0.003/query (~$9/month for 100 queries/day)

## Switch Models
Edit in code or set environment:
```bash
export OPENAI_MODEL=gpt-3.5-turbo  # Faster, cheaper
export OPENAI_MODEL=gpt-4          # Best quality
```

## Still Works: Ollama Version
```bash
python quick_start_enhanced_gpu.py  # Free, local, private
```

Both versions share the same frontend and database!

