"""Path, quote and confidence gates."""

import subprocess

from review_core.aggregator import gates
from review_core.aggregator.confidence import passes_floor, severity_rank

from .conftest import make_finding as f
from .conftest import make_repo


def test_quote_matches_ignoring_indentation_and_blank_edge_lines():
    text = "def f():\n        x = 1\n    y = 2\nreturn y\n"
    assert gates.quote_in_text("x = 1", text)
    assert gates.quote_in_text("\n  x = 1\n y = 2\n\n", text)
    assert not gates.quote_in_text("y = 2\nx = 1", text)
    assert not gates.quote_in_text("x = 99", text)
    assert not gates.quote_in_text("   \n", text)


def test_reader_serves_head_for_new_and_base_for_old_from_git_not_the_working_tree(tmp_path):
    repo = make_repo(tmp_path, {"a.py": "old = 1\n"}, {"a.py": "new = 2\n"})
    (repo / "a.py").write_text("uncommitted = 3\n")
    read = gates.GitReader(repo, "base", "head").read
    assert read("new", "a.py") == "new = 2\n"
    assert read("old", "a.py") == "old = 1\n"
    assert read("new", "missing.py") is None


def test_ref_check_accepts_a_commit_and_rejects_unknown_or_option_like_refs(tmp_path):
    repo = make_repo(tmp_path, {"a.py": "1\n"}, {"a.py": "2\n"})
    assert gates.ref_exists(repo, "head")
    assert not gates.ref_exists(repo, "nope")
    assert not gates.ref_exists(repo, "--help")


def test_confidence_floor_is_inclusive():
    assert passes_floor(f(confidence=50), 50)
    assert not passes_floor(f(confidence=25), 50)


def test_severity_order_puts_p0_first():
    assert severity_rank("P0") < severity_rank("P1") < severity_rank("P2") < severity_rank("P3")


def test_unsafe_path_never_reaches_git(tmp_path, monkeypatch):
    repo = make_repo(tmp_path, {"a.py": "1\n"}, {"a.py": "2\n"})
    asked = []
    real = subprocess.run

    def spy(cmd, *a, **kw):
        asked.append(cmd)
        return real(cmd, *a, **kw)

    monkeypatch.setattr(gates.subprocess, "run", spy)
    reader = gates.GitReader(repo, "base", "head")
    kept, dropped = gates.apply_path_and_quote_gates([f(file="../outside.py")], reader)
    assert kept == [] and [d["reason"] for d in dropped] == ["out_of_snapshot"]
    assert not any("outside.py" in part for cmd in asked for part in cmd)
