"""A finished run keeps the reviewers' raw files, so it can be rescored after its workspace is gone.

The writers of these files are the fake agent (findings.<reviewer>.json, validation.json, as the
reviewers write them) and `review_core.context.ctx._append_log` (ctx-log.jsonl).
"""

from __future__ import annotations

import json
import os

from review_core.aggregator.gates import BlobReader, export_blobs, resolve_commit
from review_core.aggregator.pipeline import rebuild
from review_core.context.ctx import _append_log
from review_core.contracts.models import REVIEWERS
from review_core.envelope import MAX_REVIEWER_FILE_BYTES
from review_core.launcher.render import (
    CTX_LOG_NAME,
    MAX_CTX_LOG_BYTES,
    copy_reviewer_files,
    reviewer_file_names,
)


def test_the_names_are_seven_findings_files_the_verdicts_and_the_search_log():
    names = reviewer_file_names()
    assert names == (*(f"findings.{r}.json" for r in REVIEWERS), "validation.json", CTX_LOG_NAME)


def test_each_named_file_that_exists_is_copied_byte_for_byte(tmp_path):
    out, dest = tmp_path / "out", tmp_path / "kept"
    out.mkdir()
    (out / "findings.security.json").write_bytes(b'{"a": 1}')
    (out / "validation.json").write_bytes(b'{"verdicts": []}')
    _append_log(out / CTX_LOG_NAME, {"verb": "search", "tokens": 5, "exit_code": 0})
    (out / "candidates.json").write_text("{}")  # the main agent's own file is not kept
    copied = copy_reviewer_files(out, dest)
    assert sorted(copied) == ["ctx-log.jsonl", "findings.security.json", "validation.json"]
    assert sorted(p.name for p in dest.iterdir()) == sorted(copied)
    assert (dest / "findings.security.json").read_bytes() == b'{"a": 1}'


def test_a_link_is_never_followed(tmp_path):
    out, dest = tmp_path / "out", tmp_path / "kept"
    out.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("not for the run folder")
    (out / "findings.tests.json").symlink_to(secret)
    assert copy_reviewer_files(out, dest) == ()
    assert not dest.exists()


def test_a_folder_or_a_pipe_in_place_of_a_file_is_skipped(tmp_path):
    out, dest = tmp_path / "out", tmp_path / "kept"
    out.mkdir()
    (out / "findings.tests.json").mkdir()
    os.mkfifo(out / "findings.security.json")
    assert copy_reviewer_files(out, dest) == ()


def test_a_file_over_its_limit_is_skipped_and_one_at_the_limit_is_kept(tmp_path):
    out, dest = tmp_path / "out", tmp_path / "kept"
    out.mkdir()
    (out / "findings.tests.json").write_bytes(b"x" * (MAX_REVIEWER_FILE_BYTES + 1))
    (out / "findings.security.json").write_bytes(b"x" * MAX_REVIEWER_FILE_BYTES)
    (out / CTX_LOG_NAME).write_bytes(b"x" * (MAX_CTX_LOG_BYTES + 1))
    assert copy_reviewer_files(out, dest) == ("findings.security.json",)


def test_a_missing_output_folder_copies_nothing(tmp_path):
    assert copy_reviewer_files(tmp_path / "nowhere", tmp_path / "kept") == ()


def test_a_review_run_keeps_the_seven_files_beside_its_result(run):
    result = run("all_ok")
    kept = result.run_dir / "reviewers"
    names = [f"findings.{r}.json" for r in REVIEWERS]
    assert sorted(p.name for p in kept.iterdir()) == sorted([*names, "ran.json"])
    for name in names:
        assert (kept / name).read_bytes() == (result.out_dir / name).read_bytes()


def test_a_review_run_keeps_the_verdicts_of_the_validator(run):
    result = run("p1_validated")
    assert (result.run_dir / "reviewers" / "validation.json").is_file()


def test_a_reviewer_file_that_is_a_link_is_not_kept_but_the_others_are(run):
    result = run("symlink_one")
    names = {p.name for p in (result.run_dir / "reviewers").iterdir()}
    assert "findings.security.json" not in names and "findings.tests.json" in names


def test_a_failed_run_keeps_its_files_too(run):
    result = run("wrong_model")
    assert result.status == "failed"
    assert (result.run_dir / "reviewers" / "findings.tests.json").is_file()


def test_the_folder_records_which_subagents_ran_so_a_rebuild_can_trust_the_same_files(run):
    result = run("self_written")  # the language reviewer never ran; its file was written anyway
    ran = json.loads((result.run_dir / "reviewers" / "ran.json").read_text())
    assert "language" not in ran["subagents"] and "tests" in ran["subagents"]
    assert ran["subagents"] == sorted(result.subagents)


def test_rebuilding_from_the_kept_folder_gives_the_findings_the_run_stored(run, workdir, tmp_path):
    """The kept folder plus the code is a complete input: no workspace, rollout or agent needed."""
    result = run("p1_validated")
    for tag in ("base", "head"):
        export_blobs(workdir, resolve_commit(workdir, tag), tmp_path / "trees" / tag)
    kept = result.run_dir / "reviewers"
    ran = set(json.loads((kept / "ran.json").read_text())["subagents"])
    doc, _ = rebuild(
        kept, BlobReader(tmp_path / "trees" / "head", tmp_path / "trees" / "base"),
        {k: result.document["envelope"][k] for k in
         ("runner", "model", "effort", "cli_version", "sandbox_mode")},
        ran=ran, validator_ran="validator" in ran,
    )  # fmt: skip
    assert doc["findings"] == result.document["findings"] and doc["findings"]
    assert doc["envelope"] == result.document["envelope"]
