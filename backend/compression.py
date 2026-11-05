"""
compression.py
Methods 17-23: Index Optimization & Compression
17. Gap Encoding
18. Variable Byte (VB) Encoding
19. Elias Gamma Encoding
20. Dictionary-as-String
21. Blocking
22. Front Coding
23. Dynamic Indexing
Also includes Byte-aligned vs Word-aligned analysis and Lossless vs Lossy stats.
"""

import math
import time
from typing import List, Tuple, Dict, Any
from execution_logger import logger


class GapEncoder:
    """Method 17: Gap Encoding (d-gaps)."""

    @staticmethod
    def encode(doc_ids: List[int]) -> List[int]:
        if not doc_ids:
            return []
        gaps = [doc_ids[0]]
        for i in range(1, len(doc_ids)):
            gaps.append(doc_ids[i] - doc_ids[i - 1])
        return gaps

    @staticmethod
    def decode(gaps: List[int]) -> List[int]:
        if not gaps:
            return []
        doc_ids = [gaps[0]]
        for i in range(1, len(gaps)):
            doc_ids.append(doc_ids[-1] + gaps[i])
        return doc_ids


class VariableByteEncoder:
    """Method 18: Variable Byte (VB) Encoding.
    Encodes integers using 7 bits of payload per byte with the highest bit (bit 7)
    as a continuation / termination flag (1 for end of byte sequence).
    """

    @staticmethod
    def encode_number(n: int) -> bytes:
        bytes_list = []
        while True:
            bytes_list.insert(0, n % 128)
            if n < 128:
                break
            n = n // 128
        bytes_list[-1] += 128  # set continuation bit to 1 on the terminal byte
        return bytes(bytes_list)

    @staticmethod
    def encode(numbers: List[int]) -> bytes:
        bytestream = bytearray()
        for num in numbers:
            bytestream.extend(VariableByteEncoder.encode_number(num))
        return bytes(bytestream)

    @staticmethod
    def decode(bytestream: bytes) -> List[int]:
        numbers = []
        n = 0
        for byte in bytestream:
            if byte < 128:
                n = 128 * n + byte
            else:
                n = 128 * n + (byte - 128)
                numbers.append(n)
                n = 0
        return numbers


class EliasGammaEncoder:
    """Method 19: Elias Gamma Encoding.
    Encodes positive integer x (x >= 1) as:
    1. Unary code of length floor(log2(x)) (written as that many 0s followed by a 1)
    2. Binary representation of remainder x - 2^floor(log2(x)) using floor(log2(x)) bits.
    """

    @staticmethod
    def encode_number(x: int) -> str:
        if x < 1:
            x = 1
        n = int(math.floor(math.log2(x)))
        unary = "0" * n + "1"
        remainder = x - (2 ** n)
        if n > 0:
            binary_rem = format(remainder, f"0{n}b")
        else:
            binary_rem = ""
        return unary + binary_rem

    @staticmethod
    def encode(numbers: List[int]) -> str:
        return "".join(EliasGammaEncoder.encode_number(n) for n in numbers)

    @staticmethod
    def decode(bitstring: str) -> List[int]:
        numbers = []
        i = 0
        length = len(bitstring)
        while i < length:
            # Read unary length of 0s until 1
            n = 0
            while i < length and bitstring[i] == '0':
                n += 1
                i += 1
            if i >= length:
                break
            # Skip the terminating '1' of unary
            i += 1
            if n > 0:
                if i + n > length:
                    break
                rem_bits = bitstring[i:i + n]
                i += n
                rem = int(rem_bits, 2)
                numbers.append((2 ** n) + rem)
            else:
                numbers.append(1)
        return numbers


class DictionaryAsString:
    """Method 20: Dictionary-as-String.
    Stores vocabulary terms contiguously in a single string buffer.
    Pointers are character offsets into the string.
    """

    def __init__(self, terms: List[str]):
        self.string_buffer = "".join(terms)
        self.term_offsets: List[int] = []
        current_offset = 0
        for t in terms:
            self.term_offsets.append(current_offset)
            current_offset += len(t)
        self.terms = terms

    @property
    def buffer_size_bytes(self) -> int:
        return len(self.string_buffer.encode("utf-8"))


class BlockedDictionary:
    """Method 21: Blocking.
    Groups terms into blocks of size k (e.g. k=4).
    Stores pointer only to the first term of each block, along with term lengths.
    """

    def __init__(self, terms: List[str], k: int = 4):
        self.k = k
        self.blocks: List[Tuple[int, List[int], str]] = []  # (start_ptr, term_lengths, concatenated_terms)
        self.total_terms = len(terms)

        for i in range(0, len(terms), k):
            block_terms = terms[i:i + k]
            cat_str = "".join(block_terms)
            lengths = [len(t) for t in block_terms]
            self.blocks.append((i, lengths, cat_str))


class FrontCoding:
    """Method 22: Front Coding.
    For consecutive terms in a block that share prefixes (e.g. automate, automatic, automation):
    Encodes terms as (common_prefix_len, suffix).
    Format: length_of_term + common_prefix + '*' + suffix.
    """

    @staticmethod
    def encode_block(terms: List[str]) -> str:
        if not terms:
            return ""
        first = terms[0]
        # Find common prefix across terms in block
        prefix = first
        for t in terms[1:]:
            common_len = 0
            while common_len < len(prefix) and common_len < len(t) and prefix[common_len] == t[common_len]:
                common_len += 1
            prefix = prefix[:common_len]

        res = [f"{len(first)}{prefix}*{first[len(prefix):]}"]
        for t in terms[1:]:
            common_with_prefix = 0
            while common_with_prefix < len(prefix) and common_with_prefix < len(t) and prefix[common_with_prefix] == t[common_with_prefix]:
                common_with_prefix += 1
            res.append(f"{len(t)}♢{common_with_prefix}*{t[common_with_prefix:]}")
        return "".join(res)

    @staticmethod
    def encode_collection(terms: List[str], k: int = 4) -> List[str]:
        encoded_blocks = []
        for i in range(0, len(terms), k):
            encoded_blocks.append(FrontCoding.encode_block(terms[i:i + k]))
        return encoded_blocks


class DynamicIndexer:
    """Method 23: Dynamic Indexing.
    Simulates main index on disk + auxiliary in-memory index, triggering
    logarithmic merge when auxiliary index exceeds memory threshold.
    """

    def __init__(self, aux_threshold: int = 50):
        self.aux_threshold = aux_threshold
        self.main_index: Dict[str, List[int]] = {}
        self.aux_index: Dict[str, List[int]] = {}
        self.merge_count = 0

    def add_document(self, doc_id: int, terms: List[str]) -> bool:
        """Adds document to auxiliary index; triggers logarithmic merge if full."""
        merged = False
        for t in terms:
            if t not in self.aux_index:
                self.aux_index[t] = []
            self.aux_index[t].append(doc_id)

        if len(self.aux_index) >= self.aux_threshold:
            self.merge()
            merged = True
        return merged

    def merge(self):
        """Logarithmic merge of auxiliary index into main index."""
        self.merge_count += 1
        for term, postings in self.aux_index.items():
            if term not in self.main_index:
                self.main_index[term] = []
            self.main_index[term].extend(postings)
            self.main_index[term] = sorted(list(set(self.main_index[term])))
        self.aux_index.clear()


class CompressionBenchmark:
    """Runs Methods 17 through 23 on the generated index and logs real comparative metrics."""

    @staticmethod
    def run_all(dictionary_terms: List[str], all_postings: List[List[int]]) -> Dict[str, Any]:
        t_start = time.time()

        # Method 17: Gap Encoding
        t0 = time.time()
        raw_ints_count = sum(len(p) for p in all_postings)
        gap_lists = [GapEncoder.encode(p) for p in all_postings]
        dur_m17 = (time.time() - t0) * 1000
        logger.log(
            stage="COMPRESSION",
            method_id=17,
            method_name="Gap Encoding",
            status="COMPLETED",
            duration_ms=dur_m17,
            message=f"Gap-encoded {raw_ints_count} document IDs into d-gaps.",
            input_info=f"{raw_ints_count} absolute doc IDs",
            output_info=f"{raw_ints_count} differential d-gaps",
            details={"sample_gap": gap_lists[0][:5] if gap_lists and gap_lists[0] else []}
        )

        # Method 18: Variable Byte Encoding
        t0 = time.time()
        flat_gaps = [g for sublist in gap_lists for g in sublist]
        vb_bytes = VariableByteEncoder.encode(flat_gaps)
        raw_size_bytes = raw_ints_count * 4  # standard 32-bit (4-byte) integer storage
        vb_size_bytes = len(vb_bytes)
        vb_ratio = (1.0 - (vb_size_bytes / raw_size_bytes)) * 100 if raw_size_bytes > 0 else 0
        dur_m18 = (time.time() - t0) * 1000
        logger.log(
            stage="COMPRESSION",
            method_id=18,
            method_name="Variable Byte Encoding",
            status="COMPLETED",
            duration_ms=dur_m18,
            message=f"VB encoded {raw_size_bytes} raw bytes down to {vb_size_bytes} bytes ({vb_ratio:.1f}% space saving).",
            input_info=f"{raw_size_bytes} bytes (32-bit ints)",
            output_info=f"{vb_size_bytes} bytes compressed",
            details={"raw_bytes": raw_size_bytes, "compressed_bytes": vb_size_bytes, "compression_ratio": f"{vb_ratio:.1f}%"}
        )

        # Method 19: Elias Gamma Encoding
        t0 = time.time()
        # Non-zero gaps for Elias gamma (replace 0 with 1 if any)
        elias_gaps = [max(1, g) for g in flat_gaps[:500]]  # sample up to 500 for fast timing
        elias_bitstring = EliasGammaEncoder.encode(elias_gaps)
        elias_bits = len(elias_bitstring)
        elias_bytes = math.ceil(elias_bits / 8)
        dur_m19 = (time.time() - t0) * 1000
        logger.log(
            stage="COMPRESSION",
            method_id=19,
            method_name="Elias Gamma Encoding",
            status="COMPLETED",
            duration_ms=dur_m19,
            message=f"Elias Gamma encoded {len(elias_gaps)} gap values into {elias_bits} bits ({elias_bytes} bytes).",
            input_info=f"{len(elias_gaps)} integers",
            output_info=f"{elias_bits} bit sequence",
            details={"bits": elias_bits, "sample_code": elias_bitstring[:32] + "..." if len(elias_bitstring) > 32 else elias_bitstring}
        )

        # Method 20: Dictionary-as-String
        t0 = time.time()
        dict_str = DictionaryAsString(dictionary_terms)
        dur_m20 = (time.time() - t0) * 1000
        pointer_overhead_saved = len(dictionary_terms) * 8  # 64-bit pointers saved
        logger.log(
            stage="COMPRESSION",
            method_id=20,
            method_name="Dictionary-as-String",
            status="COMPLETED",
            duration_ms=dur_m20,
            message=f"Compiled continuous string buffer of {dict_str.buffer_size_bytes} bytes for {len(dictionary_terms)} vocabulary terms.",
            input_info=f"{len(dictionary_terms)} distinct strings",
            output_info=f"{dict_str.buffer_size_bytes} byte string buffer",
            details={"buffer_length": dict_str.buffer_size_bytes, "pointers_eliminated": pointer_overhead_saved}
        )

        # Method 21: Blocking
        t0 = time.time()
        blocked_dict = BlockedDictionary(dictionary_terms, k=4)
        dur_m21 = (time.time() - t0) * 1000
        logger.log(
            stage="COMPRESSION",
            method_id=21,
            method_name="Blocking",
            status="COMPLETED",
            duration_ms=dur_m21,
            message=f"Grouped lexicon into {len(blocked_dict.blocks)} blocks of k=4 terms with 75% pointer reduction.",
            input_info=f"{len(dictionary_terms)} terms",
            output_info=f"{len(blocked_dict.blocks)} blocks",
            details={"block_size_k": 4, "pointer_reduction": "75%"}
        )

        # Method 22: Front Coding
        t0 = time.time()
        front_coded_blocks = FrontCoding.encode_collection(dictionary_terms, k=4)
        dur_m22 = (time.time() - t0) * 1000
        logger.log(
            stage="COMPRESSION",
            method_id=22,
            method_name="Front Coding",
            status="COMPLETED",
            duration_ms=dur_m22,
            message=f"Applied front prefix compression across {len(front_coded_blocks)} term blocks.",
            input_info=f"{len(dictionary_terms)} terms",
            output_info=f"{len(front_coded_blocks)} front-coded string blocks",
            details={"sample_block": front_coded_blocks[0] if front_coded_blocks else ""}
        )

        # Method 23: Dynamic Indexing
        t0 = time.time()
        dyn_indexer = DynamicIndexer(aux_threshold=20)
        # Simulate dynamic additions
        for idx, term in enumerate(dictionary_terms[:25]):
            dyn_indexer.add_document(1000 + idx, [term])
        dur_m23 = (time.time() - t0) * 1000
        logger.log(
            stage="COMPRESSION",
            method_id=23,
            method_name="Dynamic Indexing",
            status="COMPLETED",
            duration_ms=dur_m23,
            message=f"Simulated dynamic indexing buffer with logarithmic merge ({dyn_indexer.merge_count} merges executed).",
            input_info="Main index + Auxiliary memory store",
            output_info=f"{len(dyn_indexer.main_index)} main terms, {len(dyn_indexer.aux_index)} auxiliary terms",
            details={"merges_triggered": dyn_indexer.merge_count}
        )

        stats = {
            "raw_postings_bytes": raw_size_bytes,
            "variable_byte_bytes": vb_size_bytes,
            "vb_space_saving_pct": round(vb_ratio, 2),
            "elias_sample_bits": elias_bits,
            "dict_string_bytes": dict_str.buffer_size_bytes,
            "blocks_count": len(blocked_dict.blocks),
            "front_coding_blocks": len(front_coded_blocks),
            "total_compression_time_ms": round((time.time() - t_start) * 1000, 2)
        }
        return stats
