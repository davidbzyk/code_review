"""Per-case and averaged scores, checked against hand-computed values."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from review_core.contracts.models import load_findings, load_key
from review_core.scoring.matcher import dir_reader, match_case
from review_core.scoring.metrics import macro_average, micro_average, score_case, score_counts

FIXTURES = Path(__file__).parent / "fixtures"


def test_perfect_case_scores_one():
    s = score_counts(tp=2, fp=0, fn=0)
    assert (s.precision, s.recall, s.f1) == (1.0, 1.0, 1.0)


def test_empty_key_and_empty_findings_score_one():
    s = score_counts(tp=0, fp=0, fn=0)
    assert (s.precision, s.recall, s.f1) == (1.0, 1.0, 1.0)


def test_empty_key_with_one_false_positive_scores_zero():
    s = score_counts(tp=0, fp=1, fn=0)
    assert s.f1 == 0.0
    assert s.precision == 0.0


def test_key_with_no_findings_scores_zero():
    s = score_counts(tp=0, fp=0, fn=3)
    assert (s.precision, s.recall, s.f1) == (0.0, 0.0, 0.0)


def test_no_true_positives_scores_zero_f1():
    s = score_counts(tp=0, fp=2, fn=2)
    assert s.f1 == 0.0


def test_counts_are_kept_on_the_score():
    s = score_counts(tp=3, fp=2, fn=1)
    assert (s.tp, s.fp, s.fn) == (3, 2, 1)


def test_five_entry_fixture_matches_hand_computed_values():
    # Entries e1..e5 (e5 is tier 3). tp = e1, e2, e3; fp = one dup + one stray; fn = e4.
    # precision 3/5, recall 3/4, f1 = 2*3 / (2*3 + 2 + 1) = 2/3.
    key = load_key(json.loads((FIXTURES / "five" / "key.json").read_text()))
    doc = load_findings(json.loads((FIXTURES / "five" / "findings.json").read_text()))
    read = dir_reader(FIXTURES / "five" / "head", FIXTURES / "five" / "head")
    s = score_case(match_case(doc.findings, key.entries, read))
    assert (s.tp, s.fp, s.fn) == (3, 2, 1)
    assert s.precision == pytest.approx(0.6)
    assert s.recall == pytest.approx(0.75)
    assert s.f1 == pytest.approx(2 / 3)


def test_macro_average_is_the_mean_of_per_case_values():
    a = score_counts(3, 2, 1)  # p 0.6, r 0.75, f1 2/3
    b = score_counts(1, 0, 3)  # p 1.0, r 0.25, f1 0.4
    m = macro_average([a, b])
    assert m.precision == pytest.approx(0.8)
    assert m.recall == pytest.approx(0.5)
    assert m.f1 == pytest.approx((2 / 3 + 0.4) / 2)


def test_micro_average_comes_from_summed_counts():
    a = score_counts(3, 2, 1)
    b = score_counts(1, 0, 3)
    m = micro_average([a, b])  # tp 4, fp 2, fn 4
    assert (m.tp, m.fp, m.fn) == (4, 2, 4)
    assert m.precision == pytest.approx(2 / 3)
    assert m.recall == pytest.approx(0.5)
    assert m.f1 == pytest.approx(8 / 14)


def test_averages_of_nothing_are_an_error():
    with pytest.raises(ValueError):
        macro_average([])
    with pytest.raises(ValueError):
        micro_average([])
