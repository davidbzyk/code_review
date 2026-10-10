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


def test_a_licence_expression_asks_for_a_hatchling_that_writes_it():
    """`license = "MIT"` is a PEP 639 expression, which Hatchling writes fully from 1.27."""
    import re
    import tomllib
    from pathlib import Path

    project = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())
    assert isinstance(project["project"]["license"], str)
    (req,) = [r for r in project["build-system"]["requires"] if r.startswith("hatchling")]
    floor = tuple(int(n) for n in re.search(r">=\s*([\d.]+)", req).group(1).split("."))
    assert floor >= (1, 27)
