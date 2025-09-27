Using smolagents to run an open-source LLM locally
===============================================

This document explains a minimal, low-friction path to run an open-source LLM
locally using `smolagents` (or a similar lightweight runner). The goal is to
make the model available via a simple local HTTP endpoint and provide a tiny
adapter the rest of this repo can call.

1) Install smolagents (or your runner of choice)

   - Prefer to create and activate a virtualenv first:

     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```

   - Install smolagents (if available) or follow the runner docs. Example:

     ```bash
     pip install smolagents
     ```

2) Pull/download a small open-source model

   - Choose a compact model that fits on your hardware (e.g. ggml-quantized
     variants, or small 7B models if you have RAM). With smolagents or its
     CLI you will usually do something like:

     ```bash
     smolagents pull <model-name>
     ```

   - If you need to run the model on a different machine (Windows box) you
     can transfer the model files and run the agent locally on the Linux host.

3) Run a minimal HTTP server in front of the model

   - Many runners provide a local HTTP endpoint. Example (pseudocode):

     ```bash
     smolagents serve --model <model-path> --host 0.0.0.0 --port 8080
     ```

   - Confirm the server responds to a simple POST /generate request with JSON
     {"prompt":"..."} and returns JSON containing the generated text.

4) Wire the LLM into this project

   - The repository contains a lightweight adapter `llm_adapter.py` that calls
     a configurable HTTP endpoint (LLM_API_URL). Set LLM_API_URL to
     `http://127.0.0.1:8080` (or your server's address) and use the adapter
     functions `classify_with_llm` and `summarize_with_llm` from Python code.

Security & performance notes
----------------------------
 - Exposing an LLM server to the network without auth is dangerous. If you
   intend to access the model from other machines, use SSH tunnels or TLS and
   authentication.
 - Pick a model that fits your hardware. If you have a modest CPU-only box,
   pick a small quantized CPU model.
