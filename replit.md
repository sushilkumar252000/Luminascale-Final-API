# GFPGAN Face Restoration API

## Overview
A FastAPI-based REST API for face restoration using the official GFPGAN v1.4 model with Real-ESRGAN 4x background upsampling. Optimized for fast CPU inference.

## Project Architecture

### Directory Structure
```
/
├── main.py              # FastAPI app entry point
├── app/
│   ├── __init__.py
│   ├── pipeline.py      # GFPGAN + Real-ESRGAN processing pipeline (optimized)
│   ├── quota.py         # Rate limiting (Redis optional)
│   ├── auth.py          # API key authentication
│   └── utils.py         # Utility functions
├── gfpgan/
│   └── weights/         # Model weights (not in git)
│       ├── GFPGANv1.4.pth               # GFPGAN face restoration (333MB)
│       ├── realesr-general-x4v3.pth     # Real-ESRGAN fast upsampler (4.7MB, SRVGGNetCompact)
│       ├── detection_Resnet50_Final.pth  # Face detection model
│       └── parsing_parsenet.pth         # Face parsing model
├── requirements.txt     # Python dependencies
└── replit.md            # This file
```

### ML Pipeline
1. Decode input image (handles BGR/GRAY/RGBA)
2. Cap input size (max 1500x1500) for speed
3. Pre-upsample tiny images (height < 300px) for face detector
4. GFPGAN v1.4 face enhancement (clean arch, channel_multiplier=2)
5. Real-ESRGAN 4x background upsampling (SRVGGNetCompact, fast mode)
6. Final resize to match requested scale factor
7. Encode and return as PNG

### API Endpoints
- `GET /` - API info
- `GET /health` - Health check
- `GET /stats` - Usage statistics
- `POST /enhance` - Face restoration endpoint

### Parameters
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| scale | int | 2 | 2, 4 | Upscale factor |
| version | string | v1.4 | v1.2, v1.3, v1.4 | GFPGAN model version |

### Authentication
- Free API Key: `freeApiluminascalem!+|I1,R1u31C_V`
- Pass via `X-API-Key` header

## Running
The API runs on port 5000 via uvicorn (`python main.py`).

## Dependencies
- FastAPI + Uvicorn
- PyTorch (CPU) + torchvision
- GFPGAN, Real-ESRGAN, basicsr, facexlib
- OpenCV (headless)
- NumPy

## Performance Optimizations
- SRVGGNetCompact upsampler instead of RRDBNet (~30x faster on CPU)
- Models pre-loaded at startup (no first-request delay)
- torch.inference_mode() for faster inference
- Optimized CPU thread count via torch.set_num_threads()
- Input image size capped at 1500x1500px
- PNG compression level reduced to 3 for faster encoding
- basicsr torchvision patch applied programmatically at import time

## Technical Notes
- Redis is optional - without it, rate limiting is disabled
- All processing works on CPU (no GPU required)
- Processing time: ~2-3s per image on CPU (was ~80s before optimization)
- Face detection uses Resnet50, face parsing uses ParseNet

## Recent Changes
- 2026-02-06: Major speed optimization - switched to SRVGGNetCompact, pre-load models, torch.inference_mode(), input capping (~30x faster)
- 2026-02-06: Fixed model architecture mismatch between weight file and network definition
- 2026-02-06: Patched basicsr torchvision compatibility (functional_tensor → functional)
- 2026-02-06: Implemented full GFPGAN v1.4 + Real-ESRGAN pipeline
