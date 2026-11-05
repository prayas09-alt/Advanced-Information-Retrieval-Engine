"""
evaluation.py
Method 49: Information Retrieval Evaluation Metrics.
Computes Precision@K, Recall@K, F-measure (F1), Mean Average Precision (MAP), and R-Precision.
"""

import time
from typing import List, Dict, Set, Any
from execution_logger import logger


class IREvaluator:
    """Computes standard IR evaluation benchmarks."""

    @staticmethod
    def evaluate_retrieval(
        retrieved_doc_ids: List[int],
        relevant_doc_ids: Set[int],
        k: int = 10
    ) -> Dict[str, Any]:
        """Calculates Precision@K, Recall@K, F1@K, Average Precision (AP), and R-Precision."""
        t0 = time.time()
        top_k = retrieved_doc_ids[:k]
        num_relevant_total = len(relevant_doc_ids)

        if num_relevant_total == 0:
            return {
                "precision_at_k": 0.0,
                "recall_at_k": 0.0,
                "f_measure": 0.0,
                "average_precision": 0.0,
                "r_precision": 0.0,
                "k": k,
                "total_relevant": 0,
                "retrieved_relevant": 0
            }

        # 1. Precision@K and Recall@K
        relevant_in_top_k = sum(1 for d in top_k if d in relevant_doc_ids)
        precision = relevant_in_top_k / len(top_k) if top_k else 0.0
        recall = relevant_in_top_k / num_relevant_total

        # 2. F-measure (F1)
        if precision + recall > 0:
            f1 = 2.0 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0

        # 3. Average Precision (AP)
        running_rel_count = 0
        precisions_at_rel = []
        for rank, d_id in enumerate(retrieved_doc_ids, 1):
            if d_id in relevant_doc_ids:
                running_rel_count += 1
                precisions_at_rel.append(running_rel_count / rank)

        ap = sum(precisions_at_rel) / num_relevant_total if precisions_at_rel else 0.0

        # 4. R-Precision: Precision at rank R, where R = num_relevant_total
        r = min(len(retrieved_doc_ids), num_relevant_total)
        r_slice = retrieved_doc_ids[:r]
        r_rel_count = sum(1 for d in r_slice if d in relevant_doc_ids)
        r_precision = r_rel_count / num_relevant_total if num_relevant_total > 0 else 0.0

        metrics = {
            "precision_at_k": round(precision, 4),
            "recall_at_k": round(recall, 4),
            "f_measure": round(f1, 4),
            "average_precision": round(ap, 4),
            "r_precision": round(r_precision, 4),
            "k": k,
            "total_relevant": num_relevant_total,
            "retrieved_relevant": relevant_in_top_k
        }

        dur = (time.time() - t0) * 1000
        logger.log(
            stage="EVALUATION",
            method_id=49,
            method_name="Evaluation Metrics",
            status="COMPLETED",
            duration_ms=dur,
            message=f"Evaluation metrics: P@{k}={round(precision, 3)}, R@{k}={round(recall, 3)}, F1={round(f1, 3)}, AP={round(ap, 3)}, R-Prec={round(r_precision, 3)}.",
            input_info=f"Retrieved: {len(retrieved_doc_ids)}, Relevant: {num_relevant_total}",
            output_info=f"P@{k}={round(precision,3)} | R@{k}={round(recall,3)} | F1={round(f1,3)}",
            details=metrics
        )

        return metrics
