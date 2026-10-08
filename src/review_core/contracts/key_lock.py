"""Load an answer key only when it matches its lock. Standard library only.

This is the one place that checks a frozen key against its lock, so a grader can vendor it
without the snapshot tools that `key_tools` pulls in.
"""

from __future__ import annotations

from pathlib import Path

from review_core.contracts.models import ContractError, Key, key_hash, load_key, read_json


def load_frozen(key_path: Path | str, lock_path: Path | str) -> Key:
    """Load the key, failing unless its lock exists, is well formed and matches the key's hash."""
    key = load_key(read_json(key_path))
    if not Path(lock_path).is_file():
        raise ContractError(f"{lock_path}: lock file is missing")
    lock = read_json(lock_path)
    stored = lock.get("sha256") if isinstance(lock, dict) else None
    if not isinstance(stored, str):
        raise ContractError(f"{lock_path}: lock has no sha256")
    if stored != key_hash(key):
        raise ContractError(f"{key_path}: key does not match its lock; it changed after freezing")
    return key
