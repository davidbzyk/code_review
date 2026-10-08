"""An untrusted store, the call log, and concurrent callers."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

import pytest
from ctx_helpers import REPO, read_log, run_ctx


def copy_store(src, dst):
    shutil.copytree(src, dst)
    return dst


def set_manifest(store, **fields):
    path = store / "manifest.json"
    data = json.loads(path.read_text())
    data.update(fields)
    path.write_text(json.dumps(data))


@pytest.mark.parametrize(
    "provider", ["nope", "none", "os:system", "review_core.context.okf_search", "../okf", 7, None]
)
def test_a_manifest_naming_an_unknown_provider_or_a_module_path_is_refused(
    okf_store, tmp_path, provider
):
    store = copy_store(okf_store, tmp_path / "s")
    set_manifest(store, provider=provider)
    code, out, err = run_ctx(store, "--log", tmp_path / "l", "search", "totals")
    assert code == 2 and out == ""
    assert len(err.strip().splitlines()) == 1 and err.startswith("ctx: ")


def test_extra_manifest_keys_naming_code_are_never_used(okf_store, tmp_path):
    store = copy_store(okf_store, tmp_path / "s")
    set_manifest(
        store,
        search="os:system",
        related="os:system",
        command="touch pwned",
        module="os",
        address="http://127.0.0.1:9",
    )
    code, out, _ = run_ctx(store, "--log", tmp_path / "l", "search", "order totals")
    assert code == 0 and "note building-blocks/orders" in out
    assert not (tmp_path / "pwned").exists()


@pytest.mark.parametrize("break_it", ["missing", "malformed", "not_object", "empty_dir"])
def test_a_missing_or_malformed_store_is_a_one_line_error_with_exit_2(
    okf_store, tmp_path, break_it
):
    store = copy_store(okf_store, tmp_path / "s")
    if break_it == "missing":
        shutil.rmtree(store)
    elif break_it == "malformed":
        (store / "manifest.json").write_text("{not json")
    elif break_it == "not_object":
        (store / "manifest.json").write_text("[1]")
    else:
        shutil.rmtree(store)
        store.mkdir()
    code, out, err = run_ctx(store, "--log", tmp_path / "l", "search", "x")
    assert code == 2 and out == ""
    assert len(err.strip().splitlines()) == 1
    assert read_log(tmp_path / "l")[0]["exit_code"] == 2


def test_a_symbolic_link_inside_a_store_is_refused(okf_store, tmp_path):
    store = copy_store(okf_store, tmp_path / "s")
    os.symlink("/etc/hosts", store / "bundle" / "link.md")
    code, _, err = run_ctx(store, "--log", tmp_path / "l", "search", "totals")
    assert code == 2 and "symbolic link" in err


@pytest.mark.parametrize(
    "plant",
    [
        "scripts/okf_retrieve.py",
        "bundle/okf_common.py",
        "okf_graphify.py",
        "bundle/run.sh",
        "bundle/x.txt",
        "extra.md",
        "bundle/data.PY",
    ],
)
def test_a_store_with_code_or_unexpected_files_is_refused_and_never_imported(
    okf_store, tmp_path, plant
):
    store = copy_store(okf_store, tmp_path / "s")
    marker = tmp_path / "ran"
    target = store / plant
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"open({str(marker)!r}, 'w').close()\nraise RuntimeError('imported')\n")
    code, out, err = run_ctx(store, "--log", tmp_path / "l", "search", "order totals")
    assert code == 2 and out == "" and len(err.strip().splitlines()) == 1
    assert not marker.exists()
    code, _, _ = run_ctx(store, "--log", tmp_path / "l", "related", "src/orders.py")
    assert code == 2 and not marker.exists()


def test_a_provider_that_raises_is_exit_1_one_line_and_still_logged(okf_store, tmp_path):
    store = copy_store(okf_store, tmp_path / "s")
    (store / "bundle" / "okf.config.json").write_text("{not json")
    log = tmp_path / "l"
    code, out, err = run_ctx(store, "--log", log, "related", "src/orders.py")
    assert code == 1 and out == "" and len(err.strip().splitlines()) == 1
    (rec,) = read_log(log)
    assert rec["exit_code"] == 1 and rec["provider"] == "okf"


def test_every_call_is_logged_with_the_listed_fields(okf_store, tmp_path):
    log = tmp_path / "deep" / ".review" / "ctx-log.jsonl"
    run_ctx(okf_store, "--log", log, "search", "order totals")
    run_ctx(okf_store, "--log", log, "related", "src/orders.py")
    first, second = read_log(log)
    manifest = json.loads((okf_store / "manifest.json").read_text())
    for rec, verb, arg in ((first, "search", "order totals"), (second, "related", "src/orders.py")):
        assert set(rec) >= {
            "ts",
            "verb",
            "argument",
            "provider",
            "store_sha256",
            "item_ids",
            "tokens",
            "degraded",
            "reason",
            "exit_code",
            "duration_ms",
        }
        assert rec["verb"] == verb and rec["argument"] == arg and rec["provider"] == "okf"
        assert rec["store_sha256"] == manifest["store_sha256"] and rec["exit_code"] == 0
        assert rec["tokens"] > 0 and rec["item_ids"] and rec["duration_ms"] >= 0
        assert rec["ts"].endswith("Z")


def test_the_default_log_is_review_ctx_log_in_the_working_directory(
    okf_store, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    run_ctx(okf_store, "search", "order totals")
    assert len(read_log(tmp_path / ".review" / "ctx-log.jsonl")) == 1


def test_concurrent_callers_leave_only_whole_lines(okf_store, tmp_path):
    log = tmp_path / "ctx.jsonl"
    env = dict(os.environ, PYTHONPATH=f"{REPO / 'src'}")
    cmds = [
        [
            sys.executable,
            "-m",
            "review_core.context.ctx",
            "--store",
            str(okf_store),
            "--log",
            str(log),
            "search",
            f"order totals {n}",
        ]
        for n in range(8)
    ]
    procs = [
        subprocess.Popen(c, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for c in cmds
    ]
    for p in procs:
        p.communicate(timeout=60)
        assert p.returncode == 0
    records = read_log(log)  # every line parses
    assert len(records) == 8
    assert sorted(r["argument"] for r in records) == sorted(f"order totals {n}" for n in range(8))


def test_the_log_is_never_written_through_a_link(tmp_path):
    # A project under review can ship a `.review` folder or a log file that is a link.
    import os

    from review_core.context.ctx import _append_log

    target = tmp_path / "victim.txt"
    target.write_text("keep\n")
    by_file = tmp_path / "a" / "ctx-log.jsonl"
    by_file.parent.mkdir()
    by_file.symlink_to(target)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    by_folder = tmp_path / "b" / ".review"
    by_folder.parent.mkdir()
    by_folder.symlink_to(elsewhere, target_is_directory=True)
    for path in (by_file, by_folder / "ctx-log.jsonl"):
        try:
            _append_log(path, {"verb": "search"})
        except OSError:
            pass
        else:
            raise AssertionError(f"wrote through a link at {path}")
    assert target.read_text() == "keep\n" and os.listdir(elsewhere) == []


def test_the_log_is_a_plain_file_in_a_real_folder_and_appends(tmp_path):
    from review_core.context.ctx import _append_log

    path = tmp_path / ".review" / "ctx-log.jsonl"
    _append_log(path, {"n": 1})
    _append_log(path, {"n": 2})
    assert [json.loads(line)["n"] for line in path.read_text().splitlines()] == [1, 2]


def test_a_pinned_store_cannot_be_replaced_from_the_command_line(
    vector_store, tmp_path, monkeypatch
):
    # The launcher's wrapper pins the store; a reviewer adding its own flag must not move it.
    other = tmp_path / "other-store"
    monkeypatch.setenv("CTX_STORE", str(vector_store))
    monkeypatch.setenv("CTX_LOG", str(tmp_path / "pinned.jsonl"))
    for extra in (["--store", str(other)], ["--log", str(tmp_path / "mine.jsonl")]):
        code, out, err = run_ctx(None, "search", "anything", *extra)
        assert code == 2 and "pinned" in err and out == ""
    code, out, _ = run_ctx(None, "search", "anything")
    assert code == 0 and out
    assert not (tmp_path / "mine.jsonl").exists()
    assert len(read_log(tmp_path / "pinned.jsonl")) == 3  # refused calls are logged too


def test_only_the_embedder_key_is_taken_from_the_env_file(tmp_path, monkeypatch):
    from review_core.context.ctx import key_from_env_file

    env_file = tmp_path / ".env"
    env_file.write_text(
        'OTHER_SECRET=nope\n# comment\nexport OPENAI_API_KEY="sk-from-file"\nPATH=/evil\n'
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("PATH", "/usr/bin")
    key_from_env_file(env_file)
    assert os.environ["OPENAI_API_KEY"] == "sk-from-file"
    assert "OTHER_SECRET" not in os.environ and os.environ["PATH"] == "/usr/bin"
    monkeypatch.setenv("OPENAI_API_KEY", "already-set")
    key_from_env_file(env_file)
    assert os.environ["OPENAI_API_KEY"] == "already-set"
    key_from_env_file(tmp_path / "missing.env")  # a missing file is not an error here
