"""Document chunking and TF-IDF helpers (ported from leestott/local-rag)."""

from __future__ import annotations

import math
import re
from typing import Iterable

FRONT_MATTER_RE = re.compile(r"^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$")
TOKEN_RE = re.compile(r"[^a-z0-9\-']+")


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text

    meta: dict[str, str] = {}
    for line in match.group(1).split("\n"):
        idx = line.find(":")
        if idx > 0:
            meta[line[:idx].strip()] = line[idx + 1 :].strip()
    return meta, match.group(2)


def chunk_text(text: str, max_tokens: int = 200, overlap_tokens: int = 25) -> list[str]:
    words = [w for w in text.split() if w]
    if len(words) <= max_tokens:
        return [text.strip()] if text.strip() else []

    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap_tokens
    return chunks


def term_frequency(text: str) -> dict[str, int]:
    tf: dict[str, int] = {}
    tokens = [t for t in TOKEN_RE.sub(" ", text.lower()).split() if len(t) > 1]
    for token in tokens:
        tf[token] = tf.get(token, 0) + 1
    return tf


def cosine_similarity(a: dict[str, int], b: dict[str, int]) -> float:
    dot = 0.0
    norm_a = 0.0
    for term, freq in a.items():
        norm_a += freq * freq
        if term in b:
            dot += freq * b[term]
    norm_b = sum(freq * freq for freq in b.values())
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


def tokenize(text: str) -> Iterable[str]:
    return (t for t in TOKEN_RE.sub(" ", text.lower()).split() if len(t) > 1)
