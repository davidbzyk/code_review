"""Grouping of findings that point at the same code; no finding is dropped for its place."""

from review_core.aggregator.dedup import group_by_place, place_groups

from .conftest import make_finding as f


def _lines(groups: list[list[dict]]) -> list[list[int]]:
    """Each group's first lines, in group order."""
    return [[x["line_start"] for x in g] for g in groups]


def test_same_lines_from_two_reviewers_keep_both_each_naming_the_other():
    a = f("security", line_start=10, line_end=12, severity="P1")
    b = f("tests", line_start=10, line_end=12, severity="P1")
    kept = group_by_place([a, b], window=3)
    assert [x["reviewer"] for x in kept] == ["security", "tests"]
    assert [x["also_raised_by"] for x in kept] == [["tests"], ["security"]]


def test_findings_forty_lines_apart_stay_separate_even_with_intermediates():
    findings = [f("security", line_start=n, line_end=n) for n in (10, 20, 30, 40, 50)]
    assert _lines(place_groups(findings, window=3)) == [[10], [20], [30], [40], [50]]


def test_a_chain_of_close_findings_does_not_group_through_intermediates():
    findings = [f("security", line_start=n, line_end=n) for n in (10, 13, 16, 19)]
    # 10 and 13 are one group; 16 is 6 lines from 10, so it starts the next group with 19.
    assert _lines(place_groups(findings, window=3)) == [[10, 13], [16, 19]]


def test_gap_of_exactly_the_window_groups_and_one_more_line_does_not():
    near = place_groups([f(line_start=10, line_end=10), f("tests", line_start=13, line_end=13)], 3)
    far = place_groups([f(line_start=10, line_end=10), f("tests", line_start=14, line_end=14)], 3)
    assert len(near) == 1
    assert len(far) == 2


def test_different_file_or_side_never_group():
    base = f(line_start=10, line_end=10)
    other_file = f("tests", file="b.py", line_start=10, line_end=10)
    other_side = f("correctness", side="old", line_start=10, line_end=10)
    kept = group_by_place([base, other_file, other_side], window=3)
    assert len(kept) == 3 and all(x["also_raised_by"] == [] for x in kept)


def test_every_finding_is_kept_whatever_its_severity_or_confidence():
    low = f("security", line_start=10, line_end=10, severity="P3", confidence=100)
    high = f("tests", line_start=10, line_end=10, severity="P0", confidence=50)
    kept = group_by_place([low, high], window=3)
    assert [(x["reviewer"], x["severity"]) for x in kept] == [("security", "P3"), ("tests", "P0")]


def test_also_raised_by_is_sorted_without_the_reviewer_itself_or_repeats():
    group = [
        f("security", line_start=10, line_end=10, severity="P0"),
        f("tests", line_start=10, line_end=10),
        f("security", line_start=11, line_end=11),
        f("architecture", line_start=10, line_end=10),
        f("tests", line_start=12, line_end=12),
    ]
    kept = group_by_place(group, window=3)
    assert len(kept) == 5
    assert kept[0]["also_raised_by"] == ["architecture", "tests"]
    assert kept[1]["also_raised_by"] == ["architecture", "security"]


def test_by_default_only_findings_on_shared_lines_are_one_group():
    # Two real defects three lines apart were merged into one, so a perfect review could not be
    # credited for both. On fifteen tuning runs, 49 of 51 merges were of overlapping ranges.
    apart = place_groups([f(line_start=49, line_end=50), f("tests", line_start=53, line_end=53)])
    adjacent = place_groups([f(line_start=49, line_end=50), f("tests", line_start=51, line_end=51)])
    shared = group_by_place([f(line_start=49, line_end=50), f("tests", line_start=50, line_end=52)])
    assert len(apart) == 2 and len(adjacent) == 2
    assert [x["also_raised_by"] for x in shared] == [["tests"], ["security"]]
