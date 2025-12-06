"""
Simple JSON-based storage for reviews/feedback
More appropriate than ChromaDB for structured review data
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from threading import Lock

# Thread-safe file operations
_file_lock = Lock()

# Storage file path
STORAGE_DIR = Path(__file__).parent.parent.parent / "data"
STORAGE_FILE = STORAGE_DIR / "reviews.json"

# Ensure storage directory exists
STORAGE_DIR.mkdir(exist_ok=True)


class ReviewStorage:
    """Simple JSON-based storage for reviews"""
    
    def __init__(self, storage_file: Optional[Path] = None):
        self.storage_file = storage_file or STORAGE_FILE
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create storage file if it doesn't exist"""
        if not self.storage_file.exists():
            with _file_lock:
                with open(self.storage_file, 'w', encoding='utf-8') as f:
                    json.dump({"reviews": []}, f, indent=2)
    
    def _read_reviews(self) -> List[Dict[str, Any]]:
        """Read all reviews from storage"""
        with _file_lock:
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('reviews', [])
            except (FileNotFoundError, json.JSONDecodeError):
                return []
    
    def _write_reviews(self, reviews: List[Dict[str, Any]]):
        """Write reviews to storage"""
        with _file_lock:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump({"reviews": reviews}, f, indent=2, ensure_ascii=False)
    
    def store_review(self, review_data: Dict[str, Any]) -> str:
        """
        Store a review
        
        Args:
            review_data: Dictionary containing review information
            
        Returns:
            Review ID
        """
        # Generate unique ID
        review_id = str(uuid.uuid4())
        
        # Prepare review entry
        review_entry = {
            'id': review_id,
            'session_id': review_data.get('session_id', ''),
            'rating': review_data.get('rating', 0),
            'feedback_type': review_data.get('feedback_type', 'general'),
            'feedback_text': review_data.get('feedback_text', ''),
            'email': review_data.get('email', ''),
            'user_agent': review_data.get('user_agent', ''),
            'page_url': review_data.get('page_url', ''),
            'timestamp': review_data.get('timestamp', datetime.now().isoformat()),
            'created_at': review_data.get('created_at', datetime.now().isoformat())
        }
        
        # Read existing reviews
        reviews = self._read_reviews()
        
        # Add new review
        reviews.append(review_entry)
        
        # Write back to file
        self._write_reviews(reviews)
        
        print(f"[REVIEW STORAGE] Stored review: Rating {review_entry['rating']}/5, Type: {review_entry['feedback_type']}")
        
        return review_id
    
    def get_all_reviews(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all reviews
        
        Args:
            limit: Maximum number of reviews to return
            offset: Number of reviews to skip
            
        Returns:
            List of review dictionaries
        """
        reviews = self._read_reviews()
        
        # Sort by created_at (newest first)
        reviews.sort(key=lambda x: x.get('created_at', x.get('timestamp', '')), reverse=True)
        
        # Apply pagination
        if offset > 0:
            reviews = reviews[offset:]
        if limit:
            reviews = reviews[:limit]
        
        return reviews
    
    def get_review_stats(self) -> Dict[str, Any]:
        """Get statistics about reviews"""
        reviews = self._read_reviews()
        
        if not reviews:
            return {
                'total_reviews': 0,
                'average_rating': 0,
                'rating_distribution': {i: 0 for i in range(1, 6)},
                'feedback_types': {}
            }
        
        # Calculate statistics
        total_reviews = len(reviews)
        ratings = [r.get('rating', 0) for r in reviews if 1 <= r.get('rating', 0) <= 5]
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Rating distribution
        rating_distribution = {i: 0 for i in range(1, 6)}
        for rating in ratings:
            rating_distribution[rating] = rating_distribution.get(rating, 0) + 1
        
        # Feedback type distribution
        feedback_types = {}
        for review in reviews:
            ftype = review.get('feedback_type', 'general')
            feedback_types[ftype] = feedback_types.get(ftype, 0) + 1
        
        return {
            'total_reviews': total_reviews,
            'average_rating': round(average_rating, 2),
            'rating_distribution': rating_distribution,
            'feedback_types': feedback_types
        }
    
    def get_reviews_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get reviews for a specific session"""
        reviews = self._read_reviews()
        return [r for r in reviews if r.get('session_id') == session_id]
    
    def export_to_csv(self, output_file: Optional[Path] = None) -> Path:
        """Export reviews to CSV file"""
        import csv
        
        output_file = output_file or STORAGE_DIR / "reviews_export.csv"
        reviews = self._read_reviews()
        
        if not reviews:
            return output_file
        
        # Get all unique keys
        fieldnames = set()
        for review in reviews:
            fieldnames.update(review.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(reviews)
        
        print(f"[REVIEW STORAGE] Exported {len(reviews)} reviews to {output_file}")
        return output_file


# Global instance
review_storage = ReviewStorage()

