"""Grouping and merging of findings that point at the same code."""

from review_core.aggregator.dedup import dedup

from .conftest import make_finding as f


def test_same_lines_from_two_reviewers_merge_into_one_listing_both():
    a = f("security", line_start=10, line_end=12, severity="P1")
    b = f("tests", line_start=10, line_end=12, severity="P1")
    kept, removed = dedup([a, b], window=3)
    assert len(kept) == 1 and len(removed) == 1
    assert kept[0]["reviewer"] == "security"
    assert kept[0]["also_raised_by"] == ["tests"]


def test_findings_forty_lines_apart_stay_separate_even_with_intermediates():
    findings = [f("security", line_start=n, line_end=n) for n in (10, 20, 30, 40, 50)]
    kept, removed = dedup(findings, window=3)
    assert [k["line_start"] for k in kept] == [10, 20, 30, 40, 50]
    assert removed == []


def test_a_chain_of_close_findings_does_not_merge_through_intermediates():
    findings = [f("security", line_start=n, line_end=n) for n in (10, 13, 16, 19)]
    kept, removed = dedup(findings, window=3)
    # 10 and 13 are one group; 16 is 6 lines from 10, so it starts the next group with 19.
    assert sorted(k["line_start"] for k in kept) == [10, 16]
    assert len(removed) == 2


def test_gap_of_exactly_the_window_merges_and_one_more_line_does_not():
    near = dedup([f(line_start=10, line_end=10), f("tests", line_start=13, line_end=13)], 3)
    far = dedup([f(line_start=10, line_end=10), f("tests", line_start=14, line_end=14)], 3)
    assert len(near[0]) == 1
    assert len(far[0]) == 2


def test_different_file_or_side_never_merge():
    base = f(line_start=10, line_end=10)
    other_file = f("tests", file="b.py", line_start=10, line_end=10)
    other_side = f("correctness", side="old", line_start=10, line_end=10)
    kept, removed = dedup([base, other_file, other_side], window=3)
    assert len(kept) == 3 and removed == []


def test_higher_severity_is_kept():
    low = f("security", line_start=10, line_end=10, severity="P3", confidence=100)
    high = f("tests", line_start=10, line_end=10, severity="P0", confidence=50)
    kept, _ = dedup([low, high], window=3)
    assert kept[0]["reviewer"] == "tests" and kept[0]["severity"] == "P0"
    assert kept[0]["also_raised_by"] == ["security"]


def test_equal_severity_keeps_higher_confidence():
    low = f("security", line_start=10, line_end=10, severity="P1", confidence=50)
    high = f("tests", line_start=10, line_end=10, severity="P1", confidence=100)
    kept, _ = dedup([low, high], window=3)
    assert kept[0]["reviewer"] == "tests"


def test_equal_severity_and_confidence_keeps_lowest_line_then_reviewer_name():
    later = f("security", line_start=12, line_end=12)
    earlier = f("tests", line_start=11, line_end=11)
    assert dedup([later, earlier], 3)[0][0]["reviewer"] == "tests"
    first = f("tests", line_start=11, line_end=11)
    second = f("correctness", line_start=11, line_end=11)
    assert dedup([first, second], 3)[0][0]["reviewer"] == "correctness"


def test_also_raised_by_is_sorted_without_the_kept_reviewer_or_repeats():
    group = [
        f("security", line_start=10, line_end=10, severity="P0"),
        f("tests", line_start=10, line_end=10),
        f("security", line_start=11, line_end=11),
        f("architecture", line_start=10, line_end=10),
        f("tests", line_start=12, line_end=12),
    ]
    kept, removed = dedup(group, window=3)
    assert len(kept) == 1 and len(removed) == 4
    assert kept[0]["also_raised_by"] == ["architecture", "tests"]


def test_by_default_only_findings_on_shared_lines_are_one_finding():
    # Two real defects three lines apart were merged into one, so a perfect review could not be
    # credited for both. On fifteen tuning runs, 49 of 51 merges were of overlapping ranges.
    apart = dedup([f(line_start=49, line_end=50), f("tests", line_start=53, line_end=53)])
    adjacent = dedup([f(line_start=49, line_end=50), f("tests", line_start=51, line_end=51)])
    shared = dedup([f(line_start=49, line_end=50), f("tests", line_start=50, line_end=52)])
    assert len(apart[0]) == 2 and len(adjacent[0]) == 2
    assert len(shared[0]) == 1 and shared[0][0]["also_raised_by"] == ["tests"]
