"""The published evals: team tasks only, each the review team as a multi-step Harbor task."""

import tomllib
from pathlib import Path

EVALS = Path(__file__).resolve().parents[1] / "evals"


def test_the_evals_are_team_tasks_and_cases_only():
    """A single-agent task runs one agent, not the review team, so none is published."""
    assert sorted(p.name for p in EVALS.iterdir() if p.is_dir()) == ["cases", "team-tasks"]


def test_every_team_task_runs_seven_reviewers_then_the_validator():
    """Eight steps each, the graded validator last."""
    tasks = sorted((EVALS / "team-tasks").iterdir())
    assert [t.name for t in tasks] == [f"vo-t0{n}" for n in range(1, 7)]
    for task in tasks:
        steps = tomllib.loads((task / "task.toml").read_text(encoding="utf-8"))["steps"]
        assert len(steps) == 8 and steps[-1]["name"] == "validator", task.name
