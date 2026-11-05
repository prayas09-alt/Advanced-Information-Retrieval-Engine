"""
tokenizer.py
Implements text tokenization (Method 2) and case folding (Method 3).
Tracks token offsets and positional indices for phrase and proximity searches.
"""

import re
from typing import List, Tuple


class Token:
    def __init__(self, raw: str, normalized: str, position: int, char_start: int, char_end: int):
        self.raw = raw
        self.normalized = normalized
        self.position = position
        self.char_start = char_start
        self.char_end = char_end

    def __repr__(self):
        return f"Token({self.normalized} @ pos {self.position})"


class Tokenizer:
    """Tokenizes text streams into discrete tokens with positions and character offsets."""

    # Matches words, numbers, and hyphenated terms
    TOKEN_REGEX = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*")

    @staticmethod
    def tokenize(text: str, case_fold: bool = True) -> List[Token]:
        tokens: List[Token] = []
        pos = 0
        for match in Tokenizer.TOKEN_REGEX.finditer(text):
            raw = match.group(0)
            norm = raw.lower() if case_fold else raw
            tokens.append(
                Token(
                    raw=raw,
                    normalized=norm,
                    position=pos,
                    char_start=match.start(),
                    char_end=match.end()
                )
            )
            pos += 1
        return tokens

    @staticmethod
    def case_fold(text: str) -> str:
        """Method 3: Case folding."""
        return text.lower()
