"""Fixtures: two reviewers' findings on the same lines, shaped as a real trial wrote them, over
a repository whose head holds the quoted lines."""

import json
import os
import subprocess
from pathlib import Path

import pytest

SAME_LINES = Path(__file__).parent / "fixtures" / "same-lines"
RUNNER = "app/images.py"
GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}  # fmt: skip


def git(repo: Path, *args: str) -> str:
    """Run git with no user config and a fixed identity; returns stdout."""
    done = subprocess.run(["git", "-C", str(repo), *args], env=GIT_ENV, check=True,
                          capture_output=True, text=True)  # fmt: skip
    return done.stdout.strip()


@pytest.fixture
def same_lines(tmp_path) -> tuple[Path, Path, str, str]:
    """(output folder holding the two reviewer files, repository, base, head)."""
    out, repo = tmp_path / "review", tmp_path / "repo"
    out.mkdir()
    repo.mkdir()
    quote = None
    for doc in (SAME_LINES / f"findings.{r}.json" for r in ("correctness", "language")):
        (out / doc.name).write_text(doc.read_text())
        quote = json.loads(doc.read_text())["findings"][0]["quote"]
    git(repo, "init", "-q", "-b", "main")
    (repo / "README.md").write_text("base\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "base")
    base = git(repo, "rev-parse", "HEAD")
    source = repo / RUNNER
    source.parent.mkdir(parents=True)
    filler = "".join(f"# line {n}\n" for n in range(1, 301))
    source.write_text(f"{filler}{quote}\n        return names[0]\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "head")
    return out, repo, base, git(repo, "rev-parse", "HEAD")
