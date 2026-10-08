"""`ctx check`: the test a store must pass before any agent is started against it."""

from __future__ import annotations

import json

import pytest
from context.ctx_helpers import run_ctx

from review_core.context import vector_provider


@pytest.mark.parametrize("fixture", ("vector_store", "okf_store"))
def test_a_working_store_passes_and_the_check_is_not_counted_as_a_search(
    fixture, request, tmp_path
):
    store = request.getfixturevalue(fixture)
    log = tmp_path / "log.jsonl"
    code, out, err = run_ctx(store, "--log", str(log), "check", "app.py")
    assert (code, err) == (0, "")
    # One line a person can read: which kind of store, and that both verbs answered.
    assert out.startswith("ctx check: ok") and "search" in out and "related" in out
    assert out.count("\n") == 1
    # The log is the record of what the reviewers looked up; the check is not one of those.
    assert not log.exists()


def test_the_check_works_without_a_path(vector_store, tmp_path):
    code, out, _ = run_ctx(vector_store, "--log", str(tmp_path / "l"), "check")
    assert code == 0 and "search" in out and "related" not in out


def test_a_store_whose_search_falls_back_to_keywords_fails_the_check(
    vector_store, tmp_path, monkeypatch
):
    # The embedding service cannot be reached: a search still answers, by keywords only. A run
    # on such a store is not a run of the vector arm, so the check refuses it.
    def no_service(_manifest):
        def embed(_texts):
            raise RuntimeError("no route to the embedding service")

        return embed

    monkeypatch.setattr(vector_provider, "make_embedder", no_service)
    code, out, err = run_ctx(vector_store, "--log", str(tmp_path / "l"), "check")
    assert code == 1 and out == ""
    assert err.startswith("ctx: check failed: search answered in a reduced way")


def test_a_store_that_cannot_be_read_fails_the_check(tmp_path):
    store = tmp_path / "store"
    store.mkdir()
    (store / "manifest.json").write_text(json.dumps({"provider": "vector", "store_sha256": "a"}))
    code, out, err = run_ctx(store, "--log", str(tmp_path / "l"), "check")
    assert code in (1, 2) and out == "" and err.startswith("ctx: check failed: ")
