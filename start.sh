#!/bin/bash
# Railway startup script
# This script properly handles the PORT environment variable

# Use Railway's PORT or default to 8000
PORT=${PORT:-8000}

echo "🚀 Starting Enhanced OpenAI API on port $PORT..."

# Start uvicorn with the correct port
uvicorn services.chat_service.enhanced_openai_api:app --host 0.0.0.0 --port $PORT

