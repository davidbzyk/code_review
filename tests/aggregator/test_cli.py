"""The two commands end to end, on a small git repository with seven reviewer files."""

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import review_core.aggregator
from review_core.aggregator.cli import main
from review_core.contracts.models import DROP_REASONS, REVIEWERS, load_run_envelope

from .conftest import make_finding as f
from .conftest import make_repo, write_reviewer

HEAD = "".join(f"line {n}\n" for n in range(1, 61))
BASE = HEAD.replace("line 30\n", "only in base\n")
META = [
    "--model", "m", "--effort", "high", "--runner", "r", "--cli-version", "1.0",
    "--sandbox-mode", "ro",
]  # fmt: skip


def first_pass(tmp_path, out, repo, *extra):
    """Run first-pass and return the exit code."""
    args = [
        "first-pass",
        "--out",
        str(out),
        "--repo",
        str(repo),
        "--base",
        "base",
        "--head",
        "head",
    ]
    return main([*args, *extra])


def finalize(out, *extra):
    """Run finalize and return the exit code."""
    return main(["finalize", "--out", str(out), *META, *extra])


def setup(tmp_path, by_reviewer):
    """Build the repo and an output folder holding the given reviewer findings."""
    repo = make_repo(tmp_path, {"a.py": BASE}, {"a.py": HEAD})
    out = tmp_path / "out"
    out.mkdir()
    for reviewer, findings in by_reviewer.items():
        write_reviewer(out, reviewer, findings)
    return repo, out


def load(out, name):
    """Read a JSON file from the output folder."""
    return json.loads((out / name).read_text())


def test_quote_gate_drops_a_quote_missing_from_head_and_counts_it(tmp_path):
    good = f("security", line_start=5, line_end=5, quote="line 5", severity="P2")
    bad = f("tests", line_start=9, line_end=9, quote="never written")
    repo, out = setup(tmp_path, {"security": [good], "tests": [bad]})
    assert first_pass(tmp_path, out, repo) == 0
    cand = load(out, "candidates.json")
    assert [x["quote"] for x in cand["findings"]] == ["line 5"]
    assert cand["dropped"]["quote_gate"] == 1
    assert cand["dropped_detail"][0]["reason"] == "quote_gate"


def test_old_side_finding_quoting_a_base_only_line_survives(tmp_path):
    old = f("correctness", side="old", line_start=30, line_end=30, quote="only in base")
    new = f("tests", side="new", line_start=30, line_end=30, quote="only in base")
    repo, out = setup(tmp_path, {"correctness": [old], "tests": [new]})
    first_pass(tmp_path, out, repo)
    cand = load(out, "candidates.json")
    assert [x["side"] for x in cand["findings"]] == ["old"]
    assert cand["dropped"]["quote_gate"] == 1


def test_path_outside_the_snapshot_is_dropped_and_counted(tmp_path):
    bad = f("security", file="../outside.py", quote="line 5")
    repo, out = setup(tmp_path, {"security": [bad]})
    first_pass(tmp_path, out, repo)
    cand = load(out, "candidates.json")
    assert cand["findings"] == [] and cand["dropped"]["out_of_snapshot"] == 1


def test_path_is_normalised_and_the_fingerprint_is_left_untouched(tmp_path):
    from review_core.envelope import fingerprint

    odd = f("security", file="./sub/../a.py", quote="line 5", line_start=5, line_end=5)
    repo, out = setup(tmp_path, {"security": [odd]})
    first_pass(tmp_path, out, repo)
    (kept,) = load(out, "candidates.json")["findings"]
    assert kept["file"] == "a.py" and kept["fingerprint"] == fingerprint(odd)


def test_floor_drops_weak_findings_and_agreement_never_raises_confidence(tmp_path):
    same = {"line_start": 5, "line_end": 5, "quote": "line 5", "confidence": 25}
    trio = {r: [f(r, **same)] for r in ("security", "tests", "correctness")}
    repo, out = setup(tmp_path, trio)
    first_pass(tmp_path, out, repo, "--confidence-floor", "50")
    cand = load(out, "candidates.json")
    assert cand["findings"] == []
    assert cand["dropped"]["confidence_floor"] == 3 and cand["dropped"]["duplicate"] == 0


def test_validator_input_holds_only_p0_and_p1_with_the_listed_fields(tmp_path):
    p1 = f("security", line_start=5, line_end=6, quote="line 5", severity="P1")
    p2 = f("tests", line_start=20, line_end=20, quote="line 20", severity="P2")
    repo, out = setup(tmp_path, {"security": [p1], "tests": [p2]})
    first_pass(tmp_path, out, repo)
    (item,) = load(out, "validator-input.json")["findings"]
    assert set(item) == {
        "id", "fingerprint", "file", "side", "line_start", "line_end", "quote", "title",
        "description", "severity",
    }  # fmt: skip
    assert item["severity"] == "P1"
    # The claimed range was 5-6; the quote is one line, so the finding's lines are the quote's.
    assert item["id"] == f"{item['fingerprint']}:5-5:security"


def test_validator_declining_a_finding_removes_it_and_records_the_reason(tmp_path):
    a = f("security", line_start=5, line_end=5, quote="line 5", severity="P1")
    b = f("tests", line_start=20, line_end=20, quote="line 20", severity="P0")
    repo, out = setup(tmp_path, {"security": [a], "tests": [b]})
    first_pass(tmp_path, out, repo)
    cand = {x["quote"]: x["fingerprint"] for x in load(out, "candidates.json")["findings"]}
    ids = {x["quote"]: x["id"] for x in load(out, "validator-input.json")["findings"]}
    verdicts = [
        {"id": ids["line 5"], "verdict": "declined", "reason": "guarded on line 4"},
        {"id": ids["line 20"], "verdict": "upheld", "reason": "reachable"},
        {"id": "0" * 64 + ":1-1", "verdict": "declined", "reason": "unknown, ignored"},
    ]
    (out / "validation.json").write_text(json.dumps({"verdicts": verdicts}))
    assert finalize(out) == 0
    run = load(out, "findings.json")
    assert [x["quote"] for x in run["findings"]] == ["line 20"]
    assert run["envelope"]["dropped"]["validator_declined"] == 1
    (entry,) = load(out, "declined.json")
    assert entry["fingerprint"] == cand["line 5"] and entry["reason"] == "guarded on line 4"
    assert run["envelope"]["status"] == "partial"  # five reviewers never wrote a file
    load_run_envelope(run)


def test_p0_p1_finding_without_a_verdict_stays_and_the_run_is_partial(tmp_path):
    strong = all_seven(spread)
    repo, out = setup(tmp_path, strong)
    first_pass(tmp_path, out, repo)
    ids = [x["id"] for x in load(out, "validator-input.json")["findings"]]
    rows = [{"id": i, "verdict": "upheld", "reason": "checked"} for i in ids]
    (out / "validation.json").write_text(json.dumps({"verdicts": rows[:-1]}))
    finalize(out)
    run = load(out, "findings.json")
    assert len(run["findings"]) == 7 and run["envelope"]["status"] == "partial"
    (out / "validation.json").write_text(json.dumps({"verdicts": rows}))
    finalize(out)
    assert load(out, "findings.json")["envelope"]["status"] == "complete"


def all_seven(finding_for):
    """Every reviewer present, each with one finding built by finding_for(reviewer, index)."""
    return {r: [finding_for(r, i)] for i, r in enumerate(REVIEWERS)}


def spread(reviewer, i, severity="P1"):
    """One distinct, valid finding per reviewer."""
    n = 5 + 8 * i
    return f(reviewer, line_start=n, line_end=n, quote=f"line {n}", severity=severity)


def test_missing_validation_file_with_p1_candidates_keeps_findings_and_marks_partial(tmp_path):
    repo, out = setup(tmp_path, all_seven(spread))
    first_pass(tmp_path, out, repo)
    assert finalize(out) == 0
    run = load(out, "findings.json")
    assert len(run["findings"]) == 7 and run["envelope"]["status"] == "partial"
    load_run_envelope(run)


def test_malformed_validation_file_is_a_validator_failure(tmp_path):
    for bad in ("not json", '{"verdicts": [{"id": "x"}]}', '{"verdicts": 3}', "[]"):
        sub = tmp_path / str(abs(hash(bad)))
        sub.mkdir()
        repo, out = setup(sub, all_seven(spread))
        first_pass(sub, out, repo)
        (out / "validation.json").write_text(bad)
        finalize(out)
        run = load(out, "findings.json")
        assert len(run["findings"]) == 7 and run["envelope"]["status"] == "partial", bad
        assert not (out / "declined.json").exists()


def test_no_p0_p1_candidates_means_a_missing_validation_file_is_fine(tmp_path):
    repo, out = setup(tmp_path, all_seven(lambda r, i: spread(r, i, severity="P2")))
    first_pass(tmp_path, out, repo)
    assert finalize(out) == 0
    run = load(out, "findings.json")
    assert run["envelope"]["status"] == "complete" and len(run["findings"]) == 7
    load_run_envelope(run)


def test_failed_envelope_carries_no_findings(tmp_path):
    repo, out = setup(tmp_path, {})
    first_pass(tmp_path, out, repo)
    assert finalize(out) == 0
    run = load(out, "findings.json")
    assert run["envelope"]["status"] == "failed" and run["findings"] == []
    load_run_envelope(run)


def test_every_dropped_finding_is_counted_under_exactly_one_reason(tmp_path):
    items = {
        "security": [
            f("security", line_start=5, line_end=5, quote="line 5", severity="P1"),
            f("security", line_start=8, line_end=8, quote="nowhere"),
            f("security", file="/abs.py", quote="line 5"),
            f("security", line_start=40, line_end=40, quote="line 40", confidence=0),
        ],
        "tests": [f("tests", line_start=5, line_end=5, quote="line 5", severity="P3")],
        "correctness": [
            f("correctness", line_start=5, line_end=5, quote="line 5"),
            f("correctness", line_start=50, line_end=50, quote="line 50", severity="urgent"),
        ],
    }
    repo, out = setup(tmp_path, items)
    first_pass(tmp_path, out, repo)
    cand = load(out, "candidates.json")
    total = sum(len(v) for v in items.values())
    assert set(cand["dropped"]) == set(DROP_REASONS)
    assert len(cand["findings"]) + sum(cand["dropped"].values()) == total
    assert len(cand["dropped_detail"]) == sum(cand["dropped"].values())
    assert cand["dropped"] == {
        "quote_gate": 1, "confidence_floor": 1, "duplicate": 0, "validator_declined": 0,
        "out_of_snapshot": 1, "malformed": 1,
    }  # fmt: skip
    assert finalize(out) == 0
    assert load(out, "findings.json")["envelope"]["dropped"] == cand["dropped"]


def test_every_finding_is_kept_and_names_only_the_others_within_the_window(tmp_path):
    def spaced(reviewer, i):
        n = 4 + 7 * (i % 4)  # reviewers overlap on four spots
        return f(reviewer, line_start=n, line_end=n + 1, quote=f"line {n}")

    repo, out = setup(tmp_path, all_seven(spaced))
    first_pass(tmp_path, out, repo, "--window", "3")
    kept = load(out, "candidates.json")["findings"]
    assert len(kept) == 7
    assert load(out, "candidates.json")["dropped"]["duplicate"] == 0
    for x in kept:
        spot = {y["reviewer"] for y in kept if y["line_start"] == x["line_start"]}
        assert x["also_raised_by"] == sorted(spot - {x["reviewer"]})


def test_errors_are_one_line_on_stderr_with_a_non_zero_exit(tmp_path, capsys):
    repo = make_repo(tmp_path, {"a.py": "1\n"}, {"a.py": "2\n"})
    assert first_pass(tmp_path, tmp_path / "nope", repo) != 0
    err = capsys.readouterr().err
    assert len(err.strip().splitlines()) == 1
    empty = tmp_path / "empty"
    empty.mkdir()
    assert finalize(empty) != 0
    assert "candidates.json" in capsys.readouterr().err
    assert finalize(tmp_path / "nope") != 0
    out = tmp_path / "out2"
    out.mkdir()
    code = main(["first-pass", "--out", str(out), "--repo", str(repo), "--base", "base",
                 "--head", "no-such-ref"])  # fmt: skip
    assert code != 0 and "no-such-ref" in capsys.readouterr().err


def test_module_runs_as_a_script(tmp_path):
    repo, out = setup(tmp_path, {"security": [spread("security", 0)]})
    src = str(Path(review_core.aggregator.__file__).parents[2])
    env = {**os.environ, "PYTHONPATH": src}
    cmd = [sys.executable, "-m", "review_core.aggregator.cli", "first-pass", "--out", str(out),
           "--repo", str(repo), "--base", "base", "--head", "head"]  # fmt: skip
    done = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert (out / "candidates.json").exists()


def test_aggregator_imports_only_the_standard_library_and_review_core():
    package = Path(review_core.aggregator.__file__).parent
    for path in package.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [node.module]
            for name in names:
                root = name.split(".")[0]
                assert root in sys.stdlib_module_names or root == "review_core", (path, name)


def test_finalize_runs_without_run_details_the_agent_cannot_know(tmp_path):
    # The main agent does not know its own model or CLI version; the launcher records those.
    repo, out = setup(tmp_path, all_seven(lambda r, i: spread(r, i, severity="P2")))
    first_pass(tmp_path, out, repo)
    assert main(["finalize", "--out", str(out)]) == 0
    env = load(out, "findings.json")["envelope"]
    assert (env["model"], env["cli_version"], env["status"]) == ("unknown", "unknown", "complete")


def finished_run(tmp_path):
    """A repository and an output folder after first-pass and finalize, with two findings."""
    first = f("security", line_start=5, line_end=5, quote="line 5", title="Five")
    second = f("tests", line_start=9, line_end=9, quote="line 9", severity="P3", title="Nine")
    repo, out = setup(tmp_path, {"security": [first], "tests": [second]})
    for reviewer in REVIEWERS:
        if not (out / f"findings.{reviewer}.json").exists():
            write_reviewer(out, reviewer, [])
    assert first_pass(tmp_path, out, repo) == 0
    assert finalize(out) == 0
    return out


def test_report_writes_report_md_and_prints_the_same_text(tmp_path, capsys):
    out = finished_run(tmp_path)
    (out / "pr-summary.md").write_text("It adds two checks. They touch a.py.\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["report", "--out", str(out)]) == 0
    printed = capsys.readouterr().out
    written = (out / "report.md").read_bytes().decode("utf-8")
    assert printed == written
    assert "It adds two checks. They touch a.py." in written
    assert "#### Five" in written and "#### Nine" in written
    assert "findings.json" not in {p.name for p in out.glob("report.*")}


def test_report_works_without_a_summary_file(tmp_path, capsys):
    out = finished_run(tmp_path)
    assert not (out / "pr-summary.md").exists()
    assert main(["report", "--out", str(out)]) == 0
    assert "No summary of the change was written." in capsys.readouterr().out


def test_report_ignores_a_summary_that_is_a_link(tmp_path, capsys):
    out = finished_run(tmp_path)
    secret = tmp_path / "secret.txt"
    secret.write_text("LEAKED CONTENT\n", encoding="utf-8")
    (out / "pr-summary.md").symlink_to(secret)
    assert main(["report", "--out", str(out)]) == 0
    printed = capsys.readouterr().out
    assert "LEAKED CONTENT" not in printed
    assert "No summary of the change was written." in printed


def test_report_ignores_a_summary_larger_than_64_kb(tmp_path, capsys):
    out = finished_run(tmp_path)
    (out / "pr-summary.md").write_text("Words. " * 10_000, encoding="utf-8")
    assert (out / "pr-summary.md").stat().st_size > 64 * 1024
    assert main(["report", "--out", str(out)]) == 0
    assert "No summary of the change was written." in capsys.readouterr().out


def test_report_ignores_a_summary_that_is_not_text(tmp_path, capsys):
    out = finished_run(tmp_path)
    (out / "pr-summary.md").write_bytes(b"\xff\xfe\x00bad")
    assert main(["report", "--out", str(out)]) == 0
    assert "No summary of the change was written." in capsys.readouterr().out


def test_report_without_findings_json_fails_in_one_line_and_writes_nothing(tmp_path, capsys):
    out = tmp_path / "empty"
    out.mkdir()
    assert main(["report", "--out", str(out)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("error: ") and len(captured.err.strip().splitlines()) == 1
    assert list(out.iterdir()) == []


def test_report_refuses_a_findings_file_that_breaks_the_contract(tmp_path, capsys):
    out = finished_run(tmp_path)
    doc = load(out, "findings.json")
    doc["envelope"]["status"] = "bogus"
    (out / "findings.json").write_text(json.dumps(doc), encoding="utf-8")
    assert main(["report", "--out", str(out)]) == 1
    assert not (out / "report.md").exists()
    assert len(capsys.readouterr().err.strip().splitlines()) == 1


def test_report_will_not_write_through_a_link_named_report_md(tmp_path, capsys):
    out = finished_run(tmp_path)
    target = tmp_path / "victim.txt"
    target.write_text("keep me\n", encoding="utf-8")
    (out / "report.md").symlink_to(target)
    assert main(["report", "--out", str(out)]) == 1
    assert target.read_text(encoding="utf-8") == "keep me\n"
    assert len(capsys.readouterr().err.strip().splitlines()) == 1


def test_report_leaves_every_other_file_alone(tmp_path):
    out = finished_run(tmp_path)
    before = {p.name: p.read_bytes() for p in out.iterdir()}
    assert main(["report", "--out", str(out)]) == 0
    after = {p.name: p.read_bytes() for p in out.iterdir()}
    assert set(after) - set(before) == {"report.md"}
    assert {k: v for k, v in after.items() if k != "report.md"} == before
