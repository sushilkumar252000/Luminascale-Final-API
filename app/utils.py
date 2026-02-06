"""
Utility functions for the API
"""

import logging
from fastapi import Request

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.
    Handles X-Forwarded-For header (proxy/load balancer).
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address string
    """
    # Check for X-Forwarded-For (from proxy/load balancer)
    xff = request.headers.get("x-forwarded-for")
    if xff:
        # Take first IP from comma-separated list
        ip = xff.split(",")[0].strip()
        logger.debug(f"Client IP from X-Forwarded-For: {ip}")
        return ip
    
    # Fall back to direct connection
    ip = request.client.host if request.client else "unknown"
    logger.debug(f"Client IP from connection: {ip}")
    return ip


def format_image_size(size_bytes: int) -> str:
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}GB"
