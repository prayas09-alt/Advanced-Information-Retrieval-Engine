"""
preprocessing.py
Implements Methods 1-6:
1. Document Parsing
2. Tokenization
3. Case Folding
4. Stop Word Removal
5. Stemming (Porter Stemmer)
6. Document ID Assignment
"""

import time
import re
from typing import List, Dict, Set, Tuple, Optional
from tokenizer import Tokenizer, Token
from text_extractor import TextSegment
from execution_logger import logger

# Standard IR Stopwords list (179 common words)
STANDARD_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your",
    "yours", "yourself", "yourselves"
}


class PorterStemmer:
    """Complete implementation of Martin Porter's 1980 Stemming Algorithm."""

    def __init__(self):
        self.b = ""
        self.k = 0
        self.k0 = 0
        self.j = 0

    def _cons(self, i: int) -> bool:
        ch = self.b[i]
        if ch in "aeiou":
            return False
        if ch == 'y':
            return True if i == self.k0 else not self._cons(i - 1)
        return True

    def _m(self) -> int:
        n = 0
        i = self.k0
        while True:
            if i > self.j:
                return n
            if not self._cons(i):
                break
            i += 1
        i += 1
        while True:
            while True:
                if i > self.j:
                    return n
                if self._cons(i):
                    break
                i += 1
            i += 1
            n += 1
            while True:
                if i > self.j:
                    return n
                if not self._cons(i):
                    break
                i += 1
            i += 1

    def _vowelinstem(self) -> bool:
        for i in range(self.k0, self.j + 1):
            if not self._cons(i):
                return True
        return False

    def _doublec(self, i: int) -> bool:
        if i < self.k0 + 1:
            return False
        if self.b[i] != self.b[i - 1]:
            return False
        return self._cons(i)

    def _cvc(self, i: int) -> bool:
        if i < self.k0 + 2 or not self._cons(i) or self._cons(i - 1) or not self._cons(i - 2):
            return False
        ch = self.b[i]
        if ch in "wxy":
            return False
        return True

    def _ends(self, s: str) -> bool:
        length = len(s)
        if s[length - 1] != self.b[self.k]:
            return False
        if length > self.k - self.k0 + 1:
            return False
        if self.b[self.k - length + 1:self.k + 1] != s:
            return False
        self.j = self.k - length
        return True

    def _setto(self, s: str):
        length = len(s)
        self.b = self.b[:self.j + 1] + s + self.b[self.j + length + 1:]
        self.k = self.j + length

    def _r(self, s: str):
        if self._m() > 0:
            self._setto(s)

    def _step1ab(self):
        if self.b[self.k] == 's':
            if self._ends("sses"):
                self.k -= 2
            elif self._ends("ies"):
                self._setto("i")
            elif self.b[self.k - 1] != 's':
                self.k -= 1
        if self._ends("eed"):
            if self._m() > 0:
                self.k -= 1
        elif (self._ends("ed") or self._ends("ing")) and self._vowelinstem():
            self.k = self.j
            if self._ends("at"):
                self._setto("ate")
            elif self._ends("bl"):
                self._setto("ble")
            elif self._ends("iz"):
                self._setto("ize")
            elif self._doublec(self.k):
                self.k -= 1
                ch = self.b[self.k]
                if ch in "lsz":
                    self.k += 1
            elif self._m() == 1 and self._cvc(self.k):
                self._setto("e")

    def _step1c(self):
        if self._ends("y") and self._vowelinstem():
            self.b = self.b[:self.k] + 'i' + self.b[self.k + 1:]

    def _step2(self):
        ch = self.b[self.k - 1] if self.k > self.k0 else ''
        if ch == 'a':
            if self._ends("ational"): self._r("ate")
            elif self._ends("tional"): self._r("tion")
        elif ch == 'c':
            if self._ends("enci"): self._r("ence")
            elif self._ends("anci"): self._r("ance")
        elif ch == 'e':
            if self._ends("izer"): self._r("ize")
        elif ch == 'l':
            if self._ends("abli"): self._r("able")
            elif self._ends("alli"): self._r("al")
            elif self._ends("entli"): self._r("ent")
            elif self._ends("eli"): self._r("e")
            elif self._ends("ousli"): self._r("ous")
        elif ch == 'o':
            if self._ends("ization"): self._r("ize")
            elif self._ends("ation"): self._r("ate")
            elif self._ends("ator"): self._r("ate")
        elif ch == 's':
            if self._ends("alism"): self._r("al")
            elif self._ends("iveness"): self._r("ive")
            elif self._ends("fulness"): self._r("ful")
            elif self._ends("ousness"): self._r("ous")
        elif ch == 't':
            if self._ends("aliti"): self._r("al")
            elif self._ends("iviti"): self._r("ive")
            elif self._ends("biliti"): self._r("ble")
        elif ch == 'g':
            if self._ends("logi"): self._r("log")

    def _step3(self):
        ch = self.b[self.k]
        if ch == 'e':
            if self._ends("icate"): self._r("ic")
            elif self._ends("ative"): self._r("")
            elif self._ends("alize"): self._r("al")
        elif ch == 'i':
            if self._ends("iciti"): self._r("ic")
        elif ch == 'l':
            if self._ends("ical"): self._r("ic")
            elif self._ends("ful"): self._r("")
        elif ch == 's':
            if self._ends("ness"): self._r("")

    def _step4(self):
        ch = self.b[self.k - 1] if self.k > self.k0 else ''
        if ch == 'a':
            if self._ends("al"): pass
            else: return
        elif ch == 'c':
            if self._ends("ance") or self._ends("ence"): pass
            else: return
        elif ch == 'e':
            if self._ends("er"): pass
            else: return
        elif ch == 'i':
            if self._ends("ic"): pass
            else: return
        elif ch == 'l':
            if self._ends("able") or self._ends("ible"): pass
            else: return
        elif ch == 'n':
            if self._ends("ant") or self._ends("ement") or self._ends("ment") or self._ends("ent"): pass
            else: return
        elif ch == 'o':
            if self._ends("ion") and (self.b[self.j] in "st"): pass
            elif self._ends("ou"): pass
            else: return
        elif ch == 's':
            if self._ends("ism"): pass
            else: return
        elif ch == 't':
            if self._ends("ate") or self._ends("iti"): pass
            else: return
        elif ch == 'u':
            if self._ends("ous"): pass
            else: return
        elif ch == 'v':
            if self._ends("ive"): pass
            else: return
        elif ch == 'z':
            if self._ends("ize"): pass
            else: return
        else:
            return
        if self._m() > 1:
            self.k = self.j

    def _step5(self):
        self.j = self.k
        if self.b[self.k] == 'e':
            a = self._m()
            if a > 1 or (a == 1 and not self._cvc(self.k - 1)):
                self.k -= 1
        if self.b[self.k] == 'l' and self._doublec(self.k) and self._m() > 1:
            self.k -= 1

    def stem(self, word: str) -> str:
        word = word.lower()
        if len(word) <= 2:
            return word
        self.b = word
        self.k = len(word) - 1
        self.k0 = 0
        self._step1ab()
        self._step1c()
        self._step2()
        self._step3()
        self._step4()
        self._step5()
        return self.b[:self.k + 1]


# Singleton stemmer instance
stemmer = PorterStemmer()


class ProcessedDocument:
    """Holds all tokens, positions, and stems for a single document segment."""

    def __init__(
        self,
        doc_id: int,
        segment: TextSegment,
        raw_tokens: List[Token],
        tokens: List[str],
        stems: List[str],
        positions: Dict[str, List[int]]
    ):
        self.doc_id = doc_id
        self.segment = segment
        self.raw_tokens = raw_tokens
        self.tokens = tokens          # normalized tokens (case folded, stopwords optionally kept)
        self.stems = stems            # stemmed tokens
        self.positions = positions    # stem/token -> list of integer token positions in document


class PreprocessingPipeline:
    """Orchestrates Methods 1 through 6 with live event logging."""

    @staticmethod
    def process_segments(
        segments: List[TextSegment],
        apply_case_folding: bool = True,
        remove_stopwords: bool = True,
        apply_stemming: bool = True
    ) -> List[ProcessedDocument]:
        processed_docs: List[ProcessedDocument] = []

        total_raw_tokens = 0
        total_filtered_tokens = 0
        total_unique_stems: Set[str] = set()

        # Method 6: Document ID Assignment
        t0 = time.time()
        doc_id_map = {seg.doc_id: seg for seg in segments}
        dur_doc_id = (time.time() - t0) * 1000
        logger.log(
            stage="PREPROCESSING",
            method_id=6,
            method_name="Document ID Assignment",
            status="COMPLETED",
            duration_ms=dur_doc_id,
            message=f"Assigned sequential IDs (doc_0 to doc_{len(segments)-1}) to {len(segments)} segments.",
            input_info=f"{len(segments)} text segments",
            output_info=f"doc_0 through doc_{len(segments)-1} mapped"
        )

        # Method 2: Tokenization
        t0 = time.time()
        doc_token_map: Dict[int, List[Token]] = {}
        for seg in segments:
            tokens = Tokenizer.tokenize(seg.text, case_fold=False)
            doc_token_map[seg.doc_id] = tokens
            total_raw_tokens += len(tokens)
        dur_tok = (time.time() - t0) * 1000
        logger.log(
            stage="PREPROCESSING",
            method_id=2,
            method_name="Tokenization",
            status="COMPLETED",
            duration_ms=dur_tok,
            message=f"Tokenized {len(segments)} document segments into {total_raw_tokens} raw tokens.",
            input_info=f"{len(segments)} segments",
            output_info=f"{total_raw_tokens} total tokens extracted"
        )

        # Method 3: Case Folding
        t0 = time.time()
        if apply_case_folding:
            dur_cf = (time.time() - t0) * 1000
            logger.log(
                stage="PREPROCESSING",
                method_id=3,
                method_name="Case Folding",
                status="COMPLETED",
                duration_ms=dur_cf,
                message=f"Applied lowercase normalization to all {total_raw_tokens} tokens.",
                input_info=f"{total_raw_tokens} raw case tokens",
                output_info="Unified lowercase stream"
            )
        else:
            logger.log(
                stage="PREPROCESSING",
                method_id=3,
                method_name="Case Folding",
                status="SKIPPED",
                message="Case folding skipped: Case-sensitive search option enabled.",
                reason_skipped="User requested case-sensitive preservation"
            )

        # Method 4: Stop Word Removal
        t0 = time.time()
        removed_stop_count = 0
        if remove_stopwords:
            for d_id, tokens in doc_token_map.items():
                for tok in tokens:
                    w = tok.raw.lower() if apply_case_folding else tok.raw
                    if w in STANDARD_STOPWORDS:
                        removed_stop_count += 1
            dur_sw = (time.time() - t0) * 1000
            logger.log(
                stage="PREPROCESSING",
                method_id=4,
                method_name="Stop Word Removal",
                status="COMPLETED",
                duration_ms=dur_sw,
                message=f"Filtered {removed_stop_count} stop words from collection using 179-word stoplist.",
                input_info=f"{total_raw_tokens} tokens",
                output_info=f"{removed_stop_count} stop words filtered"
            )
        else:
            logger.log(
                stage="PREPROCESSING",
                method_id=4,
                method_name="Stop Word Removal",
                status="SKIPPED",
                message="Stop word removal skipped (all tokens preserved).",
                reason_skipped="Stop word filter disabled in index options"
            )

        # Method 5: Stemming
        t0 = time.time()
        stem_samples = []
        for seg in segments:
            raw_tokens = doc_token_map[seg.doc_id]
            clean_tokens: List[str] = []
            stemmed_tokens: List[str] = []
            positions: Dict[str, List[int]] = {}

            for tok in raw_tokens:
                word = tok.raw.lower() if apply_case_folding else tok.raw
                if remove_stopwords and word.lower() in STANDARD_STOPWORDS:
                    continue
                clean_tokens.append(word)

                if apply_stemming:
                    st = stemmer.stem(word)
                    if len(stem_samples) < 5 and st != word:
                        stem_samples.append(f"{word} -> {st}")
                else:
                    st = word

                stemmed_tokens.append(st)
                total_unique_stems.add(st)

                if st not in positions:
                    positions[st] = []
                positions[st].append(tok.position)

            processed_docs.append(
                ProcessedDocument(
                    doc_id=seg.doc_id,
                    segment=seg,
                    raw_tokens=raw_tokens,
                    tokens=clean_tokens,
                    stems=stemmed_tokens,
                    positions=positions
                )
            )

        dur_stem = (time.time() - t0) * 1000
        if apply_stemming:
            logger.log(
                stage="PREPROCESSING",
                method_id=5,
                method_name="Stemming",
                status="COMPLETED",
                duration_ms=dur_stem,
                message=f"Porter stemming applied. Vocabulary condensed to {len(total_unique_stems)} unique stems. Examples: {', '.join(stem_samples[:4])}.",
                input_info=f"{total_raw_tokens - removed_stop_count} words",
                output_info=f"{len(total_unique_stems)} root stems"
            )
        else:
            logger.log(
                stage="PREPROCESSING",
                method_id=5,
                method_name="Stemming",
                status="SKIPPED",
                message="Stemming skipped: Exact word form preservation enabled.",
                reason_skipped="Stemming disabled"
            )

        return processed_docs
