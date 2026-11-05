"""
file_handler.py
Manages file uploads, format verification, and preloaded sample documents.
"""

import os
import shutil
from typing import List, Dict, Any, Optional, Tuple

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SAMPLE_DIR, exist_ok=True)

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".doc", ".csv"}


class FileHandler:
    """Manages document uploads and sample corpora."""

    @staticmethod
    def save_upload(file_obj, filename: str) -> Tuple[str, Dict[str, Any]]:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension '{ext}'. Supported: TXT, PDF, DOCX, CSV.")

        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
        target_path = os.path.join(UPLOAD_DIR, safe_filename)

        with open(target_path, "wb") as f:
            shutil.copyfileobj(file_obj, f)

        file_size = os.path.getsize(target_path)
        if file_size == 0:
            os.remove(target_path)
            raise ValueError("Uploaded file is empty (0 bytes).")

        metadata = {
            "filename": safe_filename,
            "filepath": target_path,
            "size_bytes": file_size,
            "size_formatted": FileHandler._format_size(file_size),
            "extension": ext[1:].upper()
        }
        return target_path, metadata

    @staticmethod
    def _format_size(bytes_len: int) -> str:
        if bytes_len < 1024:
            return f"{bytes_len} B"
        elif bytes_len < 1024 * 1024:
            return f"{bytes_len / 1024:.1f} KB"
        else:
            return f"{bytes_len / (1024 * 1024):.2f} MB"

    @staticmethod
    def get_sample_files() -> List[Dict[str, Any]]:
        FileHandler._ensure_sample_files_exist()
        samples = []
        for fn in sorted(os.listdir(SAMPLE_DIR)):
            path = os.path.join(SAMPLE_DIR, fn)
            ext = os.path.splitext(fn)[1].lower()
            if os.path.isfile(path) and ext in SUPPORTED_EXTENSIONS:
                size = os.path.getsize(path)
                samples.append({
                    "filename": fn,
                    "filepath": path,
                    "extension": ext[1:].upper(),
                    "size_formatted": FileHandler._format_size(size)
                })
        return samples

    @staticmethod
    def _ensure_sample_files_exist():
        """Generates rich sample files if not already present."""
        sample_txt_path = os.path.join(SAMPLE_DIR, "information_retrieval_handbook.txt")
        if not os.path.exists(sample_txt_path):
            sample_content = """Information Retrieval and Search Engine Architecture

Chapter 1: Foundations of Information Retrieval
Information retrieval is the science of searching for material of an unstructured nature within large collections. Modern web search engines index billions of web documents to satisfy user information needs.

Chapter 2: Text Preprocessing and Tokenization
Text normalization converts raw textual documents into indexable vocabulary tokens. Tokenization isolates word boundaries while handling punctuation, hyphens, and whitespace. Case folding standardizes tokens into lowercase format. Stop word removal filters frequent functional words such as 'the', 'is', 'at', and 'which'. Stemming reduces morphological variations to their grammatical stem using the Porter stemmer.

Chapter 3: Inverted Index and Positional Postings
The inverted index is the fundamental data structure supporting modern search engines. It maps each distinct vocabulary term to a postings list containing document IDs and term frequencies. Positional indexing records exact token positions within each document, enabling accurate phrase queries and proximity search. Biword indexes accelerate common two-word phrase searches.

Chapter 4: Index Optimization and Compression
Postings lists are compressed using gap encoding, which stores differences between consecutive document IDs rather than absolute integers. Variable Byte encoding compresses d-gaps by utilizing seven bits per byte for numerical payloads. Elias Gamma coding represents integers through unary length codes followed by binary offsets. Dictionary-as-string and front coding compress vocabulary lexicons to conserve memory.

Chapter 5: Boolean and Ranked Retrieval
Boolean retrieval evaluates queries using logical operators including AND, OR, and NOT. Postings list intersection utilizes skip pointers to leap across irrelevant postings in sub-linear time. Ranked retrieval scores documents using the Vector Space Model and TF-IDF weighting. Cosine similarity calculates the normalized angular distance between query vectors and document vectors.

Chapter 6: Advanced Search Improvements
Query expansion automatically augments user search queries using Rocchio relevance feedback and pseudo-relevance feedback. Latent Semantic Indexing uncovers hidden conceptual relationships through Singular Value Decomposition. Search engine effectiveness is evaluated using Precision, Recall, Mean Average Precision, and R-Precision benchmarks.
"""
            with open(sample_txt_path, "w", encoding="utf-8") as f:
                f.write(sample_content)

        sample_csv_path = os.path.join(SAMPLE_DIR, "ai_search_algorithms.csv")
        if not os.path.exists(sample_csv_path):
            csv_content = """Algorithm_Name,Category,Description,Primary_Use
Inverted_Index,Index_Construction,Maps dictionary terms to postings lists containing document IDs and frequencies,Fast full-text lookup
Positional_Index,Index_Construction,Maintains integer token offsets for each term occurrence,Phrase and proximity search
Skip_Pointers,Optimization,Places skip pointers at interval sqrt(L) in postings lists,Sub-linear postings intersection
Variable_Byte_Encoding,Compression,Byte-aligned compression encoding d-gaps with continuation bits,Index compression
Elias_Gamma_Encoding,Compression,Bit-level compression for integer d-gaps using unary length and binary offset,Lossless posting compression
Permuterm_Index,Query_Processing,Rotates circular shifts of vocabulary terms with dollar symbol,Wildcard query resolution
Levenshtein_Distance,Spelling_Correction,Dynamic programming edit distance computing minimal insertions deletions substitutions,Typo tolerance
Vector_Space_Model,Ranking,Represents documents and queries as high-dimensional vectors with L2 normalization,Ranked retrieval
Cosine_Similarity,Ranking,Calculates angular dot product between query vector and document vector,Relevance scoring
Rocchio_Feedback,Query_Expansion,Modifies query vectors using centroid of relevant and non-relevant documents,Relevance feedback
"""
            with open(sample_csv_path, "w", encoding="utf-8") as f:
                f.write(csv_content)
