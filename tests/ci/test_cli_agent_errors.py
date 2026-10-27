"""A review whose agent exits non-zero prints the agent's own error, so a CI log says why."""

import json
from pathlib import Path

from review_core.ci.github import credentials
from review_core.cli import agent_errors

# The two failure shapes `codex exec --json` writes to stdout, as the launcher saves them.
REFRESH = "Your access token could not be refreshed because your refresh token was already used."
EVENTS = [
    {"type": "thread.started", "thread_id": "t1"},
    {"type": "error", "message": REFRESH},
    {"type": "turn.failed", "error": {"message": "stream disconnected before completion"}},
]


def test_a_failed_run_names_the_agents_error_events(tmp_path: Path) -> None:
    """The error and turn.failed messages come back in order."""
    (tmp_path / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in EVENTS))
    assert agent_errors(tmp_path) == [REFRESH, "stream disconnected before completion"]


def test_stderr_lines_are_shown_with_long_tokens_blanked(tmp_path: Path) -> None:
    """With no error event, the end of stderr is shown; anything token-shaped is blanked."""
    token = "eyJ" + "a1B2" * 20
    (tmp_path / "stderr.txt").write_text(f"starting\nError: login failed for {token}\n")
    assert agent_errors(tmp_path) == ["starting", "Error: login failed for [redacted]"]


def test_a_run_with_nothing_recorded_gives_nothing(tmp_path: Path) -> None:
    """A missing run folder or empty files give no lines, never an exception."""
    assert agent_errors(tmp_path / "missing") == []


def test_a_multi_line_message_prints_as_one_line(tmp_path: Path) -> None:
    """Every printed line carries the prefix, so no line of it starts a workflow command."""
    event = {"type": "error", "message": "first part\n::warning::second part"}
    (tmp_path / "events.jsonl").write_text(json.dumps(event) + "\n")
    assert agent_errors(tmp_path) == ["first part ::warning::second part"]


def test_a_credential_of_the_run_is_blanked_in_every_form(tmp_path: Path) -> None:
    """A login value shorter than the backstop, with `/`, is blanked as is and reversed."""
    secret = "rt_ab/cd+efGHij/klmnoPQ"
    login = tmp_path / "auth.json"
    login.write_text(json.dumps({"tokens": {"refresh_token": secret}}))
    (tmp_path / "stderr.txt").write_text(f"refresh failed: {secret}\nechoed: {secret[::-1]}\n")
    lines = agent_errors(tmp_path, credentials([login], []))
    assert lines == ["refresh failed: [redacted]", "echoed: [redacted]"]


def test_an_error_event_with_no_message_still_shows_stderr(tmp_path: Path) -> None:
    """A blank message is no error text, so the end of stderr is shown instead."""
    (tmp_path / "events.jsonl").write_text(json.dumps({"type": "error", "message": ""}) + "\n")
    (tmp_path / "stderr.txt").write_text("Error: workspace routing discovery unauthorized (401)\n")
    assert agent_errors(tmp_path) == ["Error: workspace routing discovery unauthorized (401)"]


def test_a_line_holding_a_spaced_out_credential_is_withheld(tmp_path: Path) -> None:
    """A credential with spaces or backslashes inserted, which the poster's guard also catches,
    withholds the whole line instead of printing its pieces."""
    secret = "rt_ab/cd+efGHij/klmnoPQ"
    login = tmp_path / "auth.json"
    login.write_text(json.dumps({"tokens": {"refresh_token": secret}}))
    spaced = f"{secret[:8]} {secret[8:15]}\\\\{secret[15:]}"
    (tmp_path / "stderr.txt").write_text(f"refresh failed: {spaced}\nretrying\n")
    lines = agent_errors(tmp_path, credentials([login], []))
    assert lines == ["[withheld: this line holds a credential of the run]", "retrying"]
