"""
positional_index.py
Method 15: Positional Index Construction.
Maps terms to documents and precise token offset positions:
term -> {doc_id: [pos0, pos1, ...]}
Used for phrase matching and arbitrary proximity verification.
"""

from typing import Dict, List, Optional, Any


class PositionalIndex:
    """Positional Inverted Index."""

    def __init__(self):
        # term -> {doc_id: [positions]}
        self.index: Dict[str, Dict[int, List[int]]] = {}

    def add_position(self, term: str, doc_id: int, pos: int):
        if term not in self.index:
            self.index[term] = {}
        if doc_id not in self.index[term]:
            self.index[term][doc_id] = []
        self.index[term][doc_id].append(pos)

    def get_positions(self, term: str, doc_id: int) -> List[int]:
        if term in self.index and doc_id in self.index[term]:
            return self.index[term][doc_id]
        return []

    def get_docs(self, term: str) -> List[int]:
        if term in self.index:
            return sorted(self.index[term].keys())
        return []

    def __contains__(self, term: str) -> bool:
        return term in self.index

    def __len__(self) -> int:
        return len(self.index)
