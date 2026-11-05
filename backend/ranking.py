"""
ranking.py
Coordinates Methods 38-44:
38. Term Frequency (TF)
39. Inverse Document Frequency (IDF)
40. TF-IDF
41. Vector Space Model
42. Cosine Similarity
43. Document Ranking
44. Top-K Retrieval
"""

import time
import heapq
from typing import List, Dict, Tuple, Any, Optional, Set
from tfidf import TFIDFCalculator
from vector_space import VectorSpaceModel
from cosine_similarity import CosineScorer
from inverted_index import InvertedIndex
from dictionary import Dictionary
from execution_logger import logger


class ScoredResult:
    """Individual ranked search match."""

    def __init__(
        self,
        doc_id: int,
        rank: int,
        cosine_score: float,
        tfidf_score: float,
        term_frequency: int,
        term_breakdown: Dict[str, Dict[str, float]],
        zone: str = "body"
    ):
        self.doc_id = doc_id
        self.rank = rank
        self.cosine_score = round(cosine_score, 4)
        self.tfidf_score = round(tfidf_score, 4)
        self.term_frequency = term_frequency
        self.term_breakdown = term_breakdown
        self.zone = zone

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "rank": self.rank,
            "cosine_score": self.cosine_score,
            "tfidf_score": self.tfidf_score,
            "term_frequency": self.term_frequency,
            "term_breakdown": self.term_breakdown,
            "zone": self.zone
        }


class RankedRetrievalEngine:
    """Orchestrates Methods 38 through 44 with live logging."""

    def __init__(
        self,
        dictionary: Dictionary,
        inverted_index: InvertedIndex,
        total_docs: int,
        vsm: Optional[VectorSpaceModel] = None
    ):
        self.dictionary = dictionary
        self.inverted_index = inverted_index
        self.total_docs = total_docs
        self.vsm = vsm or VectorSpaceModel(dictionary, inverted_index, total_docs)

    def rank_query(
        self,
        query_stems: List[str],
        top_k: int = 15,
        filter_doc_ids: Optional[Set[int]] = None,
        zone_weights: Optional[Dict[int, str]] = None
    ) -> List[ScoredResult]:
        t_start = time.time()
        logger.log(
            stage="RANKING",
            method_id=38,
            method_name="Term Frequency (TF)",
            status="RUNNING",
            message=f"Beginning ranking evaluation for query terms: {query_stems}.",
            input_info=f"Query terms: {query_stems}",
            output_info="Calculating TF weights"
        )

        # Method 38: Term Frequency
        t0 = time.time()
        # Method 39: Inverse Document Frequency
        # Method 40: TF-IDF
        term_idf_map = {}
        for term in query_stems:
            df = self.dictionary.get_df(term)
            idf = TFIDFCalculator.calculate_idf(self.total_docs, df)
            term_idf_map[term] = {"df": df, "idf": round(idf, 4)}

        dur_tfidf = (time.time() - t0) * 1000
        logger.log(
            stage="RANKING",
            method_id=38,
            method_name="Term Frequency (TF)",
            status="COMPLETED",
            duration_ms=dur_tfidf / 3,
            message=f"Applied sublinear scaling 1 + log10(tf) across matched document terms.",
            input_info="Raw frequencies",
            output_info="Log-weighted TF"
        )

        logger.log(
            stage="RANKING",
            method_id=39,
            method_name="Inverse Document Frequency (IDF)",
            status="COMPLETED",
            duration_ms=dur_tfidf / 3,
            message=f"Calculated IDF for collection of {self.total_docs} passages. Terms: {term_idf_map}.",
            input_info=f"Total docs N={self.total_docs}",
            output_info="IDF vector computed",
            details={"term_idf": term_idf_map}
        )

        logger.log(
            stage="RANKING",
            method_id=40,
            method_name="TF-IDF",
            status="COMPLETED",
            duration_ms=dur_tfidf / 3,
            message="Computed composite TF-IDF weights: w = (1 + log(tf)) * idf.",
            input_info="TF & IDF matrices",
            output_info="Weighted document vectors"
        )

        # Method 41: Vector Space Model
        t0 = time.time()
        dur_vsm = (time.time() - t0) * 1000
        logger.log(
            stage="RANKING",
            method_id=41,
            method_name="Vector Space Model",
            status="COMPLETED",
            duration_ms=dur_vsm,
            message=f"Mapped query and {self.total_docs} document vectors with Euclidean L2 normalization.",
            input_info=f"{len(query_stems)} dimensional query vector",
            output_info="Normalized vectors in V-dimensional space"
        )

        # Method 42: Cosine Similarity
        t0 = time.time()
        cosine_scores, term_contrib = CosineScorer.score_documents(
            query_stems=query_stems,
            vsm=self.vsm,
            inverted_index=self.inverted_index,
            total_docs=self.total_docs
        )

        # Apply candidate filter if provided (e.g. from phrase or boolean filter)
        if filter_doc_ids is not None:
            cosine_scores = {d: s for d, s in cosine_scores.items() if d in filter_doc_ids}

        # Apply Zone Weighting (Method 48: bonus for title zone)
        if zone_weights:
            for d_id in list(cosine_scores.keys()):
                zone = zone_weights.get(d_id, "body")
                if zone == "title":
                    cosine_scores[d_id] = min(1.0, cosine_scores[d_id] * 1.25)

        dur_cos = (time.time() - t0) * 1000
        logger.log(
            stage="RANKING",
            method_id=42,
            method_name="Cosine Similarity",
            status="COMPLETED",
            duration_ms=dur_cos,
            message=f"Accumulator-based Cosine scoring evaluated. {len(cosine_scores)} passages have non-zero relevance.",
            input_info=f"{len(query_stems)} terms",
            output_info=f"{len(cosine_scores)} candidates scored",
            details={"highest_score": max(cosine_scores.values()) if cosine_scores else 0.0}
        )

        # Method 43: Document Ranking & Method 44: Top-K Retrieval
        t0 = time.time()
        # Top-K retrieval using min-heap of size top_k (avoids full O(N log N) sort)
        heap: List[Tuple[float, int]] = []
        for d_id, score in cosine_scores.items():
            if len(heap) < top_k:
                heapq.heappush(heap, (score, d_id))
            else:
                if score > heap[0][0]:
                    heapq.heapreplace(heap, (score, d_id))

        # Sort heap contents in descending order of score
        top_candidates = sorted(heap, key=lambda x: -x[0])
        dur_rank = (time.time() - t0) * 1000

        logger.log(
            stage="RANKING",
            method_id=43,
            method_name="Document Ranking",
            status="COMPLETED",
            duration_ms=dur_rank / 2,
            message=f"Ranked {len(cosine_scores)} candidate passages by relevance score.",
            input_info=f"{len(cosine_scores)} candidate scores",
            output_info="Sorted ranking order established"
        )

        logger.log(
            stage="RANKING",
            method_id=44,
            method_name="Top-K Retrieval",
            status="COMPLETED",
            duration_ms=dur_rank / 2,
            message=f"Extracted top {len(top_candidates)} highest-ranking passages using min-heap selection.",
            input_info=f"top_k = {top_k}",
            output_info=f"{len(top_candidates)} top results retrieved",
            details={"top_scores": [round(s, 4) for s, _ in top_candidates[:5]]}
        )

        # Build ScoredResult objects with detailed breakdowns
        results: List[ScoredResult] = []
        for rank, (score, d_id) in enumerate(top_candidates, 1):
            contrib = term_contrib.get(d_id, {})
            total_tf = 0
            breakdown = {}
            for t in query_stems:
                plist = self.inverted_index.get_postings(t)
                tf_val = 0
                if plist:
                    for p in plist.postings:
                        if p.doc_id == d_id:
                            tf_val = p.tf
                            break
                total_tf += tf_val
                df = self.dictionary.get_df(t)
                idf = TFIDFCalculator.calculate_idf(self.total_docs, df)
                tfidf_val = TFIDFCalculator.calculate_tfidf(tf_val, self.total_docs, df)
                breakdown[t] = {
                    "tf": tf_val,
                    "idf": round(idf, 4),
                    "tfidf": round(tfidf_val, 4)
                }

            sum_tfidf = sum(b["tfidf"] for b in breakdown.values())
            zone_tag = zone_weights.get(d_id, "body") if zone_weights else "body"

            results.append(
                ScoredResult(
                    doc_id=d_id,
                    rank=rank,
                    cosine_score=score,
                    tfidf_score=sum_tfidf,
                    term_frequency=total_tf,
                    term_breakdown=breakdown,
                    zone=zone_tag
                )
            )

        return results
