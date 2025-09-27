"""Minimal adapter to call an LLM HTTP endpoint.

This module provides two functions the codebase can call: `classify_with_llm`
and `summarize_with_llm`. If LLM_API_URL is not set the functions return None
or fall back to the project's existing utilities.
"""
from __future__ import annotations
import os
from typing import List, Optional


def _is_configured() -> bool:
    return bool(os.environ.get("LLM_API_URL"))


def classify_with_llm(text: str) -> Optional[str]:
    """Return 'sos'|'urgent'|'normal' by calling remote LLM if configured.

    If not configured, returns None so callers can fall back to the rule-based
    classifier.
    """
    if not _is_configured():
        return None
    # Import lazily so this module doesn't require extra deps when unused
    try:
        from .llm_integration import classify_with_llm as _c
    except Exception:
        # If the project doesn't have the concrete integration (user removed it),
        # return None to allow a graceful fallback.
        return None
    return _c(text)


def summarize_with_llm(text: str, max_sentences: int = 3) -> List[str]:
    """Return a list of summary sentences from the LLM or an empty list.

    Callers should fall back to the extractive summarizer if the returned list
    is empty or None.
    """
    if not _is_configured():
        return []
    try:
        from .llm_integration import summarize_with_llm as _s
    except Exception:
        return []
    return _s(text, max_sentences=max_sentences)
