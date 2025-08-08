#!/usr/bin/env python3
"""
ChromaDB Restore Script
Restores ChromaDB from a backup created by backup_chromadb.py
"""

import os
import sys
import shutil
import json
import zipfile
from datetime import datetime
from pathlib import Path

class ChromaDBRestore:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.chroma_data_dir = self.project_root / "chroma_data"
        self.backup_dir = self.project_root / "chroma_backups"
        
    def list_backups(self):
        """List all available backups"""
        print("📋 Available ChromaDB Backups:")
        print("=" * 50)
        
        if not self.backup_dir.exists():
            print("No backups found.")
            return []
        
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
            return []
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        for i, backup in enumerate(backups):
            print(f"{i+1}. {backup['name']}")
            print(f"   Created: {backup['created'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Size: {backup['size_mb']:.2f} MB")
            print(f"   Path: {backup['path']}")
            print()
        
        return backups
    
    def restore_from_backup(self, backup_name=None, backup_index=None):
        """Restore ChromaDB from a backup"""
        print("🔄 Starting ChromaDB Restore...")
        
        # Find the backup to restore from
        backup_path = self._find_backup(backup_name, backup_index)
        if not backup_path:
            return False
        
        print(f"📦 Restoring from: {backup_path}")
        
        try:
            # Check if backup is compressed
            if backup_path.suffix == '.zip':
                return self._restore_from_compressed_backup(backup_path)
            else:
                return self._restore_from_directory_backup(backup_path)
                
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def _find_backup(self, backup_name=None, backup_index=None):
        """Find the backup to restore from"""
        if not self.backup_dir.exists():
            print("❌ No backup directory found")
            return None
        
        backups = []
        for item in self.backup_dir.iterdir():
            if (item.is_dir() and item.name.startswith("chroma_backup_")) or \
               (item.is_file() and item.name.startswith("chroma_backup_") and item.suffix == '.zip'):
                backups.append(item)
        
        if not backups:
            print("❌ No backups found")
            return None
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if backup_name:
            # Find by name
            for backup in backups:
                if backup.name == backup_name or backup.name == f"{backup_name}.zip":
                    return backup
            print(f"❌ Backup '{backup_name}' not found")
            return None
        
        elif backup_index is not None:
            # Find by index
            if 0 <= backup_index < len(backups):
                return backups[backup_index]
            else:
                print(f"❌ Invalid backup index: {backup_index}")
                return None
        
        else:
            # Use the most recent backup
            print(f"📦 Using most recent backup: {backups[0].name}")
            return backups[0]
    
    def _restore_from_directory_backup(self, backup_path):
        """Restore from a directory backup"""
        print("📁 Restoring from directory backup...")
        
        # Verify backup structure
        manifest_path = backup_path / "backup_manifest.json"
        if not manifest_path.exists():
            print("❌ Backup manifest not found")
            return False
        
        # Read manifest
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        print(f"📋 Backup info: {manifest['backup_info']['name']}")
        print(f"📅 Created: {manifest['backup_info']['created_at']}")
        
        # Stop ChromaDB if running (optional)
        print("⚠️  Please stop ChromaDB server if it's running")
        input("Press Enter to continue...")
        
        # Create backup of current ChromaDB
        current_backup = self._create_current_backup()
        
        try:
            # Restore SQLite database
            sqlite_backup = backup_path / "chroma.sqlite3"
            if sqlite_backup.exists():
                print("📊 Restoring SQLite database...")
                shutil.copy2(sqlite_backup, self.chroma_data_dir / "chroma.sqlite3")
                print("   ✅ SQLite database restored")
            
            # Restore embedding files
            embedding_backup = backup_path / "embeddings"
            if embedding_backup.exists():
                print("🔍 Restoring embedding files...")
                
                # Remove existing embedding directories
                for item in self.chroma_data_dir.iterdir():
                    if item.is_dir() and item.name != "__pycache__":
                        shutil.rmtree(item)
                        print(f"   🗑️  Removed existing collection: {item.name}")
                
                # Copy embedding directories
                for collection_dir in embedding_backup.iterdir():
                    if collection_dir.is_dir():
                        dest_dir = self.chroma_data_dir / collection_dir.name
                        shutil.copytree(collection_dir, dest_dir)
                        print(f"   ✅ Restored collection: {collection_dir.name}")
            
            print("✅ Restore completed successfully!")
            print(f"💾 Previous version backed up to: {current_backup}")
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            print(f"🔄 Restoring previous version from: {current_backup}")
            self._restore_from_directory_backup(current_backup)
            return False
    
    def _restore_from_compressed_backup(self, backup_path):
        """Restore from a compressed backup"""
        print("🗜️  Restoring from compressed backup...")
        
        # Extract to temporary directory
        temp_extract_dir = self.project_root / f"temp_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        temp_extract_dir.mkdir(exist_ok=True)
        
        try:
            print("📦 Extracting backup...")
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_extract_dir)
            
            # Find the extracted backup directory
            extracted_backups = [d for d in temp_extract_dir.iterdir() if d.is_dir() and d.name.startswith("chroma_backup_")]
            if not extracted_backups:
                print("❌ No valid backup found in compressed file")
                return False
            
            extracted_backup = extracted_backups[0]
            print(f"📁 Extracted to: {extracted_backup}")
            
            # Restore from extracted directory
            success = self._restore_from_directory_backup(extracted_backup)
            
            return success
            
        finally:
            # Clean up temporary directory
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)
                print("🧹 Cleaned up temporary files")
    
    def _create_current_backup(self):
        """Create a backup of current ChromaDB before restore"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup_name = f"chroma_backup_before_restore_{timestamp}"
        current_backup_path = self.backup_dir / current_backup_name
        
        if self.chroma_data_dir.exists():
            print(f"💾 Creating backup of current ChromaDB...")
            current_backup_path.mkdir(exist_ok=True)
            
            # Copy current SQLite database
            current_sqlite = self.chroma_data_dir / "chroma.sqlite3"
            if current_sqlite.exists():
                shutil.copy2(current_sqlite, current_backup_path / "chroma.sqlite3")
            
            # Copy current embedding files
            current_embeddings = current_backup_path / "embeddings"
            current_embeddings.mkdir(exist_ok=True)
            
            for item in self.chroma_data_dir.iterdir():
                if item.is_dir() and item.name != "__pycache__":
                    dest_dir = current_embeddings / item.name
                    shutil.copytree(item, dest_dir)
            
            print(f"   ✅ Current version backed up to: {current_backup_path}")
            return current_backup_path
        
        return None
    
    def verify_restore(self):
        """Verify that the restore was successful"""
        print("🔍 Verifying restore...")
        
        try:
            # Check if ChromaDB files exist
            sqlite_file = self.chroma_data_dir / "chroma.sqlite3"
            if not sqlite_file.exists():
                print("❌ SQLite database not found")
                return False
            
            # Check for embedding collections
            embedding_collections = [d for d in self.chroma_data_dir.iterdir() if d.is_dir() and d.name != "__pycache__"]
            if not embedding_collections:
                print("❌ No embedding collections found")
                return False
            
            print(f"✅ Restore verification passed")
            print(f"   📊 SQLite database: {sqlite_file.stat().st_size / (1024 * 1024):.2f} MB")
            print(f"   🔍 Embedding collections: {len(embedding_collections)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False

def main():
    """Main function to run the restore"""
    restore = ChromaDBRestore()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python restore_chromadb.py list                    # List available backups")
        print("  python restore_chromadb.py restore                 # Restore from most recent backup")
        print("  python restore_chromadb.py restore <backup_name>   # Restore from specific backup")
        print("  python restore_chromadb.py restore --index <N>     # Restore from backup index N")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        restore.list_backups()
    
    elif command == "restore":
        if len(sys.argv) > 2:
            if sys.argv[2] == "--index" and len(sys.argv) > 3:
                # Restore by index
                try:
                    backup_index = int(sys.argv[3])
                    success = restore.restore_from_backup(backup_index=backup_index)
                except ValueError:
                    print("❌ Invalid backup index")
                    return
            else:
                # Restore by name
                backup_name = sys.argv[2]
                success = restore.restore_from_backup(backup_name=backup_name)
        else:
            # Restore from most recent
            success = restore.restore_from_backup()
        
        if success:
            print("\n🎉 Restore completed successfully!")
            print("🔍 Verifying restore...")
            if restore.verify_restore():
                print("✅ Restore verification passed!")
                print("🚀 You can now start ChromaDB and your chatbot")
            else:
                print("⚠️  Restore verification failed - check the logs")
        else:
            print("\n❌ Restore failed!")
            sys.exit(1)
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main() 