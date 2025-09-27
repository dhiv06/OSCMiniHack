#!/usr/bin/env python3
"""Small Flask API to expose classifier, summarizer, and compressor to a simple static frontend.

Serves static files from ./static and provides JSON endpoints:
 - POST /api/summarize { text } -> { summary: [sentences] }
 - POST /api/classify { text } -> { label, score, matched }
 - POST /api/compress (form-data file) -> returns image/jpeg bytes

This file wires the existing modules in the same folder: classifier.py, summarizer.py, compressor.py
"""
from __future__ import annotations
import io
import os
from typing import List

from flask import Flask, request, jsonify, send_from_directory, abort, Response

try:
    from classifier import classify_text
    from summarizer import ExtractiveSummarizer, split_sentences
    from compressor import compress_image
except Exception as e:
    # Import error will be raised at runtime if modules are missing; keep app importable for tests
    raise

app = Flask(__name__, static_folder='static', static_url_path='')


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/summarize', methods=['POST'])
def api_summarize():
    data = request.get_json(force=True, silent=True)
    if not data or 'text' not in data:
        return jsonify({'error': 'missing text'}), 400
    text = data['text']
    summarizer = ExtractiveSummarizer()
    summary = summarizer.summarize(text, max_sentences=3)
    # Return as a single string (joined) for easy display
    return jsonify({'summary': ' '.join(summary), 'sentences': summary})


@app.route('/api/classify', methods=['POST'])
def api_classify():
    data = request.get_json(force=True, silent=True)
    if not data or 'text' not in data:
        return jsonify({'error': 'missing text'}), 400
    label, score, matched = classify_text(data['text'])
    return jsonify({'label': label, 'score': score, 'matched': matched})


@app.route('/api/compress', methods=['POST'])
def api_compress():
    # Expect a file field named 'image' or raw bytes in body
    file = None
    if 'image' in request.files:
        file = request.files['image']
        img_bytes = file.read()
    else:
        # Try to read raw body
        img_bytes = request.get_data() or b''

    if not img_bytes:
        return jsonify({'error': 'no image bytes provided'}), 400

    try:
        out = compress_image(img_bytes, max_dim=512, jpeg_quality=75)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'compression failed', 'detail': str(e)}), 500

    return Response(out, content_type='image/jpeg')


if __name__ == '__main__':
    # Run locally on port 5000, enable CORS for quick testing by the frontend (served by Flask itself)
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host='0.0.0.0', port=5000)

