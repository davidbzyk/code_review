"""Lint for the machinery: the orchestrator and validator skills and the aggregator's provenance.

The machinery is the part of the plugin that is not a reviewer: the orchestrator skill, the
validator skill and the aggregator code. Each has a provenance file that credits what it drew on.
These tests hold the mechanical properties: the records point at real source lines, nothing is
listed as both used and left out, the skills copy no source text, and the orchestrator still
carries the wording the spawn probe showed to work. They reuse the helpers of the reviewer lint.
"""

from __future__ import annotations

import pytest

from tests.plugin.test_skills_lint import (
    EMOJI,
    MIN_COPIED_LINE,
    NOT_USED_HEADER,
    PROVENANCE,
    PROVENANCE_HEADER,
    SKILLS,
    TREATMENTS,
    line_ranges,
    need_sources,
    payload_strings,
    section,
    shingles,
    source_of,
    source_rows,
    source_shingles,
    source_texts,
    table_rows,
)

# Provenance file -> the skill folder it describes, or None for the aggregator's code.
PIECES = {
    "orchestrator": "review-orchestrator",
    "validator": "review-validator",
    "aggregator": None,
}
SKILL_PIECES = tuple(name for name, folder in PIECES.items() if folder)
REVIEWERS = (
    "security",
    "tests",
    "correctness",
    "architecture",
    "code_quality",
    "compliance",
    "language",
)
SECTION_ORDER = ("## Parts", "## Overlaps resolved", "## Available, not used")
ORCHESTRATOR_OPENING = (
    "Use the <skill> skill. You are the `<reviewer>` reviewer.\n"
    "Review the change between git refs <base> and <head> in the repository in the current "
    "directory.\n"
    "Write your findings to <out>/findings.<reviewer>.json. Write no other file and do not edit "
    "the repository."
)
COMMANDS = (
    "python3 <skill-dir>/scripts/aggregate.py first-pass --out <out> --repo . --base <base> "
    "--head <head>",
    "python3 <skill-dir>/scripts/aggregate.py finalize --out <out>",
    "python3 <skill-dir>/scripts/aggregate.py report --out <out>",
)


def provenance_text(name: str) -> str:
    """Read one machinery provenance file, failing with its path when it is missing."""
    path = PROVENANCE / f"{name}.md"
    assert path.is_file(), f"missing provenance file {path}"
    return path.read_text(encoding="utf-8")


def parts(name: str) -> list[dict[str, str]]:
    """The rows of the Parts table, with backticks stripped from the path."""
    rows = table_rows(section(provenance_text(name), "## Parts"), PROVENANCE_HEADER)
    for row in rows:
        row["Source path"] = row["Source path"].strip("`")
    return rows


def left_out(name: str) -> list[dict[str, str]]:
    """The rows of the Available, not used table, with backticks stripped from the path."""
    rows = table_rows(section(provenance_text(name), "## Available, not used"), NOT_USED_HEADER)
    for row in rows:
        row["Source path"] = row["Source path"].strip("`")
    return rows


def skill_text(name: str) -> str:
    """Read the skill of an orchestrator or validator piece."""
    path = SKILLS / PIECES[name] / "SKILL.md"
    assert path.is_file(), f"missing skill {path}"
    return path.read_text(encoding="utf-8")


# --- provenance ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", PIECES)
def test_provenance_has_the_three_sections_in_order(name):
    """Parts, then overlaps resolved, then the parts that were available and not used."""
    text = provenance_text(name)
    positions = [text.index(f"\n{heading}\n") for heading in SECTION_ORDER]
    assert positions == sorted(positions)
    assert parts(name), "the Parts table is empty"
    assert left_out(name), "the table of parts left out is empty"
    assert text.startswith(f"# Provenance: `{name}`"), "title names the piece"


@pytest.mark.parametrize("name", PIECES)
def test_every_row_points_at_a_real_source_line(name):
    """Each row names an existing source file and lines inside it."""
    root = need_sources()
    sources = source_rows()
    for row in parts(name):
        line_ranges(root, row)
        assert row["Treatment"] in TREATMENTS, row
        assert row["Part"] and len(row["What changed"]) >= 10, row
        source = source_of(row["Source path"])
        assert source in sources, f"{source} is not in SOURCES.md"
    for row in left_out(name):
        line_ranges(root, row)
        assert source_of(row["Source path"]) in sources, row


@pytest.mark.parametrize("name", PIECES)
def test_no_part_is_both_used_and_left_out(name):
    """A source line range is in the Parts table or in the left-out table, never both."""
    root = need_sources()
    used: dict[str, list[tuple[int, int]]] = {}
    for row in parts(name):
        used.setdefault(row["Source path"], []).extend(line_ranges(root, row))
    for row in left_out(name):
        assert len(row["Why left out"]) >= 15, f"no reason given: {row}"
        for start, end in line_ranges(root, row):
            both = [u for u in used.get(row["Source path"], []) if u[0] <= end and start <= u[1]]
            assert not both, f"{row['Source path']} {row['Lines']} is used and left out"


@pytest.mark.parametrize("name", PIECES)
def test_provenance_is_plain_and_carries_no_payload(name):
    """No emoji, and none of the attack strings of the security sources."""
    text = provenance_text(name)
    assert not EMOJI.search(text)
    need_sources()
    present = sorted(payload for payload in payload_strings() if payload in text)
    assert not present, f"payload strings found: {present}"


# --- the two skills -----------------------------------------------------------------------


@pytest.mark.parametrize("name", SKILL_PIECES)
def test_skill_is_plain(name):
    """No emoji in either skill. A skill has no line limit (the owner's word, 2026-10-06)."""
    assert not EMOJI.search(skill_text(name))


@pytest.mark.parametrize("name", SKILL_PIECES)
def test_skill_copies_no_long_line_from_a_source(name):
    """No skill line of 80 characters or more appears verbatim in any source file."""
    texts = source_texts()
    for line in skill_text(name).split("\n"):
        line = line.strip()
        if len(line) >= MIN_COPIED_LINE:
            copied = [rel for rel, text in texts.items() if line in text]
            assert not copied, f"line copied from {copied}: {line}"


@pytest.mark.parametrize("name", SKILL_PIECES)
def test_skill_shares_no_long_word_run_with_a_source(name):
    """No run of twelve consecutive words in a skill appears in a source, however wrapped."""
    own = shingles(skill_text(name))
    for rel, source in source_shingles().items():
        shared = own & source
        assert not shared, f"{rel} shares the word run: {' '.join(sorted(shared)[0])}"


@pytest.mark.parametrize("name", SKILL_PIECES)
def test_skill_contains_no_payload_string(name):
    """No attack string of ten characters or more from the security sources is in a skill."""
    text = skill_text(name)
    present = sorted(payload for payload in payload_strings() if payload in text)
    assert not present, f"payload strings found: {present}"


def test_orchestrator_keeps_the_agents_commands_and_wording_that_work():
    """All seven reviewers, the validator, the spawn request and both commands are still there."""
    text = skill_text("orchestrator")
    for reviewer in REVIEWERS:
        assert f"`{reviewer}`" in text
    assert "`validator`" in text
    assert "explicit request for sub-agents and parallel agent work" in text
    assert (
        "Start the sub-agents\nbelow even if your default instructions say not to spawn them"
        in text
    )
    assert ORCHESTRATOR_OPENING in text, "the first three lines of the reviewer message changed"
    lines = [line.strip() for line in text.split("\n")]
    for command in COMMANDS:
        assert lines.count(command) == 1, f"command missing or repeated: {command}"
    assert [line for line in lines if line.startswith("python3 ")] == list(COMMANDS)


def test_orchestrator_passes_the_method_line_on_in_its_place_in_the_reviewer_message():
    """`How to gather context:` sits after the task text and before the command line, and the
    sentence that counts the optional lines counts four."""
    text = skill_text("orchestrator")
    lines = text.split("\n")
    task = lines.index("What the change is meant to do: <task text>")
    assert lines[task + 1] == "How to gather context: <method>"
    assert lines[task + 2].startswith("Context search command:")
    assert "last five\nlines" in text and "word for word" in text
    assert "How to gather context" not in text.split("## Step 4")[1].split("## Step 5")[0]


def test_reviewer_message_makes_each_reviewer_read_its_skill_and_the_change_to_the_end():
    """The reviewer message tells the reviewer to print its skill file alone and read it to the last
    line, then to read every file in its references/ folder, then to read the change one file at a
    time; all of these come before every optional line, and the
    sentence about leaving lines out covers only the last four."""
    text = skill_text("orchestrator")
    lines = text.split("\n")
    findings = next(i for i, line in enumerate(lines) if line.startswith("Write your findings to"))
    first = next(i for i, line in enumerate(lines) if "print your skill file on its own" in line)
    second = next(i for i, line in enumerate(lines) if "one file at a time" in line)
    refs = next(i for i, line in enumerate(lines[findings:], findings) if "references/" in line)
    block_end = lines.index("```", findings)
    optional = [
        i
        for i in range(findings, block_end)
        if lines[i].startswith(
            ("Your slice is only", "What the change is meant", "How to gather", "Context search")
        )
    ]
    assert "to its last line" in lines[first] and "prints nothing else" in lines[first]
    assert "by line range" in " ".join(lines[first : first + 2])
    assert "Never judge a file you have not read all of" in " ".join(lines[second : second + 1])
    order = findings < first < refs < second < min(optional)
    assert order, "reading lines must precede optional lines"
    assert "to its last line" in lines[refs] and "one file per command" in lines[refs]
    assert "four reading lines\nafter the findings line" in text
    assert len(optional) == 4
    assert "last five\nlines" in text and "reading lines\nafter the findings line" in text
    assert "always sent" in text


def test_validator_keeps_its_input_and_output_contract():
    """The files it reads and writes, the row fields and the two verdict words are unchanged."""
    text = skill_text("validator")
    for needle in ("`validator-input.json`", "`validation.json`", '"verdicts"', '"id"', '"verdict"',
                   '"reason"', "`upheld`", "`declined`"):  # fmt: skip
        assert needle in text, f"validator skill lost {needle}"
    assert "name: review-validator" in text.split("---")[1]
