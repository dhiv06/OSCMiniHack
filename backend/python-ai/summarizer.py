# summarizer.py
# Very small extractive summarizer based on TF-IDF sentence scoring.
import re
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# A simple sentence splitter: split on punctuation followed by whitespace.
# This will split "Hello world. This is X!" into ["Hello world.", "This is X!"]
_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')


def split_sentences(text: str) -> List[str]:
    """
    Break text into sentences using the regex above.

    If the regex doesn't yield any sentences (e.g., no punctuation), fall back
    to splitting on lines.
    """
    # Use the regex to split on punctuation followed by whitespace
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    # Fallback: if nothing found, split by newline/lines
    if not sentences:
        sentences = [s.strip() for s in text.splitlines() if s.strip()]
    return sentences


class ExtractiveSummarizer:
    """Extractive summarizer that picks top-N sentences by TF-IDF score.

    Behavior:
      - Vectorize each sentence with TF-IDF (ignoring English stop words).
      - Sum the TF-IDF weights per sentence (gives a simple importance score).
      - Pick the highest-scoring sentences and return them in their original order.
    """
    def __init__(self):
        # The vectorizer will convert text -> sparse TF-IDF vectors
        self.vectorizer = TfidfVectorizer(stop_words="english")

    def summarize(self, text: str, max_sentences: int = 3) -> List[str]:
        # Split into candidate sentences
        sentences = split_sentences(text)
        if not sentences:
            return []

        # If the text is shorter than requested summary size just return it
        if len(sentences) <= max_sentences:
            return sentences

        # Fit the TF-IDF on the sentences and compute a score per sentence
        tfidf = self.vectorizer.fit_transform(sentences)  # shape: (n_sentences, n_terms)
        # Sum TF-IDF weights across terms for each sentence to get a single importance score
        scores = np.asarray(tfidf.sum(axis=1)).ravel()
        # Rank sentences from highest score to lowest
        ranked = np.argsort(-scores)
        # Select top-k sentence indices, then sort them to preserve original order
        selected = sorted(ranked[:max_sentences])
        # Return the selected sentences in original document order
        return [sentences[i] for i in selected]
