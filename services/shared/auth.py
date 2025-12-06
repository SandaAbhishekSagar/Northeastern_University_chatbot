"""
Simple authentication for review endpoints
Uses API key from environment variable
"""

import os
from fastapi import HTTPException, Header
from typing import Optional

# Admin API key - set via environment variable
# IMPORTANT: Change this default key in production!
ADMIN_API_KEY = os.getenv("REVIEW_ADMIN_KEY", "change-this-to-secure-key-12345")

# Security: Warn if using default key in production
if ADMIN_API_KEY == "change-this-to-secure-key-12345" and os.getenv("ENVIRONMENT") == "production":
    print("[SECURITY WARNING] Using default API key! Set REVIEW_ADMIN_KEY environment variable.")

def verify_admin_key(authorization: Optional[str] = Header(None)) -> bool:
    """
    Verify admin API key from Authorization header
    
    Usage:
        @app.get("/reviews")
        async def get_reviews(auth: bool = Depends(verify_admin_key)):
            ...
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization required. Please provide API key in Authorization header."
        )
    
    # Support both "Bearer <key>" and direct key
    if authorization.startswith("Bearer "):
        provided_key = authorization.replace("Bearer ", "").strip()
    else:
        provided_key = authorization.strip()
    
    if provided_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key. Access denied."
        )
    
    return True

def verify_admin_key_query(api_key: Optional[str] = None) -> bool:
    """
    Verify admin API key from query parameter (for browser access)
    
    Usage:
        @app.get("/reviews")
        async def get_reviews(api_key: str = None, auth: bool = Depends(verify_admin_key_query)):
            ...
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Add ?api_key=YOUR_KEY to the URL."
        )
    
    if api_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key. Access denied."
        )
    
    return True

