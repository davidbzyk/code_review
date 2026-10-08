"""An LLM judge: which golden comments of a pull request did a review's findings state?

The method is the Martian Code Review Bench's (github.com/withmartian/code-review-benchmark,
`offline/code_review_benchmark/step3_judge_comments.py` at commit e616e849): the judge is given a
golden comment and a candidate issue as text, with no file or line, and says whether they are
the same underlying issue. Its instructions are that benchmark's own. One thing differs: that
benchmark asks once per pair; this asks once per pull request, with every golden comment and
every candidate in one prompt, and has the judge name the best candidate for each.

The judge is an agent started through a runner entry, like a reviewer, in an empty folder.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from string import Template

from review_core.contracts.models import Finding
from review_core.launcher.runners import agent_env, load_registry, read_secrets

PROMPT = Path(__file__).with_name("judge_prompt.md")
RESULT_NAME = "judge.json"
# The judge compares two texts and needs nothing else, so it is started read-only whatever its
# entry allows a reviewer: no writes and no network for the commands it could run.
JUDGE_SANDBOX = "read-only"
# The prompt travels on the command line; one this large would not be a judgement anyway.
MAX_PROMPT_BYTES = 200_000
_FENCE = re.compile(r"^```[a-z]*\n(.*)\n```$", re.DOTALL)


class JudgeError(ValueError):
    """The judge could not be asked, or its answer is not a verdict on every golden comment."""


def candidate_text(finding: Finding) -> str:
    """A finding as the judge reads it: its title and its description, with no place."""
    return f"{finding.title}\n\n{finding.description}".strip()


def render_judge_prompt(golden: Sequence[Mapping], findings: Sequence[Finding]) -> str:
    """The judge's prompt for one pull request: its golden comments and one review's findings."""
    asked = [{"golden": g["id"], "comment": g["comment"]} for g in golden]
    given = [{"candidate": i, "issue": candidate_text(f)} for i, f in enumerate(findings, 1)]
    prompt = Template(PROMPT.read_text(encoding="utf-8")).substitute(
        golden=json.dumps(asked, indent=1), candidates=json.dumps(given, indent=1)
    )
    if len(prompt.encode()) > MAX_PROMPT_BYTES:
        raise JudgeError(f"the judge's prompt is over {MAX_PROMPT_BYTES} bytes")
    return prompt


# The texts compared were written by models that read code under review, so one could carry
# words aimed at the judge ("mark this a match"). The prompt tells the judge they are data, and
# every verdict is kept with its reason for a person to read; neither makes a model judge
# proof against that, which the benchmark this follows shares.
def first_json_object(text: str) -> object:
    """The first complete JSON value in a model's answer, code fence or not.

    Text after the value is ignored: a model sometimes adds a stray `"}` after a whole answer
    (PR 599, 2026-10-07). An answer cut off before its value closes still raises ValueError.
    """
    body = text.strip()
    if fenced := _FENCE.match(body):
        body = fenced.group(1)
    return json.JSONDecoder().raw_decode(body)[0]


def read_verdicts(text: str, golden: Sequence[Mapping], candidates: int) -> list[dict]:
    """The judge's answer, checked: one verdict per golden comment, each naming a real candidate.

    Raises JudgeError otherwise; a verdict that cannot be trusted is never counted.
    """
    try:
        rows = first_json_object(text)["results"]
    except (ValueError, KeyError, TypeError):
        raise JudgeError("the judge's answer is not the JSON object it was asked for") from None
    wanted = [g["id"] for g in golden]
    if (
        not isinstance(rows, list)
        or [isinstance(r, dict) and r.get("golden") for r in rows] != wanted
    ):
        raise JudgeError(
            "the judge's answer does not hold one verdict per golden comment, in order"
        )
    verdicts = []
    for row in rows:
        match, number, confidence = row.get("match"), row.get("candidate"), row.get("confidence")
        named = (
            isinstance(number, int) and not isinstance(number, bool) and 1 <= number <= candidates
        )
        sure = isinstance(confidence, (int, float)) and not isinstance(confidence, bool)
        if (
            not isinstance(match, bool)
            or not sure
            or not 0 <= confidence <= 1
            or (match and not named)
        ):
            raise JudgeError(f"the judge's verdict on {row['golden']} is not usable")
        verdicts.append({
            "golden": row["golden"], "match": match, "candidate": number if match else None,
            "confidence": float(confidence), "reasoning": str(row.get("reasoning") or ""),
        })  # fmt: skip
    return verdicts


def _document(golden, findings, verdicts, judge: dict) -> dict:
    """The stored result: a row per golden comment, and which findings matched none."""
    by_id = {g["id"]: g for g in golden}
    rows = []
    for verdict in verdicts:
        finding = findings[verdict["candidate"] - 1] if verdict["candidate"] else None
        rows.append({
            **verdict, "title": by_id[verdict["golden"]].get("title", ""),
            "finding": None if finding is None else {
                "reviewer": finding.reviewer, "title": finding.title, "file": finding.file,
                "line_start": finding.line_start, "line_end": finding.line_end,
            },
        })  # fmt: skip
    used = {v["candidate"] for v in verdicts if v["candidate"]}
    return {
        "schema_version": 1, "judge": judge, "results": rows,
        "found": sum(v["match"] for v in verdicts), "of": len(golden),
        "unmatched_candidates": [i for i in range(1, len(findings) + 1) if i not in used],
    }  # fmt: skip


def judge_review(
    golden: Sequence[Mapping],
    findings: Sequence[Finding],
    *,
    run_dir: Path | str,
    launch: Callable,
    runner: str = "codex",
    model: str = "gpt-6-luna",
    effort: str = "high",
    registry_path: Path | str | None = None,
    codex_home: Path | str | None = None,
    env_file: Path | str | None = None,
    timeout_sec: int = 600,
) -> dict:
    """Have the judge say which golden comments a review's findings state; write judge.json.

    `golden` is the `comments` list of a pull request's golden file. `launch` starts one agent
    process and watches it (the launcher's own). With no golden comment or no finding there is
    nothing to ask, and no agent is started. Each call keeps its files in a folder of its own
    under the run's `judge/`; `judge.json` in the run folder is the latest result.
    """
    run_dir = Path(run_dir).resolve()  # the judge starts in a folder of its own
    entry = load_registry(registry_path)[runner]
    judge = {"runner": runner, "model": model, "effort": effort, "tokens": None}
    if golden and findings:
        keys = read_secrets(entry, env_file)
        folder = run_dir / "judge" / f"{datetime.now(UTC):%Y%m%dT%H%M%S%fZ}"
        work, home = folder / "work", folder / "home"
        work.mkdir(parents=True)
        home.mkdir()
        prompt = render_judge_prompt(golden, findings)
        folder.joinpath("prompt.txt").write_text(prompt, encoding="utf-8")
        last = folder / "last_message.txt"
        ctx = {
            "workdir": str(work), "out_dir": str(work), "model": model, "effort": effort,
            "last_message": str(last), "home": str(home), "prompt": prompt,
            "codex_home": str(Path(codex_home or Path.home() / ".codex").resolve()),
            "sandbox": JUDGE_SANDBOX,
        }  # fmt: skip
        env = agent_env(entry, ctx, keys)
        argv = [a.format_map(ctx) for a in entry.argv]
        events, code, stopped = launch(argv, env, work, folder, timeout_sec, None, None, None)
        if stopped or code != 0 or not last.is_file():
            raise JudgeError(f"the judge did not answer (exit code {code}, {stopped or 'ended'})")
        verdicts = read_verdicts(last.read_text(encoding="utf-8"), golden, len(findings))
        meta = entry.parser(events, env)
        if meta is not None:
            judge |= {"model": meta.model or model, "effort": meta.effort or effort}
            judge["tokens"] = ((meta.usage or {}).get("total") or {}).get("total_tokens")
    else:
        verdicts = [
            {"golden": g["id"], "match": False, "candidate": None, "confidence": 1.0,
             "reasoning": "The review kept no finding."}
            for g in golden
        ]  # fmt: skip
    doc = _document(golden, findings, verdicts, judge)
    run_dir.joinpath(RESULT_NAME).write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc
