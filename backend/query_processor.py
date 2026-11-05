"""
query_processor.py
Methods 24, 25, 33, 34:
24. Query Parsing
25. Query Tokenization
33. Phrase Query Processing
34. Proximity Search
"""

import re
import time
from typing import List, Dict, Set, Optional, Tuple, Any
from tokenizer import Tokenizer
from preprocessing import stemmer, STANDARD_STOPWORDS
from positional_index import PositionalIndex
from biword_index import BiwordIndex
from execution_logger import logger


class ParsedQuery:
    def __init__(
        self,
        raw_query: str,
        query_type: str,  # 'phrase', 'proximity', 'boolean', 'wildcard', 'standard'
        terms: List[str],
        stems: List[str],
        phrases: List[List[str]],
        proximity_params: Optional[Tuple[str, str, int]] = None,
        boolean_params: Optional[Dict[str, List[str]]] = None,
        wildcard_patterns: Optional[List[str]] = None
    ):
        self.raw_query = raw_query
        self.query_type = query_type
        self.terms = terms
        self.stems = stems
        self.phrases = phrases
        self.proximity_params = proximity_params
        self.boolean_params = boolean_params
        self.wildcard_patterns = wildcard_patterns or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_query": self.raw_query,
            "type": self.query_type,
            "terms": self.terms,
            "stems": self.stems,
            "phrases": self.phrases,
            "proximity": self.proximity_params,
            "boolean": self.boolean_params,
            "wildcards": self.wildcard_patterns
        }


class QueryProcessor:
    """Parses and evaluates queries with exact phrase and proximity capabilities."""

    @staticmethod
    def parse_query(
        query_str: str,
        case_fold: bool = True,
        remove_stopwords: bool = True,
        apply_stemming: bool = True
    ) -> ParsedQuery:
        t0 = time.time()
        q = query_str.strip()

        # Method 24: Query Parsing
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=24,
            method_name="Query Parsing",
            status="RUNNING",
            message=f"Analyzing user query syntax: '{query_str}'",
            input_info=f"Raw query: '{query_str}'",
            output_info="Determining query category"
        )

        query_type = "standard"
        phrases: List[List[str]] = []
        proximity_params = None
        boolean_params = None
        wildcard_patterns = []

        # 1. Check for NEAR / proximity search (e.g. term1 NEAR/3 term2 or term1 /3 term2)
        prox_match = re.search(r"(\w+)\s+(?:NEAR/|/)(\d+)\s+(\w+)", q, re.IGNORECASE)
        if prox_match:
            query_type = "proximity"
            t1, dist, t2 = prox_match.group(1), int(prox_match.group(2)), prox_match.group(3)
            proximity_params = (
                stemmer.stem(t1.lower()) if apply_stemming else t1.lower(),
                stemmer.stem(t2.lower()) if apply_stemming else t2.lower(),
                dist
            )

        # 2. Check for quoted phrase search (e.g. "information retrieval")
        phrase_matches = re.findall(r'"([^"]+)"|\'([^\']+)\'', q)
        if phrase_matches and not proximity_params:
            query_type = "phrase"
            for m in phrase_matches:
                phrase_content = m[0] if m[0] else m[1]
                p_tokens = [tok.raw.lower() if case_fold else tok.raw for tok in Tokenizer.tokenize(phrase_content)]
                p_stems = [stemmer.stem(t) if apply_stemming else t for t in p_tokens]
                if p_stems:
                    phrases.append(p_stems)

        # 3. Check for Boolean operators (AND, OR, NOT)
        has_boolean = bool(re.search(r"\b(AND|OR|NOT)\b", q))
        if has_boolean and not proximity_params and not phrases:
            query_type = "boolean"
            # Simple Boolean partition
            and_parts, or_parts, not_parts = [], [], []
            tokens = q.split()
            current_op = "AND"
            for tok in tokens:
                upper = tok.upper()
                if upper in ("AND", "OR", "NOT"):
                    current_op = upper
                else:
                    norm = tok.lower() if case_fold else tok
                    st = stemmer.stem(norm) if apply_stemming else norm
                    if current_op == "AND":
                        and_parts.append(st)
                    elif current_op == "OR":
                        or_parts.append(st)
                    elif current_op == "NOT":
                        not_parts.append(st)
            boolean_params = {"AND": and_parts, "OR": or_parts, "NOT": not_parts}

        # 4. Check for wildcards
        wildcards = [word for word in q.split() if "*" in word]
        if wildcards:
            wildcard_patterns = wildcards
            if query_type == "standard":
                query_type = "wildcard"

        # Method 25: Query Tokenization & Normalization
        t_tok = time.time()
        raw_tokens = Tokenizer.tokenize(q, case_fold=False)
        clean_terms = []
        stemmed_terms = []

        for tok in raw_tokens:
            w = tok.raw.lower() if case_fold else tok.raw
            if remove_stopwords and w.lower() in STANDARD_STOPWORDS and query_type != "phrase":
                continue
            clean_terms.append(w)
            st = stemmer.stem(w) if apply_stemming else w
            stemmed_terms.append(st)

        dur_tok = (time.time() - t_tok) * 1000
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=25,
            method_name="Query Tokenization",
            status="COMPLETED",
            duration_ms=dur_tok,
            message=f"Extracted {len(clean_terms)} normalized query tokens: {clean_terms}.",
            input_info=f"Query '{q}'",
            output_info=f"Tokens: {clean_terms} | Stems: {stemmed_terms}"
        )

        dur_parse = (time.time() - t0) * 1000
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=24,
            method_name="Query Parsing",
            status="COMPLETED",
            duration_ms=dur_parse,
            message=f"Query parsed successfully as '{query_type.upper()}' query.",
            input_info=f"Raw: '{q}'",
            output_info=f"Identified query mode: {query_type}",
            details={"type": query_type, "stems": stemmed_terms, "phrases": phrases}
        )

        return ParsedQuery(
            raw_query=q,
            query_type=query_type,
            terms=clean_terms,
            stems=stemmed_terms,
            phrases=phrases,
            proximity_params=proximity_params,
            boolean_params=boolean_params,
            wildcard_patterns=wildcard_patterns
        )

    @staticmethod
    def match_phrase(
        phrase_stems: List[str],
        positional_index: PositionalIndex,
        biword_index: Optional[BiwordIndex] = None
    ) -> List[int]:
        """Method 33: Phrase Query Processing using Positional Index & Biword Index."""
        t0 = time.time()
        if not phrase_stems:
            return []

        # If exactly 2 terms and biword index available, use for rapid candidate filter
        candidate_docs: Optional[Set[int]] = None
        if len(phrase_stems) == 2 and biword_index:
            candidates = biword_index.search_biword(phrase_stems[0], phrase_stems[1])
            candidate_docs = set(candidates)

        if candidate_docs is None:
            # Intersect document lists of all terms
            doc_sets = [set(positional_index.get_docs(term)) for term in phrase_stems]
            if not doc_sets:
                return []
            candidate_docs = set.intersection(*doc_sets)

        matching_docs: List[int] = []

        # Verify positional sequence (pos_{i+1} = pos_i + 1)
        for doc_id in sorted(list(candidate_docs)):
            first_term = phrase_stems[0]
            positions = positional_index.get_positions(first_term, doc_id)
            for start_pos in positions:
                matched = True
                for offset, next_term in enumerate(phrase_stems[1:], 1):
                    target_pos = start_pos + offset
                    next_term_positions = positional_index.get_positions(next_term, doc_id)
                    if target_pos not in next_term_positions:
                        matched = False
                        break
                if matched:
                    matching_docs.append(doc_id)
                    break

        dur = (time.time() - t0) * 1000
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=33,
            method_name="Phrase Query Processing",
            status="COMPLETED",
            duration_ms=dur,
            message=f"Verified positional continuity for phrase '{' '.join(phrase_stems)}': {len(matching_docs)} matching documents.",
            input_info=f"Phrase: '{' '.join(phrase_stems)}'",
            output_info=f"{len(matching_docs)} documents verified with positional index",
            details={"matching_doc_ids": matching_docs[:10]}
        )
        return matching_docs

    @staticmethod
    def match_proximity(
        term1: str,
        term2: str,
        k: int,
        positional_index: PositionalIndex
    ) -> List[int]:
        """Method 34: Proximity Search (|pos1 - pos2| <= k)."""
        t0 = time.time()
        docs1 = set(positional_index.get_docs(term1))
        docs2 = set(positional_index.get_docs(term2))
        common_docs = sorted(list(docs1.intersection(docs2)))

        matching_docs: List[int] = []
        for doc_id in common_docs:
            pos1_list = positional_index.get_positions(term1, doc_id)
            pos2_list = positional_index.get_positions(term2, doc_id)

            # Check if any pair satisfies |p1 - p2| <= k
            found = False
            for p1 in pos1_list:
                for p2 in pos2_list:
                    if abs(p1 - p2) <= k:
                        matching_docs.append(doc_id)
                        found = True
                        break
                if found:
                    break

        dur = (time.time() - t0) * 1000
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=34,
            method_name="Proximity Search",
            status="COMPLETED",
            duration_ms=dur,
            message=f"Proximity evaluation ({term1} NEAR/{k} {term2}): found {len(matching_docs)} passages within distance {k}.",
            input_info=f"{term1} NEAR/{k} {term2}",
            output_info=f"{len(matching_docs)} passages verified",
            details={"distance_k": k, "matching_doc_ids": matching_docs[:10]}
        )
        return matching_docs
