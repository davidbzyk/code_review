#!/usr/bin/env python3
"""Pick the notes a reviewer needs for a set of changed paths, packed to a token budget.

Walk the changed paths to the notes that cover them (a `resource`, a `sources`
entry, or a `covers` glob), follow ONE hop of `depends_on`, `implements`,
`supersedes` and `related` from those notes, and pack note bodies in that order
until the budget is spent. Covering notes always come before neighbors, and among
them a note that is specifically about the changed paths (it claims few paths in
all) comes before one that merely lists them among many, and a note that names a
path before one that matches it only by a glob. A note
with `status: deprecated` is never returned.

Tokens are estimated as characters / 4; there is no tokenizer in the standard
library, so the number is a budget guide, not a billing figure.

Read-only.
"""
from __future__ import annotations

import argparse
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from okf_common import (  # noqa: E402
    EXIT_FATAL,
    EXIT_OK,
    clean_path,
    coverage_rules,
    covering_notes,
    emit_json,
    in_code_root,
    resolve_bundle,
)
from okf_graphify import Graph  # noqa: E402

FOLLOWED = ("depends_on", "implements", "supersedes", "related_to")
ESTIMATOR = "chars/4"


def estimate_tokens(text: str) -> int:
    """Token estimate for a budget: characters / 4, rounded up."""
    return math.ceil(len(text) / 4)


def retrieve(graph: Graph, paths: list[str], budget: int) -> dict[str, Any]:
    """Select, order and pack the notes for `paths` within `budget` tokens."""
    docs = {d.concept_id: d for d in graph.docs if d.is_concept}
    rules = coverage_rules(graph.docs)
    roots = graph.config.code_roots

    def deprecated(cid: str) -> bool:
        data = docs[cid].fm.data if docs[cid].fm.ok else {}
        return str(data.get("status") or "").lower() == "deprecated"

    claims: dict[str, int] = {}
    for rule in rules:
        claims[rule.concept_id] = claims.get(rule.concept_id, 0) + 1

    path_report = []
    covered_by: dict[str, Fraction] = {}
    by_pattern: dict[str, Fraction] = {}
    for raw in paths:
        path = clean_path(raw)
        notes = sorted(covering_notes(rules, path))
        if notes:
            status = "covered"
        elif roots and not in_code_root(path, roots, graph.repo_root):
            status = "outside_roots"
        else:
            status = "uncovered"
        path_report.append({"path": path, "status": status, "notes": notes})
        named = {r.concept_id for r in rules if not r.is_glob and r.pattern == path}
        for cid in notes:
            # A claimed path is worth 1/(paths the note claims): a note about few files outranks a catalog.
            # A path matched only by a glob counts in a second, lower tier: one pattern can take in a tree.
            tier = covered_by if cid in named else by_pattern
            tier[cid] = tier.get(cid, Fraction(0)) + Fraction(1, claims[cid])

    excluded: list[dict[str, str]] = []
    covering = []
    zero = Fraction(0)
    ranked = sorted(covered_by.keys() | by_pattern.keys(),
                    key=lambda c: (-covered_by.get(c, zero), -by_pattern.get(c, zero), c))
    for cid in ranked:
        if deprecated(cid):
            excluded.append({"id": cid, "reason": "deprecated"})
        else:
            covering.append(cid)

    neighbors: dict[str, dict[str, Any]] = {}
    for edge in graph.edges:
        if edge["source"] not in covering or edge["relation"] not in FOLLOWED:
            continue
        target = edge["target"]
        if target in covered_by or target in by_pattern or target not in docs or graph.nodes[target]["file_type"] != "okf_concept":
            continue
        if deprecated(target):
            if not any(e["id"] == target for e in excluded):
                excluded.append({"id": target, "reason": "deprecated"})
            continue
        best = neighbors.get(target)
        if best is None or edge["weight"] > best["weight"]:
            neighbors[target] = {"weight": edge["weight"], "from": edge["source"], "relation": edge["relation"]}

    ordered = [(cid, "covering", None) for cid in covering]
    for cid in sorted(neighbors, key=lambda c: (-neighbors[c]["weight"], c)):
        info = neighbors[cid]
        ordered.append((cid, "neighbor", {"from": info["from"], "relation": info["relation"]}))

    packed: list[dict[str, Any]] = []
    omitted: list[dict[str, str]] = []
    used = 0
    full = False
    for cid, role, via in ordered:
        doc = docs[cid]
        body = (doc.fm.body if doc.fm.present else doc.text).strip()
        text = f"# {cid}\n\n{body}\n"
        tokens = estimate_tokens(text)
        if full or used + tokens > budget:
            full = True
            omitted.append({"id": cid, "reason": "budget"})
            continue
        used += tokens
        entry: dict[str, Any] = {"id": cid, "role": role, "tokens": tokens, "body": text}
        if via:
            entry["via"] = via
        packed.append(entry)

    empty = not ordered
    return {
        "bundle": str(graph.bundle),
        "budget": budget,
        "token_estimator": ESTIMATOR,
        "tokens_used": used,
        "paths": path_report,
        "notes": packed,
        "omitted": omitted,
        "excluded": sorted(excluded, key=lambda e: e["id"]),
        "empty": empty,
        "message": "no note covers any changed path" if empty else "",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="okf_retrieve",
        description="Return the notes that cover changed paths, plus one hop of neighbors, within a token budget.",
    )
    ap.add_argument("bundle_dir")
    ap.add_argument("--paths", nargs="+", required=True, metavar="PATH",
                    help="changed paths, relative to the repo root")
    ap.add_argument("--budget", type=int, required=True, help="token budget for the packed note bodies")
    ap.add_argument("--repo-root", help="root that repo-relative paths resolve against "
                                        "(default: repo_root in okf.config.json, else the bundle's parent)")
    ap.add_argument("--json", action="store_true", help="print the full result as JSON")
    args = ap.parse_args(argv)
    if args.budget < 0:
        ap.error("--budget must not be negative")

    bundle = resolve_bundle(args.bundle_dir)
    graph = Graph(bundle, Path(args.repo_root).expanduser().resolve() if args.repo_root else None)
    result = retrieve(graph, args.paths, args.budget)

    if args.json:
        emit_json(result)
        return EXIT_OK

    print(f"OKF RETRIEVE  {bundle}")
    for item in result["paths"]:
        print(f"  {item['status']:<14} {item['path']}  {', '.join(item['notes'])}")
    if result["empty"]:
        print(f"\n{result['message']}")
        return EXIT_OK
    print(f"\n{len(result['notes'])} note(s), {result['tokens_used']} of {result['budget']} tokens used "
          f"(estimated, {result['token_estimator']})")
    for o in result["omitted"]:
        print(f"  omitted {o['id']} ({o['reason']})")
    for e in result["excluded"]:
        print(f"  excluded {e['id']} ({e['reason']})")
    for entry in result["notes"]:
        print()
        print(entry["body"], end="")
    return EXIT_OK


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(EXIT_FATAL)
