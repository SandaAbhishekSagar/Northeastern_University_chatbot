#!/usr/bin/env python3
"""
Check the structure of the backup database
"""

import sqlite3
import os

def check_database_structure(backup_file):
    """Check the structure of the backup database"""
    print(f"🔍 Checking database structure: {backup_file}")
    
    if not os.path.exists(backup_file):
        print(f"❌ File not found: {backup_file}")
        return
    
    try:
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📊 Found {len(tables)} tables:")
        for (table_name,) in tables:
            print(f"  - {table_name}")
        
        # Check collections table structure
        if any('collections' in table[0] for table in tables):
            print("\n🔍 Collections table structure:")
            cursor.execute("PRAGMA table_info(collections)")
            cols = cursor.fetchall()
            for col in cols:
                print(f"  - {col[1]} ({col[2]})")
        
        # Check for any table with documents
        for (table_name,) in tables:
            if 'document' in table_name.lower() or 'embedding' in table_name.lower():
                print(f"\n🔍 {table_name} structure:")
                cursor.execute(f"PRAGMA table_info({table_name})")
                cols = cursor.fetchall()
                for col in cols:
                    print(f"  - {col[1]} ({col[2]})")
                
                # Check row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  📊 Row count: {count}")
                
                # Show sample data
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    sample = cursor.fetchone()
                    print(f"  📝 Sample row: {sample}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    backup_file = "chroma_backups/chroma_backup_20250809_112404/chroma.sqlite3"
    check_database_structure(backup_file)
