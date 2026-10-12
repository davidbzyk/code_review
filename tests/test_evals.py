"""The published evals: team tasks only, each the review team as a multi-step Harbor task."""

import tomllib
from pathlib import Path

EVALS = Path(__file__).resolve().parents[1] / "evals"


def test_the_evals_are_team_tasks_and_cases_only():
    """A single-agent task runs one agent, not the review team, so none is published."""
    assert sorted(p.name for p in EVALS.iterdir() if p.is_dir()) == ["cases", "team-tasks"]


TEAM = ["security", "tests", "correctness", "architecture", "code_quality", "compliance",
        "language"]  # fmt: skip


def test_every_team_task_runs_the_seven_reviewers_then_the_validator():
    """The review team's reviewers in order, then the graded validator step."""
    tasks = sorted((EVALS / "team-tasks").iterdir())
    assert [t.name for t in tasks] == [f"vo-t0{n}" for n in range(1, 7)]
    for task in tasks:
        steps = tomllib.loads((task / "task.toml").read_text(encoding="utf-8"))["steps"]
        assert [s["name"] for s in steps] == [*TEAM, "validator"], task.name
