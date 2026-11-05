"""
tfidf.py
Methods 38, 39, 40:
38. Term Frequency (TF)
39. Inverse Document Frequency (IDF)
40. TF-IDF Weighting
"""

import math
from typing import Dict, List, Optional


class TFIDFCalculator:
    """Calculates TF, IDF, and TF-IDF weights."""

    @staticmethod
    def calculate_tf(raw_tf: int, scheme: str = "sublinear") -> float:
        """Method 38: Term Frequency.
        - 'raw': tf
        - 'sublinear': 1 + log10(tf) if tf > 0 else 0.0
        - 'boolean': 1.0 if tf > 0 else 0.0
        """
        if raw_tf <= 0:
            return 0.0
        if scheme == "sublinear":
            return 1.0 + math.log10(raw_tf)
        elif scheme == "raw":
            return float(raw_tf)
        elif scheme == "boolean":
            return 1.0
        return 1.0 + math.log10(raw_tf)

    @staticmethod
    def calculate_idf(total_docs: int, doc_freq: int) -> float:
        """Method 39: Inverse Document Frequency.
        idf = log10(N / df_t).
        """
        if doc_freq <= 0 or total_docs <= 0:
            return 0.0
        # Smooth IDF to prevent division by zero or negative weights
        return math.log10(total_docs / doc_freq)

    @staticmethod
    def calculate_tfidf(raw_tf: int, total_docs: int, doc_freq: int) -> float:
        """Method 40: TF-IDF.
        w_{t,d} = tf_{t,d} * idf_t.
        """
        tf_val = TFIDFCalculator.calculate_tf(raw_tf, scheme="sublinear")
        idf_val = TFIDFCalculator.calculate_idf(total_docs, doc_freq)
        return tf_val * idf_val
