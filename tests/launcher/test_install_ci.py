"""The CI install: the copied folder alone runs a review and renders the post (dry run)."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("bundle", ROOT / "action" / "bundle.py")
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


def test_install_copies_the_tool_skills_action_and_workflow_and_nothing_else(workdir):
    dest = bundle.install(workdir)
    assert (dest / "action.yml").is_file() and (dest / "run-review.sh").is_file()
    assert (dest / "src" / "review_core" / "cli.py").is_file()
    assert (dest / "src" / "review_core" / "launcher" / "runners.toml").is_file()
    assert (dest / "src" / "plugin" / "skills" / "review-orchestrator" / "SKILL.md").is_file()
    assert (workdir / ".github" / "workflows" / "code-review.yml").is_file()
    copied = [p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file()]
    assert not [p for p in copied if "__pycache__" in p or p.endswith(".pyc")]
    assert not [
        p for p in copied if p.startswith(("src/context_engine", "src/review_core/scoring"))
    ]
    assert os.access(dest / "run-review.sh", os.X_OK)


def test_a_second_install_replaces_the_first(workdir):
    dest = bundle.install(workdir)
    (dest / "stray.txt").write_text("x")
    bundle.install(workdir)
    assert not (dest / "stray.txt").exists()


def test_the_installed_copy_alone_runs_a_review_and_a_dry_run_post(
    workdir, write_registry, tmp_path
):
    dest = bundle.install(workdir)
    env = {"PATH": os.environ["PATH"], "PYTHONPATH": str(dest / "src"), "HOME": str(tmp_path)}
    python = [sys.executable, "-S"]  # no site-packages: the copy must need nothing installed
    review = subprocess.run(
        [*python, "-m", "review_core.cli", "review", "--repo", str(workdir), "--base", "base",
         "--head", "head", "--runner", "fake", "--registry", str(write_registry()),
         "--out", str(tmp_path / "out"), "--runs", str(tmp_path / "runs")],
        env=env, cwd=tmp_path, capture_output=True, text=True,
    )  # fmt: skip
    assert review.returncode == 0, review.stderr
    post = subprocess.run(
        [*python, "-m", "review_core.ci.github", "--runs", str(tmp_path / "runs"),
         "--repo-dir", str(workdir), "--base", "base", "--head", "head", "--repo", "o/r",
         "--pr", "1", "--dry-run", str(tmp_path / "post")],
        env=env, cwd=tmp_path, capture_output=True, text=True,
    )  # fmt: skip
    assert post.returncode == 0, post.stderr
    payload = json.loads((tmp_path / "post" / "review.json").read_text())
    assert payload["event"] == "COMMENT" and payload["body"].startswith("### Code review")
    assert payload["comments"], "the fake agent's findings sit on app.py lines of the diff"
    assert all(c["path"] == "app.py" for c in payload["comments"])


def test_run_review_sh_reviews_and_dry_runs_with_the_token_kept_from_the_review(
    workdir, write_registry, tmp_path
):
    dest = bundle.install(workdir)
    env = {
        "PATH": os.environ["PATH"], "HOME": str(tmp_path), "RUNNER_TEMP": str(tmp_path / "rt"),
        "GITHUB_WORKSPACE": str(workdir), "CR_BASE": "base", "CR_HEAD": "head",
        "CR_REPO": "o/r", "CR_PR": "1", "CR_DRY_RUN": str(tmp_path / "post"),
        "CR_RUNNER": "fake", "CR_REGISTRY": str(write_registry()),
        "CODEX_AUTH_JSON_B64": "e30=", "GITHUB_TOKEN": "not-a-real-token",
    }  # fmt: skip
    done = subprocess.run(["bash", str(dest / "run-review.sh")], env=env, capture_output=True,
                          text=True)  # fmt: skip
    assert done.returncode == 0, done.stderr
    payload = json.loads((tmp_path / "post" / "review.json").read_text())
    assert payload["comments"] and payload["body"].startswith("### Code review")
    script = (dest / "run-review.sh").read_text()
    assert "env -u GITHUB_TOKEN python3 -m review_core.cli review" in script


def test_run_review_sh_skips_a_change_that_only_touches_the_tool(workdir, tmp_path):
    bundle.install(workdir)
    git = ["git", "-C", str(workdir), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "add", "-A"], check=True, capture_output=True)
    subprocess.run([*git, "commit", "-q", "-m", "install"], check=True, capture_output=True)
    env = {"PATH": os.environ["PATH"], "HOME": str(tmp_path), "RUNNER_TEMP": str(tmp_path / "rt"),
           "GITHUB_WORKSPACE": str(workdir), "CR_BASE": "head", "CR_HEAD": "HEAD"}  # fmt: skip
    done = subprocess.run(["bash", str(workdir / ".code-review" / "run-review.sh")], env=env,
                          capture_output=True, text=True)  # fmt: skip
    assert done.returncode == 0, done.stderr
    assert "nothing to review" in done.stdout
