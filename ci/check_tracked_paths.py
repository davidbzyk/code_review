#!/usr/bin/env python3
"""Refuse a commit that stages private case material, graded output or credentials.

Rules live in ci/tracked-paths.toml: denied globs, denied file names, and needle sources (JSON
files under $REVIEW_PRIVATE_ROOT whose text must not appear in any staged file). Without a
private root only paths and names are checked. Standard library only.

    python3 ci/check_tracked_paths.py      # exit 1 and name each refused file
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = Path("ci") / "tracked-paths.toml"


def staged_paths(repo: Path) -> list[str]:
    """Paths staged for the next commit (added, copied, modified or renamed)."""
    done = subprocess.run(
        ["git", "-C", str(repo), "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
        capture_output=True, check=True,
    )  # fmt: skip
    return [p for p in done.stdout.decode().split("\0") if p]


def staged_text(repo: Path, path: str) -> str:
    """The staged content of one file, decoded leniently."""
    done = subprocess.run(["git", "-C", str(repo), "show", f":{path}"], capture_output=True)
    return done.stdout.decode("utf-8", errors="replace")


def _strings(value, field: str) -> list[str]:
    """Strings at a dotted field path, descending through lists."""
    head, _, rest = field.partition(".")
    items = value if isinstance(value, list) else [value]
    out = []
    for item in items:
        if not isinstance(item, dict) or head not in item:
            continue
        inner = item[head]
        if rest:
            out += _strings(inner, rest)
        elif isinstance(inner, str):
            out.append(inner)
        elif isinstance(inner, list):
            out += [s for s in inner if isinstance(s, str)]
    return out


def needles(private: Path, rules: dict) -> list[str]:
    """Private strings long enough to be case material, from the rules' needle sources."""
    found = set()
    for source in rules.get("needles", []):
        for path in sorted(private.glob(source["glob"])):
            doc = json.loads(path.read_text(encoding="utf-8"))
            for field in source["fields"]:
                found.update(
                    " ".join(s.split())
                    for s in _strings(doc, field)
                    if len(s.strip()) >= rules["min_chars"]
                )
    return sorted(found)


def refused_path(path: str, rules: dict) -> str | None:
    """Why a path may not be tracked, or None."""
    name = Path(path).name
    if name in rules.get("allow_names", []):
        return None
    lowered = path.lower()
    for glob in rules.get("deny_globs", []):
        if fnmatch(lowered, glob) or fnmatch(name.lower(), glob):
            return f"matches {glob}"
    # Case material published on purpose (the public voiceover eval tasks) is allowed by path.
    if any(fnmatch(lowered, glob) for glob in rules.get("allow_globs", [])):
        return None
    if name in rules.get("deny_names", []):
        return f"file name {name} is never tracked"
    return None


def check(repo: Path, private: Path | None) -> list[str]:
    """One `path: reason` line per staged file that must not be committed."""
    rules = tomllib.loads((repo / RULES).read_text(encoding="utf-8"))
    texts = needles(private, rules) if private else []
    problems = []
    for path in staged_paths(repo):
        reason = refused_path(path, rules)
        if reason is None and texts:
            body = " ".join(staged_text(repo, path).split())
            if any(t in body for t in texts):
                reason = "holds text from private case material"
        if reason:
            problems.append(f"{path}: {reason}")
    return problems


def main() -> int:
    private = os.environ.get("REVIEW_PRIVATE_ROOT")
    problems = check(ROOT, Path(private) if private else None)
    for line in problems:
        print(f"refused {line}", file=sys.stderr)
    if not private:
        print("tracked-path check: paths only (set REVIEW_PRIVATE_ROOT to check text)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
