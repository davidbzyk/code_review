"""Read side of the on-disk store: logical files plus an embedded LanceDB table."""

from __future__ import annotations

import atexit
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import lancedb

SCHEMA_VERSION = 1
CHUNKS = "chunks.jsonl"
VECTORS = "vectors.f32"
RELATED = "related.json"
CHANGED = "changed.json"
SETTINGS = "settings.json"
MANIFEST = "manifest.json"
# The JSON files of a store can be written by an agent: bigger ones are refused unread.
MAX_JSON_BYTES = 50_000_000
DB_DIR = "db"
TABLE = "chunks"
# The logical content of a store; its hash is store_sha256. The db folder is derived from it.
DATA_FILES = (CHUNKS, VECTORS, RELATED, CHANGED, SETTINGS)
# Where the database may put scratch files. Whoever starts the engine names the folder here;
# a search command run for an agent gets one inside the folder that agent may write.
SCRATCH_ENV = "CONTEXT_ENGINE_SCRATCH"
DEFAULT_SCRATCH = Path.home() / ".cache" / "code-review-engine" / "scratch"


# One folder per scratch root for the life of this process, so parallel calls never share one.
_own_scratch: dict[Path, Path] = {}


def _scratch_for(root: Path) -> Path:
    """This process's own folder under the scratch root, removed when the process exits."""
    if root.is_symlink():
        raise ValueError(f"the scratch folder {root} is a symbolic link")
    if root not in _own_scratch:
        root.mkdir(parents=True, exist_ok=True)
        own = Path(tempfile.mkdtemp(prefix="call-", dir=root))
        atexit.register(shutil.rmtree, own, ignore_errors=True)
        _own_scratch[root] = own
    return _own_scratch[root]


def connect(db_folder: str | Path, scratch: str | Path | None = None) -> Any:
    """Connect to the database folder with its scratch folder set first.

    Lance creates a spill folder under TMPDIR the moment it connects, even to read. The ambient
    temp folder is not ours to write and an agent sandbox denies it, so the root is named here:
    the argument, else SCRATCH_ENV, else DEFAULT_SCRATCH. A link is refused. Each process works
    in its own folder under that root and removes it on exit.
    """
    root = Path(scratch or os.environ.get(SCRATCH_ENV) or DEFAULT_SCRATCH)
    os.environ["TMPDIR"] = str(_scratch_for(root))
    return lancedb.connect(str(db_folder))


@dataclass
class Store:
    """A loaded store: manifest, per-file change records, stored queries and the chunk table."""

    manifest: dict[str, Any]
    related: dict[str, Any]
    related_skipped: dict[str, str]
    changed: dict[str, Any]
    table: Any


def _read_json(path: Path) -> Any:
    """Parse a JSON file after checking its size, so a huge file is never read."""
    if path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError(f"{path.name} is larger than {MAX_JSON_BYTES} bytes")
    return json.loads(path.read_text(encoding="utf-8"))


def load_store(folder: str | Path) -> Store:
    """Open a store folder: read the small JSON files and open the database table."""
    root = Path(folder)
    manifest = _read_json(root / MANIFEST)
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported store schema {manifest.get('schema_version')!r}")
    related = _read_json(root / RELATED)
    table = connect(root / DB_DIR).open_table(TABLE)
    if table.count_rows() != manifest["counts"]["chunks"]:
        raise ValueError(
            f"the table holds {table.count_rows()} rows but the manifest lists "
            f"{manifest['counts']['chunks']} chunks"
        )
    return Store(
        manifest=manifest,
        related=related["queries"],
        related_skipped=related.get("skipped", {}),
        changed=_read_json(root / CHANGED)["files"],
        table=table,
    )
