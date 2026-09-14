"""Batch ingestion of playbooks, PDFs, and MITRE records into SQLite."""

from __future__ import annotations

from src.chunker import chunk_text
from src.config import config
from src.loaders import iter_docs
from src.vector_store import VectorStore


def ingest(clear: bool = True) -> dict:
    store = VectorStore(config.db_path)
    if clear:
        store.clear()

    sources = iter_docs(config.docs_dir, config.mitre_path)
    if not sources:
        raise FileNotFoundError(f"No documents found in {config.docs_dir}")

    total_chunks = 0
    details: list[dict] = []
    for source in sources:
        chunks = chunk_text(source.body, config.chunk_size, config.chunk_overlap)
        store.remove_by_doc_id(source.doc_id)
        for i, chunk in enumerate(chunks):
            store.insert(source.doc_id, source.title, source.category, i, chunk)
        total_chunks += len(chunks)
        details.append(
            {
                "doc_id": source.doc_id,
                "title": source.title,
                "category": source.category,
                "chunks": len(chunks),
            }
        )
        print(f"  ✓ {source.title} → {len(chunks)} chunk(s) [{source.category}]")

    summary = {
        "documents": len(sources),
        "chunks": total_chunks,
        "db_path": str(config.db_path),
        "details": details,
    }
    store.close()
    return summary


def main() -> None:
    print("=== SOC Incident Copilot — Document Ingestion ===\n")
    summary = ingest(clear=True)
    print(
        f"\nIngestion complete: {summary['chunks']} chunks from "
        f"{summary['documents']} documents."
    )
    print(f"Database: {summary['db_path']}")


if __name__ == "__main__":
    main()
