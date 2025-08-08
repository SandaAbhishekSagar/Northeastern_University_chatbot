#!/usr/bin/env python3
"""
Comprehensive ChromaDB Backup Script
Creates a complete backup of ChromaDB including database, embeddings, and metadata
"""

import os
import sys
import shutil
import sqlite3
import json
import pickle
from datetime import datetime
from pathlib import Path
import zipfile
import hashlib

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.shared.database import get_chroma_client, get_collection
from services.shared.config import config

class ChromaDBBackup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.chroma_data_dir = self.project_root / "chroma_data"
        self.backup_dir = self.project_root / "chroma_backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Create timestamp for backup name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_name = f"chroma_backup_{timestamp}"
        self.backup_path = self.backup_dir / self.backup_name
        
    def create_backup(self):
        """Create a comprehensive backup of ChromaDB"""
        print("🔄 Starting ChromaDB Backup...")
        print(f"📁 Backup location: {self.backup_path}")
        
        try:
            # Step 1: Create backup directory
            self.backup_path.mkdir(exist_ok=True)
            
            # Step 2: Backup SQLite database
            self._backup_sqlite_database()
            
            # Step 3: Backup embeddings and metadata files
            self._backup_embedding_files()
            
            # Step 4: Export data as JSON for easy inspection
            self._export_data_as_json()
            
            # Step 5: Create backup manifest
            self._create_backup_manifest()
            
            # Step 6: Create compressed backup
            self._create_compressed_backup()
            
            print(f"✅ Backup completed successfully!")
            print(f"📦 Backup location: {self.backup_path}")
            print(f"🗜️  Compressed backup: {self.backup_path}.zip")
            
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def _backup_sqlite_database(self):
        """Backup the SQLite database"""
        print("📊 Backing up SQLite database...")
        
        sqlite_source = self.chroma_data_dir / "chroma.sqlite3"
        sqlite_backup = self.backup_path / "chroma.sqlite3"
        
        if sqlite_source.exists():
            shutil.copy2(sqlite_source, sqlite_backup)
            
            # Get database info
            conn = sqlite3.connect(sqlite_source)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            db_info = {
                "tables": [table[0] for table in tables],
                "size_mb": sqlite_source.stat().st_size / (1024 * 1024),
                "backup_time": datetime.now().isoformat()
            }
            
            # Save database info
            with open(self.backup_path / "database_info.json", 'w') as f:
                json.dump(db_info, f, indent=2)
            
            conn.close()
            print(f"   ✅ SQLite database backed up ({db_info['size_mb']:.2f} MB)")
        else:
            print("   ⚠️  SQLite database not found")
    
    def _backup_embedding_files(self):
        """Backup embedding files and metadata"""
        print("🔍 Backing up embedding files...")
        
        embedding_backup_dir = self.backup_path / "embeddings"
        embedding_backup_dir.mkdir(exist_ok=True)
        
        # Copy all subdirectories (embedding collections)
        for item in self.chroma_data_dir.iterdir():
            if item.is_dir() and item.name != "__pycache__":
                dest_dir = embedding_backup_dir / item.name
                shutil.copytree(item, dest_dir, dirs_exist_ok=True)
                print(f"   ✅ Backed up collection: {item.name}")
        
        # Create embedding manifest
        embedding_manifest = {
            "collections": [],
            "total_size_mb": 0,
            "backup_time": datetime.now().isoformat()
        }
        
        total_size = 0
        for collection_dir in embedding_backup_dir.iterdir():
            if collection_dir.is_dir():
                collection_size = sum(f.stat().st_size for f in collection_dir.rglob('*') if f.is_file())
                total_size += collection_size
                
                embedding_manifest["collections"].append({
                    "name": collection_dir.name,
                    "size_mb": collection_size / (1024 * 1024),
                    "files": [f.name for f in collection_dir.iterdir() if f.is_file()]
                })
        
        embedding_manifest["total_size_mb"] = total_size / (1024 * 1024)
        
        with open(self.backup_path / "embedding_manifest.json", 'w') as f:
            json.dump(embedding_manifest, f, indent=2)
        
        print(f"   ✅ Embedding files backed up ({embedding_manifest['total_size_mb']:.2f} MB)")
    
    def _export_data_as_json(self):
        """Export ChromaDB data as JSON for easy inspection"""
        print("📄 Exporting data as JSON...")
        
        try:
            client = get_chroma_client()
            
            # Export documents collection
            documents_collection = get_collection('documents')
            doc_result = documents_collection.get()
            
            if doc_result and doc_result.get('ids'):
                documents_data = {
                    "collection": "documents",
                    "count": len(doc_result['ids']),
                    "documents": []
                }
                
                for i, doc_id in enumerate(doc_result['ids']):
                    doc_data = {
                        "id": doc_id,
                        "content": doc_result['documents'][i],
                        "metadata": doc_result['metadatas'][i],
                        "embedding_length": len(doc_result['embeddings'][i]) if doc_result.get('embeddings') else 0
                    }
                    documents_data["documents"].append(doc_data)
                
                with open(self.backup_path / "documents_export.json", 'w', encoding='utf-8') as f:
                    json.dump(documents_data, f, indent=2, ensure_ascii=False)
                
                print(f"   ✅ Exported {len(doc_result['ids'])} documents")
            
            # Export universities collection
            universities_collection = get_collection('universities')
            univ_result = universities_collection.get()
            
            if univ_result and univ_result.get('ids'):
                universities_data = {
                    "collection": "universities",
                    "count": len(univ_result['ids']),
                    "universities": []
                }
                
                for i, univ_id in enumerate(univ_result['ids']):
                    univ_data = {
                        "id": univ_id,
                        "metadata": univ_result['metadatas'][i]
                    }
                    universities_data["universities"].append(univ_data)
                
                with open(self.backup_path / "universities_export.json", 'w', encoding='utf-8') as f:
                    json.dump(universities_data, f, indent=2, ensure_ascii=False)
                
                print(f"   ✅ Exported {len(univ_result['ids'])} universities")
            
        except Exception as e:
            print(f"   ⚠️  Could not export data as JSON: {e}")
    
    def _create_backup_manifest(self):
        """Create a comprehensive backup manifest"""
        print("📋 Creating backup manifest...")
        
        manifest = {
            "backup_info": {
                "name": self.backup_name,
                "created_at": datetime.now().isoformat(),
                "backup_type": "comprehensive_chromadb_backup",
                "version": "1.0"
            },
            "source_info": {
                "chroma_data_path": str(self.chroma_data_dir),
                "project_root": str(self.project_root)
            },
            "backup_contents": {
                "sqlite_database": "chroma.sqlite3",
                "embedding_files": "embeddings/",
                "data_exports": ["documents_export.json", "universities_export.json"],
                "metadata_files": ["database_info.json", "embedding_manifest.json"]
            },
            "restore_instructions": {
                "method_1": "Use restore_chromadb.py script",
                "method_2": "Manually copy files back to chroma_data/ directory",
                "method_3": "Extract from compressed backup and restore"
            }
        }
        
        with open(self.backup_path / "backup_manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print("   ✅ Backup manifest created")
    
    def _create_compressed_backup(self):
        """Create a compressed backup archive"""
        print("🗜️  Creating compressed backup...")
        
        zip_path = f"{self.backup_path}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.backup_path)
                    zipf.write(file_path, arcname)
        
        # Calculate compressed size
        compressed_size = os.path.getsize(zip_path) / (1024 * 1024)
        print(f"   ✅ Compressed backup created ({compressed_size:.2f} MB)")
    
    def list_backups(self):
        """List all available backups"""
        print("📋 Available ChromaDB Backups:")
        print("=" * 50)
        
        if not self.backup_dir.exists():
            print("No backups found.")
            return
        
        backups = []
        for item in self.backup_dir.iterdir():
            if item.is_dir() and item.name.startswith("chroma_backup_"):
                backup_info = {
                    "name": item.name,
                    "path": item,
                    "created": datetime.fromtimestamp(item.stat().st_mtime),
                    "size_mb": sum(f.stat().st_size for f in item.rglob('*') if f.is_file()) / (1024 * 1024)
                }
                backups.append(backup_info)
        
        if not backups:
            print("No backups found.")
            return
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        for i, backup in enumerate(backups):
            print(f"{i+1}. {backup['name']}")
            print(f"   Created: {backup['created'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Size: {backup['size_mb']:.2f} MB")
            print(f"   Path: {backup['path']}")
            print()

def main():
    """Main function to run the backup"""
    backup = ChromaDBBackup()
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        backup.list_backups()
    else:
        success = backup.create_backup()
        if success:
            print("\n🎉 Backup completed successfully!")
            print("💡 To restore from this backup, use: python restore_chromadb.py")
        else:
            print("\n❌ Backup failed!")
            sys.exit(1)

if __name__ == "__main__":
    main() 