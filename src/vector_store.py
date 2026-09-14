"""SQLite-backed TF vector store with inverted index (ported from leestott/local-rag)."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from src.chunker import cosine_similarity, term_frequency


@dataclass
class SearchHit:
    id: int
    doc_id: str
    title: str
    category: str
    content: str
    score: float
    chunk_index: int = 0


class VectorStore:
    def __init__(self, db_path: str | Path) -> None:
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(db_path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode = WAL")
        self._init()
        self._row_cache: list[dict] | None = None
        self._inverted_index: dict[str, set[int]] | None = None

    def _init(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT NOT NULL,
                title TEXT,
                category TEXT,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                tf_json TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_doc_id ON chunks(doc_id);
            """
        )
        self.db.commit()

    def _invalidate_cache(self) -> None:
        self._row_cache = None
        self._inverted_index = None

    def _ensure_cache(self) -> None:
        if self._row_cache is not None:
            return
        rows = self.db.execute("SELECT * FROM chunks").fetchall()
        cache: list[dict] = []
        inverted: dict[str, set[int]] = {}
        for i, row in enumerate(rows):
            tf = {k: v for k, v in json.loads(row["tf_json"])}
            cache.append(
                {
                    "id": row["id"],
                    "doc_id": row["doc_id"],
                    "title": row["title"],
                    "category": row["category"],
                    "chunk_index": row["chunk_index"],
                    "content": row["content"],
                    "tf": tf,
                }
            )
            for term in tf:
                inverted.setdefault(term, set()).add(i)
        self._row_cache = cache
        self._inverted_index = inverted

    def clear(self) -> None:
        self.db.execute("DELETE FROM chunks")
        self.db.commit()
        self._invalidate_cache()

    def insert(
        self,
        doc_id: str,
        title: str,
        category: str,
        chunk_index: int,
        content: str,
    ) -> None:
        tf = term_frequency(content)
        tf_json = json.dumps(list(tf.items()))
        self.db.execute(
            """
            INSERT INTO chunks (doc_id, title, category, chunk_index, content, tf_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (doc_id, title, category, chunk_index, content, tf_json),
        )
        self.db.commit()
        self._invalidate_cache()

    def search(self, query: str, top_k: int = 5) -> list[SearchHit]:
        query_tf = term_frequency(query)
        self._ensure_cache()
        assert self._row_cache is not None
        assert self._inverted_index is not None

        candidate_indices: set[int] = set()
        for term in query_tf:
            candidate_indices.update(self._inverted_index.get(term, set()))

        scored: list[SearchHit] = []
        for idx in candidate_indices:
            row = self._row_cache[idx]
            score = cosine_similarity(query_tf, row["tf"])
            if score > 0:
                scored.append(
                    SearchHit(
                        id=row["id"],
                        doc_id=row["doc_id"],
                        title=row["title"],
                        category=row["category"],
                        content=row["content"],
                        score=score,
                        chunk_index=row["chunk_index"],
                    )
                )
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:top_k]

    def remove_by_doc_id(self, doc_id: str) -> None:
        self.db.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
        self.db.commit()
        self._invalidate_cache()

    def count(self) -> int:
        row = self.db.execute("SELECT COUNT(*) AS cnt FROM chunks").fetchone()
        return int(row["cnt"])

    def list_docs(self) -> list[dict]:
        rows = self.db.execute(
            """
            SELECT doc_id, title, category, COUNT(*) AS chunks
            FROM chunks
            GROUP BY doc_id
            ORDER BY title
            """
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self) -> None:
        self.db.close()
