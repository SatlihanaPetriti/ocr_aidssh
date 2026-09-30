"""Render PDF pages to images for OCR."""
from pathlib import Path
from typing import Iterator

import pymupdf as fitz
from PIL import Image

from src.config import DEFAULT_DPI


def parse_page_spec(spec: str) -> list[int]:
    """Parse a page spec like "3,4,10-15" into a sorted list of 1-based page numbers."""
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            pages.update(range(int(start), int(end) + 1))
        else:
            pages.add(int(part))
    return sorted(pages)


def pdf_pages_to_images(
    pdf_path: Path, dpi: int = DEFAULT_DPI, pages: list[int] | None = None,
) -> Iterator[tuple[int, Image.Image]]:
    """Yield (page_number, PIL.Image) for each page in the PDF, rendered at the given DPI.

    Rendering from the PDF directly (rather than trusting any embedded text layer)
    lets us re-OCR pages whose existing text layer is unusable.

    `pages`, when given, restricts rendering to those 1-based page numbers —
    useful for pulling a handful of test pages out of a 600-page file instead
    of rendering and OCR'ing the whole thing.
    """
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    doc = fitz.open(pdf_path)
    try:
        page_indices = (
            [p - 1 for p in pages] if pages is not None else range(doc.page_count)
        )
        for page_index in page_indices:
            page = doc.load_page(page_index)
            pix = page.get_pixmap(matrix=matrix)
            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            yield page_index + 1, image
    finally:
        doc.close()
