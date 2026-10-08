"""Identifier tokenizer shared by the index and the query side."""

from __future__ import annotations

import re

_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_PART = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|[0-9]+")


def tokenize(text: str) -> list[str]:
    """Lower-cased identifiers of `text` plus their snake_case and camelCase parts.

    `compute_total` gives `compute_total`, `compute`, `total`; repeats are kept (term counts).
    """
    out: list[str] = []
    for ident in _IDENT.findall(text):
        if len(ident) < 2:
            continue
        out.append(ident.lower())
        parts = [p for p in _PART.findall(ident) if len(p) > 1 and not p.isdigit()]
        if len(parts) > 1:
            out.extend(p.lower() for p in parts)
    return out
