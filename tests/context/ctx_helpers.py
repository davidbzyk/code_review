"""Shared helpers for the ctx tests: stores built once per session from small inputs."""

from __future__ import annotations

import io
import json
from pathlib import Path

from review_core.context import ctx

REPO = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"
OKF_BUNDLE = FIXTURES / "okf-bundle"

BASE_TREE = {
    "util.py": (
        "def compute_total(items):\n"
        "    total = 0\n"
        "    for item in items:\n"
        "        total += item.price * item.qty\n"
        "    return total\n"
        "\n\n"
        "def format_label(name):\n"
        "    return name.title()\n"
    ),
    "app.py": (
        "from util import format_label\n"
        "\n\n"
        "def render(order):\n"
        "    label = format_label(order.name)\n"
        "    return label\n"
        "\n\n"
        "def unrelated_helper(config):\n"
        "    return config.get('mode')\n"
    ),
    "parse.py": (
        "def parse_config(text):\n"
        "    pairs = [line.split('=') for line in text.splitlines()]\n"
        "    return dict(pairs)\n"
    ),
    "report.py": ("def summarize_total(items):\n    return sum(item.price for item in items)\n"),
}
HEAD_TREE = dict(BASE_TREE)
HEAD_TREE["app.py"] = BASE_TREE["app.py"].replace(
    "    return label\n", "    amount = compute_total(order.items)\n    return label\n", 1
)


def write_tree(root: Path, files: dict[str, str]) -> Path:
    """Write a dict of relative path to text under root and return root."""
    for rel, text in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


def run_ctx(store, *args, registry=None) -> tuple[int, str, str]:
    """Run ctx in-process on a store; returns (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = ctx.main(
        [*(["--store", str(store)] if store is not None else []), *map(str, args)],
        registry=registry,
        stdout=out,
        stderr=err,
    )
    return code, out.getvalue(), err.getvalue()


def read_log(path: Path) -> list[dict]:
    """Every line of a ctx log parsed as JSON."""
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
