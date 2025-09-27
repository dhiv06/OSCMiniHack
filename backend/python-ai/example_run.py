#!/usr/bin/env python3
"""Non-interactive example runner for classifier, summarizer, and compressor.

This script performs simple smoke tests for the three modules so you can
quickly verify they work together. It is intentionally non-interactive.
"""
from __future__ import annotations
import sys
from typing import List, Tuple

try:
    from classifier import classify_text
    from summarizer import ExtractiveSummarizer, split_sentences
    from compressor import compress_image
except Exception as e:
    print('ERROR importing project modules:', e)
    raise

import numpy as np

def run_classifier_smoke() -> None:
    print('\n== Classifier smoke tests ==')
    cases: List[Tuple[str, str]] = [
        ('', 'normal'),
        ("Help! I'm trapped under rubble and bleeding.", 'sos'),
        ('There is smoke and fire inside the building.', 'urgent'),
        ('Just checking in, all good here.', 'normal'),
    ]
    for text, expected in cases:
        label, score, matched = classify_text(text)
        ok = label == expected
        print(f"expected={expected:6} got={label:6} ok={ok} score={score:.2f} matched={matched}")


def run_summarizer_smoke() -> None:
    print('\n== Summarizer test ==')
    text = (
        "The hospital is overwhelmed with injured people in the collapse. "
        "First responders are on site. The building partially collapsed after the quake. "
        "Power is out across the block. Volunteers are organizing triage. "
        "Some people are trapped under rubble and require extraction."
    )
    print('Original text (shortened):')
    print(text)
    sents = split_sentences(text)
    print(f'Split into {len(sents)} sentences')

    summarizer = ExtractiveSummarizer()
    summary = summarizer.summarize(text, max_sentences=2)
    print('\nSummary result:')
    for i, s in enumerate(summary, 1):
        print(f' {i}. {s}')


def make_sample_png_bytes(w=480, h=320, color=(200, 180, 160)) -> bytes:
    # Create a plain-color RGB image and encode as PNG bytes using numpy (cv2 required in compressor)
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:] = color
    try:
        # Attempt to use compressor's expected input path: raw PNG/JPEG bytes
        import cv2  # type: ignore
        ok, png = cv2.imencode('.png', arr)
        if not ok:
            raise RuntimeError('cv2.imencode failed')
        return png.tobytes()
    except Exception:
        # If cv2 isn't available in this interpreter, use a fallback: raw bytes are not available
        # Signal the caller by raising an ImportError so the top-level runner can pick the proper python
        raise


def run_compressor_smoke(write_out: bool = True) -> None:
    print('\n== Compressor smoke ==')
    try:
        png_bytes = make_sample_png_bytes()
    except ImportError:
        print('cv2 not available in this Python. Re-run using the virtualenv python that has opencv installed.')
        raise

    jpg = compress_image(png_bytes, max_dim=300, jpeg_quality=80)
    ok = (len(jpg) > 10 and jpg[0] == 0xFF and jpg[1] == 0xD8)
    print(f'In-memory -> JPEG ok={ok} bytes={len(jpg)}')
    if write_out:
        out_path = 'example_out.jpg'
        with open(out_path, 'wb') as f:
            f.write(jpg)
        print(f'Wrote {out_path}')


def main() -> int:
    try:
        run_classifier_smoke()
        run_summarizer_smoke()
        run_compressor_smoke(write_out=True)
    except ImportError:
        print('\nOne or more required native packages (cv2 / opencv) are missing in this interpreter.')
        print('Try running with your project virtualenv python. Example:')
        print('  /home/squidlord/OSCHackathon/.venv/bin/python backend/python-ai/example_run.py')
        return 2
    except Exception as e:
        print('\nERROR during run:', e)
        return 3
    print('\nAll tests finished.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
