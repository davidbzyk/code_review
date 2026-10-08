"""No text given to an agent mentions a context file: reviewers search or read for themselves."""

from __future__ import annotations

from pathlib import Path

import pytest

from review_core.context.providers import load_registry
from review_core.launcher import render

ROOT = Path(__file__).resolve().parents[2]
SKILL_FILES = sorted((ROOT / "src" / "plugin" / "skills").glob("review-*/SKILL.md"))


def test_the_seven_reviewers_and_the_orchestrator_are_found():
    assert len(SKILL_FILES) == 9  # seven reviewers, the orchestrator and the validator


@pytest.mark.parametrize("path", SKILL_FILES, ids=lambda p: p.parent.name)
def test_no_skill_mentions_the_context_file(path):
    assert "context.md" not in path.read_text(encoding="utf-8")


def test_no_method_text_and_no_prompt_mentions_the_context_file():
    for name, row in load_registry().providers.items():
        assert "context.md" not in row.method, name
    assert "context.md" not in render.PROMPT.read_text(encoding="utf-8")
    assert not hasattr(render, "CONTEXT_FILE_NAME")
