"""Fixtures: finding builders, reviewer files and a throwaway git repository."""

import json
import subprocess
from pathlib import Path

GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]


def make_finding(reviewer="security", **overrides) -> dict:
    """A valid reviewer finding; override any field."""
    item = {
        "file": "a.py", "line_start": 5, "line_end": 5, "side": "new", "quote": "x = 1",
        "title": "t", "description": "d", "severity": "P2", "confidence": 75,
        "category": reviewer, "reviewer": reviewer, "scope": "in_diff", "fingerprint": None,
    }  # fmt: skip
    item.update(overrides)
    return item


def write_reviewer(out: Path, reviewer: str, findings: list[dict]) -> None:
    """Write findings.<reviewer>.json the way a reviewer sub-agent would."""
    doc = {"schema_version": 1, "reviewer": reviewer, "findings": findings}
    (out / f"findings.{reviewer}.json").write_text(json.dumps(doc), encoding="utf-8")


def _git(repo: Path, *args: str) -> None:
    """Run one git command in the repository, failing the test on error."""
    subprocess.run([*GIT, "-C", str(repo), *args], check=True, capture_output=True)


def make_repo(root: Path, base: dict[str, str], head: dict[str, str]) -> Path:
    """Create a repo with tags `base` and `head`, each holding exactly the given files."""
    repo = root / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    for tag, files in (("base", base), ("head", head)):
        for old in repo.iterdir():
            if old.name != ".git":
                old.unlink()
        for name, text in files.items():
            (repo / name).write_text(text, encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "--allow-empty", "-m", tag)
        _git(repo, "tag", tag)
    return repo
