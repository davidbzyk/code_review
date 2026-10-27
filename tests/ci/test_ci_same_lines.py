"""CI posts each finding once, with the findings at one place in one inline comment. Runs are
built as production builds them: first_pass, an upholding validator, finalize, then publish."""

import json

import pytest
from x599 import RUNNER, SAME_LINES

from review_core.aggregator.pipeline import finalize, first_pass
from review_core.ci.github import BOT, posted_findings, pr_diff, publish
from review_core.ci.history import our_threads
from review_core.envelope import fingerprint

META = {"runner": "t", "model": "t", "effort": "t", "cli_version": "t", "sandbox_mode": "t"}
NO_THREADS = {"data": {"repository": {"pullRequest": {"reviewThreads": {"nodes": []}}}}}
CORRECTNESS = "Multi-region AWS jobs fail when runner repositories differ"
LANGUAGE = "Exclude disabled AWS regions when selecting the runner repository"
TESTS = "The repository set is rebuilt on every call"


class GitHub:
    """A pull request holding this action's earlier inline comments; records posted reviews."""

    def __init__(self, earlier: list[str] = ()):
        """Earlier inline comment bodies, posted by the action's own login."""
        self.earlier = [{"user": {"login": BOT}, "body": body} for body in earlier]
        self.reviews: list[dict] = []

    def __call__(self, method: str, url: str, token: str, body: dict | None = None):
        """Answer one REST or GraphQL call."""
        if method == "GET":
            return self.earlier if "/pulls/1/comments?" in url else []
        if url.endswith("/graphql"):
            return NO_THREADS
        if url.endswith("/pulls/1/reviews"):
            self.reviews.append(body)
        return {}


def _reviewer_finding(reviewer: str) -> dict:
    """The fixture finding one reviewer wrote."""
    return json.loads((SAME_LINES / f"findings.{reviewer}.json").read_text())["findings"][0]


def _line_302() -> dict:
    """A tests-reviewer file with one P2 on the middle line of the other two findings."""
    quoted = _reviewer_finding("correctness")
    middle = quoted["quote"].split("\n")[1]
    finding = {**quoted, "line_start": 302, "line_end": 302, "quote": middle, "title": TESTS,
               "severity": "P2", "category": "tests", "reviewer": "tests"}  # fmt: skip
    return {"schema_version": 1, "reviewer": "tests", "findings": [finding]}


def _posted(same_lines, earlier: list[str] = (), tests: bool = False) -> list[dict]:
    """The inline comments one push posts, after an upholding validator."""
    out, repo, base, head = same_lines
    if tests:
        (out / "findings.tests.json").write_text(json.dumps(_line_302()))
    first_pass(out, repo, base, head)
    given = json.loads((out / "validator-input.json").read_text())["findings"]
    verdicts = [{"id": f["id"], "verdict": "upheld", "reason": "r"} for f in given]
    (out / "validation.json").write_text(json.dumps({"verdicts": verdicts}))
    doc = finalize(out, META)
    github = GitHub(earlier)
    publish(doc, pr_diff(repo, base, head), head=head, repo="o/n", pr=1, change_summary=None,
            token="t", request=github)  # fmt: skip
    return github.reviews[0]["comments"]


def test_findings_at_one_place_share_one_inline_comment(same_lines):
    """Three reviewers' findings on overlapping lines are one thread, a section each, the most
    severe first and anchored at its lines."""
    comments = _posted(same_lines, tests=True)

    assert len(comments) == 1
    body = comments[0]["body"]
    assert body.count("<!-- code-review:v1 ") == 3
    assert body.index(CORRECTNESS) < body.index(LANGUAGE) < body.index(TESTS)
    assert (comments[0]["start_line"], comments[0]["line"]) == (301, 303)


@pytest.mark.parametrize(("reviewer", "posted"), [("correctness", [LANGUAGE]), (None, [])])
def test_a_later_push_posts_another_reviewers_point_on_already_commented_code(
    same_lines, reviewer, posted
):
    """An earlier marker suppresses only its own reviewer's finding on that quote; a marker
    written before markers named a reviewer still suppresses every finding on it."""
    marker = {"fingerprint": fingerprint(_reviewer_finding("correctness")), "head": "0" * 40}
    if reviewer:
        marker["reviewer"] = reviewer
    earlier = f"old comment\n\n<!-- code-review:v1 {json.dumps(marker, sort_keys=True)} -->"

    comments = _posted(same_lines, earlier=[earlier])

    bodies = "\n".join(c["body"] for c in comments)
    assert [title for title in (CORRECTNESS, LANGUAGE) if title in bodies] == posted


def test_an_earlier_comment_holding_three_findings_reads_back_as_three(same_lines):
    """The next review's history lists every finding one shared comment holds."""
    comment = _posted(same_lines, tests=True)[0]
    first = {"author": {"login": "github-actions"}, "authorAssociation": "NONE",
             "body": comment["body"], "createdAt": "2026-10-27T00:00:00Z",
             "originalCommit": {"oid": "0" * 40}}  # fmt: skip
    node = {"isResolved": False, "isOutdated": False, "path": RUNNER, "line": 303,
            "startLine": 301, "comments": {"nodes": [first]}}  # fmt: skip

    threads = our_threads([node])

    assert [(t.severity, t.title, t.state, t.start, t.end) for t in threads] == [
        ("P1", CORRECTNESS, "open", 301, 303),
        ("P2", LANGUAGE, "open", 301, 303),
        ("P2", TESTS, "open", 301, 303),
    ]


def test_a_place_whose_top_finding_runs_off_the_diff_is_anchored_at_a_member_on_it(same_lines):
    """The most severe finding ends past the hunk; its place still goes inline, at the first
    member whose end line is on the diff, rather than every finding moving to the body."""
    from x599 import git

    out, repo, _, _ = same_lines
    source = repo / RUNNER
    head_text = source.read_text() + "".join(f"# tail {n}\n" for n in range(305, 341))
    lines = head_text.splitlines(keepends=True)
    old = lines[:300] + [f"# old {n}\n" for n in (301, 302, 303)] + lines[303:]
    source.write_text("".join(old))
    git(repo, "commit", "-qam", "base with the tail")
    base = git(repo, "rev-parse", "HEAD")
    source.write_text(head_text)
    git(repo, "commit", "-qam", "head changes lines 301-303")
    head = git(repo, "rev-parse", "HEAD")
    wide = {**_reviewer_finding("correctness"), "line_end": 330, "severity": "P0",
            "quote": "".join(lines[300:330]).rstrip("\n"), "title": "Wide", "reviewer": "security",
            "category": "security"}  # fmt: skip
    (out / "findings.security.json").write_text(
        json.dumps({"schema_version": 1, "reviewer": "security", "findings": [wide]})
    )
    comments = _posted((out, repo, base, head))

    assert len(comments) == 1
    assert (comments[0]["start_line"], comments[0]["line"]) == (301, 303)
    assert comments[0]["body"].count("<!-- code-review:v1 ") == 3


def test_marker_text_inside_a_finding_is_not_read_back_as_a_finding(same_lines):
    """A description quoting a marker, as a review of this plugin's own changes may, is not a
    section boundary for the history, nor a fingerprint already posted."""
    out = same_lines[0]
    doc = json.loads((out / "findings.language.json").read_text())
    fake = '<!-- code-review:v1 {"fingerprint": "f", "head": "h", "reviewer": "tests"} -->'
    doc["findings"][0]["description"] += f" The test quotes {fake} as written."
    (out / "findings.language.json").write_text(json.dumps(doc))
    comment = _posted(same_lines)[0]
    first = {"author": {"login": "github-actions"}, "authorAssociation": "NONE",
             "body": comment["body"], "createdAt": "2026-10-27T00:00:00Z",
             "originalCommit": {"oid": "0" * 40}}  # fmt: skip
    node = {"isResolved": False, "isOutdated": False, "path": RUNNER, "line": 303,
            "startLine": 301, "comments": {"nodes": [first]}}  # fmt: skip

    assert [t.title for t in our_threads([node])] == [CORRECTNESS, LANGUAGE]
    assert ("f", "tests") not in posted_findings([comment["body"]])
