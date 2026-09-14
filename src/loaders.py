"""Load markdown, text, PDF, and JSON knowledge sources for ingestion."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from src.chunker import parse_front_matter


@dataclass
class SourceDoc:
    doc_id: str
    title: str
    category: str
    body: str
    source_path: str


def load_markdown_or_text(path: Path) -> SourceDoc:
    raw = path.read_text(encoding="utf-8", errors="replace")
    meta, body = parse_front_matter(raw)
    doc_id = meta.get("id") or path.stem
    title = meta.get("title") or path.stem.replace("_", " ").replace("-", " ").title()
    category = meta.get("category") or "Uncategorised"
    return SourceDoc(doc_id=doc_id, title=title, category=category, body=body, source_path=str(path))


def load_pdf(path: Path) -> SourceDoc:
    reader = PdfReader(str(path))
    pages: list[str] = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages.append(f"[Page {i}]\n{text}")
    body = "\n\n".join(pages)
    if not body.strip():
        body = f"PDF extracted no selectable text: {path.name}"
    title = path.stem.replace("_", " ").replace("-", " ").title()
    category = "Playbook PDF"
    return SourceDoc(doc_id=path.stem, title=title, category=category, body=body, source_path=str(path))


def load_mitre_json(path: Path) -> list[SourceDoc]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    docs: list[SourceDoc] = []
    for item in payload:
        technique_id = item["id"]
        name = item["name"]
        tactic = item.get("tactic", "Unknown")
        body = (
            f"# {technique_id} — {name}\n\n"
            f"Tactic: {tactic}\n"
            f"Platforms: {', '.join(item.get('platforms', []))}\n"
            f"Detection: {item.get('detection', '')}\n\n"
            f"## Description\n{item.get('description', '')}\n\n"
            f"## SOC Response\n{item.get('soc_response', '')}\n\n"
            f"## Example Observables\n"
            + "\n".join(f"- {obs}" for obs in item.get("observables", []))
            + "\n\n## Containment Notes\n"
            + item.get("containment", "")
        )
        docs.append(
            SourceDoc(
                doc_id=technique_id.lower(),
                title=f"{technique_id} {name}",
                category=f"MITRE ATT&CK / {tactic}",
                body=body,
                source_path=str(path),
            )
        )
    return docs


def iter_docs(docs_dir: Path, mitre_path: Path | None = None) -> list[SourceDoc]:
    docs: list[SourceDoc] = []
    if docs_dir.exists():
        for path in sorted(docs_dir.iterdir()):
            if path.suffix.lower() in {".md", ".txt"}:
                docs.append(load_markdown_or_text(path))
            elif path.suffix.lower() == ".pdf":
                docs.append(load_pdf(path))
    if mitre_path and mitre_path.exists():
        docs.extend(load_mitre_json(mitre_path))
    return docs
