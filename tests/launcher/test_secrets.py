"""An agent entry that runs on a key: where the key is looked up, and where it must never land."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from review_core.launcher import team as team_mod
from review_core.launcher.runners import RegistryError, load_registry

PACKAGED = Path(__file__).resolve().parents[2] / "src" / "plugin" / "skills"
KEY = "sk-test-0123456789-not-a-real-key"
SECRETS = {"AGENT_KEY": "SOURCE_KEY"}


def everything_written(root: Path) -> str:
    """The text of every file under a folder, to search for a value that must not be there."""
    return "\n".join(p.read_text(errors="replace") for p in root.rglob("*") if p.is_file())


def test_the_key_reaches_the_agent_under_the_name_its_entry_gives(run, write_registry, monkeypatch):
    monkeypatch.setenv("SOURCE_KEY", KEY)
    result = run("env_probe", registry=write_registry(scenario="env_probe", secrets=SECRETS))
    names = json.loads((result.out_dir / "env.json").read_text())
    assert "AGENT_KEY" in names and "SOURCE_KEY" not in names
    assert result.status == "complete"


def test_the_key_is_read_from_the_env_file_when_the_caller_does_not_hold_it(
    run, write_registry, tmp_path, monkeypatch
):
    monkeypatch.delenv("SOURCE_KEY", raising=False)
    env_file = tmp_path / "keys.env"
    env_file.write_text(f'OTHER=1\nexport SOURCE_KEY="{KEY}"\n')
    registry = write_registry(scenario="env_probe", secrets=SECRETS)
    result = run("env_probe", registry=registry, env_file=env_file)
    assert "AGENT_KEY" in json.loads((result.out_dir / "env.json").read_text())


def test_the_key_is_written_nowhere(run, write_registry, tmp_path, monkeypatch):
    monkeypatch.setenv("SOURCE_KEY", KEY)
    result = run(registry=write_registry(secrets=SECRETS))
    assert KEY not in everything_written(result.run_dir)
    assert KEY not in everything_written(result.out_dir)


def test_a_run_without_its_key_starts_no_agent(run, write_registry, tmp_path, monkeypatch):
    monkeypatch.delenv("SOURCE_KEY", raising=False)
    marker = tmp_path / "started"
    registry = write_registry(secrets=SECRETS, marker=str(marker))
    with pytest.raises(RegistryError, match="SOURCE_KEY"):
        run(registry=registry, env_file=tmp_path / "missing.env")
    assert not marker.exists()


def test_each_separate_agent_gets_the_key_and_its_own_session_folder(
    run, write_registry, tmp_path, monkeypatch
):
    monkeypatch.setenv("SOURCE_KEY", KEY)
    skills = tmp_path / "team-skills"
    shutil.copytree(PACKAGED / "review-orchestrator", skills / "review-orchestrator")
    for skill in team_mod.read_team(skills).reviewers.values():
        (skills / skill).mkdir()
    registry = (
        write_registry(secrets=SECRETS)
        .read_text()
        .replace('CODEX_HOME = "{codex_home}"', 'CODEX_HOME = "{home}/.codex"')
        .replace('stdin = "closed"', 'stdin = "closed"\nmake_dirs = ["{home}/.codex"]')
    )
    path = tmp_path / "own-home.toml"
    path.write_text(registry)
    result = run(registry=path, team="separate", skills_dir=skills, reviewers=["security", "tests"])
    assert result.status == "complete" and len(result.findings) == 2
    homes = set()
    for name in ("security", "tests"):
        seen = json.loads((result.out_dir / f"seen.{name}.json").read_text())
        assert "AGENT_KEY" in seen["env"]
        homes.add(seen["codex_home"])
        assert seen["codex_home"].endswith(f"agents/{name}/home/.codex")
    assert len(homes) == 2 and KEY not in everything_written(result.run_dir)


def test_the_packaged_key_entry_hides_the_key_from_the_commands_an_agent_runs():
    entry = load_registry()["codex-key"]
    assert entry.secrets == {"CODEX_API_KEY": "OPENAI_API_KEY"}
    assert entry.env["CODEX_HOME"] == "{home}/.codex"  # no login file, no installed plugins
    assert entry.make_dirs == ("{home}/.codex",)  # Codex will not create its own home
    joined = " ".join(entry.argv)
    assert 'shell_environment_policy.exclude=["CODEX_API_KEY","OPENAI_API_KEY"]' in joined
    assert "CODEX_API_KEY" not in entry.pass_env and entry.permissions.network


def test_a_secrets_table_must_map_names_to_names(tmp_path, write_registry):
    path = write_registry()
    path.write_text(path.read_text() + "[fake.secrets]\nAGENT_KEY = 3\n")
    with pytest.raises(RegistryError, match="secrets"):
        load_registry(path)
