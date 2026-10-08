"""The build report and its coverage floor."""

from __future__ import annotations

import pytest

from context_engine.report import CoverageError, Report


def test_counts_per_language_and_floor():
    report = Report()
    report.add_chunked("rust", "a.rs", lines=300, covered=300)
    report.add_skipped("rust", "big.rs", lines=100, reason="too-large")
    report.add_parse_failure("rust", "bad.rs")
    summary = report.to_dict()
    rust = summary["languages"]["rust"]
    assert rust["files_seen"] == 2
    assert rust["files_chunked"] == 1
    assert rust["files_skipped"] == [{"path": "big.rs", "reason": "too-large"}]
    assert rust["parse_failures"] == ["bad.rs"]
    assert rust["lines_seen"] == 400 and rust["lines_covered"] == 300
    with pytest.raises(CoverageError, match="rust"):
        report.check_coverage(floor=0.95, min_lines=200)
    report.check_coverage(floor=0.5, min_lines=200)


def test_small_languages_are_exempt():
    report = Report()
    report.add_skipped("json", "x.json", lines=50, reason="too-large")
    report.check_coverage(floor=0.95, min_lines=200)


def test_excluded_files_are_listed_but_not_counted_as_lines():
    report = Report()
    report.add_chunked("rust", "a.rs", lines=250, covered=250)
    report.add_excluded("png", "logo.png", reason="binary")
    summary = report.to_dict()
    assert summary["excluded"] == [{"path": "logo.png", "reason": "binary"}]
    report.check_coverage(floor=0.95, min_lines=200)
