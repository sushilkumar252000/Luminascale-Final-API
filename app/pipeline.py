"""
GFPGAN Face Enhancement Pipeline
Uses real GFPGAN v1.4 for face restoration and Real-ESRGAN for background upsampling.
Optimized for CPU inference speed.
"""

import os
import logging
from typing import Optional, Dict, Any
import numpy as np
import cv2
import torch

logger = logging.getLogger(__name__)

WEIGHTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gfpgan', 'weights')

MAX_INPUT_PIXELS = 1500 * 1500
NUM_THREADS = os.cpu_count() or 4

torch.set_num_threads(NUM_THREADS)
torch.set_num_interop_threads(max(1, NUM_THREADS // 2))

_face_enhancer = None
_current_version = None


def _patch_basicsr():
    import importlib
    try:
        import basicsr.data
        degradations_path = os.path.join(
            os.path.dirname(basicsr.data.__file__), 'degradations.py'
        )
        if os.path.exists(degradations_path):
            with open(degradations_path, 'r') as f:
                content = f.read()
            if 'functional_tensor' in content:
                content = content.replace(
                    'from torchvision.transforms.functional_tensor import rgb_to_grayscale',
                    'from torchvision.transforms.functional import rgb_to_grayscale'
                )
                with open(degradations_path, 'w') as f:
                    f.write(content)
                logger.info("Patched basicsr functional_tensor import")
    except Exception as e:
        logger.warning(f"basicsr patch check: {e}")

_patch_basicsr()

from gfpgan import GFPGANer
from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact


def _get_face_enhancer(version: str = "v1.4"):
    global _face_enhancer, _current_version

    if _face_enhancer is not None and _current_version == version:
        return _face_enhancer

    logger.info(f"Loading GFPGAN {version} with fast SRVGGNet upsampler...")

    bg_model = SRVGGNetCompact(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_conv=32,
        upscale=4,
        act_type='prelu',
    )
    bg_model_path = os.path.join(WEIGHTS_DIR, 'realesr-general-x4v3.pth')

    upsampler = RealESRGANer(
        scale=4,
        model_path=bg_model_path,
        model=bg_model,
        tile=0,
        tile_pad=10,
        pre_pad=0,
        half=False,
    )

    model_path = os.path.join(WEIGHTS_DIR, f'GFPGAN{version}.pth')
    _face_enhancer = GFPGANer(
        model_path=model_path,
        upscale=2,
        arch='clean',
        channel_multiplier=2,
        bg_upsampler=upsampler,
    )
    _current_version = version

    logger.info(f"GFPGAN {version} model loaded successfully (fast mode)")
    return _face_enhancer


def preload_models():
    logger.info("Pre-loading GFPGAN models at startup...")
    try:
        _get_face_enhancer("v1.4")
        logger.info("Models pre-loaded successfully")
    except Exception as e:
        logger.warning(f"Model pre-load failed (will retry on first request): {e}")


def _cap_input_size(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    pixels = h * w
    if pixels > MAX_INPUT_PIXELS:
        ratio = (MAX_INPUT_PIXELS / pixels) ** 0.5
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        logger.info(f"Capping input from {w}x{h} to {new_w}x{new_h} for speed")
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return image


def enhance_image(
    image_bytes: bytes,
    scale: int = 2,
    options: Optional[Dict[str, Any]] = None
) -> bytes:
    if scale not in (2, 4):
        raise ValueError("Scale must be 2 or 4")

    if options is None:
        options = {}

    version = options.get("version", "v1.4")
    if version not in ("v1.2", "v1.3", "v1.4"):
        version = "v1.4"

    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

        if image is None:
            raise ValueError("Failed to decode image")

        img_mode = None
        if image.ndim == 3 and image.shape[2] == 4:
            img_mode = "RGBA"
        elif image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        image = _cap_input_size(image)
        h, w = image.shape[:2]
        logger.info(f"Processing image: {w}x{h}")

        if h < 300:
            image = cv2.resize(
                image,
                (w * 2, h * 2),
                interpolation=cv2.INTER_LANCZOS4,
            )
            h, w = image.shape[:2]
            logger.info(f"Pre-upsampled small image to: {w}x{h}")

        face_enhancer = _get_face_enhancer(version)

        with torch.inference_mode():
            _, _, restored = face_enhancer.enhance(
                image,
                has_aligned=False,
                only_center_face=False,
                paste_back=True,
            )

        if not np.isclose(scale, 2.0):
            target_w = int(w * scale)
            target_h = int(h * scale)
            if scale > 2:
                interp = cv2.INTER_LANCZOS4
            else:
                interp = cv2.INTER_AREA
            restored = cv2.resize(restored, (target_w, target_h), interpolation=interp)

        logger.info(f"Enhanced image: {restored.shape[1]}x{restored.shape[0]}")

        _, buffer = cv2.imencode('.png', restored, [cv2.IMWRITE_PNG_COMPRESSION, 3])
        return buffer.tobytes()

    except cv2.error as e:
        logger.error(f"OpenCV error: {e}")
        raise ValueError(f"Image processing error: {str(e)}")
    except Exception as e:
        logger.error(f"Enhancement failed: {e}")
        raise ValueError(f"Image processing error: {str(e)}")
