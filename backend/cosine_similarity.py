"""
cosine_similarity.py
Method 42: Cosine Similarity.
Calculates normalized angular dot product using Accumulator-based scoring:
sim(q, d) = (q · d) / (||q|| * ||d||)
"""

import time
from typing import Dict, List, Tuple
from vector_space import VectorSpaceModel
from inverted_index import InvertedIndex
from tfidf import TFIDFCalculator
from execution_logger import logger


class CosineScorer:
    """Calculates cosine similarity scores using the efficient accumulator algorithm."""

    @staticmethod
    def score_documents(
        query_stems: List[str],
        vsm: VectorSpaceModel,
        inverted_index: InvertedIndex,
        total_docs: int
    ) -> Tuple[Dict[int, float], Dict[int, Dict[str, float]]]:
        """Calculates cosine similarity for all documents sharing at least one query term.
        Returns:
            scores: doc_id -> cosine similarity score [0.0, 1.0]
            per_term_scores: doc_id -> {term: tfidf_weight}
        """
        # 1. Compute query vector weights and query norm
        query_weights, query_norm = vsm.create_query_vector(query_stems)

        # 2. Accumulators table
        accumulators: Dict[int, float] = {}
        per_term_contrib: Dict[int, Dict[str, float]] = {}

        for term, q_weight in query_weights.items():
            plist = inverted_index.get_postings(term)
            if not plist:
                continue

            df = len(plist)
            idf = TFIDFCalculator.calculate_idf(total_docs, df)

            for posting in plist.postings:
                d_id = posting.doc_id
                tf = TFIDFCalculator.calculate_tf(posting.tf)
                d_weight = tf * idf

                if d_id not in accumulators:
                    accumulators[d_id] = 0.0
                    per_term_contrib[d_id] = {}

                accumulators[d_id] += q_weight * d_weight
                per_term_contrib[d_id][term] = d_weight

        # 3. Normalize by product of lengths (||q|| * ||d||)
        final_scores: Dict[int, float] = {}
        for d_id, dot_product in accumulators.items():
            dvec = vsm.doc_vectors.get(d_id)
            d_norm = dvec.norm if dvec else 1.0
            denominator = query_norm * d_norm
            cos_sim = dot_product / denominator if denominator > 0 else 0.0
            # Clamp between 0.0 and 1.0
            final_scores[d_id] = min(1.0, max(0.0, cos_sim))

        return final_scores, per_term_contrib
