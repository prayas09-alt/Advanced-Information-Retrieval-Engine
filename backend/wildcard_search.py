"""
wildcard_search.py
Methods 26-28:
26. Wildcard Query Processing
27. Permuterm Index
28. Bigram / N-gram Processing & Post-filtering
Also includes Reverse B-Tree / Suffix simulation.
"""

import time
import re
from typing import List, Dict, Set, Tuple
from execution_logger import logger


class PermutermIndex:
    """Method 27: Permuterm Index.
    Stores all circular rotations of each vocabulary word followed by '$'.
    Enables prefix, suffix, and infix wildcard lookups in O(1) or O(log V).
    """

    def __init__(self, vocabulary: List[str]):
        # rotation -> original word
        self.rotations: Dict[str, str] = {}
        self.keys_sorted: List[str] = []
        self._build(vocabulary)

    def _build(self, vocabulary: List[str]):
        for word in vocabulary:
            w = word + "$"
            for i in range(len(w)):
                rotation = w[i:] + w[:i]
                self.rotations[rotation] = word
        self.keys_sorted = sorted(self.rotations.keys())

    def search_wildcard(self, pattern: str) -> List[str]:
        """Maps pattern to a permuterm prefix lookup:
        - X*   -> lookup prefix 'X$'
        - *X   -> lookup prefix 'X$'
        - X*Y  -> lookup prefix 'Y$X'
        - *X*  -> lookup contains 'X'
        """
        pattern_lower = pattern.lower()
        if not pattern_lower.endswith("$"):
            p = pattern_lower + "$"
        else:
            p = pattern_lower

        # Find prefix to match in permuterm
        if "*" not in pattern_lower:
            # exact match
            rot = pattern_lower + "$"
            return [self.rotations[rot]] if rot in self.rotations else []

        parts = pattern_lower.split("*")
        if len(parts) == 2:
            prefix_part, suffix_part = parts
            if prefix_part and not suffix_part:
                # X* -> look for pattern matching $X...
                # Word ended with $, so rotation starting with $ has original word
                lookup_prefix = "$" + prefix_part
            elif not prefix_part and suffix_part:
                # *X -> suffix_part + "$"
                lookup_prefix = suffix_part + "$"
            elif prefix_part and suffix_part:
                # X*Y -> suffix_part + "$" + prefix_part
                lookup_prefix = suffix_part + "$" + prefix_part
            else:
                # * alone matches all
                return list(set(self.rotations.values()))
        else:
            # Multiple wildcards e.g. *a*b* -> fallback to general prefix
            lookup_prefix = parts[0] if parts[0] else ""

        matched_words: Set[str] = set()
        for rot in self.keys_sorted:
            if rot.startswith(lookup_prefix):
                matched_words.add(self.rotations[rot])

        return sorted(list(matched_words))


class BigramWildcardSearch:
    """Method 28: Bigram / N-gram Processing with Post-Filtering.
    Splits wildcard query into character bigrams, retrieves vocabulary words
    containing all query bigrams, then post-filters candidates with regex.
    """

    def __init__(self, vocabulary: List[str]):
        # bigram -> list of vocabulary words
        self.bigram_index: Dict[str, Set[str]] = {}
        for word in vocabulary:
            w = f"${word}$"
            for i in range(len(w) - 1):
                bg = w[i:i + 2]
                if bg not in self.bigram_index:
                    self.bigram_index[bg] = set()
                self.bigram_index[bg].add(word)

    def search_with_post_filter(self, pattern: str) -> Tuple[List[str], int, int]:
        """Retrieves candidates via bigram intersection, then applies post-filtering."""
        clean_pat = pattern.lower()
        # Create regex for post-filtering
        regex_pattern = "^" + clean_pat.replace("*", ".*") + "$"
        matcher = re.compile(regex_pattern)

        # Extract query bigrams
        parts = clean_pat.split("*")
        query_bigrams = []
        if parts[0]:
            # start bigrams
            w = "$" + parts[0]
            for i in range(len(w) - 1):
                query_bigrams.append(w[i:i + 2])
        if parts[-1]:
            # end bigrams
            w = parts[-1] + "$"
            for i in range(len(w) - 1):
                query_bigrams.append(w[i:i + 2])
        # middle parts
        for p in parts[1:-1]:
            for i in range(len(p) - 1):
                query_bigrams.append(p[i:i + 2])

        if not query_bigrams:
            # Fallback
            candidates = set()
            for words in self.bigram_index.values():
                candidates.update(words)
        else:
            # Intersection of candidate sets
            candidate_sets = [self.bigram_index.get(bg, set()) for bg in query_bigrams if bg in self.bigram_index]
            if not candidate_sets:
                candidates = set()
            else:
                candidates = set.intersection(*candidate_sets)

        candidates_count = len(candidates)
        # Apply regex post-filtering
        verified = [w for w in candidates if matcher.match(w)]
        return sorted(verified), candidates_count, len(verified)


class WildcardEngine:
    """Orchestrates Methods 26, 27, and 28 with logging."""

    def __init__(self, vocabulary: List[str]):
        self.vocabulary = vocabulary
        self.permuterm = PermutermIndex(vocabulary)
        self.bigram_search = BigramWildcardSearch(vocabulary)

    def execute_wildcard(self, pattern: str) -> List[str]:
        t0 = time.time()
        # Method 26: Wildcard Query Processing
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=26,
            method_name="Wildcard Query Processing",
            status="RUNNING",
            message=f"Initiating wildcard resolution for pattern '{pattern}'.",
            input_info=f"Pattern: {pattern}",
            output_info="Searching indices"
        )

        # Method 27: Permuterm Index Lookup
        t_perm = time.time()
        perm_matches = self.permuterm.search_wildcard(pattern)
        dur_perm = (time.time() - t_perm) * 1000
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=27,
            method_name="Permuterm Index",
            status="COMPLETED",
            duration_ms=dur_perm,
            message=f"Permuterm rotation lookup matched {len(perm_matches)} terms for '{pattern}'.",
            input_info=f"Wildcard '{pattern}'",
            output_info=f"{len(perm_matches)} matching vocabulary terms",
            details={"matches": perm_matches[:10]}
        )

        # Method 28: Bigram / N-gram Processing with Post-Filtering
        t_bg = time.time()
        bg_matches, cand_count, ver_count = self.bigram_search.search_with_post_filter(pattern)
        dur_bg = (time.time() - t_bg) * 1000
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=28,
            method_name="Bigram / N-gram Processing",
            status="COMPLETED",
            duration_ms=dur_bg,
            message=f"Character bigram filtering retrieved {cand_count} candidates; post-filtering verified {ver_count} matches.",
            input_info=f"Bigrams of '{pattern}'",
            output_info=f"{cand_count} candidates -> {ver_count} post-filtered",
            details={"candidates_evaluated": cand_count, "passed_post_filter": ver_count}
        )

        # Combine/reconcile results
        final_terms = sorted(list(set(perm_matches).union(set(bg_matches))))
        dur_total = (time.time() - t0) * 1000
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=26,
            method_name="Wildcard Query Processing",
            status="COMPLETED",
            duration_ms=dur_total,
            message=f"Wildcard resolution completed for '{pattern}'. Expanded to {len(final_terms)} terms: {', '.join(final_terms[:5])}.",
            input_info=pattern,
            output_info=f"{len(final_terms)} expanded terms",
            details={"expanded_terms": final_terms}
        )
        return final_terms
