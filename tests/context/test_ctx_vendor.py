"""The vendored OKF tool: its record matches the files, and the sync command reproduces it."""

from __future__ import annotations

import json
import shutil

from review_core.context.sync_okf_tool import VENDOR_DIR, main, needed_files, read_record, sync
from review_core.hashing import file_sha256


def test_vendored_record_matches_the_files_on_disk():
    record = read_record()
    assert sorted(record["files"]) == needed_files(VENDOR_DIR)
    for name, digest in record["files"].items():
        assert file_sha256(VENDOR_DIR / name) == digest
    on_disk = {p.name for p in VENDOR_DIR.glob("*.py")}
    assert on_disk == set(record["files"]) and record["source"]


def plugin_copy(tmp_path):
    """A temporary plugin folder: the vendored scripts plus a script nothing imports."""
    scripts = tmp_path / "okf-plugin" / "scripts"
    scripts.mkdir(parents=True)
    for name in read_record()["files"]:
        shutil.copyfile(VENDOR_DIR / name, scripts / name)
    (scripts / "okf_verify.py").write_text("print('not vendored')\n")
    return tmp_path / "okf-plugin"


def test_sync_on_a_copy_of_the_tool_reproduces_the_same_hashes(tmp_path):
    dest = tmp_path / "dest"
    record = sync(plugin_copy(tmp_path), dest)
    assert record["files"] == read_record()["files"]
    assert record["tool_sha256"] == read_record()["tool_sha256"]
    assert record["source"] == "okf-plugin"
    assert json.loads((dest / "VENDORED.json").read_text()) == record
    assert not (dest / "okf_verify.py").exists()


def test_sync_replaces_changed_files_and_the_command_reports_bad_input(tmp_path, capsys):
    plugin = plugin_copy(tmp_path)
    dest = tmp_path / "dest"
    first = sync(plugin, dest)
    (plugin / "scripts" / "okf_retrieve.py").write_text(
        (plugin / "scripts" / "okf_retrieve.py").read_text() + "\n# a change\n"
    )
    assert main([str(plugin), "--dest", str(dest)]) == 0
    assert read_record(dest)["files"]["okf_retrieve.py"] != first["files"]["okf_retrieve.py"]
    assert main([str(tmp_path / "nowhere"), "--dest", str(dest)]) == 2
    assert capsys.readouterr().err.startswith("sync_okf_tool:")
