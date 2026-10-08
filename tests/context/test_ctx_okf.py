"""The OKF provider through ctx, on the hand-written fixture bundle."""

from __future__ import annotations

import json

import pytest
from ctx_helpers import read_log, run_ctx

from review_core.context import okf_search

ROW = {"direct_hits": 2, "bm25_k1": 1.2, "bm25_b": 0.75, "title_weight": 3, "meta_weight": 2}


def ids(result) -> list[str]:
    """The item ids of a provider result, in order."""
    return [i["id"] for i in result["items"]]


def test_related_on_a_covered_path_returns_the_covering_note_then_neighbours(okf_store, tmp_path):
    log = tmp_path / "l"
    code, out, err = run_ctx(okf_store, "--log", log, "related", "src/orders.py")
    assert code == 0 and err == ""
    headers = [ln for ln in out.splitlines() if ln.startswith("[")]
    assert headers[0] == "[1] note building-blocks/orders  Order totals"
    assert {h.split()[2] for h in headers[1:]} == {"runtime/checkout-flow", "crosscutting/logging"}
    assert "compute_total" in out
    assert read_log(log)[0]["item_ids"][0] == "building-blocks/orders"


def test_related_on_an_uncovered_path_is_empty_with_the_reason(okf_store, tmp_path):
    code, out, _ = run_ctx(okf_store, "--log", tmp_path / "l", "related", "src/unknown.py")
    assert code == 0
    assert out.splitlines()[1:] == ["0 items, ~0 tokens; no note covers 'src/unknown.py'"]


def test_search_puts_direct_hits_first_then_one_hop_neighbours_by_touches_then_id(okf_store):
    result = okf_search.search(okf_store, "totals price discount", ROW)
    assert result["degraded"] is False
    assert set(ids(result)[:2]) == {"building-blocks/orders", "building-blocks/pricing"}
    # runtime/checkout-flow touches both direct hits; the other two touch one each (ties by id).
    assert ids(result)[2:] == [
        "runtime/checkout-flow",
        "crosscutting/logging",
        "runtime/audit-trail",
    ]
    for it in result["items"]:
        assert it["start"] == 0 and it["end"] == 0 and it["path"].endswith(".md")


def test_direct_hits_are_ranked_by_keyword_match(okf_store):
    top = okf_search.search(okf_store, "tax discount", dict(ROW, direct_hits=1))
    assert ids(top)[0] == "building-blocks/pricing"
    top = okf_search.search(okf_store, "order totals", dict(ROW, direct_hits=1))
    assert ids(top)[0] == "building-blocks/orders"


def test_search_with_one_direct_hit_adds_only_its_neighbours(okf_store):
    result = okf_search.search(okf_store, "audit record who changed", dict(ROW, direct_hits=1))
    assert ids(result) == ["runtime/audit-trail", "building-blocks/orders"]


def test_search_with_no_match_is_empty_with_a_reason(okf_store):
    result = okf_search.search(okf_store, "zzzz qqqq", ROW)
    assert result["items"] == [] and result["reason"] == "no note matches the query"


def test_search_through_ctx_uses_the_row_default_of_three_direct_hits(okf_store, tmp_path):
    code, out, _ = run_ctx(okf_store, "--log", tmp_path / "l", "search", "order totals")
    assert code == 0
    assert out.count("[") >= 3 and "note building-blocks/orders" in out


def test_a_deprecated_note_is_never_returned(okf_store, tmp_path):
    copy = tmp_path / "copy"
    import shutil

    shutil.copytree(okf_store, copy)
    note = copy / "bundle" / "runtime" / "audit-trail.md"
    note.write_text(note.read_text().replace("status: stable", "status: deprecated"))
    manifest = json.loads((copy / "manifest.json").read_text())
    result = okf_search.search(copy, "audit record who changed", dict(ROW, direct_hits=1))
    assert "runtime/audit-trail" not in ids(result)
    assert manifest["provider"] == "okf"


@pytest.mark.parametrize("text", ["", "a b", "!!!"])
def test_search_with_no_searchable_words_is_empty(okf_store, text):
    result = okf_search.search(okf_store, text, ROW)
    assert result["items"] == [] and "no searchable words" in result["reason"]
