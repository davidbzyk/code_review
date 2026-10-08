"""Building a store: determinism, the vector cache, the change ranges and the coverage floor."""

from __future__ import annotations

import json
import shutil

import pytest
from ce_helpers import BASE, FAKE_DIM, HEAD, CountingEmbedder, build, fake_settings, write_tree

from context_engine.build_cli import main as build_main
from context_engine.embed import hashed_bow_embedder
from context_engine.report import CoverageError
from context_engine.retrieve import related, search
from context_engine.settings import load_settings
from context_engine.store import load_store
from review_core.hashing import tree_sha256

FILES = ["chunks.jsonl", "vectors.f32", "related.json", "changed.json", "settings.json"]


def read_all(folder):
    """Bytes of every store file."""
    return {name: (folder / name).read_bytes() for name in FILES}


def ask(folder, text):
    """Top search results (path, start, score) of a store for a query, with the fake embedder."""
    out = search(load_store(folder), text, 10, hashed_bow_embedder(FAKE_DIM))
    return [(r["path"], r["start"], r["score"]) for r in out["results"]]


def test_two_builds_have_the_same_hash_and_results_and_the_second_embeds_nothing(tmp_path):
    cache = tmp_path / "cache"
    out1, stats1, embed1 = build(tmp_path, "one", cache)
    assert embed1.texts > 0
    out2, stats2, embed2 = build(tmp_path, "two", cache)
    assert embed2.texts == 0
    assert read_all(out1) == read_all(out2)
    assert stats1.store_sha256 == stats2.store_sha256
    assert ask(out1, "compute total items") == ask(out2, "compute total items")
    assert (out1 / "db").is_dir()


def test_a_fresh_cache_gives_the_same_store_and_results(tmp_path):
    out1, stats1, _ = build(tmp_path, "one", tmp_path / "cache-a")
    out2, stats2, embed = build(tmp_path, "two", tmp_path / "cache-b")
    assert embed.texts > 0
    assert stats1.store_sha256 == stats2.store_sha256
    assert ask(out1, "format label") == ask(out2, "format label")


def test_manifest_has_hash_settings_and_no_timestamps(tmp_path):
    out, stats, _ = build(tmp_path, "one", tmp_path / "cache")
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["model"] == "fake" and manifest["vector_size"] == 64
    assert manifest["schema_version"] == 1
    assert manifest["settings"]["chunk"]["merge_target_lines"] == 0
    assert manifest["counts"]["chunks"] == len((out / "chunks.jsonl").read_text().splitlines())
    assert json.loads((out / "settings.json").read_text()) == manifest["settings"]
    assert "estimated_embed_tokens" in manifest["counts"]
    assert manifest["report"]["languages"]["python"]["files_chunked"] == 3
    assert not any(word in json.dumps(manifest) for word in ("timestamp", "created", 'time"'))
    staged = tmp_path / "staged"
    staged.mkdir()
    for name in FILES:
        shutil.copy(out / name, staged / name)
    assert manifest["store_sha256"] == tree_sha256(staged) == stats.store_sha256


def test_chunks_are_sorted_and_vectors_match(tmp_path):
    out, _, _ = build(tmp_path, "one", tmp_path / "cache")
    rows = [json.loads(line) for line in (out / "chunks.jsonl").read_text().splitlines()]
    assert [(r["path"], r["start"]) for r in rows] == sorted((r["path"], r["start"]) for r in rows)
    assert len((out / "vectors.f32").read_bytes()) == len(rows) * 64 * 4
    assert set(rows[0]) == {"path", "start", "end", "language", "signature", "code"}


def test_changed_json_holds_base_side_ranges(tmp_path):
    out, _, _ = build(tmp_path, "one", tmp_path / "cache")
    changed = json.loads((out / "changed.json").read_text())["files"]
    assert list(changed) == ["app.py"]
    ranges = changed["app.py"]["ranges"]
    # head line 1 replaces base line 1; head line 6 is inserted after base line 5
    assert {"start": 1, "end": 1, "kind": "change"} in ranges
    assert {"start": 5, "end": 5, "kind": "insert"} in ranges
    assert changed["app.py"]["status"] == "modified"


def test_added_and_deleted_files_are_recorded(tmp_path):
    base = {**BASE, "gone.py": "def old():\n    return 1\n"}
    head = {**HEAD, "new.py": "def fresh():\n    return 2\n"}
    del head["parse.py"]
    out, _, _ = build(tmp_path, "one", tmp_path / "cache", base=base, head=head)
    changed = json.loads((out / "changed.json").read_text())["files"]
    assert changed["new.py"] == {"status": "added", "ranges": []}
    assert changed["parse.py"]["status"] == "deleted"
    assert changed["parse.py"]["ranges"] == [{"start": 1, "end": 3, "kind": "delete"}]


def test_related_holds_a_query_per_changed_file(tmp_path):
    out, _, _ = build(tmp_path, "one", tmp_path / "cache")
    related = json.loads((out / "related.json").read_text())["queries"]
    assert list(related) == ["app.py"]
    assert "compute_total" in related["app.py"]["terms"]
    assert len(related["app.py"]["vector"]) == 64


def test_build_fails_below_the_coverage_floor_and_writes_nothing(tmp_path):
    big = "".join(f"x{n} = {n}\n" for n in range(40))
    base = {**BASE, "huge.py": big}
    settings = load_settings(
        {"chunk": {"file_size_limit_bytes": 100}, "report": {"coverage_min_lines": 20}}
    )
    with pytest.raises(CoverageError, match="python"):
        build(tmp_path, "one", tmp_path / "cache", base=base, head=base, settings=settings)
    assert not (tmp_path / "one").exists() or not any((tmp_path / "one").iterdir())


def test_cli_build_exits_non_zero_with_a_clear_message(tmp_path, capsys):
    big = "".join(f"x{n} = {n}\n" for n in range(40))
    base = write_tree(tmp_path / "b", {**BASE, "huge.py": big})
    head = write_tree(tmp_path / "h", {**BASE, "huge.py": big})
    code = build_main(
        [
            "build",
            str(base),
            str(head),
            str(tmp_path / "out"),
            "--cache-dir",
            str(tmp_path / "c"),
            "--fake-embedder",
            "--set",
            "chunk.file_size_limit_bytes=100",
            "--set",
            "report.coverage_min_lines=20",
        ]
    )
    assert code != 0
    assert "coverage below the floor" in capsys.readouterr().err


def test_parse_failures_and_skips_are_listed_in_the_report(tmp_path):
    base = {**BASE, "broken.rs": "pub fn oops( -> {\n", "logo.png": "\x00\x01binary"}
    out, _, _ = build(tmp_path, "one", tmp_path / "cache", base=base, head=base)
    report = json.loads((out / "manifest.json").read_text())["report"]
    assert report["languages"]["rust"]["parse_failures"] == ["broken.rs"]
    assert {"path": "logo.png", "reason": "binary"} in report["excluded"]


def test_default_settings_build_does_not_embed_the_head_tree(tmp_path):
    out, _, _ = build(tmp_path, "one", tmp_path / "cache", settings=load_settings())
    rows = [json.loads(line) for line in (out / "chunks.jsonl").read_text().splitlines()]
    assert all("compute_total(order.items)" not in r["code"] for r in rows)


def read_guard(monkeypatch, limit=1_000_000):
    """Make Path.read_bytes/read_text fail on any file bigger than `limit` bytes."""
    import pathlib

    real_bytes, real_text = pathlib.Path.read_bytes, pathlib.Path.read_text

    def guard(real):
        def wrapped(self, *args, **kwargs):
            if self.is_file() and self.stat().st_size > limit:
                raise AssertionError(f"read a {self.stat().st_size}-byte file whole: {self}")
            return real(self, *args, **kwargs)

        return wrapped

    monkeypatch.setattr(pathlib.Path, "read_bytes", guard(real_bytes))
    monkeypatch.setattr(pathlib.Path, "read_text", guard(real_text))


def notes(out):
    """The change notes of a built store's report."""
    return json.loads((out / "manifest.json").read_text())["report"]["change_notes"]


def test_a_changed_file_that_grew_past_the_size_limit_is_modified_not_deleted(tmp_path):
    base = {**BASE, "grow.py": "x = 1\n" * 10}
    head = {**BASE, "grow.py": "x = 1\n" * 40}
    settings = load_settings({"chunk": {"file_size_limit_bytes": 100}})
    out, _, _ = build(tmp_path, "one", tmp_path / "cache", base=base, head=head, settings=settings)
    changed = json.loads((out / "changed.json").read_text())["files"]
    assert changed["grow.py"]["status"] == "modified"
    assert changed["grow.py"]["ranges"] == [{"start": 1, "end": 10, "kind": "change"}]


def test_a_5mb_changed_file_is_never_read_whole(tmp_path, monkeypatch):
    read_guard(monkeypatch)
    base = {**BASE, "big.py": "".join(f"v{n} = {n}\n" for n in range(100))}
    head = {**BASE, "big.py": "wide = 1\n" * 600_000}
    out, _, _ = build(tmp_path, "one", tmp_path / "cache", base=base, head=head)
    changed = json.loads((out / "changed.json").read_text())["files"]
    assert changed["big.py"] == {
        "status": "modified",
        "ranges": [{"start": 1, "end": 100, "kind": "change"}],
    }
    assert {"path": "big.py", "reason": "changed file over the size limit"} in notes(out)
    hits = search(load_store(out), "v1 v2 v50", 20, hashed_bow_embedder(FAKE_DIM))["results"]
    assert hits and all(h["path"] != "big.py" for h in hits)
    terms = json.loads((out / "related.json").read_text())["queries"]["big.py"]["terms"]
    assert terms and len(terms) <= 64


def test_a_new_oversize_changed_file_is_added_with_bounded_text(tmp_path, monkeypatch):
    read_guard(monkeypatch)
    head = {**BASE, "gen.py": "token = 1\n" * 600_000}
    out, _, _ = build(tmp_path, "one", tmp_path / "cache", head=head)
    changed = json.loads((out / "changed.json").read_text())["files"]
    assert changed["gen.py"] == {"status": "added", "ranges": []}
    assert {"path": "gen.py", "reason": "changed file over the size limit"} in notes(out)


def test_two_unrelated_8000_line_files_are_not_diffed(tmp_path):
    import time

    base = {**BASE, "a.py": "".join(f"left{n} = {n}\n" for n in range(8000))}
    head = {**BASE, "a.py": "".join(f"right{n} = -{n}\n" for n in range(8000))}
    started = time.monotonic()
    out, _, _ = build(tmp_path, "one", tmp_path / "cache", base=base, head=head)
    assert time.monotonic() - started < 2.0 + 3.0  # build includes chunking 8000 lines twice
    changed = json.loads((out / "changed.json").read_text())["files"]
    assert changed["a.py"]["ranges"] == [{"start": 1, "end": 8000, "kind": "change"}]
    assert {"path": "a.py", "reason": "change too large to diff"} in notes(out)


def test_diff_budget_is_a_setting(tmp_path):
    import time

    from context_engine.change import compute_change

    base = {"a.py": "".join(f"left{n} = {n}\n" for n in range(8000))}
    head = {"a.py": "".join(f"right{n} = -{n}\n" for n in range(8000))}
    started = time.monotonic()
    files, hunks, found = compute_change(base, head, {}, load_settings())
    assert time.monotonic() - started < 2.0
    assert files["a.py"]["ranges"] == [{"start": 1, "end": 8000, "kind": "change"}]
    assert len(hunks["a.py"]) <= 6000
    assert found == [{"path": "a.py", "reason": "change too large to diff"}]


def test_a_base_file_over_the_limit_is_counted_without_being_read_whole(tmp_path, monkeypatch):
    read_guard(monkeypatch)
    base = {**BASE, "dump.py": "x = 1\n" * 400_000}
    settings = load_settings({"chunk": {"merge_target_lines": 0}, "report": {"coverage_floor": 0}})
    out, _, _ = build(tmp_path, "one", tmp_path / "cache", base=base, head=base, settings=settings)
    py = json.loads((out / "manifest.json").read_text())["report"]["languages"]["python"]
    assert {"path": "dump.py", "reason": "too-large"} in py["files_skipped"]
    assert py["lines_seen"] > 300_000


def test_a_file_with_a_very_long_line_is_skipped_and_listed(tmp_path):
    base = {**BASE, "wide.py": "x = '" + "a" * 30_000 + "'\n"}
    out, _, _ = build(tmp_path, "one", tmp_path / "cache", base=base, head=base)
    py = json.loads((out / "manifest.json").read_text())["report"]["languages"]["python"]
    assert {"path": "wide.py", "reason": "line-too-long"} in py["files_skipped"]
    rows = [json.loads(line) for line in (out / "chunks.jsonl").read_text().splitlines()]
    assert all(r["path"] != "wide.py" for r in rows)


def test_a_cache_file_of_the_wrong_size_is_a_miss_without_being_read(tmp_path, monkeypatch):
    from context_engine.index import VectorCache

    cache = VectorCache(tmp_path / "c", "fake", 4)
    cache.put("t", [1.0, 2.0, 3.0, 4.0])
    assert cache.get("t") == [1.0, 2.0, 3.0, 4.0]
    path = cache._path("t")
    path.write_bytes(b"x" * 5_000_000)
    read_guard(monkeypatch)
    assert cache.get("t") is None


def reference_overlap(ranges, start, end):
    """The plain rule: change ranges overlap by line; an insert after g needs start <= g < end."""
    for rng in ranges:
        if rng["kind"] == "insert":
            if start <= rng["start"] < end:
                return True
        elif rng["start"] <= end and rng["end"] >= start:
            return True
    return False


def test_the_touch_index_matches_the_reference_rule():
    import random

    from context_engine.change import Touched

    rng = random.Random(5)
    for _ in range(200):
        ranges, pos = [], 0
        for _ in range(rng.randrange(0, 8)):
            pos += rng.randrange(1, 6)
            if rng.random() < 0.4:
                ranges.append({"start": pos, "end": pos, "kind": "insert"})
            else:
                end = pos + rng.randrange(0, 4)
                ranges.append({"start": pos, "end": end, "kind": "change"})
                pos = end
        changed = {"f.py": {"status": "modified", "ranges": ranges}}
        index = Touched(changed)
        for _ in range(30):
            start = rng.randrange(1, 40)
            end = start + rng.randrange(0, 8)
            assert index.overlaps("f.py", start, end) == reference_overlap(ranges, start, end)


def test_repeated_lines_over_the_budget_are_not_diffed():
    import time

    from context_engine.change import compute_change

    base = {"a.py": "x = 1\n" * 8000}
    head = {"a.py": "x = 1\n" * 7999 + "y = 2\n"}
    started = time.monotonic()
    files, _, notes = compute_change(base, head, {}, load_settings())
    assert time.monotonic() - started < 1.0
    assert files["a.py"]["ranges"] == [{"start": 1, "end": 8000, "kind": "change"}]
    assert notes == [{"path": "a.py", "reason": "change too large to diff"}]


def test_many_files_each_under_the_diff_budget_cannot_exceed_the_budget_for_the_whole_change():
    # One file under the per-file limit takes seconds to diff. A change made of many must not.
    import time

    from context_engine.change import TOTAL_NOTE, compute_change

    settings = load_settings()
    settings["change"]["diff_cell_budget"] = 1_000_000
    settings["change"]["diff_total_cell_budget"] = 2_500_000
    base = {f"f{n:02d}.py": "x = 1\n" * 900 for n in range(40)}
    head = {f"f{n:02d}.py": "x = 1\n" * 899 + "y = 2\n" for n in range(40)}
    started = time.monotonic()
    files, _, notes = compute_change(base, head, {}, settings)
    assert time.monotonic() - started < 5.0
    whole = [
        p for p, f in files.items() if f["ranges"] == [{"start": 1, "end": 900, "kind": "change"}]
    ]
    # 900 x 900 cells a file: three fit in the total, in path order; the rest count as whole.
    assert sorted(set(files) - set(whole)) == ["f00.py", "f01.py", "f02.py"]
    assert {n["reason"] for n in notes} == {TOTAL_NOTE} and len(notes) == 37


def test_a_tree_with_more_files_than_the_limit_fails_the_build_with_a_clear_message(tmp_path):
    import pytest

    from context_engine.index import TreeTooLarge

    base = {**BASE, **{f"many/f{n}.py": f"v = {n}\n" for n in range(30)}}
    settings = fake_settings()
    settings["chunk"]["max_files"] = 20
    with pytest.raises(TreeTooLarge, match="more than 20 entries"):
        build(tmp_path, "one", tmp_path / "cache", base=base, head=base, settings=settings)


def settings_with(**tables):
    """Fake-embedder settings (no merging) with `table={key: value}` overrides."""
    return load_settings({"chunk": {"merge_target_lines": 0}, **tables})


def test_walk_refuses_a_directory_over_the_limit_before_sorting_or_opening(tmp_path, monkeypatch):
    from context_engine import index
    from context_engine.index import TreeTooLarge, scan_tree
    from context_engine.report import Report

    for n in range(60):
        (tmp_path / f"f{n}.py").write_text("x = 1\n")

    def boom(*args, **kwargs):
        raise AssertionError("work done before the count check")

    monkeypatch.setattr(index, "sorted", boom, raising=False)
    monkeypatch.setattr(index, "_inspect", boom)
    with pytest.raises(TreeTooLarge, match="more than 50 entries"):
        scan_tree(tmp_path, settings_with(chunk={"max_files": 50}), Report())


def test_walk_counts_empty_directories_too(tmp_path):
    from context_engine.index import TreeTooLarge, scan_tree
    from context_engine.report import Report

    for n in range(60):
        (tmp_path / f"d{n}").mkdir()
    with pytest.raises(TreeTooLarge):
        scan_tree(tmp_path, settings_with(chunk={"max_files": 50}), Report())


def test_walk_refuses_a_chain_of_directories_deeper_than_the_limit(tmp_path):
    from context_engine.index import TreeTooLarge, scan_tree
    from context_engine.report import Report

    deep = tmp_path.joinpath(*["d"] * 12)
    deep.mkdir(parents=True)
    (deep / "x.py").write_text("x = 1\n")
    with pytest.raises(TreeTooLarge, match="deeper than 8"):
        scan_tree(tmp_path, settings_with(chunk={"max_depth": 8}), Report())
    assert load_settings()["chunk"]["max_depth"] == 40


def test_walk_order_is_files_then_subdirectories_each_sorted(tmp_path):
    import os

    from context_engine.index import scan_tree
    from context_engine.report import Report

    write_tree(
        tmp_path,
        {
            "b.py": "b = 1\n",
            "a.py": "a = 1\n",
            "z/y.py": "y = 1\n",
            "m/k.py": "k = 1\n",
            "m/c.py": "c = 1\n",
        },
    )
    expected = []
    for folder, dirs, names in os.walk(tmp_path):
        dirs.sort()
        expected += [os.path.relpath(os.path.join(folder, n), tmp_path) for n in sorted(names)]
    assert list(scan_tree(tmp_path, load_settings(), Report())) == expected


def test_a_build_over_the_embedding_budget_fails_before_the_first_embed_call(tmp_path):
    from context_engine.index import EmbedBudgetError

    settings = settings_with(embedding={"max_build_tokens": 50})
    embed = CountingEmbedder()
    with pytest.raises(EmbedBudgetError, match=r"at most \d+ tokens.*limit of 50"):
        build(tmp_path, "one", tmp_path / "cache", settings=settings, embed=embed)
    assert embed.texts == 0


def test_the_same_build_passes_when_every_vector_is_cached(tmp_path):
    cache = tmp_path / "cache"
    build(tmp_path, "one", cache)
    embed = CountingEmbedder()
    out, _, _ = build(
        tmp_path,
        "two",
        cache,
        settings=settings_with(embedding={"max_build_tokens": 1}),
        embed=embed,
    )
    assert embed.texts == 0 and (out / "manifest.json").exists()
    assert load_settings()["embedding"]["max_build_tokens"] == 40_000_000


def test_cli_reports_an_over_budget_build_with_exit_code_3(tmp_path, capsys):
    base = write_tree(tmp_path / "b", BASE)
    head = write_tree(tmp_path / "h", HEAD)
    code = build_main(
        [
            "build",
            str(base),
            str(head),
            str(tmp_path / "out"),
            "--cache-dir",
            str(tmp_path / "c"),
            "--fake-embedder",
            "--set",
            "embedding.max_build_tokens=50",
        ]
    )
    assert code == 3 and "limit of 50" in capsys.readouterr().err


def test_related_queries_stop_at_the_file_cap_and_the_rest_are_listed(tmp_path):
    from context_engine.change import NO_RELATED_NOTE

    base = {**BASE, **{f"m{n}.py": f"v = {n}\n" for n in range(4)}}
    head = {**HEAD, **{f"m{n}.py": f"v = {n}\nw = {n}\n" for n in range(4)}}
    settings = settings_with(change={"max_related_files": 2})
    out, _, _ = build(tmp_path, "one", tmp_path / "cache", base=base, head=head, settings=settings)
    queries = json.loads((out / "related.json").read_text())["queries"]
    assert list(queries) == ["app.py", "m0.py"]  # path order
    left = {n["path"] for n in notes(out) if n["reason"] == NO_RELATED_NOTE}
    assert left == {"m1.py", "m2.py", "m3.py"}
    answer = related(load_store(out), "m2.py", 3)
    assert answer["results"] == [] and answer["reason"] == NO_RELATED_NOTE
    assert load_settings()["change"]["max_related_files"] == 500


def test_hunk_text_is_cut_when_it_is_collected():
    from context_engine.change import compute_change

    cap = load_settings()["change"]["query_max_chars"]
    big = "".join(f"line{n} = {n}\n" for n in range(5000))
    files, hunks, _ = compute_change(
        {"gone.py": big, "mod.py": "a = 1\n"}, {"new.py": big, "mod.py": big}, {}, load_settings()
    )
    assert {p: len(h) <= cap for p, h in hunks.items()} == {
        "gone.py": True,
        "new.py": True,
        "mod.py": True,
    }
    assert files["gone.py"]["status"] == "deleted" and files["new.py"]["status"] == "added"


def test_store_json_over_the_size_limit_is_refused_unread(tmp_path, monkeypatch):
    from context_engine import store as store_module

    out, _, _ = build(tmp_path, "one", tmp_path / "cache")
    monkeypatch.setattr(store_module, "MAX_JSON_BYTES", 100)
    with pytest.raises(ValueError, match=r"\.json is larger than 100 bytes"):
        load_store(out)
    assert store_module.MAX_JSON_BYTES == 100
    monkeypatch.undo()
    assert load_store(out) is not None


def test_a_store_whose_table_disagrees_with_the_manifest_is_refused(tmp_path):
    out, _, _ = build(tmp_path, "one", tmp_path / "cache")
    manifest = json.loads((out / "manifest.json").read_text())
    manifest["counts"]["chunks"] += 1
    (out / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="rows"):
        load_store(out)


def test_a_tree_holding_more_bytes_than_the_limit_is_refused_before_any_file_is_read(tmp_path):
    import pytest

    from context_engine.index import TreeTooLarge

    base = {**BASE, "big/a.txt": "x" * 4000, "big/b.txt": "y" * 4000}
    settings = fake_settings()
    settings["chunk"]["max_tree_bytes"] = 5000
    with pytest.raises(TreeTooLarge, match="more than 5000 bytes"):
        build(tmp_path, "one", tmp_path / "cache", base=base, head=base, settings=settings)


def test_the_embedding_budget_counts_an_upper_bound_not_an_estimate(tmp_path):
    # Dense text has far more tokens than characters over three. No text has more tokens than
    # bytes, so the limit is checked against bytes and cannot be slipped under.
    from context_engine.index import EmbedBudgetError

    dense = "\n".join("\U0001f600" * 40 for _ in range(30))  # 1,200 characters, 4,800 bytes
    base = {"notes.md": dense + "\n"}
    _, stats, _ = build(tmp_path, "probe", tmp_path / "cache-probe", base=base, head=base)
    by_estimate = stats.estimated_tokens
    assert by_estimate < 1000
    # A limit the characters-over-three estimate fits under, with room; the bytes do not.
    settings = settings_with(embedding={"max_build_tokens": by_estimate + 500})
    embed = CountingEmbedder()
    with pytest.raises(EmbedBudgetError, match="at most"):
        build(
            tmp_path,
            "one",
            tmp_path / "cache",
            base=base,
            head=base,
            settings=settings,
            embed=embed,
        )
    assert embed.texts == 0
