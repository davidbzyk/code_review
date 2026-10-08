#!/usr/bin/env python3
"""Copy the smallest working review tool into TARGET/.code-review and add the CI workflow.

The modules are the import closure of the review command and the poster; the data files are those
lying beside a needed module (runners.toml, prompt.md, schemas, providers.toml, pipeline.toml).
The review skills go where the command looks for them. Nothing is kept by hand, so a new import
or data file is picked up on the next install. Standard library only.

    python3 action/bundle.py PATH-TO-REPO      # or: sh action/install.sh PATH-TO-REPO
"""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
ENTRIES = ("review_core.cli", "review_core.ci.github")
DEST = ".code-review"
WORKFLOW = Path(".github") / "workflows" / "code-review.yml"
SKIP_NAMES = {"__pycache__", ".DS_Store"}
SKIP_SUFFIXES = (".pyc", ".pyo")


def _closure() -> set[Path]:
    spec = importlib.util.spec_from_file_location(
        "build_plugin", ROOT / "scripts" / "build_plugin.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_plugin"] = module
    spec.loader.exec_module(module)
    return module.closure(SRC, ENTRIES)


def files() -> list[str]:
    """Paths relative to the repository root that a working install needs, sorted."""
    modules = _closure()
    found = {p.relative_to(ROOT).as_posix() for p in modules}
    for folder in {p.parent for p in modules}:
        for data in folder.iterdir():
            if data.is_file() and data.suffix != ".py" and data.name not in SKIP_NAMES:
                found.add(data.relative_to(ROOT).as_posix())
    skills = SRC / "plugin" / "skills"
    for path in skills.rglob("*"):
        rel = path.relative_to(ROOT)
        if (path.is_file() and not path.is_symlink() and not path.name.endswith(SKIP_SUFFIXES)
                and not SKIP_NAMES & set(rel.parts)):  # fmt: skip
            found.add(rel.as_posix())
    found |= {"action/action.yml", "action/run-review.sh", "action/ruff.toml"}
    return sorted(found)


def install(target: Path) -> Path:
    """Replace TARGET/.code-review with a fresh copy and write the workflow; returns the folder."""
    if not (target / ".git").exists():
        raise SystemExit(f"{target} is not the root of a git repository")
    dest = target / DEST
    shutil.rmtree(dest, ignore_errors=True)
    for rel in files():
        out = dest / (rel.removeprefix("action/") if rel.startswith("action/") else rel)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, out)
    workflow = target / WORKFLOW
    workflow.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "action" / "workflow.yml", workflow)
    return dest


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("target", type=Path, help="root of the repository to add the review to")
    args = p.parse_args(argv)
    dest = install(args.target.resolve())
    count = sum(1 for p in dest.rglob("*") if p.is_file())
    print(f"installed {count} files in {dest} and {args.target / WORKFLOW}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
