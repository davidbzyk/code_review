"""Registry loading and the codex_rollout metadata parser."""

import json
from datetime import datetime

import pytest

from review_core.launcher.rollout import parse_codex_rollout
from review_core.launcher.runners import RegistryError, load_registry

ROOT = "01a10e3d-a734-7602-ac54-171fcffa137e"


def test_packaged_codex_entry_follows_the_probe_record():
    entry = load_registry()["codex"]
    assert entry.argv[:3] == ["codex", "exec", "--json"]
    assert "--ignore-user-config" in entry.argv
    assert entry.stdin == "closed"
    assert entry.metadata == "codex_rollout"
    assert entry.permissions.sandbox == "workspace-write"
    assert entry.permissions.writable_roots == ["{workdir}"]
    assert entry.permissions.network is False
    assert entry.env["HOME"].startswith("{home}") and entry.env["CODEX_HOME"] == "{codex_home}"
    assert entry.skills_copy_to == "{home}/.agents/skills"


def test_entry_without_permissions_is_refused(write_registry):
    with pytest.raises(RegistryError, match="permissions"):
        load_registry(write_registry(permissions=False))


def _day(tmp_path):
    now = datetime.now()
    day = tmp_path / "sessions" / f"{now:%Y}" / f"{now:%m}" / f"{now:%d}"
    day.mkdir(parents=True)
    return day


def _line(**payload):
    return json.dumps({"type": "session_meta", "payload": payload}) + "\n"


def test_codex_rollout_reads_model_effort_version_and_subagents(tmp_path):
    day = _day(tmp_path)
    context = {
        "model": "gpt-6-luna",
        "effort": "high",
        "sandbox_policy": {"type": "workspace-write"},
    }
    (day / f"rollout-2026-10-05T18-44-44-{ROOT}.jsonl").write_text(
        _line(id=ROOT, cli_version="0.160.0", source="exec")
        + json.dumps({"type": "turn_context", "payload": context})
        + "\n"
    )
    for name in ("tests", "security"):
        (day / f"rollout-2026-10-05T18-44-59-child-{name}.jsonl").write_text(
            _line(
                id=f"c-{name}",
                parent_thread_id=ROOT,
                cli_version="0.160.0",
                agent_path=f"/root/{name}",
            )  # fmt: skip
        )
    (day / "rollout-2026-10-05T18-45-00-other.jsonl").write_text(
        _line(id="o", parent_thread_id="someone-else", agent_path="/root/language")
    )
    events = [{"type": "thread.started", "thread_id": ROOT}, {"type": "turn.started"}]
    meta = parse_codex_rollout(events, {"CODEX_HOME": str(tmp_path)})
    assert (meta.model, meta.effort, meta.cli_version, meta.sandbox) == (
        "gpt-6-luna", "high", "0.160.0", "workspace-write",
    )  # fmt: skip
    assert meta.subagents == ("security", "tests")


def test_codex_rollout_is_none_without_a_rollout(tmp_path):
    events = [{"type": "thread.started", "thread_id": ROOT}]
    assert parse_codex_rollout(events, {"CODEX_HOME": str(tmp_path)}) is None
    assert parse_codex_rollout([], {"CODEX_HOME": str(tmp_path)}) is None


def test_a_row_lets_commands_reach_the_network_only_when_it_says_so():
    # On a developer's machine the vector arm's search must reach the embedding service, and
    # every arm of a comparison then runs with the same access. The permission is a row's own
    # statement, and it must agree with the command line the row gives Codex.
    registry = load_registry()
    flag = "sandbox_workspace_write.network_access=true"
    for name in ("codex", "codex-net"):
        entry = registry[name]
        assert entry.permissions.network == (flag in entry.argv), name
    assert registry["codex-net"].permissions.network and not registry["codex"].permissions.network
    same = [a for a in registry["codex-net"].argv if a not in ("-c", flag)]
    assert same == [a for a in registry["codex"].argv if a != "-c"]
