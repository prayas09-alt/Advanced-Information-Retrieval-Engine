"""
advanced_ir.py
Methods 46-48:
46. Latent Semantic Indexing (LSI)
47. Cluster Pruning
48. Zone Weighting
"""

import math
import time
import random
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from sklearn.decomposition import TruncatedSVD
from vector_space import VectorSpaceModel
from dictionary import Dictionary
from execution_logger import logger


class LatentSemanticIndexing:
    """Method 46: Latent Semantic Indexing (LSI).
    Applies Truncated Singular Value Decomposition (SVD) on the term-document matrix
    to map high-dimensional term representations into low-dimensional latent semantic concepts.
    """

    def __init__(self, vsm: VectorSpaceModel, dictionary: Dictionary, total_docs: int, n_components: int = 5):
        self.vsm = vsm
        self.dictionary = dictionary
        self.total_docs = total_docs
        self.terms = dictionary.terms()
        self.vocab_size = len(self.terms)
        self.term_to_idx = {t: i for i, t in enumerate(self.terms)}

        # Cap components to valid matrix dimensions
        self.k = min(n_components, max(1, self.total_docs - 1), max(1, self.vocab_size - 1))
        self.svd = TruncatedSVD(n_components=self.k, random_state=42)
        self.doc_concept_matrix: Optional[np.ndarray] = None
        self._fit()

    def _fit(self):
        if self.vocab_size < 2 or self.total_docs < 2:
            return

        # Build term-document matrix: shape (num_docs, vocab_size)
        A = np.zeros((self.total_docs, self.vocab_size), dtype=np.float32)
        for doc_id, dvec in self.vsm.doc_vectors.items():
            for term, weight in dvec.weights.items():
                if term in self.term_to_idx:
                    A[doc_id, self.term_to_idx[term]] = weight

        # Fit SVD: A ~ U * Sigma * V^T
        self.doc_concept_matrix = self.svd.fit_transform(A)

    def search_lsi(self, query_stems: List[str], top_k: int = 5) -> List[Tuple[int, float]]:
        """Projects query vector into concept space and computes cosine similarity."""
        t0 = time.time()
        if self.doc_concept_matrix is None or self.vocab_size < 2:
            logger.log(
                stage="ADVANCED_IR",
                method_id=46,
                method_name="Latent Semantic Indexing (LSI)",
                status="SKIPPED",
                message="Collection too small for LSI dimensionality reduction.",
                reason_skipped="Collection size < 2"
            )
            return []

        # Build query vector in vocabulary space
        q_vec = np.zeros((1, self.vocab_size), dtype=np.float32)
        for t in query_stems:
            if t in self.term_to_idx:
                q_vec[0, self.term_to_idx[t]] = 1.0

        # Project query to latent concept space: q_concept = q * V_k * Sigma_k^-1
        q_concept = self.svd.transform(q_vec)[0]
        q_norm = np.linalg.norm(q_concept)
        if q_norm == 0:
            q_norm = 1.0

        scores = []
        for doc_id in range(self.total_docs):
            d_concept = self.doc_concept_matrix[doc_id]
            d_norm = np.linalg.norm(d_concept)
            if d_norm == 0:
                continue
            cos_sim = float(np.dot(q_concept, d_concept) / (q_norm * d_norm))
            scores.append((doc_id, max(0.0, min(1.0, cos_sim))))

        scores.sort(key=lambda x: -x[1])
        top_lsi = scores[:top_k]
        dur = (time.time() - t0) * 1000

        logger.log(
            stage="ADVANCED_IR",
            method_id=46,
            method_name="Latent Semantic Indexing (LSI)",
            status="COMPLETED",
            duration_ms=dur,
            message=f"LSI projection into {self.k} semantic concepts completed. Top match: doc_{top_lsi[0][0] if top_lsi else 'None'} with score {round(top_lsi[0][1], 3) if top_lsi else 0}.",
            input_info=f"{self.vocab_size} vocabulary terms -> {self.k} latent dimensions",
            output_info=f"{len(top_lsi)} concept-scored matches",
            details={"latent_components": self.k, "top_matches": [f"doc_{d}: {round(s,3)}" for d, s in top_lsi[:3]]}
        )

        return top_lsi


class ClusterPruning:
    """Method 47: Cluster Pruning.
    Selects sqrt(N) leaders, assigns followers to closest leaders.
    Fast approximate Top-K search evaluates only followers of the nearest leader.
    """

    def __init__(self, vsm: VectorSpaceModel, total_docs: int):
        self.vsm = vsm
        self.total_docs = total_docs
        self.num_leaders = max(1, int(math.isqrt(total_docs)))
        # leader_doc_id -> list of follower_doc_ids
        self.clusters: Dict[int, List[int]] = {}
        self.leaders: List[int] = []
        self._build_clusters()

    def _build_clusters(self):
        if self.total_docs <= 3:
            self.leaders = list(range(self.total_docs))
            for l in self.leaders:
                self.clusters[l] = [l]
            return

        # Pick random leaders
        random.seed(42)
        self.leaders = random.sample(range(self.total_docs), self.num_leaders)
        for l in self.leaders:
            self.clusters[l] = []

        # Assign each doc to closest leader
        for doc_id in range(self.total_docs):
            best_leader = self.leaders[0]
            best_sim = -1.0
            dvec = self.vsm.doc_vectors.get(doc_id)
            if not dvec:
                continue

            for l_id in self.leaders:
                lvec = self.vsm.doc_vectors.get(l_id)
                if not lvec:
                    continue
                # Dot product / norms
                sim = sum(w * lvec.weights.get(t, 0.0) for t, w in dvec.weights.items()) / (dvec.norm * lvec.norm)
                if sim > best_sim:
                    best_sim = sim
                    best_leader = l_id

            self.clusters[best_leader].append(doc_id)

    def prune_and_search(self, query_weights: Dict[str, float], query_norm: float) -> Tuple[int, List[int]]:
        """Finds closest leader to query, then returns its cluster followers."""
        t0 = time.time()
        best_leader = self.leaders[0] if self.leaders else 0
        best_sim = -1.0

        for l_id in self.leaders:
            lvec = self.vsm.doc_vectors.get(l_id)
            if not lvec:
                continue
            sim = sum(w * lvec.weights.get(t, 0.0) for t, w in query_weights.items()) / (query_norm * lvec.norm)
            if sim > best_sim:
                best_sim = sim
                best_leader = l_id

        followers = self.clusters.get(best_leader, [])
        dur = (time.time() - t0) * 1000

        logger.log(
            stage="ADVANCED_IR",
            method_id=47,
            method_name="Cluster Pruning",
            status="COMPLETED",
            duration_ms=dur,
            message=f"Cluster pruning evaluated {len(self.leaders)} leaders (sqrt(N)). Closest leader doc_{best_leader} selected with {len(followers)} candidate followers.",
            input_info=f"Total docs N={self.total_docs}, Leaders={len(self.leaders)}",
            output_info=f"Search space pruned to {len(followers)} candidate passages",
            details={"leader": best_leader, "candidate_followers": followers[:10]}
        )

        return best_leader, followers


class ZoneWeighting:
    """Method 48: Zone Weighting.
    Combines weighted relevance scores across document zones (Title vs Body).
    Score = g * Title_Score + (1 - g) * Body_Score.
    """

    @staticmethod
    def apply_zone_weights(
        doc_scores: Dict[int, float],
        doc_zones: Dict[int, str],
        title_weight: float = 0.6
    ) -> Dict[int, float]:
        t0 = time.time()
        weighted_scores = {}
        title_boost_count = 0

        for doc_id, score in doc_scores.items():
            zone = doc_zones.get(doc_id, "body")
            if zone == "title":
                # Title zone matches receive higher weighting
                boosted = min(1.0, score * (1.0 + title_weight))
                weighted_scores[doc_id] = boosted
                title_boost_count += 1
            else:
                weighted_scores[doc_id] = score

        dur = (time.time() - t0) * 1000
        logger.log(
            stage="ADVANCED_IR",
            method_id=48,
            method_name="Zone Weighting",
            status="COMPLETED",
            duration_ms=dur,
            message=f"Zone weighting applied (title_weight={title_weight}). Boosted {title_boost_count} title zone passages.",
            input_info=f"{len(doc_scores)} passages scored",
            output_info=f"{title_boost_count} title passages boosted",
            details={"title_boost_factor": 1.0 + title_weight}
        )
        return weighted_scores
