"""Ingestion: PDFs -> pages -> clean text -> chunks.

Design decisions (see also notebooks/01_retrieval.ipynb):
- Pages keep their page number, so answers can cite "ΑΑΔΕ FAQ, p. 17".
- Chunks are built within each page (exactly one page per chunk). The cost is
  that a sentence crossing a page break is cut.
- Chunks store only filename/page/text. Title, URL and date are looked up in
  data/sources.csv, the single source of truth for document details.
"""
import re
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

from src.config import CHUNK_SIZE, OVERLAP, RAW_DIR, SOURCES_PATH


def load_sources(path: Path = SOURCES_PATH) -> pd.DataFrame:
    """Document metadata (title, publisher, url, published_date), indexed by filename."""
    return pd.read_csv(path, encoding="utf-8").set_index("filename")


def load_pages(raw_dir: Path = RAW_DIR) -> list[dict]:
    """Read every PDF page by page: [{"filename", "page", "text"}, ...] (raw text)."""
    pages = []
    for pdf_path in sorted(raw_dir.glob("*.pdf")):
        reader = PdfReader(pdf_path)
        for page_num, page in enumerate(reader.pages, start=1):
            pages.append({
                "filename": pdf_path.name,
                "page": page_num,
                "text": page.extract_text() or "",
            })
    return pages


def clean_text(text: str) -> str:
    """Remove PDF-extraction noise that hurts search quality.

    1. TOC dot leaders ("Έννοιες ........ 2") become a space. Runs before step 3
       so the spaces around the dots are collapsed too.
    2. Words split across lines in ΦΕΚ PDFs ("βραχυχρό-\\nνιας") are joined, but
       only between two lowercase Greek letters, so real dashes such as
       "Α.1217/2023 - ΦΕΚ" are kept. [ά-ώ] covers U+03AC-U+03CE: all lowercase
       Greek letters, accented ones and final ς.
    3. Any run of whitespace becomes one space.

    Known limitation: genuine hyphenated compounds are also merged, and words
    split in capitals are not fixed. Both are rare in this corpus.
    """
    text = re.sub(r"\.{2,}", " ", text)
    text = re.sub(r"([ά-ώ])\s*-\s*([ά-ώ])", r"\1\2", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """Split text into chunks of at most `chunk_size` characters with `overlap`.

    Chunks end at a word boundary. `max(..., start + 1)` guarantees the loop
    always moves forward, so no input can cause an infinite loop.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # don't cut a word in half: move the end back to the last space
        if end < len(text):
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        # next chunk starts `overlap` characters earlier, at a word boundary
        next_start = max(end - overlap, start + 1)
        space = text.find(" ", next_start, end)
        start = space + 1 if space != -1 else next_start
    return [c for c in chunks if c]


def build_chunks(pages: list[dict], chunk_size: int = CHUNK_SIZE,
                 overlap: int = OVERLAP) -> list[dict]:
    """Clean each page and split it into chunks with a unique chunk_id."""
    chunks = []
    for p in pages:
        for i, chunk in enumerate(chunk_text(clean_text(p["text"]), chunk_size, overlap)):
            chunks.append({
                "chunk_id": f"{p['filename']}_p{p['page']}_c{i}",
                "filename": p["filename"],
                "page": p["page"],
                "text": chunk,
            })
    return chunks
