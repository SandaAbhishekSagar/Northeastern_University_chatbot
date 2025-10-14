"""
Bulk Data Import Script for Northeastern University Chatbot
Supports: JSON, CSV, TXT files
Author: Enhanced GPU Chatbot System
Date: 2025-01-07
"""

import sys
import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.shared.chroma_service import chroma_service
from services.shared.models import University

class BulkImporter:
    """Handles bulk import of documents from various file formats"""
    
    def __init__(self, university_name: str = "Northeastern University", 
                 university_url: str = "https://www.northeastern.edu"):
        """
        Initialize the bulk importer
        
        Args:
            university_name: Name of the university
            university_url: Base URL of the university
        """
        self.university_name = university_name
        self.university_url = university_url
        self.university = None
        self.stats = {
            'total_files': 0,
            'successful_imports': 0,
            'failed_imports': 0,
            'skipped': 0,
            'errors': []
        }
    
    def _ensure_university(self) -> University:
        """Ensure university exists in database"""
        if self.university:
            return self.university
        
        # Try to get existing university
        self.university = chroma_service.get_university_by_name(self.university_name)
        
        # Create if doesn't exist
        if not self.university:
            print(f"📝 Creating university: {self.university_name}")
            self.university = chroma_service.create_university(
                name=self.university_name,
                base_url=self.university_url
            )
            print(f"✅ University created with ID: {self.university.id}")
        else:
            print(f"✅ Found existing university: {self.university_name} (ID: {self.university.id})")
        
        return self.university
    
    def import_json(self, file_path: str) -> int:
        """
        Import documents from JSON file
        
        Expected JSON format:
        [
            {
                "title": "Document Title",
                "content": "Document content...",
                "source_url": "https://example.edu/page",
                "metadata": {
                    "key": "value"
                }
            }
        ]
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Number of documents imported
        """
        print(f"\n📄 Importing JSON file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                data = [data]  # Convert single object to list
            
            university = self._ensure_university()
            imported = 0
            
            for i, item in enumerate(data, 1):
                try:
                    # Validate required fields
                    if 'content' not in item:
                        print(f"⚠️  Skipping item {i}: Missing 'content' field")
                        self.stats['skipped'] += 1
                        continue
                    
                    # Extract fields with defaults
                    title = item.get('title', f"Document {i}")
                    content = item['content']
                    source_url = item.get('source_url', f"bulk_import/{Path(file_path).stem}/{i}")
                    metadata = item.get('metadata', {})
                    
                    # Add import metadata
                    metadata['import_source'] = 'bulk_import_json'
                    metadata['import_file'] = Path(file_path).name
                    metadata['import_timestamp'] = datetime.now().isoformat()
                    
                    # Create document
                    doc = chroma_service.create_document(
                        source_url=source_url,
                        title=title,
                        content=content,
                        university_id=university.id,
                        extra_data=metadata
                    )
                    
                    print(f"  ✅ [{i}/{len(data)}] Imported: {title}")
                    imported += 1
                    self.stats['successful_imports'] += 1
                    
                except Exception as e:
                    error_msg = f"Error importing item {i}: {str(e)}"
                    print(f"  ❌ {error_msg}")
                    self.stats['failed_imports'] += 1
                    self.stats['errors'].append(error_msg)
            
            return imported
            
        except Exception as e:
            error_msg = f"Error reading JSON file {file_path}: {str(e)}"
            print(f"❌ {error_msg}")
            self.stats['failed_imports'] += 1
            self.stats['errors'].append(error_msg)
            return 0
    
    def import_csv(self, file_path: str, 
                   title_column: str = 'title',
                   content_column: str = 'content',
                   url_column: str = 'source_url') -> int:
        """
        Import documents from CSV file
        
        Expected CSV format:
        title,content,source_url,additional_field1,additional_field2
        "Title","Content...","https://example.edu/page","value1","value2"
        
        Args:
            file_path: Path to CSV file
            title_column: Name of column containing titles
            content_column: Name of column containing content
            url_column: Name of column containing URLs
            
        Returns:
            Number of documents imported
        """
        print(f"\n📊 Importing CSV file: {file_path}")
        
        try:
            university = self._ensure_university()
            imported = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                print(f"📋 Found {len(rows)} rows in CSV")
                
                for i, row in enumerate(rows, 1):
                    try:
                        # Validate required fields
                        if content_column not in row or not row[content_column]:
                            print(f"⚠️  Skipping row {i}: Missing or empty '{content_column}' field")
                            self.stats['skipped'] += 1
                            continue
                        
                        # Extract fields
                        title = row.get(title_column, f"Document {i}")
                        content = row[content_column]
                        source_url = row.get(url_column, f"bulk_import/{Path(file_path).stem}/{i}")
                        
                        # All other columns become metadata
                        metadata = {
                            k: v for k, v in row.items() 
                            if k not in [title_column, content_column, url_column] and v
                        }
                        
                        # Add import metadata
                        metadata['import_source'] = 'bulk_import_csv'
                        metadata['import_file'] = Path(file_path).name
                        metadata['import_timestamp'] = datetime.now().isoformat()
                        
                        # Create document
                        doc = chroma_service.create_document(
                            source_url=source_url,
                            title=title,
                            content=content,
                            university_id=university.id,
                            extra_data=metadata
                        )
                        
                        print(f"  ✅ [{i}/{len(rows)}] Imported: {title}")
                        imported += 1
                        self.stats['successful_imports'] += 1
                        
                    except Exception as e:
                        error_msg = f"Error importing row {i}: {str(e)}"
                        print(f"  ❌ {error_msg}")
                        self.stats['failed_imports'] += 1
                        self.stats['errors'].append(error_msg)
            
            return imported
            
        except Exception as e:
            error_msg = f"Error reading CSV file {file_path}: {str(e)}"
            print(f"❌ {error_msg}")
            self.stats['failed_imports'] += 1
            self.stats['errors'].append(error_msg)
            return 0
    
    def import_txt(self, file_path: str, title: Optional[str] = None) -> int:
        """
        Import a single text file as a document
        
        Args:
            file_path: Path to TXT file
            title: Optional title (defaults to filename)
            
        Returns:
            Number of documents imported (0 or 1)
        """
        print(f"\n📝 Importing TXT file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                print(f"⚠️  Skipping empty file: {file_path}")
                self.stats['skipped'] += 1
                return 0
            
            university = self._ensure_university()
            
            # Generate title from filename if not provided
            if not title:
                title = Path(file_path).stem.replace('_', ' ').replace('-', ' ').title()
            
            source_url = f"file://{Path(file_path).name}"
            
            metadata = {
                'import_source': 'bulk_import_txt',
                'import_file': Path(file_path).name,
                'import_timestamp': datetime.now().isoformat(),
                'file_size': len(content)
            }
            
            # Create document
            doc = chroma_service.create_document(
                source_url=source_url,
                title=title,
                content=content,
                university_id=university.id,
                file_name=Path(file_path).name,
                extra_data=metadata
            )
            
            print(f"  ✅ Imported: {title}")
            self.stats['successful_imports'] += 1
            return 1
            
        except Exception as e:
            error_msg = f"Error importing TXT file {file_path}: {str(e)}"
            print(f"❌ {error_msg}")
            self.stats['failed_imports'] += 1
            self.stats['errors'].append(error_msg)
            return 0
    
    def import_directory(self, directory_path: str, recursive: bool = True) -> int:
        """
        Import all supported files from a directory
        
        Args:
            directory_path: Path to directory
            recursive: Whether to search subdirectories
            
        Returns:
            Total number of documents imported
        """
        print(f"\n📁 Importing from directory: {directory_path}")
        
        directory = Path(directory_path)
        if not directory.exists():
            print(f"❌ Directory not found: {directory_path}")
            return 0
        
        total_imported = 0
        pattern = '**/*' if recursive else '*'
        
        # Process JSON files
        json_files = list(directory.glob(f'{pattern}.json'))
        for json_file in json_files:
            self.stats['total_files'] += 1
            total_imported += self.import_json(str(json_file))
        
        # Process CSV files
        csv_files = list(directory.glob(f'{pattern}.csv'))
        for csv_file in csv_files:
            self.stats['total_files'] += 1
            total_imported += self.import_csv(str(csv_file))
        
        # Process TXT files
        txt_files = list(directory.glob(f'{pattern}.txt'))
        for txt_file in txt_files:
            self.stats['total_files'] += 1
            total_imported += self.import_txt(str(txt_file))
        
        return total_imported
    
    def print_summary(self):
        """Print import summary statistics"""
        print("\n" + "="*60)
        print("📊 IMPORT SUMMARY")
        print("="*60)
        print(f"Total Files Processed: {self.stats['total_files']}")
        print(f"✅ Successfully Imported: {self.stats['successful_imports']}")
        print(f"❌ Failed Imports: {self.stats['failed_imports']}")
        print(f"⚠️  Skipped: {self.stats['skipped']}")
        
        if self.stats['errors']:
            print(f"\n❌ Errors ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more errors")
        
        print("="*60)


def main():
    """Main function to run bulk import"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Bulk import documents into Northeastern University Chatbot database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import a single JSON file
  python bulk_import.py --json data.json
  
  # Import a single CSV file
  python bulk_import.py --csv data.csv
  
  # Import all files from a directory
  python bulk_import.py --directory ./data
  
  # Import with custom university
  python bulk_import.py --json data.json --university "MIT" --url "https://mit.edu"
  
  # Import CSV with custom column names
  python bulk_import.py --csv data.csv --title-col "name" --content-col "text"
        """
    )
    
    # Input options
    parser.add_argument('--json', type=str, help='Path to JSON file')
    parser.add_argument('--csv', type=str, help='Path to CSV file')
    parser.add_argument('--txt', type=str, help='Path to TXT file')
    parser.add_argument('--directory', '-d', type=str, help='Path to directory containing files')
    parser.add_argument('--recursive', '-r', action='store_true', 
                       help='Search subdirectories (used with --directory)')
    
    # University options
    parser.add_argument('--university', '-u', type=str, 
                       default='Northeastern University',
                       help='University name (default: Northeastern University)')
    parser.add_argument('--url', type=str, 
                       default='https://www.northeastern.edu',
                       help='University base URL')
    
    # CSV-specific options
    parser.add_argument('--title-col', type=str, default='title',
                       help='CSV column name for titles (default: title)')
    parser.add_argument('--content-col', type=str, default='content',
                       help='CSV column name for content (default: content)')
    parser.add_argument('--url-col', type=str, default='source_url',
                       help='CSV column name for URLs (default: source_url)')
    
    args = parser.parse_args()
    
    # Validate input
    if not any([args.json, args.csv, args.txt, args.directory]):
        parser.print_help()
        print("\n❌ Error: Please specify at least one input source (--json, --csv, --txt, or --directory)")
        sys.exit(1)
    
    # Create importer
    print("="*60)
    print("🚀 BULK DATA IMPORT TOOL")
    print("="*60)
    print(f"University: {args.university}")
    print(f"Base URL: {args.url}")
    print("="*60)
    
    importer = BulkImporter(
        university_name=args.university,
        university_url=args.url
    )
    
    # Perform imports
    total_imported = 0
    
    if args.json:
        importer.stats['total_files'] += 1
        total_imported += importer.import_json(args.json)
    
    if args.csv:
        importer.stats['total_files'] += 1
        total_imported += importer.import_csv(
            args.csv,
            title_column=args.title_col,
            content_column=args.content_col,
            url_column=args.url_col
        )
    
    if args.txt:
        importer.stats['total_files'] += 1
        total_imported += importer.import_txt(args.txt)
    
    if args.directory:
        total_imported += importer.import_directory(args.directory, args.recursive)
    
    # Print summary
    importer.print_summary()
    
    # Verify database
    print(f"\n🔍 Verifying database...")
    doc_count = chroma_service.get_collection_count('documents')
    print(f"📊 Total documents in database: {doc_count:,}")
    
    print(f"\n✅ Import complete! Imported {total_imported} documents.")


if __name__ == "__main__":
    main()

