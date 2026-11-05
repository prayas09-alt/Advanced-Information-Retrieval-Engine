"""
query_expansion.py
Method 45: Query Expansion & Relevance Feedback.
Implements the Rocchio Relevance Feedback formula and Pseudo-Relevance Feedback (PRF).
"""

import time
from typing import Dict, List, Set, Tuple, Any, Optional
from vector_space import VectorSpaceModel
from dictionary import Dictionary
from execution_logger import logger


class RocchioRelevanceFeedback:
    """Method 45: Rocchio Formula and Pseudo-Relevance Feedback."""

    @staticmethod
    def expand_query_prf(
        original_query_stems: List[str],
        top_ranked_doc_ids: List[int],
        vsm: VectorSpaceModel,
        dictionary: Dictionary,
        num_expansion_terms: int = 3,
        alpha: float = 1.0,
        beta: float = 0.75
    ) -> Tuple[List[str], Dict[str, float]]:
        """Pseudo-Relevance Feedback (PRF) assuming top k passages are relevant."""
        t0 = time.time()
        logger.log(
            stage="QUERY_EXPANSION",
            method_id=45,
            method_name="Query Expansion & Relevance Feedback",
            status="RUNNING",
            message=f"Applying Pseudo-Relevance Feedback (PRF) on top {len(top_ranked_doc_ids)} passages.",
            input_info=f"Original stems: {original_query_stems}",
            output_info="Calculating Rocchio centroid"
        )

        orig_set = set(original_query_stems)
        orig_weights, _ = vsm.create_query_vector(original_query_stems)

        # Accumulate weights across top relevant documents (beta * 1/|Dr| * sum(d))
        rel_centroid: Dict[str, float] = {}
        num_rel = max(1, len(top_ranked_doc_ids))

        for d_id in top_ranked_doc_ids:
            dvec = vsm.doc_vectors.get(d_id)
            if not dvec:
                continue
            for term, weight in dvec.weights.items():
                rel_centroid[term] = rel_centroid.get(term, 0.0) + weight

        # Average and scale by beta
        for term in rel_centroid:
            rel_centroid[term] = beta * (rel_centroid[term] / num_rel)

        # Combine with alpha * q0
        expanded_weights: Dict[str, float] = {}
        for term, w in orig_weights.items():
            expanded_weights[term] = alpha * w

        for term, w in rel_centroid.items():
            expanded_weights[term] = expanded_weights.get(term, 0.0) + w

        # Find top candidate expansion terms NOT in original query
        candidates = [(t, w) for t, w in rel_centroid.items() if t not in orig_set]
        candidates.sort(key=lambda x: -x[1])
        new_terms = [t for t, _ in candidates[:num_expansion_terms]]

        final_stems = list(original_query_stems) + new_terms
        dur = (time.time() - t0) * 1000

        logger.log(
            stage="QUERY_EXPANSION",
            method_id=45,
            method_name="Query Expansion & Relevance Feedback",
            status="COMPLETED",
            duration_ms=dur,
            message=f"Rocchio PRF expanded query with {len(new_terms)} terms: {new_terms}. Expanded query: {final_stems}.",
            input_info=f"{len(original_query_stems)} original query terms",
            output_info=f"Added: {new_terms} | New query: {final_stems}",
            details={"original_query": original_query_stems, "expanded_stems": final_stems, "expansion_terms": new_terms}
        )

        return final_stems, expanded_weights
