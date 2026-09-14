"""Application configuration — paths relative to project root."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


class Config:
    model: str = os.getenv("FOUNDRY_MODEL", "phi-3.5-mini")
    app_name: str = os.getenv("FOUNDRY_APP_NAME", "soc-incident-copilot")
    docs_dir: Path = ROOT / "docs"
    data_dir: Path = ROOT / "data"
    db_path: Path = ROOT / "data" / "rag.db"
    mitre_path: Path = ROOT / "data" / "mitre_techniques.json"
    incidents_path: Path = ROOT / "data" / "sample_incidents.json"
    chunk_size: int = _int_env("CHUNK_SIZE", 200)
    chunk_overlap: int = _int_env("CHUNK_OVERLAP", 25)
    top_k: int = _int_env("TOP_K", 5)
    max_tokens: int = 640
    temperature: float = 0.2


config = Config()
