"""Command line: `search` and `related` (light imports) and `build` (lazy import)."""

from __future__ import annotations

import argparse
import json
import sys

from context_engine.embed import OpenAIEmbedder, hashed_bow_embedder
from context_engine.retrieve import related, search
from context_engine.store import load_store


def main(argv: list[str] | None = None) -> int:
    """Dispatch a command; returns the process exit code."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "build":
        from context_engine.build_cli import main as build_main  # build side, only for build

        return build_main(argv)
    parser = argparse.ArgumentParser(prog="context_engine")
    sub = parser.add_subparsers(dest="command", required=True)
    find = sub.add_parser("search", help="hybrid search over a store")
    find.add_argument("store")
    find.add_argument("text")
    near = sub.add_parser("related", help="chunks related to the change in one path")
    near.add_argument("store")
    near.add_argument("path")
    for p in (find, near):
        p.add_argument("--k", type=int, default=None)
    args = parser.parse_args(argv)
    try:
        store = load_store(args.store)
    except (OSError, ValueError, KeyError) as exc:
        print(f"cannot read the store at {args.store}: {exc}", file=sys.stderr)
        return 2
    if args.command == "search":
        manifest = store.manifest
        if manifest["model"] == "fake":
            embed = hashed_bow_embedder(manifest["vector_size"])
        else:
            embed = OpenAIEmbedder.from_settings(manifest["settings"]["embedding"])
        out = search(store, args.text, args.k, embed)
    else:
        out = related(store, args.path, args.k)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
