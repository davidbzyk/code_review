"""Bundle the aggregator into the orchestrator skill so the skill runs with only Python 3 and git.

The bundle is `aggregate.py` plus a `review_core/` package holding exactly the modules the
aggregator's command line imports, found by reading imports with `ast`. Files are copied byte for
byte, so a second run changes nothing. `--check` reports drift and writes nothing.

    python3 scripts/build_plugin.py            # write the bundle
    python3 scripts/build_plugin.py --check    # exit 1 and name the files that differ

A second kind of copy, for the Harbor images, is described in a TOML file (`--vendors`, default
evals/vendor.toml): one table per copy, with a destination folder, the
packages to follow, the entry modules and extra globs. `--vendor NAME` builds or checks one:

    python3 scripts/build_plugin.py --vendor grader
    python3 scripts/build_plugin.py --vendor grader --check
"""

from __future__ import annotations

import argparse
import ast
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

ENTRY_MODULE = "review_core.aggregator.cli"
PACKAGE = "review_core"
BUNDLE = Path("src/plugin/skills/review-orchestrator/scripts")

AGGREGATE = '''"""Entry point of the bundled review aggregator: `first-pass` and `finalize`."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from review_core.aggregator.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
'''


def _module_file(src: Path, module: str) -> Path | None:
    """Source file of a dotted module under src, or None when it is not ours."""
    base = src.joinpath(*module.split("."))
    if base.with_suffix(".py").is_file():
        return base.with_suffix(".py")
    if (base / "__init__.py").is_file():
        return base / "__init__.py"
    return None


def _imports(path: Path, packages: tuple[str, ...] = (PACKAGE,)) -> set[str]:
    """Dotted names of modules of our packages a file imports; relative imports are refused."""
    found = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                raise SystemExit(f"{path}: relative imports are not followed; use absolute ones")
            head = node.module or ""
            found.add(head)
            found |= {f"{head}.{a.name}" for a in node.names}  # `from pkg import submodule`
    return {
        name for name in found if any(name == pkg or name.startswith(pkg + ".") for pkg in packages)
    }


def closure(
    src: Path, entries: tuple[str, ...] = (ENTRY_MODULE,), packages: tuple[str, ...] = (PACKAGE,)
) -> set[Path]:
    """Files under src the entry modules need, plus each package __init__ on the way."""
    files: set[Path] = set()
    todo = list(entries)
    seen: set[str] = set()
    while todo:
        module = todo.pop()
        if module in seen:
            continue
        seen.add(module)
        path = _module_file(src, module)
        if path is None:
            continue  # a name imported from a module, not a module of its own
        files.add(path)
        parts = module.split(".")
        todo += [".".join(parts[:i]) for i in range(1, len(parts))]
        todo += sorted(_imports(path, packages))
    return files


def expected(root: Path) -> dict[str, bytes]:
    """Bundle contents the sources call for: path under the bundle folder -> bytes."""
    src = root / "src"
    out = {"aggregate.py": AGGREGATE.encode("utf-8")}
    for path in closure(src):
        out[path.relative_to(src).as_posix()] = path.read_bytes()
    return out


def actual(root: Path) -> dict[str, bytes]:
    """Bundle contents on disk, ignoring bytecode caches."""
    folder = root / BUNDLE
    if not folder.is_dir():
        return {}
    return {
        p.relative_to(folder).as_posix(): p.read_bytes()
        for p in folder.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }


def build(root: Path) -> None:
    """Write the bundle, removing files that are no longer part of it."""
    folder = root / BUNDLE
    want = expected(root)
    for name in set(actual(root)) - set(want):
        (folder / name).unlink()
    for name, data in want.items():
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_bytes() != data:
            target.write_bytes(data)


def drift(root: Path) -> list[str]:
    """Names of bundled files that are missing, extra or different."""
    want, have = expected(root), actual(root)
    return sorted(n for n in want.keys() | have.keys() if want.get(n) != have.get(n))


@dataclass(frozen=True)
class Vendor:
    """One copy described in the vendor file."""

    name: str
    dest: str
    packages: tuple[str, ...]
    entries: tuple[str, ...]
    include: tuple[str, ...]


VENDORS = Path("evals/vendor.toml")


def load_vendors(path: Path) -> dict[str, Vendor]:
    """Read the vendor file: one table per copy."""
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    return {
        name: Vendor(
            name,
            table["dest"],
            tuple(table["packages"]),
            tuple(table["entries"]),
            tuple(table.get("include", ())),
        )
        for name, table in raw.items()
    }


def vendor_expected(root: Path, spec: Vendor) -> dict[str, bytes]:
    """Copy contents the sources call for: path under the destination -> bytes."""
    src = root / "src"
    out = {}
    for path in closure(src, spec.entries, spec.packages):
        out[path.relative_to(src).as_posix()] = path.read_bytes()
    for pattern in spec.include:
        for path in src.glob(pattern):
            if path.is_file() and "__pycache__" not in path.parts:
                out[path.relative_to(src).as_posix()] = path.read_bytes()
    return out


def vendor_actual(root: Path, spec: Vendor) -> dict[str, bytes]:
    """Copy contents on disk, ignoring bytecode caches."""
    folder = root / spec.dest
    if not folder.is_dir():
        return {}
    return {
        p.relative_to(folder).as_posix(): p.read_bytes()
        for p in folder.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }


def build_vendor(root: Path, spec: Vendor) -> None:
    """Write the copy, removing files that are no longer part of it."""
    folder = root / spec.dest
    want = vendor_expected(root, spec)
    for name in set(vendor_actual(root, spec)) - set(want):
        (folder / name).unlink()
    for name, data in want.items():
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_bytes() != data:
            target.write_bytes(data)


def vendor_drift(root: Path, spec: Vendor) -> list[str]:
    """Names of copied files that are missing, extra or different."""
    want, have = vendor_expected(root, spec), vendor_actual(root, spec)
    return sorted(n for n in want.keys() | have.keys() if want.get(n) != have.get(n))


def main(argv: list[str] | None = None) -> int:
    """Build or check the bundle; `--check` exits 1 naming the files that are off."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report drift, write nothing")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--vendor", help="build or check one copy named in the vendor file")
    parser.add_argument("--vendors", type=Path, help="the vendor file (default: the Harbor one)")
    args = parser.parse_args(argv)
    if args.vendor:
        specs = load_vendors(args.vendors or args.root / VENDORS)
        if args.vendor not in specs:
            raise SystemExit(f"no copy named {args.vendor!r} in the vendor file")
        spec = specs[args.vendor]
        if args.check:
            names = vendor_drift(args.root, spec)
            for name in names:
                print(f"out of date: {spec.dest}/{name}", file=sys.stderr)
            return 1 if names else 0
        build_vendor(args.root, spec)
        return 0
    if args.check:
        names = drift(args.root)
        for name in names:
            print(f"out of date: {BUNDLE / name}", file=sys.stderr)
        return 1 if names else 0
    build(args.root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
