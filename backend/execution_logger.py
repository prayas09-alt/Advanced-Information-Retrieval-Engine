"""
execution_logger.py
Real-time Execution Logger and Event Broadcaster for Information Retrieval Methods.
Supports WebSocket and Server-Sent Events (SSE) streaming to the Live Terminal.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ExecutionEvent(BaseModel):
    id: str
    timestamp: str
    stage: str
    method_id: Optional[int] = None
    method_name: str
    status: str  # PENDING, RUNNING, COMPLETED, SKIPPED, FAILED
    level: str   # INFO, SUCCESS, WARNING, ERROR, SKIPPED
    message: str
    duration_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


# Definition catalog of all 45 standard IR methods + supplemental algorithms
ALL_METHODS_METADATA = [
    # A. Text Processing and Normalization (1 - 6)
    {
        "id": 1,
        "category": "A. Text Processing & Normalization",
        "name": "Document Parsing",
        "type": "indexing",
        "description": "Extracts structured text, zones (titles, headers, body), paragraphs, and page/line numbers from raw formats (TXT, PDF, DOCX, CSV)."
    },
    {
        "id": 2,
        "category": "A. Text Processing & Normalization",
        "name": "Tokenization",
        "type": "both",
        "description": "Splits text streams into individual tokens (words, alphanumeric units), isolating punctuation, symbols, and formatting marks."
    },
    {
        "id": 3,
        "category": "A. Text Processing & Normalization",
        "name": "Case Folding",
        "type": "both",
        "description": "Normalizes all characters to a unified lower case to ensure case-insensitive matching."
    },
    {
        "id": 4,
        "category": "A. Text Processing & Normalization",
        "name": "Stop Word Removal",
        "type": "both",
        "description": "Filters out extremely common, low-information words (e.g., 'the', 'is', 'at') to reduce index size and noise."
    },
    {
        "id": 5,
        "category": "A. Text Processing & Normalization",
        "name": "Stemming",
        "type": "both",
        "description": "Reduces words to their root or base morphological stem using the Porter Stemming algorithm."
    },
    {
        "id": 6,
        "category": "A. Text Processing & Normalization",
        "name": "Document ID Assignment",
        "type": "indexing",
        "description": "Assigns unique, sequential integer document/passage identifiers (doc_id) to each segmented unit."
    },

    # B. Index Construction (7 - 16)
    {
        "id": 7,
        "category": "B. Index Construction",
        "name": "Term-Document Pair Generation",
        "type": "indexing",
        "description": "Generates flat (term, doc_id) tuples from the tokenized and normalized document collection."
    },
    {
        "id": 8,
        "category": "B. Index Construction",
        "name": "Sorting",
        "type": "indexing",
        "description": "Sorts the term-document pairs lexicographically by term as primary key and doc_id as secondary key."
    },
    {
        "id": 9,
        "category": "B. Index Construction",
        "name": "Merging Duplicate Terms",
        "type": "indexing",
        "description": "Aggregates identical (term, doc_id) pairs into single postings with term frequency counts."
    },
    {
        "id": 10,
        "category": "B. Index Construction",
        "name": "Term Frequency Calculation",
        "type": "indexing",
        "description": "Computes the exact occurrence count of each term in each document segment (tf_t,d)."
    },
    {
        "id": 11,
        "category": "B. Index Construction",
        "name": "Dictionary Construction",
        "type": "indexing",
        "description": "Builds the vocabulary lexicon mapping each unique term to document frequency (df_t) and pointer to its postings list."
    },
    {
        "id": 12,
        "category": "B. Index Construction",
        "name": "Inverted Index Construction",
        "type": "indexing",
        "description": "Constructs the core inverted index mapping vocabulary terms to ordered lists of document occurrences."
    },
    {
        "id": 13,
        "category": "B. Index Construction",
        "name": "Postings List Construction",
        "type": "indexing",
        "description": "Instantiates compact singly linked / array structures holding doc_ids and term frequencies."
    },
    {
        "id": 14,
        "category": "B. Index Construction",
        "name": "Biword Index",
        "type": "indexing",
        "description": "Indexes consecutive token pairs (w1, w2) to provide fast, accelerated matching for common two-word phrases."
    },
    {
        "id": 15,
        "category": "B. Index Construction",
        "name": "Positional Index",
        "type": "indexing",
        "description": "Stores exact token offset positions: term -> {doc_id: [pos0, pos1, ...]} for arbitrary phrase and proximity queries."
    },
    {
        "id": 16,
        "category": "B. Index Construction",
        "name": "Skip Pointers",
        "type": "indexing",
        "description": "Augments postings lists with skip pointers at interval floor(sqrt(L)) for sub-linear postings intersection."
    },

    # C. Index Optimization and Compression (17 - 23)
    {
        "id": 17,
        "category": "C. Index Optimization & Compression",
        "name": "Gap Encoding",
        "type": "indexing",
        "description": "Replaces absolute document IDs with difference d-gaps (d1, d2 - d1, ...) to substantially reduce integer magnitudes."
    },
    {
        "id": 18,
        "category": "C. Index Optimization & Compression",
        "name": "Variable Byte Encoding",
        "type": "indexing",
        "description": "Byte-aligned compression encoding d-gaps using 7 payload bits per byte and a 1-bit continuation flag."
    },
    {
        "id": 19,
        "category": "C. Index Optimization & Compression",
        "name": "Elias Gamma Encoding",
        "type": "indexing",
        "description": "Bit-level compression representing numbers as unary length floor(log2(x)) followed by binary remainder."
    },
    {
        "id": 20,
        "category": "C. Index Optimization & Compression",
        "name": "Dictionary-as-String",
        "type": "indexing",
        "description": "Stores vocabulary terms contiguously in a single string buffer with pointer offsets to eliminate pointer overhead."
    },
    {
        "id": 21,
        "category": "C. Index Optimization & Compression",
        "name": "Blocking",
        "type": "indexing",
        "description": "Groups dictionary terms into blocks of size k (e.g. k=4) storing string offsets only for the first term of each block."
    },
    {
        "id": 22,
        "category": "C. Index Optimization & Compression",
        "name": "Front Coding",
        "type": "indexing",
        "description": "Compresses consecutive terms sharing common prefixes by storing (common_prefix_length, suffix) tuples."
    },
    {
        "id": 23,
        "category": "C. Index Optimization & Compression",
        "name": "Dynamic Indexing",
        "type": "indexing",
        "description": "Maintains an active main index alongside an auxiliary in-memory index with periodic logarithmic merge."
    },

    # D. Query Processing and Search (24 - 37)
    {
        "id": 24,
        "category": "D. Query Processing & Search",
        "name": "Query Parsing",
        "type": "query",
        "description": "Parses search input into an Abstract Syntax Tree (AST) handling Boolean operators, quotes, NEAR, and wildcards."
    },
    {
        "id": 25,
        "category": "D. Query Processing & Search",
        "name": "Query Tokenization",
        "type": "query",
        "description": "Tokenizes query terms and applies identical normalization (case folding, stop words, stemming) as the document index."
    },
    {
        "id": 26,
        "category": "D. Query Processing & Search",
        "name": "Wildcard Query Processing",
        "type": "query",
        "description": "Evaluates prefix, suffix, and infix wildcard patterns (e.g., comput*, *tion, re*al) against vocabulary structures."
    },
    {
        "id": 27,
        "category": "D. Query Processing & Search",
        "name": "Permuterm Index",
        "type": "query",
        "description": "Transforms wildcard queries into prefix lookups using rotated circular shift terms ending with the '$' symbol."
    },
    {
        "id": 28,
        "category": "D. Query Processing & Search",
        "name": "Bigram / N-gram Processing",
        "type": "query",
        "description": "Splits wildcard queries into character n-grams to retrieve candidate vocabulary matches followed by post-filtering."
    },
    {
        "id": 29,
        "category": "D. Query Processing & Search",
        "name": "Spelling Correction",
        "type": "query",
        "description": "Detects out-of-vocabulary query terms and suggests closest dictionary alternatives using edit distance and phonetic algorithms."
    },
    {
        "id": 30,
        "category": "D. Query Processing & Search",
        "name": "Edit Distance",
        "type": "query",
        "description": "Calculates minimum character insertions, deletions, substitutions, and transpositions (Levenshtein & Damerau)."
    },
    {
        "id": 31,
        "category": "D. Query Processing & Search",
        "name": "N-gram Overlap",
        "type": "query",
        "description": "Measures character tri-gram overlap between misspelled query terms and vocabulary lexicon words."
    },
    {
        "id": 32,
        "category": "D. Query Processing & Search",
        "name": "Jaccard Similarity",
        "type": "query",
        "description": "Computes set similarity coefficient |A ∩ B| / |A ∪ B| on character n-grams to rank spelling candidate terms."
    },
    {
        "id": 33,
        "category": "D. Query Processing & Search",
        "name": "Phrase Query Processing",
        "type": "query",
        "description": "Verifies that multi-term phrase tokens appear consecutively (offset delta = 1) using the positional index."
    },
    {
        "id": 34,
        "category": "D. Query Processing & Search",
        "name": "Proximity Search",
        "type": "query",
        "description": "Retrieves documents where two terms appear within a specified window distance k (e.g., term1 NEAR/k term2)."
    },
    {
        "id": 35,
        "category": "D. Query Processing & Search",
        "name": "Boolean Retrieval",
        "type": "query",
        "description": "Executes exact set-theoretic retrieval evaluating Boolean logic expressions: AND, OR, and NOT."
    },
    {
        "id": 36,
        "category": "D. Query Processing & Search",
        "name": "Postings List Intersection",
        "type": "query",
        "description": "Performs fast two-pointer intersection leaping forward using skip pointers whenever available."
    },
    {
        "id": 37,
        "category": "D. Query Processing & Search",
        "name": "Query Optimization",
        "type": "query",
        "description": "Orders multi-term conjunctive intersections in ascending order of document frequency (df) to minimize intermediate sets."
    },

    # E. Ranked Retrieval (38 - 44)
    {
        "id": 38,
        "category": "E. Ranked Retrieval",
        "name": "Term Frequency (TF)",
        "type": "query",
        "description": "Calculates sublinear term frequency weighting: 1 + log10(tf) when tf > 0, otherwise 0."
    },
    {
        "id": 39,
        "category": "E. Ranked Retrieval",
        "name": "Inverse Document Frequency (IDF)",
        "type": "query",
        "description": "Computes collection rarity weighting: idf = log10(N / df_t) where N is the total document count."
    },
    {
        "id": 40,
        "category": "E. Ranked Retrieval",
        "name": "TF-IDF",
        "type": "query",
        "description": "Combines local term frequency with global rarity: w_{t,d} = (1 + log(tf)) * log(N / df)."
    },
    {
        "id": 41,
        "category": "E. Ranked Retrieval",
        "name": "Vector Space Model",
        "type": "query",
        "description": "Represents documents and queries as high-dimensional vectors in vocabulary space with Euclidean L2 normalization."
    },
    {
        "id": 42,
        "category": "E. Ranked Retrieval",
        "name": "Cosine Similarity",
        "type": "query",
        "description": "Computes normalized angular dot product: sim(q, d) = (q · d) / (||q|| * ||d||) using accumulator tables."
    },
    {
        "id": 43,
        "category": "E. Ranked Retrieval",
        "name": "Document Ranking",
        "type": "query",
        "description": "Orders candidate documents in descending order of relevance score."
    },
    {
        "id": 44,
        "category": "E. Ranked Retrieval",
        "name": "Top-K Retrieval",
        "type": "query",
        "description": "Extracts the top K highest-scoring passages using a min-heap / priority queue to avoid full collection sort."
    },

    # F. Search Improvement and Evaluation (45 + Supplemental)
    {
        "id": 45,
        "category": "F. Search Improvement & Evaluation",
        "name": "Query Expansion & Relevance Feedback",
        "type": "query",
        "description": "Expands search queries using the Rocchio algorithm and Pseudo-Relevance Feedback (PRF) from top passages."
    },
    {
        "id": 46,
        "category": "F. Search Improvement & Evaluation",
        "name": "Latent Semantic Indexing (LSI)",
        "type": "advanced",
        "description": "Applies Truncated Singular Value Decomposition (SVD) on the term-document matrix to uncover latent semantic concepts."
    },
    {
        "id": 47,
        "category": "F. Search Improvement & Evaluation",
        "name": "Cluster Pruning",
        "type": "advanced",
        "description": "Partitions documents into leader-follower clusters for fast approximate nearest-neighbor Top-K search."
    },
    {
        "id": 48,
        "category": "F. Search Improvement & Evaluation",
        "name": "Zone Weighting",
        "type": "advanced",
        "description": "Applies linear score combination weighting matches in title/header zones higher than regular body passages."
    },
    {
        "id": 49,
        "category": "F. Search Improvement & Evaluation",
        "name": "Evaluation Metrics",
        "type": "advanced",
        "description": "Computes formal IR evaluation metrics: Precision, Recall, F-measure, Mean Average Precision (MAP), and R-Precision."
    }
]


class ExecutionLogger:
    """Central event logger and broadcaster for live terminal and method pipeline."""

    def __init__(self):
        self._listeners: List[asyncio.Queue] = []
        self._history: List[ExecutionEvent] = []
        # method_id -> current method state dict
        self._method_states: Dict[int, Dict[str, Any]] = {}
        self.reset_methods()

    def reset_methods(self):
        """Initializes or resets state for all methods."""
        self._method_states = {}
        for m in ALL_METHODS_METADATA:
            self._method_states[m["id"]] = {
                "id": m["id"],
                "name": m["name"],
                "category": m["category"],
                "type": m["type"],
                "description": m["description"],
                "status": "PENDING",
                "duration_ms": 0.0,
                "input_info": None,
                "output_info": None,
                "reason_skipped": None,
                "details": None,
                "last_run": None
            }

    def reset_query_methods(self):
        """Resets query-time methods while preserving indexing-time methods."""
        for m in ALL_METHODS_METADATA:
            if m["type"] in ("query", "both", "advanced"):
                self._method_states[m["id"]]["status"] = "PENDING"
                self._method_states[m["id"]]["duration_ms"] = 0.0
                self._method_states[m["id"]]["input_info"] = None
                self._method_states[m["id"]]["output_info"] = None
                self._method_states[m["id"]]["reason_skipped"] = None
                self._method_states[m["id"]]["details"] = None

    def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self._listeners.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self._listeners:
            self._listeners.remove(queue)

    def log(
        self,
        stage: str,
        method_id: Optional[int],
        method_name: str,
        status: str,
        message: str,
        duration_ms: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
        level: str = "INFO",
        input_info: Optional[str] = None,
        output_info: Optional[str] = None,
        reason_skipped: Optional[str] = None
    ) -> ExecutionEvent:
        """Logs an event, updates method status, and broadcasts to live terminal listeners."""
        now_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        event_id = f"evt_{int(time.time() * 1000)}_{len(self._history)}"

        event = ExecutionEvent(
            id=event_id,
            timestamp=now_str,
            stage=stage,
            method_id=method_id,
            method_name=method_name,
            status=status,
            level=level,
            message=message,
            duration_ms=duration_ms,
            details=details
        )
        self._history.append(event)
        if len(self._history) > 2000:
            self._history.pop(0)

        # Update method dashboard state if associated with a catalog method
        if method_id and method_id in self._method_states:
            st = self._method_states[method_id]
            st["status"] = status
            if duration_ms is not None:
                st["duration_ms"] = duration_ms
            if input_info:
                st["input_info"] = input_info
            if output_info:
                st["output_info"] = output_info
            if reason_skipped:
                st["reason_skipped"] = reason_skipped
            if details:
                st["details"] = details
            st["last_run"] = now_str

        # Broadcast to active queues
        for queue in list(self._listeners):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                pass

        return event

    def get_history(self) -> List[ExecutionEvent]:
        return self._history

    def clear_history(self):
        self._history.clear()

    def get_all_method_states(self) -> List[Dict[str, Any]]:
        return list(self._method_states.values())

    def get_method_state(self, method_id: int) -> Optional[Dict[str, Any]]:
        return self._method_states.get(method_id)


# Global singleton logger instance
logger = ExecutionLogger()
