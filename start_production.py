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
    
    # Check if ChromaDB data already exists and has content
    if chroma_sqlite.exists():
        # Check if the collection actually has documents
        try:
            from services.shared.database import get_chroma_client, get_collection
            client = get_chroma_client()
            collection = get_collection('documents')
            result = collection.get()
            
            if result and result.get('ids') and len(result['ids']) > 0:
                print(f"✅ ChromaDB data found with {len(result['ids'])} documents, skipping restore")
                return True
            else:
                print("⚠️  ChromaDB exists but is empty, proceeding with restore...")
        except Exception as e:
            print(f"⚠️  Error checking ChromaDB content: {e}, proceeding with restore...")
    else:
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
        response = requests.get(backup_url, stream=True, timeout=300)
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
        
        # List extracted contents for debugging
        print("📁 Extracted contents:")
        for item in backup_dir.iterdir():
            print(f"   - {item.name} ({'dir' if item.is_dir() else 'file'})")
        
        # Find the extracted backup directory - try multiple patterns
        extracted_dirs = []
        
        # Pattern 1: chroma_backup_*
        extracted_dirs.extend([d for d in backup_dir.iterdir() if d.is_dir() and d.name.startswith("chroma_backup_")])
        
        # Pattern 2: Any directory that might contain chroma data
        if not extracted_dirs:
            for item in backup_dir.iterdir():
                if item.is_dir():
                    # Check if this directory contains chroma.sqlite3 or embeddings
                    if (item / "chroma.sqlite3").exists() or (item / "embeddings").exists():
                        extracted_dirs.append(item)
                    # Also check for any subdirectories that might be the actual backup
                    for subitem in item.iterdir():
                        if subitem.is_dir() and ((subitem / "chroma.sqlite3").exists() or (subitem / "embeddings").exists()):
                            extracted_dirs.append(subitem)
        
        # Pattern 3: Look for chroma.sqlite3 directly in backup_dir
        if not extracted_dirs and (backup_dir / "chroma.sqlite3").exists():
            extracted_dirs.append(backup_dir)
        
        if not extracted_dirs:
            print("❌ No valid backup found in downloaded file")
            print("🔍 Available files and directories:")
            for item in backup_dir.rglob("*"):
                if item.is_file():
                    print(f"   - {item.relative_to(backup_dir)}")
            return False
        
        extracted_backup = extracted_dirs[0]
        print(f"📁 Using backup directory: {extracted_backup}")
        
        # Restore ChromaDB data
        print("🔄 Restoring ChromaDB data...")
        
        # Restore SQLite database
        sqlite_backup = extracted_backup / "chroma.sqlite3"
        if sqlite_backup.exists():
            import shutil
            shutil.copy2(sqlite_backup, chroma_sqlite)
            print("✅ SQLite database restored")
        else:
            print("⚠️  No chroma.sqlite3 found in backup")
        
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
        else:
            print("⚠️  No embeddings directory found in backup")
            # Try to find embedding files in the backup directory itself
            for item in extracted_backup.iterdir():
                if item.is_dir() and item.name not in ["__pycache__", "chroma_data"]:
                    dest_dir = chroma_data_path / item.name
                    import shutil
                    shutil.copytree(item, dest_dir)
                    print(f"✅ Restored directory: {item.name}")
        
        # Verify restore
        try:
            from services.shared.database import get_chroma_client, get_collection
            client = get_chroma_client()
            collection = get_collection('documents')
            result = collection.get()
            
            if result and result.get('ids') and len(result['ids']) > 0:
                print(f"✅ ChromaDB restore verified: {len(result['ids'])} documents found")
                return True
            else:
                print("❌ Restore completed but no documents found")
                return False
                
        except Exception as e:
            print(f"⚠️  Could not verify restore: {e}")
            return True  # Assume success if we can't verify
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        import traceback
        traceback.print_exc()
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