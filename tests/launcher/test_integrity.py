"""The launcher trusts what it observed, not what the agent claims about its own run."""

import json

import pytest


def outcomes(result):
    """Map reviewer to outcome from the result envelope."""
    return {r["reviewer"]: r["outcome"] for r in result.document["envelope"]["reviewers"]}


def by_reviewer(result):
    """Map reviewer to its finding in the result."""
    return {f.reviewer: f for f in result.findings}


def test_final_file_cannot_claim_a_reviewer_that_never_wrote_its_file(run):
    result = run("forged_final")
    assert outcomes(result)["tests"] == "not_run"
    assert result.status == "partial"
    found = by_reviewer(result)
    # Nothing invented, nothing rewritten, nothing doubled, no credit to a reviewer that never ran.
    assert sorted(found) == sorted(set(outcomes(result)) - {"tests"})
    assert all(f.title != "invented" and f.also_raised_by == () for f in result.findings)
    assert found["security"].severity == "P2"


def test_reviewer_file_with_no_matching_subagent_is_not_counted(run):
    result = run("self_written")
    assert outcomes(result)["language"] == "spawn_declined"
    assert result.status == "partial"
    assert "language" not in {f.reviewer for f in result.findings}
    assert len(result.findings) == 6


@pytest.mark.parametrize("scenario", ["symlink_one", "oversized_one", "deep_one", "flood_one"])
def test_reviewer_file_that_is_a_link_too_large_or_too_deep_is_malformed(run, scenario):
    result = run(scenario)
    assert outcomes(result)["security"] == "malformed"
    assert result.status == "partial"
    assert "security" not in {f.reviewer for f in result.findings}


def test_agent_does_not_inherit_the_callers_environment(run, monkeypatch):
    monkeypatch.setenv("CR_SECRET_PROBE", "do-not-pass")
    result = run("env_probe")
    seen = json.loads((result.out_dir / "env.json").read_text())
    assert "CR_SECRET_PROBE" not in seen
    assert {"PATH", "HOME", "CODEX_HOME"} <= set(seen)


def test_reviewer_file_holding_another_reviewers_finding_is_malformed(run):
    result = run("wrong_owner")
    assert outcomes(result)["tests"] == "malformed"
    assert result.status == "partial"


def test_two_reviewers_reporting_the_same_lines_become_one_finding_crediting_both(run):
    result = run("collision")
    assert len(result.findings) == 6
    (merged,) = [f for f in result.findings if f.quote == "x = security"]
    assert {merged.reviewer, *merged.also_raised_by} == {"correctness", "security"}
    assert result.document["envelope"]["dropped"]["duplicate"] == 1


def test_a_finding_is_placed_where_its_quote_is_not_where_it_claims(run):
    plain, lied = run(), run("wrong_lines")
    assert len(lied.findings) == 7
    assert by_reviewer(lied)["tests"].line_start == by_reviewer(plain)["tests"].line_start
    assert all(f.also_raised_by == () for f in lied.findings)


@pytest.mark.parametrize(("scenario", "reason"), [("weak_one", "confidence_floor"),
                                                  ("bad_quote", "quote_gate")])  # fmt: skip
def test_the_launcher_applies_the_gates_itself(run, scenario, reason):
    result = run(scenario)
    assert "security" not in by_reviewer(result) and len(result.findings) == 6
    assert result.document["envelope"]["dropped"][reason] == 1
    assert outcomes(result)["security"] == "ok"


def test_refs_are_pinned_before_the_agent_runs(run):
    # The agent commits its planted quote and moves the `head` name onto that commit.
    result = run("moved_ref")
    assert "security" not in by_reviewer(result)
    assert result.document["envelope"]["dropped"]["quote_gate"] == 1


def test_a_replacement_object_planted_by_the_agent_is_not_read(run):
    # `git replace` makes git serve other content for a pinned commit id.
    result = run("replaced_object")
    assert "security" not in by_reviewer(result)
    assert result.document["envelope"]["dropped"]["quote_gate"] == 1


def test_the_repository_is_not_read_after_the_agent_ran(run):
    # The agent deletes .git outright; the result is the same as an honest run.
    honest = run().document
    assert run("trashed_repo").document == honest


def test_strong_finding_with_an_upheld_verdict_from_a_validator_is_complete(run):
    result = run("p1_validated")
    assert result.status == "complete"
    assert by_reviewer(result)["security"].severity == "P1"


@pytest.mark.parametrize("scenario", ["p1_unvalidated", "p1_forged_validation"])
def test_strong_finding_without_real_validation_makes_the_run_partial(run, scenario):
    # No verdict file; or a verdict file while no validator sub-agent ran.
    result = run(scenario)
    assert result.status == "partial"
    assert by_reviewer(result)["security"].severity == "P1"
    assert any("validator" in reason for reason in result.reasons)


def test_a_declined_finding_is_removed_by_the_launcher_itself(run):
    result = run("p1_declined")
    assert "security" not in by_reviewer(result)
    assert result.document["envelope"]["dropped"]["validator_declined"] == 1
    assert result.status == "complete"


def test_an_output_folder_that_is_a_link_is_refused_before_launch(run, workdir, tmp_path):
    import pytest

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (workdir / ".review").symlink_to(elsewhere, target_is_directory=True)
    with pytest.raises(ValueError, match="real folder"):
        run()
    assert list(elsewhere.iterdir()) == []
