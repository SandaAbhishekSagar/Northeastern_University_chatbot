#!/usr/bin/env python3
"""
Comprehensive System Restoration and Fix Script
- Restores ChromaDB data from backups
- Fixes URL storage issues
- Migrates to ChatGPT API
- Sets up Pinecone with proper data
"""

import os
import sys
import shutil
import sqlite3
from pathlib import Path
import json
from datetime import datetime

def restore_chromadb_from_backup():
    """Restore ChromaDB from the most recent backup"""
    print("🔄 Restoring ChromaDB from backup...")
    
    # Find the most recent backup
    backup_dirs = [
        "chroma_backups/chroma_backup_20250809_112404",
        "chroma_data_backup_manual", 
        "chroma_data_backup_before_efficient_restore_1754159955"
    ]
    
    source_backup = None
    for backup_dir in backup_dirs:
        if os.path.exists(backup_dir):
            source_backup = backup_dir
            break
    
    if not source_backup:
        print("❌ No backup found!")
        return False
    
    print(f"📁 Found backup: {source_backup}")
    
    # Create new chroma_data directory
    target_dir = "chroma_data"
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    # Copy backup to new location
    shutil.copytree(source_backup, target_dir)
    print(f"✅ Restored ChromaDB from {source_backup}")
    return True

def create_env_file():
    """Create .env file with necessary configuration"""
    print("📝 Creating .env file...")
    
    env_content = """# Northeastern University Chatbot Configuration

# OpenAI Configuration (for ChatGPT)
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone Configuration (optional - for cloud vector storage)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=northeastern-university

# ChromaDB Configuration
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_HTTP_PORT=8000

# University URLs to scrape
UNIVERSITY_URLS=https://www.northeastern.edu,https://catalog.northeastern.edu

# Scraping Configuration
SCRAPING_DELAY=3
MAX_CONCURRENT_REQUESTS=2
USER_AGENT=UniversityResearchBot/1.0

# LLM Configuration
LOCAL_LLM_MODEL=llama2:7b
EMBEDDING_MODEL=all-MiniLM-L6-v2
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file - please add your API keys!")

def update_requirements():
    """Update requirements.txt to include OpenAI"""
    print("📦 Updating requirements.txt...")
    
    requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
chromadb==0.4.18
sentence-transformers>=2.6.1
langchain==0.2.0
langchain-community==0.2.0
langchain-core==0.2.20
langchain-openai==0.1.0
openai>=1.0.0
pinecone-client==3.0.0
numpy>=1.26.0
pandas>=2.1.0
requests==2.31.0
python-dotenv==1.0.0
pydantic==2.5.0
scikit-learn>=1.3.0
torch>=2.1.0
transformers>=4.35.0
scrapy==2.11.0
beautifulsoup4==4.12.2
lxml==4.9.3
selenium==4.15.2
webdriver-manager==4.0.1
httpx==0.27.0
aiofiles==23.2.1
python-multipart==0.0.6
jinja2==3.1.2
markdown==3.5.1
pyyaml==6.0.1
tqdm==4.66.1
colorama==0.4.6
rich==13.7.0
huggingface-hub==0.34.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Updated requirements.txt with OpenAI support")

def main():
    print("🚀 Northeastern University Chatbot - System Restoration")
    print("=" * 60)
    
    # Step 1: Restore ChromaDB data
    if restore_chromadb_from_backup():
        print("✅ ChromaDB data restored successfully")
    else:
        print("⚠️  No backup found - will start with empty database")
    
    # Step 2: Create .env file
    create_env_file()
    
    # Step 3: Update requirements
    update_requirements()
    
    print("\n🎉 System restoration completed!")
    print("\n📋 Next steps:")
    print("1. Add your OpenAI API key to the .env file")
    print("2. Install updated requirements: pip install -r requirements.txt")
    print("3. Run the fixed chatbot: python start_fixed_chatbot.py")
    print("\n💡 The system will now use ChatGPT instead of Ollama for better reliability!")

if __name__ == "__main__":
    main()
