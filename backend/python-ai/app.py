#!/usr/bin/env python3
"""Small Flask API used by the frontend.

High-level architecture and purpose:
 - This module provides a tiny REST API that the static frontend (served from
     `./static`) can call directly. During development the frontend is often
     served from a Vite dev server and calls the API at /api/* (we add permissive
     CORS headers to make that easy).

 - Endpoints provided:
         POST /api/summarize  -> accepts JSON { text } and returns { summary, sentences }
         POST /api/classify   -> accepts JSON { text } and returns { label, score, matched }
         POST /api/compress   -> accepts image bytes or multipart file 'image' and returns JPEG bytes
         GET  /health         -> simple health check (returns { status: 'ok' })

 - This file wires together three helper modules in the same folder:
         `classifier.py`  - rule-based emergency-style message classifier
         `summarizer.py`  - small extractive TF-IDF based summarizer
         `compressor.py`  - image decode/resize/re-encode helper using OpenCV

 - Execution / configuration:
         * The app binds to the host and port from the environment (PORT, BIND_HOST)
         * For quick local dev we enable permissive CORS via headers set in
             `@app.after_request`. Use `ALLOW_ALL_CORS=0` in production if you need
             stricter policies.

This file is intentionally small: it handles request parsing, validation,
error handling, and delegates core work to the helper modules above.
"""
from __future__ import annotations
import io
import os
from typing import List

from flask import Flask, request, jsonify, send_from_directory, abort, Response
import logging
import logging

try:
    from classifier import classify_text
    from summarizer import ExtractiveSummarizer, split_sentences
    from compressor import compress_image
except Exception as e:
    # Import error will be raised at runtime if modules are missing; keep app importable for tests
    raise

app = Flask(__name__, static_folder='static', static_url_path='')

# Configure a small logger to make startup/runtime issues easy to diagnose.
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    # Serve the single-page app index.html when visiting '/'. If you build the
    # frontend and copy artifacts into the `static` folder this will serve the
    # production UI from the same port as the API (handy for deployment).
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/summarize', methods=['POST'])
def api_summarize():
    # Expect JSON body with a 'text' field. We use force=True so the endpoint
    # will attempt to parse JSON even if the client didn't send a Content-Type
    # header. silent=True prevents Flask from raising a 400 automatically so
    # we can control the error response shape.
    data = request.get_json(force=True, silent=True)
    if not data or 'text' not in data:
        return jsonify({'error': 'missing text'}), 400

    text = data['text']
    # Delegate actual summarization to the ExtractiveSummarizer helper. It
    # returns a list of selected sentences; we also provide a single joined
    # string for simple display in the frontend.
    summarizer = ExtractiveSummarizer()
    summary = summarizer.summarize(text, max_sentences=3)
    return jsonify({'summary': ' '.join(summary), 'sentences': summary})


@app.route('/health')
def health():
    """Simple health check for load balancers / dev checks."""
    return jsonify({'status': 'ok'}), 200


@app.route('/api/classify', methods=['POST'])
def api_classify():
    # Similar JSON shape expected as /api/summarize
    data = request.get_json(force=True, silent=True)
    if not data or 'text' not in data:
        return jsonify({'error': 'missing text'}), 400

    # classify_text is a small, deterministic substring matcher (see
    # classifier.py). It returns (label, score, matched_keywords).
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

#cd /home/squidlord/OSCHackathon/OSCMiniHack/backend/python-ai && FLASK_APP=app.py FLASK_ENV=development python3 app.py 