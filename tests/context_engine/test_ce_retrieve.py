"""Search and related over a built store."""

from __future__ import annotations

import json

import pytest
from ce_helpers import FAKE_DIM, build

from context_engine.change import Touched
from context_engine.embed import EmbedError, hashed_bow_embedder
from context_engine.retrieve import related, search
from context_engine.settings import load_settings
from context_engine.store import load_store


@pytest.fixture()
def store(tmp_path):
    out, _, _ = build(tmp_path, "s", tmp_path / "cache")
    return load_store(out)


def span(result):
    """(path, start, end) of one result."""
    return result["path"], result["start"], result["end"]


def test_search_never_returns_a_chunk_overlapping_the_change(store):
    embed = hashed_bow_embedder(FAKE_DIM)
    query = "def render order label format_label unrelated_helper compute_total"
    out = search(store, query, 20, embed)
    assert out["results"]
    for hit in out["results"]:
        assert not Touched(store.changed).overlaps(*span(hit))
    assert all(span(h)[0] != "app.py" or span(h)[1] > 5 for h in out["results"])
    assert any(h["path"] == "util.py" for h in out["results"])


def test_search_fields_and_fusion(store):
    out = search(store, "compute total items price", 3, hashed_bow_embedder(FAKE_DIM))
    assert out["degraded"] is False and out["mode"] == "hybrid"
    top = out["results"][0]
    assert top["path"] == "util.py" and top["signature"] == "def compute_total(items):"
    assert set(top) == {"path", "start", "end", "signature", "score", "code"}
    assert "total += item.price" in top["code"]


def test_failing_embedder_gives_bm25_marked_degraded(store):
    def broken(texts):
        raise EmbedError("environment variable OPENAI_API_KEY is not set")

    out = search(store, "compute total items", 3, broken)
    assert out["degraded"] is True
    assert "OPENAI_API_KEY is not set" in out["reason"]
    assert out["mode"] == "bm25"
    assert out["results"][0]["signature"] == "def compute_total(items):"


def test_no_embedder_is_degraded_too(store):
    out = search(store, "compute total", 3, None)
    assert out["degraded"] is True and out["reason"]


def test_wrong_size_vector_is_degraded(store):
    out = search(store, "compute total", 3, lambda texts: [[1.0, 2.0]])
    assert out["degraded"] is True and "size" in out["reason"]


def test_related_returns_the_callee_definition_without_an_embedder(store, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    out = related(store, "app.py", 3)
    assert out["degraded"] is False
    top = [h["signature"] for h in out["results"]]
    assert "def compute_total(items):" in top
    assert all(not Touched(store.changed).overlaps(*span(h)) for h in out["results"])


def test_related_on_an_untouched_path_is_empty_with_a_reason(store):
    out = related(store, "parse.py", 5)
    assert out["results"] == []
    assert "does not touch" in out["reason"]
    assert related(store, "./parse.py", 5)["results"] == []


def test_results_are_deterministic(store):
    embed = hashed_bow_embedder(FAKE_DIM)
    runs = [json.dumps(search(store, "format label name", 5, embed)) for _ in range(3)]
    assert len(set(runs)) == 1
    runs = [json.dumps(related(store, "app.py", 5)) for _ in range(3)]
    assert len(set(runs)) == 1


def test_rrf_constant_comes_from_the_settings(tmp_path):
    settings = load_settings({"chunk": {"merge_target_lines": 0}, "retrieval": {"rrf_k": 10}})
    out, _, _ = build(tmp_path, "k10", tmp_path / "cache", settings=settings)
    top = search(load_store(out), "compute total items", 3, hashed_bow_embedder(FAKE_DIM))
    # the best chunk is first in both the keyword and the vector ranking: 2 / (K + 1)
    assert top["results"][0]["score"] == pytest.approx(2 / 11, abs=1e-6)


def test_keyword_search_matches_any_term(store):
    out = search(store, "compute label", 10, lambda texts: (_ for _ in ()).throw(EmbedError("x")))
    sigs = {r["signature"] for r in out["results"]}
    assert "def compute_total(items):" in sigs and "def format_label(name):" in sigs


def test_ties_break_by_path_then_start_line():
    from context_engine.retrieve import _hits

    rows = [
        (1.0, {"path": "b.py", "start": 1, "end": 2, "signature": "", "code": ""}),
        (1.0, {"path": "a.py", "start": 9, "end": 9, "signature": "", "code": ""}),
        (1.0, {"path": "a.py", "start": 2, "end": 2, "signature": "", "code": ""}),
    ]
    assert [(h["path"], h["start"]) for h in _hits(rows, 3)] == [
        ("a.py", 2),
        ("a.py", 9),
        ("b.py", 1),
    ]


def test_overlap_rules():
    changed = {
        "f.py": {
            "status": "modified",
            "ranges": [
                {"start": 10, "end": 12, "kind": "change"},
                {"start": 20, "end": 20, "kind": "insert"},
            ],
        },
        "gone.py": {"status": "deleted", "ranges": [{"start": 1, "end": 5, "kind": "delete"}]},
    }
    touched = Touched(changed)
    assert touched.overlaps("f.py", 1, 10)
    assert touched.overlaps("f.py", 12, 30)
    assert not touched.overlaps("f.py", 1, 9)
    assert touched.overlaps("f.py", 15, 25)  # insert gap inside the chunk
    assert not touched.overlaps("f.py", 15, 20)  # insert lands after the chunk's end
    assert not touched.overlaps("f.py", 21, 30)
    assert touched.overlaps("gone.py", 3, 4)
    assert not touched.overlaps("other.py", 1, 9)


def test_the_database_gets_its_own_scratch_folder_and_never_the_ambient_one(tmp_path, monkeypatch):
    # Lance makes a spill folder when it connects. An agent sandbox denies the ambient temp
    # folder, which broke every search; the engine now names the folder itself.
    from ce_helpers import build

    from context_engine import store as store_module
    from context_engine.retrieve import search
    from context_engine.store import load_store

    scratch = tmp_path / "scratch"
    monkeypatch.setenv(store_module.SCRATCH_ENV, str(scratch))
    out, _, embed = build(tmp_path, "s", tmp_path / "cache")
    monkeypatch.setenv("TMPDIR", str(tmp_path / "ambient-that-does-not-exist"))
    result = search(load_store(out), "compute total", 2, embed)
    assert result["results"] and scratch.is_dir()
    assert not (tmp_path / "ambient-that-does-not-exist").exists()


def test_a_scratch_folder_that_is_a_link_is_refused(tmp_path, monkeypatch):
    import pytest

    from context_engine import store as store_module

    target = tmp_path / "elsewhere"
    target.mkdir()
    link = tmp_path / "scratch"
    link.symlink_to(target, target_is_directory=True)
    monkeypatch.setenv(store_module.SCRATCH_ENV, str(link))
    with pytest.raises(ValueError, match="scratch"):
        store_module.connect(tmp_path / "db")
    assert list(target.iterdir()) == []


def test_each_process_cleans_up_its_own_scratch_and_leaves_the_others(tmp_path):
    # Reviewers call the command in parallel and share one scratch root. A call removes only
    # what it made, from inside its own process, so nothing outside the sandbox has to delete.
    import os
    import subprocess
    import sys
    from pathlib import Path

    from ce_helpers import build

    out, _, _ = build(tmp_path, "s", tmp_path / "cache")
    root = tmp_path / "shared-scratch"
    other = root / "call-of-another-process"
    other.mkdir(parents=True)
    (other / "spill").write_text("in use")
    src = Path(__file__).resolve().parents[2] / "src"
    code = (
        "import os, sys\n"
        "from context_engine.store import load_store\n"
        "load_store(sys.argv[1])\n"
        "print(os.environ['TMPDIR'])\n"
    )
    env = {"PATH": os.environ["PATH"], "PYTHONPATH": str(src), "CONTEXT_ENGINE_SCRATCH": str(root)}
    done = subprocess.run(
        [sys.executable, "-c", code, str(out)], capture_output=True, text=True, check=False, env=env
    )
    assert done.returncode == 0, done.stderr[-300:]
    used = Path(done.stdout.strip())
    assert used.parent == root and used != other  # its own folder, under the root
    assert sorted(p.name for p in root.iterdir()) == ["call-of-another-process"]
    assert (other / "spill").read_text() == "in use"


@pytest.mark.parametrize("embedded", [True, False])
def test_ranking_never_pulls_the_stored_vectors_or_terms_into_memory(store, embedded):
    # Every eligible row is ranked; carrying each chunk's full embedding made one lookup
    # about 0.4 GB, and twenty at once ran the machine out of memory (2026-10-07).
    from context_engine.retrieve import _rows

    vector = hashed_bow_embedder(FAKE_DIM)(["compute total"])[0] if embedded else None
    rows, _ = _rows(store, ["compute", "total"], vector)
    assert rows
    for _, row in rows:
        assert "vector" not in row and "terms" not in row
