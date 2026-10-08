"""The team started as separate agents: one process per reviewer, then the validator.

The fake agent (fake_agent.py) acts as whichever member its prompt names. The team and the
messages are read from the packaged orchestrator skill, so these tests also pin that the skill
still says what the launcher needs from it.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from review_core.contracts.models import REVIEWERS
from review_core.launcher import team as team_mod
from review_core.launcher.render import prompt_extras

PACKAGED = Path(__file__).resolve().parents[2] / "src" / "plugin" / "skills"


@pytest.fixture
def team_skills(tmp_path) -> Path:
    """A skills folder with the packaged orchestrator skill and a stub for every member."""
    path = tmp_path / "team-skills"
    shutil.copytree(PACKAGED / "review-orchestrator", path / "review-orchestrator")
    members = team_mod.read_team(path)
    for skill in (*members.reviewers.values(), members.validator_skill):
        (path / skill).mkdir()
        (path / skill / "SKILL.md").write_text(f"# {skill}\n")
    return path


@pytest.fixture
def go(run, team_skills):
    """Run the fake team as separate agents."""

    def start(scenario="all_ok", **kw):
        return run(scenario, team="separate", skills_dir=team_skills, **kw)

    return start


def seen(result, name: str) -> dict:
    """What one fake member recorded about how it was started."""
    return json.loads((result.out_dir / f"seen.{name}.json").read_text())


# --- the team as the skill lays it out -------------------------------------------------------


def test_the_packaged_skill_names_every_reviewer_and_both_messages():
    members = team_mod.read_team(PACKAGED)
    assert tuple(members.reviewers) == REVIEWERS
    assert members.reviewers["code_quality"] == "review-code-quality"
    assert members.validator_skill == "review-validator"
    assert "<reviewer>" in members.reviewer_message and "<out>" in members.validator_message


def test_a_skill_that_does_not_lay_out_a_team_is_refused(skills):
    with pytest.raises(team_mod.TeamError, match="does not name the reviewers"):
        team_mod.read_team(skills)


def test_a_message_is_the_skills_own_words_with_only_the_given_items():
    members = team_mod.read_team(PACKAGED)
    values = {"<skill>": "review-tests", "<reviewer>": "tests", "<base>": "b", "<head>": "h",
              "<out>": "/o"}  # fmt: skip
    bare = team_mod.fill(members.reviewer_message, values, [], "in the folder `app`")
    assert bare.startswith("Use the review-tests skill. You are the `tests` reviewer.\n")
    assert "between git refs b and h in the repository in the folder `app`." in bare
    assert "Write your findings to /o/findings.tests.json." in bare
    assert "<" not in bare and "Your slice" not in bare and "Context search command" not in bare
    extras = prompt_extras(["app.py"], "Adds a line.", "ctx . search", "Read first.")
    full = team_mod.fill(members.reviewer_message, values, extras, "in the current directory")
    assert full.splitlines()[-4:] == extras  # every optional line of the skill has its item
    assert len(full.splitlines()) == len(bare.splitlines()) + 4


def test_a_placeholder_nothing_fills_is_an_error_not_a_message():
    with pytest.raises(team_mod.TeamError, match="<mystery>"):
        team_mod.fill("Do <mystery> now.", {"<base>": "b"}, [], "here")


# --- a run -----------------------------------------------------------------------------------


def test_each_reviewer_is_its_own_agent_with_its_own_skill_and_message(go):
    result = go()
    assert result.status == "complete" and len(result.findings) == 7
    assert set(result.subagents) == set(REVIEWERS)
    for name in REVIEWERS:
        mine = seen(result, name)
        assert mine["skills"] == ["review-" + name.replace("_", "-")]
        assert f"You are the `{name}` reviewer." in mine["prompt"]
        assert "review-orchestrator" not in mine["prompt"]
        assert (result.run_dir / "agents" / name / "events.jsonl").is_file()
    record = json.loads((result.run_dir / "team.json").read_text())
    assert [a["agent"] for a in record["agents"]] == list(REVIEWERS)
    assert all(a["counted"] and a["exit_code"] == 0 for a in record["agents"])
    assert not (result.run_dir / "home" / ".agents").exists()  # no shared set of skills


def test_tokens_are_listed_per_member(go):
    usage = json.loads((go().run_dir / "usage.json").read_text())
    assert set(usage["sessions"]) == set(REVIEWERS)
    assert usage["total"]["total_tokens"] == sum(
        s["total_tokens"] for s in usage["sessions"].values()
    )


def test_one_reviewer_can_be_run_alone(go):
    result = go(reviewers=["security"])
    envelope = result.document["envelope"]
    assert envelope["reviewers_planned"] == ["security"] and result.status == "complete"
    assert [f.reviewer for f in result.findings] == ["security"]
    assert not (result.out_dir / "findings.tests.json").exists()


def test_a_reviewer_can_have_its_own_model(go):
    result = go(reviewers=["security", "tests"], models={"tests": "gpt-6.1-sol"})
    assert seen(result, "tests")["model"] == "gpt-6.1-sol"
    assert seen(result, "security")["model"] == "gpt-6-luna"
    assert result.document["envelope"]["model"] == "gpt-6-luna,gpt-6.1-sol"
    assert result.status == "complete"


def test_a_reviewer_that_writes_nothing_leaves_the_run_partial(go):
    result = go("missing_one")
    assert result.status == "partial" and len(result.findings) == 6


def test_a_reviewer_whose_record_shows_another_model_is_left_out(go):
    result = go("solo_wrong_model")
    assert result.status == "partial"
    assert "security" not in {f.reviewer for f in result.findings}
    assert any(r.startswith("security: model mismatch") for r in result.reasons)


def test_a_run_in_which_no_agent_starts_has_failed(go):
    result = go("auth_fail")
    assert result.status == "failed" and result.findings == ()


def test_the_validator_is_started_only_when_a_finding_needs_a_verdict(go):
    plain = go()
    assert not (plain.out_dir / "validator-input.json").exists()
    assert not (plain.run_dir / "agents" / "validator").exists()


def test_the_validator_is_its_own_agent_and_its_verdict_counts(go):
    result = go("p1_validated")
    mine = seen(result, "validator")
    assert mine["skills"] == ["review-validator"]
    assert mine["prompt"].startswith("Use the review-validator skill. The output folder is ")
    assert "validator" in result.subagents and not result.reasons
    assert [f.severity for f in result.findings if f.reviewer == "security"] == ["P1"]


def test_a_declined_finding_is_dropped(go):
    result = go("p1_declined")
    assert "security" not in {f.reviewer for f in result.findings}
    assert result.document["envelope"]["dropped"]["validator_declined"] == 1


def test_the_validators_input_is_never_written_through_a_planted_link(go, workdir, tmp_path):
    out = workdir / ".review-linked"
    out.mkdir()
    target = tmp_path / "elsewhere.json"
    target.write_text("untouched")
    (out / "validator-input.json").symlink_to(target)
    result = go("p1_validated", out_dir=out)
    assert target.read_text() == "untouched"
    assert any("its input file could not be written" in r for r in result.reasons)


def test_reviewers_run_at_once_unless_told_otherwise(go):
    result = go(parallel=1, reviewers=["security", "tests"])
    assert result.status == "complete"


@pytest.mark.parametrize(
    "kw",
    [{"reviewers": []}, {"reviewers": ["nobody"]}, {"reviewers": ["tests", "tests"]},
     {"models": {"nobody": "gpt-6-luna"}}],
)  # fmt: skip
def test_a_team_of_unknown_or_repeated_reviewers_is_refused(go, kw):
    with pytest.raises(ValueError, match="reviewers must be distinct names"):
        go(**kw)


def test_the_one_agent_run_takes_no_team_settings(run):
    with pytest.raises(ValueError, match="belong to a separate team run"):
        run(reviewers=["security"])
    with pytest.raises(ValueError, match="team must be one of"):
        run(team="several")


def test_the_fake_agent_still_plays_the_whole_team_for_a_one_agent_run(run, fake):
    assert fake.REVIEWERS == list(REVIEWERS)
    assert len(run().findings) == 7
