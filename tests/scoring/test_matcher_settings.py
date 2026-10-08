"""The matcher's two tunable settings: the line gap and the test-lane rule."""

from __future__ import annotations

import dataclasses

from review_core.contracts.models import Finding, KeyEntry, Site
from review_core.scoring.matcher import MAX_GAP, match_case


def entry(eid="e1", line=50):
    """A tier 1 entry with one site on app.py."""
    site = Site(file="app.py", side="new", line_start=line, line_end=line, anchor="a")
    return KeyEntry(
        id=eid, case="c", tier=1, tag="visible_in_diff", description="d",
        sites=(site,), fixed_sites=(),
    )  # fmt: skip


def finding(line, **overrides):
    """A finding on app.py, written by the correctness reviewer."""
    base = Finding(
        file="app.py", line_start=line, line_end=line, side="new", quote="q", title="t",
        description="d", severity="P1", confidence=75, category="correctness",
        reviewer="correctness", scope="in_diff", fingerprint=None,
    )  # fmt: skip
    return dataclasses.replace(base, **overrides)


def nothing(side, file):
    """A reader with no files, so quotes never snap."""
    return None


def test_a_wider_gap_matches_a_finding_the_default_misses():
    far = finding(50 + MAX_GAP + 2)
    assert match_case([far], [entry()], nothing).matched == ()
    assert match_case([far], [entry()], nothing, max_gap=MAX_GAP + 2).matched == ("e1",)


def test_a_narrower_gap_drops_a_finding_the_default_matches():
    near = finding(50 + MAX_GAP)
    assert match_case([near], [entry()], nothing).matched == ("e1",)
    assert match_case([near], [entry()], nothing, max_gap=MAX_GAP - 1).matched == ()


def test_test_lane_rule_off_lets_a_test_finding_match():
    lone = finding(50, category="tests", reviewer="tests")
    barred = match_case([lone], [entry()], nothing)
    assert barred.results[0].reason == "test_gap" and barred.matched == ()
    freed = match_case([lone], [entry()], nothing, test_lane_rule=False)
    assert freed.results[0].label == "tp" and freed.matched == ("e1",) and freed.test_gap == 0


def test_defaults_are_the_documented_values():
    lone = finding(50, category="tests", reviewer="tests")
    assert match_case([lone], [entry()], nothing) == match_case(
        [lone], [entry()], nothing, max_gap=MAX_GAP, test_lane_rule=True
    )
