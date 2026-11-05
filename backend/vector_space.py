"""
vector_space.py
Method 41: Vector Space Model.
Represents documents and queries as high-dimensional vectors with L2 normalization.
"""

import math
from typing import Dict, List, Optional, Tuple
from tfidf import TFIDFCalculator
from dictionary import Dictionary
from inverted_index import InvertedIndex


class DocumentVector:
    def __init__(self, doc_id: int):
        self.doc_id = doc_id
        self.weights: Dict[str, float] = {}
        self.norm: float = 0.0

    def add_weight(self, term: str, weight: float):
        self.weights[term] = weight

    def compute_norm(self):
        sq_sum = sum(w * w for w in self.weights.values())
        self.norm = math.sqrt(sq_sum) if sq_sum > 0 else 1.0


class VectorSpaceModel:
    """Method 41: Vector Space Model representation."""

    def __init__(self, dictionary: Dictionary, inverted_index: InvertedIndex, total_docs: int):
        self.dictionary = dictionary
        self.inverted_index = inverted_index
        self.total_docs = total_docs
        self.doc_vectors: Dict[int, DocumentVector] = {}
        self._build_doc_vectors()

    def _build_doc_vectors(self):
        """Constructs vector representations for all documents in collection."""
        for doc_id in range(self.total_docs):
            self.doc_vectors[doc_id] = DocumentVector(doc_id)

        for term, entry in self.dictionary.entries.items():
            plist = self.inverted_index.get_postings(term)
            if not plist:
                continue
            idf = TFIDFCalculator.calculate_idf(self.total_docs, entry.doc_freq)
            for posting in plist.postings:
                tf = TFIDFCalculator.calculate_tf(posting.tf)
                w = tf * idf
                if posting.doc_id in self.doc_vectors:
                    self.doc_vectors[posting.doc_id].add_weight(term, w)

        for dvec in self.doc_vectors.values():
            dvec.compute_norm()

    def create_query_vector(self, query_stems: List[str]) -> Tuple[Dict[str, float], float]:
        """Constructs weighted query vector with L2 norm."""
        tf_counts: Dict[str, int] = {}
        for s in query_stems:
            tf_counts[s] = tf_counts.get(s, 0) + 1

        query_weights: Dict[str, float] = {}
        sq_sum = 0.0

        for term, count in tf_counts.items():
            df = self.dictionary.get_df(term)
            idf = TFIDFCalculator.calculate_idf(self.total_docs, df) if df > 0 else 1.0
            tf = TFIDFCalculator.calculate_tf(count)
            w = tf * idf
            query_weights[term] = w
            sq_sum += w * w

        query_norm = math.sqrt(sq_sum) if sq_sum > 0 else 1.0
        return query_weights, query_norm
