"""Shared primitives for the okf plugin.

Stdlib only, on purpose: every script here must run under a bare `python3` with
no site-packages, so that `okf_verify.py` can be copied verbatim into a bundle's
own `scripts/` directory and still work. That constraint is why this module
carries its own YAML-subset parser and its own JSON Schema Draft-07 subset
validator instead of importing PyYAML and jsonschema.

Vocabulary follows the OKF v0.2 specification as transcribed in
`okf/standards/okf_protocol_reference.md`:

  concept        a non-reserved .md file; its id IS its bundle-relative path
                 minus the .md suffix (spec section 2)
  reserved       index.md and log.md (spec section 3.1)
  conformance    the mechanical checklist in spec section 11
  local profile  this repository's stricter producer rules, which a consumer
                 MUST NOT reject a bundle for (spec section 11)
"""
from __future__ import annotations

import fnmatch
import json
import os
import posixpath
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Iterator, NamedTuple

# ---------------------------------------------------------------------------
# exit codes, shared by every CLI in this plugin
# ---------------------------------------------------------------------------

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_FATAL = 2

RESERVED_NAMES = ("index.md", "log.md")

#: Timestamps must be ISO 8601 with an explicit UTC offset (spec section 5).
TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}"
    r"(?:[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2}))?$"
)
#: The subset that carries a time-of-day, which is where the offset is required.
DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})$"
)
DATE_ONLY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

#: Actor convention (spec section 7): producer/version, human:<id>, process:<id>.
ACTOR_RE = re.compile(r"^(?:human:.+|process:.+|[^/\s]+/[^/\s]+)$")

# Every repeat is length-capped. An unclosed link used to make each opening scan to the end of
# the text, which is quadratic; a real label, target or title is far shorter than these caps.
MD_LINK_RE = re.compile(
    r"(?<!!)\[(?:[^\]]{0,1000})\]\(([^)\s]{1,2000})(?:\s{1,8}\"[^\"]{0,500}\")?\)"
)
WIKI_LINK_RE = re.compile(r"\[\[([^\]|]{1,500}?)(?:\|[^\]]{0,500})?\]\]")
FOOTNOTE_USE_RE = re.compile(r"(?<!^)\[\^([^\]]+)\]", re.MULTILINE)
FOOTNOTE_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:", re.MULTILINE)
VERBATIM_START_RE = re.compile(r"<!--\s*okf:verbatim:start\s+(\S+)\s*-->")
VERBATIM_END_RE = re.compile(r"<!--\s*okf:verbatim:end\s*-->")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


# ---------------------------------------------------------------------------
# YAML subset
# ---------------------------------------------------------------------------

class YamlError(ValueError):
    """Raised when the frontmatter is not parseable by the supported subset."""


class _Line:
    __slots__ = ("indent", "text", "no")

    def __init__(self, indent: int, text: str, no: int) -> None:
        self.indent = indent
        self.text = text
        self.no = no

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"_Line({self.indent}, {self.text!r}, {self.no})"


def _scan(src: str) -> list[_Line]:
    out: list[_Line] = []
    for i, raw in enumerate(src.splitlines(), start=1):
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise YamlError(f"line {i}: tab in indentation")
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        out.append(_Line(len(raw) - len(raw.lstrip(" ")), stripped, i))
    return out


#: Flow values (`[a, [b]]`, `{k: {j: v}}`) nested deeper than this are refused, not recursed into.
MAX_FLOW_DEPTH = 32


def _scalar(tok: str, depth: int = 0) -> Any:
    """Parse a YAML scalar. Quoted values always come back as `str`."""
    if depth > MAX_FLOW_DEPTH:
        raise YamlError(f"flow value nested too deeply (more than {MAX_FLOW_DEPTH} levels)")
    tok = tok.strip()
    if not tok:
        return None
    if len(tok) >= 2 and tok[0] == tok[-1] and tok[0] in "\"'":
        body = tok[1:-1]
        if tok[0] == '"':
            body = body.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")
        else:
            body = body.replace("''", "'")
        return body
    if tok in ("null", "Null", "NULL", "~"):
        return None
    if tok in ("true", "True", "TRUE", "yes", "on"):
        return True
    if tok in ("false", "False", "FALSE", "no", "off"):
        return False
    if tok == "[]":
        return []
    if tok == "{}":
        return {}
    if tok.startswith("[") and tok.endswith("]"):
        inner = tok[1:-1].strip()
        return [_scalar(p, depth + 1) for p in _split_flow(inner)] if inner else []
    if tok.startswith("{") and tok.endswith("}"):
        inner = tok[1:-1].strip()
        out: dict[str, Any] = {}
        for part in _split_flow(inner):
            at = _flow_colon(part)
            if at < 0:
                raise YamlError(f"flow mapping entry without a colon: {part[:80]!r}")
            key = _scalar(part[:at], depth + 1)
            if isinstance(key, (list, dict)):
                raise YamlError(f"flow mapping key must be a scalar: {part[:at][:80]!r}")
            out[key] = _scalar(part[at + 1 :], depth + 1)
        return out
    if re.fullmatch(r"[+-]?\d+", tok):
        try:
            return int(tok)
        except ValueError:  # more digits than Python will convert: keep the text
            return tok
    if re.fullmatch(r"[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?", tok):
        return float(tok)
    return tok


def _flow_colon(part: str) -> int:
    """Index of the first colon outside quotes and brackets in a flow mapping entry, or -1."""
    depth, quote = 0, ""
    for i, ch in enumerate(part):
        if quote:
            quote = "" if ch == quote else quote
        elif ch in "\"'":
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        elif ch == ":" and depth == 0:
            return i
    return -1


def _split_flow(text: str) -> list[str]:
    """Split a flow sequence or mapping body at its top-level commas.

    Brackets and quotes must balance: a stray closer used to drive the depth negative, after
    which no comma split and the rest was read as one value.
    """
    parts, depth, buf, quote = [], 0, [], ""
    for ch in text:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = ""
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch in "[{":
            depth += 1
            buf.append(ch)
        elif ch in "]}":
            depth -= 1
            if depth < 0:
                raise YamlError("flow value has a closing bracket with nothing open")
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if depth or quote:
        raise YamlError("flow value has an unclosed bracket or quote")
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def _split_key(text: str) -> tuple[str, str] | None:
    """Split `key: value`, tolerating colons inside a quoted key or value."""
    if text.startswith(('"', "'")):
        q = text[0]
        end = text.find(q, 1)
        while end != -1 and end + 1 < len(text) and text[end + 1] == q:
            end = text.find(q, end + 2)
        if end == -1:
            return None
        rest = text[end + 1:].lstrip()
        if not rest.startswith(":"):
            return None
        return _scalar(text[: end + 1]), rest[1:].strip()
    idx = text.find(":")
    while idx != -1:
        after = text[idx + 1: idx + 2]
        if after in ("", " "):
            return text[:idx].strip(), text[idx + 1:].strip()
        idx = text.find(":", idx + 1)
    return None


def _parse_block(lines: list[_Line], i: int, indent: int) -> tuple[Any, int]:
    if i >= len(lines):
        return None, i
    if lines[i].text.startswith("- ") or lines[i].text == "-":
        return _parse_seq(lines, i, lines[i].indent)
    return _parse_map(lines, i, lines[i].indent)


def _parse_seq(lines: list[_Line], i: int, indent: int) -> tuple[list[Any], int]:
    items: list[Any] = []
    while i < len(lines) and lines[i].indent == indent and (
        lines[i].text == "-" or lines[i].text.startswith("- ")
    ):
        line = lines[i]
        rest = line.text[1:].strip()
        i += 1
        if not rest:
            if i < len(lines) and lines[i].indent > indent:
                value, i = _parse_block(lines, i, lines[i].indent)
                items.append(value)
            else:
                items.append(None)
            continue
        kv = _split_key(rest)
        if kv is None:
            items.append(_scalar(rest))
            continue
        # An inline mapping opened by `- key: value`; its members sit at the
        # column where `key` began, which is two past the dash.
        inner_indent = indent + 2
        synthetic = [_Line(inner_indent, rest, line.no)]
        while i < len(lines) and lines[i].indent >= inner_indent:
            synthetic.append(lines[i])
            i += 1
        value, consumed = _parse_map(synthetic, 0, inner_indent)
        if consumed != len(synthetic):
            raise YamlError(f"line {synthetic[consumed].no}: unexpected indentation")
        items.append(value)
    return items, i


def _parse_map(lines: list[_Line], i: int, indent: int) -> tuple[dict[str, Any], int]:
    out: dict[str, Any] = {}
    while i < len(lines) and lines[i].indent == indent:
        line = lines[i]
        if line.text.startswith("- ") or line.text == "-":
            break
        kv = _split_key(line.text)
        if kv is None:
            raise YamlError(f"line {line.no}: expected 'key: value', got {line.text!r}")
        key, rest = kv
        i += 1
        if rest:
            out[key] = _scalar(rest)
            continue
        if i < len(lines) and lines[i].indent > indent:
            out[key], i = _parse_block(lines, i, lines[i].indent)
        elif i < len(lines) and lines[i].indent == indent and (
            lines[i].text == "-" or lines[i].text.startswith("- ")
        ):
            # YAML permits a sequence at the same column as its parent key.
            out[key], i = _parse_seq(lines, i, indent)
        else:
            out[key] = None
    return out, i


def parse_yaml(src: str) -> dict[str, Any]:
    """Parse the YAML subset used by OKF frontmatter into a dict."""
    lines = _scan(src)
    if not lines:
        return {}
    value, consumed = _parse_map(lines, 0, lines[0].indent)
    if consumed != len(lines):
        raise YamlError(f"line {lines[consumed].no}: unexpected indentation")
    return value


# ---------------------------------------------------------------------------
# frontmatter
# ---------------------------------------------------------------------------

class Frontmatter:
    """The result of splitting one markdown file into frontmatter and body."""

    __slots__ = ("data", "body", "raw", "error", "present", "body_offset", "quoted_keys")

    def __init__(
        self,
        data: dict[str, Any],
        body: str,
        raw: str,
        error: str | None,
        present: bool,
        body_offset: int,
        quoted_keys: set[str],
    ) -> None:
        self.data = data
        self.body = body
        self.raw = raw
        self.error = error
        self.present = present
        self.body_offset = body_offset
        self.quoted_keys = quoted_keys

    @property
    def ok(self) -> bool:
        return self.present and self.error is None


def split_frontmatter(text: str) -> Frontmatter:
    """Split a `---` delimited YAML frontmatter block off the front of `text`.

    A block whose closing fence is glued to the last value (`key: v---`) is
    reported as an error rather than silently swallowed, because that is a real
    defect a producer needs to see.
    """
    if not text.startswith("---"):
        return Frontmatter({}, text, "", None, False, 0, set())
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return Frontmatter({}, text, "", None, False, 0, set())
    for idx in range(1, len(lines)):
        if lines[idx].strip() in ("---", "..."):
            raw = "\n".join(lines[1:idx])
            body = "\n".join(lines[idx + 1:])
            try:
                data = parse_yaml(raw)
            except YamlError as exc:
                return Frontmatter({}, body, raw, str(exc), True, idx + 1, set())
            if not isinstance(data, dict):
                return Frontmatter({}, body, raw, "frontmatter is not a mapping", True, idx + 1, set())
            return Frontmatter(data, body, raw, None, True, idx + 1, _quoted_keys(raw))
        if lines[idx].rstrip().endswith("---") and lines[idx].strip() != "---":
            return Frontmatter(
                {}, text, "",
                f"line {idx + 1}: closing '---' is glued to the value "
                f"({lines[idx].strip()!r}); it needs its own line",
                True, 0, set(),
            )
    return Frontmatter({}, text, "", "no closing '---' fence", True, 0, set())


def _quoted_keys(raw: str) -> set[str]:
    """Top-level keys whose scalar value was written quoted (local rule 10.1.1)."""
    found: set[str] = set()
    for line in raw.split("\n"):
        if not line or line[0] in " -#":
            continue
        kv = _split_key(line.strip())
        if kv is None:
            continue
        key, rest = kv
        if rest[:1] in ('"', "'"):
            found.add(key)
    return found


# ---------------------------------------------------------------------------
# bundle model
# ---------------------------------------------------------------------------

class Doc:
    """One markdown file inside a bundle."""

    __slots__ = ("path", "rel", "fm", "text", "kind")

    def __init__(self, path: Path, rel: str, text: str, fm: Frontmatter) -> None:
        self.path = path
        self.rel = rel
        self.text = text
        self.fm = fm
        name = path.name
        self.kind = name if name in RESERVED_NAMES else "concept"

    @property
    def concept_id(self) -> str:
        """The spec identity: bundle-relative path with `.md` removed."""
        return self.rel[:-3] if self.rel.endswith(".md") else self.rel

    @property
    def is_concept(self) -> bool:
        return self.kind == "concept"

    @property
    def is_root_index(self) -> bool:
        return self.rel == "index.md"

    def type_of(self) -> str:
        value = self.fm.data.get("type")
        return value if isinstance(value, str) else ""


def iter_markdown(root: Path) -> Iterator[Path]:
    """Every .md under `root`, sorted, skipping dot-directories and schemas/."""
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if any(part.startswith(".") for part in rel.parts):
            continue
        yield path


def load_bundle(root: Path, *, include_schemas: bool = False) -> list[Doc]:
    """Read every markdown file in a bundle into a `Doc`, sorted by path.

    `schemas/templates/` is excluded by default: templates are placeholders, not
    concepts, and they deliberately carry unfilled frontmatter.
    """
    docs: list[Doc] = []
    for path in iter_markdown(root):
        rel = path.relative_to(root).as_posix()
        if not include_schemas and rel.startswith("schemas/templates/"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        docs.append(Doc(path, rel, text, split_frontmatter(text)))
    return docs


INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def without_inline_code(line: str) -> str:
    """Blank out `inline code spans`.

    A document that documents OKF quotes OKF syntax inline. Those quotations are
    examples, not markup: a marker or a link inside backticks must not be read
    as the real thing.
    """
    return INLINE_CODE_RE.sub("", line)


def strip_code_and_verbatim(body: str) -> str:
    """Blank out fenced code blocks, inline code spans, and okf:verbatim regions.

    Links inside any of them are archival or illustrative text and are exempt
    from link checking (local rule 10.1.5).
    """
    out: list[str] = []
    fence: str | None = None
    verbatim = False
    for line in body.split("\n"):
        if verbatim:
            out.append("")
            if VERBATIM_END_RE.search(line):
                verbatim = False
            continue
        if fence is None and VERBATIM_START_RE.search(without_inline_code(line)):
            verbatim = True
            out.append("")
            continue
        m = FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = marker
            elif line.strip().startswith(fence):
                fence = None
            out.append("")
            continue
        out.append("" if fence else without_inline_code(line))
    return "\n".join(out)


def verbatim_regions(body: str) -> list[tuple[str, str]]:
    """Return (source_path, captured_text) for each okf:verbatim region."""
    regions: list[tuple[str, str]] = []
    lines = body.split("\n")
    i = 0
    while i < len(lines):
        m = VERBATIM_START_RE.search(without_inline_code(lines[i]))
        if not m:
            i += 1
            continue
        src = m.group(1)
        j = i + 1
        captured: list[str] = []
        while j < len(lines) and not VERBATIM_END_RE.search(without_inline_code(lines[j])):
            captured.append(lines[j])
            j += 1
        regions.append((src, "\n".join(captured)))
        i = j + 1
    return regions


def word_count(text: str) -> int:
    """Words in the prose body, ignoring frontmatter and code fences."""
    return len(re.findall(r"\S+", strip_code_and_verbatim(text)))


def code_line_count(body: str) -> int:
    """Lines inside fenced code blocks (fence lines excluded), summed over the body."""
    count = 0
    fence: str | None = None
    for line in body.split("\n"):
        m = FENCE_RE.match(line)
        if m:
            if fence is None:
                fence = m.group(1)
            elif line.strip().startswith(fence):
                fence = None
            else:
                count += 1
        elif fence:
            count += 1
    return count


# ---------------------------------------------------------------------------
# JSON Schema Draft-07 subset
# ---------------------------------------------------------------------------

_TYPES: dict[str, tuple[type, ...] | type] = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}


class SchemaStore:
    """Loads and caches the schemas under a `schemas/v1` directory."""

    def __init__(self, root: Path, domains: tuple[str, ...] | None = None) -> None:
        self.root = root
        self.domains = domains
        self._cache: dict[str, dict[str, Any]] = {}

    def get(self, name: str) -> dict[str, Any] | None:
        name = Path(name).name
        if name in self._cache:
            return self._cache[name]
        path = self.root / name
        if not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        domain = data.get("properties", {}).get("domain") if name == "base.json" else None
        if self.domains and isinstance(domain, dict):
            domain["enum"] = list(self.domains)  # the bundle's own domain list wins
        self._cache[name] = data
        return data

    def validate(self, instance: Any, schema: dict[str, Any], where: str = "") -> list[str]:
        return _validate(instance, schema, where, self)


def _type_ok(value: Any, expected: str) -> bool:
    want = _TYPES.get(expected)
    if want is None:
        return True
    if expected in ("integer", "number") and isinstance(value, bool):
        return False
    if expected == "boolean":
        return isinstance(value, bool)
    return isinstance(value, want)


def _validate(instance: Any, schema: dict[str, Any], where: str, store: SchemaStore) -> list[str]:
    errs: list[str] = []
    ref = schema.get("$ref")
    if isinstance(ref, str):
        target = store.get(ref)
        if target is None:
            errs.append(f"{where or '<root>'}: unresolvable $ref {ref!r}")
        else:
            errs.extend(_validate(instance, target, where, store))

    for sub in schema.get("allOf", []) or []:
        errs.extend(_validate(instance, sub, where, store))

    one_of = schema.get("oneOf") or schema.get("anyOf")
    if one_of:
        if not any(not _validate(instance, sub, where, store) for sub in one_of):
            errs.append(f"{where or '<root>'}: matches none of the permitted shapes")

    expected = schema.get("type")
    if expected is not None:
        options = expected if isinstance(expected, list) else [expected]
        if not any(_type_ok(instance, opt) for opt in options):
            errs.append(f"{where or '<root>'}: expected type {'|'.join(options)}, got {_kind(instance)}")
            return errs

    enum = schema.get("enum")
    if enum is not None and instance not in enum:
        errs.append(f"{where or '<root>'}: {instance!r} is not one of {enum}")

    if isinstance(instance, str):
        pattern = schema.get("pattern")
        if pattern and not re.search(pattern, instance):
            errs.append(f"{where or '<root>'}: {instance!r} does not match /{pattern}/")
        min_len = schema.get("minLength")
        if isinstance(min_len, int) and len(instance) < min_len:
            errs.append(f"{where or '<root>'}: shorter than minLength {min_len}")

    if isinstance(instance, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(instance) < min_items:
            errs.append(f"{where or '<root>'}: needs at least {min_items} item(s)")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(instance):
                errs.extend(_validate(item, item_schema, f"{where}[{idx}]", store))

    if isinstance(instance, dict):
        for key in schema.get("required", []) or []:
            if key not in instance or instance[key] is None:
                errs.append(f"{where or '<root>'}: missing required key {key!r}")
        props = schema.get("properties") or {}
        for key, sub in props.items():
            if key in instance and instance[key] is not None:
                errs.extend(_validate(instance[key], sub, f"{where}.{key}" if where else key, store))
    return errs


def _kind(value: Any) -> str:
    for name, want in _TYPES.items():
        if name == "number":
            continue
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, want):  # type: ignore[arg-type]
            return name
    return type(value).__name__


# ---------------------------------------------------------------------------
# findings and reporting
# ---------------------------------------------------------------------------

class Finding:
    """One problem, in one tier, about one file."""

    __slots__ = ("tier", "rule", "where", "message", "fix")

    def __init__(self, tier: str, rule: str, where: str, message: str, fix: str = "") -> None:
        self.tier = tier
        self.rule = rule
        self.where = where
        self.message = message
        self.fix = fix

    def as_dict(self) -> dict[str, str]:
        return {
            "tier": self.tier,
            "rule": self.rule,
            "where": self.where,
            "message": self.message,
            "fix": self.fix,
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Finding({self.tier}, {self.rule}, {self.where})"


def emit_json(payload: Any) -> None:
    """Deterministic JSON: sorted keys, trailing newline."""
    json.dump(payload, sys.stdout, indent=2, sort_keys=True, default=str)
    sys.stdout.write("\n")


def table(rows: Iterable[Iterable[Any]], headers: Iterable[str]) -> str:
    """A plain two-space-padded text table, wide enough for its content."""
    head = [str(h) for h in headers]
    body = [[("" if c is None else str(c)) for c in row] for row in rows]
    widths = [len(h) for h in head]
    for row in body:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))
    out = ["  ".join(h.ljust(widths[i]) for i, h in enumerate(head)).rstrip()]
    out.append("  ".join("-" * w for w in widths))
    for row in body:
        out.append("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip())
    return "\n".join(out)


def resolve_bundle(arg: str) -> Path:
    path = Path(os.path.expanduser(arg)).resolve()
    if not path.is_dir():
        die(f"not a directory: {path}")
    return path


def die(message: str, code: int = EXIT_FATAL) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


# ---------------------------------------------------------------------------
# coverage: which notes claim which source paths
# ---------------------------------------------------------------------------

WILDCARD_RE = re.compile(r"[*?\[]")


class CoverageRule(NamedTuple):
    """One note's claim on a source path: an exact path, or a glob from `covers`."""

    pattern: str
    concept_id: str
    is_glob: bool


def entry_path(entry: Any) -> str:
    """The path of a `sources`/`covers` entry, written as a string or a mapping."""
    if isinstance(entry, dict):
        for key in ("resource", "path", "pattern"):
            if isinstance(entry.get(key), str) and entry[key].strip():
                return entry[key].strip()
        return ""
    return str(entry).strip() if isinstance(entry, str) else ""


def clean_path(raw: str) -> str:
    """A repo-relative POSIX path: no fragment, no leading `/` or `./`, normalized."""
    return posixpath.normpath(raw.split("#", 1)[0].strip().lstrip("/"))


def glob_match(path: str, pattern: str) -> bool:
    """Segment-wise glob where `**` spans directories; same semantics as ge-okf's coverage index."""
    path_parts = posixpath.normpath(path).split("/")
    reachable = [False] * (len(path_parts) + 1)
    reachable[0] = True
    for part in posixpath.normpath(pattern).split("/"):
        following = [False] * (len(path_parts) + 1)
        if part == "**":
            seen = False
            for index in range(len(path_parts) + 1):
                seen = seen or reachable[index]
                following[index] = seen
        else:
            for index, path_part in enumerate(path_parts):
                if reachable[index] and fnmatch.fnmatchcase(path_part, part):
                    following[index + 1] = True
        reachable = following
    return reachable[-1]


def coverage_rules(docs: Iterable["Doc"]) -> list[CoverageRule]:
    """Every exact (`resource`, `sources`) and glob (`covers`) claim the concepts make."""
    rules: set[CoverageRule] = set()
    for doc in docs:
        if not doc.is_concept or not doc.fm.ok:
            continue
        data = doc.fm.data
        for key in ("resource", "sources", "covers"):
            for entry in data.get(key) if isinstance(data.get(key), list) else [data.get(key)]:
                raw = entry_path(entry)
                if not raw or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", raw):
                    continue
                path = clean_path(raw)
                rules.add(CoverageRule(path, doc.concept_id, key == "covers" and bool(WILDCARD_RE.search(path))))
    return sorted(rules)


def covering_notes(rules: Iterable[CoverageRule], path: str) -> set[str]:
    """Concept ids whose exact path equals `path` or whose glob matches it."""
    path = clean_path(path)
    return {r.concept_id for r in rules if (glob_match(path, r.pattern) if r.is_glob else r.pattern == path)}


#: The domains the plugin shipped with. A bundle replaces them with `domains` in its config.
DEFAULT_DOMAINS = (
    "evaluations", "infrastructure", "governance", "posttraining", "superpowers",
    "standards", "architecture", "meta", "lineage", "evidence", "inventory",
    "tombstones", "runs",
)
CONFIG_NAME = "okf.config.json"


class Config:
    """Per-bundle settings read from `okf.config.json` at the bundle root.

    domains     the allowed values of the `domain` frontmatter key; None means
                "the schemas' own list" (and DEFAULT_DOMAINS for migrate)
    code_roots  repo-relative directory prefixes that count as source code, plus any
                existing file directly in repo_root; empty means "any path that
                exists under repo_root"
    repo_root   where repo-relative paths resolve, relative to the bundle
    """

    __slots__ = ("domains", "code_roots", "repo_root")

    def __init__(self, domains: tuple[str, ...] | None, code_roots: tuple[str, ...], repo_root: Path) -> None:
        self.domains = domains
        self.code_roots = code_roots
        self.repo_root = repo_root


def load_config(bundle: Path, repo_root: Path | None = None) -> Config:
    """Read the bundle's config, falling back to defaults; a malformed file is fatal."""
    path = bundle / CONFIG_NAME
    data: dict[str, Any] = {}
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            die(f"{path}: not valid JSON ({exc})")
        if not isinstance(data, dict):
            die(f"{path}: must be a JSON object")
    for key in ("domains", "code_roots"):
        value = data.get(key, [])
        if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
            die(f"{path}: {key} must be a list of non-empty strings")
    raw_root = data.get("repo_root")
    if raw_root is not None and not isinstance(raw_root, str):
        die(f"{path}: repo_root must be a string")
    if repo_root is None:
        repo_root = (bundle / raw_root).resolve() if raw_root else bundle.parent
    roots = tuple(r.strip().lstrip("/").rstrip("/") + "/" for r in data.get("code_roots", []))
    domains = tuple(data["domains"]) if data.get("domains") else None
    return Config(domains, roots, repo_root)


def in_code_root(path: str, code_roots: tuple[str, ...], repo_root: Path) -> bool:
    """Whether a repo-relative `path` counts as source code.

    With `code_roots`, it is under one of them, or it is an existing file directly
    in `repo_root` (a build manifest has no directory a root could name). With none,
    the static prefix of `path` exists under `repo_root`.
    """
    if code_roots:
        if any(path.startswith(root) for root in code_roots):
            return True
        return "/" not in path and not WILDCARD_RE.search(path) and (repo_root / path).is_file()
    static: list[str] = []
    for part in path.split("/"):
        if WILDCARD_RE.search(part):
            break
        static.append(part)
    return bool(static) and (repo_root / "/".join(static)).exists()


def plugin_root() -> Path:
    """This plugin's root, whether run in place or copied into a bundle."""
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env and Path(env).is_dir():
        return Path(env)
    return Path(__file__).resolve().parent.parent
