"""Chunking: syntax units, windows, parse failures and coverage."""

from __future__ import annotations

from pathlib import Path

from context_engine.chunk import chunk_file
from context_engine.settings import load_settings

FIXTURES = Path(__file__).parent / "fixtures"
NO_MERGE = {"chunk": {"merge_target_lines": 0}}


def run(name: str, overrides: dict | None = None, rel: str | None = None):
    """Chunk one fixture file and return the ChunkResult."""
    settings = load_settings(overrides)
    text = (FIXTURES / name).read_text(encoding="utf-8")
    return chunk_file(rel or name, text, settings), text


def nonblank(text: str) -> list[int]:
    """1-based numbers of the non-blank lines of a text."""
    return [n for n, line in enumerate(text.split("\n"), 1) if line.strip()]


def covered(result) -> list[int]:
    """Every line number covered by the chunks, with repeats."""
    return [n for c in result.chunks for n in range(c.start, c.end + 1)]


def test_rust_items_one_chunk_each():
    result, _ = run("items.rs", NO_MERGE)
    signatures = [c.signature for c in result.chunks if c.signature]
    assert signatures == [
        "pub fn add(a: i32, b: i32) -> i32",
        "pub struct Counter",
        "impl Counter",
        "pub fn describe(counter: &Counter) -> String",
    ]
    assert all(c.path == "items.rs" and c.language == "rust" for c in result.chunks)
    add = next(c for c in result.chunks if c.signature.startswith("pub fn add"))
    assert (add.start, add.end) == (3, 7)  # the doc comment is attached to the function
    assert add.code.startswith("/// Add two numbers.")
    assert not result.parse_failed


def test_rust_large_impl_splits_per_method():
    settings = {"chunk": {"merge_target_lines": 0, "size_cap_lines": 8, "size_cap_chars": 400}}
    result, _ = run("items.rs", settings)
    sigs = [c.signature for c in result.chunks]
    assert "impl Counter :: pub fn new() -> Self" in sigs
    assert "impl Counter :: pub fn bump(&mut self, key: &str) -> u32" in sigs


def test_small_units_merge_up_to_target():
    result, _ = run("items.rs")  # default merge target is 30 lines
    assert len(result.chunks) < 5
    assert result.chunks[0].start == 1


def test_svelte_script_is_typescript_with_original_lines():
    result, text = run("widget.svelte", NO_MERGE)
    script = [c for c in result.chunks if c.language == "typescript"]
    assert script, "script block produced no typescript chunks"
    increment = next(c for c in script if "function increment" in c.signature)
    lines = text.split("\n")
    assert lines[increment.start - 1].lstrip().startswith("function increment")
    assert increment.start == 7
    markup = [c for c in result.chunks if c.language == "svelte"]
    assert any("<button" in c.code for c in markup)
    assert not any("function increment" in c.code for c in markup)


def test_python_decorator_stays_with_function():
    result, _ = run("decorated.py", NO_MERGE)
    square = next(c for c in result.chunks if "slow_square" in c.signature)
    assert square.code.startswith("@cache_result")
    assert square.signature == "def slow_square(n):"


def test_parse_failure_falls_back_to_windows_and_is_flagged():
    result, text = run("broken.rs", {"chunk": {"window_lines": 4}})
    assert result.parse_failed
    assert result.chunks, "a failing file is never dropped"
    assert all(c.signature == "" for c in result.chunks)
    assert {n for n in nonblank(text)} <= set(covered(result))


def test_unit_over_cap_is_split_and_covers_each_line_once():
    result, text = run("long_fn.rs", {"chunk": {"size_cap_lines": 40, "size_cap_chars": 100000}})
    assert len(result.chunks) >= 4
    assert all(c.end - c.start + 1 <= 40 for c in result.chunks)
    assert all(c.signature == "pub fn long_one(input: &[i32]) -> i32" for c in result.chunks)
    assert {n for n in nonblank(text)} <= set(covered(result))


def test_chars_cap_splits_lines_too():
    result, _ = run("long_fn.rs", {"chunk": {"size_cap_lines": 1000, "size_cap_chars": 500}})
    assert all(len(c.code) <= 500 or c.start == c.end for c in result.chunks)


def test_no_chunk_overlaps_for_every_fixture():
    for path in sorted(FIXTURES.iterdir()):
        for overrides in (None, NO_MERGE, {"chunk": {"size_cap_lines": 5, "size_cap_chars": 90}}):
            result, _ = run(path.name, overrides)
            seen = covered(result)
            assert len(seen) == len(set(seen)), f"{path.name} {overrides}: a line is covered twice"


def test_plain_text_goes_in_windows():
    settings = load_settings({"chunk": {"window_lines": 3}})
    text = "a\nb\nc\nd\ne\nf\ng\n"
    result = chunk_file("notes.md", text, settings)
    assert [(c.start, c.end) for c in result.chunks] == [(1, 3), (4, 6), (7, 7)]
    assert {c.language for c in result.chunks} == {"markdown"}


def test_chunk_text_is_path_signature_code():
    result, _ = run("items.rs", NO_MERGE)
    chunk = result.chunks[0]
    assert chunk.embed_text() == f"{chunk.path}\n{chunk.signature}\n{chunk.code}"


def test_typescript_top_level_declarations_are_units():
    result, _ = run("service.ts", NO_MERGE)
    sigs = [c.signature for c in result.chunks if c.signature]
    assert "export interface Options" in sigs
    assert "export function clamp(value: number, low: number, high: number): number" in sigs
    assert "export class Registry" in sigs
    assert any(s.startswith("export const DEFAULT_OPTIONS") for s in sigs)
    assert all(c.language == "typescript" for c in result.chunks)


def test_typescript_class_members_are_split_when_the_class_is_large():
    result, text = run("service.ts", {"chunk": {"merge_target_lines": 0, "size_cap_lines": 10}})
    sigs = [c.signature for c in result.chunks]
    assert "export class Registry :: add(name: string, weight: number): void" in sigs
    assert "export class Registry :: total(): number" in sigs
    total = next(c for c in result.chunks if c.signature.endswith(":: total(): number"))
    assert text.split("\n")[total.start - 1].strip() == "total(): number {"


def test_svelte_with_two_script_blocks_and_crlf_line_endings():
    settings = load_settings(NO_MERGE)
    text = (
        '<script context="module">\nexport const KIND = 1;\n</script>\n\n'
        "<script>\nlet n = 0;\nfunction bump() {\n  n += 1;\n}\n</script>\n\n<p>{n}</p>\n"
    ).replace("\n", "\r\n")
    result = chunk_file("two.svelte", text, settings)
    ts = [c for c in result.chunks if c.language == "typescript"]
    assert [c.start for c in ts] == [2, 6, 7]
    assert "KIND" in ts[0].code and "\r" not in ts[0].code
    assert any("<p>{n}</p>" in c.code for c in result.chunks if c.language == "svelte")
    seen = [n for c in result.chunks for n in range(c.start, c.end + 1)]
    assert len(seen) == len(set(seen))


def test_svelte_script_that_does_not_parse_is_flagged():
    text = "<script>\nfunction (( {\n</script>\n<p>hi</p>\n"
    result = chunk_file("bad.svelte", text, load_settings())
    assert result.parse_failed
    assert any("function ((" in c.code for c in result.chunks)


def test_unclosed_script_lines_are_chunked_in_linear_time():
    import time

    text = "<script>\n" * 20000
    started = time.monotonic()
    result = chunk_file("many.svelte", text, load_settings())
    assert time.monotonic() - started < 1.0
    seen = [n for c in result.chunks for n in range(c.start, c.end + 1)]
    assert sorted(seen) == list(range(1, 20001))
    assert {c.language for c in result.chunks} == {"svelte"}


def test_unclosed_script_after_a_good_block_leaves_the_rest_as_markup():
    text = "<script>\nlet a = 1;\n</script>\n<script>\nlet b = 2;\n<p>x</p>\n"
    result = chunk_file("half.svelte", text, load_settings({"chunk": {"merge_target_lines": 0}}))
    assert [c.start for c in result.chunks if c.language == "typescript"] == [2]
    assert any("let b = 2;" in c.code for c in result.chunks if c.language == "svelte")


def test_deeply_nested_containers_do_not_blow_the_stack():
    depth = 3000
    text = "".join(f"mod m{n} {{\n" for n in range(depth)) + "fn f() {}\n" + "}\n" * depth
    settings = load_settings({"chunk": {"size_cap_lines": 5, "file_size_limit_bytes": 10**7}})
    result = chunk_file("deep.rs", text, settings)
    seen = [n for c in result.chunks for n in range(c.start, c.end + 1)]
    assert len(seen) == len(set(seen)) and seen


def test_tokenizer_is_fast_on_a_line_at_the_length_limit():
    import time

    from context_engine.tokens import tokenize

    started = time.monotonic()
    for hostile in ("A" * 20000 + "a", "aB" * 10000, "_" * 20000, "a1" * 10000):
        tokenize(hostile)
    assert time.monotonic() - started < 1.0
