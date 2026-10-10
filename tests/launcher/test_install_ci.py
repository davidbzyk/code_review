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
    assert (dest / "ruff.toml").is_file()  # a host's ruff lints the copy with its own settings
    readme = (dest / "README.md").read_text()  # setup for both sign-ins travels with the tool
    assert "CODEX_AUTH_JSON_B64" in readme and "CODE_REVIEW_AUTH -b api-key" in readme
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
    assert payload["event"] == "COMMENT" and payload["body"].startswith("### Custom Code Review")
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
    assert payload["comments"] and payload["body"].startswith("### Custom Code Review")
    # Codex's sandbox lets agents write only inside the checkout, so the output folder is there.
    assert (workdir / ".code-review-out").is_dir()
    script = (dest / "run-review.sh").read_text()
    assert 'env -u GITHUB_TOKEN "${py[@]}" -m review_core.cli review' in script


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


def test_the_action_lets_codex_sandbox_before_the_review():
    text = (ROOT / "action" / "action.yml").read_text()
    allow = text.index("kernel.apparmor_restrict_unprivileged_userns=0")
    assert allow < text.index("name: Review and post")


def test_run_review_sh_hands_the_poster_both_logins_and_the_api_key_name():
    script = (ROOT / "action" / "run-review.sh").read_text()
    assert '--secret-file "$CODEX_HOME/auth.json" --secret-file "$work/auth.seed.json"' in script
    assert "--secret-env OPENAI_API_KEY" in script


def test_a_module_planted_in_the_checkout_is_never_imported(workdir, write_registry, tmp_path):
    # Agents can write inside the checkout; python -m would import from the working directory.
    dest = bundle.install(workdir)
    planted = workdir / "review_core"
    planted.mkdir()
    (planted / "__init__.py").write_text("raise SystemExit('planted module ran')\n")
    env = {
        "PATH": os.environ["PATH"], "HOME": str(tmp_path), "RUNNER_TEMP": str(tmp_path / "rt"),
        "GITHUB_WORKSPACE": str(workdir), "CR_BASE": "base", "CR_HEAD": "head",
        "CR_REPO": "o/r", "CR_PR": "1", "CR_DRY_RUN": str(tmp_path / "post"),
        "CR_RUNNER": "fake", "CR_REGISTRY": str(write_registry()), "CODEX_AUTH_JSON_B64": "e30=",
    }  # fmt: skip
    done = subprocess.run(["bash", str(dest / "run-review.sh")], cwd=workdir, env=env,
                          capture_output=True, text=True)  # fmt: skip
    assert "planted module ran" not in done.stdout + done.stderr
    assert done.returncode == 0, done.stderr


def test_the_run_folder_is_uploaded_only_when_asked():
    text = (ROOT / "action" / "action.yml").read_text()
    upload = text[text.index("uses: actions/upload-artifact") :]
    assert "inputs.keep-run == 'true'" in text[: text.index("uses: actions/upload-artifact")]
    assert 'default: "false"' in text.split("keep-run:")[1].split("runs:")[0]
    assert upload


def _env(workdir, tmp_path, registry):
    return {
        "PATH": os.environ["PATH"], "HOME": str(tmp_path), "RUNNER_TEMP": str(tmp_path / "rt"),
        "GITHUB_WORKSPACE": str(workdir), "CR_BASE": "base", "CR_HEAD": "head",
        "CR_REPO": "o/r", "CR_PR": "1", "CR_DRY_RUN": str(tmp_path / "post"),
        "CR_RUNNER": "fake", "CR_REGISTRY": str(registry), "CODEX_AUTH_JSON_B64": "e30=",
    }  # fmt: skip


def test_an_agent_that_edits_the_installed_tool_cannot_change_what_posts(
    workdir, write_registry, tmp_path
):
    # The checkout is the one folder agents may write, and .code-review/ sits inside it.
    dest = bundle.install(workdir)
    fake = write_registry()
    text = fake.read_text()
    argv_line = next(line for line in text.splitlines() if line.startswith("argv = ["))
    script = tmp_path / "tamper.sh"
    script.write_text(
        "#!/bin/bash\n"
        "python3 -c 'import pathlib, sys; p = pathlib.Path(sys.argv[1]); "
        'p.write_text("raise SystemExit(7)\\\\n" + p.read_text())\' '
        '"$1/.code-review/src/review_core/ci/github.py"\n'
        'shift\nexec "$@"\n'
    )
    prefix = ", ".join(json.dumps(x) for x in ("bash", str(script), "{workdir}")) + ", "
    fake.write_text(text.replace(argv_line, argv_line.replace("argv = [", "argv = [" + prefix, 1)))
    done = subprocess.run(
        ["bash", str(dest / "run-review.sh")],
        cwd=workdir,
        env=_env(workdir, tmp_path, fake),
        capture_output=True,
        text=True,
    )
    assert (dest / "src/review_core/ci/github.py").read_text().startswith("raise SystemExit(7)")
    assert done.returncode == 0, done.stderr
    assert (tmp_path / "post" / "review.json").is_file()


def test_a_changed_file_with_a_non_ascii_name_is_reviewed(workdir, write_registry, tmp_path):
    git = ["git", "-C", str(workdir), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "checkout", "-q", "base"], check=True, capture_output=True)
    (workdir / "café.py").write_text("x = 1\n")
    subprocess.run([*git, "add", "-A"], check=True, capture_output=True)
    subprocess.run([*git, "commit", "-q", "-m", "accent"], check=True, capture_output=True)
    sha = subprocess.run([*git, "rev-parse", "HEAD"], check=True, capture_output=True,
                         text=True).stdout.strip()  # fmt: skip
    dest = bundle.install(workdir)
    env = {**_env(workdir, tmp_path, write_registry()), "CR_HEAD": sha}
    done = subprocess.run(["bash", str(dest / "run-review.sh")], cwd=workdir, env=env,
                          capture_output=True, text=True)  # fmt: skip
    assert done.returncode == 0, done.stderr
    assert "nothing to review" not in done.stdout


def test_the_workflow_pins_actions_by_sha_drops_the_token_and_skips_dependabot():
    workflow = (ROOT / "action" / "workflow.yml").read_text()
    action = (ROOT / "action" / "action.yml").read_text()
    for text in (workflow, action):
        for line in text.splitlines():
            if "uses: actions/" in line:
                ref = line.split("@", 1)[1].split()[0]
                assert len(ref) == 40 and all(c in "0123456789abcdef" for c in ref), line
    assert "persist-credentials: false" in workflow
    assert "github.event.pull_request.user.login != 'dependabot[bot]'" in workflow


def test_the_action_reviews_on_the_rows_that_give_commands_no_network():
    script = (ROOT / "action" / "run-review.sh").read_text()
    assert "runner=codex-ci\n" in script and "runner=codex-ci-key\n" in script
    assert "runner=codex-clean" not in script and "runner=codex-key\n" not in script


def _commit(workdir, message, change):
    git = ["git", "-C", str(workdir), "-c", "user.name=t", "-c", "user.email=t@t"]
    change()
    subprocess.run([*git, "add", "-A"], check=True, capture_output=True)
    subprocess.run([*git, "commit", "-q", "-m", message], check=True, capture_output=True)
    return subprocess.run([*git, "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()  # fmt: skip


def _recording(registry, tmp_path):
    """The fake runner, wrapped so the agent's arguments (its prompt among them) are kept."""
    log = tmp_path / "argv.txt"
    wrap = tmp_path / "record.sh"
    wrap.write_text(f'#!/bin/bash\nprintf "%s\\n" "$@" >> {json.dumps(str(log))}\nexec "$@"\n')
    text = registry.read_text()
    line = next(x for x in text.splitlines() if x.startswith("argv = ["))
    prefix = ", ".join(json.dumps(x) for x in ("bash", str(wrap))) + ", "
    registry.write_text(text.replace(line, line.replace("argv = [", "argv = [" + prefix, 1)))
    return registry, log


def _run(dest, workdir, env):
    return subprocess.run(["bash", str(dest / "run-review.sh")], cwd=workdir, env=env,
                          capture_output=True, text=True)  # fmt: skip


def _sha(workdir, ref):
    return subprocess.run(["git", "-C", str(workdir), "rev-parse", ref], check=True,
                          capture_output=True, text=True).stdout.strip()  # fmt: skip


def test_a_change_that_only_deletes_a_file_is_reviewed(workdir, write_registry, tmp_path):
    # SHAs, not the fixture's `head` tag: on a case-insensitive disk it collides with HEAD.
    start = _sha(workdir, "refs/tags/head")
    sha = _commit(workdir, "drop", lambda: (workdir / "app.py").unlink())
    dest = bundle.install(workdir)
    done = _run(dest, workdir, {**_env(workdir, tmp_path, write_registry()), "CR_BASE": start,
                                "CR_HEAD": sha})  # fmt: skip
    assert "nothing to review" not in done.stdout, done.stdout
    assert done.returncode == 0, done.stderr


def test_a_file_named_like_an_option_is_reviewed(workdir, write_registry, tmp_path):
    start = _sha(workdir, "refs/tags/head")
    sha = _commit(workdir, "dash", lambda: (workdir / "--head").write_text("x\n"))
    dest = bundle.install(workdir)
    registry, argv_log = _recording(write_registry(), tmp_path)
    done = _run(dest, workdir, {**_env(workdir, tmp_path, registry), "CR_BASE": start,
                                "CR_HEAD": sha})  # fmt: skip
    assert done.returncode == 0, done.stderr
    assert "--head" in argv_log.read_text()  # the file is in the reviewers' slice


def test_the_review_gets_the_merge_base_not_the_moved_target(workdir, write_registry, tmp_path):
    git = ["git", "-C", str(workdir), "-c", "user.name=t", "-c", "user.email=t@t"]
    fork = _sha(workdir, "refs/tags/head")
    pr = _commit(workdir, "pr", lambda: (workdir / "app.py").write_text("changed\n"))
    subprocess.run([*git, "checkout", "-q", fork], check=True, capture_output=True)
    tip = _commit(workdir, "target moved", lambda: (workdir / "other.py").write_text("y\n"))
    subprocess.run([*git, "checkout", "-q", pr], check=True, capture_output=True)
    dest = bundle.install(workdir)
    registry, argv_log = _recording(write_registry(), tmp_path)
    env = {**_env(workdir, tmp_path, registry), "CR_BASE": tip, "CR_HEAD": pr}
    done = _run(dest, workdir, env)
    assert done.returncode == 0, done.stderr
    prompt = argv_log.read_text()
    assert fork in prompt and tip not in prompt


def test_the_installed_copy_carries_the_context_command(workdir, tmp_path):
    dest = bundle.install(workdir)
    done = subprocess.run([sys.executable, "-S", "-m", "review_core.context.ctx", "--help"],
                          env={"PATH": os.environ["PATH"], "PYTHONPATH": str(dest / "src")},
                          cwd=tmp_path, capture_output=True, text=True)  # fmt: skip
    assert done.returncode == 0, done.stderr


def test_the_workflow_reviews_the_pr_head_skips_dependabot_by_author_and_reruns_on_retarget():
    text = (ROOT / "action" / "workflow.yml").read_text()
    assert "ref: ${{ github.event.pull_request.head.sha }}" in text
    assert "github.event.pull_request.user.login != 'dependabot[bot]'" in text
    assert "github.actor" not in text
    assert "types: [opened, synchronize, reopened, ready_for_review, edited]" in text
    assert "(github.event.action != 'edited' || github.event.changes.base)" in text


def test_run_review_sh_hands_the_reviewers_the_earlier_review_and_reads_it_with_the_token(
    workdir, write_registry, tmp_path
):
    dest = bundle.install(workdir)
    earlier = tmp_path / "earlier.md"
    earlier.write_text("# Earlier review of this pull request\n")
    env = {
        "PATH": os.environ["PATH"], "HOME": str(tmp_path), "RUNNER_TEMP": str(tmp_path / "rt"),
        "GITHUB_WORKSPACE": str(workdir), "CR_BASE": "base", "CR_HEAD": "head",
        "CR_REPO": "o/r", "CR_PR": "1", "CR_DRY_RUN": str(tmp_path / "post"),
        "CR_RUNNER": "fake", "CR_REGISTRY": str(write_registry()), "CODEX_AUTH_JSON_B64": "e30=",
        "CR_PRIOR_REVIEW": str(earlier),
    }  # fmt: skip
    done = subprocess.run(["bash", str(dest / "run-review.sh")], env=env, capture_output=True,
                          text=True)  # fmt: skip
    assert done.returncode == 0, done.stderr
    prompt = (workdir / ".code-review-out" / "prompt.txt").read_text()
    assert "Earlier review of this pull request: read " in prompt
    script = (dest / "run-review.sh").read_text()
    # The history is read while the token is there; the review after it never gets the token.
    assert script.index("review_core.ci.history") < script.index("env -u GITHUB_TOKEN")


def test_the_install_carries_every_module_the_wrapper_runs(workdir):
    dest = bundle.install(workdir)
    script = (dest / "run-review.sh").read_text()
    import re

    for module in sorted(set(re.findall(r"-m (review_core[\w.]+)", script))):
        assert (dest / "src" / (module.replace(".", "/") + ".py")).is_file(), module
