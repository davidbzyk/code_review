"""Build report: what was seen, chunked, skipped and lost, per language (build side)."""

from __future__ import annotations

from typing import Any


class CoverageError(Exception):
    """Raised when a language's covered-line ratio is below the configured floor."""


class Report:
    """Per-language counts of files and lines, plus files excluded by policy."""

    def __init__(self) -> None:
        self._langs: dict[str, dict[str, Any]] = {}
        self._excluded: list[dict[str, str]] = []
        self._change_notes: list[dict[str, str]] = []

    def _lang(self, language: str) -> dict[str, Any]:
        """The mutable record for one language, created on first use."""
        return self._langs.setdefault(
            language,
            {
                "files_seen": 0,
                "files_chunked": 0,
                "files_skipped": [],
                "parse_failures": [],
                "lines_seen": 0,
                "lines_covered": 0,
            },
        )

    def add_chunked(self, language: str, path: str, lines: int, covered: int) -> None:
        """Record a file that produced chunks covering `covered` of its `lines` lines."""
        rec = self._lang(language)
        rec["files_seen"] += 1
        rec["files_chunked"] += 1
        rec["lines_seen"] += lines
        rec["lines_covered"] += covered

    def add_skipped(self, language: str, path: str, lines: int, reason: str) -> None:
        """Record a file that was read but not chunked; its lines count as seen and lost."""
        rec = self._lang(language)
        rec["files_seen"] += 1
        rec["files_skipped"].append({"path": path, "reason": reason})
        rec["lines_seen"] += lines

    def add_parse_failure(self, language: str, path: str) -> None:
        """Record that a file did not parse and was chunked by line windows instead."""
        self._lang(language)["parse_failures"].append(path)

    def add_excluded(self, language: str, path: str, reason: str) -> None:
        """Record a file left out by policy (binary, ignored folder); no lines are counted."""
        self._excluded.append({"path": path, "reason": reason})

    def add_change_notes(self, notes: list[dict[str, str]]) -> None:
        """Record changed files that were not diffed normally (too big, too large to diff)."""
        self._change_notes.extend(notes)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-ready, deterministically ordered copy of the report."""
        langs = {}
        for name in sorted(self._langs):
            rec = self._langs[name]
            langs[name] = {
                **rec,
                "files_skipped": sorted(rec["files_skipped"], key=lambda r: r["path"]),
                "parse_failures": sorted(rec["parse_failures"]),
            }
        return {
            "languages": langs,
            "excluded": sorted(self._excluded, key=lambda r: r["path"]),
            "change_notes": sorted(self._change_notes, key=lambda r: (r["path"], r["reason"])),
        }

    def check_coverage(self, floor: float, min_lines: int) -> None:
        """Raise CoverageError when a language with enough lines is covered below `floor`."""
        bad = []
        for name, rec in sorted(self._langs.items()):
            seen = rec["lines_seen"]
            if seen >= min_lines and rec["lines_covered"] / seen < floor:
                ratio = rec["lines_covered"] / seen
                bad.append(f"{name}: {rec['lines_covered']}/{seen} lines ({ratio:.1%})")
        if bad:
            raise CoverageError(f"coverage below the floor of {floor:.0%} for " + "; ".join(bad))
