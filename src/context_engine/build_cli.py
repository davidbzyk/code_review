"""The `build` command (build side): index a tree and record the change against it."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from context_engine.embed import EmbedError, OpenAIEmbedder, hashed_bow_embedder
from context_engine.index import EmbedBudgetError, TreeTooLarge, build_index
from context_engine.report import CoverageError
from context_engine.settings import load_settings


def _overrides(pairs: list[str]) -> dict:
    """Turn `a.b=value` flags into a nested dict; values are JSON when they parse as JSON."""
    out: dict = {}
    for pair in pairs:
        key, _, raw = pair.partition("=")
        try:
            value = json.loads(raw)
        except ValueError:
            value = raw
        node = out
        *parents, last = key.split(".")
        for part in parents:
            node = node.setdefault(part, {})
        node[last] = value
    return out


def main(argv: list[str] | None = None) -> int:
    """Run `build`; returns the process exit code (0 ok, 2 coverage, 3 embedding)."""
    parser = argparse.ArgumentParser(prog="context_engine")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="index BASE and record how HEAD differs")
    build.add_argument("base", type=Path)
    build.add_argument("head", type=Path)
    build.add_argument("out", type=Path)
    build.add_argument("--cache-dir", type=Path, required=True)
    build.add_argument(
        "--fake-embedder",
        action="store_true",
        help="offline hashed bag-of-words vectors, recorded as model 'fake' (no key, no network)",
    )
    build.add_argument("--set", action="append", default=[], metavar="TABLE.KEY=VALUE")
    args = parser.parse_args(argv)

    settings = load_settings(_overrides(args.set))
    emb = settings["embedding"]
    if args.fake_embedder:
        model, size = "fake", emb["fake_vector_size"]
        embed = hashed_bow_embedder(size)
    else:
        model, size = emb["model"], emb["vector_size"]
        embed = OpenAIEmbedder.from_settings(emb)
    started = time.monotonic()
    try:
        stats = build_index(
            args.base, args.head, args.out, args.cache_dir, embed, model, size, settings
        )
    except TreeTooLarge as exc:
        print(f"build refused: {exc}", file=sys.stderr)
        return 3
    except EmbedBudgetError as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 3
    except CoverageError as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 2
    except EmbedError as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 3
    summary = {
        "store": str(args.out),
        "model": model,
        "files": stats.files,
        "chunks": stats.chunks,
        "embedded_texts": stats.embedded_texts,
        "cache_hits": stats.cache_hits,
        "estimated_embed_tokens": stats.estimated_tokens,
        "seconds": round(time.monotonic() - started, 2),
        "store_sha256": stats.store_sha256,
        "languages": {
            name: {k: rec[k] for k in ("lines_seen", "lines_covered")}
            | {"parse_failures": rec["parse_failures"], "skipped": rec["files_skipped"]}
            for name, rec in stats.report["languages"].items()
        },
        "excluded": stats.report["excluded"],
    }
    print(json.dumps(summary, indent=2))
    return 0
