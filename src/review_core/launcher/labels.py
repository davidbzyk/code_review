"""Which of our reviewers should have raised each golden comment: a label from a model.

Most golden comments carry no category (the Codex bot gives none), so to compare what the bots
raised with what our reviewers found, a model sorts each comment into one of our reviewers'
categories. The categories are the reviewers themselves, described by each reviewer skill's own
`description`, so a new reviewer is a new skill and nothing here. One call per pull request;
the labels go to `golden_labels.json` beside the golden file and are a model's judgement, kept
with its reason for each so a person can check and correct them.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from string import Template

from review_core.contracts.models import REVIEWERS
from review_core.launcher.judge import JUDGE_SANDBOX, MAX_PROMPT_BYTES, first_json_object
from review_core.launcher.runners import agent_env, load_registry, read_secrets

PROMPT = Path(__file__).with_name("label_prompt.md")
RESULT_NAME = "golden_labels.json"
SKILLS = Path(__file__).resolve().parents[2] / "plugin" / "skills"


class LabelError(ValueError):
    """The labeller could not be asked, or its answer does not label every comment."""


def kinds(skills: Path | str = SKILLS) -> list[dict]:
    """Each reviewer's name and its skill's description, as the labeller reads them."""
    out = []
    for name in REVIEWERS:
        text = (Path(skills) / f"review-{name.replace('_', '-')}" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        found = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
        if not found:
            raise LabelError(f"the {name} reviewer's skill has no description")
        out.append({"category": name, "description": found.group(1).strip()})
    return out


def render_label_prompt(golden: Sequence[Mapping], skills: Path | str = SKILLS) -> str:
    """The labeller's prompt for one pull request's golden comments."""
    comments = [{"golden": g["id"], "comment": g["comment"]} for g in golden]
    prompt = Template(PROMPT.read_text(encoding="utf-8")).substitute(
        kinds=json.dumps(kinds(skills), indent=1), comments=json.dumps(comments, indent=1)
    )
    if len(prompt.encode()) > MAX_PROMPT_BYTES:
        raise LabelError(f"the labeller's prompt is over {MAX_PROMPT_BYTES} bytes")
    return prompt


def read_labels(text: str, golden: Sequence[Mapping]) -> dict[str, dict]:
    """The labeller's answer as {golden id: {category, reason}}; every comment, known names."""
    try:
        rows = first_json_object(text)["labels"]
    except (ValueError, KeyError, TypeError) as exc:
        raise LabelError(f"the labeller's answer is not the labels JSON: {exc}") from exc
    got = {}
    for row in rows:
        if not isinstance(row, Mapping) or row.get("category") not in REVIEWERS:
            raise LabelError(f"a label names no known reviewer: {row!r}")
        got[str(row.get("golden"))] = {"category": row["category"],
                                       "reason": str(row.get("reason", ""))}  # fmt: skip
    missing = [g["id"] for g in golden if g["id"] not in got]
    if missing:
        raise LabelError(f"the labeller left out {', '.join(missing)}")
    return {g["id"]: got[g["id"]] for g in golden}


def label_golden(
    golden: Sequence[Mapping],
    *,
    folder: Path | str,
    launch: Callable,
    runner: str,
    model: str,
    effort: str,
    registry_path: Path | str | None = None,
    codex_home: Path | str | None = None,
    env_file: Path | str | None = None,
    skills: Path | str = SKILLS,
    timeout_sec: int = 600,
) -> dict:
    """Label one pull request's golden comments and write `golden_labels.json` in `folder`."""
    folder = Path(folder).resolve()
    entry = load_registry(registry_path)[runner]
    labels: dict[str, dict] = {}
    if golden:
        work_root = folder / "labels" / f"{datetime.now(UTC):%Y%m%dT%H%M%S%fZ}"
        work, home = work_root / "work", work_root / "home"
        work.mkdir(parents=True)
        home.mkdir()
        prompt = render_label_prompt(golden, skills)
        work_root.joinpath("prompt.txt").write_text(prompt, encoding="utf-8")
        last = work_root / "last_message.txt"
        ctx = {
            "workdir": str(work), "out_dir": str(work), "model": model, "effort": effort,
            "last_message": str(last), "home": str(home), "prompt": prompt,
            "codex_home": str(Path(codex_home or Path.home() / ".codex").resolve()),
            "sandbox": JUDGE_SANDBOX,
        }  # fmt: skip
        env = agent_env(entry, ctx, read_secrets(entry, env_file))
        argv = [a.format_map(ctx) for a in entry.argv]
        _events, code, stopped = launch(argv, env, work, work_root, timeout_sec, None, None, None)
        if stopped or code != 0 or not last.is_file():
            raise LabelError(
                f"the labeller did not answer (exit code {code}, {stopped or 'ended'})"
            )
        labels = read_labels(last.read_text(encoding="utf-8"), golden)
    doc = {"labeller": {"runner": runner, "model": model, "effort": effort}, "labels": labels}
    folder.joinpath(RESULT_NAME).write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc
