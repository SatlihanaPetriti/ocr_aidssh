"""Local full-text search index over OCR'd pages, using SQLite FTS5.

SQLite ships with Python and needs no separate service — a good fit for an
on-premise, single-machine deployment. If usage later needs typo-tolerant or
fuzzy search, swap this for Meilisearch/Typesense without touching the OCR
side.
"""
import sqlite3
from pathlib import Path


SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS pages USING fts5(
    source_file,
    page_num UNINDEXED,
    text,
    mean_confidence UNINDEXED
);
"""


def get_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def add_page(conn: sqlite3.Connection, source_file: str, page_num: int, text: str, mean_confidence: float) -> None:
    """Insert a page's OCR text, replacing any previous entry for the same
    (source_file, page_num) — so re-running OCR on a page (e.g. to compare
    settings, or after a partial --pages run) updates the index instead of
    piling up duplicate rows alongside the old ones."""
    conn.execute(
        "DELETE FROM pages WHERE source_file = ? AND page_num = ?",
        (source_file, page_num),
    )
    conn.execute(
        "INSERT INTO pages (source_file, page_num, text, mean_confidence) VALUES (?, ?, ?, ?)",
        (source_file, page_num, text, mean_confidence),
    )
    conn.commit()


def search(conn: sqlite3.Connection, query: str, limit: int = 20) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(
        """
        SELECT source_file, page_num, snippet(pages, 2, '[', ']', '...', 10) AS snippet, mean_confidence
        FROM pages
        WHERE pages MATCH ?
        ORDER BY rank
        LIMIT ?
        """,
        (query, limit),
    )
    return cursor.fetchall()
