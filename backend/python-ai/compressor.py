# compressor.py
# Utilities for decoding image bytes, downscaling if necessary, and re-encoding
# as JPEG bytes. Used by the Flask `/api/compress` endpoint which either accepts
# a multipart file field named 'image' or raw bytes in the request body.
import cv2
import numpy as np
from typing import Tuple


def compress_image(
    img_bytes: bytes,
    max_dim: int = 512,
    jpeg_quality: int = 70
) -> bytes:
    """Downscale and JPEG-compress an image.

    Args:
      img_bytes: raw bytes (e.g. contents of a PNG or JPEG file)
      max_dim: target maximum width/height (keeps aspect ratio)
      jpeg_quality: JPEG quality 0-100 (higher -> better quality and larger size)

    Returns:
      JPEG-encoded bytes (the byte string starts with JPEG magic 0xFF 0xD8).

    Steps:
      1. Convert the incoming Python bytes into a numpy uint8 buffer because
         OpenCV's `imdecode` expects that layout.
      2. Decode into an image array (BGR channels). If decoding fails we raise
         ValueError so the API can return a 400 to the client.
      3. If either dimension is larger than `max_dim`, compute a scale factor
         and resize using OpenCV's `INTER_AREA` (good for downscaling).
      4. Encode the possibly-resized image as JPEG in memory with the
         requested quality and return the raw bytes.
    """
    # Convert bytes -> numpy array required by cv2.imdecode
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        # The bytes didn't decode to a valid image
        raise ValueError("Could not decode image")

    h, w = img.shape[:2]
    # Compute shrink factor; don't enlarge (scale capped at 1.0)
    scale = min(max_dim / float(h), max_dim / float(w), 1.0)
    if scale < 1.0:
        new_size = (int(w * scale), int(h * scale))
        img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)

    ok, enc = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
    if not ok:
        raise RuntimeError("JPEG encoding failed")
    return enc.tobytes()
