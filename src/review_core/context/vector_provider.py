"""The vector provider: `ctx` search and related over a store built by `context_engine`."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from review_core.context.providers import (
    BuildSpec,
    ProviderError,
    StoreError,
    StoreLimits,
    make_result,
    quoted,
    walk_store,
)

PROVIDER = "vector"
MAX_VECTOR_SIZE = 8192
# A vector store is the engine's folder: LanceDB files plus a few JSON files. Real ones hold under
# a hundred entries and a few MB; these bounds sit far above and only stop a runaway listing.
LIMITS = StoreLimits(max_entries=5000, max_depth=8, max_file_bytes=1 << 30, max_total_bytes=4 << 30)


def checked_manifest(manifest: Mapping[str, Any], settings: Mapping[str, Any]) -> dict[str, Any]:
    """What the engine may use of a store's manifest: its model name and vector size, only.

    The model must be on the row's allow-list and the size a whole number from 1 to 8192. Every
    other value (timeouts, retries, batch sizes, retrieval depth) comes from the packaged engine
    settings, never from the store.
    """
    from context_engine.settings import load_settings

    model, size = manifest.get("model"), manifest.get("vector_size")
    if not isinstance(model, str) or model not in tuple(settings.get("models", ())):
        raise StoreError(f"the store names a model that is not allowed: {quoted(model)}")
    if not isinstance(size, int) or isinstance(size, bool) or not 1 <= size <= MAX_VECTOR_SIZE:
        raise StoreError("the store names a vector size that is not allowed")
    counts = manifest.get("counts")
    chunks = counts.get("chunks") if isinstance(counts, dict) else None
    packaged = load_settings()
    embedding = {**packaged["embedding"], "model": model, "vector_size": size}
    return {
        "model": model,
        "vector_size": size,
        "counts": {"chunks": chunks},
        "settings": {"embedding": embedding, "retrieval": packaged["retrieval"]},
    }


def make_embedder(manifest: Mapping[str, Any]):
    """The query embedder for a checked manifest: offline hashed for model "fake", else OpenAI."""
    from context_engine.embed import OpenAIEmbedder, hashed_bow_embedder

    if manifest["model"] == "fake":
        return hashed_bow_embedder(manifest["vector_size"])
    return OpenAIEmbedder.from_settings(manifest["settings"]["embedding"])


def _open_store(store_dir: Path, settings: Mapping[str, Any]):
    """Check the folder against the bounds, load it, and swap in the checked manifest."""
    from context_engine.store import load_store

    walk_store(Path(store_dir), LIMITS)
    store = load_store(store_dir)
    store.manifest = checked_manifest(store.manifest, settings)
    return store


def _items(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Engine hits as shared items: id and path:lines, the signature as title, code as text."""
    return [
        {
            "id": f"{h['path']}:{h['start']}-{h['end']}",
            "title": (h["signature"] or "").strip().splitlines()[0] if h["signature"] else "",
            "path": h["path"],
            "start": h["start"],
            "end": h["end"],
            "text": h["code"],
        }
        for h in hits
    ]


def _reason(engine_reason: str | None, degraded: bool, path: str | None = None) -> str | None:
    """One of a few fixed messages for the engine's reason; only a short quoted path varies."""
    if not engine_reason:
        return None
    if degraded:
        if engine_reason.startswith("embedding failed"):
            return "embedding failed"
        if engine_reason.startswith("query vector size"):
            return "the query vector size does not match the store"
        return "no embedder was available"
    if engine_reason.startswith("the change does not touch"):
        return f"the change does not touch {quoted(path)}"
    return "no related query was stored for this path"


def search(store_dir: Path, text: str, settings: Mapping[str, Any]) -> dict[str, Any]:
    """Hybrid search of the store; a keyword-only answer is marked degraded with its reason."""
    from context_engine.retrieve import search as engine_search

    store = _open_store(store_dir, settings)
    try:
        embed = make_embedder(store.manifest)
    except Exception:  # no embedder means keywords alone, and the reader is told
        embed = None
    out = engine_search(store, text, settings.get("k"), embed)
    reason = out["reason"] if embed is not None else "embedding failed"
    return make_result(_items(out["results"]), out["degraded"], _reason(reason, out["degraded"]))


def related(store_dir: Path, path: str, settings: Mapping[str, Any]) -> dict[str, Any]:
    """Chunks the engine stored as related to the change in `path`."""
    from context_engine.retrieve import related as engine_related

    store = _open_store(store_dir, settings)
    out = engine_related(store, path, settings.get("k"))
    return make_result(_items(out["results"]), out["degraded"], _reason(out["reason"], False, path))


def build(spec: BuildSpec) -> dict[str, Any]:
    """Build the engine's store from the base and head trees and stamp the provider on it."""
    from context_engine.embed import OpenAIEmbedder, hashed_bow_embedder
    from context_engine.index import build_index
    from context_engine.settings import load_settings

    for tree in (spec.base_tree, spec.head_tree):
        if not tree.is_dir():
            raise ProviderError(f"there is no source tree at {tree}")
    settings = load_settings()
    emb = settings["embedding"]
    if spec.fake_embedder:
        model, size = "fake", emb["fake_vector_size"]
        embed = hashed_bow_embedder(size)
    else:
        model, size = emb["model"], emb["vector_size"]
        embed = OpenAIEmbedder.from_settings(emb)
    stats = build_index(
        spec.base_tree, spec.head_tree, spec.out, spec.cache_dir, embed, model, size, settings
    )
    path = spec.out / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["provider"] = PROVIDER  # the engine's store hash is unchanged: it ignores the manifest
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return {"store_sha256": stats.store_sha256, "chunks": stats.chunks, "files": stats.files}
