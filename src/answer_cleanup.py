"""Stop Phi-3.5 from restating the same SOC answer in one message."""

from __future__ import annotations

import re

_HEADING = re.compile(
    r"(?im)^(?:#{1,3}\s+|\*\*)?(summary|severity(?:\s*/\s*mitre)?|immediate actions|"
    r"evidence|sources|containment|gaps?\s*/\s*questions)(?:\*\*)?\s*:"
)


def trim_repeated_content(text: str) -> str:
    matches = list(_HEADING.finditer(text))
    seen: dict[str, int] = {}
    for match in matches:
        key = re.sub(r"\s+", " ", match.group(1).lower())
        if key in seen:
            return text[: match.start()].rstrip()
        seen[key] = match.start()

    stripped = text.strip()
    if len(stripped) < 80:
        return text
    midpoint = len(stripped) // 2
    first = stripped[:midpoint].strip()
    second = stripped[midpoint:].strip()
    if len(first) >= 60 and first[:80] in second:
        return stripped[: midpoint + second.find(first[:80])].rstrip()
    return text
