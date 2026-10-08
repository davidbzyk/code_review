"""load_frozen lives in contracts and imports nothing outside review_core.contracts."""

import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"

CODE = """
import sys
sys.modules["targets"] = None  # any import of the targets package now fails
from review_core.contracts.key_lock import load_frozen
print("ok")
"""


def test_load_frozen_imports_without_the_targets_package():
    done = subprocess.run(
        [sys.executable, "-c", CODE],
        env={"PYTHONPATH": str(SRC), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == "ok"
