#!/usr/bin/env python3
"""
Debug startup script for FastAPI deployment
"""

import sys
import os
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting debug startup script...")
        
        # Check Python version
        logger.info(f"Python version: {sys.version}")
        
        # Check current directory
        logger.info(f"Current directory: {os.getcwd()}")
        
        # List files in current directory
        logger.info("Files in current directory:")
        for file in os.listdir('.'):
            logger.info(f"  - {file}")
        
        # Try to import FastAPI
        logger.info("Importing FastAPI...")
        from fastapi import FastAPI
        logger.info("FastAPI imported successfully")
        
        # Try to import uvicorn
        logger.info("Importing uvicorn...")
        import uvicorn
        logger.info("Uvicorn imported successfully")
        
        # Create a simple app
        logger.info("Creating FastAPI app...")
        app = FastAPI(title="Debug API", version="1.0.0")
        
        @app.get("/")
        async def root():
            return {"message": "Debug API is running!", "status": "success"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "message": "Debug API is working"}
        
        @app.get("/debug")
        async def debug():
            return {
                "python_version": sys.version,
                "current_directory": os.getcwd(),
                "files": os.listdir('.'),
                "environment": dict(os.environ)
            }
        
        logger.info("Starting uvicorn server...")
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 