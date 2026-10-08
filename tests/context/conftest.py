"""Fixtures for the context command tests; plain helpers live in ctx_helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
from ctx_helpers import BASE_TREE, HEAD_TREE, OKF_BUNDLE, write_tree

from review_core.context import build_stores


@pytest.fixture(scope="session")
def vector_store(tmp_path_factory) -> Path:
    """A vector store built with the offline embedder from a two-file tree."""
    root = tmp_path_factory.mktemp("vector")
    snaps = root / "snaps" / "toy"
    write_tree(snaps / "base", BASE_TREE)
    write_tree(snaps / "head", HEAD_TREE)
    code = build_stores.main(
        [
            "--case",
            "toy",
            "--arm",
            "vector",
            "--fake-embedder",
            "--snapshots-dir",
            str(root / "snaps"),
            "--out",
            str(root / "out"),
            "--cache-dir",
            str(root / "cache"),
        ]
    )
    assert code == 0
    return root / "out" / "toy" / "vector"


@pytest.fixture(scope="session")
def okf_store(tmp_path_factory) -> Path:
    """An OKF store built from the hand-written fixture bundle and the staged tool."""
    root = tmp_path_factory.mktemp("okf")
    code = build_stores.main(
        [
            "--case",
            "toy",
            "--arm",
            "okf",
            "--okf-bundle",
            str(OKF_BUNDLE),
            "--out",
            str(root / "out"),
            "--cache-dir",
            str(root / "cache"),
        ]
    )
    assert code == 0
    return root / "out" / "toy" / "okf"
