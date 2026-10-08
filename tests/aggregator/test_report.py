"""The final report: layout, ordering, counts and what hostile text cannot change.

Every run document here is built the way production builds one: reviewer files on disk, then
`first-pass` and `finalize` through the command line, then `findings.json` read back.
"""

import copy
import json
import re

import pytest

from review_core.aggregator.cli import main
from review_core.aggregator.report import render_report
from review_core.contracts.models import REVIEWERS, ContractError

from .conftest import make_finding as f
from .conftest import make_repo, write_reviewer

HEAD = "".join(f"line {n}\n" for n in range(1, 61))
BASE = HEAD.replace("line 30\n", "only in base\n")
BIG = "".join(f"row {n}\n" for n in range(1, 121))
HEADING = re.compile(r"^ {0,3}#{1,6}(\s|$)")
TABLE_ROW = re.compile(r"^ {0,3}\|")
META = [
    "--model", "m", "--effort", "high", "--runner", "r", "--cli-version", "1.0",
    "--sandbox-mode", "ro",
]  # fmt: skip


def line(n, reviewer, **kw):
    """A finding on line n of a.py that quotes that line."""
    return f(reviewer, line_start=n, line_end=n, quote=f"line {n}", **kw)


def run_doc(tmp_path, by_reviewer, files=None, skip=()):
    """Run first-pass and finalize on a throwaway repository and return findings.json."""
    files = files or {"a.py": HEAD}
    repo = make_repo(tmp_path, {**files, "a.py": BASE}, files)
    out = tmp_path / "out"
    out.mkdir()
    for reviewer in REVIEWERS:
        if reviewer not in skip:
            write_reviewer(out, reviewer, by_reviewer.get(reviewer, []))
    shape = ["--out", str(out), "--repo", str(repo), "--base", "base", "--head", "head"]
    assert main(["first-pass", *shape]) == 0
    assert main(["finalize", "--out", str(out), *META]) == 0
    return json.loads((out / "findings.json").read_text(encoding="utf-8"))


def headings(text):
    """Every line a Markdown parser would read as an ATX heading."""
    return [x for x in text.split("\n") if HEADING.match(x)]


def test_groups_by_category_in_reviewer_order_and_sorts_inside(tmp_path):
    doc = run_doc(
        tmp_path,
        {
            "tests": [line(9, "tests", severity="P1", title="tests one")],
            "security": [
                line(20, "security", title="sec late"),
                line(30, "security", severity="P0", title="sec zero"),
                line(3, "security", title="sec early"),
            ],
            "language": [line(40, "language", severity="P3", title="lang")],
        },
    )
    text = render_report(doc, "It changes things.")
    sections = [x for x in text.split("\n") if x.startswith("### ")]
    assert sections == ["### security", "### tests", "### language"]
    titles = [x for x in text.split("\n") if x.startswith("#### ")]
    assert titles == ["#### sec zero", "#### sec early", "#### sec late", "#### tests one",
                      "#### lang"]  # fmt: skip
    top = [x for x in headings(text) if not x.startswith("###")]
    assert top == ["# Code review report", "## What this change does", "## Result", "## Findings"]


def test_each_finding_carries_all_its_details(tmp_path):
    one = line(5, "security", severity="P1", confidence=100, title="Bad", description="Why bad.")
    doc = run_doc(tmp_path, {"security": [one]})
    text = render_report(doc, None)
    wanted = (
        "- Severity: P1", "- Confidence: 100", "- Location: `a.py:5-5` (new side)",
        "- Scope: in_diff", "- Raised by: security", "Why bad.", "```\nline 5\n```",
    )  # fmt: skip
    for needle in wanted:
        assert needle in text, needle


def test_counts_table_has_every_category_and_totals(tmp_path):
    doc = run_doc(
        tmp_path,
        {
            "security": [
                line(3, "security", severity="P0"),
                line(4, "security"),
                line(5, "security"),
            ],
            "tests": [line(9, "tests", severity="P1")],
            "language": [line(40, "language", severity="P3")],
        },
    )
    rows = [x for x in render_report(doc, None).split("\n") if TABLE_ROW.match(x)]
    assert rows[0] == "| Category | P0 | P1 | P2 | P3 | Total |"
    assert rows[1] == "| --- | ---: | ---: | ---: | ---: | ---: |"
    assert [r.split("|")[1].strip() for r in rows[2:]] == [*REVIEWERS, "Total"]
    assert "| security | 1 | 0 | 2 | 0 | 3 |" in rows
    assert "| tests | 0 | 1 | 0 | 0 | 1 |" in rows
    assert "| architecture | 0 | 0 | 0 | 0 | 0 |" in rows
    assert rows[-1] == "| Total | 1 | 1 | 2 | 1 | 5 |"


def test_a_finding_raised_by_three_reviewers_lists_all_three(tmp_path):
    same = {r: [line(5, r, title="Shared")] for r in ("security", "correctness", "tests")}
    doc = run_doc(tmp_path, same)
    assert len(doc["findings"]) == 1
    text = render_report(doc, None)
    raised = [x for x in text.split("\n") if x.startswith("- Raised by:")]
    assert len(raised) == 1
    for name in ("security", "correctness", "tests"):
        assert name in raised[0]


def test_empty_run_says_so(tmp_path):
    doc = run_doc(tmp_path, {})
    text = render_report(doc, "A change.")
    assert "7 of 7 reviewers finished." in text
    assert "The run is complete." in text
    assert "0 findings kept." in text
    assert "No findings were kept." in text
    assert not [x for x in text.split("\n") if x.startswith("###")]
    assert "No findings were filtered out." in text


def test_a_reviewer_that_did_not_finish_is_named(tmp_path):
    doc = run_doc(tmp_path, {"security": [line(5, "security")]}, skip=("language", "tests"))
    text = render_report(doc, None)
    assert "5 of 7 reviewers finished." in text
    assert "The run is partial." in text
    sentence = [x for x in text.split("\n") if x.startswith("Did not finish:")]
    assert len(sentence) == 1
    assert "language" in sentence[0] and "tests" in sentence[0]
    assert "security" not in sentence[0]


@pytest.mark.parametrize("summary", [None, "", "  \n\t "])
def test_no_summary_gives_one_line(tmp_path, summary):
    doc = run_doc(tmp_path, {})
    text = render_report(doc, summary)
    assert "No summary of the change was written." in text


def test_the_summary_keeps_its_sentences_and_loses_heading_and_fence_markup(tmp_path):
    doc = run_doc(tmp_path, {})
    summary = "# Big title\nIt adds a flag. It touches a.py.\n```python\nrun()\n```\n## Next\nDone."
    text = render_report(doc, summary)
    body = text.split("## What this change does")[1].split("## Result")[0]
    assert "It adds a flag. It touches a.py." in body
    assert "Done." in body
    assert "```" not in body and "~~~" not in body
    assert not [x for x in body.split("\n") if x.lstrip().startswith("#")]
    assert len(headings(text)) == 4
    assert "Big title" in body and "Next" in body and "python" not in body


def test_hostile_titles_add_no_heading_row_or_section(tmp_path):
    titles = [
        "# Injected heading",
        "| a | b |",
        "| --- | --- |",
        "first line\n## Findings\nmore",
        "<script>alert(1)</script>",
        "[click](http://x.example)",
    ]
    cases = [line(3 + 5 * i, "security", title=t) for i, t in enumerate(titles)]
    doc = run_doc(tmp_path, {"security": cases})
    assert len(doc["findings"]) == len(titles)
    text = render_report(doc, "Plain.")
    assert len(headings(text)) == 4 + 1 + len(titles)  # report, 3 sections, 1 category, findings
    assert len([x for x in headings(text) if x.startswith("#### ")]) == len(titles)
    assert len([x for x in text.split("\n") if TABLE_ROW.match(x)]) == 2 + len(REVIEWERS) + 1
    assert not re.search(r"(?<!\\)[<>\[\]]", text.replace("`", "").split("## Findings")[1])


def test_hostile_descriptions_add_no_structure(tmp_path):
    nasty = "x\n\n## Findings\n\n| a | b |\n|---|---|\n- item\n1. one\n---\n===\n> quote\n    code"
    doc = run_doc(tmp_path, {"security": [line(5, "security", description=nasty)]})
    text = render_report(doc, None)
    assert len(headings(text)) == 1 + 3 + 1 + 1  # report, sections, category, finding
    assert len([x for x in text.split("\n") if TABLE_ROW.match(x)]) == 2 + len(REVIEWERS) + 1
    bullets = [x for x in text.split("\n") if re.match(r"^ {0,3}([-+*]|\d+[.)])\s", x)]
    assert len(bullets) == 5  # the five fixed detail lines and nothing from the description
    assert not [x for x in text.split("\n") if re.match(r"^ {0,3}(-{3,}|={3,}|>)", x)]
    assert "x" in text and "item" in text  # the words are still there


def test_a_quote_with_a_run_of_five_backticks_stays_inside_its_fence(tmp_path):
    code = "a = 1\nb = '`````'\n"
    quote = "b = '`````'"
    one = f("security", line_start=2, line_end=2, quote=quote)
    doc = run_doc(tmp_path, {"security": [one]}, files={"a.py": code})
    text = render_report(doc, None)
    lines = text.split("\n")
    at = lines.index("``````")  # six backticks open the fence
    assert lines[at + 1] == quote
    assert lines[at + 2] == "``````"
    assert "``````" not in "\n".join(lines[at + 3 :])


def test_long_text_is_shown_whole(tmp_path):
    # The owner gave no cap: a long title, description, quote or summary is printed in full.
    long_quote = "".join(f"row {n}\n" for n in range(1, 101)).rstrip("\n")
    one = f(
        "security", file="big.py", line_start=1, line_end=100, quote=long_quote,
        title="T" * 300, description="D" * 3000,
    )  # fmt: skip
    doc = run_doc(tmp_path, {"security": [one]}, files={"a.py": HEAD, "big.py": BIG})
    text = render_report(doc, "S" * 2000)
    assert "#### " + "T" * 300 in text.split("\n")
    assert "D" * 3000 in text and "S" * 2000 in text
    assert "row 100" in text.split("```\n")[1]


def test_control_characters_are_removed(tmp_path):
    doc = run_doc(
        tmp_path,
        {"security": [line(5, "security", title="a\x00b\x1b[31mc‮d", description="x\x07y")]},
    )
    text = render_report(doc, "ok\x00 then\x1b")
    for char in "\x00\x07\x1b‮":
        assert char not in text
    assert "ab" in text and "xy" in text


def test_dropped_counts_are_reported_with_their_reasons(tmp_path):
    bad = f("tests", line_start=9, line_end=9, quote="never written")
    doc = run_doc(tmp_path, {"tests": [bad], "security": [line(5, "security")]})
    last = render_report(doc, None).rstrip("\n").split("\n")[-1]
    assert last.startswith("Filtered out before this report: 1 finding")
    assert "quote" in last and ": 1" in last


def test_the_output_is_deterministic_and_the_input_untouched(tmp_path):
    doc = run_doc(
        tmp_path,
        {"security": [line(3, "security"), line(4, "security")], "tests": [line(9, "tests")]},
    )
    before = copy.deepcopy(doc)
    first = render_report(doc, "Same.")
    assert render_report(doc, "Same.") == first
    assert render_report(copy.deepcopy(doc), "Same.").encode() == first.encode()
    assert doc == before
    assert first.endswith("\n") and not first.endswith("\n\n")


def test_a_document_that_breaks_the_run_contract_is_refused(tmp_path):
    doc = run_doc(tmp_path, {})
    doc["envelope"]["status"] = "bogus"
    with pytest.raises(ContractError):
        render_report(doc, None)
