"""
indexer.py
Coordinates Index Construction:
Method 7: Term-Document Pair Generation
Method 8: Sorting
Method 9: Merging Duplicate Terms
Method 10: Term Frequency Calculation
Method 11: Dictionary Construction
Method 12: Inverted Index Construction
Method 13: Postings List Construction
Method 14: Biword Index
Method 15: Positional Index
Method 16: Skip Pointers
"""

import time
from typing import List, Dict, Tuple, Any
from preprocessing import ProcessedDocument
from dictionary import Dictionary
from inverted_index import InvertedIndex
from positional_index import PositionalIndex
from biword_index import BiwordIndex
from execution_logger import logger


class IndexBundle:
    """Encapsulates all compiled indexing structures for an uploaded document."""

    def __init__(
        self,
        dictionary: Dictionary,
        inverted_index: InvertedIndex,
        positional_index: PositionalIndex,
        biword_index: BiwordIndex,
        processed_docs: List[ProcessedDocument],
        total_term_doc_pairs: int,
        build_time_ms: float
    ):
        self.dictionary = dictionary
        self.inverted_index = inverted_index
        self.positional_index = positional_index
        self.biword_index = biword_index
        self.processed_docs = processed_docs
        self.total_term_doc_pairs = total_term_doc_pairs
        self.build_time_ms = build_time_ms

    @property
    def total_docs(self) -> int:
        return len(self.processed_docs)

    @property
    def vocab_size(self) -> int:
        return len(self.dictionary)


class Indexer:
    """Executes Methods 7 through 16 with real-time event logging."""

    @staticmethod
    def build_all(processed_docs: List[ProcessedDocument]) -> IndexBundle:
        t_start_all = time.time()
        num_docs = len(processed_docs)

        # Method 7: Term-Document Pair Generation
        t0 = time.time()
        pairs: List[Tuple[str, int]] = []
        for pdoc in processed_docs:
            for term in pdoc.stems:
                pairs.append((term, pdoc.doc_id))
        dur_m7 = (time.time() - t0) * 1000
        logger.log(
            stage="INDEXING",
            method_id=7,
            method_name="Term-Document Pair Generation",
            status="COMPLETED",
            duration_ms=dur_m7,
            message=f"Generated {len(pairs)} raw (term, doc_id) pairs across {num_docs} document segments.",
            input_info=f"{num_docs} processed documents",
            output_info=f"{len(pairs)} term-doc pairs generated",
            details={"sample_pairs": [f"({t}, {d})" for t, d in pairs[:6]]}
        )

        # Method 8: Sorting
        t0 = time.time()
        pairs.sort(key=lambda x: (x[0], x[1]))
        dur_m8 = (time.time() - t0) * 1000
        logger.log(
            stage="INDEXING",
            method_id=8,
            method_name="Sorting",
            status="COMPLETED",
            duration_ms=dur_m8,
            message=f"Sorted {len(pairs)} term-doc pairs lexicographically by term and doc_id.",
            input_info=f"{len(pairs)} unsorted pairs",
            output_info=f"{len(pairs)} sorted pairs",
            details={"sort_keys": "primary: term, secondary: doc_id"}
        )

        # Method 9: Merging Duplicate Terms & Method 10: Term Frequency Calculation
        t0 = time.time()
        # Aggregated structure: term -> list of (doc_id, tf)
        merged_postings: Dict[str, List[Tuple[int, int]]] = {}
        term_coll_freq: Dict[str, int] = {}

        if pairs:
            current_term, current_doc = pairs[0]
            current_tf = 0
            for term, doc_id in pairs:
                if term == current_term and doc_id == current_doc:
                    current_tf += 1
                else:
                    if current_term not in merged_postings:
                        merged_postings[current_term] = []
                    merged_postings[current_term].append((current_doc, current_tf))
                    term_coll_freq[current_term] = term_coll_freq.get(current_term, 0) + current_tf

                    current_term = term
                    current_doc = doc_id
                    current_tf = 1

            if current_term not in merged_postings:
                merged_postings[current_term] = []
            merged_postings[current_term].append((current_doc, current_tf))
            term_coll_freq[current_term] = term_coll_freq.get(current_term, 0) + current_tf

        dur_m9 = (time.time() - t0) * 1000
        logger.log(
            stage="INDEXING",
            method_id=9,
            method_name="Merging Duplicate Terms",
            status="COMPLETED",
            duration_ms=dur_m9 / 2,
            message=f"Merged duplicate occurrences into {len(merged_postings)} distinct vocabulary terms.",
            input_info=f"{len(pairs)} sorted pairs",
            output_info=f"{len(merged_postings)} unique term entries"
        )

        logger.log(
            stage="INDEXING",
            method_id=10,
            method_name="Term Frequency Calculation",
            status="COMPLETED",
            duration_ms=dur_m9 / 2,
            message=f"Calculated intra-document term frequencies tf(t, d) for all {len(merged_postings)} terms.",
            input_info=f"{len(merged_postings)} terms",
            output_info="tf values per document stored in postings"
        )

        # Method 11: Dictionary Construction
        t0 = time.time()
        dictionary = Dictionary()
        offset_counter = 0
        for term, postings in merged_postings.items():
            df = len(postings)
            cf = term_coll_freq.get(term, 0)
            dictionary.add_term(term, doc_freq=df, coll_freq=cf, postings_offset=offset_counter)
            offset_counter += df
        dur_m11 = (time.time() - t0) * 1000
        logger.log(
            stage="INDEXING",
            method_id=11,
            method_name="Dictionary Construction",
            status="COMPLETED",
            duration_ms=dur_m11,
            message=f"Constructed vocabulary dictionary holding {len(dictionary)} entries with df and cf metadata.",
            input_info=f"{len(merged_postings)} aggregated terms",
            output_info=f"Lexicon of {len(dictionary)} terms compiled"
        )

        # Method 12: Inverted Index Construction & Method 13: Postings List Construction
        t0 = time.time()
        inv_index = InvertedIndex()
        total_postings_nodes = 0
        for term, postings in merged_postings.items():
            for doc_id, tf in postings:
                inv_index.add_term_doc(term, doc_id, tf)
                total_postings_nodes += 1
        dur_m12 = (time.time() - t0) * 1000

        logger.log(
            stage="INDEXING",
            method_id=12,
            method_name="Inverted Index Construction",
            status="COMPLETED",
            duration_ms=dur_m12 / 2,
            message=f"Constructed inverted index with {len(inv_index)} term postings lists.",
            input_info=f"{len(merged_postings)} terms",
            output_info=f"Inverted index mapping {len(inv_index)} terms -> postings"
        )

        logger.log(
            stage="INDEXING",
            method_id=13,
            method_name="Postings List Construction",
            status="COMPLETED",
            duration_ms=dur_m12 / 2,
            message=f"Created {total_postings_nodes} individual posting nodes with doc_id and tf values.",
            input_info=f"{total_postings_nodes} doc occurrences",
            output_info=f"{total_postings_nodes} posting nodes linked"
        )

        # Method 14: Biword Index
        t0 = time.time()
        biword_idx = BiwordIndex()
        total_biwords = 0
        for pdoc in processed_docs:
            stems = pdoc.stems
            for i in range(len(stems) - 1):
                biword_idx.add_biword(stems[i], stems[i + 1], pdoc.doc_id)
                total_biwords += 1
        dur_m14 = (time.time() - t0) * 1000
        logger.log(
            stage="INDEXING",
            method_id=14,
            method_name="Biword Index",
            status="COMPLETED",
            duration_ms=dur_m14,
            message=f"Constructed biword index containing {len(biword_idx)} unique two-word phrases from {total_biwords} pairs.",
            input_info=f"{total_biwords} adjacent token transitions",
            output_info=f"{len(biword_idx)} unique biword phrases indexed"
        )

        # Method 15: Positional Index
        t0 = time.time()
        pos_index = PositionalIndex()
        for pdoc in processed_docs:
            for term, positions in pdoc.positions.items():
                for pos in positions:
                    pos_index.add_position(term, pdoc.doc_id, pos)
        dur_m15 = (time.time() - t0) * 1000
        logger.log(
            stage="INDEXING",
            method_id=15,
            method_name="Positional Index",
            status="COMPLETED",
            duration_ms=dur_m15,
            message=f"Built positional index tracking exact token offsets for {len(pos_index)} terms.",
            input_info=f"{len(pos_index)} terms across {num_docs} docs",
            output_info="Full positional mapping instantiated"
        )

        # Method 16: Skip Pointers
        t0 = time.time()
        skip_count = inv_index.build_all_skip_pointers()
        dur_m16 = (time.time() - t0) * 1000
        logger.log(
            stage="INDEXING",
            method_id=16,
            method_name="Skip Pointers",
            status="COMPLETED",
            duration_ms=dur_m16,
            message=f"Generated skip pointers with interval floor(sqrt(L)) for {skip_count} eligible postings lists.",
            input_info=f"{len(inv_index)} postings lists",
            output_info=f"Skip pointers embedded on {skip_count} lists"
        )

        total_time_ms = (time.time() - t_start_all) * 1000

        return IndexBundle(
            dictionary=dictionary,
            inverted_index=inv_index,
            positional_index=pos_index,
            biword_index=biword_idx,
            processed_docs=processed_docs,
            total_term_doc_pairs=len(pairs),
            build_time_ms=total_time_ms
        )
