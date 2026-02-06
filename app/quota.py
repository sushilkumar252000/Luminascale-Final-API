"""
Rate limiting and quota management using Redis
Tracks daily requests per IP address
Redis is optional - if unavailable, rate limiting is disabled
"""

import os
import time
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "")
FREE_DAILY_LIMIT = int(os.getenv("FREE_DAILY_LIMIT", "10000"))

r: Optional[object] = None
REDIS_AVAILABLE = False

if REDIS_URL:
    try:
        import redis
        r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        r.ping()
        logger.info(f"Redis connected: {REDIS_URL}")
        REDIS_AVAILABLE = True
    except Exception as e:
        logger.warning(f"Redis connection failed: {e} - rate limiting disabled")
        r = None
else:
    logger.info("No REDIS_URL configured - rate limiting disabled")


def get_day_bucket() -> str:
    """Get current UTC day in YYYY-MM-DD format"""
    return time.strftime("%Y-%m-%d", time.gmtime())


def check_and_increment_ip_quota(ip: str) -> Tuple[bool, int, int, str]:
    """
    Check and increment IP quota.
    
    Args:
        ip: Client IP address
        
    Returns:
        Tuple of (allowed, used, limit, reset_time)
    """
    if not REDIS_AVAILABLE or r is None:
        return True, 0, FREE_DAILY_LIMIT, ""
    
    day = get_day_bucket()
    key = f"quota:ip:{ip}:{day}"
    
    try:
        used = r.incr(key)
        
        if used == 1:
            r.expire(key, 60 * 60 * 36)
            logger.info(f"New quota bucket created for IP {ip}: {day}")
        
        allowed = used <= FREE_DAILY_LIMIT
        reset_time = f"{day}T23:59:59Z"
        
        return allowed, used, FREE_DAILY_LIMIT, reset_time
        
    except Exception as e:
        logger.error(f"Quota check failed for {ip}: {e}")
        return True, 0, FREE_DAILY_LIMIT, ""


def check_and_increment_api_key_quota(api_key_name: str) -> Tuple[bool, int, int, str]:
    """
    Check and increment API key quota (for authenticated requests).
    
    Args:
        api_key_name: Free API key identifier
        
    Returns:
        Tuple of (allowed, used, limit, reset_time)
    """
    if not REDIS_AVAILABLE or r is None:
        return True, 0, FREE_DAILY_LIMIT, ""
    
    day = get_day_bucket()
    key = f"quota:apikey:{api_key_name}:{day}"
    
    try:
        used = r.incr(key)
        
        if used == 1:
            r.expire(key, 60 * 60 * 36)
            logger.info(f"New quota bucket created for API key {api_key_name}: {day}")
        
        allowed = used <= FREE_DAILY_LIMIT
        reset_time = f"{day}T23:59:59Z"
        
        return allowed, used, FREE_DAILY_LIMIT, reset_time
        
    except Exception as e:
        logger.error(f"Quota check failed for API key {api_key_name}: {e}")
        return True, 0, FREE_DAILY_LIMIT, ""


def get_quota_stats() -> dict:
    """Get global quota statistics (for monitoring)"""
    if not REDIS_AVAILABLE or r is None:
        return {"redis_connected": False}
    
    try:
        ip_keys = r.keys("quota:ip:*")
        apikey_keys = r.keys("quota:apikey:*")
        total_requests = sum(int(r.get(k)) for k in ip_keys + apikey_keys if r.get(k))
        return {
            "total_ips_today": len(ip_keys),
            "total_api_keys_today": len(apikey_keys),
            "total_requests_today": total_requests,
            "redis_connected": True
        }
    except Exception as e:
        logger.error(f"Failed to get quota stats: {e}")
        return {"redis_connected": False}
