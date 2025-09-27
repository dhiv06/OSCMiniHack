# compressor.py
import cv2
import numpy as np
from typing import Tuple

def compress_image(
    img_bytes: bytes,
    max_dim: int = 512,
    jpeg_quality: int = 70
) -> bytes:
    """
    Downscale + JPEG compress an image.
    Args:
        img_bytes: raw image data (e.g. from file.read())
        max_dim: maximum width/height
        jpeg_quality: 0–100 (higher = better quality, larger size)
    Returns:
        Compressed JPEG as bytes
    """
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image")

    h, w = img.shape[:2]
    scale = min(max_dim / float(h), max_dim / float(w), 1.0)
    if scale < 1.0:
        new_size = (int(w * scale), int(h * scale))
        img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)

    ok, enc = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
    if not ok:
        raise RuntimeError("JPEG encoding failed")
    return enc.tobytes()
