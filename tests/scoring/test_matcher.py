"""Edge-case table for the matcher: distance, snapping, assignment, neutrality, control mode."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

from review_core.contracts.models import Finding, KeyEntry, Site, load_findings, load_key
from review_core.scoring.matcher import check_control, dir_reader, match_case

FIXTURES = Path(__file__).parent / "fixtures"
SCORING_SRC = Path(__file__).parents[2] / "src" / "review_core" / "scoring"


def S(start, end=None, file="app/a.py", side="new", anchor="a"):
    """Build a site."""
    return Site(file=file, side=side, line_start=start, line_end=end or start, anchor=anchor)


def E(eid, sites, tier=1, fixed=()):
    """Build a key entry."""
    return KeyEntry(
        id=eid, case="c", tier=tier, tag="visible_in_diff", description="d",
        sites=tuple(sites), fixed_sites=tuple(fixed),
    )  # fmt: skip


def F(start, end=None, file="app/a.py", side="new", quote="q", scope="in_diff"):
    """Build a finding."""
    return Finding(
        file=file, line_start=start, line_end=end or start, side=side, quote=quote, title="t",
        description="d", severity="P1", confidence=75, category="correctness",
        reviewer="correctness", scope=scope, fingerprint=None,
    )  # fmt: skip


def no_text(side, file):
    """A reader with no files, so quotes never snap."""
    return None


def reader_of(texts):
    """A reader over a dict keyed by (side, file)."""

    def read(side, file):
        return texts.get((side, file))

    return read


def labels(case):
    """The label of each finding, in input order."""
    return [r.label for r in case.results]


# --- distance and span --------------------------------------------------------------------


def test_finding_inside_site_is_true_positive():
    case = match_case([F(21)], [E("e1", [S(20, 22)])], no_text)
    assert labels(case) == ["tp"]
    assert case.results[0].entry_id == "e1"
    assert case.matched == ("e1",)
    assert case.missed == ()


def test_three_lines_away_matches_four_does_not():
    entry = [E("e1", [S(20, 22)])]
    assert labels(match_case([F(25)], entry, no_text)) == ["tp"]  # 25 - 22 = 3
    assert labels(match_case([F(26)], entry, no_text)) == ["fp"]  # 26 - 22 = 4
    assert labels(match_case([F(17)], entry, no_text)) == ["tp"]  # 20 - 17 = 3
    assert labels(match_case([F(16)], entry, no_text)) == ["fp"]  # 20 - 16 = 4


def test_multi_line_finding_measures_the_gap_between_ranges():
    entry = [E("e1", [S(20, 22)])]
    assert labels(match_case([F(24, 26)], entry, no_text)) == ["tp"]  # gap 24 - 22 = 2
    assert labels(match_case([F(26, 30)], entry, no_text)) == ["fp"]  # gap 4


def test_finding_spanning_31_lines_never_matches_but_30_does():
    entry = [E("e1", [S(20)])]
    assert labels(match_case([F(10, 40)], entry, no_text)) == ["fp"]  # 31 lines, covers line 20
    assert labels(match_case([F(10, 39)], entry, no_text)) == ["tp"]  # 30 lines


def test_other_file_does_not_match():
    case = match_case([F(20, file="app/b.py")], [E("e1", [S(20)])], no_text)
    assert labels(case) == ["fp"]
    assert case.missed == ("e1",)


# --- quote snapping -----------------------------------------------------------------------

HEAD = ["filler"] * 60
HEAD[9] = "    the unique bug line   "  # line 10, with stray whitespace


def test_unique_quote_snaps_wrong_line_numbers_to_the_site():
    texts = {("new", "app/a.py"): "\n".join(HEAD)}
    finding = F(50, quote="the unique bug line")  # claims line 50; quote is at line 10
    assert labels(match_case([finding], [E("e1", [S(10)])], reader_of(texts))) == ["tp"]
    assert labels(match_case([finding], [E("e1", [S(10)])], no_text)) == ["fp"]  # no snap


def test_multi_line_quote_snaps_on_stripped_lines():
    text = ["pad"] * 40
    text[19:22] = ["  a = 1", "b = 2  ", "\tc = 3"]  # lines 20-22
    texts = {("new", "app/a.py"): "\n".join(text)}
    finding = F(5, quote="a = 1\n    b = 2\nc = 3")
    assert labels(match_case([finding], [E("e1", [S(21)])], reader_of(texts))) == ["tp"]


def test_quote_occurring_twice_falls_back_to_claimed_lines():
    text = ["pad"] * 60
    text[9] = text[29] = "duplicate line"  # lines 10 and 30
    texts = {("new", "app/a.py"): "\n".join(text)}
    entry = [E("e1", [S(10)])]
    claimed_near = F(10, quote="duplicate line")
    claimed_far = F(50, quote="duplicate line")
    assert labels(match_case([claimed_near], entry, reader_of(texts))) == ["tp"]
    assert labels(match_case([claimed_far], entry, reader_of(texts))) == ["fp"]


def test_quote_absent_from_file_falls_back_to_claimed_lines():
    texts = {("new", "app/a.py"): "\n".join(HEAD)}
    assert labels(match_case([F(10, quote="not there")], [E("e1", [S(10)])], reader_of(texts))) == [
        "tp"
    ]


def test_new_side_finding_looks_in_head_not_base():
    texts = {("new", "app/a.py"): "nothing here", ("old", "app/a.py"): "\n".join(HEAD)}
    finding = F(50, quote="the unique bug line", side="new")
    assert labels(match_case([finding], [E("e1", [S(10)])], reader_of(texts))) == ["fp"]


def test_old_side_finding_does_not_match_new_side_site_at_same_lines():
    case = match_case([F(10, side="old")], [E("e1", [S(10, side="new")])], no_text)
    assert labels(case) == ["fp"]


def test_old_side_finding_snaps_to_old_site_from_base_tree():
    read = dir_reader(FIXTURES / "old_side" / "head", FIXTURES / "old_side" / "base")
    finding = F(25, file="app/b.py", side="old", quote="removed_bug = True")  # base line 12
    entry = E("e1", [S(12, file="app/b.py", side="old")])
    assert labels(match_case([finding], [entry], read)) == ["tp"]
    # The same quote on the new side is not in the head tree, so it cannot snap.
    new_side = F(25, file="app/b.py", side="new", quote="removed_bug = True")
    assert labels(match_case([new_side], [E("e1", [S(12, file="app/b.py")])], read)) == ["fp"]


def test_dir_reader_returns_none_for_missing_and_escaping_paths():
    read = dir_reader(FIXTURES / "old_side" / "head", FIXTURES / "old_side" / "base")
    assert read("new", "app/b.py").startswith("h1 = 1")
    assert read("old", "app/b.py").startswith("b1 = 1")
    assert read("new", "app/missing.py") is None
    assert read("new", "../base/app/b.py") is None


def test_long_quote_is_not_snapped_and_snapped_range_never_exceeds_the_span_limit():
    text = [f"line {n}" for n in range(1, 101)]
    texts = {("new", "app/a.py"): "\n".join(text)}
    block = "\n".join(text[19:59])  # 40 lines, 20-59, unique in the file
    entry = [E("e1", [S(45)])]
    wide = F(10, 12, quote=block)  # claims 10-12, quote covers the site at 45
    assert labels(match_case([wide], entry, reader_of(texts))) == ["fp"]
    narrow = F(10, 12, quote="\n".join(text[43:46]))  # 3-line quote at 44-46
    assert labels(match_case([narrow], entry, reader_of(texts))) == ["tp"]
    # A 30-line quote still snaps, and a 31-line one falls back to the claimed lines.
    thirty = F(80, 82, quote="\n".join(text[29:59]))  # lines 30-59
    assert labels(match_case([thirty], [E("e1", [S(55)])], reader_of(texts))) == ["tp"]
    thirty_one = F(80, 82, quote="\n".join(text[29:60]))
    assert labels(match_case([thirty_one], [E("e1", [S(55)])], reader_of(texts))) == ["fp"]


def test_unsafe_paths_are_ignored_and_never_read():
    calls = []

    def recording(side, file):
        calls.append((side, file))
        return None

    bad = [F(1, file="../../etc/passwd"), F(1, file="/abs/src/a.rs")]
    entry = [E("e1", [S(1, file="src/a.rs")])]
    case = match_case(bad, entry, recording)
    assert labels(case) == ["ignored", "ignored"]
    assert [r.reason for r in case.results] == ["out_of_snapshot"] * 2
    assert case.out_of_snapshot == 2
    assert case.missed == ("e1",)
    assert calls == []


def test_dot_slash_path_matches_normalised_site_file():
    entry = [E("e1", [S(1, file="src/a.rs")])]
    case = match_case([F(1, file="./src/a.rs")], entry, no_text)
    assert labels(case) == ["tp"]
    assert case.out_of_snapshot == 0


def test_unsafe_finding_is_ignored_in_control_mode_and_not_read():
    calls = []

    def recording(side, file):
        calls.append(file)

    entries = [E("e1", [S(99)], fixed=[S(1, file="src/a.rs")])]
    assert check_control([F(1, file="/abs/src/a.rs")], entries, recording).false_alarms == 0
    assert calls == []
    assert check_control([F(1, file="./src/a.rs")], entries, no_text).false_alarms == 1


# --- assignment ---------------------------------------------------------------------------


def test_second_finding_on_one_entry_is_a_dup_and_nearest_is_the_true_positive():
    entry = [E("e1", [S(10)])]
    case = match_case([F(12), F(10)], entry, no_text)  # the nearer finding comes second
    assert labels(case) == ["dup", "tp"]
    assert [r.entry_id for r in case.results] == ["e1", "e1"]
    assert case.matched == ("e1",)


def test_equally_near_findings_keep_the_earlier_as_true_positive():
    case = match_case([F(9), F(11)], [E("e1", [S(10)])], no_text)
    assert labels(case) == ["tp", "dup"]


def test_finding_near_two_entries_goes_to_the_nearer_and_other_stays_missed():
    entries = [E("e1", [S(10)]), E("e2", [S(15)])]
    case = match_case([F(12)], entries, no_text)  # distances 2 and 3
    assert labels(case) == ["tp"]
    assert case.results[0].entry_id == "e1"
    assert case.matched == ("e1",)
    assert case.missed == ("e2",)


def test_equal_distance_to_two_entries_breaks_ties_by_entry_id():
    entries = [E("b", [S(10)]), E("a", [S(14)])]
    case = match_case([F(12)], entries, no_text)
    assert case.results[0].entry_id == "a"
    assert case.missed == ("b",)


def test_entry_with_two_sites_is_satisfied_by_a_finding_at_either():
    entry = [E("e1", [S(5, file="app/a.py"), S(50, file="app/b.py")])]
    assert labels(match_case([F(50, file="app/b.py")], entry, no_text)) == ["tp"]
    assert labels(match_case([F(5)], entry, no_text)) == ["tp"]
    both = match_case([F(5), F(50, file="app/b.py")], entry, no_text)
    assert labels(both) == ["tp", "dup"]


# --- neutrality ---------------------------------------------------------------------------


def test_pre_existing_and_out_of_slice_findings_are_neutral_and_do_not_satisfy_entries():
    entry = [E("e1", [S(10)])]
    case = match_case([F(10, scope="pre_existing"), F(10, scope="out_of_slice")], entry, no_text)
    assert labels(case) == ["neutral", "neutral"]
    assert case.missed == ("e1",)


def test_neutral_finding_does_not_make_a_later_real_one_a_dup():
    entry = [E("e1", [S(10)])]
    case = match_case([F(10, scope="pre_existing"), F(11)], entry, no_text)
    assert labels(case) == ["neutral", "tp"]


def test_tier_three_match_is_neutral_and_the_entry_is_not_counted_as_missed():
    entries = [E("opinion", [S(10)], tier=3)]
    case = match_case([F(10), F(11)], entries, no_text)
    assert labels(case) == ["neutral", "neutral"]
    assert case.matched == ()
    assert case.missed == ()
    unmatched = match_case([], entries, no_text)
    assert unmatched.missed == ()


# --- control mode -------------------------------------------------------------------------


def test_control_counts_findings_at_fixed_sites_and_ignores_the_rest():
    entries = [E("e1", [S(99)], fixed=[S(10, 12, file="app/c.py")])]
    at_fixed = F(11, file="app/c.py")
    elsewhere = F(40, file="app/c.py")
    other_file = F(11, file="app/other.py")
    result = check_control([at_fixed, elsewhere, other_file], entries, no_text)
    assert result.false_alarms == 1
    assert result.findings == (at_fixed,)


def test_control_reads_the_fixed_tree_for_quote_snapping():
    texts = {("new", "app/c.py"): "\n".join(["pad"] * 9 + ["the fix is here"] + ["pad"] * 20)}
    entries = [E("e1", [S(99)], fixed=[S(10, file="app/c.py")])]
    snapped = F(25, file="app/c.py", quote="the fix is here")
    assert check_control([snapped], entries, reader_of(texts)).false_alarms == 1
    assert check_control([snapped], entries, no_text).false_alarms == 0


def test_control_counts_a_finding_once_even_if_it_touches_two_fixed_sites():
    entries = [E("e1", [S(99)], fixed=[S(10), S(12)]), E("e2", [S(98)], fixed=[S(11)])]
    assert check_control([F(11)], entries, no_text).false_alarms == 1


def test_control_skips_neutral_scopes_and_tier_three_entries():
    entries = [
        E("e1", [S(99)], fixed=[S(10)]),
        E("opinion", [S(98)], tier=3, fixed=[S(30)]),
    ]
    findings = [F(10, scope="pre_existing"), F(10, scope="out_of_slice"), F(30)]
    assert check_control(findings, entries, no_text).false_alarms == 0


def test_control_with_no_fixed_sites_has_no_false_alarms():
    assert check_control([F(10)], [E("e1", [S(10)])], no_text).false_alarms == 0


# --- fixture through the contract loaders ---------------------------------------------------


def test_five_entry_fixture_labels():
    key = load_key(json.loads((FIXTURES / "five" / "key.json").read_text()))
    doc = load_findings(json.loads((FIXTURES / "five" / "findings.json").read_text()))
    read = dir_reader(FIXTURES / "five" / "head", FIXTURES / "five" / "head")
    case = match_case(doc.findings, key.entries, read)
    # f5@5 tp e1, f16 tp e2, f25 tp e3, f26 dup, f45 neutral (tier 3), f55 fp, f35 pre_existing
    assert labels(case) == ["tp", "tp", "tp", "dup", "neutral", "fp", "neutral"]
    assert case.matched == ("e1", "e2", "e3")
    assert case.missed == ("e4",)


# --- vendoring guard ------------------------------------------------------------------------


def test_scoring_package_imports_only_stdlib_and_contract_models():
    allowed_roots = set(sys.stdlib_module_names) | {"review_core"}
    allowed_review_core = {"review_core.contracts.models", "review_core.scoring"}
    files = sorted(SCORING_SRC.glob("*.py"))
    assert {p.name for p in files} >= {"__init__.py", "matcher.py", "metrics.py", "bootstrap.py"}
    for path in files:
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [("." * node.level) + (node.module or "")] if node.level else [node.module]
            else:
                continue
            for name in names:
                if name.startswith("."):
                    continue  # relative import inside the scoring package
                assert name.split(".")[0] in allowed_roots, f"{path.name} imports {name}"
                if name.split(".")[0] == "review_core":
                    assert any(name.startswith(a) for a in allowed_review_core), (path.name, name)


# --- a finding from the test lane alone ---------------------------------------------------


def T(start, raised_by=(), category="tests"):
    """A finding in the test lane at `start`, optionally also raised by other reviewers."""
    from dataclasses import replace

    return replace(F(start), category=category, reviewer=category, also_raised_by=raised_by)


def test_a_test_lane_finding_on_a_defect_is_a_false_positive_and_the_defect_stays_missed():
    # "This code has no test" says nothing about what is wrong with it.
    case = match_case([T(10)], [E("k1", [S(10)])], no_text)
    assert labels(case) == ["fp"] and case.results[0].reason == "test_gap"
    assert case.matched == () and case.missed == ("k1",) and case.test_gap == 1


def test_it_does_not_take_the_place_of_a_real_finding_on_the_same_entry():
    case = match_case([T(10), F(12)], [E("k1", [S(10)])], no_text)
    assert labels(case) == ["fp", "tp"] and case.matched == ("k1",) and case.test_gap == 1


def test_a_finding_another_lane_also_raised_keeps_its_match():
    case = match_case([T(10, raised_by=("correctness",))], [E("k1", [S(10)])], no_text)
    assert labels(case) == ["tp"] and case.test_gap == 0
    again = match_case([T(10, raised_by=("tests",))], [E("k1", [S(10)])], no_text)
    assert labels(again) == ["fp"]


def test_a_test_lane_finding_stays_neutral_out_of_scope_and_is_fp_at_a_tier_three_site():
    from dataclasses import replace

    out = replace(T(10), scope="pre_existing")
    case = match_case([out, T(10)], [E("k3", [S(10)], tier=3)], no_text)
    assert labels(case) == ["neutral", "fp"] and case.test_gap == 1


def test_other_lanes_are_untouched_by_the_rule():
    case = match_case([T(10, category="security")], [E("k1", [S(10)])], no_text)
    assert labels(case) == ["tp"] and case.test_gap == 0
