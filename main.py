"""
GFPGAN Free Tier Production API
High-performance REST API for face restoration and upscaling

Features:
- Face enhancement with GFPGAN
- 2x & 4x upscaling with Real-ESRGAN
- Free API Key authentication: freeApiluminascalem!+|I1,R1u31C_V
- Rate limiting: 10,000 requests/day per API key or IP
- Production-ready with health checks
- GPU optimized (CUDA 12.1+)
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException, Request, status
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.pipeline import enhance_image, preload_models
from app.quota import check_and_increment_ip_quota, check_and_increment_api_key_quota, get_quota_stats
from app.utils import get_client_ip, format_image_size
from app.auth import validate_api_key, get_free_api_key_name

# Logging configuration
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "info").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# App initialization
app = FastAPI(
    title="GFPGAN Free API with Authentication",
    description=
    "Face restoration & upscaling API powered by GFPGAN v1.4 + Real-ESRGAN 4x (10,000 free requests/day with API key)",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json")

# CORS - Allow all origins (modify for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_FORMATS = {"image/jpeg", "image/png", "image/webp", "image/tiff"}


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("=" * 60)
    logger.info("🚀 GFPGAN Free API Starting")
    logger.info("=" * 60)

    # Verify Redis
    stats = get_quota_stats()
    if stats.get("redis_connected"):
        logger.info("✅ Redis connected")
    else:
        logger.warning("⚠️  Redis not available - rate limiting disabled")

    logger.info(f"📊 Free API Key: freeApiluminascalem***")
    logger.info(f"📊 Daily limit: 10,000 requests")
    logger.info("=" * 60)

    preload_models()


@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns:
        Status and timestamp
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "GFPGAN Free API",
        "authentication": "X-API-Key required"
    }


@app.get("/stats", tags=["System"])
async def get_stats() -> Dict[str, Any]:
    """
    Get API statistics (quota usage, connected services).
    
    Returns:
        Current quota statistics
    """
    stats = get_quota_stats()
    return {
        **stats, "daily_limit_per_key": 10000,
        "daily_limit_per_ip": 10000,
        "free_api_key_name": "freeApiluminascalem",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/", tags=["Info"])
async def root():
    """API root endpoint"""
    return {
        "name":
        "GFPGAN Free API",
        "version":
        "1.0.0",
        "docs":
        "/docs",
        "features": [
            "GFPGAN v1.4 face restoration (arch=clean, channel_multiplier=2)",
            "Real-ESRGAN 4x background upsampling (SRVGGNetCompact, fast mode)",
            "Automatic face detection and enhancement",
            "High-quality LANCZOS4 upscaling (2x/4x)",
            "Supports v1.2, v1.3, v1.4 GFPGAN checkpoints"
        ],
        "authentication":
        "Required - X-API-Key header",
        "free_api_key":
        "freeApiluminascalem!+|I1,R1u31C_V",
        "endpoints": {
            "health": "/health",
            "enhance": "/enhance?scale=2",
            "stats": "/stats"
        },
        "free_tier":
        "10,000 requests/day",
        "status":
        "ready"
    }


@app.post("/enhance", tags=["Enhancement"])
async def enhance(request: Request,
                  file: UploadFile = File(...),
                  version: str = "v1.4",
                  scale: int = 2) -> Response:
    """
    Enhance image using GFPGAN face restoration + Real-ESRGAN 4x background upsampling.
    
    **Authentication Required:** Pass `X-API-Key` header
    
    **Free Tier:** 10,000 requests per 24-hour period per API key
    
    **Free API Key:** `freeApiluminascalem!+|I1,R1u31C_V`
    
    **Pipeline:**
    1. Pre-upsample tiny images (height < 300px) for face detection
    2. GFPGAN v1.4 face enhancement (arch=clean, channel_multiplier=2)
    3. Real-ESRGAN 4x background upsampling (SRVGGNetCompact, fast mode)
    4. Final resize to requested scale factor
    
    Args:
        file: Image file (JPG, PNG, WebP, TIFF)
        version: GFPGAN checkpoint - v1.4 (sharpest, most natural), v1.3, or v1.2 (default: v1.4)
        scale: Final upscale factor (2 or 4, default: 2)
        
    Returns:
        Enhanced image as PNG
        
    Status Codes:
        - 200: Enhancement successful
        - 400: Invalid parameters or corrupted image
        - 401: Invalid or missing API key
        - 413: File too large (>50MB)
        - 415: Unsupported image format
        - 429: Daily quota exceeded
        - 500: Processing errors
    """

    # Get client IP
    client_ip = get_client_ip(request)

    # Check for API key authentication
    api_key = request.headers.get("X-API-Key")
    is_authenticated = False
    quota_identifier = None

    if api_key:
        is_valid, message = validate_api_key(api_key)
        if not is_valid:
            logger.warning(f"Invalid API key attempt from {client_ip}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=message,
                                headers={"WWW-Authenticate": "Bearer"})
        is_authenticated = True
        quota_identifier = "freeApiluminascalem"  # Use key name for quota tracking
        logger.info(f"✅ Authenticated request from {client_ip} with API key")
    else:
        # Use IP-based tracking as fallback
        quota_identifier = client_ip
        logger.info(f"📝 IP-based request from {client_ip} (no API key)")

    logger.info(f"Enhancement request - scale: {scale}x")

    # Validate scale parameter
    if scale not in (2, 4):
        logger.warning(f"Invalid scale parameter: {scale}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Scale must be 2 or 4")

    # Validate file size
    file_size = 0
    try:
        # Peek at file size
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File too large: {format_image_size(file_size)}")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=
                f"File too large (max {format_image_size(MAX_FILE_SIZE)})")

        if file_size < 100:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="File too small")

        # Validate MIME type
        mime_type = file.content_type
        if mime_type not in ALLOWED_FORMATS:
            logger.warning(f"Unsupported format: {mime_type}")
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=
                f"Unsupported format: {mime_type}. Allowed: JPG, PNG, WebP, TIFF"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid file")

    # Check quota based on authentication method
    if is_authenticated:
        allowed, used, limit, reset_time = check_and_increment_api_key_quota(
            quota_identifier)
        logger.info(f"API Key quota check: {used}/{limit}")
    else:
        allowed, used, limit, reset_time = check_and_increment_ip_quota(
            quota_identifier)
        logger.info(f"IP quota check: {used}/{limit}")

    if not allowed:
        logger.warning(
            f"Quota exceeded for {quota_identifier}: {used}/{limit}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=
            f"Daily quota exceeded ({used}/{limit}). Resets at {reset_time}",
            headers={
                "X-Quota-Used": str(used),
                "X-Quota-Limit": str(limit),
                "X-Quota-Reset": reset_time,
                "Retry-After": "86400"
            })

    # Process image
    try:
        logger.info(f"Processing image ({format_image_size(file_size)})...")

        enhancement_options = {
            "version": version,
        }

        enhanced_bytes = enhance_image(file_content,
                                       scale=scale,
                                       options=enhancement_options)

        logger.info(
            f"✅ Enhancement complete - Output: {format_image_size(len(enhanced_bytes))}"
        )

        # Return enhanced image with quota headers
        return Response(content=enhanced_bytes,
                        media_type="image/png",
                        headers={
                            "X-Quota-Used": str(used),
                            "X-Quota-Limit": str(limit),
                            "X-Quota-Reset": reset_time,
                            "X-Authenticated":
                            "true" if is_authenticated else "false",
                            "Cache-Control":
                            "no-cache, no-store, must-revalidate"
                        })

    except ValueError as e:
        logger.error(f"Image processing error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image processing failed. Please try again.")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(status_code=exc.status_code,
                        content={"detail": exc.detail},
                        headers=exc.headers)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
