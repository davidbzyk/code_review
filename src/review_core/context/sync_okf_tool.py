"""Refresh the vendored OKF tool from a plugin folder: `python -m ...sync_okf_tool <plugin-dir>`.

Copies the scripts `ctx` and `build_stores` run (and any sibling script they import) unchanged
into `okf_tool/` and rewrites `VENDORED.json` with the source folder name and file hashes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from hashlib import sha256
from pathlib import Path

from review_core.hashing import file_sha256

VENDOR_DIR = Path(__file__).with_name("okf_tool")
RECORD = "VENDORED.json"
ROOTS = ("okf_common", "okf_retrieve", "okf_graphify")
_IMPORT = re.compile(r"^\s*(?:from|import)\s+(okf_[a-z0-9_]+)", re.MULTILINE)


def needed_files(scripts: Path) -> list[str]:
    """The root scripts plus every okf_* sibling they import, by name, sorted."""
    found: set[str] = set()
    todo = list(ROOTS)
    while todo:
        name = todo.pop()
        if name in found:
            continue
        path = scripts / f"{name}.py"
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"{path} is not a plain file")
        found.add(name)
        todo.extend(_IMPORT.findall(path.read_text(encoding="utf-8")))
    return sorted(f"{n}.py" for n in found)


def tool_hash(files: dict[str, str]) -> str:
    """One hash of the vendored files: sha256 over sorted `name:sha256` lines."""
    return sha256("".join(f"{k}:{v}\n" for k, v in sorted(files.items())).encode()).hexdigest()


def read_record(vendor: Path = VENDOR_DIR) -> dict:
    """The parsed VENDORED.json of a vendored folder."""
    return json.loads((vendor / RECORD).read_text(encoding="utf-8"))


def sync(plugin_dir: Path, dest: Path = VENDOR_DIR) -> dict:
    """Copy the needed scripts from `plugin_dir/scripts` to `dest` and rewrite the record."""
    scripts = plugin_dir / "scripts"
    names = needed_files(scripts)
    dest.mkdir(parents=True, exist_ok=True)
    if (dest / RECORD).is_file():
        for old in read_record(dest)["files"]:
            if old not in names:
                (dest / old).unlink(missing_ok=True)
    for name in names:
        (dest / name).write_bytes((scripts / name).read_bytes())
    files = {name: file_sha256(dest / name) for name in names}
    record = {"source": plugin_dir.resolve().name, "files": files, "tool_sha256": tool_hash(files)}
    (dest / RECORD).write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", "utf-8")
    return record


def main(argv: list[str] | None = None) -> int:
    """Run the sync; prints the new record."""
    parser = argparse.ArgumentParser(prog="sync_okf_tool")
    parser.add_argument("plugin_dir", type=Path)
    parser.add_argument("--dest", type=Path, default=VENDOR_DIR)
    args = parser.parse_args(argv)
    try:
        record = sync(args.plugin_dir, args.dest)
    except (OSError, ValueError) as exc:
        print(f"sync_okf_tool: {' '.join(str(exc).split())}", file=sys.stderr)
        return 2
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
