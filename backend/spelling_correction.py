"""
spelling_correction.py
Methods 29-32:
29. Spelling Correction (Isolated-term)
30. Edit Distance (Levenshtein & Weighted Edit Distance)
31. N-gram Overlap
32. Jaccard Similarity
Also includes Soundex phonetic matching.
"""

import time
from typing import List, Dict, Tuple, Optional, Any, Set
from execution_logger import logger


class Soundex:
    """Phonetic algorithm encoding words by sound."""

    SOUNDEX_MAP = {
        'b': '1', 'f': '1', 'p': '1', 'v': '1',
        'c': '2', 'g': '2', 'j': '2', 'k': '2', 'q': '2', 's': '2', 'x': '2', 'z': '2',
        'd': '3', 't': '3',
        'l': '4',
        'm': '5', 'n': '5',
        'r': '6'
    }

    @staticmethod
    def encode(word: str) -> str:
        if not word:
            return ""
        word = word.lower()
        first_char = word[0].upper()
        encoded = [first_char]

        prev_code = Soundex.SOUNDEX_MAP.get(word[0], '0')

        for char in word[1:]:
            code = Soundex.SOUNDEX_MAP.get(char, '0')
            if code != '0':
                if code != prev_code:
                    encoded.append(code)
                    prev_code = code
            else:
                prev_code = '0'
            if len(encoded) == 4:
                break

        while len(encoded) < 4:
            encoded.append('0')

        return "".join(encoded[:4])


class EditDistance:
    """Method 30: Levenshtein and Weighted Edit Distance."""

    # Keyboard adjacency penalty weights for QWERTY keyboard
    KEYBOARD_ADJACENT = {
        'q': 'wase', 'w': 'qase', 'e': 'wsdr', 'r': 'edft', 't': 'rfgy',
        'y': 'tghu', 'u': 'yhji', 'i': 'ujko', 'o': 'iklp', 'p': 'ol',
        'a': 'qwsz', 's': 'awedxz', 'd': 'serfcx', 'f': 'drtgvc',
        'g': 'ftyhbv', 'h': 'gyujnb', 'j': 'huikmn', 'k': 'jiolm',
        'l': 'kop', 'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb',
        'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
    }

    @staticmethod
    def levenshtein(s1: str, s2: str) -> int:
        """Standard Levenshtein dynamic programming distance."""
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,       # deletion
                    dp[i][j - 1] + 1,       # insertion
                    dp[i - 1][j - 1] + cost # substitution
                )
        return dp[m][n]

    @staticmethod
    def weighted_edit_distance(s1: str, s2: str) -> float:
        """Weighted edit distance penalizing physically adjacent keys less."""
        m, n = len(s1), len(s2)
        dp = [[0.0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = float(i)
        for j in range(n + 1):
            dp[0][j] = float(j)

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                c1, c2 = s1[i - 1], s2[j - 1]
                if c1 == c2:
                    sub_cost = 0.0
                elif c2 in EditDistance.KEYBOARD_ADJACENT.get(c1, ""):
                    sub_cost = 0.5  # lower penalty for accidental adjacent key press
                else:
                    sub_cost = 1.0

                dp[i][j] = min(
                    dp[i - 1][j] + 1.0,         # deletion
                    dp[i][j - 1] + 1.0,         # insertion
                    dp[i - 1][j - 1] + sub_cost # substitution
                )
        return dp[m][n]


class NgramSimilarity:
    """Methods 31 and 32: N-gram Overlap and Jaccard Similarity."""

    @staticmethod
    def get_trigrams(word: str) -> Set[str]:
        padded = f"${word}$"
        return {padded[i:i + 3] for i in range(len(padded) - 2)}

    @staticmethod
    def overlap(s1: str, s2: str) -> int:
        """Method 31: Count of intersecting character trigrams."""
        t1 = NgramSimilarity.get_trigrams(s1)
        t2 = NgramSimilarity.get_trigrams(s2)
        return len(t1.intersection(t2))

    @staticmethod
    def jaccard(s1: str, s2: str) -> float:
        """Method 32: Jaccard coefficient |A ∩ B| / |A ∪ B|."""
        t1 = NgramSimilarity.get_trigrams(s1)
        t2 = NgramSimilarity.get_trigrams(s2)
        union = t1.union(t2)
        if not union:
            return 0.0
        return len(t1.intersection(t2)) / len(union)


class SpellingCorrector:
    """Orchestrates Methods 29 through 32 with execution logging."""

    def __init__(self, vocabulary: List[str]):
        self.vocabulary = vocabulary
        self.soundex_map: Dict[str, List[str]] = {}
        for w in vocabulary:
            sx = Soundex.encode(w)
            if sx not in self.soundex_map:
                self.soundex_map[sx] = []
            self.soundex_map[sx].append(w)

    def correct_term(self, term: str) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """Finds closest vocabulary word for an out-of-vocabulary query term."""
        t0 = time.time()
        term_clean = term.lower()

        if term_clean in self.vocabulary:
            # Word is spelled correctly
            logger.log(
                stage="QUERY_PROCESSING",
                method_id=29,
                method_name="Spelling Correction",
                status="SKIPPED",
                message=f"Term '{term}' is in the indexed vocabulary. Spelling correction not needed.",
                reason_skipped="Term exists in vocabulary"
            )
            return None, []

        logger.log(
            stage="QUERY_PROCESSING",
            method_id=29,
            method_name="Spelling Correction",
            status="RUNNING",
            message=f"Term '{term}' not found in vocabulary. Initiating spell check candidate generation.",
            input_info=f"Term: {term}",
            output_info="Evaluating candidates"
        )

        # Soundex candidate filtering
        sx_code = Soundex.encode(term_clean)
        sx_candidates = set(self.soundex_map.get(sx_code, []))

        # Evaluate candidate metrics across vocabulary
        # Method 30: Edit distance, Method 31: N-gram overlap, Method 32: Jaccard
        scored_candidates = []
        # Check phonetic candidates first, plus full vocabulary if small
        candidate_pool = sx_candidates if len(sx_candidates) >= 5 else set(self.vocabulary)

        t_edit = time.time()
        for cand in candidate_pool:
            lev = EditDistance.levenshtein(term_clean, cand)
            if lev <= 3:  # Only consider reasonably close terms
                wed = EditDistance.weighted_edit_distance(term_clean, cand)
                overlap = NgramSimilarity.overlap(term_clean, cand)
                jaccard = NgramSimilarity.jaccard(term_clean, cand)
                score = (1.0 / (wed + 0.5)) * 0.5 + jaccard * 0.5
                scored_candidates.append({
                    "candidate": cand,
                    "levenshtein": lev,
                    "weighted_edit": round(wed, 2),
                    "trigram_overlap": overlap,
                    "jaccard": round(jaccard, 3),
                    "combined_score": round(score, 3)
                })

        # Sort candidates descending by score
        scored_candidates.sort(key=lambda x: (x["levenshtein"], -x["jaccard"]))
        dur_eval = (time.time() - t_edit) * 1000

        top_candidates = scored_candidates[:5]
        best_candidate = top_candidates[0]["candidate"] if top_candidates else None

        # Log Method 30: Edit distance
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=30,
            method_name="Edit Distance",
            status="COMPLETED",
            duration_ms=dur_eval / 3,
            message=f"Levenshtein and Weighted Edit Distance computed for candidate terms. Best match: '{best_candidate}' (dist={top_candidates[0]['levenshtein'] if top_candidates else 'N/A'}).",
            input_info=f"Query term '{term}'",
            output_info=f"{len(scored_candidates)} candidates within distance 3",
            details={"best_match": best_candidate, "distances": [c["weighted_edit"] for c in top_candidates[:3]]}
        )

        # Log Method 31: N-gram Overlap
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=31,
            method_name="N-gram Overlap",
            status="COMPLETED",
            duration_ms=dur_eval / 3,
            message=f"Trigram character overlap evaluated across candidates.",
            input_info=f"Trigrams of '{term}'",
            output_info=f"Max overlap: {top_candidates[0]['trigram_overlap'] if top_candidates else 0}"
        )

        # Log Method 32: Jaccard Similarity
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=32,
            method_name="Jaccard Similarity",
            status="COMPLETED",
            duration_ms=dur_eval / 3,
            message=f"Calculated character n-gram Jaccard coefficient: best candidate has Jaccard {top_candidates[0]['jaccard'] if top_candidates else 0}.",
            input_info="|A ∩ B| / |A ∪ B|",
            output_info=f"Jaccard score: {top_candidates[0]['jaccard'] if top_candidates else 0}"
        )

        dur_total = (time.time() - t0) * 1000
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=29,
            method_name="Spelling Correction",
            status="COMPLETED",
            duration_ms=dur_total,
            message=f"Spelling correction suggestion: '{term}' -> '{best_candidate}'.",
            input_info=term,
            output_info=f"Suggested '{best_candidate}'",
            details={"suggestions": top_candidates}
        )

        return best_candidate, top_candidates
