# summarizer.py
import re
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')

def split_sentences(text: str) -> List[str]:
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    if not sentences:
        sentences = [s.strip() for s in text.splitlines() if s.strip()]
    return sentences

class ExtractiveSummarizer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")

    def summarize(self, text: str, max_sentences: int = 3) -> List[str]:
        sentences = split_sentences(text)
        if not sentences:
            return []

        if len(sentences) <= max_sentences:
            return sentences

        tfidf = self.vectorizer.fit_transform(sentences)
        scores = np.asarray(tfidf.sum(axis=1)).ravel()
        ranked = np.argsort(-scores)
        selected = sorted(ranked[:max_sentences])
        return [sentences[i] for i in selected]
