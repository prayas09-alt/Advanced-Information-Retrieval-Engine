"""
boolean_retrieval.py
Methods 35-37:
35. Boolean Retrieval
36. Postings List Intersection (with skip pointers)
37. Query Optimization
"""

import time
from typing import List, Dict, Set, Optional, Tuple, Any
from inverted_index import InvertedIndex, PostingsList, Posting
from dictionary import Dictionary
from execution_logger import logger


class BooleanOperations:
    """Core set operations on postings lists with skip pointer optimization."""

    @staticmethod
    def intersect_with_skips(p1: PostingsList, p2: PostingsList) -> Tuple[List[int], int]:
        """Method 36: Fast postings intersection utilizing skip pointers where available."""
        answer: List[int] = []
        i = 0
        j = 0
        len1 = len(p1)
        len2 = len(p2)
        skips_used = 0

        while i < len1 and j < len2:
            doc1 = p1[i].doc_id
            doc2 = p2[j].doc_id

            if doc1 == doc2:
                answer.append(doc1)
                i += 1
                j += 1
            elif doc1 < doc2:
                # Check if p1 has a skip pointer and if skip target doc_id <= doc2
                skip_target = p1[i].skip_to
                if skip_target is not None and skip_target < len1 and p1[skip_target].doc_id <= doc2:
                    while p1[i].skip_to is not None and p1[i].skip_to < len1 and p1[p1[i].skip_to].doc_id <= doc2:
                        skips_used += 1
                        i = p1[i].skip_to
                else:
                    i += 1
            else:
                # Check if p2 has a skip pointer and if skip target doc_id <= doc1
                skip_target = p2[j].skip_to
                if skip_target is not None and skip_target < len2 and p2[skip_target].doc_id <= doc1:
                    while p2[j].skip_to is not None and p2[j].skip_to < len2 and p2[p2[j].skip_to].doc_id <= doc1:
                        skips_used += 1
                        j = p2[j].skip_to
                else:
                    j += 1

        return answer, skips_used

    @staticmethod
    def union_lists(list1: List[int], list2: List[int]) -> List[int]:
        """Computes OR (union) of two sorted doc_id lists."""
        return sorted(list(set(list1).union(set(list2))))

    @staticmethod
    def difference_lists(list1: List[int], list2: List[int]) -> List[int]:
        """Computes AND NOT (difference): list1 without list2."""
        set2 = set(list2)
        return [doc for doc in list1 if doc not in set2]


class BooleanSearchEngine:
    """Executes Boolean AST queries with query optimization (Method 37)."""

    def __init__(self, inverted_index: InvertedIndex, dictionary: Dictionary, all_doc_ids: List[int]):
        self.inverted_index = inverted_index
        self.dictionary = dictionary
        self.all_doc_ids = all_doc_ids

    def execute_and_query(self, terms: List[str]) -> Tuple[List[int], int]:
        """Executes multi-term AND query with Method 37: Query Optimization."""
        t0 = time.time()
        if not terms:
            return [], 0

        # Method 37: Query Optimization - sort terms by df ascending
        t_opt = time.time()
        term_dfs = [(t, self.dictionary.get_df(t)) for t in terms]
        # Check for zero df terms
        for t, df in term_dfs:
            if df == 0:
                # Immediate empty result optimization
                logger.log(
                    stage="QUERY_PROCESSING",
                    method_id=37,
                    method_name="Query Optimization",
                    status="COMPLETED",
                    message=f"Term '{t}' has df=0. Optimized to empty result immediately.",
                    input_info=f"Terms: {terms}",
                    output_info="0 matching docs"
                )
                return [], 0

        sorted_terms = sorted(term_dfs, key=lambda x: x[1])
        ordered_terms = [t for t, _ in sorted_terms]
        dur_opt = (time.time() - t_opt) * 1000

        logger.log(
            stage="QUERY_PROCESSING",
            method_id=37,
            method_name="Query Optimization",
            status="COMPLETED",
            duration_ms=dur_opt,
            message=f"Ordered {len(terms)} terms by document frequency (df ascending): {', '.join([f'{t}(df={df})' for t, df in sorted_terms])}.",
            input_info=f"Original order: {terms}",
            output_info=f"Optimized order: {ordered_terms}"
        )

        # Method 36: Postings List Intersection
        t_inter = time.time()
        first_term = ordered_terms[0]
        first_postings = self.inverted_index.get_postings(first_term)
        current_result = first_postings.doc_ids() if first_postings else []
        total_skips = 0

        for term in ordered_terms[1:]:
            p2 = self.inverted_index.get_postings(term)
            if not p2:
                current_result = []
                break
            # Create a temporary PostingsList for the current accumulated result
            temp_p1 = PostingsList("temp")
            for doc in current_result:
                temp_p1.append(doc)
            if len(temp_p1) >= 4:
                temp_p1.build_skip_pointers()

            intersected, skips = BooleanOperations.intersect_with_skips(temp_p1, p2)
            total_skips += skips
            current_result = intersected
            if not current_result:
                break

        dur_inter = (time.time() - t_inter) * 1000
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=36,
            method_name="Postings List Intersection",
            status="COMPLETED",
            duration_ms=dur_inter,
            message=f"Intersected postings lists using skip pointers ({total_skips} skips taken). Found {len(current_result)} docs.",
            input_info=f"Conjunctive intersection of {len(ordered_terms)} lists",
            output_info=f"{len(current_result)} intersecting docs",
            details={"skips_taken": total_skips, "matching_doc_ids": current_result[:10]}
        )

        dur_bool = (time.time() - t0) * 1000
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=35,
            method_name="Boolean Retrieval",
            status="COMPLETED",
            duration_ms=dur_bool,
            message=f"Boolean AND retrieval yielded {len(current_result)} matching passages.",
            input_info=" AND ".join(terms),
            output_info=f"{len(current_result)} docs"
        )

        return current_result, total_skips

    def execute_complex_boolean(
        self,
        and_terms: List[str],
        or_terms: List[str],
        not_terms: List[str]
    ) -> List[int]:
        """Evaluates arbitrary boolean combination: (AND terms) OR (OR terms) NOT (NOT terms)."""
        t0 = time.time()
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=35,
            method_name="Boolean Retrieval",
            status="RUNNING",
            message=f"Evaluating Boolean logic: AND={and_terms}, OR={or_terms}, NOT={not_terms}.",
            input_info=f"AND:{and_terms} | OR:{or_terms} | NOT:{not_terms}",
            output_info="Executing logic"
        )

        # 1. Evaluate AND component
        if and_terms:
            res_and, _ = self.execute_and_query(and_terms)
        else:
            res_and = []

        # 2. Evaluate OR component
        res_or = []
        for term in or_terms:
            plist = self.inverted_index.get_postings(term)
            if plist:
                res_or = BooleanOperations.union_lists(res_or, plist.doc_ids())

        # Combine positive results
        if and_terms and or_terms:
            positive_result = BooleanOperations.union_lists(res_and, res_or)
        elif and_terms:
            positive_result = res_and
        elif or_terms:
            positive_result = res_or
        else:
            positive_result = list(self.all_doc_ids)

        # 3. Evaluate NOT component
        res_not = []
        for term in not_terms:
            plist = self.inverted_index.get_postings(term)
            if plist:
                res_not = BooleanOperations.union_lists(res_not, plist.doc_ids())

        final_result = BooleanOperations.difference_lists(positive_result, res_not)

        dur = (time.time() - t0) * 1000
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=35,
            method_name="Boolean Retrieval",
            status="COMPLETED",
            duration_ms=dur,
            message=f"Boolean query completed: {len(final_result)} passages satisfy the logical expression.",
            input_info=f"Positive={len(positive_result)} docs, Excluded={len(res_not)} docs",
            output_info=f"{len(final_result)} filtered docs",
            details={"matching_doc_ids": final_result[:15]}
        )

        return final_result
