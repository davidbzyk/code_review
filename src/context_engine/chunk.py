"""Cut one file into chunks that follow syntax units (build side; uses tree-sitter).

Every chunk is a run of whole lines. A file's chunks never overlap, so each line is covered at
most once. Units over the size cap are split, small neighbouring units are merged, and a file
that does not parse is cut into line windows and flagged.
"""

from __future__ import annotations

import importlib
import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

from tree_sitter import Language, Node, Parser

# language -> (module, function giving its grammar). JavaScript parses with the TSX grammar.
_GRAMMARS = {
    "rust": ("tree_sitter_rust", "language"),
    "typescript": ("tree_sitter_typescript", "language_typescript"),
    "tsx": ("tree_sitter_typescript", "language_tsx"),
    "javascript": ("tree_sitter_typescript", "language_tsx"),
    "python": ("tree_sitter_python", "language"),
}

# Per grammar: attached (comments, attributes), containers (members worth splitting),
# wrappers (export, decorators) and plain (imports, bare expressions: no signature).
_SPECS: dict[str, dict[str, Any]] = {
    "rust": {
        "attached": {"line_comment", "block_comment", "attribute_item"},
        "containers": {"impl_item", "trait_item", "mod_item"},
        "wrappers": {},
        "inner_start": set(),
        "plain": {"use_declaration", "extern_crate_declaration", "expression_statement"},
    },
    "typescript": {
        "attached": {"comment", "decorator"},
        "containers": {"class_declaration", "abstract_class_declaration"},
        "wrappers": {"export_statement": "declaration"},
        "inner_start": set(),
        "plain": {"import_statement", "expression_statement"},
    },
    "python": {
        "attached": {"comment"},
        "containers": {"class_definition"},
        "wrappers": {"decorated_definition": "definition"},
        "inner_start": {"decorated_definition"},
        "plain": {"import_statement", "import_from_statement", "expression_statement"},
    },
}
_SPECS["tsx"] = _SPECS["javascript"] = _SPECS["typescript"]

_SCRIPT_OPEN = re.compile(r"^[ \t]*<script\b[^>]*>[ \t]*$")
_SCRIPT_CLOSE = re.compile(r"^[ \t]*</script>")
_MAX_SIGNATURE = 160


@dataclass(frozen=True)
class Chunk:
    """A run of whole lines of one file, with its enclosing item's header as signature."""

    path: str
    start: int
    end: int
    language: str
    signature: str
    code: str

    def embed_text(self) -> str:
        """The text that is embedded and BM25-indexed: path, signature, code."""
        return f"{self.path}\n{self.signature}\n{self.code}"


@dataclass
class ChunkResult:
    """The chunks of one file plus what the report needs to know about it."""

    language: str
    chunks: list[Chunk] = field(default_factory=list)
    parse_failed: bool = False
    lines_seen: int = 0
    lines_covered: int = 0


@dataclass(frozen=True)
class _Unit:
    """A run of lines [start, end] (1-based, inclusive) with a signature."""

    start: int
    end: int
    signature: str


def language_of(path: str, settings: dict[str, Any]) -> str:
    """The language name for a path by file extension, or "text"."""
    suffix = PurePosixPath(path).suffix.lower()
    for name, suffixes in settings["languages"].items():
        if suffix in suffixes:
            return name
    return "text"


def split_lines(text: str) -> list[str]:
    """Split text into lines on \\n only, so row numbers match the parser's."""
    lines = text.replace("\r\n", "\n").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def _blank(line: str) -> bool:
    """True for an empty or whitespace-only line."""
    return not line.strip()


def _span_chars(lines: list[str], start: int, end: int) -> int:
    """Characters in lines [start, end], counting one newline per line."""
    return sum(len(line) + 1 for line in lines[start - 1 : end])


def _end_line(node: Node) -> int:
    """Last 1-based line a node occupies (a node ending at column 0 stops the line before)."""
    row, col = node.end_point
    if col == 0 and row > node.start_point[0]:
        row -= 1
    return row + 1


def _unwrap(node: Node, spec: dict[str, Any]) -> Node:
    """Follow wrapper nodes (export, decorators) down to the declaration."""
    while node.type in spec["wrappers"]:
        inner = node.child_by_field_name(spec["wrappers"][node.type])
        if inner is None:
            break
        node = inner
    return node


def _header(node: Node, src: bytes, spec: dict[str, Any]) -> str:
    """One-line header of an item: its text up to its body, whitespace collapsed."""
    inner = _unwrap(node, spec)
    body = inner.child_by_field_name("body")
    first = inner if node.type in spec["inner_start"] else node
    if body is not None:
        raw = src[first.start_byte : body.start_byte]
    else:
        raw = src[first.start_byte : first.end_byte].split(b"\n", 1)[0]
    return " ".join(raw.decode("utf-8", "replace").split())[:_MAX_SIGNATURE]


def _members(node: Node, spec: dict[str, Any]) -> list[Node] | None:
    """The member nodes of a container item (impl, trait, class), or None."""
    inner = _unwrap(node, spec)
    if inner.type not in spec["containers"]:
        return None
    body = inner.child_by_field_name("body")
    return list(body.named_children) if body is not None else None


def _extract(
    siblings: list[Node],
    spec: dict[str, Any],
    src: bytes,
    lines: list[str],
    caps: tuple[int, int, int],
    prefix: str,
    depth: int = 0,
) -> list[_Unit]:
    """Units for a run of sibling nodes, descending into containers that are over the cap."""
    attached = spec["attached"]
    units: list[_Unit] = []
    taken = 0
    for i, node in enumerate(siblings):
        if node.type in attached:
            continue
        first_row = node.start_point[0]
        j = i - 1
        while j >= 0 and siblings[j].type in attached and _end_line(siblings[j]) >= first_row:
            before = siblings[j - 1] if j > 0 else None
            own_row = siblings[j].start_point[0]
            if before is not None and before.type not in attached and _end_line(before) > own_row:
                break  # a trailing comment of the statement before, not ours
            first_row = own_row
            j -= 1
        start = max(first_row + 1, taken + 1)
        end = min(_end_line(node), len(lines))
        if start > end:
            continue
        header = "" if node.type in spec["plain"] else _header(node, src, spec)
        signature = f"{prefix} :: {header}" if prefix and header else header
        taken = end
        members = _members(node, spec)
        too_big = end - start + 1 > caps[0] or _span_chars(lines, start, end) > caps[1]
        if members and too_big and depth < caps[2]:
            sub = _extract(members, spec, src, lines, caps, signature, depth + 1)
            if sub:
                if sub[0].start > start:
                    units.append(_Unit(start, sub[0].start - 1, signature))
                units.extend(sub)
                continue
        units.append(_Unit(start, end, signature))
    return units


def _code_units(lines: list[str], language: str, caps: tuple[int, int, int]) -> list[_Unit] | None:
    """Syntax units of a code file, or None when it does not parse cleanly."""
    module, func = _GRAMMARS[language]
    grammar = getattr(importlib.import_module(module), func)()
    src = "\n".join(lines).encode("utf-8")
    root = Parser(Language(grammar)).parse(src).root_node
    if root.has_error:
        return None
    return _extract(list(root.children), _SPECS[language], src, lines, caps, "")


def _fill_gaps(units: list[_Unit], lo: int, hi: int) -> list[_Unit]:
    """Add signature-less units for the lines between units so [lo, hi] is fully covered."""
    out: list[_Unit] = []
    pos = lo
    for unit in units:
        if unit.start > pos:
            out.append(_Unit(pos, unit.start - 1, ""))
        out.append(unit)
        pos = unit.end + 1
    if pos <= hi:
        out.append(_Unit(pos, hi, ""))
    return out


def _split(unit: _Unit, lines: list[str], max_lines: int, max_chars: int) -> list[_Unit]:
    """Cut a unit into pieces within both caps, preferring to cut after a blank line."""
    pieces: list[_Unit] = []
    pos = unit.start
    while pos <= unit.end:
        stop = pos
        chars = len(lines[pos - 1]) + 1
        while stop < unit.end and stop - pos + 1 < max_lines:
            chars += len(lines[stop]) + 1
            if chars > max_chars:
                break
            stop += 1
        if stop < unit.end:
            floor = pos + (stop - pos) * 3 // 4
            for cut in range(stop, floor, -1):
                if _blank(lines[cut - 1]):
                    stop = cut
                    break
        pieces.append(_Unit(pos, stop, unit.signature))
        pos = stop + 1
    return pieces


def _merge(units: list[_Unit], lines: list[str], max_lines: int, max_chars: int) -> list[_Unit]:
    """Merge adjacent units while the result stays within the merge target."""
    out: list[_Unit] = []
    for unit in units:
        if out:
            last = out[-1]
            size = unit.end - last.start + 1
            if size <= max_lines and _span_chars(lines, last.start, unit.end) <= max_chars:
                out[-1] = _Unit(last.start, unit.end, last.signature or unit.signature)
                continue
        out.append(unit)
    return out


def _to_chunks(
    path: str, language: str, lines: list[str], units: list[_Unit], offset: int = 0
) -> list[Chunk]:
    """Turn units into chunks, trimming blank edges and dropping blank-only units."""
    chunks = []
    for unit in units:
        start, end = unit.start, unit.end
        while start <= end and _blank(lines[start - 1]):
            start += 1
        while end >= start and _blank(lines[end - 1]):
            end -= 1
        if start > end:
            continue
        code = "\n".join(lines[start - 1 : end])
        chunks.append(Chunk(path, start + offset, end + offset, language, unit.signature, code))
    return chunks


def _pipeline(
    path: str,
    language: str,
    lines: list[str],
    units: list[_Unit],
    cfg: dict[str, Any],
    cap_lines: int,
    offset: int = 0,
) -> list[Chunk]:
    """Fill gaps, split over-cap units, merge small ones and build the chunks."""
    full = _fill_gaps(units, 1, len(lines))
    split: list[_Unit] = []
    for unit in full:
        if (
            unit.end - unit.start + 1 > cap_lines
            or _span_chars(lines, unit.start, unit.end) > cfg["size_cap_chars"]
        ):
            split.extend(_split(unit, lines, cap_lines, cfg["size_cap_chars"]))
        else:
            split.append(unit)
    merged = _merge(split, lines, cfg["merge_target_lines"], cfg["merge_target_chars"])
    return _to_chunks(path, language, lines, merged, offset)


def _windows(path: str, language: str, lines: list[str], cfg: dict[str, Any], offset: int = 0):
    """Line-window chunks over a run of lines (no signatures, no merging across windows)."""
    whole = [_Unit(1, len(lines), "")] if lines else []
    split = []
    for unit in whole:
        split.extend(_split(unit, lines, cfg["window_lines"], cfg["size_cap_chars"]))
    return _to_chunks(path, language, lines, split, offset)


def _script_blocks(lines: list[str]) -> list[tuple[int, int]]:
    """(first, last) 1-based body lines of each script block, found in one pass.

    An opening line with no closing line after it ends the scan: the rest is markup.
    """
    blocks: list[tuple[int, int]] = []
    i = 0
    while i < len(lines):
        if not _SCRIPT_OPEN.match(lines[i]):
            i += 1
            continue
        j = i + 1
        while j < len(lines) and not _SCRIPT_CLOSE.match(lines[j]):
            j += 1
        if j == len(lines):
            break
        if j > i + 1:
            blocks.append((i + 2, j))
        i = j + 1
    return blocks


def _svelte(path: str, lines: list[str], cfg: dict[str, Any]) -> ChunkResult:
    """Script blocks chunked as TypeScript with original line numbers; markup in windows."""
    result = ChunkResult("svelte")
    caps = (cfg["size_cap_lines"], cfg["size_cap_chars"], cfg["max_container_depth"])
    pos = 1
    for first, last in _script_blocks(lines):
        result.chunks += _windows(path, "svelte", lines[pos - 1 : first - 1], cfg, pos - 1)
        body = lines[first - 1 : last]
        units = _code_units(body, "typescript", caps)
        if units is None:
            result.parse_failed = True
            result.chunks += _windows(path, "typescript", body, cfg, first - 1)
        else:
            result.chunks += _pipeline(
                path, "typescript", body, units, cfg, cfg["size_cap_lines"], first - 1
            )
        pos = last + 1
    result.chunks += _windows(path, "svelte", lines[pos - 1 :], cfg, pos - 1)
    return result


def chunk_file(path: str, text: str, settings: dict[str, Any]) -> ChunkResult:
    """Chunk one file's text. Never returns an empty result for a file with content."""
    cfg = settings["chunk"]
    language = language_of(path, settings)
    text = text.replace("\r\n", "\n")
    lines = split_lines(text)
    caps = (cfg["size_cap_lines"], cfg["size_cap_chars"], cfg["max_container_depth"])
    if language == "svelte":
        result = _svelte(path, lines, cfg)
    elif language in _GRAMMARS:
        units = _code_units(lines, language, caps)
        result = ChunkResult(language)
        if units is None:
            result.parse_failed = True
            result.chunks = _windows(path, language, lines, cfg)
        else:
            result.chunks = _pipeline(path, language, lines, units, cfg, cfg["size_cap_lines"])
    else:
        result = ChunkResult(language, chunks=_windows(path, language, lines, cfg))
    result.lines_seen = sum(1 for line in lines if not _blank(line))
    covered = {n for c in result.chunks for n in range(c.start, c.end + 1)}
    result.lines_covered = sum(1 for n in covered if not _blank(lines[n - 1]))
    return result
