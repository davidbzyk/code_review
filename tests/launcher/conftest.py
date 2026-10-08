"""Fixtures: a fake agent registered as runner entries, a workspace and a skills folder."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

FAKE = Path(__file__).parent / "fake_agent.py"
_spec = importlib.util.spec_from_file_location("fake_agent", FAKE)
fake_agent = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fake_agent)
CODEX_ENV = '[{n}.env]\nHOME = "{{home}}"\nCODEX_HOME = "{{codex_home}}"\n'
PERMISSIONS = (
    '[{n}.permissions]\nsandbox = "workspace-write"\n'
    'writable_roots = ["{{workdir}}"]\nnetwork = false\n'
)


def _argv(shape: str, scenario: str, marker: str | None) -> list[str]:
    """Two different command templates for the same fake agent."""
    extra = ["--marker", marker] if marker else []
    if shape == "a":
        return [
            sys.executable, str(FAKE), "--scenario", scenario, "--out", "{out_dir}",
            "--model", "{model}", "--effort", "{effort}", "--last", "{last_message}",
            "--workdir", "{workdir}", *extra, "{prompt}",
        ]  # fmt: skip
    return [
        sys.executable, str(FAKE), "{prompt}", f"--scenario={scenario}", "--out={out_dir}",
        "--effort={effort}", "--model={model}", "--last={last_message}", *extra,
    ]  # fmt: skip


@pytest.fixture
def fake():
    """The fake agent's module, for its sample findings and its list of reviewers."""
    return fake_agent


@pytest.fixture
def write_registry(tmp_path):
    """Return a function that writes a runners.toml holding one fake entry and returns its path."""

    def write(
        name="fake", shape="a", scenario="all_ok", permissions=True, marker=None, secrets=None
    ) -> Path:
        argv = ", ".join(json.dumps(x) for x in _argv(shape, scenario, marker))
        text = f'[{name}]\nargv = [{argv}]\nstdin = "closed"\nmetadata = "codex_rollout"\n'
        text += CODEX_ENV.format(n=name)
        if secrets:
            rows = "".join(f"{k} = {json.dumps(v)}\n" for k, v in secrets.items())
            text += f"[{name}.secrets]\n{rows}"
        text += f'[{name}.skills]\ncopy_to = "{{home}}/.agents/skills"\n'
        if permissions:
            text += PERMISSIONS.format(n=name)
        path = tmp_path / f"runners-{name}-{shape}-{scenario}.toml"
        path.write_text(text)
        return path

    return write


@pytest.fixture
def workdir(tmp_path) -> Path:
    """A git repository standing in for the one under review, with tags `base` and `head`."""
    path = tmp_path / "work"
    path.mkdir()
    git = [*fake_agent.GIT, "-C", str(path)]
    subprocess.run([*git, "init", "-q"], check=True, capture_output=True)
    for tag, text in (("base", "pad 1\n"), ("head", fake_agent.APP)):
        (path / "app.py").write_text(text)
        subprocess.run([*git, "add", "-A"], check=True, capture_output=True)
        subprocess.run([*git, "commit", "-q", "-m", tag], check=True, capture_output=True)
        subprocess.run([*git, "tag", tag], check=True, capture_output=True)
    return path


@pytest.fixture
def skills(tmp_path) -> Path:
    """A skills folder holding one skill."""
    path = tmp_path / "skills"
    (path / "review-orchestrator").mkdir(parents=True)
    (path / "review-orchestrator" / "SKILL.md").write_text("# orchestrator\n")
    return path


@pytest.fixture
def run(tmp_path, workdir, skills, write_registry):
    """Return a function that runs one review with the fake agent and returns the result."""
    from review_core.launcher.run import run_review

    calls: list[str] = []

    def go(scenario="all_ok", shape="a", timeout_sec=60, registry=None, **kw):
        registry = registry or write_registry(shape=shape, scenario=scenario)
        kw.setdefault("head", "head")
        repo = kw.pop("workdir", workdir)
        calls.append(scenario)
        if len(calls) > 1:  # a second run in one test needs its own findings folder
            kw.setdefault("out_dir", workdir / f".review-{len(calls)}")
        kw.setdefault("skills_dir", skills)
        (tmp_path / "codex_home").mkdir(exist_ok=True)  # the caller's own Codex home exists
        return run_review(
            workdir=repo, base="base", runner="fake",
            model="gpt-6-luna", effort="high", timeout_sec=timeout_sec, runs_dir=tmp_path / "runs",
            registry_path=registry, codex_home=tmp_path / "codex_home", **kw,
        )  # fmt: skip

    return go
