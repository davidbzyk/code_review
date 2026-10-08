"""The OKF provider: keyword search over a bundle's notes plus one hop of the tool's graph.

The store is data only: the bundle, the graph JSON the tool's graphify wrote at build time, and a
manifest. The tool's scripts are vendored in this package (`okf_tool/`); nothing is ever loaded
from a store, and a store holding any other kind of file is refused.
"""

from __future__ import annotations

import importlib
import json
import math
import os
import shutil
import sys
from collections import Counter
from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from context_engine.tokens import tokenize
from review_core.context.providers import (
    BuildSpec,
    ProviderError,
    StoreError,
    StoreLimits,
    make_result,
    quoted,
    read_bounded,
    walk_store,
)
from review_core.context.sync_okf_tool import VENDOR_DIR, read_record
from review_core.hashing import file_sha256, tree_sha256

PROVIDER = "okf"
BUNDLE, GRAPH, MANIFEST = "bundle", "graph.json", "manifest.json"
ALLOWED_SUFFIXES = {".md", ".json", ".yaml", ".yml"}
TOP_LEVEL = {BUNDLE, GRAPH, MANIFEST}
NO_LIMIT = 10**12  # the tool's own token budget is off; ctx applies the one shared cap
SKIP_DIRS = {"__pycache__"}
SKIP_FILES = {".DS_Store"}
MODULES = ("okf_common", "okf_graphify", "okf_retrieve")

# Bounds on a store, set a few times above the real bundles (65-69 files, notes up to 3.2 KB,
# 18 brackets a note, lines up to 476 characters, a graph of 0.2 MB). Each is checked from a
# listing, `stat` or a bounded read before the work it limits. The bracket and size bounds keep
# the vendored tool's quadratic link patterns (see the report) under 0.2 s.
LIMITS = StoreLimits(
    max_entries=600, max_depth=8, max_file_bytes=4_000_000, max_total_bytes=12_000_000
)
MAX_NOTES = 300  # markdown files in the bundle
# Sized for a repository's own notes as well as bundles written for one case: the platform
# repository's hold 86 notes, the largest 96,414 bytes, with lines up to 48,341 characters.
MAX_NOTE_BYTES = 131_072
MAX_JSON_BYTES = 32_768  # the manifest and any other json file of the bundle
MAX_GRAPH_BYTES = 4_000_000
MAX_NODES, MAX_LINKS = 2000, 10_000
MAX_LINE_CHARS = 65_536
MAX_BRACKETS_NOTE, MAX_BRACKETS_TOTAL = 400, 4000
MAX_RULES, MAX_PATTERN_CHARS = 2000, 256  # coverage claims of the notes, and one claim's length
MAX_PATH_CHARS = 128  # the path a caller asks `related` about
MAX_QUERY_TERMS = 64


@dataclass(frozen=True)
class Note:
    """One note as search sees it: identity, display fields, weighted terms and its text."""

    id: str
    title: str
    path: str
    text: str
    terms: Counter
    length: int
    deprecated: bool


def _read_json(path: Path, limit: int) -> Any:
    """Parse a JSON file of the store after a bounded, link-refusing read."""
    try:
        return json.loads(read_bounded(path, limit))
    except ValueError:
        raise StoreError(f"{quoted(path.name)} is not valid JSON") from None


def _load_tool() -> SimpleNamespace:
    """Import the vendored tool modules from this package, never from anywhere else."""
    vendor = VENDOR_DIR.resolve()
    for name in MODULES:
        loaded = sys.modules.get(name)
        if loaded is not None and Path(loaded.__file__).resolve().parent != vendor:
            del sys.modules[name]
    sys.path.insert(0, str(vendor))
    try:
        modules = {name: importlib.import_module(name) for name in MODULES}
    finally:
        sys.path[:] = [p for p in sys.path if p != str(vendor)]
    return SimpleNamespace(
        common=modules["okf_common"],
        graphify=modules["okf_graphify"],
        retrieve=modules["okf_retrieve"],
    )


def check_store_files(store: Path, *, final: bool = True) -> list[str]:
    """The relative paths of a store that holds only data within bounds, else a StoreError."""
    found = walk_store(store, LIMITS)
    notes = 0
    for rel, size in found:
        top, _, rest = rel.partition("/")
        suffix = Path(rel).suffix.lower()
        if top not in TOP_LEVEL or (top != BUNDLE and rest):
            raise StoreError(f"the store holds an unexpected entry: {quoted(top)}")
        if suffix not in ALLOWED_SUFFIXES:
            raise StoreError(f"the store holds a file a bundle does not need: {quoted(rel)}")
        limit = MAX_NOTE_BYTES if suffix == ".md" else MAX_JSON_BYTES
        if rel == GRAPH:
            limit = MAX_GRAPH_BYTES
        if size > limit:
            raise StoreError(f"the store file {quoted(rel)} is over {limit} bytes")
        notes += suffix == ".md"
    if notes > MAX_NOTES:
        raise StoreError(f"the bundle holds more than {MAX_NOTES} markdown files")
    names = {rel for rel, _ in found}
    if not any(r.startswith(f"{BUNDLE}/") for r in names) or (
        final and not {GRAPH, MANIFEST} <= names
    ):
        raise StoreError("the store has no bundle or no graph")
    return sorted(names)


def _load_docs(tool: SimpleNamespace, store: Path, names: list[str]) -> list[Any]:
    """The bundle's markdown as the tool's documents, read here under per-file and total bounds."""
    docs, brackets = [], 0
    for rel in names:
        inner = rel.removeprefix(f"{BUNDLE}/")
        parts = inner.split("/")
        if (
            not rel.startswith(f"{BUNDLE}/")
            or not rel.endswith(".md")
            or any(p.startswith(".") for p in parts)
            or inner.startswith("schemas/templates/")
        ):
            continue
        text = read_bounded(store / rel, MAX_NOTE_BYTES).decode("utf-8", errors="replace")
        if max(map(len, text.split("\n"))) > MAX_LINE_CHARS:
            raise StoreError(f"a line of {quoted(rel)} is over {MAX_LINE_CHARS} characters")
        here = text.count("[")
        brackets += here
        if here > MAX_BRACKETS_NOTE or brackets > MAX_BRACKETS_TOTAL:
            raise StoreError("the bundle holds more square brackets than a bundle needs")
        docs.append(tool.common.Doc(store / rel, inner, text, tool.common.split_frontmatter(text)))
    return docs


def _check_claims(tool: SimpleNamespace, docs: list[Any]) -> None:
    """Bound the coverage claims the tool will match a path against."""
    rules = tool.common.coverage_rules(docs)
    if len(rules) > MAX_RULES or any(len(r.pattern) > MAX_PATTERN_CHARS for r in rules):
        raise StoreError("the notes make more or longer coverage claims than a bundle needs")


@contextmanager
def _tool_reads(tool: SimpleNamespace, docs: list[Any]):
    """Make the tool's graph use the documents read above instead of reading the folder."""
    original = tool.graphify.load_bundle
    tool.graphify.load_bundle = lambda root, **kwargs: docs
    try:
        yield
    finally:
        tool.graphify.load_bundle = original


def _open(store: Path, *, final: bool = True) -> tuple[SimpleNamespace, Path, list[Any]]:
    """Check the store holds only bounded data; return the vendored tool, bundle and documents."""
    store = Path(store)
    names = check_store_files(store, final=final)
    tool = _load_tool()
    docs = _load_docs(tool, store, names)
    _check_claims(tool, docs)
    return tool, store / BUNDLE, docs


def _graph(tool: SimpleNamespace, bundle: Path, docs: list[Any]) -> Any:
    """The tool's graph of a bundle; repo-relative paths resolve at the store, not the config."""
    try:
        bundle = bundle.resolve()  # the tool compares resolved paths against this one
        with _tool_reads(tool, docs):
            return tool.graphify.Graph(bundle, bundle.parent)
    except SystemExit:
        raise ProviderError("the bundle's okf.config.json cannot be read") from None


def _read_graph(store: Path) -> dict[str, Any]:
    """graph.json as a dict with bounded nodes and links."""
    graph = _read_json(store / GRAPH, MAX_GRAPH_BYTES)
    nodes, links = (graph.get(k) if isinstance(graph, dict) else None for k in ("nodes", "links"))
    if not isinstance(nodes, list) or not isinstance(links, list):
        raise StoreError("graph.json has no nodes and links")
    if len(nodes) > MAX_NODES or len(links) > MAX_LINKS:
        raise StoreError("graph.json holds more nodes or links than a bundle needs")
    return graph


def _weights(settings: Mapping[str, Any]) -> tuple[int, int]:
    """(title weight, meta weight) from the row, as whole numbers of at least one."""
    return max(1, int(settings.get("title_weight", 3))), max(1, int(settings.get("meta_weight", 2)))


def _notes(
    tool: SimpleNamespace, docs: list[Any], graph: Mapping[str, Any], settings
) -> list[Note]:
    """The bundle's notes: concept documents the graph lists, never index or template files."""
    concepts = {
        n["id"]
        for n in graph["nodes"]
        if isinstance(n.get("id"), str) and n.get("file_type") == "okf_concept"
    }
    tw, mw = _weights(settings)
    notes = []
    for doc in docs:
        if not doc.is_concept or doc.concept_id not in concepts:
            continue
        data = doc.fm.data if doc.fm.ok else {}
        body = (doc.fm.body if doc.fm.present else doc.text).strip()
        tags = data.get("tags") if isinstance(data.get("tags"), list) else []
        title = str(data.get("title") or doc.path.stem)
        meta = " ".join([str(data.get("description") or ""), *map(str, tags)])
        terms: Counter = Counter(tokenize(body))
        for token in tokenize(title):
            terms[token] += tw
        for token in tokenize(meta):
            terms[token] += mw
        notes.append(
            Note(
                id=doc.concept_id,
                title=title,
                path=doc.rel,
                text=f"# {doc.concept_id}\n\n{body}\n",
                terms=terms,
                length=sum(terms.values()),
                deprecated=str(data.get("status") or "").lower() == "deprecated",
            )
        )
    return notes


def _bm25(notes: list[Note], query: list[str], k1: float, b: float) -> list[tuple[float, str]]:
    """Notes with a positive BM25 score for the query terms, best first, ties by id."""
    n = len(notes)
    avg = (sum(note.length for note in notes) / n) or 1.0
    df = {t: sum(1 for note in notes if t in note.terms) for t in query}
    scored = []
    for note in notes:
        score = 0.0
        for term in query:
            tf = note.terms.get(term, 0)
            if not tf:
                continue
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
            score += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * note.length / avg))
        if score > 0:
            scored.append((round(score, 9), note.id))
    return sorted(scored, key=lambda s: (-s[0], s[1]))


def _neighbours(direct: list[str], graph: Mapping[str, Any], allowed: set[str]) -> list[str]:
    """Notes one edge from a direct hit, either direction, most direct hits touched first."""
    hits = set(direct)
    touched: dict[str, set[str]] = {}
    for link in graph["links"]:
        a, b = link.get("source"), link.get("target")
        if not isinstance(a, str) or not isinstance(b, str):
            continue
        for here, there in ((a, b), (b, a)):
            if here in hits and there not in hits and there in allowed:
                touched.setdefault(there, set()).add(here)
    return sorted(touched, key=lambda note_id: (-len(touched[note_id]), note_id))


def _item(note: Note) -> dict[str, Any]:
    """A note as a shared item: lines are 0 because a note has none."""
    return {
        "id": note.id,
        "title": note.title,
        "path": note.path,
        "start": 0,
        "end": 0,
        "text": note.text,
    }


def search(store_dir: Path, text: str, settings: Mapping[str, Any]) -> dict[str, Any]:
    """Keyword-rank the notes, then add the notes one graph edge from the top few."""
    tool, _, docs = _open(store_dir)
    query = sorted(set(tokenize(text)))[:MAX_QUERY_TERMS]
    if not query:
        return make_result([], reason="the query has no searchable words")
    graph = _read_graph(Path(store_dir))
    notes = _notes(tool, docs, graph, settings)
    by_id = {n.id: n for n in notes}
    live = [n for n in notes if not n.deprecated]
    ranked = _bm25(
        live, query, float(settings.get("bm25_k1", 1.2)), float(settings.get("bm25_b", 0.75))
    )
    direct = [note_id for _, note_id in ranked[: int(settings.get("direct_hits", 3))]]
    if not direct:
        return make_result([], reason="no note matches the query")
    near = _neighbours(direct, graph, {n.id for n in live})
    return make_result([_item(by_id[i]) for i in [*direct, *near]])


def related(store_dir: Path, path: str, settings: Mapping[str, Any]) -> dict[str, Any]:
    """The notes that cover `path` and their one-hop neighbours, via the tool's own retrieve."""
    tool, bundle, docs = _open(store_dir)
    if len(path) > MAX_PATH_CHARS:
        return make_result([], reason=f"the path is longer than {MAX_PATH_CHARS} characters")
    clean = tool.common.clean_path(path)
    graph = _graph(tool, bundle, docs)
    result = tool.retrieve.retrieve(graph, [clean], NO_LIMIT)
    if result["empty"]:
        return make_result([], reason=f"no note covers {quoted(clean)}")
    docs = {d.concept_id: d for d in graph.docs}
    items = [
        {
            "id": e["id"],
            "title": graph.nodes[e["id"]]["title"],
            "path": docs[e["id"]].rel,
            "start": 0,
            "end": 0,
            "text": e["body"],
        }
        for e in result["notes"]
    ]
    return make_result(items)


def _copy_tree(src: Path, dst: Path, skipped: list[str]) -> None:
    """Copy the regular files of `src` to `dst`; links, dot-folders and caches are left out."""
    for root, dirs, files in os.walk(src, followlinks=False):
        here = Path(root)
        keep = []
        for name in sorted(dirs):
            if (here / name).is_symlink():
                skipped.append((here / name).relative_to(src).as_posix())
            elif not name.startswith(".") and name not in SKIP_DIRS:
                keep.append(name)
        dirs[:] = keep
        for name in sorted(files):
            source = here / name
            if source.is_symlink():
                skipped.append(source.relative_to(src).as_posix())
            elif name not in SKIP_FILES:
                target = dst / source.relative_to(src)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)


def _clear_previous(out: Path) -> None:
    """Remove an earlier store at `out`; anything else already there is an error."""
    if not out.exists():
        return
    manifest = out / MANIFEST
    if out.is_dir() and not any(out.iterdir()):
        return
    try:
        old = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {}
    except ValueError:
        old = {}
    if isinstance(old, dict) and old.get("provider") == PROVIDER:
        shutil.rmtree(out)
        return
    raise ProviderError(f"{out} exists and is not an okf store")


def build(spec: BuildSpec) -> dict[str, Any]:
    """Copy the bundle, run the vendored graphify on the copy, and write the manifest."""
    if spec.okf_bundle is None:
        raise ProviderError("the okf arm needs --okf-bundle")
    bundle = spec.okf_bundle
    if bundle.is_symlink() or not bundle.is_dir():
        raise ProviderError(f"{bundle} is not a plain folder")
    out = spec.out
    skipped: list[str] = []
    total = 0
    staged: list[Path] = []  # nothing is written until the whole bundle is known to be data
    for root, dirs, files in os.walk(bundle, followlinks=False):
        dirs[:] = [
            d
            for d in dirs
            if not (Path(root, d).is_symlink() or d.startswith(".")) and d not in SKIP_DIRS
        ]
        for name in files:
            path = Path(root, name)
            if path.is_symlink():
                skipped.append(path.relative_to(bundle).as_posix())
            elif name not in SKIP_FILES:
                if path.suffix.lower() not in ALLOWED_SUFFIXES:
                    raise ProviderError(f"the bundle holds a file that is not data: {name!r}")
                size = path.stat().st_size
                total += size
                limit = MAX_NOTE_BYTES if path.suffix.lower() == ".md" else MAX_JSON_BYTES
                if (
                    len(staged) >= LIMITS.max_entries
                    or size > limit
                    or total > LIMITS.max_total_bytes
                ):
                    raise ProviderError(f"the bundle is over a size bound at {name!r}")
                staged.append(path)
    _clear_previous(out)
    for path in staged:
        target = out / BUNDLE / path.relative_to(bundle)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    try:
        tool, bundle_dir, docs = _open(out, final=False)  # the bounds a query will apply
        graph = _graph(tool, bundle_dir, docs)
    except Exception:
        shutil.rmtree(out, ignore_errors=True)
        raise
    payload = graph.as_dict()
    if len(payload["nodes"]) > MAX_NODES or len(payload["links"]) > MAX_LINKS:
        shutil.rmtree(out, ignore_errors=True)
        raise ProviderError("the bundle's graph is bigger than a store may hold")
    payload["bundle"] = BUNDLE  # not the absolute path, so the same inputs hash the same
    (out / GRAPH).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digest = sha256(
        f"bundle:{tree_sha256(out / BUNDLE)}\ngraph:{file_sha256(out / GRAPH)}\n".encode()
    ).hexdigest()
    manifest = {
        "schema_version": 1,
        "provider": PROVIDER,
        "store_sha256": digest,
        "tool_sha256": read_record()["tool_sha256"],
        "notes": payload["stats"]["concepts"],
        "nodes": payload["stats"]["nodes"],
        "edges": payload["stats"]["edges"],
    }
    (out / MANIFEST).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    check_store_files(out)
    return {"store_sha256": digest, "notes": manifest["notes"], "skipped_symlinks": skipped}
