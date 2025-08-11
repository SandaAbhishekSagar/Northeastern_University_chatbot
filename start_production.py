#!/usr/bin/env python3
"""
Production Startup Script for Enhanced GPU Chatbot
Optimized for cloud deployment with environment variable configuration
"""

import os
import sys
import uvicorn
import subprocess
import requests
import zipfile
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def check_and_restore_chromadb():
    """Check if ChromaDB data exists, restore from backup if needed"""
    chroma_data_path = Path("/app/chroma_data")
    chroma_sqlite = chroma_data_path / "chroma.sqlite3"
    
    # Check if ChromaDB data already exists
    if chroma_sqlite.exists():
        print("✅ ChromaDB data found, skipping restore")
        return True
    
    print("🔄 ChromaDB data not found, attempting auto-restore...")
    
    # Get backup URL from environment
    backup_url = os.environ.get("CHROMA_RESTORE_URL")
    if not backup_url:
        print("⚠️  CHROMA_RESTORE_URL not set, skipping restore")
        return False
    
    try:
        # Create backup directory
        backup_dir = Path("/app/chroma_backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Download backup
        print(f"📥 Downloading backup from: {backup_url}")
        response = requests.get(backup_url, stream=True)
        response.raise_for_status()
        
        backup_file = backup_dir / "backup.zip"
        with open(backup_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("📦 Backup downloaded successfully")
        
        # Extract backup
        print("🗜️  Extracting backup...")
        with zipfile.ZipFile(backup_file, 'r') as zip_ref:
            zip_ref.extractall(backup_dir)
        
        # Find the extracted backup directory
        extracted_dirs = [d for d in backup_dir.iterdir() if d.is_dir() and d.name.startswith("chroma_backup_")]
        if not extracted_dirs:
            print("❌ No valid backup found in downloaded file")
            return False
        
        extracted_backup = extracted_dirs[0]
        print(f"📁 Extracted to: {extracted_backup}")
        
        # Restore ChromaDB data
        print("🔄 Restoring ChromaDB data...")
        
        # Restore SQLite database
        sqlite_backup = extracted_backup / "chroma.sqlite3"
        if sqlite_backup.exists():
            import shutil
            shutil.copy2(sqlite_backup, chroma_sqlite)
            print("✅ SQLite database restored")
        
        # Restore embedding files
        embedding_backup = extracted_backup / "embeddings"
        if embedding_backup.exists():
            # Remove existing embedding directories
            for item in chroma_data_path.iterdir():
                if item.is_dir() and item.name != "__pycache__":
                    import shutil
                    shutil.rmtree(item)
            
            # Copy embedding directories
            for collection_dir in embedding_backup.iterdir():
                if collection_dir.is_dir():
                    dest_dir = chroma_data_path / collection_dir.name
                    import shutil
                    shutil.copytree(collection_dir, dest_dir)
                    print(f"✅ Restored collection: {collection_dir.name}")
        
        print("✅ ChromaDB restore completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

def main():
    """Start the production server with cloud-optimized settings"""
    
    # Check and restore ChromaDB data if needed
    check_and_restore_chromadb()
    
    # Get configuration from environment variables
    port = int(os.environ.get("PORT", 8001))
    host = os.environ.get("HOST", "0.0.0.0")
    workers = int(os.environ.get("WORKERS", 1))
    log_level = os.environ.get("LOG_LEVEL", "info")
    
    print(f"🚀 Starting Enhanced GPU Chatbot in production mode...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"👥 Workers: {workers}")
    print(f"📝 Log Level: {log_level}")
    
    # Import the FastAPI app
    try:
        from services.chat_service.enhanced_gpu_api import app
        print("✅ Enhanced GPU API imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Enhanced GPU API: {e}")
        print("💡 Make sure all dependencies are installed")
        sys.exit(1)
    
    # Start the server
    uvicorn.run(
        "services.chat_service.enhanced_gpu_api:app",
        host=host,
        port=port,
        workers=workers,
        log_level=log_level,
        access_log=True,
        reload=False,  # Disable reload in production
        server_header=False,  # Security: don't expose server info
        date_header=False,    # Security: don't expose date info
    )

if __name__ == "__main__":
    main() 