#!/usr/bin/env python3
"""Export an OKF bundle as a node-link graph.

There is no graph format in the OKF specification -- the graph is emergent, not
serialized. Spec section 6.1: consumers that build a graph view "typically treat
all links as directed edges of an untyped relationship". So this is a derived
artifact and a local convention, not a conformance requirement. Nothing in a
bundle depends on it.

The output is node-link JSON (`nodes` + `links`) and the relation names match
the general-environments `ge-okf` tool, so graphs from either agree:

  references           a markdown link or a [[id]] in the body. The only
                       relation a generic OKF consumer sees.
  related_to           `related` / `relations.relates_to`
  depends_on           `depends_on` / `relations.depends_on`
  implements           `implements` / `relations.implements`
  supersedes           `supersedes`, or `relations.superseded_by` read in reverse
  part_of              `relations.part_of` (plugin-local, not in ge-okf)
  sources_from         each `sources` entry, a string or a `{resource: ...}` map
  implements_resource  the top-level `resource`
  covers               each `covers` glob (plugin-local, not in ge-okf's graph)

Targets that are not concepts become nodes of their own: `source_code` (under a
configured code root), `external_url`, or `unresolved_reference` (everything
else, listed in the stats so it is never silently dropped). Domains and code
roots come from the bundle's `okf.config.json`.

Read-only. It never writes into the bundle; --out takes an explicit path.
"""
from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from okf_common import (  # noqa: E402
    EXIT_FATAL,
    EXIT_OK,
    MD_LINK_RE,
    WIKI_LINK_RE,
    WILDCARD_RE,
    Doc,
    emit_json,
    entry_path,
    in_code_root,
    load_bundle,
    load_config,
    resolve_bundle,
    strip_code_and_verbatim,
    table,
)

#: Reserved files have no `type` of their own; label them by what they are.
RESERVED_TYPE = {"index.md": "Index", "log.md": "Log"}
RESERVED_FILE_TYPE = {"index.md": "okf_index", "log.md": "okf_log"}

#: Nested `relations.<key>` -> relation name. `superseded_by` is read in reverse.
NESTED_RELATIONS = {
    "depends_on": "depends_on",
    "relates_to": "related_to",
    "implements": "implements",
    "supersedes": "supersedes",
    "superseded_by": "supersedes",
    "part_of": "part_of",
}
#: Top-level frontmatter key -> relation name.
TOP_LEVEL_RELATIONS = {
    "related": "related_to",
    "depends_on": "depends_on",
    "implements": "implements",
    "supersedes": "supersedes",
}
WEIGHTS = {
    "depends_on": 1.0, "implements": 1.0, "supersedes": 1.0, "part_of": 1.0,
    "sources_from": 0.9, "implements_resource": 0.9, "covers": 0.9,
    "references": 0.6, "related_to": 0.5,
}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _is_external(target: str) -> bool:
    return bool(re.match(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//|#|mailto:)", target))


class Graph:
    def __init__(self, bundle: Path, repo_root: Path | None = None) -> None:
        self.bundle = bundle
        self.config = load_config(bundle, repo_root)
        self.repo_root = self.config.repo_root
        self.docs = load_bundle(bundle)
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []
        self._seen: set[tuple[str, str, str, str]] = set()
        self._concepts: set[str] = set()
        self._build()

    # -- construction -----------------------------------------------------

    def _build(self) -> None:
        for doc in self.docs:
            self.nodes[doc.concept_id] = {
                "id": doc.concept_id,
                "path": doc.rel,
                "source_file": doc.rel,
                "type": doc.type_of() or RESERVED_TYPE.get(doc.kind, "Untyped"),
                "title": str(doc.fm.data.get("title") or doc.path.stem) if doc.fm.ok else doc.path.stem,
                "domain": str(doc.fm.data.get("domain") or "") if doc.fm.ok else "",
                "status": str(doc.fm.data.get("status") or "stable") if doc.fm.ok else "stable",
                "reserved": not doc.is_concept,
                "file_type": "okf_concept" if doc.is_concept else RESERVED_FILE_TYPE[doc.kind],
            }
        self._concepts = set(self.nodes)
        for doc in self.docs:
            if doc.fm.ok:
                self._relation_edges(doc)
                self._evidence_edges(doc)
            self._link_edges(doc)
        self.edges.sort(key=lambda e: (e["source"], e["relation"], e["provenance"], e["target"]))

    def _add(self, src: str, dst: str, relation: str, provenance: str, raw: str | None = None) -> None:
        key = (src, dst, relation, provenance)
        if key in self._seen:
            return
        self._seen.add(key)
        edge: dict[str, Any] = {
            "source": src, "target": dst, "relation": relation,
            "confidence": "EXTRACTED", "provenance": provenance,
            "weight": WEIGHTS.get(relation, 0.5),
        }
        if raw is not None:
            edge["metadata"] = {"raw_target": raw}
        self.edges.append(edge)

    def _relation_edges(self, doc: Doc) -> None:
        data = doc.fm.data
        for key, relation in TOP_LEVEL_RELATIONS.items():
            for target in _as_list(data.get(key)):
                if isinstance(target, str) and target.strip():
                    self._add(doc.concept_id, self._relation_target(target), relation,
                              f"frontmatter:{key}", target)
        relations = data.get("relations")
        if not isinstance(relations, dict):
            return
        for key, relation in NESTED_RELATIONS.items():
            for target in _as_list(relations.get(key)):
                if target is None:
                    continue
                dst = self._relation_target(str(target))
                provenance = f"frontmatter:relations.{key}"
                if key == "superseded_by":
                    self._add(dst, doc.concept_id, relation, provenance, str(target))
                else:
                    self._add(doc.concept_id, dst, relation, provenance, str(target))

    def _evidence_edges(self, doc: Doc) -> None:
        data = doc.fm.data
        for entry in _as_list(data.get("sources")):
            self._evidence(doc, entry_path(entry), "sources_from", "frontmatter:sources")
        for entry in _as_list(data.get("resource")):
            self._evidence(doc, entry_path(entry), "implements_resource", "frontmatter:resource")
        for entry in _as_list(data.get("covers")):
            self._evidence(doc, entry_path(entry), "covers", "frontmatter:covers", concept_ok=False)

    def _evidence(self, doc: Doc, raw: str, relation: str, provenance: str, *, concept_ok: bool = True) -> None:
        """Point `doc` at a concept, an external URL, a code path, or an unresolved path."""
        if not raw:
            return
        if re.match(r"^https?://", raw):
            self._external_node(raw)
            self._add(doc.concept_id, raw, relation, provenance, raw)
            return
        if _is_external(raw):
            return
        concept = self._concept_id(raw) if concept_ok else None
        if concept:
            self._add(doc.concept_id, concept, relation, provenance, raw)
            return
        path = posixpath.normpath(raw.split("#", 1)[0].lstrip("/"))
        self._path_node(path)
        self._add(doc.concept_id, path, relation, provenance, raw)

    def _external_node(self, url: str) -> None:
        self.nodes.setdefault(url, {
            "id": url, "path": url, "source_file": url, "type": "ExternalResource",
            "title": url, "domain": "external", "status": "external", "reserved": False,
            "file_type": "external_url",
        })

    def _path_node(self, path: str) -> None:
        if path in self.nodes:
            return
        code = self._in_code_root(path)
        glob = bool(WILDCARD_RE.search(path))
        self.nodes[path] = {
            "id": path, "path": path, "source_file": path,
            "type": ("SourceGlob" if glob else "SourceCode") if code else "UnresolvedReference",
            "title": path, "domain": "codebase" if code else "", "status": "unverified",
            "reserved": False,
            "file_type": "source_code" if code else "unresolved_reference",
        }

    def _in_code_root(self, path: str) -> bool:
        """See `in_code_root`: under a configured root, a root-level file, or present on disk."""
        return in_code_root(path, self.config.code_roots, self.repo_root)

    def _link_edges(self, doc: Doc) -> None:
        body = strip_code_and_verbatim(doc.fm.body if doc.fm.present else doc.text)
        for target in MD_LINK_RE.findall(body):
            if _is_external(target):
                continue
            clean = target.split("#", 1)[0].strip()
            if not clean or not clean.endswith(".md"):
                continue
            base = self.bundle if clean.startswith("/") else doc.path.parent
            resolved = (base / clean.lstrip("/")).resolve()
            try:
                rel = resolved.relative_to(self.bundle).as_posix()
            except ValueError:
                continue  # points outside the bundle; not a graph edge
            self._add(doc.concept_id, rel[:-3], "references", "body:markdown_link", target)
        for target in WIKI_LINK_RE.findall(body):
            self._add(doc.concept_id, self._normalize(target.strip()), "references",
                      "body:wiki_link", target.strip())

    def _concept_id(self, target: str) -> str | None:
        """The concept a target names: bundle-relative, or repo-relative into the bundle."""
        text = target.strip().split("#", 1)[0].lstrip("/")
        if text.endswith(".md"):
            text = text[:-3]
        if text in self._concepts:
            return text
        if f"{text}/index" in self._concepts:
            return f"{text}/index"
        try:
            rel = (self.repo_root / text).resolve().relative_to(self.bundle).as_posix()
        except ValueError:
            return None
        for candidate in (rel, f"{rel}/index"):
            if candidate in self._concepts:
                return candidate
        return None

    def _relation_target(self, target: str) -> str:
        """A concept id, or a code node when the target is a path that exists or sits under a code root."""
        found = self._concept_id(target)
        if found:
            return found
        path = posixpath.normpath(target.strip().split("#", 1)[0].lstrip("/"))
        if self._in_code_root(path):
            self._path_node(path)
            return path
        return self._normalize(target)

    def _normalize(self, target: str) -> str:
        found = self._concept_id(target)
        if found:
            return found
        text = target.strip().lstrip("/")
        return text[:-3] if text.endswith(".md") else text

    # -- analysis ---------------------------------------------------------

    def dangling(self) -> list[dict[str, Any]]:
        return [e for e in self.edges if e["target"] not in self.nodes]

    def orphans(self) -> list[str]:
        """Concepts with no edge in or out. Reserved index/log files don't count."""
        touched = {e["source"] for e in self.edges} | {e["target"] for e in self.edges}
        return sorted(
            nid for nid, node in self.nodes.items()
            if node["file_type"] == "okf_concept" and nid not in touched
        )

    def stats(self) -> dict[str, Any]:
        by_relation: dict[str, int] = {}
        for edge in self.edges:
            by_relation[edge["relation"]] = by_relation.get(edge["relation"], 0) + 1
        by_type: dict[str, int] = {}
        by_file_type: dict[str, int] = {}
        for node in self.nodes.values():
            by_type[node["type"]] = by_type.get(node["type"], 0) + 1
            by_file_type[node["file_type"]] = by_file_type.get(node["file_type"], 0) + 1
        dangling = self.dangling()
        unresolved = sorted(n for n, node in self.nodes.items() if node["file_type"] == "unresolved_reference")
        return {
            "nodes": len(self.nodes),
            "concepts": by_file_type.get("okf_concept", 0),
            "edges": len(self.edges),
            "edges_by_relation": by_relation,
            "nodes_by_type": by_type,
            "nodes_by_file_type": by_file_type,
            "orphans": self.orphans(),
            "orphan_count": len(self.orphans()),
            "dangling_edges": dangling,
            "dangling_count": len(dangling),
            "unresolved": unresolved,
            "unresolved_count": len(unresolved),
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "bundle": str(self.bundle),
            "directed": True,
            "multigraph": True,
            "graph": {"name": self.bundle.name, "node_count": len(self.nodes), "edge_count": len(self.edges)},
            "nodes": [self.nodes[k] for k in sorted(self.nodes)],
            "links": self.edges,
            "stats": self.stats(),
        }

    # -- mermaid ----------------------------------------------------------

    def mermaid(self, max_nodes: int = 60) -> str:
        ids = sorted(nid for nid, n in self.nodes.items() if n["file_type"] == "okf_concept")
        truncated = len(ids) > max_nodes
        keep = set(ids[:max_nodes])
        alias = {nid: f"n{i}" for i, nid in enumerate(sorted(keep))}
        lines = ["graph LR"]
        for nid in sorted(keep):
            label = self.nodes[nid]["title"].replace('"', "'")
            lines.append(f'  {alias[nid]}["{label}"]')
        arrow = {"references": "-.->", "sources_from": "==>"}
        for edge in self.edges:
            if edge["source"] not in keep or edge["target"] not in keep:
                continue
            lines.append(
                f"  {alias[edge['source']]} {arrow.get(edge['relation'], '-->')}"
                f"|{edge['relation']}| {alias[edge['target']]}"
            )
        if truncated:
            lines.append(f"  %% truncated to {max_nodes} of {len(ids)} concepts (--max-nodes)")
        return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="okf_graphify",
        description="Export an OKF bundle's emergent graph as nodes and edges.",
    )
    ap.add_argument("bundle_dir")
    ap.add_argument("--out", help="write the graph JSON to this path (outside the bundle unless you say otherwise)")
    ap.add_argument("--mermaid", action="store_true", help="also emit a Mermaid diagram")
    ap.add_argument("--mermaid-out", help="write the Mermaid diagram to this path")
    ap.add_argument("--max-nodes", type=int, default=60, help="node cap for the Mermaid diagram (default: %(default)s)")
    ap.add_argument("--json", action="store_true", help="print the whole graph as JSON on stdout")
    ap.add_argument("--repo-root", help="root that repo-relative paths resolve against "
                                        "(default: repo_root in okf.config.json, else the bundle's parent)")
    args = ap.parse_args(argv)

    bundle = resolve_bundle(args.bundle_dir)
    graph = Graph(bundle, Path(args.repo_root).expanduser().resolve() if args.repo_root else None)
    payload = graph.as_dict()
    stats = payload["stats"]

    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    mermaid = graph.mermaid(args.max_nodes) if (args.mermaid or args.mermaid_out) else ""
    if args.mermaid_out:
        mpath = Path(args.mermaid_out).expanduser()
        mpath.parent.mkdir(parents=True, exist_ok=True)
        mpath.write_text(mermaid, encoding="utf-8")

    if args.json:
        emit_json(payload)
        return EXIT_OK

    print(f"OKF GRAPH  {bundle}")
    kinds = ", ".join(f"{n} {k}" for k, n in sorted(stats["nodes_by_file_type"].items()))
    print(f"  {stats['nodes']} node(s) ({kinds}), {stats['edges']} edge(s)")
    print()
    notes = {"references": "visible to any OKF consumer",
             "sources_from": "provenance (spec section 5.1)",
             "part_of": "plugin-local", "covers": "plugin-local"}
    print(table(
        [[rel, count, notes.get(rel, "frontmatter extension")]
         for rel, count in sorted(stats["edges_by_relation"].items())],
        ["RELATION", "COUNT", "NOTE"],
    ))
    print()
    print(table(
        [[t, c] for t, c in sorted(stats["nodes_by_type"].items())],
        ["NODE TYPE", "COUNT"],
    ))
    print()
    print(f"ORPHANS ({stats['orphan_count']})")
    for nid in stats["orphans"]:
        print(f"  {nid}")
    if not stats["orphans"]:
        print("  none")
    print()
    print(f"DANGLING EDGES ({stats['dangling_count']})")
    for edge in stats["dangling_edges"]:
        print(f"  {edge['source']} -{edge['relation']}-> {edge['target']}  (no such node)")
    if not stats["dangling_edges"]:
        print("  none")
    print()
    print(f"UNRESOLVED PATHS ({stats['unresolved_count']})")
    for path in stats["unresolved"]:
        print(f"  {path}  (outside every code root, or not found)")
    if not stats["unresolved"]:
        print("  none")
    if stats["dangling_edges"]:
        print()
        print("  Note: OKF tolerates broken links (spec section 6.1) -- a dangling edge may")
        print("  simply be not-yet-written knowledge, not a defect.")
    if args.out:
        print()
        print(f"wrote {args.out}")
    if args.mermaid_out:
        print(f"wrote {args.mermaid_out}")
    if args.mermaid and not args.mermaid_out:
        print()
        print(mermaid, end="")
    return EXIT_OK


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(EXIT_FATAL)
