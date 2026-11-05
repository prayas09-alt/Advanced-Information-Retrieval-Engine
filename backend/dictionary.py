"""
dictionary.py
Method 11: Dictionary Construction.
Maintains the collection lexicon, document frequencies (df_t), and collection frequencies (cf_t).
"""

from typing import Dict, Any, List, Optional


class DictionaryEntry:
    def __init__(self, term: str, doc_freq: int = 0, coll_freq: int = 0, postings_offset: int = 0):
        self.term = term
        self.doc_freq = doc_freq        # df_t: number of documents containing term
        self.coll_freq = coll_freq      # cf_t: total occurrences across collection
        self.postings_offset = postings_offset

    def to_dict(self) -> Dict[str, Any]:
        return {
            "term": self.term,
            "df": self.doc_freq,
            "cf": self.coll_freq,
            "offset": self.postings_offset
        }


class Dictionary:
    """Vocabulary Lexicon."""

    def __init__(self):
        self.entries: Dict[str, DictionaryEntry] = {}

    def add_term(self, term: str, doc_freq: int, coll_freq: int, postings_offset: int = 0):
        self.entries[term] = DictionaryEntry(term, doc_freq, coll_freq, postings_offset)

    def get(self, term: str) -> Optional[DictionaryEntry]:
        return self.entries.get(term)

    def __contains__(self, term: str) -> bool:
        return term in self.entries

    def __len__(self) -> int:
        return len(self.entries)

    def terms(self) -> List[str]:
        return sorted(self.entries.keys())

    def get_df(self, term: str) -> int:
        entry = self.entries.get(term)
        return entry.doc_freq if entry else 0

    def get_cf(self, term: str) -> int:
        entry = self.entries.get(term)
        return entry.coll_freq if entry else 0
