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
