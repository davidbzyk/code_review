"""A reviewer's file is model output: near misses are kept where sound and counted where not.

The shapes here are the ones real runs produced (2026-10-05, tuning case vo-d01): an empty
result written as `{"findings":[]}` with no header, and findings with a confidence of 90 and 95
where the contract allows five fixed values.
"""

import json

import pytest

from review_core.aggregator import gates
from review_core.aggregator.pipeline import rebuild
from review_core.contracts.models import DROP_REASONS
from review_core.envelope import DROP_COUNTS, read_reviewer

from .conftest import make_finding as f
from .conftest import make_repo, write_reviewer

META = {"runner": "r", "model": "m", "effort": "high", "cli_version": "1", "sandbox_mode": "ro"}


def put(out, reviewer, doc) -> None:
    """Write a reviewer file exactly as given."""
    out.mkdir(exist_ok=True)
    (out / f"findings.{reviewer}.json").write_text(json.dumps(doc))


def test_drop_reasons_are_stated_once_and_include_malformed():
    assert DROP_COUNTS is DROP_REASONS and "malformed" in DROP_REASONS


def test_an_empty_result_without_its_header_is_an_empty_result(tmp_path):
    put(tmp_path, "security", {"findings": []})
    assert read_reviewer(tmp_path, "security")[0] == "empty"


def test_a_header_naming_another_reviewer_is_still_refused(tmp_path):
    put(tmp_path, "security", {"reviewer": "tests", "findings": []})
    assert read_reviewer(tmp_path, "security")[0] == "malformed"
    put(tmp_path, "tests", {"schema_version": 2, "reviewer": "tests", "findings": []})
    assert read_reviewer(tmp_path, "tests")[0] == "malformed"


@pytest.mark.parametrize(("given", "kept"), [(90, 75), (95, 75), (100, 100), (60, 50), (10, 0)])
def test_a_confidence_between_two_allowed_values_is_lowered_never_raised(tmp_path, given, kept):
    put(tmp_path, "compliance", {"findings": [f("compliance", confidence=given)]})
    outcome, doc, bad = read_reviewer(tmp_path, "compliance")
    assert (outcome, bad) == ("ok", 0) and doc.findings[0].confidence == kept


@pytest.mark.parametrize("confidence", [101, -5, "90", 90.5, None, True])
def test_a_confidence_that_is_no_whole_number_from_0_to_100_drops_that_finding(
    tmp_path, confidence
):
    good = f("tests", title="sound")
    write_reviewer(tmp_path, "tests", [f("tests", confidence=confidence), good])
    outcome, doc, bad = read_reviewer(tmp_path, "tests")
    assert (outcome, bad) == ("ok", 1) and [x.title for x in doc.findings] == ["sound"]


def test_a_finding_credited_to_another_reviewer_is_dropped_and_the_rest_kept(tmp_path):
    write_reviewer(tmp_path, "tests", [f("tests"), {**f("tests"), "reviewer": "security"}])
    outcome, doc, bad = read_reviewer(tmp_path, "tests")
    assert (outcome, bad, len(doc.findings)) == ("ok", 1, 1)


def test_a_file_with_no_sound_finding_at_all_is_malformed(tmp_path):
    write_reviewer(tmp_path, "tests", [{"title": "no fields"}, "not an object"])
    assert read_reviewer(tmp_path, "tests")[::2] == ("malformed", 2)


def test_dropped_findings_are_counted_in_the_result(tmp_path):
    repo = make_repo(tmp_path, {"a.py": "a\n"}, {"a.py": "a\nx = 1\n"})
    out = tmp_path / "out"
    put(out, "security", {"findings": []})
    put(out, "compliance", {"findings": [f("compliance", quote="x = 1", line_start=2, line_end=2,
                                           confidence=95), {"title": "broken"}]})  # fmt: skip
    for other in ("tests", "correctness", "architecture", "code_quality", "language"):
        write_reviewer(out, other, [])
    run, _ = rebuild(out, gates.GitReader(repo, "base", "head"), META)
    # Something a reviewer wrote was thrown away, so the run cannot call itself complete: a
    # change that talks a reviewer into a broken finding must not buy a clean result.
    assert run["envelope"]["status"] == "partial"
    assert run["envelope"]["dropped"]["malformed"] == 1
    assert [(x["reviewer"], x["confidence"]) for x in run["findings"]] == [("compliance", 75)]


def test_a_repaired_file_with_nothing_dropped_still_completes(tmp_path):
    repo = make_repo(tmp_path, {"a.py": "a\n"}, {"a.py": "a\nx = 1\n"})
    out = tmp_path / "out"
    put(out, "security", {"findings": []})
    put(out, "compliance", {"findings": [f("compliance", quote="x = 1", line_start=2, line_end=2,
                                           confidence=95, severity="P3")]})  # fmt: skip
    for other in ("tests", "correctness", "architecture", "code_quality", "language"):
        write_reviewer(out, other, [])
    run, _ = rebuild(out, gates.GitReader(repo, "base", "head"), META)
    assert run["envelope"]["status"] == "complete" and len(run["findings"]) == 1


def test_the_contract_refuses_a_complete_run_that_dropped_malformed_findings(tmp_path):
    from review_core.contracts.models import ContractError, load_run_envelope

    repo = make_repo(tmp_path, {"a.py": "a\n"}, {"a.py": "a\nx = 1\n"})
    out = tmp_path / "out"
    out.mkdir()
    for name in ("security", "tests", "correctness", "architecture", "code_quality",
                 "compliance", "language"):  # fmt: skip
        write_reviewer(out, name, [])
    run, _ = rebuild(out, gates.GitReader(repo, "base", "head"), META)
    assert load_run_envelope(run)
    run["envelope"]["dropped"]["malformed"] = 1
    with pytest.raises(ContractError, match="malformed"):
        load_run_envelope(run)
