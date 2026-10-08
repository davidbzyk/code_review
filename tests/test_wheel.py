"""The built wheel carries the review skills where the installed command looks for them."""

import subprocess
import zipfile

import pytest


@pytest.mark.slow
def test_the_wheel_ships_the_skills_beside_the_package(tmp_path):
    subprocess.run(["uv", "build", "--wheel", "-o", str(tmp_path), "-q"], check=True)
    (wheel,) = tmp_path.glob("*.whl")
    names = set(zipfile.ZipFile(wheel).namelist())
    assert "review_core/cli.py" in names
    assert "review_core/launcher/runners.toml" in names
    assert "plugin/skills/review-orchestrator/SKILL.md" in names  # cli.DEFAULT_SKILLS
    assert not [n for n in names if "__pycache__" in n]
