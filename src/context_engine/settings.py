"""Load the engine settings (build side: reads settings.toml with tomllib)."""

from __future__ import annotations

import copy
import tomllib
from pathlib import Path
from typing import Any

SETTINGS_PATH = Path(__file__).with_name("settings.toml")


def _merge(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    """Recursively overlay `extra` on `base`, returning a new dict."""
    out = copy.deepcopy(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def load_settings(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Read settings.toml and overlay `overrides` (a nested dict, used by tests and flags)."""
    settings = tomllib.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    return _merge(settings, overrides or {})
