"""Query intent and token budget. Response language is always English."""

from __future__ import annotations

import re
from dataclasses import dataclass

_PUNCT = re.compile(r"[^\w\sçğıöşüÇĞİÖŞÜ'-]", re.UNICODE)

_GREETINGS = {
    "merhaba",
    "selam",
    "selamlar",
    "merhabalar",
    "gunaydin",
    "günaydın",
    "iyi",
    "akşamlar",
    "aksamlar",
    "hello",
    "hi",
    "hey",
    "yo",
    "thanks",
    "thank",
    "you",
    "teşekkür",
    "tesekkur",
    "tesekkurler",
    "teşekkürler",
    "sağol",
    "sagol",
    "naber",
    "nasılsın",
    "nasilsin",
}


@dataclass(frozen=True)
class QueryPolicy:
    smalltalk: bool
    skip_rag: bool
    max_tokens: int
    top_k: int


def _tokens(text: str) -> list[str]:
    cleaned = _PUNCT.sub(" ", text.lower())
    return [t for t in cleaned.split() if t]


def is_smalltalk(text: str) -> bool:
    tokens = _tokens(text)
    if not tokens:
        return True
    if len(tokens) > 5:
        return False
    return all(t in _GREETINGS for t in tokens)


def policy_for(question: str) -> QueryPolicy:
    if is_smalltalk(question):
        return QueryPolicy(smalltalk=True, skip_rag=True, max_tokens=96, top_k=0)
    short = len(_tokens(question)) <= 8
    return QueryPolicy(
        smalltalk=False,
        skip_rag=False,
        max_tokens=384 if short else 640,
        top_k=3 if short else 5,
    )
