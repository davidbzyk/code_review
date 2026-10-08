"""build_stores: the same inputs give the same hash, symlinks are never copied, none is empty."""

from __future__ import annotations

import json
import os
import shutil

from ctx_helpers import BASE_TREE, HEAD_TREE, OKF_BUNDLE, write_tree

from review_core.context import build_stores
from review_core.context.sync_okf_tool import read_record


def build_vector(tmp_path, name):
    root = tmp_path / name
    write_tree(root / "snaps" / "toy" / "base", BASE_TREE)
    write_tree(root / "snaps" / "toy" / "head", HEAD_TREE)
    code = build_stores.main(
        [
            "--case",
            "toy",
            "--arm",
            "vector",
            "--fake-embedder",
            "--snapshots-dir",
            str(root / "snaps"),
            "--out",
            str(root / "out"),
            "--cache-dir",
            str(root / "cache"),
        ]
    )
    assert code == 0
    return json.loads((root / "out" / "toy" / "vector" / "manifest.json").read_text())


def build_okf(tmp_path, name, bundle=OKF_BUNDLE):
    root = tmp_path / name
    code = build_stores.main(
        [
            "--case",
            "toy",
            "--arm",
            "okf",
            "--okf-bundle",
            str(bundle),
            "--out",
            str(root),
            "--cache-dir",
            str(root / "c"),
        ]
    )
    assert code == 0
    return root / "toy" / "okf"


def test_the_vector_arm_builds_twice_to_the_same_hash(tmp_path):
    a, b = build_vector(tmp_path, "a"), build_vector(tmp_path, "b")
    assert a["store_sha256"] == b["store_sha256"] and a["provider"] == "vector"


def test_the_okf_arm_builds_twice_to_the_same_hash(tmp_path):
    a, b = build_okf(tmp_path, "a"), build_okf(tmp_path, "b")
    ma = json.loads((a / "manifest.json").read_text())
    mb = json.loads((b / "manifest.json").read_text())
    assert ma["store_sha256"] == mb["store_sha256"] and len(ma["store_sha256"]) == 64
    assert ma["tool_sha256"] == mb["tool_sha256"]
    assert ma["provider"] == "okf" and ma["notes"] == 5
    assert (a / "graph.json").read_bytes() == (b / "graph.json").read_bytes()
    assert sorted(p.name for p in a.iterdir()) == ["bundle", "graph.json", "manifest.json"]
    assert not list(a.rglob("*.py"))
    assert ma["tool_sha256"] == read_record()["tool_sha256"]
    assert not list(a.rglob("__pycache__"))


def test_rebuilding_into_the_same_folder_is_the_same_store(tmp_path):
    first = build_okf(tmp_path, "a")
    h1 = json.loads((first / "manifest.json").read_text())["store_sha256"]
    again = build_okf(tmp_path, "a")
    assert json.loads((again / "manifest.json").read_text())["store_sha256"] == h1


def test_a_changed_bundle_changes_the_hash(tmp_path):
    other = tmp_path / "bundle"
    shutil.copytree(OKF_BUNDLE, other)
    note = other / "runtime" / "audit-trail.md"
    note.write_text(note.read_text() + "\nOne more line.\n")
    a, b = build_okf(tmp_path, "a"), build_okf(tmp_path, "b", other)
    ha = json.loads((a / "manifest.json").read_text())["store_sha256"]
    hb = json.loads((b / "manifest.json").read_text())["store_sha256"]
    assert ha != hb


def test_symbolic_links_in_a_bundle_are_never_copied(tmp_path):
    bundle = tmp_path / "bundle"
    shutil.copytree(OKF_BUNDLE, bundle)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.md").write_text("# secret\n")
    os.symlink(outside / "secret.md", bundle / "leak.md")
    os.symlink(outside, bundle / "leakdir")
    root = tmp_path / "out"
    code = build_stores.main(
        [
            "--case",
            "toy",
            "--arm",
            "okf",
            "--okf-bundle",
            str(bundle),
            "--out",
            str(root),
            "--cache-dir",
            str(root / "c"),
        ]
    )
    assert code == 0
    store = root / "toy" / "okf"
    assert (
        not (store / "bundle" / "leak.md").exists() and not (store / "bundle" / "leakdir").exists()
    )
    assert not any(p.is_symlink() for p in store.rglob("*"))


def test_arm_none_writes_nothing(tmp_path, capsys):
    out = tmp_path / "out"
    code = build_stores.main(
        ["--case", "toy", "--arm", "none", "--out", str(out), "--cache-dir", str(tmp_path / "c")]
    )
    assert code == 0 and not out.exists() and not (tmp_path / "c").exists()
    assert "no store" in capsys.readouterr().out


def test_bad_inputs_are_one_line_errors(tmp_path, capsys):
    code = build_stores.main(
        [
            "--case",
            "../x",
            "--arm",
            "okf",
            "--out",
            str(tmp_path / "o"),
            "--cache-dir",
            str(tmp_path / "c"),
        ]
    )
    assert code == 2
    code = build_stores.main(
        [
            "--case",
            "toy",
            "--arm",
            "okf",
            "--out",
            str(tmp_path / "o"),
            "--cache-dir",
            str(tmp_path / "c"),
        ]
    )
    assert code == 2  # no --okf-bundle
    err = capsys.readouterr().err
    assert all(len(line) < 300 for line in err.splitlines()) and not (tmp_path / "o").exists()


def test_a_bundle_holding_code_or_other_non_data_files_is_refused(tmp_path, capsys):
    bundle = tmp_path / "bundle"
    shutil.copytree(OKF_BUNDLE, bundle)
    (bundle / "helper.py").write_text("raise SystemExit\n")
    root = tmp_path / "out"
    code = build_stores.main(
        [
            "--case",
            "toy",
            "--arm",
            "okf",
            "--okf-bundle",
            str(bundle),
            "--out",
            str(root),
            "--cache-dir",
            str(root / "c"),
        ]
    )
    assert code == 2 and not root.exists()
    assert "not data" in capsys.readouterr().err
