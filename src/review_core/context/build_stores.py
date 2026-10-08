"""Build the context store for one case and one arm: `python -m review_core.context.build_stores`.

Writes `<out>/<slug>/<store_dir of the arm>/`. The `none` arm has no store and writes nothing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from review_core.context.providers import (
    BuildSpec,
    ProviderError,
    Registry,
    RegistryError,
    StoreError,
    load_registry,
    resolve,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
SNAPSHOTS = REPO_ROOT / "src" / "artifacts" / "snapshots"
SLUG = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")


def _fail(message: str, code: int = 2) -> int:
    """Print a one-line error and return the exit code."""
    print(f"build_stores: {' '.join(message.split())}", file=sys.stderr)
    return code


def main(argv: list[str] | None = None, *, registry: Registry | None = None) -> int:
    """Build one store; returns 0 ok, 2 for bad inputs, 1 for a failed build."""
    registry = registry or load_registry()
    parser = argparse.ArgumentParser(prog="build_stores")
    parser.add_argument("--case", required=True)
    parser.add_argument("--arm", required=True, choices=sorted(registry.providers))
    parser.add_argument("--fake-embedder", action="store_true")
    parser.add_argument("--okf-bundle", type=Path)
    parser.add_argument("--snapshots-dir", type=Path, default=SNAPSHOTS)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    row = registry.providers[args.arm]
    if not row.command:
        print(f"no store for the {row.name} arm; nothing written")
        return 0
    if not SLUG.match(args.case):
        return _fail(f"the case name {args.case!r} is not a plain name")
    cases = args.snapshots_dir / args.case
    spec = BuildSpec(
        slug=args.case,
        base_tree=cases / "base",
        head_tree=cases / "head",
        out=args.out / args.case / row.store_dir,
        cache_dir=args.cache_dir,
        fake_embedder=args.fake_embedder,
        okf_bundle=args.okf_bundle,
        settings=row.settings,
    )
    try:
        summary = resolve(row.build)(spec)
    except (ProviderError, RegistryError, StoreError) as exc:
        return _fail(str(exc))
    except Exception as exc:  # a failed build is reported in one line, not a traceback
        return _fail(f"{type(exc).__name__}: {exc}", 1)
    print(json.dumps({"store": str(spec.out), "provider": row.name, **summary}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
