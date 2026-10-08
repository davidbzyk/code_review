"""End-to-end launcher behaviour against the fake agent."""

import json
import os
import time

import pytest

from review_core.contracts.models import load_manifest, load_run_envelope
from review_core.envelope import build_envelope
from review_core.launcher.runners import RegistryError

REVIEWERS = ["security", "tests", "correctness", "architecture", "code_quality", "compliance",
             "language"]  # fmt: skip


@pytest.fixture
def notes(workdir):
    """The project's own `okf/` folder of notes, copied from the okf plugin's fixture bundle."""
    import shutil
    from pathlib import Path

    src = Path(__file__).parents[1] / "context" / "fixtures" / "okf-bundle"
    return shutil.copytree(src, workdir / "okf")


def outcomes(result):
    """Map reviewer to outcome from the result envelope."""
    return {r["reviewer"]: r["outcome"] for r in result.document["envelope"]["reviewers"]}


@pytest.mark.parametrize("shape", ["a", "b"])
def test_seven_valid_files_make_a_complete_run(run, shape):
    seen = []
    result = run(shape=shape, on_event=seen.append)
    assert result.status == "complete"
    assert outcomes(result) == dict.fromkeys(REVIEWERS, "ok")
    assert len(result.findings) == 7
    assert all(len(f.fingerprint) == 64 for f in result.findings)
    assert result.subagents == tuple(sorted(REVIEWERS))
    assert [e["type"] for e in seen][:2] == ["thread.started", "turn.started"]
    events = (result.run_dir / "events.jsonl").read_text().splitlines()
    assert json.loads(events[0])["type"] == "thread.started"
    load_run_envelope(json.loads((result.run_dir / "review.json").read_text()))
    manifest = load_manifest(json.loads((result.run_dir / "manifest.json").read_text()))
    assert (manifest.arm, manifest.repeat, manifest.status) == ("plain", 0, "complete")
    observed = (manifest.model, manifest.effort, manifest.cli_version)
    assert observed == ("gpt-6-luna", "high", "0.160.0")


def test_prompt_asks_for_seven_parallel_subagents(run):
    result = run()
    prompt = (result.out_dir / "prompt.txt").read_text()
    assert "This is an explicit request for sub-agents and parallel agent work." in prompt
    assert "review-orchestrator" in prompt
    assert all(r in prompt for r in REVIEWERS)
    assert str(result.out_dir) in prompt


def test_empty_reviewer_list_is_still_complete(run):
    result = run("empty_one")
    assert outcomes(result)["security"] == "empty"
    assert result.status == "complete"
    assert len(result.findings) == 6


def test_missing_reviewer_file_is_not_run_and_partial(run):
    result = run("missing_one")
    assert outcomes(result)["tests"] == "not_run"
    assert result.status == "partial"


def test_malformed_reviewer_file_is_malformed_and_partial(run):
    result = run("malformed_one")
    assert outcomes(result)["correctness"] == "malformed"
    assert result.status == "partial"
    assert len(result.findings) == 6


def test_auth_error_with_no_files_fails_and_presents_no_findings(run):
    result = run("auth_fail")
    assert result.status == "failed"
    assert result.exit_code == 1
    assert result.findings == ()
    doc = json.loads((result.run_dir / "review.json").read_text())
    assert doc["envelope"]["status"] == "failed" and doc["findings"] == []
    assert "401" in (result.run_dir / "stderr.txt").read_text()


def test_rollout_reporting_another_model_fails_the_run(run):
    result = run("wrong_model")
    assert result.status == "failed"
    assert result.findings == ()
    assert any("model" in reason for reason in result.reasons)


def test_runner_without_permissions_is_refused_before_any_process_starts(
    run, write_registry, tmp_path
):
    marker = tmp_path / "started"
    registry = write_registry(permissions=False, marker=str(marker))
    with pytest.raises(RegistryError, match="permissions"):
        run(registry=registry)
    assert not marker.exists()


def test_envelope_records_the_sandbox_mode_the_run_used(run):
    assert run().document["envelope"]["sandbox_mode"] == "workspace-write"


def test_agent_stdin_is_closed(run):
    # The fake exits 5 when fd 0 is not /dev/null, so exit code 0 proves it was.
    assert run().exit_code == 0


def test_the_agents_own_final_file_changes_nothing(run):
    plain, junk = run(), run("final_file")
    env = junk.document["envelope"]
    observed = {k: env[k] for k in ("runner", "model", "effort", "cli_version", "sandbox_mode")}
    assert observed == {
        "runner": "fake", "model": "gpt-6-luna", "effort": "high",
        "cli_version": "0.160.0", "sandbox_mode": "workspace-write",
    }  # fmt: skip
    assert junk.document == plain.document
    assert set(env["dropped"].values()) == {0}


def test_run_past_the_wall_clock_limit_is_stopped_and_leaves_no_child(run):
    result = run("hang", timeout_sec=3)
    assert result.timed_out and result.status == "failed"
    pid = int((result.out_dir / "child.pid").read_text())
    for _ in range(40):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.05)
    pytest.fail(f"child {pid} is still alive")


def test_refs_that_name_no_commit_are_refused_before_anything_starts(run, write_registry, tmp_path):
    marker = tmp_path / "started"
    registry = write_registry(marker=str(marker))
    with pytest.raises(ValueError, match="commit"):
        run(registry=registry, head="no-such-ref")
    assert not marker.exists()


def test_findings_left_by_an_earlier_run_are_refused(run, workdir):
    out = workdir / ".review"
    out.mkdir()
    (out / "findings.security.json").write_text("{}")
    with pytest.raises(FileExistsError, match="findings"):
        run()


def _write_valid(out, reviewer):
    doc = {"schema_version": 1, "reviewer": reviewer, "findings": []}
    (out / f"findings.{reviewer}.json").write_text(json.dumps(doc))


def test_build_envelope_output_is_accepted_by_the_loader(tmp_path):
    for r in REVIEWERS[:3]:
        _write_valid(tmp_path, r)
    meta = {"runner": "x", "model": "m", "effort": "e", "cli_version": "1", "sandbox_mode": "s"}
    doc = build_envelope(tmp_path, REVIEWERS, meta)
    loaded = load_run_envelope(doc)
    assert loaded.envelope.status == "partial"
    assert doc["findings"] == [] and doc["envelope"]["dropped"]["duplicate"] == 0


def test_prompt_carries_the_slice_the_task_text_and_the_context_command_when_given(run):
    plain = (run().out_dir / "prompt.txt").read_text()
    assert not any(x in plain for x in ("Your slice is", "meant to do", "Context search"))
    result = run(
        slice_paths=["src/a (b)/x.py", "./app.py"], task_text="  Adds a thing.\nIt has parts.  ",
        context_command="ctx",
    )  # fmt: skip
    lines = (result.out_dir / "prompt.txt").read_text().splitlines()
    assert "Your slice is only these files: src/a (b)/x.py, app.py" in lines
    assert "What the change is meant to do: Adds a thing. It has parts." in lines
    assert "Context search command: ctx" in lines


@pytest.mark.parametrize("bad", [["../x.py"], ["a\nb.py"], []])
def test_a_slice_path_that_is_unsafe_or_an_empty_slice_is_refused_before_launch(run, bad):
    with pytest.raises(ValueError, match="slice"):
        run(slice_paths=bad)


def test_usage_file_records_tokens_per_session_and_the_allowance_reading(run):
    result = run("p1_validated")
    usage = json.loads((result.run_dir / "usage.json").read_text())
    assert set(usage["sessions"]) == {"main", "validator", *REVIEWERS}
    assert usage["sessions"]["main"]["input_tokens"] == 50  # the last running total, not a sum
    assert usage["total"]["input_tokens"] == 50 + 8 * 59
    assert usage["total"]["cached_input_tokens"] == 25 + 8 * 29
    assert usage["allowance"] == {"window_minutes": 10080, "used_percent_first": 41.0,
                                  "used_percent_last": 43.0, "plan_type": "pro"}  # fmt: skip


def test_manifest_records_a_hash_of_the_skills_the_agent_was_given(run, tmp_path):
    first = json.loads((run().run_dir / "manifest.json").read_text())["skills_hash"]
    again = json.loads((run().run_dir / "manifest.json").read_text())["skills_hash"]
    assert len(first) == 64 and first == again


def test_a_run_where_nothing_happens_any_more_is_stopped_and_its_reviews_kept(run):
    started = time.monotonic()
    result = run("stall", timeout_sec=120, idle_sec=2)
    assert time.monotonic() - started < 30
    assert not result.timed_out and result.status == "complete"
    assert outcomes(result) == dict.fromkeys(REVIEWERS, "ok")
    assert any("no activity" in reason for reason in result.reasons)


def test_a_quiet_main_agent_is_not_stopped_while_a_sub_agent_still_works(run):
    result = run("busy", timeout_sec=120, idle_sec=2)
    assert result.status == "complete" and result.exit_code == 0
    assert not any("no activity" in reason for reason in result.reasons)


def test_the_script_command_runs_the_named_python_on_the_runs_own_copy_of_the_script(run):
    # A login shell on a Mac finds the system python3 first, whatever the caller's path says, so
    # the command names the interpreter; and it runs the copy of the skills this run was given.
    import sys

    result = run()
    lines = (result.out_dir / "prompt.txt").read_text().splitlines()
    skills = result.run_dir / "home" / ".agents" / "skills"
    script = skills / "review-orchestrator" / "scripts" / "aggregate.py"
    assert f"The skills are installed in: {skills}" in lines
    wrapper = (result.run_dir / "bin" / "review-aggregate").read_text()
    assert f"exec {sys.executable} {script} " in wrapper.replace("'", "")


_REAL_STORES: dict = {}


def _toy_store(tmp_path, provider="vector"):
    """A folder that only declares itself a store: it has a manifest and answers nothing."""
    store = tmp_path / "store"
    store.mkdir()
    (store / "manifest.json").write_text(
        json.dumps({"provider": provider, "store_sha256": "a" * 64})
    )
    return store


def _store(tmp_path, provider="vector"):
    """A real small store of one arm, built once per session by the builder and copied here."""
    import contextlib
    import io
    import shutil
    from pathlib import Path

    from fake_agent import APP

    from review_core.context import build_stores

    root = tmp_path.parent / "launcher-stores"
    if root not in _REAL_STORES:
        slug, snaps = "tt-d01", root / "snaps"
        for tree, text in (("base", "pad 1\n"), ("head", APP)):
            (snaps / slug / tree).mkdir(parents=True)
            (snaps / slug / tree / "app.py").write_text(text)
        manifest = {"slug": slug, "slices": [{"id": f"{slug}-s01", "paths": ["app.py"]}]}
        (snaps / slug / "manifest.json").write_text(json.dumps(manifest))
        okf = Path(__file__).parents[1] / "context" / "fixtures" / "okf-bundle"
        built = {}
        for arm in ("vector", "okf"):
            argv = [
                "--case",
                slug,
                "--arm",
                arm,
                "--snapshots-dir",
                str(snaps),
                "--out",
                str(root / "stores"),
                "--cache-dir",
                str(root / "cache"),
                "--fake-embedder",
                *(["--okf-bundle", str(okf)] if arm == "okf" else []),
            ]
            seen = io.StringIO()
            with contextlib.redirect_stdout(seen), contextlib.redirect_stderr(seen):
                assert build_stores.main(argv) == 0, seen.getvalue()
            built[arm] = root / "stores" / slug / arm
        _REAL_STORES[root] = built
    return shutil.copytree(_REAL_STORES[root][provider], tmp_path / "store")


def _store_hash(store):
    return json.loads((store / "manifest.json").read_text())["store_sha256"]


def test_a_run_with_a_store_gets_a_search_command_and_records_its_arm(run, tmp_path):
    import subprocess

    store = _store(tmp_path)
    result = run(store=store)
    manifest = json.loads((result.run_dir / "manifest.json").read_text())
    assert (manifest["arm"], manifest["store_hash"]) == ("vector", _store_hash(store))
    wrapper = result.run_dir / "bin" / "ctx"
    lines = (result.out_dir / "prompt.txt").read_text().splitlines()
    line = next(x for x in lines if x.startswith("Context search command: "))
    # The reviewer is told the two verbs in words that name no kind of store.
    assert line.startswith("Context search command: ctx . ") and "related" in line
    assert not any(word in line.lower() for word in ("vector", "okf", "graph", "embedding", "note"))
    # The wrapper is the whole command: no flag for the reviewer to get wrong.
    assert os.access(wrapper, os.X_OK) and str(tmp_path / "store") in wrapper.read_text()
    done = subprocess.run(
        [str(wrapper), "search", "status"], capture_output=True, text=True, check=False
    )
    assert done.returncode == 0 and done.stdout  # the store answers through the wrapper


def test_a_run_without_a_store_is_the_plain_arm_and_has_no_command(run):
    result = run()
    manifest = json.loads((result.run_dir / "manifest.json").read_text())
    assert (manifest["arm"], manifest["store_hash"]) == ("plain", None)
    assert not (result.run_dir / "bin" / "ctx").exists()
    assert "Context search command" not in (result.out_dir / "prompt.txt").read_text()


@pytest.mark.parametrize("bad", ["none", "plain", "../x", 7])
def test_a_store_naming_no_real_arm_is_refused_before_launch(run, tmp_path, bad):
    with pytest.raises(ValueError, match="store"):
        run(store=_toy_store(tmp_path, provider=bad))


def test_the_search_wrapper_cannot_be_steered_by_the_project_it_runs_in(run, tmp_path):
    # ctx runs with the reviewed project as its folder. A module planted there must not load.
    import subprocess

    result = run(store=_store(tmp_path), env_file=tmp_path / "keys.env")
    text = (result.run_dir / "bin" / "ctx").read_text()
    assert " -P " in text and "set -a" not in text and "--store" not in text
    assert f"CTX_STORE={tmp_path / 'store'}" in text.replace("'", "")
    planted = tmp_path / "project"
    (planted / "review_core").mkdir(parents=True)
    (planted / "review_core" / "__init__.py").write_text("raise SystemExit(99)\n")
    (planted / "json.py").write_text("raise SystemExit(98)\n")
    done = subprocess.run(
        [str(result.run_dir / "bin" / "ctx"), "search", "x"], cwd=planted, capture_output=True,
        text=True, env={"PATH": os.environ["PATH"], "PYTHONPATH": str(planted)}, check=False,
    )  # fmt: skip
    assert done.returncode == 0 and done.stdout  # our ctx ran; neither planted module loaded


def test_the_wrapper_pins_the_log_and_the_key_file_against_the_callers_environment(run, tmp_path):
    # The reviewer starts the wrapper, so anything left to its environment is the reviewer's.
    import subprocess

    result = run(store=_store(tmp_path))
    wrapper = result.run_dir / "bin" / "ctx"
    text = wrapper.read_text()
    log = result.out_dir / "ctx-log.jsonl"
    assert f"CTX_LOG={log}" in text.replace("'", "") and "unset CTX_ENV_FILE" in text
    elsewhere, planted = tmp_path / "elsewhere.jsonl", tmp_path / "planted.env"
    planted.write_text("OPENAI_API_KEY=planted\n")
    env = {"PATH": os.environ["PATH"], "CTX_LOG": str(elsewhere), "CTX_ENV_FILE": str(planted)}
    env["CTX_STORE"] = str(tmp_path / "another-store")
    done = subprocess.run(
        [str(wrapper), "search", "x"], cwd=tmp_path, env=env, capture_output=True, text=True,
        check=False,
    )  # fmt: skip
    assert done.returncode == 0 and not elsewhere.exists()
    rows = [json.loads(line) for line in log.read_text().splitlines()]
    # The pinned store answered, and the one row is this call: the pre-start check is not logged.
    assert len(rows) == 1 and rows[0]["store_sha256"] == _store_hash(tmp_path / "store")
    assert not (tmp_path / ".review").exists()


def test_the_wrapper_names_a_scratch_folder_the_agent_may_write_and_the_run_keeps_a_record(
    run, tmp_path
):
    # The vector database needs scratch space even to read; the sandbox denies the ambient one.
    result = run(store=_store(tmp_path))
    text = (result.run_dir / "bin" / "ctx").read_text().replace("'", "")
    assert f"CONTEXT_ENGINE_SCRATCH={result.out_dir / 'ctx-scratch'}" in text
    # No reviewer called the command in this fake run, and the record says so.
    record = json.loads((result.run_dir / "ctx.json").read_text())
    check = record.pop("check")
    assert record == {"log": "missing", "calls": 0, "failed": 0, "degraded": 0, "empty": 0}
    assert check.startswith("ctx check: ok (search ") and "related" in check


def test_the_launcher_deletes_nothing_in_the_folder_the_agent_could_write(tmp_path):
    # It runs outside the sandbox. A link planted where the scratch folder was must not turn
    # its clean-up into a delete somewhere else, so it has no clean-up: ctx removes its own.
    from review_core.launcher.run import _close_ctx

    out, run_dir, elsewhere = tmp_path / "out", tmp_path / "run", tmp_path / "elsewhere"
    for folder in (out, run_dir, elsewhere / "keep"):
        folder.mkdir(parents=True)
    (elsewhere / "keep" / "file.txt").write_text("x")
    (out / "ctx-scratch").symlink_to(elsewhere, target_is_directory=True)
    _close_ctx(run_dir, out)
    assert (elsewhere / "keep" / "file.txt").read_text() == "x"
    assert (out / "ctx-scratch").is_symlink()


def test_the_search_record_counts_failed_degraded_and_empty_calls(tmp_path):
    from review_core.launcher.run import summarise_ctx_log

    log = tmp_path / "ctx-log.jsonl"
    rows = [
        {"exit_code": 0, "degraded": False, "item_ids": ["a"]},
        {"exit_code": 1, "degraded": False, "item_ids": []},
        {"exit_code": 0, "degraded": True, "item_ids": ["a"]},
        {"exit_code": 0, "degraded": False, "item_ids": []},
    ]
    log.write_text("".join(json.dumps(r) + "\n" for r in rows) + "not json\n")
    assert summarise_ctx_log(log) == {
        "log": "read", "calls": 5, "failed": 2, "degraded": 1, "empty": 1,
    }  # fmt: skip
    assert summarise_ctx_log(tmp_path / "missing.jsonl")["log"] == "missing"


def test_a_log_that_cannot_be_trusted_to_parse_is_reported_and_never_raises(tmp_path, monkeypatch):
    # The log sits where the agent writes. Whatever is in it, the run must still be recorded,
    # and a log that could not be read must not look like a run with no failed calls.
    from review_core.launcher import render as run_module

    nested = tmp_path / "nested.jsonl"
    nested.write_text("[" * 200_000 + "\n" + '"text"\n' + "[1]\n" + '{"exit_code": "x"}\n')
    assert run_module.summarise_ctx_log(nested) == {
        "log": "read", "calls": 4, "failed": 4, "degraded": 0, "empty": 0,
    }  # fmt: skip
    link = tmp_path / "link.jsonl"
    link.symlink_to(nested)
    assert run_module.summarise_ctx_log(link)["log"] == "unreadable"
    folder = tmp_path / "folder.jsonl"
    folder.mkdir()
    assert run_module.summarise_ctx_log(folder)["log"] == "unreadable"
    monkeypatch.setattr(run_module, "MAX_CTX_LOG_BYTES", 10)
    assert run_module.summarise_ctx_log(nested)["log"] == "unreadable"


def test_the_log_is_checked_and_read_through_one_open_file(tmp_path, monkeypatch):
    # Checking the path and then opening it leaves a gap in which the file can be swapped for
    # a link or grown past the limit. Here the path looked fine when checked and is a link now.
    from review_core.launcher import render as run_module

    small, big = tmp_path / "small.jsonl", tmp_path / "big.jsonl"
    small.write_text('{"exit_code": 0, "degraded": false, "item_ids": ["a"]}\n')
    big.write_text('{"exit_code": 0, "degraded": false, "item_ids": ["a"]}\n' * 50)
    looked_fine = os.lstat(small)
    log = tmp_path / "ctx-log.jsonl"
    log.symlink_to(big)
    monkeypatch.setattr(run_module.os, "lstat", lambda path: looked_fine)
    assert run_module.summarise_ctx_log(log) == {
        "log": "unreadable", "calls": 0, "failed": 0, "degraded": 0, "empty": 0,
    }  # fmt: skip
    # A file that grows after the check is still cut off at the limit and reported.
    monkeypatch.setattr(run_module, "MAX_CTX_LOG_BYTES", 100)
    assert run_module.summarise_ctx_log(big)["log"] == "unreadable"


def test_the_agent_is_given_short_command_names_and_never_a_long_path_to_type(run, tmp_path):
    # A real run typed the 150-character path of the script wrongly on its second use, twice in
    # two days. Nothing the agent must type is a path now: two names on its PATH.
    import subprocess

    from review_core.cli import DEFAULT_SKILLS

    result = run(store=_store(tmp_path), skills_dir=DEFAULT_SKILLS)  # the real plugin's skills
    prompt = (result.out_dir / "prompt.txt").read_text()
    assert "Run the skill's script with exactly this command: review-aggregate\n" in prompt
    assert "aggregate.py" not in prompt
    line = next(x for x in prompt.splitlines() if x.startswith("Context search command: "))
    assert line.startswith("Context search command: ctx . Run `ctx search ")
    bin_dir = result.run_dir / "bin"
    assert sorted(p.name for p in bin_dir.iterdir()) == ["ctx", "review-aggregate"]
    # The agent's PATH starts with that folder, and the names work from any folder.
    assert json.loads((result.out_dir / "path.json").read_text())[0] == str(bin_dir)
    env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
    done = subprocess.run(
        ["review-aggregate", "finalize", "--help"], cwd=tmp_path, env=env, capture_output=True,
        text=True, check=False,
    )  # fmt: skip
    assert done.returncode == 0 and "--out" in done.stdout
    done = subprocess.run(
        ["ctx", "search", "x"], cwd=tmp_path, env=env, capture_output=True, text=True,
        check=False,
    )  # fmt: skip
    assert done.returncode == 0 and done.stdout  # ours ran, by name


def test_a_run_without_a_store_has_the_script_command_and_no_search_command(run):
    result = run()
    assert [p.name for p in (result.run_dir / "bin").iterdir()] == ["review-aggregate"]


def test_the_run_keeps_a_report_made_from_the_launchers_own_result(run, workdir):
    # The agent's report.md is built from the agent's own aggregate. The run folder's report is
    # rendered from the result the launcher rebuilt, with the agent's summary as its only prose.
    out = workdir / ".review"
    out.mkdir()
    (out / "pr-summary.md").write_text("This change adds a retry to the uploader.\n")
    (out / "report.md").write_text("# A report the agent wrote itself\n")
    result = run()
    report = (result.run_dir / "report.md").read_text()
    assert report.startswith("# Code review report\n")
    assert "This change adds a retry to the uploader." in report
    assert "A report the agent wrote itself" not in report
    assert result.findings
    for finding in result.findings:
        assert f"{finding.file}:{finding.line_start}" in report


def test_a_summary_that_is_a_link_or_missing_leaves_the_report_without_one(run, workdir, tmp_path):
    secret = tmp_path / "elsewhere.txt"
    secret.write_text("text from outside the review folder\n")
    out = workdir / ".review"
    out.mkdir()
    (out / "pr-summary.md").symlink_to(secret)
    report = (run().run_dir / "report.md").read_text()
    assert "text from outside" not in report and "## What this change does" in report


def test_a_store_that_fails_its_check_starts_no_agent(run, tmp_path, workdir):
    # The store is built and checked before the agent, never by it. A store that cannot answer
    # stops the run here: an agent started against it would be a run of no arm.
    from review_core.launcher.run import StoreCheckError

    with pytest.raises(StoreCheckError, match="did not pass its check, so no agent was started"):
        run(store=_toy_store(tmp_path))
    out = workdir / ".review"
    assert not (out / "path.json").exists() and not (out / "prompt.txt").exists()
    (run_dir,) = (tmp_path / "runs").iterdir()
    assert not (run_dir / "manifest.json").exists() and not (run_dir / "events.jsonl").exists()


def test_a_store_that_passes_its_check_is_recorded_and_the_agent_runs(run, tmp_path):
    result = run(store=_store(tmp_path))
    record = json.loads((result.run_dir / "ctx.json").read_text())
    assert record["check"].startswith("ctx check: ok (search ") and "pack" not in record
    assert (result.out_dir / "path.json").exists()  # the agent ran


def test_a_changed_file_named_like_a_flag_is_never_handed_to_the_store_check(tmp_path):
    # File names come from the project under review. One named `--help` made the check print
    # its usage and exit 0, so a store that was never checked counted as passed.
    from review_core.launcher.run import _changed_path

    assert _changed_path(tmp_path, "a", "b", ["--help", "-x.py", "b.py", "a/c.py"]) == "a/c.py"
    assert _changed_path(tmp_path, "a", "b", ["--help", "-h"]) == ""


def test_the_store_check_passes_only_on_its_own_ok_line(tmp_path):
    from review_core.launcher.run import StoreCheckError, _check_store

    def wrapper(text):
        path = tmp_path / "ctx"
        path.write_text(f"#!/bin/sh\n{text}\n")
        path.chmod(0o755)
        return path

    line = "ctx check: ok (search 3 items)"
    assert _check_store(wrapper(f"echo '{line}'"), tmp_path, "") == line
    # Exit 0 is not enough: usage text, silence, or the line after other output all fail.
    for said in ("echo 'usage: ctx [-h]'", "true", f"echo noise; echo '{line}'"):
        with pytest.raises(StoreCheckError, match="did not pass its check"):
            _check_store(wrapper(said), tmp_path, "")
    with pytest.raises(StoreCheckError):
        _check_store(wrapper(f"echo '{line}'; exit 3"), tmp_path, "")


def test_each_arm_is_told_its_own_way_of_gathering_context(run, tmp_path, monkeypatch, notes):
    # The three kinds of review differ in how a reviewer gathers context, and each is told its
    # own way: the plain arm from the `none` row, the others from their own provider rows.
    import dataclasses

    from review_core.context import providers
    from review_core.launcher import run as launcher

    real = providers.load_registry()
    said = {"none": "Read the code around the change.", "vector": "Search the database first."}
    rows = {
        name: dataclasses.replace(row, method=said.get(name, ""))
        for name, row in real.providers.items()
    }
    monkeypatch.setattr(
        launcher, "load_providers", lambda: dataclasses.replace(real, providers=rows)
    )

    def method_line(result):
        lines = (result.out_dir / "prompt.txt").read_text().splitlines()
        return [x for x in lines if x.startswith("How to gather context: ")]

    assert method_line(run()) == ["How to gather context: Read the code around the change."]
    assert method_line(run(store=_store(tmp_path))) == [
        "How to gather context: Search the database first."
    ]
    # An arm whose row has no method gets no such line.
    assert method_line(run(arm="okf")) == []


def test_a_vector_run_gives_reviewers_the_search_command_and_writes_no_context_file(run, tmp_path):
    # The reviewers search the database themselves. Nothing is gathered for them beforehand.
    result = run(store=_store(tmp_path))
    prompt = (result.out_dir / "prompt.txt").read_text()
    assert "Context search command: ctx . " in prompt
    assert sorted(p.name for p in (result.run_dir / "bin").iterdir()) == ["ctx", "review-aggregate"]
    # The method the reviewer reads names the two verbs and no file.
    (method,) = [x for x in prompt.splitlines() if x.startswith("How to gather context: ")]
    assert 'search "<words>"' in method and "related <path>" in method
    assert "context.md" not in prompt
    assert not list(result.out_dir.rglob("context.md")) and not list(
        result.run_dir.rglob("context.md")
    )
    # The fake agent looked for the file when it started and found none.
    assert json.loads((result.out_dir / "context_seen.json").read_text()) is False
    record = json.loads((result.run_dir / "ctx.json").read_text())
    assert "pack" not in record and record["calls"] == 0


def test_an_okf_run_with_notes_has_no_store_and_no_command_and_the_okf_method(run, notes):
    from review_core.context.providers import load_registry

    result = run(arm="okf")
    manifest = json.loads((result.run_dir / "manifest.json").read_text())
    assert (manifest["arm"], manifest["store_hash"]) == ("okf", None)
    prompt = (result.out_dir / "prompt.txt").read_text()
    assert "Context search command" not in prompt and "context.md" not in prompt
    method = " ".join(load_registry().providers["okf"].method.split())
    assert f"How to gather context: {method}" in prompt.splitlines()
    assert "`okf/`" in method and "README.md" in method
    # No command was made for the run, on the PATH or anywhere else in its folder.
    assert [p.name for p in (result.run_dir / "bin").iterdir()] == ["review-aggregate"]
    assert not list(result.run_dir.rglob("ctx")) and not (result.run_dir / "ctx.json").exists()
    assert not list(result.out_dir.rglob("context.md"))


def test_an_okf_run_without_notes_is_refused_before_anything_starts(run, tmp_path, workdir):
    with pytest.raises(ValueError, match=r"okf/"):
        run(arm="okf")
    assert not (workdir / ".review").exists()
    assert not (tmp_path / "runs").exists()  # no run folder was made either
    # A link in place of the folder is not a folder of notes.
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (workdir / "okf").symlink_to(elsewhere, target_is_directory=True)
    with pytest.raises(ValueError, match=r"okf/"):
        run(arm="okf")


@pytest.mark.parametrize("arm", ["vector", "bogus", 7])
def test_an_arm_that_needs_a_store_or_is_unknown_is_refused_without_one(run, arm):
    with pytest.raises(ValueError, match="arm"):
        run(arm=arm)


def test_an_arm_that_disagrees_with_the_store_is_refused(run, tmp_path):
    with pytest.raises(ValueError, match="arm"):
        run(store=_store(tmp_path), arm="okf")


def test_a_store_still_decides_the_kind_when_the_arm_agrees(run, tmp_path):
    result = run(store=_store(tmp_path), arm="vector")
    assert json.loads((result.run_dir / "manifest.json").read_text())["arm"] == "vector"


def test_a_plain_run_may_name_its_arm(run):
    result = run(arm="plain")
    assert json.loads((result.run_dir / "manifest.json").read_text())["arm"] == "plain"


FIRST = "Review the changes between git refs base and head in the repository "


def test_without_start_in_the_agent_starts_in_the_repository_and_the_prompt_is_unchanged(
    run, workdir
):
    result = run()
    prompt = (result.out_dir / "prompt.txt").read_text()
    assert prompt.splitlines()[0] == FIRST + "in the current directory."
    assert json.loads((result.out_dir / "cwd.json").read_text()) == os.path.realpath(workdir)
    # Naming the repository itself as the start folder changes nothing.
    again = run(start_in=workdir)
    same = (again.out_dir / "prompt.txt").read_text()
    swap = {str(result.out_dir): str(again.out_dir), result.run_id: again.run_id}
    for old, new in swap.items():
        prompt = prompt.replace(old, new)
    assert same == prompt


def test_an_agent_started_above_the_repository_is_told_where_it_is(run, workdir, tmp_path):
    start = tmp_path / "case"
    start.mkdir()
    repo = start / "project"
    workdir.rename(repo)
    (start / "change.diff").write_text("the change\n")
    out = start / "findings"
    result = run(start_in=start, out_dir=out, workdir=repo)
    assert result.status != "failed" and result.out_dir == out.resolve()
    assert json.loads((out / "cwd.json").read_text()) == os.path.realpath(start)
    lines = (out / "prompt.txt").read_text().splitlines()
    assert lines[0] == FIRST + "in the folder `project`."
    assert "The change is also in the file `change.diff` in the current directory." in lines
    assert (out / "findings.security.json").exists()  # the aggregator read what landed there


def test_the_start_folder_names_the_repository_relative_to_itself_when_it_is_deeper(
    run, workdir, tmp_path
):
    start = tmp_path / "case"
    (start / "a").mkdir(parents=True)
    repo = start / "a" / "project"
    workdir.rename(repo)
    result = run(start_in=start, out_dir=start / "out", workdir=repo)
    first = (result.out_dir / "prompt.txt").read_text().splitlines()[0]
    assert first == FIRST + "in the folder `a/project`."
    assert not any(
        "change.diff" in x for x in (result.out_dir / "prompt.txt").read_text().splitlines()
    )


@pytest.mark.parametrize("where", ["elsewhere", "inside", "missing"])
def test_a_start_folder_that_does_not_contain_the_repository_is_refused(
    run, workdir, tmp_path, where
):
    start = {
        "elsewhere": tmp_path / "other",
        "inside": workdir / "sub",
        "missing": tmp_path / "no",
    }[where]
    if where != "missing":
        start.mkdir()
    with pytest.raises(ValueError, match="start_in"):
        run(start_in=start)
    assert not (tmp_path / "runs").exists() and not (workdir / ".review").exists()
