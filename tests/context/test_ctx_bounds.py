"""Bounds on what a store may hold, each checked before the work it limits."""

from __future__ import annotations

import json
import os
import shutil
import textwrap
import time

import pytest
from ctx_helpers import read_log, run_ctx

from review_core.context import okf_search as okf
from review_core.context import vector_provider
from review_core.context.providers import StoreLimits, load_registry

PAD = ("x" * 1900 + "\n") * 3  # about 5.7 KB with no square bracket


def fresh(okf_store, tmp_path):
    """A writable copy of the OKF store."""
    return shutil.copytree(okf_store, tmp_path / "s")


def many_notes(count):
    """A mutation adding `count` tiny notes."""

    def edit(store):
        for i in range(count):
            (store / "bundle" / f"extra{i}.md").write_text("# n\n")

    return edit


def deep(store):
    folder = store / "bundle"
    for i in range(12):
        folder = folder / f"d{i}"
    folder.mkdir(parents=True)
    (folder / "n.md").write_text("# deep\n")


def graph_with(nodes=0, links=0):
    def edit(store):
        (store / "graph.json").write_text(
            json.dumps(
                {
                    "nodes": [{"id": str(i)} for i in range(nodes)],
                    "links": [{"source": "a", "target": "b"}] * links,
                }
            )
        )

    return edit


def claims(count, width=10):
    def edit(store):
        per = 100
        for i in range(0, count, per):
            body = "".join(f"  - {'a' * width}{j}\n" for j in range(min(per, count - i)))
            (store / "bundle" / f"c{i}.md").write_text(f"---\ntitle: t\ncovers:\n{body}---\nx\n")

    return edit


def brackets(notes, each):
    def edit(store):
        for i in range(notes):
            (store / "bundle" / f"b{i}.md").write_text("[" * each + "\n" + PAD)

    return edit


def replace_file(rel, text):
    def edit(store):
        (store / rel).write_text(text)

    return edit


def json_files(count, size):
    def edit(store):
        for i in range(count):
            (store / "bundle" / f"big{i}.json").write_text(" " * size)

    return edit


OVER = {
    "entries": lambda s: [(s / "bundle" / f"e{i}.json").write_text("{}") for i in range(700)],
    "notes": many_notes(301),
    "depth": deep,
    "note_bytes": replace_file("bundle/big.md", "x\n" * (okf.MAX_NOTE_BYTES // 2 + 30)),
    "json_bytes": replace_file("bundle/big.json", " " * 40_000),
    "total_bytes": json_files(okf.LIMITS.max_total_bytes // 30_000 + 4, 30_000),
    "graph_bytes": replace_file("graph.json", " " * (okf.MAX_GRAPH_BYTES + 1000)),
    "long_line": replace_file("bundle/line.md", "y" * (okf.MAX_LINE_CHARS + 1) + "\n"),
    "brackets_note": brackets(1, okf.MAX_BRACKETS_NOTE + 1),
    "brackets_total": brackets(
        okf.MAX_BRACKETS_TOTAL // (okf.MAX_BRACKETS_NOTE - 1) + 1, okf.MAX_BRACKETS_NOTE - 1
    ),
    "claims": claims(okf.MAX_RULES + 1),
    "claim_length": claims(1, width=okf.MAX_PATTERN_CHARS + 6),
    "manifest_bytes": replace_file("manifest.json", " " * (okf.LIMITS.max_file_bytes + 1000)),
    "top_level": replace_file("notes.md", "# stray\n"),
}


@pytest.mark.parametrize("name", sorted(OVER))
@pytest.mark.parametrize("verb,arg", [("search", "order totals"), ("related", "src/orders.py")])
def test_a_store_over_a_bound_is_refused_with_one_line_and_exit_2(
    okf_store, tmp_path, name, verb, arg
):
    store = fresh(okf_store, tmp_path)
    OVER[name](store)
    code, out, err = run_ctx(store, "--log", tmp_path / "l", verb, arg)
    assert code == 2 and out == "" and len(err.strip().splitlines()) == 1, err
    assert read_log(tmp_path / "l")[0]["exit_code"] == 2


@pytest.mark.parametrize("edit", [graph_with(nodes=2001), graph_with(links=10_001)])
def test_a_graph_with_too_many_nodes_or_links_is_refused_by_search(okf_store, tmp_path, edit):
    store = fresh(okf_store, tmp_path)
    edit(store)
    code, out, err = run_ctx(store, "--log", tmp_path / "l", "search", "order totals")
    assert code == 2 and out == "" and len(err.strip().splitlines()) == 1


def test_a_store_just_under_the_bounds_still_answers(okf_store, tmp_path):
    store = fresh(okf_store, tmp_path)
    many_notes(200)(store)
    brackets(8, okf.MAX_BRACKETS_NOTE - 1)(store)
    claims(okf.MAX_RULES - 50)(store)
    graph = json.loads((store / "graph.json").read_text())
    graph["nodes"] += [{"id": f"z{i}", "file_type": "other"} for i in range(1500)]
    (store / "graph.json").write_text(json.dumps(graph) + " " * 800_000)
    for verb, arg in (("search", "order totals"), ("related", "src/orders.py")):
        code, out, err = run_ctx(store, "--log", tmp_path / "l", verb, arg)
        assert code == 0, err


def test_an_argument_over_the_cap_is_refused_and_a_long_path_is_just_unmatched(okf_store, tmp_path):
    log = tmp_path / "l"
    code, out, err = run_ctx(okf_store, "--log", log, "search", "x " * 1001)
    assert code == 2 and len(err.strip().splitlines()) == 1
    assert len(read_log(log)[0]["argument"]) <= 2000
    code, out, _ = run_ctx(okf_store, "--log", log, "related", "a/" * 70)
    assert code == 0 and out.splitlines()[1].endswith("characters")


def test_a_store_path_that_is_a_link_is_refused(okf_store, tmp_path):
    link = tmp_path / "link"
    os.symlink(okf_store, link)
    code, out, err = run_ctx(link, "--log", tmp_path / "l", "search", "order totals")
    assert code == 2 and out == "" and len(err.strip().splitlines()) == 1


def test_a_manifest_that_is_a_link_is_refused(okf_store, tmp_path):
    store = fresh(okf_store, tmp_path)
    real = tmp_path / "elsewhere.json"
    shutil.move(store / "manifest.json", real)
    os.symlink(real, store / "manifest.json")
    code, _, err = run_ctx(store, "--log", tmp_path / "l", "search", "order totals")
    assert code == 2 and len(err.strip().splitlines()) == 1


def test_the_vector_store_listing_is_bounded_too(vector_store, tmp_path, monkeypatch):
    monkeypatch.setattr(vector_provider, "LIMITS", StoreLimits(3, 8, 1 << 30, 1 << 30))
    code, _, err = run_ctx(vector_store, "--log", tmp_path / "l", "search", "compute total")
    assert code == 2 and len(err.strip().splitlines()) == 1
    monkeypatch.setattr(vector_provider, "LIMITS", StoreLimits(5000, 8, 100, 1 << 30))
    code, _, _ = run_ctx(vector_store, "--log", tmp_path / "l", "search", "compute total")
    assert code == 2


N = okf.MAX_BRACKETS_NOTE


@pytest.mark.parametrize(
    "head", ["[[" * (N // 2), "[a](" * (N // 4) + "[" * (N // 2), "[" * N, "[[a|" * (N // 4)]
)
def test_the_vendored_link_patterns_stay_fast_at_the_bounds(okf_store, tmp_path, head):
    store = fresh(okf_store, tmp_path)
    for i in range(okf.MAX_BRACKETS_TOTAL // N - 1):  # as many full notes as the total allows
        (store / "bundle" / f"adv{i}.md").write_text(head + "\n" + PAD)
    start = time.perf_counter()
    code, _, err = run_ctx(store, "--log", tmp_path / "l", "related", "src/orders.py")
    took = time.perf_counter() - start
    assert code == 0, err
    assert took < 0.5, took  # measured 0.1 s or less on a laptop; the slack is for loaded CI


def test_the_coverage_match_stays_fast_at_the_claim_and_path_bounds(okf_store, tmp_path):
    store = fresh(okf_store, tmp_path)
    for i in range(3):
        pattern = "/".join(["**", "*a*"] * 10)[:64]
        body = "".join(f"  - {pattern}\n" for _ in range(85))
        (store / "bundle" / f"c{i}.md").write_text(f"---\ntitle: t\ncovers:\n{body}---\nx\n")
    start = time.perf_counter()
    code, _, err = run_ctx(store, "--log", tmp_path / "l", "related", "a/" * 63 + "a")
    assert code == 0, err
    assert time.perf_counter() - start < 0.5


def test_deeply_nested_frontmatter_is_an_error_or_an_answer_never_a_hang(okf_store, tmp_path):
    store = fresh(okf_store, tmp_path)
    flow = "[" * 55 + "]" * 55
    block = "".join(" " * i + f"k{i}:\n" for i in range(60))
    (store / "bundle" / "nest.md").write_text(f"---\ntitle: t\nx: {flow}\n{block}---\nbody\n")
    start = time.perf_counter()
    code, _, _ = run_ctx(store, "--log", tmp_path / "l", "related", "src/orders.py")
    assert code in (0, 1, 2) and time.perf_counter() - start < 0.5


def test_the_log_caps_the_item_ids_and_a_call_prints_a_bounded_number_of_items(
    tmp_path, monkeypatch
):
    mods = tmp_path / "mods"
    mods.mkdir()
    (mods / "many_provider.py").write_text(
        textwrap.dedent(
            """
            def search(store_dir, text, settings):
                items = [{"id": "i%d" % n, "title": "t", "path": "p", "start": 1, "end": 1,
                          "text": "x"} for n in range(500)]
                return {"items": items, "degraded": False, "reason": None}
            """
        )
    )
    monkeypatch.syspath_prepend(str(mods))
    reg_file = tmp_path / "providers.toml"
    reg_file.write_text(
        '[defaults]\nbudget_tokens = 100000\n[many]\ncommand = true\nstore_dir = "many"\n'
        'build = "many_provider:search"\nsearch = "many_provider:search"\n'
        'related = "many_provider:search"\n'
    )
    store = tmp_path / "store"
    store.mkdir()
    (store / "manifest.json").write_text('{"provider": "many", "store_sha256": "x"}')
    log = tmp_path / "l"
    code, out, _ = run_ctx(store, "--log", log, "search", "q", registry=load_registry(reg_file))
    rec = read_log(log)[0]
    assert code == 0 and out.count("<<<item") == 100
    assert len(rec["item_ids"]) == 50 and rec["item_count"] == 100
