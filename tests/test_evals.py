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
    scored = [f"vo-t0{n}" for n in range(1, 7)]
    keyed_from_reviews = [f"vo-x{n}" for n in (1, 4, 7, 8, 17, 20)]
    judged = ("vo-x7", "vo-x4", "vo-t06", "vo-t01", "vo-t04", "vo-t02")
    llm_judge = [f"{s}-llm-judge" for s in judged]
    assert sorted(t.name for t in tasks) == sorted(scored + keyed_from_reviews + llm_judge)
    for task in tasks:
        steps = tomllib.loads((task / "task.toml").read_text(encoding="utf-8"))["steps"]
        assert [s["name"] for s in steps] == [*TEAM, "validator"], task.name


def test_every_llm_judge_task_scores_weighted_scales_summing_to_one():
    """An -llm-judge task's grader rates 1-5 scales whose weights sum to 1, and gets the code."""
    judged = sorted((EVALS / "team-tasks").glob("*-llm-judge"))
    assert len(judged) == 6
    for task in judged:
        tests = task / "steps" / "validator" / "tests"
        crit = tomllib.loads((tests / "rubric" / "review" / "judge.toml").read_text())["criterion"]
        assert all(c["type"] == "likert" and c["points"] == 5 for c in crit), task.name
        assert abs(sum(c["weight"] for c in crit) - 1) < 1e-9, task.name
        assert (tests / "workspace" / "known_issues.json").is_file(), task.name
        assert (tests / "workspace" / "repo.tar.gz").is_file(), task.name
