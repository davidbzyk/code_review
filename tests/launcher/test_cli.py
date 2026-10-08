"""The command line prints one line per reviewer and exits non-zero on a failed run."""

import re

import pytest

from review_core.cli import main


@pytest.mark.parametrize(("scenario", "code"), [("all_ok", 0), ("auth_fail", 1)])
def test_review_command(
    scenario, code, tmp_path, workdir, skills, write_registry, capsys, monkeypatch
):
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex_home"))
    argv = [
        "review", "--repo", str(workdir), "--base", "base", "--head", "head", "--runner", "fake",
        "--skills", str(skills), "--runs", str(tmp_path / "runs"), "--timeout-sec", "30",
        "--registry", str(write_registry(scenario=scenario)),
    ]  # fmt: skip
    assert main(argv) == code
    out = capsys.readouterr().out
    if code == 0:
        assert "security: ok" in out and "language: ok" in out
    assert re.search(r"status: (complete|failed)", out)
    assert re.search(r"review\.json: \S+review\.json", out)
