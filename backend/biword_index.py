"""
biword_index.py
Method 14: Biword Index.
Indexes consecutive pairs of tokens (w_i, w_{i+1}) -> [doc_id, ...]
Allows rapid filtering for common two-word phrase queries.
"""

from typing import Dict, List, Set, Tuple


class BiwordIndex:
    """Biword Index for fast two-word phrase retrieval."""

    def __init__(self):
        # (term1, term2) -> sorted list of doc_ids
        self.index: Dict[Tuple[str, str], Set[int]] = {}

    def add_biword(self, term1: str, term2: str, doc_id: int):
        pair = (term1, term2)
        if pair not in self.index:
            self.index[pair] = set()
        self.index[pair].add(doc_id)

    def search_biword(self, term1: str, term2: str) -> List[int]:
        pair = (term1, term2)
        return sorted(list(self.index.get(pair, set())))

    def __len__(self) -> int:
        return len(self.index)
