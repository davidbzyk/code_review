"""Packaging checks: manifest, skill names, the orchestrator skill's text and the bundled script.

The orchestrator skill is a prompt, so these tests hold what can be checked mechanically: it names
every reviewer the code names, the commands it shows parse with the aggregator's own parser, and
the bundle inside the skill folder is exactly the aggregator and what it imports.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

from review_core.aggregator import cli
from review_core.aggregator.validate import VALIDATOR
from review_core.contracts.models import REVIEWERS
from review_core.envelope import reviewer_file
from tests.aggregator.conftest import make_finding, make_repo, write_reviewer

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "src" / "plugin" / "skills"
ORCH = SKILLS / "review-orchestrator"
SCRIPTS = ORCH / "scripts"
MANIFEST = ROOT / "src" / "plugin" / ".codex-plugin" / "plugin.json"
BUILD = ROOT / "scripts" / "build_plugin.py"
THERMOS = ROOT / "lane-inputs" / "u4" / "third_party" / "thermos"
SKILL_TEXT = (ORCH / "SKILL.md").read_text(encoding="utf-8")


def _load_build():
    """Import scripts/build_plugin.py as a module."""
    spec = importlib.util.spec_from_file_location("build_plugin", BUILD)
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_plugin"] = module
    spec.loader.exec_module(module)
    return module


def _skill_names() -> dict[str, str]:
    """Map each skill folder under src/plugin/skills to its frontmatter name."""
    names = {}
    for folder in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        text = (folder / "SKILL.md").read_text(encoding="utf-8")
        front = re.match(r"---\n(.*?)\n---\n", text, re.S)
        assert front, f"{folder.name} has no frontmatter"
        match = re.search(r"^name:\s*(\S+)\s*$", front.group(1), re.M)
        assert match, f"{folder.name} has no name"
        names[folder.name] = match.group(1)
    return names


def _commands() -> list[list[str]]:
    """Argument lists of the `python3 .../aggregate.py` lines shown in the skill, filled in."""
    fill = {
        "<skill-dir>": "SKILLDIR",
        "<out>": "OUT",
        "<base>": "BASE",
        "<head>": "HEAD",
    }
    found = []
    for line in SKILL_TEXT.splitlines():
        line = line.strip()
        if line.startswith("python3 "):
            for key, value in fill.items():
                line = line.replace(key, value)
            parts = shlex.split(line)
            assert parts[1] == "SKILLDIR/scripts/aggregate.py"
            found.append(parts[2:])
    return found


def test_manifest_is_valid_and_skill_names_are_unique():
    """The manifest has name, version, description and points at the skills folder."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for key in ("name", "version", "description"):
        assert isinstance(manifest[key], str) and manifest[key]
    assert manifest["skills"] == "./skills/"
    names = list(_skill_names().values())
    assert len(names) == len(set(names)) == 9


def test_orchestrator_mentions_exactly_the_other_skills():
    """Every review-* name in the skill exists, and all eight other skills are mentioned."""
    mentioned = set(re.findall(r"\breview-[a-z][a-z-]*", SKILL_TEXT))
    package = set(_skill_names().values())
    assert "review-orchestrator" in package
    assert mentioned <= package
    assert package - {"review-orchestrator"} <= mentioned


def test_orchestrator_asks_for_sub_agents_and_names_every_agent():
    """The skill asks for sub-agents outright and names the reviewers and the validator."""
    assert "explicit request for sub-agents and parallel agent work" in SKILL_TEXT
    for reviewer in REVIEWERS:
        assert f"`{reviewer}`" in SKILL_TEXT
    assert len(REVIEWERS) == 7
    assert f"`{VALIDATOR}`" in SKILL_TEXT


def test_reviewer_file_pattern_matches_the_envelope():
    """The file name the skill tells reviewers to write is the one the aggregator reads."""
    assert "<out>/findings.<reviewer>.json" in SKILL_TEXT
    for reviewer in REVIEWERS:
        stated = "<out>/findings.<reviewer>.json".replace("<out>", "OUT").replace(
            "<reviewer>", reviewer
        )
        assert Path(stated) == reviewer_file("OUT", reviewer)


def test_commands_in_the_skill_parse_with_the_aggregator_parser():
    """First pass, finalize and report, as written in the skill, are accepted by the real parser."""
    commands = _commands()
    assert [c[0] for c in commands] == ["first-pass", "finalize", "report"]
    parser = cli._parser()
    first = parser.parse_args(commands[0])
    assert (first.out, first.base, first.head) == ("OUT", "BASE", "HEAD")
    assert parser.parse_args(commands[1]).out == "OUT"
    shown = parser.parse_args(commands[2])
    assert (shown.command, shown.out) == ("report", "OUT")


def _step(title: str) -> str:
    """One step of the skill, from its heading to the next, with line breaks read as spaces."""
    start = SKILL_TEXT.index(f"## Step {title}")
    end = SKILL_TEXT.find("\n## ", start + 1)
    return " ".join(SKILL_TEXT[start : end if end != -1 else len(SKILL_TEXT)].split())


def test_summary_step_comes_after_finalize_and_before_the_report():
    """Reading the change is step 6, after step 5 wrote findings.json, and the report is last."""
    five = SKILL_TEXT.index("## Step 5: finalize")
    six = SKILL_TEXT.index("## Step 6: summarise the change")
    seven = SKILL_TEXT.index("## Step 7: report")
    assert five < six < seven
    assert "belongs to this step alone" in _step("6: summarise the change")
    assert "colour what the reviewers were told" in _step("6: summarise the change")
    for earlier in range(1, 6):
        assert "git diff" not in _step(f"{earlier}:")
    assert SKILL_TEXT.count("git diff") == 1


def test_summary_describes_and_does_not_judge_and_is_the_only_file_written():
    """The summary has no opinion in it, and the agent still never writes a findings file."""
    summary = _step("6: summarise the change")
    assert "describes and does not judge" in summary
    assert "<out>/pr-summary.md" in summary
    assert "nothing about what the reviewers found" in summary
    assert "the only file you write, and not a findings file" in summary
    flat = " ".join(SKILL_TEXT.split())
    assert "you do not write or edit any findings file" in flat


def test_report_step_replies_with_the_printed_text_and_has_a_fallback():
    """Step 7 runs the command and passes its output on; a failure falls back to one line."""
    report = _step("7: report")
    assert "aggregate.py report --out <out>" in report
    assert "Reply with exactly what it printed" in report
    failing = SKILL_TEXT[SKILL_TEXT.index("## When a step fails") :]
    assert "If `report` does" in failing
    assert "how many of the seven reviewers finished" in failing
    assert "`report.md`" in failing


def test_skill_has_no_emoji_and_copies_no_line_from_thermos():
    """No emoji anywhere, and no long line shared with the example orchestrator plugin."""
    for char in SKILL_TEXT:
        assert unicodedata.category(char) != "So" and ord(char) < 0x2000, repr(char)
    if not THERMOS.is_dir():
        pytest.skip("thermos source not present")
    theirs = set()
    for path in THERMOS.rglob("*.md"):
        theirs |= {ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()}
    ours = {ln.strip() for ln in SKILL_TEXT.splitlines() if len(ln.strip()) >= 20}
    assert not ours & theirs


def test_build_check_passes_on_committed_bundle():
    """`--check` exits 0 on the committed bundle and writes nothing."""
    before = sorted(p.relative_to(ROOT) for p in SCRIPTS.rglob("*") if p.is_file())
    assert _load_build().main(["--check"]) == 0
    assert before == sorted(p.relative_to(ROOT) for p in SCRIPTS.rglob("*") if p.is_file())


def test_build_check_fails_after_a_bundled_file_changes(tmp_path, capsys):
    """In a copy of the tree, editing one bundled file makes `--check` fail and name it."""
    copy = tmp_path / "tree"
    shutil.copytree(ROOT / "src" / "review_core", copy / "src" / "review_core",
                    ignore=shutil.ignore_patterns("__pycache__"))  # fmt: skip
    shutil.copytree(SCRIPTS, copy / "src" / "plugin" / "skills" / "review-orchestrator" / "scripts",
                    ignore=shutil.ignore_patterns("__pycache__"))  # fmt: skip
    build = _load_build()
    assert build.main(["--check", "--root", str(copy)]) == 0
    target = copy / "src/plugin/skills/review-orchestrator/scripts/review_core/envelope.py"
    target.write_text(target.read_text(encoding="utf-8") + "# edited\n", encoding="utf-8")
    capsys.readouterr()
    assert build.main(["--check", "--root", str(copy)]) == 1
    assert "review_core/envelope.py" in capsys.readouterr().err
    assert target.read_text(encoding="utf-8").endswith("# edited\n")  # check wrote nothing


def test_build_twice_gives_identical_bytes(tmp_path):
    """Two builds into a copy produce the same files with the same bytes."""
    copy = tmp_path / "tree"
    shutil.copytree(ROOT / "src" / "review_core", copy / "src" / "review_core",
                    ignore=shutil.ignore_patterns("__pycache__"))  # fmt: skip
    build = _load_build()
    assert build.main(["--root", str(copy)]) == 0
    out = copy / "src/plugin/skills/review-orchestrator/scripts"
    first = {p.relative_to(out): p.read_bytes() for p in out.rglob("*") if p.is_file()}
    assert build.main(["--root", str(copy)]) == 0
    second = {p.relative_to(out): p.read_bytes() for p in out.rglob("*") if p.is_file()}
    assert first == second
    committed = {p.relative_to(SCRIPTS): p.read_bytes() for p in SCRIPTS.rglob("*") if p.is_file()
                 and "__pycache__" not in p.parts}  # fmt: skip
    assert first == committed


def test_bundle_holds_only_the_import_closure():
    """No module outside what the aggregator imports is bundled."""
    bundled = {
        p.relative_to(SCRIPTS).as_posix()
        for p in SCRIPTS.rglob("*.py")
        if "__pycache__" not in p.parts
    }
    assert bundled == {
        "aggregate.py",
        "review_core/__init__.py",
        "review_core/envelope.py",
        "review_core/aggregator/__init__.py",
        "review_core/aggregator/cli.py",
        "review_core/aggregator/confidence.py",
        "review_core/aggregator/dedup.py",
        "review_core/aggregator/gates.py",
        "review_core/aggregator/pipeline.py",
        "review_core/aggregator/report.py",
        "review_core/aggregator/validate.py",
        "review_core/contracts/__init__.py",
        "review_core/contracts/models.py",
    }
    for banned in ("key_tools", "launcher", "scoring"):
        assert not any(banned in name for name in bundled)


# The agent runs the bundle with whatever `python3` its shell finds, not with this project's
# interpreter. On a Mac that is the system one, 3.9. The bundle must run on it.
OLDEST = (3, 9)


def _interpreters() -> list[str]:
    """This interpreter plus every other python3 on the machine that is at least OLDEST."""
    found = {os.path.realpath(sys.executable): sys.executable}
    names = ["/usr/bin/python3", *(f"python3.{minor}" for minor in range(OLDEST[1], 15))]
    for name in names:
        path = shutil.which(name)
        if not path or os.path.realpath(path) in found:
            continue
        probe = subprocess.run(
            [path, "-c", f"import sys; print(sys.version_info >= {OLDEST!r})"],
            capture_output=True, text=True, check=False,
        )  # fmt: skip
        if probe.stdout.strip() == "True":
            found[os.path.realpath(path)] = path
    return list(found.values())


@pytest.mark.parametrize("python", _interpreters())
def test_bundled_script_matches_the_module_byte_for_byte(tmp_path, python):
    """The bundled entry, run bare from another folder, writes the same files as the module."""
    base = {"a.py": "a\nb\nc\nd\ne\n", "b.py": "p = 1\n"}
    head = {"a.py": "a\nb\nc\nd\nx = 1\n", "b.py": "p = 2\nq = 3\n"}
    repo = make_repo(tmp_path, base, head)
    work = {"module": tmp_path / "out_module", "bundle": tmp_path / "out_bundle"}
    for out in work.values():
        out.mkdir()
        write_reviewer(out, "security", [make_finding("security", quote="x = 1")])
        write_reviewer(out, "correctness", [make_finding("correctness", quote="x = 1")])
        tests_finding = make_finding(
            "tests", file="b.py", line_start=2, line_end=2, quote="q = 3", severity="P3"
        )
        write_reviewer(out, "tests", [tests_finding])
        for other in ("architecture", "code_quality", "compliance", "language"):
            write_reviewer(out, other, [])
    shape = ["--repo", str(repo), "--base", "base", "--head", "head"]
    steps = (["first-pass", *shape], ["finalize"], ["report"])
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    env = {**os.environ, "PYTHONPATH": ""}
    for out in work.values():
        (out / "pr-summary.md").write_text("It adds a line. It touches caf\u00e9.py.\n", "utf-8")
    for step in steps:
        assert cli.main([step[0], "--out", str(work["module"]), *step[1:]]) == 0
        done = subprocess.run(
            [python, str(SCRIPTS / "aggregate.py"), step[0],
             "--out", str(work["bundle"]), *step[1:]],  # fmt: skip
            cwd=elsewhere, env=env, capture_output=True, encoding="utf-8",
        )  # fmt: skip
        assert done.returncode == 0, done.stderr
    names = ("candidates.json", "validator-input.json", "findings.json", "report.md")
    for name in names:
        assert (work["module"] / name).read_bytes() == (work["bundle"] / name).read_bytes()
    assert done.stdout == (work["bundle"] / "report.md").read_text(encoding="utf-8")
    assert "caf\u00e9.py" in done.stdout
    doc = json.loads((work["bundle"] / "findings.json").read_text(encoding="utf-8"))
    assert doc["findings"], "fixture should leave at least one finding"


def test_every_skill_folder_is_named_after_its_skill():
    # A host finds "the review-security skill" by folder; a reviewer told to use it looks there.
    names = _skill_names()
    assert {folder: name for folder, name in names.items() if folder != name} == {}


def test_orchestrator_lets_the_caller_name_the_python():
    text = (ORCH / "SKILL.md").read_text(encoding="utf-8")
    assert "If you were given the exact command for the script" in text
