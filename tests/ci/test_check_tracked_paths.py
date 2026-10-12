"""The tracked-path guard: denied paths, denied names and private text are refused before commit."""

import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("guard", ROOT / "ci" / "check_tracked_paths.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
SECRET = "the retry loop never stops when the upstream returns a 429 status code"


def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    (r / "ci").mkdir(parents=True)
    (r / "ci" / "tracked-paths.toml").write_text((ROOT / "ci" / "tracked-paths.toml").read_text())
    subprocess.run(["git", "init", "-q", str(r)], check=True)
    return r


def private_root(tmp_path: Path) -> Path:
    p = tmp_path / "private" / "cases" / "ge-x1"
    p.mkdir(parents=True)
    golden = {"comments": [{"id": "g1", "title": "Retry loop never ends", "comment": SECRET}]}
    (p / "golden.json").write_text(json.dumps(golden))
    return tmp_path / "private"


def stage(r: Path, rel: str, text: str) -> None:
    path = r / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    subprocess.run(["git", "-C", str(r), "add", "-f", rel], check=True)


def test_denied_paths_and_names_are_refused(tmp_path):
    r = repo(tmp_path)
    stage(r, "trials/results/job/result.json", "{}")
    stage(r, "evals/tasks/ge-x1/environment/repo.tar.gz", "x")
    stage(r, ".env", "KEY=1")
    stage(r, ".env.example", "KEY=")
    stage(r, "src/ok.py", "x = 1\n")
    problems = guard.check(r, private=None)
    assert sorted(p.split(":")[0] for p in problems) == [
        ".env",
        "evals/tasks/ge-x1/environment/repo.tar.gz",
        "trials/results/job/result.json",
    ]


def test_private_case_text_is_refused_wherever_it_is_staged(tmp_path):
    r = repo(tmp_path)
    stage(r, "docs/notes.md", f"An example: {SECRET}.\n")
    stage(r, "src/ok.py", "x = 1\n")
    problems = guard.check(r, private=private_root(tmp_path))
    assert [p.split(":")[0] for p in problems] == ["docs/notes.md"]


def test_without_a_private_root_only_paths_are_checked(tmp_path):
    r = repo(tmp_path)
    stage(r, "docs/notes.md", f"An example: {SECRET}.\n")
    assert guard.check(r, private=None) == []


def test_public_voiceover_tasks_may_ship_their_case_material_but_ge_tasks_never():
    import tomllib
    from pathlib import Path

    toml = Path(__file__).resolve().parents[2] / "ci" / "tracked-paths.toml"
    rules = tomllib.loads(toml.read_text())
    # No single-agent tasks are published, voiceover or not.
    assert guard.refused_path("evals/tasks/vo-t01/environment/repo.tar.gz", rules)
    assert guard.refused_path("evals/tasks/vo-t01/task.toml", rules)
    assert guard.refused_path("evals/tasks/ge-x766/task.toml", rules)
    assert guard.refused_path("anything/else/repo.tar.gz", rules)
    assert guard.refused_path("evals/team-tasks/vo-t01/environment/repo.tar.gz", rules) is None
    assert guard.refused_path("evals/team-tasks/ge-x766/environment/repo.tar.gz", rules)
    assert guard.refused_path("evals/team-tasks/ge-x766/task.toml", rules)


def test_a_public_voiceover_task_still_refuses_credentials_and_graded_output():
    """The voiceover allowance covers only the case archive, never a login or a grade."""
    import tomllib

    toml = Path(__file__).resolve().parents[2] / "ci" / "tracked-paths.toml"
    rules = tomllib.loads(toml.read_text())
    for name in ("auth.json", ".private-repository", "golden.json", "reward-details.json"):
        assert guard.refused_path(f"evals/team-tasks/vo-t01/{name}", rules), name
