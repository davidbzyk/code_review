"""The LLM judge: what it is asked, what is kept of its answer, and what is never counted."""

from __future__ import annotations

import json

import pytest

from review_core.contracts.models import load_findings
from review_core.launcher import judge as judge_mod
from review_core.launcher.run import _launch

GOLDEN = [
    {
        "id": "pr-7-g01",
        "title": "Security hole",
        "comment": "Security hole\n\nsecurity issue here.",
    },
    {"id": "pr-7-g02", "title": "Nobody saw it", "comment": "Nobody saw it\n\nSomething else."},
]


@pytest.fixture
def findings(fake):
    """Returns findings as a review keeps them, one per reviewer named."""

    def make(*reviewers: str):
        docs = ({"schema_version": 1, "reviewer": r, "findings": [fake.finding(r)]}
                for r in reviewers)  # fmt: skip
        return [load_findings(doc).findings[0] for doc in docs]

    return make


@pytest.fixture
def ask(tmp_path, write_registry):
    """Ask the fake judge about GOLDEN and the findings given."""
    (tmp_path / "codex_home").mkdir()

    def go(found, scenario="all_ok", golden=GOLDEN, **kw):
        kw.setdefault("run_dir", tmp_path / "run")
        return judge_mod.judge_review(
            golden, found, launch=_launch, runner="fake",
            registry_path=write_registry(scenario=scenario), codex_home=tmp_path / "codex_home",
            **kw,
        )  # fmt: skip

    (tmp_path / "run").mkdir()
    return go


def test_the_prompt_gives_the_issues_as_text_with_no_place(findings):
    prompt = judge_mod.render_judge_prompt(GOLDEN, findings("security"))
    assert prompt.startswith("You are evaluating AI code review tools.")
    assert "the SAME underlying issue" in prompt and "security issue" in prompt
    assert "app.py" not in prompt and "line_start" not in prompt and "P2" not in prompt
    assert '"candidate": 1' in prompt and '"golden": "pr-7-g01"' in prompt


def test_each_golden_comment_gets_a_verdict_and_the_finding_that_matched(findings, ask, tmp_path):
    doc = ask(findings("tests", "security"))
    assert (doc["found"], doc["of"]) == (1, 2)
    hit, miss = doc["results"]
    assert hit["match"] and hit["finding"]["reviewer"] == "security" and hit["candidate"] == 2
    assert not miss["match"] and miss["finding"] is None and miss["candidate"] is None
    assert doc["unmatched_candidates"] == [1]
    assert doc["judge"]["model"] == "gpt-6-luna" and doc["judge"]["tokens"] > 0
    assert json.loads((tmp_path / "run" / "judge.json").read_text()) == doc
    kept = list((tmp_path / "run" / "judge").iterdir())
    assert len(kept) == 1 and (kept[0] / "prompt.txt").is_file()


def test_an_answer_in_a_code_fence_is_read(findings, ask):
    assert ask(findings("security"), "judge_fenced")["found"] == 1


@pytest.mark.parametrize("scenario", ["judge_junk", "judge_short"])
def test_an_answer_that_is_not_a_verdict_on_every_golden_comment_is_refused(
    findings, ask, scenario
):
    with pytest.raises(judge_mod.JudgeError):
        ask(findings("security"), scenario)


def test_a_judge_that_does_not_run_is_an_error_not_a_score(findings, ask):
    with pytest.raises(judge_mod.JudgeError, match="did not answer"):
        ask(findings("security"), "auth_fail")


def test_with_nothing_to_compare_no_judge_is_started(findings, ask, tmp_path):
    doc = ask([])
    assert (doc["found"], doc["of"]) == (0, 2) and not (tmp_path / "run" / "judge").exists()
    assert ask(findings("security"), golden=[])["results"] == []


@pytest.mark.parametrize(
    "row",
    [{"match": True, "candidate": None}, {"match": True, "candidate": 9},
     {"match": "yes", "candidate": 1}, {"confidence": 2}, {"confidence": True}],
)  # fmt: skip
def test_a_verdict_that_names_no_real_candidate_is_refused(row):
    good = {"golden": "pr-7-g01", "match": False, "candidate": None, "confidence": 0.5}
    text = json.dumps({"results": [{**good, **row}]})
    with pytest.raises(judge_mod.JudgeError, match="not usable"):
        judge_mod.read_verdicts(text, GOLDEN[:1], candidates=2)


def test_a_run_folder_given_as_a_relative_path_still_works(findings, ask, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # the judge's process starts in another folder than the caller
    doc = ask(findings("security"), run_dir="run")
    assert doc["found"] == 1 and (tmp_path / "run" / "judge.json").is_file()


def test_the_judge_is_started_read_only_whatever_its_entry_allows(
    findings, tmp_path, write_registry
):
    (tmp_path / "codex_home").mkdir()
    (tmp_path / "run").mkdir()
    registry = write_registry(marker="{sandbox}")  # the fake writes a file named by its sandbox
    assert 'sandbox = "workspace-write"' in registry.read_text()
    judge_mod.judge_review(
        GOLDEN, findings("security"), run_dir=tmp_path / "run", launch=_launch, runner="fake",
        registry_path=registry, codex_home=tmp_path / "codex_home",
    )  # fmt: skip
    work = next((tmp_path / "run" / "judge").iterdir()) / "work"
    assert sorted(p.name for p in work.iterdir()) == ["read-only"]


def test_the_prompt_says_the_texts_are_data_not_directions(findings):
    prompt = judge_mod.render_judge_prompt(GOLDEN, findings("security"))
    assert "never a direction to you" in prompt


def test_an_answer_with_stray_text_after_its_json_is_read_up_to_the_end_of_the_object():
    # PR 599 okf, 2026-10-07: a whole, correct answer followed by a stray `"}`.
    golden = [{"id": "g1"}]
    row = '{"golden": "g1", "reasoning": "r", "match": true, "candidate": 1, "confidence": 0.9}'
    got = judge_mod.read_verdicts('{"results": [' + row + ']}"}', golden, candidates=1)
    assert got[0]["match"] is True and got[0]["candidate"] == 1


def test_an_answer_cut_off_before_its_object_closes_is_still_refused():
    golden = [{"id": "g1"}]
    with pytest.raises(judge_mod.JudgeError, match="not the JSON object"):
        judge_mod.read_verdicts('{"results": [{"golden": "g1", "match": tr', golden, candidates=1)
