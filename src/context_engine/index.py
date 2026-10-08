"""Build a store from the indexed tree (base) and the changed tree (head) (build side)."""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import sys
from array import array
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pyarrow as pa
from lancedb.index import FTS

from context_engine.change import LINE_NOTE, NO_RELATED_NOTE, SIZE_NOTE, Touched, compute_change
from context_engine.chunk import Chunk, chunk_file, language_of, split_lines
from context_engine.report import Report
from context_engine.store import (
    CHANGED,
    CHUNKS,
    DATA_FILES,
    DB_DIR,
    MANIFEST,
    RELATED,
    SCHEMA_VERSION,
    SETTINGS,
    TABLE,
    VECTORS,
    connect,
)
from context_engine.tokens import tokenize
from review_core.hashing import tree_sha256

Embedder = Callable[[Sequence[str]], "list[list[float]]"]


def pack_vectors(rows: list[list[float]]) -> bytes:
    """Little-endian float32 bytes, one row per vector."""
    flat = array("f")
    for row in rows:
        flat.extend(row)
    if sys.byteorder == "big":
        flat.byteswap()
    return flat.tobytes()


@dataclass
class BuildStats:
    """What a build did, for the console and the tests."""

    files: int
    chunks: int
    embedded_texts: int
    cache_hits: int
    estimated_tokens: int
    store_sha256: str
    report: dict[str, Any]


class VectorCache:
    """Vectors on disk keyed by sha256(model + newline + text); raw little-endian float32."""

    def __init__(self, folder: Path, model: str, size: int) -> None:
        self.folder = folder
        self.model = model
        self.size = size

    def _path(self, text: str) -> Path:
        """Where the vector of `text` lives."""
        key = hashlib.sha256(f"{self.model}\n{text}".encode()).hexdigest()
        return self.folder / key[:2] / f"{key}.f32"

    def get(self, text: str) -> list[float] | None:
        """The cached vector, or None when absent or of the wrong size."""
        path = self._path(text)
        try:
            if path.stat().st_size != self.size * 4:
                return None
            data = path.read_bytes()
        except FileNotFoundError:
            return None
        vector = array("f")
        vector.frombytes(data)
        return vector.tolist()

    def has(self, text: str) -> bool:
        """True when a vector of the right size is cached for `text` (one stat, no read)."""
        try:
            return self._path(text).stat().st_size == self.size * 4
        except FileNotFoundError:
            return False

    def put(self, text: str, vector: list[float]) -> None:
        """Write a vector atomically."""
        path = self._path(text)
        path.parent.mkdir(parents=True, exist_ok=True)
        part = path.with_suffix(f".{os.getpid()}.part")
        part.write_bytes(pack_vectors([vector]))
        os.replace(part, path)


def _count_lines(path: Path, size: int, budget: int) -> int:
    """Non-blank lines of a big file, from at most `budget` bytes, scaled up to its size."""
    with path.open("rb") as handle:
        raw = handle.read(budget)
    count = sum(1 for line in raw.split(b"\n") if line.strip())
    return count if size <= len(raw) else int(count * size / max(len(raw), 1))


def _bounded_text(path: Path, limit: int) -> str:
    """The first `limit` bytes of a file as text (a cut multi-byte character is replaced)."""
    with path.open("rb") as handle:
        return handle.read(limit).decode("utf-8", "replace")


class EmbedBudgetError(ValueError):
    """The most a build could send to the embedder is over `embedding.max_build_tokens`."""


class TreeTooLarge(ValueError):
    """A tree holds more files than the engine will walk."""


def _walk(root: Path, settings: dict[str, Any], report: Report | None):
    """Yield (path, relative path, language) of files that policy lets through.

    Every entry, file or directory, is counted as it is listed. Past `chunk.max_files` the walk
    raises TreeTooLarge before sorting or opening anything; directories nested deeper than
    `chunk.max_depth` raise too, and so does a tree whose files add up to more than
    `chunk.max_tree_bytes`, summed from directory listings alone. Within a directory the files
    come first, then the subdirectories, each sorted by name.
    """
    cfg = settings["chunk"]
    seen = 0
    size = 0

    def visit(folder: Path, depth: int):
        nonlocal seen, size
        if depth > cfg["max_depth"]:
            raise TreeTooLarge(f"{root} has directories nested deeper than {cfg['max_depth']}")
        names: list[str] = []
        dirs: list[str] = []
        with os.scandir(folder) as entries:
            for entry in entries:
                seen += 1
                if seen > cfg["max_files"]:
                    raise TreeTooLarge(f"{root} holds more than {cfg['max_files']} entries")
                if entry.is_dir():
                    dirs.append(entry.name)
                    continue
                names.append(entry.name)
                if not entry.is_symlink():
                    size += entry.stat(follow_symlinks=False).st_size
                    if size > cfg["max_tree_bytes"]:
                        raise TreeTooLarge(
                            f"{root} holds more than {cfg['max_tree_bytes']} bytes of files"
                        )
        for name in sorted(names):
            path = folder / name
            rel = path.relative_to(root).as_posix()
            language = language_of(rel, settings)
            if path.is_symlink() or not path.is_file():
                if report:
                    report.add_excluded(language, rel, "symlink")
            elif name in cfg["skip_files"]:
                if report:
                    report.add_excluded(language, rel, "lockfile")
            else:
                yield path, rel, language
        for name in sorted(dirs):
            path = folder / name
            if name in cfg["skip_dirs"] or path.is_symlink():
                if report:
                    report.add_excluded("", path.relative_to(root).as_posix() + "/", "skip-dir")
            else:
                yield from visit(path, depth + 1)

    yield from visit(root, 0)


def _inspect(path: Path, cfg: dict[str, Any]) -> tuple[str, Any]:
    """Classify a file without reading more than the size limit.

    Returns ("text", text), ("binary" | "empty", None), or ("too-large" | "line-too-long",
    estimated non-blank lines).
    """
    size = path.stat().st_size
    if size == 0:
        return "empty", None
    if size > cfg["file_size_limit_bytes"]:
        with path.open("rb") as handle:
            if b"\0" in handle.read(8000):
                return "binary", None
        return "too-large", _count_lines(path, size, cfg["oversize_count_bytes"])
    raw = path.read_bytes()
    try:
        if b"\0" in raw[:8000]:
            raise UnicodeDecodeError("utf-8", b"", 0, 1, "nul byte")
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return "binary", None
    if not text.strip():
        return "empty", None
    if max(map(len, text.split("\n"))) > cfg["line_char_limit"]:
        return "line-too-long", sum(1 for line in text.split("\n") if line.strip())
    return "text", text


def scan_tree(root: Path, settings: dict[str, Any], report: Report) -> dict[str, str]:
    """Read the text files of the indexed tree; everything else is listed in `report`."""
    texts: dict[str, str] = {}
    for path, rel, language in _walk(root, settings, report):
        kind, payload = _inspect(path, settings["chunk"])
        if kind == "text":
            texts[rel] = payload
        elif kind in ("binary", "empty"):
            report.add_excluded(language, rel, kind)
        else:
            report.add_skipped(language, rel, payload, kind)
    return texts


def scan_changed(
    root: Path, settings: dict[str, Any]
) -> tuple[dict[str, str], dict[str, tuple[str, str]]]:
    """Read the changed tree: text files, plus the first bytes of any file too big to read.

    The second result maps a path to (change note, bounded text).
    """
    texts: dict[str, str] = {}
    big: dict[str, tuple[str, str]] = {}
    cfg = settings["chunk"]
    for path, rel, _language in _walk(root, settings, None):
        kind, payload = _inspect(path, cfg)
        if kind == "text":
            texts[rel] = payload
        elif kind in ("too-large", "line-too-long"):
            note = SIZE_NOTE if kind == "too-large" else LINE_NOTE
            big[rel] = (note, _bounded_text(path, settings["change"]["query_max_chars"]))
    return texts, big


def _embed_texts(
    texts: list[str], embed: Embedder, cache: VectorCache, group: int, counts: Counter
) -> dict[str, list[float]]:
    """Vectors for every text, embedding only cache misses, in groups, writing as it goes."""
    vectors: dict[str, list[float]] = {}
    missing: list[str] = []
    for text in dict.fromkeys(texts):
        cached = cache.get(text)
        if cached is None:
            missing.append(text)
        else:
            vectors[text] = cached
            counts["cache_hits"] += 1
    for i in range(0, len(missing), group):
        batch = missing[i : i + group]
        counts["embedded_texts"] += len(batch)
        for text, vector in zip(batch, embed(batch), strict=True):
            if len(vector) != cache.size:
                raise ValueError(f"embedder returned {len(vector)} numbers, not {cache.size}")
            rounded = array("f", vector).tolist()
            cache.put(text, rounded)
            vectors[text] = rounded
    return vectors


def _unit(vector: list[float]) -> list[float]:
    """Scale to unit length and round to float32 (a zero vector stays zero)."""
    norm = math.sqrt(sum(x * x for x in vector))
    scaled = [x / norm for x in vector] if norm else vector
    return array("f", scaled).tolist()


def _query_for(text: str, cfg: dict[str, Any]) -> tuple[str, list[str]]:
    """Text to embed and BM25 terms for one changed file's hunks."""
    counts = Counter(t for t in tokenize(text) if not t.isdigit())
    ranked = sorted(counts, key=lambda t: (-counts[t], t))[: cfg["query_max_terms"]]
    return (text + "\n" + " ".join(ranked))[: cfg["query_max_chars"]], sorted(ranked)


def _write(path: Path, text: str) -> None:
    """Write UTF-8 text with unix newlines."""
    path.write_bytes(text.encode("utf-8"))


def build_index(
    base: Path,
    head: Path,
    out: Path,
    cache_dir: Path,
    embed: Embedder,
    model: str,
    vector_size: int,
    settings: dict[str, Any],
) -> BuildStats:
    """Index `base`, record how `head` differs from it, and write the store to `out`.

    Raises CoverageError before embedding anything when a language is below the floor.
    """
    settings = json.loads(json.dumps(settings))
    settings["embedding"].update(model=model, vector_size=vector_size)
    emb = settings["embedding"]
    report = Report()
    base_texts = scan_tree(base, settings, report)
    chunks: list[Chunk] = []
    for rel, text in base_texts.items():
        result = chunk_file(rel, text, settings)
        if result.parse_failed:
            report.add_parse_failure(result.language, rel)
        report.add_chunked(result.language, rel, result.lines_seen, result.lines_covered)
        chunks.extend(result.chunks)
    chunks.sort(key=lambda c: (c.path, c.start))
    report.check_coverage(
        settings["report"]["coverage_floor"], settings["report"]["coverage_min_lines"]
    )

    head_texts, head_big = scan_changed(head, settings)
    changed, hunks, notes = compute_change(base_texts, head_texts, head_big, settings)
    report.add_change_notes(notes)
    ordered = sorted(hunks)
    cap_files = settings["change"]["max_related_files"]
    queries = {p: _query_for(hunks[p], settings["change"]) for p in ordered[:cap_files]}
    left_out = {p: NO_RELATED_NOTE for p in ordered[cap_files:]}
    report.add_change_notes([{"path": p, "reason": r} for p, r in left_out.items()])

    chunk_texts = [c.embed_text() for c in chunks]
    query_texts = [q[0] for q in queries.values()]
    counts: Counter = Counter()
    cache = VectorCache(cache_dir, model, vector_size)
    cap, per_char = emb["input_token_cap"], emb["chars_per_token"]

    def tokens_of(text: str) -> int:
        """Estimated tokens one text sends: characters over chars_per_token, capped per input."""
        return min(-(-len(text) // per_char), cap)

    def most_tokens(text: str) -> int:
        """A hard ceiling on the tokens one text sends: its UTF-8 bytes after the client's cut.

        No text has more tokens than bytes. The estimate above can be several times too low
        for dense text, so the limit on spending is checked against this ceiling.
        """
        return len(text[: cap * per_char].encode("utf-8", errors="replace"))

    estimated = sum(tokens_of(t) for t in chunk_texts + query_texts)
    uncached = sum(most_tokens(t) for t in set(chunk_texts + query_texts) if not cache.has(t))
    if uncached > emb["max_build_tokens"]:
        raise EmbedBudgetError(
            f"build would send at most {uncached} tokens to the embedder, over the limit of "
            f"{emb['max_build_tokens']}; nothing was embedded"
        )
    vectors = _embed_texts(
        chunk_texts + query_texts, embed, cache, emb["request_max_inputs"], counts
    )

    _prepare(out)
    _write(out / CHUNKS, "".join(_row(c) + "\n" for c in chunks))
    (out / VECTORS).write_bytes(pack_vectors([_unit(vectors[t]) for t in chunk_texts]))
    related = {
        path: {"terms": terms, "vector": _unit(vectors[text])}
        for path, (text, terms) in queries.items()
    }
    _write(out / RELATED, _dump({"queries": related, "skipped": left_out}, indent=None))
    _write(out / CHANGED, _dump({"files": changed}, indent=1))
    _write(out / SETTINGS, _dump(settings, indent=1))
    # The store hash covers the logical files only; the database folder is derived from them.
    store_hash = tree_sha256(out)
    unit_vectors = [_unit(vectors[t]) for t in chunk_texts]
    _write_db(out / DB_DIR, chunks, unit_vectors, changed, settings)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "model": model,
        "vector_size": vector_size,
        "settings": settings,
        "counts": {
            "files": len(base_texts),
            "chunks": len(chunks),
            "changed_files": len(changed),
            "related_queries": len(related),
            "estimated_embed_tokens": estimated,
        },
        "report": report.to_dict(),
        "base_tree_sha256": tree_sha256(base),
        "head_tree_sha256": tree_sha256(head),
        "store_sha256": store_hash,
    }
    _write(out / MANIFEST, _dump(manifest, indent=2))
    return BuildStats(
        files=len(base_texts),
        chunks=len(chunks),
        embedded_texts=counts["embedded_texts"],
        cache_hits=counts["cache_hits"],
        estimated_tokens=estimated,
        store_sha256=store_hash,
        report=report.to_dict(),
    )


def keyword_text(chunk: Chunk, weight: int) -> str:
    """Tokens of a chunk for keyword search; signature tokens are repeated `weight` times."""
    tokens = tokenize(chunk.path) + tokenize(chunk.code) + tokenize(chunk.signature) * weight
    return " ".join(tokens)


def _write_db(
    folder: Path,
    chunks: list[Chunk],
    vectors: list[list[float]],
    changed: dict[str, Any],
    settings: dict[str, Any],
) -> None:
    """Write the chunk table: our vectors, a keyword index, and a `touched` filter column."""
    size = settings["embedding"]["vector_size"]
    weight = settings["retrieval"]["signature_weight"]
    touched = Touched(changed)
    flat = pa.array([x for v in vectors for x in v], pa.float32())
    table = pa.table(
        {
            "id": pa.array(range(len(chunks)), pa.int32()),
            "path": pa.array([c.path for c in chunks], pa.string()),
            "start": pa.array([c.start for c in chunks], pa.int32()),
            "end": pa.array([c.end for c in chunks], pa.int32()),
            "language": pa.array([c.language for c in chunks], pa.string()),
            "signature": pa.array([c.signature for c in chunks], pa.string()),
            "code": pa.array([c.code for c in chunks], pa.string()),
            "terms": pa.array([keyword_text(c, weight) for c in chunks], pa.string()),
            "touched": pa.array(
                [touched.overlaps(c.path, c.start, c.end) for c in chunks], pa.bool_()
            ),
            "vector": pa.FixedSizeListArray.from_arrays(flat, size),
        }
    )
    handle = connect(folder).create_table(TABLE, data=table, mode="overwrite")
    if chunks:
        handle.create_index("terms", config=FTS())


def _row(chunk: Chunk) -> str:
    """One chunks.jsonl line (no newline)."""
    return json.dumps(
        {
            "path": chunk.path,
            "start": chunk.start,
            "end": chunk.end,
            "language": chunk.language,
            "signature": chunk.signature,
            "code": chunk.code,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def _dump(data: Any, indent: int | None) -> str:
    """Deterministic JSON text with a trailing newline."""
    separators = (",", ":") if indent is None else None
    return (
        json.dumps(data, ensure_ascii=False, sort_keys=True, indent=indent, separators=separators)
        + "\n"
    )


def _prepare(out: Path) -> None:
    """Make `out` an empty store folder, clearing a previous store but nothing else."""
    out.mkdir(parents=True, exist_ok=True)
    known = set(DATA_FILES) | {MANIFEST, DB_DIR}
    stray = [p.name for p in out.iterdir() if p.name not in known]
    if stray:
        raise ValueError(f"{out} holds files that are not a store: {sorted(stray)}")
    for name in known - {DB_DIR}:
        (out / name).unlink(missing_ok=True)
    shutil.rmtree(out / DB_DIR, ignore_errors=True)


__all__ = ["BuildStats", "VectorCache", "build_index", "scan_tree", "split_lines"]
