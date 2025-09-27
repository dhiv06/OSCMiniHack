# compressor.py
# Utilities to decode image bytes, downscale if necessary, and re-encode as JPEG.
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
        img_bytes: raw image data (e.g. bytes read from a PNG or JPEG file)
        max_dim: maximum width/height (keeps aspect ratio)
        jpeg_quality: 0–100 (higher = better quality and larger size)

    Returns:
        Compressed JPEG as bytes (starts with 0xFF 0xD8)

    Workflow:
      1. Convert the incoming bytes into a numpy uint8 buffer.
      2. Ask OpenCV to decode the buffer into an image array (BGR color order).
      3. If the image is larger than max_dim, resize it preserving aspect ratio.
      4. Encode the image as JPEG and return the resulting bytes.
    """
    # View the raw bytes as a uint8 numpy array (required by cv2.imdecode)
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    # Decode the in-memory bytes into an image (BGR color channels)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        # Decoding failed (input may not be a valid image)
        raise ValueError("Could not decode image")

    # Get height and width
    h, w = img.shape[:2]
    # Compute scale factor to shrink the image to fit within max_dim
    scale = min(max_dim / float(h), max_dim / float(w), 1.0)
    if scale < 1.0:
        # New size expects (width, height) tuple
        new_size = (int(w * scale), int(h * scale))
        # Resize using an anti-aliasing interpolation for downscaling
        img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)

    # Encode image as JPEG in memory with the requested quality
    ok, enc = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
    if not ok:
        raise RuntimeError("JPEG encoding failed")
    # Return raw bytes (use .tobytes so callers get a plain bytes object)
    return enc.tobytes()
