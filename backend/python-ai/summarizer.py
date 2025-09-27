# summarizer.py
# Very small extractive summarizer used by the /api/summarize endpoint.
# It picks the most "important" sentences from a text by scoring sentences
# with TF-IDF and selecting the top-scoring ones.
import re
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# A lightweight sentence splitter. It splits on punctuation (.!? ) followed by
# whitespace — good enough for short messages and multi-sentence inputs.
_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')


def split_sentences(text: str) -> List[str]:
    """Split text into sentences.

    If the regex doesn't find sentences (e.g. no punctuation), fall back to
    splitting on newlines. Returns a list of non-empty trimmed sentence strings.
    """
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    if not sentences:
        sentences = [s.strip() for s in text.splitlines() if s.strip()]
    return sentences


class ExtractiveSummarizer:
    """Extractive summarizer that picks top-N sentences by TF-IDF score.

    How it works:
      1. Split the input into sentences using `split_sentences`.
      2. Vectorize each sentence with scikit-learn's TF-IDF (English stop words
         removed).
      3. For each sentence, sum its TF-IDF weights across all terms to get a
         single numeric importance score.
      4. Select the top-k scoring sentences and return them in their original
         document order (so the summary reads sensibly).

    This is intentionally simple and fast. It performs well enough for short
    messages and gives deterministic, explainable output that is easy to
    communicate to non-technical users.
    """
    def __init__(self):
        # The TfidfVectorizer is created once per instance. We ignore English
        # stop words to focus the scores on informative words.
        self.vectorizer = TfidfVectorizer(stop_words="english")

    def summarize(self, text: str, max_sentences: int = 3) -> List[str]:
        # Split into candidate sentences
        sentences = split_sentences(text)
        if not sentences:
            return []

        # If the document is short return it unchanged
        if len(sentences) <= max_sentences:
            return sentences

        # Fit TF-IDF across the sentences and compute a scalar score per
        # sentence by summing TF-IDF weights. Higher means more "important".
        tfidf = self.vectorizer.fit_transform(sentences)  # shape: (n_sentences, n_terms)
        scores = np.asarray(tfidf.sum(axis=1)).ravel()

        # Rank sentences by score (descending). We then select the indices of
        # the top-scoring sentences and sort them so the returned sentences
        # preserve the original reading order.
        ranked = np.argsort(-scores)
        selected = sorted(ranked[:max_sentences])
        return [sentences[i] for i in selected]
