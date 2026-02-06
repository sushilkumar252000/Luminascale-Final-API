"""
API Key Authentication for Free Tier
Simple API key validation without database
"""

import os
import logging
import hashlib
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Free tier API key (stored in environment)
FREE_API_KEY = os.getenv("FREE_API_KEY", "freeApiluminascalem!+|I1,R1u31C_V")
FREE_API_KEY_HASH = hashlib.sha256(FREE_API_KEY.encode()).hexdigest()


def hash_api_key(key: str) -> str:
    """Hash API key for validation"""
    return hashlib.sha256(key.encode()).hexdigest()


def validate_api_key(api_key: Optional[str]) -> Tuple[bool, str]:
    """
    Validate API key for free tier.
    
    Args:
        api_key: API key from request header (X-API-Key)
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not api_key:
        logger.warning("No API key provided")
        return False, "Missing X-API-Key header"
    
    if not api_key.strip():
        logger.warning("Empty API key provided")
        return False, "API key cannot be empty"
    
    # Hash provided key and compare
    provided_hash = hash_api_key(api_key)
    
    if provided_hash == FREE_API_KEY_HASH:
        logger.info("✅ Valid free tier API key")
        return True, "Valid"
    else:
        logger.warning(f"❌ Invalid API key attempt")
        return False, "Invalid API key"


def get_free_api_key_name() -> str:
    """Get the free tier API key name for documentation"""
    return "freeApiluminascalem"
