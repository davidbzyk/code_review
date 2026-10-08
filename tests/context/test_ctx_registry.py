"""The provider registry: rows load and validate, and a new row needs no edit to ctx."""

from __future__ import annotations

import json
import re
import textwrap

import pytest
from ctx_helpers import read_log, run_ctx

from review_core.context import build_stores
from review_core.context.providers import CTX_HELP, RegistryError, load_registry, resolve


def test_packaged_rows_load_with_the_three_arms():
    reg = load_registry()
    assert set(reg.providers) == {"none", "vector", "okf"}
    assert reg.budget_tokens is None and not hasattr(reg, "pack_items")
    assert reg.providers["none"].command is False
    for name in ("vector", "okf"):
        row = reg.providers[name]
        assert row.command and row.store_dir == name
        assert callable(resolve(row.search)) and callable(resolve(row.related))
        assert callable(resolve(row.build))
    assert reg.providers["okf"].settings["direct_hits"] == 3


BANNED_IN_METHODS = ("arm", "benchmark", "embedding")
# A kind's own text may name its own store; the plain text names neither.
OWN_WORDS = {"none": ("vector", "okf"), "vector": ("okf",), "okf": ("vector",)}


def method_of(name: str) -> str:
    """The shipped `method` text of one row, as the launcher receives it."""
    return load_registry().providers[name].method


def test_every_shipped_row_has_a_method_within_the_bound():
    for name in ("none", "vector", "okf"):
        text = method_of(name)
        assert text.strip(), name
        assert "\n" not in text, f"{name} is not one line"


@pytest.mark.parametrize("name", ["none", "vector", "okf"])
def test_methods_name_no_kind_of_store_or_the_benchmark(name):
    text = method_of(name).lower()
    shown = [
        w
        for w in (*BANNED_IN_METHODS, *OWN_WORDS[name])
        if re.search(rf"(?<![a-z0-9]){w}(?![a-z0-9])", text)
    ]
    assert not shown, f"{name} names {shown}"


@pytest.mark.parametrize("name", ["none", "vector", "okf"])
def test_methods_allow_an_empty_result_only_after_every_changed_file(name):
    text = method_of(name)
    assert "empty result" in text and "every changed file" in text


def test_the_plain_method_names_no_file_and_no_command():
    text = method_of("none")
    for word in ("context.md", "command", "ctx"):
        assert word not in text
    for word in ("function or class", "calls", "tests", "Judge only after"):
        assert word in text


@pytest.mark.parametrize("name", ["none", "vector", "okf"])
def test_no_method_names_a_context_file(name):
    assert "context.md" not in method_of(name) and "context file" not in method_of(name).lower()


def test_the_vector_method_sends_the_reviewer_to_search_the_database_itself():
    text = method_of("vector")
    assert 'search "<words>"' in text and "related <path>" in text
    assert "vector database" in text and "as often as" in text
    assert (
        "Open the files the results name" in text
        and "read around them" in text
        and "Findings come from the code" in text
    )
    assert load_registry().providers["vector"].agent_search is True


def test_the_okf_method_sends_the_reviewer_to_the_notes_folder_and_on_to_the_code():
    text = method_of("okf")
    assert "`okf/`" in text and "README.md" in text and "knowledge notes" in text
    assert "follow them to the code" in text and "never from a note alone" in text
    assert "disagrees with the code is not a finding" in text
    # The notes are plain files: no command to search them, and no search verb in the text.
    assert "related <path>" not in text and 'search "' not in text
    assert load_registry().providers["okf"].agent_search is False


@pytest.mark.parametrize("name", ["vector", "okf"])
def test_no_method_limits_how_much_to_search_or_read(name):
    text = method_of(name).lower()
    assert not re.search(r"\b(at most|no more than|up to \d|limit)\b", text)


def write_registry(tmp_path, body: str):
    path = tmp_path / "providers.toml"
    path.write_text(textwrap.dedent(body), encoding="utf-8")
    return path


GOOD = """
    [defaults]
    budget_tokens = 100

    [fourth]
    command = true
    store_dir = "fourth"
    build = "fourth_provider:build"
    search = "fourth_provider:search"
    related = "fourth_provider:related"
    width = 7
"""


@pytest.mark.parametrize(
    "body",
    [
        "[fourth]\ncommand = true\n",  # no defaults table
        "[defaults]\nbudget_tokens = 0\n[none]\ncommand = false\n",
        "[defaults]\nbudget_tokens = 5\n[Bad-Name]\ncommand = false\n",
        "[defaults]\nbudget_tokens = 5\n[x]\ncommand = true\nstore_dir = 'x'\n",  # no callables
        "[defaults]\nbudget_tokens = 5\n[x]\ncommand = true\nstore_dir = '../x'\n"
        "build = 'a:b'\nsearch = 'a:b'\nrelated = 'a:b'\n",
        "[defaults]\nbudget_tokens = 5\n[x]\ncommand = true\nstore_dir = 'x'\n"
        "build = 'a.b'\nsearch = 'a:b'\nrelated = 'a:b'\n",  # not module:function
        "[defaults]\nbudget_tokens = 5\n[x]\ncommand = 'yes'\n",
    ],
)
def test_bad_rows_are_refused(tmp_path, body):
    with pytest.raises(RegistryError):
        load_registry(write_registry(tmp_path, body))


def test_two_rows_may_not_share_a_store_folder(tmp_path):
    row = "command = true\nstore_dir = 'same'\nbuild = 'a:b'\nsearch = 'a:b'\nrelated = 'a:b'\n"
    body = f"[defaults]\nbudget_tokens = 5\n[x]\n{row}[y]\n{row}"
    with pytest.raises(RegistryError):
        load_registry(write_registry(tmp_path, body))


def test_a_fourth_provider_answers_both_verbs_with_no_change_to_ctx(tmp_path, monkeypatch):
    module = tmp_path / "mods"
    module.mkdir()
    (module / "fourth_provider.py").write_text(
        textwrap.dedent(
            """
            def search(store_dir, text, settings):
                item = {"id": "f1", "title": "Fourth", "path": "a/b.py", "start": 3, "end": 9,
                        "text": "line one\\nline two " + str(settings["width"])}
                return {"items": [item], "degraded": False, "reason": None}

            def related(store_dir, path, settings):
                return {"items": [], "degraded": False, "reason": "nothing for " + path}

            def build(spec):
                spec.out.mkdir(parents=True, exist_ok=True)
                (spec.out / "manifest.json").write_text(
                    '{"provider": "fourth", "store_sha256": "abc"}', encoding="utf-8")
                return {"store_sha256": "abc"}
            """
        ),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(module))
    reg = load_registry(write_registry(tmp_path, GOOD))
    assert reg.budget_tokens == 100
    store = tmp_path / "out" / "case" / "fourth"
    code = build_stores.main(
        [
            "--case",
            "case",
            "--arm",
            "fourth",
            "--out",
            str(tmp_path / "out"),
            "--cache-dir",
            str(tmp_path / "cache"),
            "--snapshots-dir",
            str(tmp_path),
        ],
        registry=reg,
    )
    assert code == 0 and (store / "manifest.json").is_file()
    log = tmp_path / "log.jsonl"
    code, out, _ = run_ctx(store, "--log", log, "search", "anything", registry=reg)
    assert code == 0
    assert out.splitlines()[1].startswith("1 item, ~")
    assert "[1] a/b.py:3-9  Fourth" in out and "line two 7" in out
    code, out, _ = run_ctx(store, "--log", log, "related", "x.py", registry=reg)
    assert code == 0 and out.splitlines()[1].endswith("nothing for x.py")
    assert [r["provider"] for r in read_log(log)] == ["fourth", "fourth"]


def test_ctx_help_names_no_store_kind():
    words = set(re.findall(r"[a-z]+", CTX_HELP.lower()))
    banned = {
        "vector",
        "vectors",
        "embedding",
        "embeddings",
        "graph",
        "note",
        "notes",
        "okf",
        "bundle",
        "index",
        "store",
        "semantic",
        "keyword",
        "markdown",
        "bm25",
        "knowledge",
    }
    assert not words & banned
    assert "ctx search" in CTX_HELP and "ctx related" in CTX_HELP
    assert json.dumps(CTX_HELP)  # plain text


def test_a_row_may_carry_the_arms_own_way_of_gathering_context(tmp_path):
    # Each arm tells its reviewers how to gather context: read the code, ask the search, or read
    # the notes first. The text is a row's `method`, so a new arm brings its own.
    reg = load_registry(
        write_registry(
            tmp_path,
            "[defaults]\nbudget_tokens = 5\n"
            '[none]\ncommand = false\nmethod = """\nRead the code\n  around the change.\n"""\n'
            "[quiet]\ncommand = false\n",
        )
    )
    assert reg.providers["none"].method == "Read the code around the change."
    assert reg.providers["quiet"].method == ""
    assert "method" not in reg.providers["none"].settings


@pytest.mark.parametrize("value", ["7", "true", '["a"]'])
def test_a_method_that_is_not_a_short_text_is_refused(tmp_path, value):
    body = f"[defaults]\nbudget_tokens = 5\n[none]\ncommand = false\nmethod = {value}\n"
    with pytest.raises(RegistryError, match="method"):
        load_registry(write_registry(tmp_path, body))
