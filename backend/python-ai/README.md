# python-ai backend

This small backend exposes the project's simple AI utilities (classifier, summarizer, image compressor)
over HTTP so the frontend can call them during development.

Endpoints:

- `GET /` : health/status
- `POST /api/summarize` : JSON { text: string, max_sentences?: int } -> { summary: string }
- `POST /api/classify` : JSON { text: string } -> { label: string, score: float, matched: [str] }
- `POST /api/compress-image` : multipart form upload with field `image` -> returns image/jpeg bytes

Quick start (recommended inside the provided virtualenv under `source/` if present):

```bash
# create venv or use the provided one
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The frontend dev server can proxy API requests to `http://localhost:5000` or you can run both services
and configure CORS appropriately. The frontend code expects an endpoint at `/api/summarize`.