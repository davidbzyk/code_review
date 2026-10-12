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
SLOT = "{findings}"  # where each rubric prompt gets the findings themselves
# Written as JSON escapes, which decode to the same finding: Reward Kit fills {criteria} across the
# whole prompt after this, and the prompt fences the findings in ```, so neither may come from one.
INERT = (("{criteria}", "\\u007bcriteria}"), ("`", "\\u0060"))


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


def rubric_with_findings(rubric: Path, findings: list, work: Path) -> Path:
    """A copy of the rubric whose prompts hold the findings, so no judge can grade without them.

    An agent judge is only pointed at its working directory and may answer without opening
    findings.json; text in the prompt reaches every backend.
    """
    copy = work / "rubric"
    shutil.rmtree(copy, ignore_errors=True)
    shutil.copytree(rubric, copy)
    text = json.dumps(findings, indent=2)
    for raw, escaped in INERT:
        text = text.replace(raw, escaped)
    prompts = [p for p in copy.rglob("*.md") if SLOT in p.read_text(encoding="utf-8")]
    if not prompts:
        raise ValueError(f"no rubric prompt under {rubric} has a {SLOT} slot")
    for p in prompts:
        p.write_text(p.read_text(encoding="utf-8").replace(SLOT, text), encoding="utf-8")
    return copy


def precision_and_f1(details: dict, findings: int, recall: float) -> tuple[float, float]:
    """Precision against the key (known issues matched per finding) and its F1 with recall.

    A real issue missing from the key counts against precision, so read it against the key only.
    """
    criteria = details.get(DIMENSION, {}).get("criteria", [])
    matched = sum(1 for c in criteria if float(c.get("value") or 0) >= 1)
    precision = min(matched, findings) / findings if findings else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return round(precision, 4), round(f1, 4)


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
        reward = {"reward": 0.0, "recall": 0.0, "precision": 0.0, "f1": 0.0,
                  "format": 0.0 if findings is None else 1.0,
                  "findings": 0.0}  # fmt: skip
        # No judge ran: an empty criteria list marks the zero as unjudged, with the reason.
        unjudged = {"score": 0.0, "criteria": [], "note": reason or "empty findings list"}
        _write(out, reward, {DIMENSION: unjudged})
        return 0
    # Clear only the judge's workspace: the work folder may be the process's working directory,
    # and deleting it leaves imports that call os.getcwd() (LiteLLM's) to fail.
    workspace = work / "workspace"
    shutil.rmtree(workspace, ignore_errors=True)
    workspace.mkdir(parents=True)
    (workspace / FINDINGS).write_text(json.dumps(findings, indent=2) + "\n")
    output = work / "reward.json"
    try:
        judge(rubric_with_findings(tests / "rubric", findings, work), workspace, output)
        scores = json.loads(output.read_text())
        details = json.loads(output.with_name("reward-details.json").read_text())
    except (subprocess.CalledProcessError, OSError, ValueError) as exc:
        print(f"finish: the judge did not run: {exc}", file=sys.stderr)
        return 1
    if errors := judge_errors(details):
        print("finish: the judge failed on " + "; ".join(errors), file=sys.stderr)
        return 1
    if DIMENSION not in scores:
        print(f"finish: Reward Kit wrote no {DIMENSION!r} score: {scores}", file=sys.stderr)
        return 1
    recall = float(scores[DIMENSION])
    precision, f1 = precision_and_f1(details, len(findings), recall)
    reward = {"reward": recall, "recall": recall, "precision": precision, "f1": f1, "format": 1.0,
              "findings": float(len(findings))}  # fmt: skip
    # Reward Kit's own document, unwrapped: graders and the platform read it as written.
    _write(out, reward, details)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("--artifacts", "--tests", "--out", "--work"):
        p.add_argument(name, type=Path, required=True)
    args = p.parse_args(argv)
    return finish(args.artifacts, args.tests, args.out, args.work)


if __name__ == "__main__":
    sys.exit(main())
