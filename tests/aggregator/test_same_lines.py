"""The aggregator keeps every finding that passes its gates; findings at one place are grouped.
Fixtures: a correctness P1 and a language P2 on one quote, shaped as a real trial wrote them."""

import json
import os
import subprocess
from pathlib import Path

import pytest

from review_core.aggregator.gates import GitReader
from review_core.aggregator.pipeline import finalize, first_pass, rebuild

SAME_LINES = Path(__file__).parent / "fixtures" / "same-lines"
RUNNER = "app/images.py"
META = {"runner": "t", "model": "t", "effort": "t", "cli_version": "t", "sandbox_mode": "t"}
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


def _by_reviewer(findings: list[dict]) -> dict[str, dict]:
    """Findings by reviewer."""
    return {f["reviewer"]: f for f in findings}


def _decline_language(out: Path, repo: Path, base: str, head: str) -> None:
    """Raise the language finding to P1, run the first pass, and decline it alone."""
    language = out / "findings.language.json"
    doc = json.loads(language.read_text())
    doc["findings"][0]["severity"] = "P1"
    language.write_text(json.dumps(doc))
    first_pass(out, repo, base, head)
    given = json.loads((out / "validator-input.json").read_text())["findings"]
    verdicts = [{"id": f["id"], "verdict": "declined" if f["title"] == doc["findings"][0]["title"]
                 else "upheld", "reason": "r"} for f in given]  # fmt: skip
    (out / "validation.json").write_text(json.dumps({"verdicts": verdicts}))


def test_two_problems_on_the_same_lines_both_reach_the_validator(same_lines):
    """A finding is never dropped because another reviewer reported on its lines."""
    out, repo, base, head = same_lines

    candidates = first_pass(out, repo, base, head)

    found = _by_reviewer(candidates["findings"])
    assert set(found) == {"correctness", "language"}
    assert candidates["dropped"]["duplicate"] == 0
    assert found["correctness"]["also_raised_by"] == ["language"]
    assert found["language"]["also_raised_by"] == ["correctness"]
    given = json.loads((out / "validator-input.json").read_text())["findings"]
    assert [f["title"] for f in given] == [found["correctness"]["title"]]  # P2 is not validated


def test_a_decline_names_one_of_two_findings_on_the_same_lines(same_lines):
    """Two P1 findings on one quote from two reviewers get two verdict ids; declining one
    removes only that one."""
    out, repo, base, head = same_lines
    _decline_language(out, repo, base, head)

    run = finalize(out, META)

    assert [f["reviewer"] for f in run["findings"]] == ["correctness"]
    assert run["envelope"]["dropped"]["validator_declined"] == 1
    declined = json.loads((out / "declined.json").read_text())
    assert [row["reviewer"] for row in declined] == ["language"]


def test_a_declined_finding_is_not_named_beside_the_one_kept(same_lines):
    """Grouping used to run before the verdicts, so the kept correctness finding still named
    the declined language reviewer as also on its lines, in findings.json and a rebuild."""
    out, repo, base, head = same_lines
    _decline_language(out, repo, base, head)

    final = finalize(out, META)
    rebuilt, _ = rebuild(out, GitReader(repo, base, head), META)

    for run in (final, rebuilt):
        assert [(f["reviewer"], f["also_raised_by"]) for f in run["findings"]] == [
            ("correctness", [])
        ]
