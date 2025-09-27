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
import logging

try:
    from classifier import classify_text
    from summarizer import ExtractiveSummarizer, split_sentences
    from compressor import compress_image
except Exception as e:
    # Import error will be raised at runtime if modules are missing; keep app importable for tests
    raise

app = Flask(__name__, static_folder='static', static_url_path='')

# Simple logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


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


@app.route('/health')
def health():
    """Simple health check for load balancers / dev checks."""
    return jsonify({'status': 'ok'}), 200


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


# Add permissive CORS headers in development to make it easy for the Vite frontend to call
@app.after_request
def _add_cors_headers(response: Response):
    # Allow override via environment in case stricter policy is needed
    allow_all = os.environ.get('ALLOW_ALL_CORS', '1')
    if allow_all in ('1', 'true', 'True'):
        response.headers['Access-Control-Allow-Origin'] = os.environ.get('CORS_ORIGIN', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


if __name__ == '__main__':
    # Run locally with configurable port/host for development convenience
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)

    bind_host = os.environ.get('BIND_HOST', '0.0.0.0')
    port_str = os.environ.get('PORT', os.environ.get('FLASK_RUN_PORT', '5000'))
    try:
        port = int(port_str)
    except ValueError:
        logger.error('Invalid PORT value %r, falling back to 5000', port_str)
        port = 5000

    debug = os.environ.get('FLASK_DEBUG', os.environ.get('DEBUG', '0')) in ('1', 'true', 'True')

    logger.info('Starting Flask app: host=%s port=%d debug=%s static_folder=%s', bind_host, port, debug, app.static_folder)
    try:
        app.run(host=bind_host, port=port, debug=debug)
    except OSError as e:
        logger.exception('Failed to start server on %s:%s — %s', bind_host, port, e)
        logger.info('If the port is already in use, find the process with:')
        logger.info('  lsof -i :%d    # or use: ss -ltnp | grep :%d', port, port)
        raise

