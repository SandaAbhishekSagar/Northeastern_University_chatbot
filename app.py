#!/usr/bin/env python3
"""
Simple app.py for Railway deployment
This is the standard entry point Railway looks for
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Northeastern University Chatbot",
    description="Simple chatbot API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Northeastern University Chatbot",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "chat": "/chat"
        }
    }

@app.post("/chat")
async def chat():
    """Simple chat endpoint"""
    return {
        "answer": "Hello! I'm the Northeastern University Chatbot. The full chatbot is being initialized.",
        "sources": [],
        "confidence": 0.8,
        "session_id": "simple_mode",
        "response_time": 0.1,
        "documents_analyzed": 0
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
