"""
inverted_index.py
Methods 12, 13, 16:
12. Inverted Index Construction
13. Postings List Construction
16. Skip Pointers
"""

import math
from typing import List, Dict, Any, Optional


class Posting:
    """Individual posting node representing an occurrence in a document."""

    def __init__(self, doc_id: int, tf: int = 1):
        self.doc_id = doc_id
        self.tf = tf
        self.skip_to: Optional[int] = None  # index in postings list to skip ahead

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "tf": self.tf,
            "skip_to": self.skip_to
        }


class PostingsList:
    """Ordered sequence of postings for a specific vocabulary term."""

    def __init__(self, term: str):
        self.term = term
        self.postings: List[Posting] = []

    def append(self, doc_id: int, tf: int = 1):
        self.postings.append(Posting(doc_id, tf))

    def __len__(self) -> int:
        return len(self.postings)

    def __getitem__(self, idx: int) -> Posting:
        return self.postings[idx]

    def doc_ids(self) -> List[int]:
        return [p.doc_id for p in self.postings]

    def build_skip_pointers(self):
        """Method 16: Skip pointers placed at floor(sqrt(L)) intervals."""
        n = len(self.postings)
        if n < 4:
            return  # Skip pointers not needed for tiny postings lists

        skip_interval = int(math.isqrt(n))
        if skip_interval < 2:
            skip_interval = 2

        for i in range(0, n - skip_interval, skip_interval):
            self.postings[i].skip_to = i + skip_interval


class InvertedIndex:
    """Core inverted index mapping terms to postings lists."""

    def __init__(self):
        self.index: Dict[str, PostingsList] = {}

    def add_term_doc(self, term: str, doc_id: int, tf: int = 1):
        if term not in self.index:
            self.index[term] = PostingsList(term)
        self.index[term].append(doc_id, tf)

    def get_postings(self, term: str) -> Optional[PostingsList]:
        return self.index.get(term)

    def build_all_skip_pointers(self) -> int:
        count = 0
        for plist in self.index.values():
            if len(plist) >= 4:
                plist.build_skip_pointers()
                count += 1
        return count

    def __contains__(self, term: str) -> bool:
        return term in self.index

    def __len__(self) -> int:
        return len(self.index)
