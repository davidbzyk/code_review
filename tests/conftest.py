"""Fixtures shared by every test folder."""

from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def engine_scratch(tmp_path_factory, monkeypatch):
    """Keep the vector engine's scratch folder, and the TMPDIR it sets, inside the test tree."""
    before = os.environ.get("TMPDIR")
    monkeypatch.setenv("CONTEXT_ENGINE_SCRATCH", str(tmp_path_factory.mktemp("engine-scratch")))
    yield
    if before is None:
        os.environ.pop("TMPDIR", None)
    else:
        os.environ["TMPDIR"] = before
