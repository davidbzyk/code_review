"""The aggregator reads files an agent wrote, so it must not be steered or crashed by them."""

import json

from review_core.aggregator import gates
from review_core.aggregator.cli import main
from review_core.aggregator.dedup import group_by_place

from .conftest import make_finding as f
from .conftest import make_repo, write_reviewer

META = [
    "--model", "m", "--effort", "high", "--runner", "r", "--cli-version", "1.0",
    "--sandbox-mode", "ro",
]  # fmt: skip
TEXT = "".join("same\n" if n in (5, 40) else f"line {n}\n" for n in range(1, 61))


def run_both(tmp_path, by_reviewer, verdict_for):
    """Run first-pass, write verdicts chosen by verdict_for(candidates), run finalize."""
    repo = make_repo(tmp_path, {"a.py": TEXT}, {"a.py": TEXT})
    out = tmp_path / "out"
    out.mkdir()
    for reviewer, findings in by_reviewer.items():
        write_reviewer(out, reviewer, findings)
    args = ["--out", str(out), "--repo", str(repo), "--base", "base", "--head", "head"]
    assert main(["first-pass", *args]) == 0
    candidates = json.loads((out / "candidates.json").read_text())["findings"]
    for item in candidates:
        lines = f"{item['line_start']}-{item['line_end']}"
        item["id"] = f"{item['fingerprint']}:{lines}:{item['reviewer']}"
    (out / "validation.json").write_text(json.dumps({"verdicts": verdict_for(candidates)}))
    code = main(["finalize", "--out", str(out), *META])
    return out, code


def declined(key):
    """One declining verdict row."""
    return {"id": key, "verdict": "declined", "reason": "no"}


def test_a_verdict_on_a_finding_the_validator_was_never_given_is_ignored(tmp_path):
    weak = f("security", line_start=10, line_end=10, quote="line 10", severity="P2")
    strong = f("tests", line_start=20, line_end=20, quote="line 20", severity="P1")
    out, code = run_both(
        tmp_path,
        {"security": [weak], "tests": [strong]},
        lambda c: [declined(x["id"]) for x in c if x["severity"] == "P2"],
    )
    run = json.loads((out / "findings.json").read_text())
    assert code == 0
    assert sorted(x["quote"] for x in run["findings"]) == ["line 10", "line 20"]
    assert run["envelope"]["dropped"]["validator_declined"] == 0


def test_two_findings_with_one_fingerprint_are_declined_separately(tmp_path):
    first = f("security", line_start=5, line_end=5, quote="same", severity="P1")
    second = f("security", line_start=40, line_end=40, quote="same", severity="P1")
    assert_same = []

    def decline_the_second(candidates):
        assert_same.append(len({x["fingerprint"] for x in candidates}))
        return [declined(candidates[1]["id"])]

    out, _ = run_both(tmp_path, {"security": [first, second]}, decline_the_second)
    run = json.loads((out / "findings.json").read_text())
    assert assert_same == [1]
    assert [x["line_start"] for x in run["findings"]] == [5]
    assert run["envelope"]["dropped"]["validator_declined"] == 1


def test_candidates_file_with_a_broken_finding_is_an_error_not_a_crash(tmp_path, capsys):
    out = tmp_path / "out"
    out.mkdir()
    counts = dict.fromkeys(
        ("quote_gate", "confidence_floor", "duplicate", "validator_declined", "out_of_snapshot"), 0
    )
    for broken in (5, {"severity": "P1"}, {**f(), "severity": 7}):
        (out / "candidates.json").write_text(json.dumps({"findings": [broken], "dropped": counts}))
        assert main(["finalize", "--out", str(out), *META]) == 1
    assert "error:" in capsys.readouterr().err


def test_validation_file_that_is_a_link_counts_as_a_validator_failure(tmp_path):
    from review_core.aggregator.validate import read_verdicts

    real = tmp_path / "elsewhere.json"
    real.write_text(json.dumps({"verdicts": []}))
    link = tmp_path / "validation.json"
    link.symlink_to(real)
    assert read_verdicts(real) == {}
    assert read_verdicts(link) is None


def test_a_finding_claiming_a_huge_range_does_not_swallow_its_neighbours():
    wide = f("security", line_start=1, line_end=500, severity="P3")
    inside = f("tests", line_start=200, line_end=200, severity="P1")
    later = f("correctness", line_start=400, line_end=401, severity="P2")
    kept = group_by_place([wide, inside, later], window=3)
    assert sorted(k["reviewer"] for k in kept) == ["correctness", "security", "tests"]
    assert all(k["also_raised_by"] == [] for k in kept)


def test_git_reads_ignore_a_git_dir_set_by_the_caller(tmp_path, monkeypatch):
    (tmp_path / "one").mkdir()
    (tmp_path / "two").mkdir()
    target = make_repo(tmp_path / "one", {"a.py": "base\n"}, {"a.py": "target\n"})
    other = make_repo(tmp_path / "two", {"a.py": "base\n"}, {"a.py": "other\n"})
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    assert gates.GitReader(target, "base", "head").read("new", "a.py") == "target\n"


def test_a_verdict_whose_id_fits_two_candidates_declines_neither():
    # Findings over the span limit are never merged, so two can share lines and a fingerprint.
    from review_core.aggregator.validate import apply_verdicts, verdict_id

    # The id carries the reviewer, so only one reviewer's two findings can share one.
    twin = {"fingerprint": "a" * 64, "line_start": 1, "line_end": 90, "severity": "P1",
            "reviewer": "security"}  # fmt: skip
    a, b = {**twin, "title": "one"}, {**twin, "title": "two"}
    alone = {**twin, "reviewer": "language", "line_start": 200, "line_end": 201}
    rows = {verdict_id(x): {"id": verdict_id(x), "verdict": "declined", "reason": "no"}
            for x in (a, alone)}  # fmt: skip
    kept, declined = apply_verdicts([a, b, alone], rows)
    assert [k["title"] for k in kept] == ["one", "two"]
    assert [d["reviewer"] for d in declined] == ["language"]


# --- a finding's lines come from its quote, not from what the reviewer claims ---------------


def test_claimed_lines_are_replaced_by_where_the_quote_is(tmp_path):
    repo = make_repo(tmp_path, {"a.py": TEXT}, {"a.py": TEXT})
    reader = gates.GitReader(repo, "base", "head")
    lied = f("security", line_start=5, line_end=9, quote="line 20")
    twice_near_40 = f("tests", line_start=38, line_end=38, quote="same")
    twice_near_5 = f("tests", line_start=1, line_end=1, quote="  same  ")
    kept, dropped = gates.apply_path_and_quote_gates([lied, twice_near_40, twice_near_5], reader)
    assert dropped == []
    assert [(k["line_start"], k["line_end"]) for k in kept] == [(20, 20), (40, 40), (5, 5)]


def test_a_finding_cannot_absorb_another_by_claiming_its_lines(tmp_path):
    from review_core.aggregator.pipeline import gate_and_merge

    repo = make_repo(tmp_path, {"a.py": TEXT}, {"a.py": TEXT})
    real = f("tests", line_start=20, line_end=20, quote="line 20", severity="P2")
    squatter = f("security", line_start=20, line_end=20, quote="line 50", severity="P0")
    merged, dropped, _ = gate_and_merge(
        ([real, squatter], []), gates.GitReader(repo, "base", "head")
    )
    assert sorted((m["reviewer"], m["line_start"]) for m in merged) == [
        ("security", 50),
        ("tests", 20),
    ]
    assert dropped["duplicate"] == 0


def test_rebuild_gives_the_same_document_as_the_two_commands_and_writes_nothing(tmp_path):
    from review_core.aggregator.pipeline import rebuild

    by_reviewer = {
        "security": [f("security", line_start=10, line_end=10, quote="line 10", severity="P1")],
        "tests": [f("tests", line_start=11, line_end=11, quote="line 11", severity="P2")],
        "language": [f("language", line_start=30, line_end=30, quote="line 30", confidence=25)],
    }
    out, code = run_both(
        tmp_path, by_reviewer, lambda c: [{"id": c[0]["id"], "verdict": "upheld", "reason": "ok"}]
    )
    assert code == 0
    written = json.loads((out / "findings.json").read_text())
    before = sorted(p.name for p in out.iterdir())
    meta = dict.fromkeys(("runner", "model", "effort", "cli_version", "sandbox_mode"), "x")
    meta.update(model="m", effort="high", runner="r", cli_version="1.0", sandbox_mode="ro")
    reader = gates.GitReader(tmp_path / "repo", "base", "head")
    run, loose = rebuild(out, reader, meta)
    assert run == written and loose == 0
    assert sorted(p.name for p in out.iterdir()) == before
    # The same from two exported trees, with no repository in reach.
    trees = {side: tmp_path / "trees" / side for side in ("base", "head")}
    for side, dest in trees.items():
        gates.export_blobs(tmp_path / "repo", gates.resolve_commit(tmp_path / "repo", side), dest)
    assert rebuild(out, gates.BlobReader(trees["head"], trees["base"]), meta)[0] == written
    # Without evidence that a validator ran, the verdict file counts for nothing.
    run, loose = rebuild(out, reader, meta, validator_ran=False)
    assert loose == 1 and len(run["findings"]) == len(written["findings"])


def test_a_ref_is_resolved_to_a_commit_id_once(tmp_path):
    repo = make_repo(tmp_path, {"a.py": "1\n"}, {"a.py": "2\n"})
    commit = gates.resolve_commit(repo, "head")
    assert len(commit) == 40 and gates.resolve_commit(repo, commit) == commit
    assert (
        gates.resolve_commit(repo, "nope") is None and gates.resolve_commit(repo, "--all") is None
    )


def test_export_writes_every_file_whatever_the_tree_says_about_exporting(tmp_path):
    import subprocess

    files = {"a.py": "kept\n", ".gitattributes": "a.py export-ignore\n", "d/b c.py": "deep\n"}
    repo = tmp_path / "repo"
    (repo / "d").mkdir(parents=True)
    for name, text in files.items():
        (repo / name).write_text(text)
    (repo / "link").symlink_to("/etc/hosts")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(repo)]
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "x"]):
        subprocess.run([*git, *args], check=True, capture_output=True)
    dest = tmp_path / "out"
    skipped = gates.export_commit(repo, gates.resolve_commit(repo, "HEAD"), dest)
    assert {p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file()} == set(files)
    assert skipped == ["link"] and not (dest / "link").exists()
    from review_core.contracts.models import TreeReader

    reader = TreeReader(dest, dest)
    assert reader.read("new", "a.py") == "kept\n" and reader.read("old", "d/b c.py") == "deep\n"
    assert reader.read("new", "../repo/a.py") is None and reader.read("new", "nope") is None


def test_agent_side_reads_ignore_replacement_objects(tmp_path):
    import subprocess

    repo = make_repo(tmp_path, {"a.py": "base\n"}, {"a.py": "real\n"})
    head = gates.resolve_commit(repo, "head")
    (repo / "a.py").write_text("planted\n")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(repo)]
    subprocess.run([*git, "commit", "-qam", "p"], check=True, capture_output=True)
    subprocess.run([*git, "replace", head, "HEAD"], check=True, capture_output=True)
    assert gates.GitReader(repo, "base", head).read("new", "a.py") == "real\n"


def _commit_with_paths(tmp_path, entries: dict[str, str]):
    """A commit whose tree holds exactly these paths, built without touching the filesystem."""
    import subprocess

    repo = tmp_path / "crafted"
    repo.mkdir()
    # precomposeunicode off: on a Mac git would otherwise recompose the names we pass in.
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.precomposeunicode=false"]
    git += ["-C", str(repo)]
    subprocess.run([*git, "init", "-q"], check=True, capture_output=True)
    for path, text in entries.items():
        blob = subprocess.run(
            [*git, "hash-object", "-w", "--stdin"], input=text.encode(), check=True,
            capture_output=True,
        ).stdout.decode().strip()  # fmt: skip
        cache = f"100644,{blob},{path}"
        subprocess.run([*git, "update-index", "--add", "--cacheinfo", cache], check=True)
    tree = subprocess.run([*git, "write-tree"], check=True, capture_output=True).stdout.decode()
    done = subprocess.run(
        [*git, "commit-tree", tree.strip(), "-m", "x"], check=True, capture_output=True
    )
    return repo, done.stdout.decode().strip()


def test_two_paths_that_differ_only_by_case_are_both_readable_and_never_overwrite(tmp_path):
    # On a case-insensitive disk these two land on one file name; a directory export loses one.
    repo, commit = _commit_with_paths(
        tmp_path, {"Config.rs": "upper\n", "config.rs": "lower\n", "d/odd\\name.py": "odd\n"}
    )
    gates.export_blobs(repo, commit, tmp_path / "blobs")
    reader = gates.BlobReader(tmp_path / "blobs", tmp_path / "blobs")
    assert reader.read("new", "Config.rs") == "upper\n"
    assert reader.read("old", "config.rs") == "lower\n"
    assert reader.read("new", "CONFIG.RS") is None and reader.read("new", "../x") is None
    assert reader.read("new", "d/odd\\name.py") == "odd\n"


def test_a_directory_export_refuses_paths_that_would_collide(tmp_path):
    import pytest

    repo, commit = _commit_with_paths(tmp_path, {"Config.rs": "upper\n", "config.rs": "lower\n"})
    with pytest.raises(ValueError, match="collide"):
        gates.export_commit(repo, commit, tmp_path / "tree")


def test_a_path_cited_in_another_unicode_form_still_finds_its_file(tmp_path):
    # The tree spells the name with a combining accent; a model will usually write it composed.
    decomposed, composed = "src/café.py", "src/café.py"
    repo, commit = _commit_with_paths(tmp_path, {decomposed: "x = 1\n", "src/Other.py": "y = 2\n"})
    gates.export_blobs(repo, commit, tmp_path / "blobs")
    for reader in (
        gates.GitReader(repo, commit, commit),
        gates.BlobReader(tmp_path / "blobs", tmp_path / "blobs"),
    ):
        assert reader.find("new", composed) == decomposed
        assert reader.read("new", composed) == "x = 1\n"
        assert reader.find("new", "src/other.py") is None  # letter case is not forgiven
        kept, dropped = gates.apply_path_and_quote_gates(
            [f(file=composed, quote="x = 1", line_start=1, line_end=1)], reader
        )
        assert dropped == [] and kept[0]["file"] == decomposed


def test_two_paths_with_one_unicode_form_are_only_found_by_their_exact_spelling(tmp_path):
    decomposed, composed = "café.py", "café.py"
    repo, commit = _commit_with_paths(tmp_path, {decomposed: "a\n", composed: "b\n"})
    reader = gates.GitReader(repo, commit, commit)
    assert reader.read("new", decomposed) == "a\n" and reader.read("new", composed) == "b\n"
