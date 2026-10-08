"""The prompt and the `ctx` wrapper text come from one module that the Harbor generator shares."""

import subprocess
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src"


def test_render_module_imports_no_process_rollout_or_runner_code():
    code = (
        "import sys\n"
        "import review_core.launcher.render\n"
        "bad = [m for m in ('subprocess', 'review_core.launcher.run', "
        "'review_core.launcher.rollout', 'review_core.launcher.runners') if m in sys.modules]\n"
        "print(bad)\n"
    )
    done = subprocess.run(
        [sys.executable, "-S", "-c", code],
        env={"PYTHONPATH": str(SRC)},
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == "[]"


def test_render_prompt_fills_the_template_and_appends_extras():
    from review_core.launcher.render import prompt_extras, render_prompt

    extras = prompt_extras(["a.py"], "  fix  the\nbug ", "ctx-cmd")
    text = render_prompt("B", "H", "/o", "/sk", extras)
    assert "refs B and H" in text
    assert "/o/findings.<reviewer>.json" in text
    assert "The skills are installed in: /sk\n" in text
    assert "with exactly this command: review-aggregate\n" in text and "aggregate.py" not in text
    assert text.endswith(
        "\nYour slice is only these files: a.py\n"
        "What the change is meant to do: fix the bug\n"
        "Context search command: ctx-cmd\n"
    )


def test_prompt_extras_refuse_a_path_outside_the_repository():
    from review_core.launcher.render import prompt_extras

    with pytest.raises(ValueError):
        prompt_extras(["../x"], None, None)


def test_ctx_wrapper_text_pins_the_five_variables_and_the_interpreter():
    from review_core.launcher.render import ctx_wrapper_text

    text = ctx_wrapper_text("/usr/bin/python3", "/src", "/st", "/o/ctx-log.jsonl", "/o/scr", None)
    lines = text.splitlines()
    assert lines[0] == "#!/bin/sh"
    assert "export PYTHONPATH=/src" in lines
    assert "export CTX_STORE=/st" in lines
    assert "export CTX_LOG=/o/ctx-log.jsonl" in lines
    assert "export CONTEXT_ENGINE_SCRATCH=/o/scr" in lines
    assert "unset CTX_ENV_FILE" in lines
    assert lines[-1] == 'exec /usr/bin/python3 -P -m review_core.context.ctx "$@"'


def test_ctx_wrapper_text_can_map_another_variable_to_the_embedder_key():
    from review_core.launcher.render import ctx_wrapper_text

    text = ctx_wrapper_text("python3", "/s", "/st", "/l", "/c", None, key_from="CTX_EMBEDDER_KEY")
    assert 'export OPENAI_API_KEY="$CTX_EMBEDDER_KEY"' in text.splitlines()
    plain = ctx_wrapper_text("python3", "/s", "/st", "/l", "/c", None)
    assert "OPENAI_API_KEY" not in plain


def test_the_arms_method_is_one_line_before_the_search_command():
    from review_core.launcher.render import prompt_extras

    extras = prompt_extras(["a.py"], "adds x", "ctx-cmd", "Read the\n  notes first.")
    assert extras == [
        "Your slice is only these files: a.py",
        "What the change is meant to do: adds x",
        "How to gather context: Read the notes first.",
        "Context search command: ctx-cmd",
    ]
    assert prompt_extras(None, None, None, "  ") == []
    assert prompt_extras(None, None, None, "Read the code.") == [
        "How to gather context: Read the code."
    ]
