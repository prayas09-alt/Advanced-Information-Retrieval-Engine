"""
text_extractor.py
Extracts and segments text from TXT, PDF, DOCX, and CSV files.
Produces discrete document/passage units with page/line metadata and zone tags.
"""

import os
import io
import csv
from typing import List, Dict, Any, Tuple


class TextSegment:
    def __init__(
        self,
        doc_id: int,
        text: str,
        page: int = 1,
        line_start: int = 1,
        line_end: int = 1,
        zone: str = "body",
        source_ref: str = ""
    ):
        self.doc_id = doc_id
        self.text = text.strip()
        self.page = page
        self.line_start = line_start
        self.line_end = line_end
        self.zone = zone  # "title" or "body"
        self.source_ref = source_ref

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "text": self.text,
            "page": self.page,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "zone": self.zone,
            "source_ref": self.source_ref
        }


class TextExtractor:
    """Extracts raw text and partitions it into indexed segments."""

    @staticmethod
    def extract_and_segment(file_path: str, filename: str) -> Tuple[List[TextSegment], Dict[str, Any]]:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".txt":
            return TextExtractor._parse_txt(file_path, filename)
        elif ext == ".pdf":
            return TextExtractor._parse_pdf(file_path, filename)
        elif ext in (".docx", ".doc"):
            return TextExtractor._parse_docx(file_path, filename)
        elif ext == ".csv":
            return TextExtractor._parse_csv(file_path, filename)
        else:
            # Fallback to plain text read
            return TextExtractor._parse_txt(file_path, filename)

    @staticmethod
    def _parse_txt(file_path: str, filename: str) -> Tuple[List[TextSegment], Dict[str, Any]]:
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        content = None
        used_encoding = "utf-8"
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    content = f.read()
                    used_encoding = enc
                    break
            except (UnicodeDecodeError, Exception):
                continue

        if content is None:
            raise ValueError(f"Could not decode text file {filename} using supported encodings.")

        lines = content.splitlines()
        segments: List[TextSegment] = []
        current_block: List[str] = []
        start_line = 1
        doc_id = 0

        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                if current_block:
                    text = " ".join(current_block)
                    zone = "title" if (doc_id == 0 or (len(current_block) == 1 and len(text) < 60)) else "body"
                    segments.append(
                        TextSegment(
                            doc_id=doc_id,
                            text=text,
                            page=1,
                            line_start=start_line,
                            line_end=idx - 1,
                            zone=zone,
                            source_ref=f"Lines {start_line}-{idx - 1}"
                        )
                    )
                    doc_id += 1
                    current_block = []
                start_line = idx + 1
            else:
                current_block.append(stripped)

        if current_block:
            text = " ".join(current_block)
            zone = "title" if (doc_id == 0 and len(text) < 60) else "body"
            segments.append(
                TextSegment(
                    doc_id=doc_id,
                    text=text,
                    page=1,
                    line_start=start_line,
                    line_end=len(lines),
                    zone=zone,
                    source_ref=f"Lines {start_line}-{len(lines)}"
                )
            )

        # Fallback if no empty line separators (single dense file)
        if not segments and lines:
            for idx, line in enumerate(lines, 1):
                if line.strip():
                    segments.append(
                        TextSegment(
                            doc_id=len(segments),
                            text=line.strip(),
                            page=1,
                            line_start=idx,
                            line_end=idx,
                            zone="title" if len(segments) == 0 else "body",
                            source_ref=f"Line {idx}"
                        )
                    )

        stats = {
            "format": "TXT",
            "encoding": used_encoding,
            "total_lines": len(lines),
            "total_segments": len(segments),
            "raw_characters": len(content)
        }
        return segments, stats

    @staticmethod
    def _parse_pdf(file_path: str, filename: str) -> Tuple[List[TextSegment], Dict[str, Any]]:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        segments: List[TextSegment] = []
        doc_id = 0
        total_pages = len(reader.pages)
        total_chars = 0

        for page_idx, page in enumerate(reader.pages, 1):
            page_text = page.extract_text() or ""
            total_chars += len(page_text)
            paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
            if not paragraphs:
                paragraphs = [p.strip() for p in page_text.splitlines() if p.strip()]

            for p_idx, para in enumerate(paragraphs, 1):
                zone = "title" if (doc_id == 0 or (p_idx == 1 and len(para) < 80)) else "body"
                segments.append(
                    TextSegment(
                        doc_id=doc_id,
                        text=para,
                        page=page_idx,
                        line_start=p_idx,
                        line_end=p_idx,
                        zone=zone,
                        source_ref=f"Page {page_idx}, Paragraph {p_idx}"
                    )
                )
                doc_id += 1

        stats = {
            "format": "PDF",
            "total_pages": total_pages,
            "total_segments": len(segments),
            "raw_characters": total_chars
        }
        return segments, stats

    @staticmethod
    def _parse_docx(file_path: str, filename: str) -> Tuple[List[TextSegment], Dict[str, Any]]:
        import docx
        doc = docx.Document(file_path)
        segments: List[TextSegment] = []
        doc_id = 0
        total_chars = 0

        for p_idx, p in enumerate(doc.paragraphs, 1):
            text = p.text.strip()
            if text:
                total_chars += len(text)
                is_heading = p.style.name.startswith("Heading") or (doc_id == 0 and len(text) < 70)
                segments.append(
                    TextSegment(
                        doc_id=doc_id,
                        text=text,
                        page=1,
                        line_start=p_idx,
                        line_end=p_idx,
                        zone="title" if is_heading else "body",
                        source_ref=f"Paragraph {p_idx}"
                    )
                )
                doc_id += 1

        # Also extract table text if present
        for t_idx, table in enumerate(doc.tables, 1):
            for r_idx, row in enumerate(table.rows, 1):
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    total_chars += len(row_text)
                    segments.append(
                        TextSegment(
                            doc_id=doc_id,
                            text=row_text,
                            page=1,
                            line_start=r_idx,
                            line_end=r_idx,
                            zone="body",
                            source_ref=f"Table {t_idx}, Row {r_idx}"
                        )
                    )
                    doc_id += 1

        stats = {
            "format": "DOCX",
            "total_paragraphs": len(doc.paragraphs),
            "total_tables": len(doc.tables),
            "total_segments": len(segments),
            "raw_characters": total_chars
        }
        return segments, stats

    @staticmethod
    def _parse_csv(file_path: str, filename: str) -> Tuple[List[TextSegment], Dict[str, Any]]:
        segments: List[TextSegment] = []
        total_chars = 0
        encodings = ["utf-8", "latin-1"]

        content = None
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    content = f.read()
                    break
            except Exception:
                continue

        if content is None:
            raise ValueError(f"Could not read CSV file {filename}")

        reader = csv.reader(io.StringIO(content))
        headers = []
        doc_id = 0

        for r_idx, row in enumerate(reader, 1):
            if not row:
                continue
            if r_idx == 1:
                headers = row
                header_text = " | ".join(headers)
                total_chars += len(header_text)
                segments.append(
                    TextSegment(
                        doc_id=doc_id,
                        text=f"CSV Columns: {header_text}",
                        page=1,
                        line_start=1,
                        line_end=1,
                        zone="title",
                        source_ref="Header Row 1"
                    )
                )
                doc_id += 1
                continue

            row_text = " ".join(f"{h}: {val}" if h else val for h, val in zip(headers, row) if val.strip())
            if not row_text.strip():
                row_text = " ".join(val.strip() for val in row if val.strip())

            if row_text.strip():
                total_chars += len(row_text)
                segments.append(
                    TextSegment(
                        doc_id=doc_id,
                        text=row_text.strip(),
                        page=1,
                        line_start=r_idx,
                        line_end=r_idx,
                        zone="body",
                        source_ref=f"Row {r_idx}"
                    )
                )
                doc_id += 1

        stats = {
            "format": "CSV",
            "total_rows": doc_id,
            "total_segments": len(segments),
            "raw_characters": total_chars
        }
        return segments, stats
