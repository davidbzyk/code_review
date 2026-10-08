"""The search path stays light (no tree-sitter, no chunker) and its CLI works end to end."""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from ce_helpers import build

SRC = Path(__file__).resolve().parents[2] / "src"
PACKAGE = SRC / "context_engine"
QUERY_MODULES = ["__main__", "embed", "retrieve", "store", "tokens"]
BUILD_MODULES = {"chunk", "index", "report", "change", "settings", "build_cli"}


def all_imports(path: Path) -> set[str]:
    """Every module name imported anywhere in a file, including inside functions."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module or "")
    return names


@pytest.mark.parametrize("module", QUERY_MODULES)
def test_search_path_never_imports_the_chunker_or_tree_sitter(module):
    for name in all_imports(PACKAGE / f"{module}.py"):
        root = name.split(".")[0]
        assert not root.startswith("tree_sitter"), f"{module} imports {name}"
        if root == "context_engine" and "." in name:
            leaf = name.split(".")[1]
            lazy = module == "__main__" and leaf == "build_cli"
            assert leaf not in BUILD_MODULES or lazy, f"{module} imports {name}"


def test_main_imports_the_build_side_only_inside_the_build_branch():
    path = PACKAGE / "__main__.py"
    module_level = set()
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.ImportFrom):
            module_level.add(node.module)
        elif isinstance(node, ast.Import):
            module_level |= {a.name for a in node.names}
    assert not any("build_cli" in m or "index" in m or "chunk" in m for m in module_level)
    assert "context_engine.build_cli" in all_imports(path)


def test_importing_the_query_commands_does_not_load_tree_sitter():
    code = (
        "import sys, context_engine.__main__, context_engine.retrieve; "
        "bad = [m for m in sys.modules if m.startswith('tree_sitter') or "
        "m in ('context_engine.chunk', 'context_engine.index')]; print(bad)"
    )
    done = subprocess.run(
        [sys.executable, "-c", code], cwd=SRC, capture_output=True, text=True, timeout=60
    )
    assert done.stdout.strip() == "[]", done.stdout + done.stderr


def run_cli(python: str, *args: str) -> subprocess.CompletedProcess:
    """Run the query CLI from the src folder with a given interpreter and no key."""
    env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    env["PYTHONPATH"] = str(SRC)
    return subprocess.run(
        [python, "-m", "context_engine", *args],
        cwd=SRC,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_query_cli_end_to_end_with_this_python(tmp_path):
    out, _, _ = build(tmp_path, "s", tmp_path / "cache")
    done = run_cli(sys.executable, "search", str(out), "compute total items", "--k", "2")
    assert done.returncode == 0, done.stderr
    payload = json.loads(done.stdout)
    assert payload["degraded"] is False and len(payload["results"]) == 2
    done = run_cli(sys.executable, "related", str(out), "app.py")
    assert json.loads(done.stdout)["results"]
    done = run_cli(sys.executable, "related", str(out), "parse.py")
    assert json.loads(done.stdout)["results"] == []
    assert run_cli(sys.executable, "search", str(tmp_path / "nowhere"), "x").returncode == 2


def test_real_embedder_without_a_key_degrades_loudly(tmp_path):
    out, _, _ = build(tmp_path, "s", tmp_path / "cache")
    manifest = json.loads((out / "manifest.json").read_text())
    manifest["model"] = "text-embedding-3-small"
    manifest["vector_size"] = 64
    manifest["settings"]["embedding"]["vector_size"] = 64
    (out / "manifest.json").write_text(json.dumps(manifest))
    done = run_cli(sys.executable, "search", str(out), "compute total items")
    payload = json.loads(done.stdout)
    assert payload["degraded"] is True
    assert "OPENAI_API_KEY is not set" in payload["reason"]
    assert payload["results"]


def test_build_script_is_executable_and_points_at_the_cli():
    script = PACKAGE / "build_index.sh"
    assert os.access(script, os.X_OK)
    assert "python -m context_engine build" in script.read_text()
