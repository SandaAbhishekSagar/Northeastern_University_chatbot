import hashlib
from bs4 import BeautifulSoup
import re
from typing import Optional

class ChangeDetector:
    def __init__(self):
        self.dynamic_selectors = [
            '[class*="timestamp"]', '[class*="date"]', '[class*="time"]',
            '[id*="session"]', '[class*="counter"]', '[class*="visitor"]',
            '[class*="social"]', '[class*="share"]', '.breadcrumb'
        ]
    
    def extract_meaningful_content(self, html_content: str) -> str:
        """Extract meaningful content, filtering out dynamic elements"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove scripts, styles, and navigation
        for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Remove dynamic elements
        for selector in self.dynamic_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Focus on main content
        main_content = soup.find(['main', 'article', '.content', '#content', '.main'])
        if main_content:
            content = main_content.get_text(strip=True)
        else:
            content = soup.get_text(strip=True)
        
        # Clean up whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        return content
    
    def generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def has_content_changed(self, new_content: str, old_hash: Optional[str]) -> tuple[bool, str]:
        """Check if content has changed compared to old hash"""
        meaningful_content = self.extract_meaningful_content(new_content)
        new_hash = self.generate_content_hash(meaningful_content)
        
        if old_hash is None:
            return True, new_hash  # New content
        
        return new_hash != old_hash, new_hash