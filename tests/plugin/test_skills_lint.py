"""Lint for the seven reviewer skills, their provenance records and the licence table.

The skills are prompts, so nothing executes them here. These tests hold the properties that
can be checked mechanically: frontmatter, one shared output contract that agrees with
findings.schema.json, provenance that points at real source lines, and the own-words and
no-payload rules against the source plugins the ideas came from.
"""

from __future__ import annotations

import json
import re
from functools import cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "src" / "plugin" / "skills"
PROVENANCE = ROOT / "src" / "plugin" / "provenance"
SCHEMA = ROOT / "src" / "review_core" / "contracts" / "findings.schema.json"
SOURCE_ROOTS = (ROOT / "private" / "third_party", ROOT / "lane-inputs" / "u4" / "third_party")

FOLDERS = (
    "security",
    "tests",
    "correctness",
    "architecture",
    "code-quality",
    "compliance",
    "language",
)
SECTIONS = (
    "## Scope",
    "## What to look for",
    "## Leave to the other reviewers",
    "## Precision rules",
    "## Never report",
    "## Severity and confidence",
    "## Working method",
    "## Output contract",
)
RULES_FILES = ("PROJECT_RULES.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md")
METHOD = "## Working method"
METHOD_HIDDEN = (
    "vector",
    "embedding",
    "graph",
    "OKF",
    "note",
    "notes",
    "bundle",
    "database",
)
METHOD_SUBJECTS = (
    "security",
    "tests",
    "correctness",
    "architecture",
    "code quality",
    "code_quality",
    "code-quality",
    "compliance",
    "language",
    "test coverage",
)
PROVENANCE_HEADER = ("Part", "Source path", "Lines", "Licence", "Treatment", "What changed")
LICENCE_HEADER = ("Source", "Licence as found", "Contribution")
NOT_USED_HEADER = ("Part", "Source path", "Lines", "Why left out")
TREATMENTS = ("adapted", "cited")
NOTHING = "Nothing:"
TEXT_SUFFIXES = {".md", ".py", ".sh", ".json", ".yaml", ".yml", ".txt", ".toml", ""}
KEBAB = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
EMOJI = re.compile("[\U0001f000-\U0001faff☀-➿️‍]")
FENCE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN = re.compile(r"`([^`\n]+)`")
HEADING = re.compile(r"^(#{1,6}) +(.*)")
QUOTED = re.compile(r'"([^"\n]+)"')
REQUEST_SPAN = re.compile(r"https?://|^(GET|POST|PUT|PATCH|DELETE) +/")
PAYLOAD_HEADING = re.compile(
    r"payload|bypass|attack|jailbreak|smuggl|wordlist|gf pattern|prompt injection|exploit", re.I
)
TAKEN_HEADING = re.compile(r"always rejected|conditionally valid", re.I)
LINE_RANGE = re.compile(r"(\d+)(?:-(\d+))?")
MIN_PAYLOAD = 10
# Folders that hold several separately licensed sources, each named by its own sub-folder.
COLLECTIONS = ("security", "claude-plugins-official")
PLAIN_WORD = re.compile(r"[A-Za-z][A-Za-z_-]*:?")
MIN_COPIED_LINE = 80
SHINGLE_WORDS = 12


def schema_name(folder: str) -> str:
    """Return the reviewer name the contract uses for a skill folder."""
    return folder.replace("-", "_")


def skill_text(folder: str) -> str:
    """Read one skill, failing with the missing path when it is not there."""
    path = SKILLS / f"review-{folder}" / "SKILL.md"
    assert path.is_file(), f"missing skill file {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> dict[str, str]:
    """Parse the leading `key: value` block between two `---` lines."""
    lines = text.split("\n")
    assert lines[0] == "---", "skill must open with a frontmatter fence"
    end = lines.index("---", 1)
    fields = {}
    for line in lines[1:end]:
        key, sep, value = line.partition(":")
        assert sep and key == key.strip(), f"frontmatter line is not `key: value`: {line!r}"
        fields[key] = value.strip()
    return fields


def section(text: str, heading: str) -> str:
    """Return a level-two section, heading included, up to the next one or the end."""
    lines = text.split("\n")
    assert heading in lines, f"missing section {heading!r}"
    start = lines.index(heading)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[start:end])


def table_rows(text: str, header: tuple[str, ...]) -> list[dict[str, str]]:
    """Return the rows of the first markdown table whose header cells are `header`."""
    rows, found = [], False
    for line in text.split("\n"):
        if not line.startswith("|"):
            if found:
                break
            continue
        cells = tuple(c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|")))
        if not found:
            found = cells == header
        elif not set("".join(cells)) <= set("-: "):
            assert len(cells) == len(header), (
                f"row has {len(cells)} cells, not {len(header)}: {line}"
            )
            rows.append(dict(zip(header, cells, strict=True)))
    assert found, f"no table with header {header}"
    return rows


@cache
def source_root() -> Path | None:
    """Return the folder holding the source plugins, or None when this checkout has none."""
    return next((root for root in SOURCE_ROOTS if root.is_dir()), None)


def need_sources() -> Path:
    """Return the source root or skip the test that needs it."""
    root = source_root()
    if root is None:
        pytest.skip("source plugins not present: neither private/third_party nor lane-inputs/u4")
    return root


@cache
def source_texts() -> dict[str, str]:
    """Read every text file of the source plugins, keyed by path relative to the root."""
    root = need_sources()
    texts = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if not path.is_file() or ".git" in rel.parts or path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            texts[rel.as_posix()] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
    return texts


def source_names() -> list[str]:
    """List the sources: each top-level folder, and each folder inside a collection."""
    root = need_sources()
    names = []
    for child in sorted(p for p in root.iterdir() if p.is_dir()):
        if child.name in COLLECTIONS:
            names += [f"{child.name}/{p.name}" for p in sorted(child.iterdir()) if p.is_dir()]
        else:
            names.append(child.name)
    return names


def source_of(path: str) -> str:
    """Name the source a provenance path belongs to."""
    parts = path.split("/")
    return "/".join(parts[:2]) if parts[0] in COLLECTIONS else parts[0]


def provenance_rows(folder: str) -> list[dict[str, str]]:
    """Read one reviewer's provenance table, with backticks stripped from the path."""
    path = PROVENANCE / f"{folder}.md"
    assert path.is_file(), f"missing provenance file {path.relative_to(ROOT)}"
    rows = table_rows(path.read_text(encoding="utf-8"), PROVENANCE_HEADER)
    for row in rows:
        row["Source path"] = row["Source path"].strip("`")
    return rows


def not_used_rows(folder: str) -> list[dict[str, str]]:
    """Read the table of fitting parts a reviewer left out, with backticks stripped."""
    text = (PROVENANCE / f"{folder}.md").read_text(encoding="utf-8")
    rows = table_rows(section(text, "## Available, not used"), NOT_USED_HEADER)
    for row in rows:
        row["Source path"] = row["Source path"].strip("`")
    return rows


def line_ranges(root: Path, row: dict[str, str]) -> list[tuple[int, int]]:
    """Check a row names an existing source file and lines inside it; return the ranges."""
    path = root / row["Source path"]
    assert path.is_file(), f"{row['Source path']} does not exist under {root.name}"
    length = len(path.read_text(encoding="utf-8").split("\n"))
    found = LINE_RANGE.findall(row["Lines"])
    assert found and LINE_RANGE.sub("", row["Lines"]).strip(", ") == "", row["Lines"]
    ranges = [(int(start), int(end or start)) for start, end in found]
    for start, end in ranges:
        assert 1 <= start <= end <= length, f"{row['Source path']} {row['Lines']} > {length}"
    return ranges


def licence_rows() -> dict[str, dict[str, str]]:
    """Read LICENCES.md as a mapping from source name to its row."""
    path = PROVENANCE / "LICENCES.md"
    assert path.is_file(), f"missing {path.relative_to(ROOT)}"
    rows = table_rows(path.read_text(encoding="utf-8"), LICENCE_HEADER)
    return {row["Source"].strip("`"): row for row in rows}


def words(text: str) -> list[str]:
    """Lower-case word tokens, so wrapping and punctuation do not hide a copied passage."""
    return re.findall(r"[a-z0-9_]+", text.lower())


def shingles(text: str) -> set[tuple[str, ...]]:
    """Every run of SHINGLE_WORDS consecutive words in the text."""
    tokens = words(text)
    return {tuple(tokens[i : i + SHINGLE_WORDS]) for i in range(len(tokens) - SHINGLE_WORDS + 1)}


@cache
def source_shingles() -> dict[str, set[tuple[str, ...]]]:
    """The word runs of every source file, computed once."""
    return {rel: shingles(text) for rel, text in source_texts().items()}


def payload_strings() -> set[str]:
    """Collect attack strings from the markdown of the security sources.

    Taken as payload: every line of a fenced code block, wherever it sits; inside a section
    headed as payloads, attacks, bypasses and the like, also inline code spans and table
    cells; anywhere, code spans that are a request or a URL; and quoted example prompts in
    the LLM tables. The two lists the security skill is built from on purpose (findings
    always rejected, findings valid only in a chain) are not payload sections.
    """
    found = set()
    for rel, text in source_texts().items():
        if not rel.startswith("security/") or not rel.endswith(".md"):
            continue
        fenced, chain = False, {}
        for line in text.split("\n"):
            if FENCE.match(line):
                fenced = not fenced
                continue
            heading = None if fenced else HEADING.match(line)
            if heading:
                level = len(heading.group(1))
                chain = {k: v for k, v in chain.items() if k < level} | {level: heading.group(2)}
                continue
            titles = " / ".join(chain.values())
            if TAKEN_HEADING.search(titles):
                continue
            if fenced:
                found.add(line.strip())
                continue
            spans = [span.strip() for span in CODE_SPAN.findall(line)]
            found.update(span for span in spans if REQUEST_SPAN.search(span))
            if PAYLOAD_HEADING.search(titles):
                found.update(spans)
                if line.startswith("|"):
                    found.update(cell.strip() for cell in line.strip("|").split("|"))
            if PAYLOAD_HEADING.search(titles) or "LLM" in titles:
                found.update(QUOTED.findall(line))
    # One plain word, with or without a colon after it, is a label from a config example and
    # not an attack string: a long skill will hold "Description" or "monitoring:" honestly.
    return {s for s in found if len(s) >= MIN_PAYLOAD and not PLAIN_WORD.fullmatch(s)}


# --- skills -------------------------------------------------------------------------------


def test_skill_folders_are_the_schema_reviewers():
    """Every reviewer name in the contract has a skill folder; other lanes may add other skills."""
    reviewers = json.loads(SCHEMA.read_text(encoding="utf-8"))["properties"]["reviewer"]["enum"]
    assert sorted(schema_name(f) for f in FOLDERS) == sorted(reviewers)
    missing = [f for f in FOLDERS if not (SKILLS / f"review-{f}" / "SKILL.md").is_file()]
    assert not missing, f"reviewers with no skill: {missing}"


@pytest.mark.parametrize("folder", FOLDERS)
def test_skill_frontmatter(folder):
    """Each skill names itself review-<folder> and says in one sentence when to use it."""
    fields = frontmatter(skill_text(folder))
    assert set(fields) == {"name", "description"}
    assert fields["name"] == f"review-{folder}"
    assert KEBAB.fullmatch(fields["name"])
    description = fields["description"]
    assert description.endswith(".") and ". " not in description, "description is one sentence"
    assert "Use when" in description, "description says when to use the skill"


@pytest.mark.parametrize("folder", FOLDERS)
def test_skill_has_the_required_parts(folder):
    """Each skill carries the same sections in the same order, and names its own reviewer."""
    text = skill_text(folder)
    headings = [line for line in text.split("\n") if line.startswith("## ")]
    assert headings == list(SECTIONS)
    body = text.replace(section(text, "## Output contract"), "")
    name = schema_name(folder)
    assert f"`{name}`" in body and f"findings.{name}.json" in body
    scope = section(text, "## Scope")
    assert "base" in scope and "head" in scope
    rules = section(text, "## Precision rules")
    for needle in ("quote", "`pre_existing`", "`out_of_slice`", "`in_diff`", "empty"):
        assert needle in rules, f"precision rules do not mention {needle}"
    grading = section(text, "## Severity and confidence")
    for needle in ("`P0`", "`P1`", "`P2`", "`P3`", "`0`", "`25`", "`50`", "`75`", "`100`"):
        assert needle in grading, f"severity and confidence section does not mention {needle}"
    assert len(section(text, "## Never report").split("\n- ")) > 3, "always-reject list is short"


@pytest.mark.parametrize("folder", FOLDERS)
def test_skill_is_plain(folder):
    """No emoji. A skill has no line limit (the owner's word, 2026-10-06)."""
    assert not EMOJI.search(skill_text(folder))


def test_compliance_names_the_rules_files_in_order():
    """The compliance reviewer looks for the project's rules file in the agreed order."""
    text = skill_text("compliance")
    positions = [text.index(f"`{name}`") for name in RULES_FILES]
    assert positions == sorted(positions)
    assert "quot" in section(text, "## Precision rules"), "no finding without the quoted rule"


def test_output_contract_is_identical_everywhere():
    """All seven skills carry one output contract, byte for byte."""
    contracts = {folder: section(skill_text(folder), "## Output contract") for folder in FOLDERS}
    first = contracts[FOLDERS[0]]
    assert first.strip() != "## Output contract"
    different = [folder for folder, text in contracts.items() if text.encode() != first.encode()]
    assert not different, f"output contract differs in {different}"


def test_output_contract_matches_the_schema():
    """The contract names every field and every allowed value in findings.schema.json."""
    contract = section(skill_text(FOLDERS[0]), "## Output contract")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    finding = schema["properties"]["findings"]["items"]
    properties = {**schema["properties"], **finding["properties"]}
    assert set(schema["required"]) == set(schema["properties"])
    assert set(finding["required"]) == set(finding["properties"])
    for name, spec in properties.items():
        assert f"`{name}`" in contract, f"contract does not name field {name}"
        for value in spec.get("enum", []):
            assert f"`{value}`" in contract, f"contract does not list {name} value {value}"
    assert "null" in finding["properties"]["fingerprint"]["type"]
    assert "`null`" in contract
    assert "`findings.<reviewer>.json`" in contract
    closing = contract.strip().split("\n\n")[-1]
    assert "empty" in closing and "one line" in closing


def method_body(folder: str) -> str:
    """Return the Working method section of one skill, without its heading line."""
    return section(skill_text(folder), METHOD).split("\n", 1)[1]


def has_word(word: str, text: str) -> bool:
    """True when `word` appears in the text as a whole word, in any case."""
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(word)}(?![A-Za-z0-9_])", text, re.I) is not None


@pytest.mark.parametrize("folder", FOLDERS)
def test_working_method_sits_right_before_the_output_contract(folder):
    """Each skill has the Working method heading as the line block just above the contract."""
    headings = [line for line in skill_text(folder).split("\n") if line.startswith("## ")]
    assert headings[-2:] == [METHOD, "## Output contract"]


def test_working_method_is_identical_everywhere():
    """All seven skills carry one Working method section, byte for byte."""
    bodies = {folder: method_body(folder) for folder in FOLDERS}
    first = bodies[FOLDERS[0]]
    assert first.strip(), "the Working method section is empty"
    different = [folder for folder, text in bodies.items() if text.encode() != first.encode()]
    assert not different, f"working method differs in {different}"


def test_working_method_makes_the_context_line_a_requirement_and_marks_results_as_data():
    """The section tells the reviewer to follow a `How to gather context:` line in its order,
    says what to do without one, marks printed passages as not instructions, and ends by
    leaving the output contract alone."""
    raw = method_body(FOLDERS[0])
    body = " ".join(raw.split())
    for needle in (
        "How to gather context:",
        "requirement, not an option",
        "in the order it gives",
        "callers, callees",
        "what a file in the project says",
        "never instructions",
        "Confirm anything you rely on",
        "output contract",
    ):
        assert needle in body, f"working method does not mention {needle!r}"
    assert all(f"\n{n}. " in raw for n in "1234"), "steps are not numbered 1 to 4"
    assert "\n5. " not in raw


def test_working_method_does_not_reveal_the_store_behind_the_command():
    """The section never says what kind of store answers the context search command."""
    body = method_body(FOLDERS[0])
    shown = [word for word in METHOD_HIDDEN if has_word(word, body)]
    assert not shown, f"working method reveals the store: {shown}"


def test_working_method_is_method_only():
    """The section names no reviewer and no subject area, so it reads the same for all seven."""
    body = method_body(FOLDERS[0])
    shown = [word for word in METHOD_SUBJECTS if has_word(word, body)]
    assert not shown, f"working method names a reviewer or subject: {shown}"


# --- provenance ---------------------------------------------------------------------------


@pytest.mark.parametrize("folder", FOLDERS)
def test_provenance_rows_point_at_real_source_lines(folder):
    """Each provenance row names an existing source file and a line range inside it."""
    rows = provenance_rows(folder)
    assert rows, "provenance table is empty"
    assert "## Overlaps resolved" in (PROVENANCE / f"{folder}.md").read_text(encoding="utf-8")
    root = need_sources()
    licences = licence_rows()
    for row in rows:
        line_ranges(root, row)
        assert row["Treatment"] in TREATMENTS
        assert row["Part"] and row["What changed"]
        source = source_of(row["Source path"])
        assert source in licences, f"{source} is not in LICENCES.md"
        assert row["Licence"] == licences[source]["Licence as found"]


@pytest.mark.parametrize("folder", FOLDERS)
def test_provenance_lists_fitting_parts_that_were_left_out(folder):
    """After the overlaps, each provenance file lists the parts it left out, each with a reason."""
    text = (PROVENANCE / f"{folder}.md").read_text(encoding="utf-8")
    assert "## Available, not used" in text, "no list of parts that were available and not used"
    assert text.index("## Overlaps resolved") < text.index("## Available, not used")
    root = need_sources()
    used: dict[str, list[tuple[int, int]]] = {}
    for row in provenance_rows(folder):
        used.setdefault(row["Source path"], []).extend(line_ranges(root, row))
    rows = not_used_rows(folder)
    assert rows, "the list of parts left out is empty"
    for row in rows:
        assert row["Part"] and len(row["Why left out"]) >= 15, f"no reason given: {row}"
        for start, end in line_ranges(root, row):
            both = [u for u in used.get(row["Source path"], []) if u[0] <= end and start <= u[1]]
            assert not both, (
                f"{row['Source path']} {row['Lines']} is listed as used and as left out"
            )


def test_every_source_contributes_or_says_why():
    """Each source has a licence row, and either a provenance row or a stated reason."""
    licences = licence_rows()
    assert sorted(licences) == sorted(source_names())
    used = {source_of(row["Source path"]) for folder in FOLDERS for row in provenance_rows(folder)}
    for source, row in licences.items():
        contribution = row["Contribution"]
        if contribution.startswith(NOTHING):
            assert len(contribution) > len(NOTHING) + 20, f"{source}: no reason given"
            assert source not in used, f"{source} is marked unused but has provenance rows"
        else:
            assert source in used, f"{source} claims a contribution but no provenance row cites it"
        assert row["Licence as found"]


def test_security_draws_on_every_security_source():
    """The security reviewer cites every security source that LICENCES.md does not rule out."""
    licences = licence_rows()
    cited = {source_of(row["Source path"]) for row in provenance_rows("security")}
    expected = {
        source
        for source in source_names()
        if source.startswith("security/") or source == "secrets-management"
    }
    unused = {s for s in expected if licences[s]["Contribution"].startswith(NOTHING)}
    assert expected - unused <= cited, f"security does not cite {sorted(expected - unused - cited)}"


# --- own words and no payloads ------------------------------------------------------------


@pytest.mark.parametrize("folder", FOLDERS)
def test_skill_copies_no_long_line_from_a_source(folder):
    """No skill line of 80 characters or more appears verbatim in any source file."""
    texts = source_texts()
    for line in skill_text(folder).split("\n"):
        line = line.strip()
        if len(line) < MIN_COPIED_LINE:
            continue
        copied = [rel for rel, text in texts.items() if line in text]
        assert not copied, f"line copied from {copied}: {line}"


@pytest.mark.parametrize("folder", FOLDERS)
def test_skill_shares_no_long_word_run_with_a_source(folder):
    """No run of twelve consecutive words in a skill appears in a source, however it is wrapped."""
    text = skill_text(folder)
    own = shingles(text.replace(section(text, "## Output contract"), ""))
    for rel, source in source_shingles().items():
        shared = own & source
        assert not shared, f"{rel} shares the word run: {' '.join(sorted(shared)[0])}"


@pytest.mark.parametrize("name", [*FOLDERS, "LICENCES"])
def test_provenance_contains_no_payload_string(name):
    """The provenance files describe the security sources without repeating their attack strings."""
    text = (PROVENANCE / f"{name}.md").read_text(encoding="utf-8")
    present = sorted(payload for payload in payload_strings() if payload in text)
    assert not present, f"payload strings found: {present}"


@pytest.mark.parametrize("folder", FOLDERS)
def test_skill_contains_no_payload_string(folder):
    """No attack string of ten characters or more from the security sources is in a skill."""
    text = skill_text(folder)
    present = sorted(payload for payload in payload_strings() if payload in text)
    assert not present, f"payload strings found: {present}"
