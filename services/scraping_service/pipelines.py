import sys
import os
from datetime import datetime

# Add parent directory to path - fix the path calculation
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
sys.path.insert(0, project_root)

# Import with correct path
from services.shared.chroma_service import ChromaService
from services.shared.config import config
from change_detector import ChangeDetector

class ChangeDetectionPipeline:
    def __init__(self):
        self.change_detector = ChangeDetector()
    
    def process_item(self, item, spider):
        # Extract meaningful content and generate hash
        meaningful_content = self.change_detector.extract_meaningful_content(item['content'])
        content_hash = self.change_detector.generate_content_hash(meaningful_content)
        
        # Store the hash and cleaned content
        item['content_hash'] = content_hash
        item['content'] = meaningful_content
        
        return item

class ChromaDBPipeline:
    def __init__(self):
        self.chroma_service = ChromaService()
    
    def process_item(self, item, spider):
        try:
            # Get or create university - search by name in all universities
            universities = self.chroma_service.get_all_universities()
            university = None
            
            for univ in universities:
                if univ.name == item['university_name']:
                    university = univ
                    break
            
            if not university:
                # Extract base URL from the scraped URL
                from urllib.parse import urlparse
                parsed_url = urlparse(item['url'])
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
                university = self.chroma_service.create_university(
                    name=item['university_name'],
                    base_url=base_url
                )
            
            # Check if content has changed by comparing hashes
            existing_docs = self.chroma_service.search_documents(
                query=item['url'],  # Search by URL
                n_results=1
            )
            
            has_changed = True
            if existing_docs:
                existing_doc, _ = existing_docs[0]
                has_changed = existing_doc.content_hash != item['content_hash']
            
            if has_changed and university and university.id:
                # Extract file name from URL path
                from urllib.parse import urlparse
                parsed_url = urlparse(item['url'])
                path_parts = parsed_url.path.strip('/').split('/')
                file_name = path_parts[-1] if path_parts else 'index.html'
                if not file_name or file_name.isspace():
                    file_name = 'index.html'
                if not '.' in file_name:
                    file_name += '.html'
                
                # Create metadata dictionary with file name
                metadata = {
                    'file_name': file_name,  # Include file name in metadata
                    'content_hash': item['content_hash'],
                    'status_code': item.get('metadata', {}).get('status_code'),
                    'content_length': item.get('metadata', {}).get('content_length'),
                    'page_type': item.get('metadata', {}).get('page_type'),
                    'scraped_at': item['scraped_at']
                }
                
                self.chroma_service.create_document(
                    source_url=item['url'],
                    title=item['title'],
                    content=item['content'],
                    university_id=university.id,
                    file_name=file_name,  # Pass file name explicitly
                    extra_data=metadata  # Pass complete metadata dictionary
                )
                
                # Update university last scraped time
                self.chroma_service.update_university(
                    university.id,
                    last_scraped=datetime.now().isoformat()
                )
                
                spider.logger.info(f"Content changed for {item['url']}")
            else:
                spider.logger.info(f"No changes detected for {item['url']}")
            
        except Exception as e:
            spider.logger.error(f"Error processing item: {e}")
            raise
        
        return item