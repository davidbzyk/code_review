"""Grade one trial of a rubric task: guard the findings file, run the judge, write the reward.

    python3 finish.py --artifacts DIR --tests DIR --out DIR --work DIR

No findings file, one that does not parse, or an empty list scores 0.0 with no judge call. A
judge error writes no reward, so Harbor counts the attempt as an exception and runs it again.
Standard library only: it runs in the grader image beside Reward Kit.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

FINDINGS = "findings.json"
DIMENSION = "recall"


def load_findings(path: Path) -> tuple[list | None, str]:
    """The findings list, or None with the reason it cannot be graded."""
    if not path.is_file():
        return None, "no findings file"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, f"findings file does not parse: {exc}"
    if not isinstance(data, list) or not all(isinstance(f, dict) for f in data):
        return None, "findings file is not a list of objects"
    return data, ""


def run_rewardkit(rubric: Path, workspace: Path, output: Path) -> None:
    """Run Reward Kit on the rubric folder; it writes reward.json and reward-details.json."""
    command = ["rewardkit", str(rubric), "--workspace", str(workspace), "--output", str(output)]
    subprocess.run(command, check=True)


def _write(out: Path, reward: dict, details: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "reward-details.json").write_text(json.dumps(details, indent=2) + "\n")
    (out / "reward.json").write_text(json.dumps(reward) + "\n")


def judge_errors(details: dict) -> list[str]:
    """Every criterion the judge failed to score, as `name: error`."""
    return [
        f"{c.get('name')}: {c['error']}"
        for dim in details.values()
        if isinstance(dim, dict)
        for c in dim.get("criteria", [])
        if c.get("error")
    ]


def finish(
    artifacts: Path,
    tests: Path,
    out: Path,
    work: Path,
    judge: Callable[[Path, Path, Path], None] = run_rewardkit,
) -> int:
    """Grade the trial and write the reward; returns the process exit code."""
    findings, reason = load_findings(artifacts / FINDINGS)
    if not findings:
        reward = {"reward": 0.0, "recall": 0.0, "format": 0.0 if findings is None else 1.0,
                  "findings": 0.0}  # fmt: skip
        _write(out, reward, {"judged": False, "reason": reason or "empty findings list"})
        return 0
    # Clear only the judge's workspace: the work folder may be the process's working directory,
    # and deleting it leaves imports that call os.getcwd() (LiteLLM's) to fail.
    workspace = work / "workspace"
    shutil.rmtree(workspace, ignore_errors=True)
    workspace.mkdir(parents=True)
    (workspace / FINDINGS).write_text(json.dumps(findings, indent=2) + "\n")
    output = work / "reward.json"
    try:
        judge(tests / "rubric", workspace, output)
        scores = json.loads(output.read_text())
        details = json.loads(output.with_name("reward-details.json").read_text())
    except (subprocess.CalledProcessError, OSError, json.JSONDecodeError) as exc:
        print(f"finish: the judge did not run: {exc}", file=sys.stderr)
        return 1
    if errors := judge_errors(details):
        print("finish: the judge failed on " + "; ".join(errors), file=sys.stderr)
        return 1
    if DIMENSION not in scores:
        print(f"finish: Reward Kit wrote no {DIMENSION!r} score: {scores}", file=sys.stderr)
        return 1
    recall = float(scores[DIMENSION])
    reward = {"reward": recall, "recall": recall, "format": 1.0, "findings": float(len(findings))}
    _write(out, reward, {"judged": True, "rubric": details})
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("--artifacts", "--tests", "--out", "--work"):
        p.add_argument(name, type=Path, required=True)
    args = p.parse_args(argv)
    return finish(args.artifacts, args.tests, args.out, args.work)


if __name__ == "__main__":
    sys.exit(main())
