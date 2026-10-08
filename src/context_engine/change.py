"""The change under review: base-side line ranges it touches and its head text (build side)."""

from __future__ import annotations

import bisect
import difflib
from typing import Any

from context_engine.chunk import split_lines

SIZE_NOTE = "changed file over the size limit"
LINE_NOTE = "changed file has a line over the limit"
DIFF_NOTE = "change too large to diff"
NO_RELATED_NOTE = "no related query: too many changed files"
TOTAL_NOTE = "diff budget for the whole change is spent"


def diff_file(base_text: str, head_text: str) -> tuple[list[dict[str, Any]], str]:
    """Base-side ranges touched by the change in one file, and the text of the changed hunks.

    Ranges are 1-based and inclusive. An insertion is recorded as kind "insert" at the base
    line it follows (0 for the top of the file). The hunk text is the head-side text of
    replaced and inserted lines; a file with only deletions gives the deleted base text.
    """
    base, head = split_lines(base_text), split_lines(head_text)
    matcher = difflib.SequenceMatcher(None, base, head, autojunk=False)
    ranges: list[dict[str, Any]] = []
    added: list[str] = []
    removed: list[str] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "insert":
            ranges.append({"start": i1, "end": i1, "kind": "insert"})
        else:
            kind = "delete" if tag == "delete" else "change"
            ranges.append({"start": i1 + 1, "end": i2, "kind": kind})
            removed.extend(base[i1:i2])
        added.extend(head[j1:j2])
    return ranges, "\n".join(added or removed)


def _whole(base_text: str) -> list[dict[str, Any]]:
    """One range covering every line of the indexed file."""
    return [{"start": 1, "end": len(split_lines(base_text)), "kind": "change"}]


def compute_change(
    base: dict[str, str], head: dict[str, str], head_big: dict[str, tuple[str, str]], settings: dict
) -> tuple[dict[str, Any], dict[str, str], list[dict[str, str]]]:
    """Per-path change records, hunk text and report notes for the two trees.

    `head_big` maps a changed-tree path that was too big to read whole to (reason, the first
    bytes of its text). Such a file, and a pair too large to diff, count as wholly touched. So
    does every pair met after the budget for the whole change is spent, in path order: a limit
    for each file alone would let a change of many files run for as long as it liked.
    """
    cfg = settings["change"]
    cap = cfg["query_max_chars"]
    files: dict[str, Any] = {}
    hunks: dict[str, str] = {}
    notes: list[dict[str, str]] = []
    spent = 0
    for path in sorted(set(base) | set(head) | set(head_big)):
        if path in head_big:
            reason, text = head_big[path]
            notes.append({"path": path, "reason": reason})
            hunks[path] = text[:cap]
            if path in base:
                files[path] = {"status": "modified", "ranges": _whole(base[path])}
            else:
                files[path] = {"status": "added", "ranges": []}
        elif path not in base:
            files[path] = {"status": "added", "ranges": []}
            hunks[path] = head[path][:cap]
        elif path not in head:
            count = len(split_lines(base[path]))
            files[path] = {
                "status": "deleted",
                "ranges": [{"start": 1, "end": count, "kind": "delete"}],
            }
            hunks[path] = base[path][:cap]
        elif base[path] != head[path]:
            cells = (base[path].count("\n") + 1) * (head[path].count("\n") + 1)
            over_file = cells > cfg["diff_cell_budget"]
            if over_file or spent + cells > cfg["diff_total_cell_budget"]:
                notes.append({"path": path, "reason": DIFF_NOTE if over_file else TOTAL_NOTE})
                files[path] = {"status": "modified", "ranges": _whole(base[path])}
                hunks[path] = head[path][:cap]
                continue
            spent += cells
            ranges, text = diff_file(base[path], head[path])
            if ranges:
                files[path] = {"status": "modified", "ranges": ranges}
                hunks[path] = text[:cap]
    return files, hunks, notes


class Touched:
    """Answers "does a chunk overlap the change?" with a binary search per path."""

    def __init__(self, changed: dict[str, Any]) -> None:
        self._deleted = {p for p, f in changed.items() if f["status"] == "deleted"}
        self._spans: dict[str, tuple[list[int], list[int]]] = {}
        self._gaps: dict[str, list[int]] = {}
        for path, info in changed.items():
            spans = [r for r in info["ranges"] if r["kind"] != "insert"]
            self._spans[path] = ([r["start"] for r in spans], [r["end"] for r in spans])
            self._gaps[path] = sorted(r["start"] for r in info["ranges"] if r["kind"] == "insert")

    def overlaps(self, path: str, start: int, end: int) -> bool:
        """True when lines [start, end] hold or touch a changed line of `path`.

        A range overlaps by line numbers; an insertion after line g overlaps a chunk only when
        the gap lies inside it (start <= g < end).
        """
        if path in self._deleted:
            return True
        if path not in self._spans:
            return False
        starts, ends = self._spans[path]
        i = bisect.bisect_left(ends, start)
        if i < len(starts) and starts[i] <= end:
            return True
        gaps = self._gaps[path]
        j = bisect.bisect_left(gaps, start)
        return j < len(gaps) and gaps[j] < end
