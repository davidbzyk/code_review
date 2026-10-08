"""Hybrid retrieval over a store: LanceDB keyword plus vector search fused by reciprocal rank.

Chunks that overlap the change under review carry `touched` and are filtered out before any
ranking. Our own tie-break (path, then start line) is applied on top of the database's order.
"""

from __future__ import annotations

import posixpath
from collections.abc import Callable, Sequence
from typing import Any

from lancedb.rerankers import RRFReranker

from context_engine.store import Store
from context_engine.tokens import tokenize

Embedder = Callable[[Sequence[str]], list[list[float]]]
NOT_TOUCHED = "NOT touched"
# What an answer uses. Every eligible row is ranked, so carrying the stored vector (3072
# floats) and terms of each one made a single lookup about 0.4 GB (2026-10-07).
ANSWER_COLUMNS = ["path", "start", "end", "signature", "code"]


def _unit(vector: Sequence[float]) -> list[float]:
    """Scale a vector to unit length (a zero vector stays zero)."""
    norm = sum(x * x for x in vector) ** 0.5
    return [x / norm for x in vector] if norm else list(vector)


def _rows(
    store: Store, terms: Sequence[str], vector: Sequence[float] | None
) -> tuple[list[tuple[float, dict[str, Any]]], str]:
    """(score, row) for every eligible chunk the engine ranks, plus the mode used."""
    table = store.table
    total = table.count_rows()
    text = " ".join(terms)
    if not total or (vector is None and not text):
        return [], "bm25" if vector is None else "vector"
    rrf_k = store.manifest["settings"]["retrieval"]["rrf_k"]
    if vector is not None and text:
        query = (
            table.search(query_type="hybrid")
            .vector(list(vector))
            .text(text)
            .distance_type("cosine")
            .rerank(RRFReranker(K=rrf_k))
        )
        score_key, mode = "_relevance_score", "hybrid"
    elif vector is not None:
        query = table.search(list(vector)).distance_type("cosine")
        score_key, mode = "_distance", "vector"
    else:
        query = table.search(text, query_type="fts")
        score_key, mode = "_score", "bm25"
    rows = query.select(ANSWER_COLUMNS).where(NOT_TOUCHED, prefilter=True).limit(total).to_list()
    sign = -1.0 if score_key == "_distance" else 1.0
    return [(sign * float(r[score_key]), r) for r in rows], mode


def _hits(rows: list[tuple[float, dict[str, Any]]], k: int) -> list[dict[str, Any]]:
    """The top k rows as JSON-ready results, ordered by score, then path, then start line."""
    scored = sorted(
        ((round(s, 6), r) for s, r in rows), key=lambda x: (-x[0], x[1]["path"], x[1]["start"])
    )
    return [
        {
            "path": r["path"],
            "start": int(r["start"]),
            "end": int(r["end"]),
            "signature": r["signature"],
            "score": s,
            "code": r["code"],
        }
        for s, r in scored[:k]
    ]


def search(store: Store, text: str, k: int | None, embed: Embedder | None) -> dict[str, Any]:
    """Search the store for `text`. Falls back to keywords alone, loudly, if embedding fails."""
    k = k or store.manifest["settings"]["retrieval"]["default_k"]
    vector: list[float] | None = None
    reason: str | None = None
    if embed is None:
        reason = "no embedder was given"
    else:
        try:
            vector = _unit(embed([text])[0])
            if len(vector) != store.manifest["vector_size"]:
                reason = (
                    f"query vector size {len(vector)} does not match the store's "
                    f"{store.manifest['vector_size']}"
                )
                vector = None
        except Exception as exc:  # any failure degrades to keywords, and is reported
            reason = f"embedding failed: {exc}"
    rows, mode = _rows(store, tokenize(text), vector)
    return {
        "query": text,
        "mode": mode,
        "degraded": vector is None,
        "reason": reason,
        "results": _hits(rows, k),
    }


def _clean(path: str) -> str:
    """Normalise a repo-relative path the way the build records it."""
    normal = posixpath.normpath(path.strip())
    return normal.removeprefix("./")


def related(store: Store, path: str, k: int | None) -> dict[str, Any]:
    """Chunks related to the change in `path`, using the query stored at build time."""
    k = k or store.manifest["settings"]["retrieval"]["default_k"]
    path = _clean(path)
    entry = store.related.get(path)
    base = {"path": path, "mode": "hybrid", "degraded": False, "reason": None}
    if entry is None:
        if path in store.related_skipped:
            why = store.related_skipped[path]
        elif path in store.changed:
            why = "no related query was stored for this path"
        else:
            why = f"the change does not touch {path}"
        return {**base, "reason": why, "results": []}
    rows, mode = _rows(store, entry["terms"], entry["vector"])
    return {**base, "mode": mode, "results": _hits(rows, k)}
