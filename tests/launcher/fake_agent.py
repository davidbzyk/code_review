"""Stand-in for an agent CLI. It behaves like `codex exec` as far as the launcher can tell.

It checks that stdin is /dev/null, prints a thread.started event, writes per-reviewer findings
files and a Codex-shaped rollout under CODEX_HOME, and misbehaves on request (--scenario).
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

REVIEWERS = ["security", "tests", "correctness", "architecture", "code_quality", "compliance",
             "language"]  # fmt: skip


# Each reviewer's finding quotes its own line of app.py, ten lines apart so none merge.
LINE = {name: 10 * i + 3 for i, name in enumerate(REVIEWERS)}
APP = "".join(
    f"x = {next(r for r in REVIEWERS if LINE[r] == n)}\n" if n in LINE.values() else f"pad {n}\n"
    for n in range(1, 81)
)
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]


def finding(reviewer: str, **overrides) -> dict:
    """One valid finding, as a reviewer writes it: it quotes that reviewer's line of app.py."""
    item = {
        "file": "app.py", "line_start": LINE[reviewer], "line_end": LINE[reviewer], "side": "new",
        "quote": f"x = {reviewer}", "title": f"{reviewer} issue", "description": "It breaks.",
        "severity": "P2", "confidence": 75, "category": reviewer, "reviewer": reviewer,
        "scope": "in_diff", "fingerprint": None,
    }  # fmt: skip
    return {**item, **overrides}


def verdict_id(item: dict) -> str:
    """The id a verdict uses, spelled out: sha256 of file, side and quote lines, then the lines."""
    parts = [item["file"], item["side"], *(line.strip() for line in item["quote"].splitlines())]
    digest = hashlib.sha256("\n".join(parts).encode()).hexdigest()
    return f"{digest}:{item['line_start']}-{item['line_end']}"


def write_findings(out: Path, reviewer: str, findings: list[dict]) -> None:
    """Write findings.<reviewer>.json holding the given findings."""
    doc = {"schema_version": 1, "reviewer": reviewer, "findings": findings}
    (out / f"findings.{reviewer}.json").write_text(json.dumps(doc))


def token_line(total: int, used_percent: float) -> dict:
    """A token_count line as Codex writes it: running totals plus the allowance reading."""
    usage = {"input_tokens": total, "cached_input_tokens": total // 2, "output_tokens": 10,
             "reasoning_output_tokens": 4, "total_tokens": total + 10}  # fmt: skip
    limits = {
        "primary": {"used_percent": used_percent, "window_minutes": 10080},
        "plan_type": "pro",
    }
    payload = {"type": "token_count", "info": {"total_token_usage": usage}, "rate_limits": limits}
    return {
        "timestamp": f"2026-01-01T00:00:{total % 60:02d}Z",
        "type": "event_msg",
        "payload": payload,
    }


def write_rollout(codex_home, thread: str, model: str, effort: str, skip=(), extra=()) -> None:
    """Write a root rollout and seven child rollouts in the shape Codex 0.160.0 writes."""
    now = datetime.now()
    day = codex_home / "sessions" / f"{now:%Y}" / f"{now:%m}" / f"{now:%d}"
    day.mkdir(parents=True, exist_ok=True)
    stamp = f"{now:%Y-%m-%dT%H-%M-%S}"
    root_meta = {"id": thread, "session_id": thread, "cli_version": "0.160.0", "source": "exec"}
    context = {"model": model, "effort": effort, "sandbox_policy": {"type": "workspace-write"}}
    lines = [
        {"type": "session_meta", "payload": root_meta},
        {"type": "turn_context", "payload": context},
        token_line(1, 41.0),
        token_line(50, 42.0),
    ]
    (day / f"rollout-{stamp}-{thread}.jsonl").write_text(
        "\n".join(json.dumps(x) for x in lines) + "\n"
    )
    for name in (*REVIEWERS, *extra):
        if name in skip:
            continue
        child = str(uuid.uuid4())
        meta = {
            "id": child, "forked_from_id": thread, "parent_thread_id": thread,
            "cli_version": "0.160.0", "agent_path": f"/root/{name}",
            "source": {"subagent": {"thread_spawn": {"parent_thread_id": thread,
                                                      "agent_path": f"/root/{name}"}}},
        }  # fmt: skip
        child_lines = [{"type": "session_meta", "payload": meta}, token_line(59, 43.0)]
        (day / f"rollout-{stamp}-{child}.jsonl").write_text(
            "\n".join(json.dumps(x) for x in child_lines) + "\n"
        )


def junk_final() -> dict:
    """A final findings.json full of claims the launcher must ignore, though it is well formed."""
    rows = [{"reviewer": r, "outcome": "ok", "retries": 0, "findings_count": 9} for r in REVIEWERS]
    env = {
        "status": "complete", "reviewers_planned": REVIEWERS, "reviewers": rows,
        "runner": "agent-claim", "model": "gpt-9", "effort": "low", "cli_version": "9.9.9",
        "sandbox_mode": "danger-full-access",
        "dropped": {"quote_gate": 0, "confidence_floor": 2, "duplicate": 0,
                    "validator_declined": 0, "out_of_snapshot": 0},
    }  # fmt: skip
    extra = {"fingerprint": "f" * 64, "also_raised_by": ["tests"]}
    invented = finding("correctness", quote="never reported", title="invented", **extra)
    louder = finding("tests", severity="P0", confidence=100, title="REWRITTEN", **extra)
    twice = finding("security", **extra)
    return {"schema_version": 1, "envelope": env, "findings": [invented, louder, twice, twice]}


REVIEWER_LINE = re.compile(r"You are the `(\w+)` reviewer")
OUT_LINE = re.compile(r"The output folder is (\S+?)\. ")


def solo(a, name: str) -> int:
    """Act as one member of a team started as separate agents: a reviewer, or the validator.

    It writes its own file only, records the prompt it was sent and the skills its home holds,
    and leaves a root rollout with no children. Scenarios: `missing_one` (the tests reviewer
    writes nothing), `p1_*` (the security finding is P1; the validator upholds or declines it),
    `solo_wrong_model` (the security reviewer's record shows another model).
    """
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if not os.path.isdir(os.environ["CODEX_HOME"]):  # as Codex does: it will not create its home
        print("Error finding codex home: CODEX_HOME points to a path that does not exist",
              file=sys.stderr)  # fmt: skip
        return 1
    thread = str(uuid.uuid4())
    print(json.dumps({"type": "thread.started", "thread_id": thread}), flush=True)
    model = "gpt-5-other" if (a.scenario, name) == ("solo_wrong_model", "security") else a.model
    write_rollout(Path(os.environ["CODEX_HOME"]), thread, model, a.effort, skip=REVIEWERS)
    held = sorted(q.name for q in (Path(os.environ["HOME"]) / ".agents" / "skills").iterdir())
    seen = {"prompt": a.prompt, "skills": held, "model": a.model, "cwd": os.path.realpath("."),
            "env": sorted(os.environ), "codex_home": os.environ["CODEX_HOME"]}  # fmt: skip
    (out / f"seen.{name}.json").write_text(json.dumps(seen))
    if name == "validator":
        rows = json.loads((out / "validator-input.json").read_text())["findings"]
        verdict = "declined" if a.scenario == "p1_declined" else "upheld"
        verdicts = [{"id": row["id"], "verdict": verdict, "reason": "checked"} for row in rows]
        (out / "validation.json").write_text(json.dumps({"verdicts": verdicts}))
    elif not (a.scenario == "missing_one" and name == "tests"):
        severity = "P1" if a.scenario.startswith("p1_") and name == "security" else "P2"
        write_findings(out, name, [finding(name, severity=severity)])
    print(json.dumps({"type": "turn.completed"}), flush=True)
    return 0


def judge(a) -> int:
    """Act as the judge: a candidate matches a golden comment that contains its title.

    Scenarios: `judge_junk` answers with text that is no JSON, `judge_short` leaves the last
    golden comment out, `judge_fenced` wraps a good answer in a code fence.
    """
    golden, candidates = (json.loads(b) for b in re.findall(r"```json\n(.*?)\n```", a.prompt, re.S))
    thread = str(uuid.uuid4())
    print(json.dumps({"type": "thread.started", "thread_id": thread}), flush=True)
    write_rollout(Path(os.environ["CODEX_HOME"]), thread, a.model, a.effort, skip=REVIEWERS)
    rows = []
    for g in golden:
        hit = next((c["candidate"] for c in candidates
                    if c["issue"].split("\n")[0] in g["comment"]), None)  # fmt: skip
        rows.append({"golden": g["golden"], "reasoning": "same issue" if hit else "no candidate",
                     "match": hit is not None, "candidate": hit, "confidence": 0.9})  # fmt: skip
    answer = json.dumps({"results": rows[:-1] if a.scenario == "judge_short" else rows})
    if a.scenario == "judge_junk":
        answer = "I could not decide."
    if a.scenario == "judge_fenced":
        answer = f"```json\n{answer}\n```"
    Path(a.last).write_text(answer)
    return 0


def label(a) -> int:
    """Act as the golden-comment labeller: tests when the comment says "test", else correctness.

    Scenario `label_junk` answers with text that is no JSON.
    """
    comments = json.loads(re.findall(r"```json\n(.*?)\n```", a.prompt, re.S)[1])
    thread = str(uuid.uuid4())
    print(json.dumps({"type": "thread.started", "thread_id": thread}), flush=True)
    write_rollout(Path(os.environ["CODEX_HOME"]), thread, a.model, a.effort, skip=REVIEWERS)
    rows = [{"golden": c["golden"], "reason": "by its words",
             "category": "tests" if "test" in c["comment"].lower() else "correctness"}
            for c in comments]  # fmt: skip
    answer = "No labels." if a.scenario == "label_junk" else json.dumps({"labels": rows})
    Path(a.last).write_text(answer)
    return 0


def main() -> int:
    """Run one scenario and return the exit code."""
    p = argparse.ArgumentParser()
    p.add_argument("prompt")
    for flag in ("scenario", "out", "model", "effort", "last", "workdir", "marker"):
        p.add_argument(f"--{flag}")
    a = p.parse_args()
    if a.marker:
        Path(a.marker).write_text("started")
    if not os.path.samestat(os.fstat(0), os.stat(os.devnull)) or sys.stdin.read():
        print("stdin is not /dev/null", file=sys.stderr)
        return 5
    if a.scenario == "auth_fail":
        print("401 Unauthorized: please sign in", file=sys.stderr)
        return 1
    if a.prompt.startswith("You are sorting code review comments"):
        return label(a)
    if a.prompt.startswith("You are evaluating AI code review tools."):
        return judge(a)
    member = REVIEWER_LINE.search(a.prompt)
    if member or "review-validator skill" in a.prompt:
        return solo(a, member.group(1) if member else "validator")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "prompt.txt").write_text(a.prompt)
    thread = str(uuid.uuid4())
    print(json.dumps({"type": "thread.started", "thread_id": thread}), flush=True)
    print(json.dumps({"type": "turn.started"}), flush=True)
    codex_home = Path(os.environ["CODEX_HOME"])
    model = "gpt-5-other" if a.scenario == "wrong_model" else a.model
    skip = ("language",) if a.scenario == "self_written" else ()
    extra = ("validator",) if a.scenario in ("p1_validated", "p1_declined") else ()
    write_rollout(codex_home, thread, model, a.effort, skip=skip, extra=extra)
    (out / "cwd.json").write_text(json.dumps(os.path.realpath(os.getcwd())))
    (out / "path.json").write_text(json.dumps(os.environ.get("PATH", "").split(os.pathsep)))
    (out / "context_seen.json").write_text(json.dumps((out / "context.md").is_file()))
    run_dir = Path(os.environ.get("HOME", ".")).parent  # HOME is <run_dir>/home in these tests
    found = sorted(str(q.relative_to(run_dir)) for q in run_dir.rglob("ctx") if q.is_file())
    (out / "ctx_seen.json").write_text(json.dumps([f for f in found if not f.startswith("bin/")]))
    if a.scenario == "env_probe":
        (out / "env.json").write_text(json.dumps(sorted(os.environ)))
    if a.scenario == "hang":
        child = subprocess.Popen(["sleep", "300"])
        (out / "child.pid").write_text(str(child.pid))
        time.sleep(300)
        return 0
    security = finding("security")
    if a.scenario.startswith("p1_"):
        security = finding("security", severity="P1")
    if a.scenario == "weak_one":
        security = finding("security", confidence=25)
    if a.scenario in ("bad_quote", "moved_ref", "replaced_object"):
        security = finding("security", quote="x = planted")
    for name in REVIEWERS:
        if a.scenario in ("missing_one", "forged_final") and name == "tests":
            continue
        if a.scenario == "malformed_one" and name == "correctness":
            (out / f"findings.{name}.json").write_text("{not json")
            continue
        mine = [security if name == "security" else finding(name)]
        if a.scenario == "empty_one" and name == "security":
            mine = []
        if a.scenario == "wrong_lines" and name == "tests":
            # Claims the security reviewer's lines while quoting its own.
            mine = [finding("tests", line_start=LINE["security"], line_end=LINE["security"])]
        if a.scenario == "collision" and name == "correctness":
            # Reports the very same lines and quote as the security reviewer.
            mine = [{**finding("security"), "reviewer": "correctness", "category": "correctness"}]
        if a.scenario == "wrong_owner" and name == "tests":
            mine = [{**finding("tests"), "reviewer": "security"}]
        write_findings(out, name, mine)
    target = out / "findings.security.json"
    if a.scenario == "symlink_one":
        real = out.parent / "elsewhere.json"
        real.write_text(target.read_text())
        target.unlink()
        target.symlink_to(real)
    if a.scenario == "oversized_one":
        doc = json.loads(target.read_text())
        doc["findings"][0]["description"] = "x" * 6_000_000
        target.write_text(json.dumps(doc))
    if a.scenario == "flood_one":
        doc = json.loads(target.read_text())
        doc["findings"] = doc["findings"] * 501
        target.write_text(json.dumps(doc))
    if a.scenario == "deep_one":
        target.write_text("[" * 200_000 + "]" * 200_000)
    if a.scenario == "moved_ref":
        # Make the planted quote real in a new commit and point the `head` name at it.
        Path("app.py").write_text(APP + "x = planted\n")
        subprocess.run([*GIT, "commit", "-qam", "planted"], check=True, capture_output=True)
        subprocess.run([*GIT, "tag", "-f", "head"], check=True, capture_output=True)
    if a.scenario == "replaced_object":
        # Keep every name where it was, but tell git to serve another commit in place of head.
        real = subprocess.run([*GIT, "rev-parse", "head"], check=True, capture_output=True)
        Path("app.py").write_text(APP + "x = planted\n")
        subprocess.run([*GIT, "commit", "-qam", "planted"], check=True, capture_output=True)
        subprocess.run([*GIT, "replace", real.stdout.decode().strip(), "HEAD"], check=True)
    if a.scenario == "trashed_repo":
        shutil.rmtree(".git")
    if a.scenario in ("p1_validated", "p1_forged_validation", "p1_declined"):
        verdict = "declined" if a.scenario == "p1_declined" else "upheld"
        row = {"id": verdict_id(security), "verdict": verdict, "reason": "checked"}
        (out / "validation.json").write_text(json.dumps({"verdicts": [row]}))
    if a.scenario in ("final_file", "forged_final"):
        (out / "findings.json").write_text(json.dumps(junk_final()))
    if a.scenario == "stall":
        # Every reviewer is done and the main agent waits on nothing, for ever.
        time.sleep(300)
    if a.scenario == "busy":
        # The main agent prints nothing while a sub-agent keeps working for a few seconds.
        child = sorted((codex_home / "sessions").glob("*/*/*/rollout-*.jsonl"))[-1]
        for _ in range(8):
            time.sleep(0.5)
            with child.open("a") as fh:
                fh.write(json.dumps({"type": "event_msg", "payload": {"type": "working"}}) + "\n")
    print(json.dumps({"type": "turn.completed"}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
