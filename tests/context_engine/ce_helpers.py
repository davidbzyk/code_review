"""Shared builders for the context-engine tests."""

from __future__ import annotations

from pathlib import Path

from context_engine.embed import hashed_bow_embedder
from context_engine.index import build_index
from context_engine.settings import load_settings

FAKE_DIM = 64

BASE = {
    "util.py": """def compute_total(items):
    total = 0
    for item in items:
        total += item.price * item.qty
    return total


def format_label(name):
    return name.title()
""",
    "app.py": """from util import format_label


def render(order):
    label = format_label(order.name)
    return label


def unrelated_helper(config):
    return config.get("mode")
""",
    "parse.py": """def parse_config(text):
    pairs = [line.split("=") for line in text.splitlines()]
    return dict(pairs)
""",
    "README.md": "# Shop\n\nA tiny order renderer.\n",
}

HEAD = dict(BASE)
HEAD["app.py"] = """from util import format_label, compute_total


def render(order):
    label = format_label(order.name)
    amount = compute_total(order.items)
    return label


def unrelated_helper(config):
    return config.get("mode")
"""


def write_tree(root: Path, files: dict[str, str]) -> Path:
    """Write a dict of path -> text under root and return root."""
    for rel, text in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


def fake_settings(**chunk) -> dict:
    """Settings with no merging, so every item is its own chunk, plus any chunk overrides."""
    return load_settings({"chunk": {"merge_target_lines": 0, **chunk}})


class CountingEmbedder:
    """The hashed bag-of-words fake, counting how many texts it was asked to embed."""

    def __init__(self, dim: int = FAKE_DIM) -> None:
        self.inner = hashed_bow_embedder(dim)
        self.texts = 0

    def __call__(self, texts):
        self.texts += len(texts)
        return self.inner(texts)


def build(tmp: Path, name: str, cache: Path, base=BASE, head=HEAD, settings=None, embed=None):
    """Build a store for base/head dicts into tmp/name; returns (out folder, stats, embedder)."""
    embed = embed or CountingEmbedder()
    settings = settings or fake_settings()
    base_dir = write_tree(tmp / f"{name}-base", base)
    head_dir = write_tree(tmp / f"{name}-head", head)
    out = tmp / name
    stats = build_index(
        base_dir,
        head_dir,
        out,
        cache,
        embed,
        model="fake",
        vector_size=FAKE_DIM,
        settings=settings,
    )
    return out, stats, embed
