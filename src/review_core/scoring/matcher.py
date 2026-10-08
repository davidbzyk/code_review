"""Match one case's findings against its key entries (KTD7). Standard library only.

A finding matches a site when file and side agree and the finding's lines come within MAX_GAP
lines of the site. Before comparing, the finding's quote is located in the file text on the
finding's side; a unique hit replaces the claimed lines. Assignment is one-to-one: each finding
goes to its nearest entry, and each entry keeps its nearest finding as the true positive.

A place is not a meaning, so one kind of finding is barred from matching: a finding from the
test lane that no other reviewer raised. It says code lacks a test, not what is wrong with it,
and stays a false positive with reason `test_gap` wherever it lands. This holds while no key
entry sits in a test file (true of both keys at freeze); a key that gains one needs a mark on
that entry.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from review_core.contracts.models import (
    MAX_SPAN,
    Finding,
    KeyEntry,
    Site,
    TreeReader,
    locate_quote,
    quote_lines,
    safe_relpath,
)

MAX_GAP = 3
TEST_LANE = "tests"
TEST_GAP = "test_gap"

Reader = Callable[[str, str], "str | None"]
"""Reads file text for (side, file): `new` is the head tree, `old` the base tree; None if absent."""


@dataclass(frozen=True)
class FindingResult:
    """How one finding was scored: tp, fp, dup, neutral or ignored, and its entry, if any.

    An ignored finding names an unsafe path and carries reason `out_of_snapshot`. A false
    positive with reason `test_gap` is a test-lane finding barred from matching.
    """

    finding: Finding
    label: str
    entry_id: str | None
    reason: str | None = None


@dataclass(frozen=True)
class CaseMatch:
    """Per-finding labels plus which tier 1 and 2 entries were matched or missed."""

    results: tuple[FindingResult, ...]
    matched: tuple[str, ...]
    missed: tuple[str, ...]
    out_of_snapshot: int = 0
    test_gap: int = 0


@dataclass(frozen=True)
class ControlResult:
    """Findings raised at fixed sites on the fixed tree, each one a false alarm."""

    false_alarms: int
    findings: tuple[Finding, ...]


def dir_reader(head_root: Path | str, base_root: Path | str) -> Reader:
    """Build a Reader over two directories; paths that escape their root read as missing."""
    return TreeReader(head_root, base_root).read


def _snap(finding: Finding, file: str, read: Reader) -> tuple[int, int]:
    """Return the quote's unique location in the file, else the claimed lines.

    A quote longer than MAX_SPAN lines is never located, so a snapped range stays within it.
    """
    claimed = (finding.line_start, finding.line_end)
    quote = quote_lines(finding.quote)
    if not quote or len(quote) > MAX_SPAN:
        return claimed
    text = read(finding.side, file)
    if text is None:
        return claimed
    hits = locate_quote(text, finding.quote)
    if len(hits) != 1:
        return claimed
    return hits[0], hits[0] + len(quote) - 1


def _span(finding: Finding, file: str, read: Reader) -> tuple[int, int] | None:
    """Lines to match on, or None when the finding is neutral or claims more than MAX_SPAN lines."""
    if finding.scope != "in_diff":
        return None
    if finding.line_end - finding.line_start + 1 > MAX_SPAN:
        return None
    return _snap(finding, file, read)


def _distance(
    finding: Finding,
    file: str,
    span: tuple[int, int],
    sites: Iterable[Site],
    max_gap: int = MAX_GAP,
) -> int | None:
    """Smallest line gap to a site on the same file and side, if within max_gap; 0 on overlap."""
    gaps = [
        max(site.line_start - span[1], span[0] - site.line_end, 0)
        for site in sites
        if site.side == finding.side and safe_relpath(site.file) == file
    ]
    gap = min(gaps, default=None)
    return gap if gap is not None and gap <= max_gap else None


def only_from_test_lane(finding: Finding) -> bool:
    """True for a finding in the test lane that no reviewer outside that lane also raised."""
    return finding.category == TEST_LANE and set(finding.also_raised_by) <= {TEST_LANE}


def match_case(
    findings: Sequence[Finding],
    entries: Sequence[KeyEntry],
    read: Reader,
    *,
    max_gap: int = MAX_GAP,
    test_lane_rule: bool = True,
) -> CaseMatch:
    """Label every finding and report which tier 1 and 2 entries were matched or missed.

    max_gap and test_lane_rule are for tuning in a notebook; the defaults are the scored values.
    """
    labels: list[tuple[str, str | None, str | None]] = [("fp", None, None)] * len(findings)
    claims: dict[str, list[tuple[int, int]]] = {}  # entry id -> (distance, finding index)
    by_id = {e.id: e for e in entries}
    for i, finding in enumerate(findings):
        file = safe_relpath(finding.file)
        if file is None:
            labels[i] = ("ignored", None, "out_of_snapshot")
            continue
        span = _span(finding, file, read)
        if finding.scope != "in_diff":
            labels[i] = ("neutral", None, None)
        elif test_lane_rule and only_from_test_lane(finding):
            labels[i] = ("fp", None, TEST_GAP)
        elif span is not None:
            near = [
                (d, e.id)
                for e in entries
                if (d := _distance(finding, file, span, e.sites, max_gap)) is not None
            ]
            if near:
                dist, entry_id = min(near)
                claims.setdefault(entry_id, []).append((dist, i))
    for entry_id, claimed in claims.items():
        winner = min(claimed)[1]
        neutral = by_id[entry_id].tier == 3
        for _, i in claimed:
            label = "neutral" if neutral else ("tp" if i == winner else "dup")
            labels[i] = (label, entry_id, None)
    results = tuple(
        FindingResult(finding, label, entry_id, reason)
        for finding, (label, entry_id, reason) in zip(findings, labels, strict=True)
    )
    counted = [e.id for e in entries if e.tier != 3]
    matched = tuple(i for i in counted if i in claims)
    missed = tuple(i for i in counted if i not in claims)
    ignored = sum(r.label == "ignored" for r in results)
    gaps = sum(r.reason == TEST_GAP for r in results)
    return CaseMatch(
        results=results, matched=matched, missed=missed, out_of_snapshot=ignored, test_gap=gaps
    )


def check_control(
    findings: Sequence[Finding], entries: Sequence[KeyEntry], read: Reader
) -> ControlResult:
    """Count findings on the fixed tree that land on a fixed site of a tier 1 or 2 entry."""
    sites = [s for e in entries if e.tier != 3 for s in e.fixed_sites]
    hits = []
    for finding in findings:
        file = safe_relpath(finding.file)
        span = None if file is None else _span(finding, file, read)
        if span is not None and _distance(finding, file, span, sites) is not None:
            hits.append(finding)
    return ControlResult(false_alarms=len(hits), findings=tuple(hits))
