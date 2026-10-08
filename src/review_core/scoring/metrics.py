"""Precision, recall and F1 per case, and their macro and micro averages (KTD18).

Standard library only.

A ratio with nothing to divide by scores 0.0, except that a case with no key entries and no
in-scope findings scores 1.0 on all three.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from review_core.scoring.matcher import CaseMatch


@dataclass(frozen=True)
class CaseScore:
    """True positives, false positives (dups included), false negatives and the three ratios."""

    tp: int
    fp: int
    fn: int
    precision: float
    recall: float
    f1: float


@dataclass(frozen=True)
class Averages:
    """Macro averages of the three ratios over cases."""

    precision: float
    recall: float
    f1: float


def score_counts(tp: int, fp: int, fn: int) -> CaseScore:
    """Turn counts into a CaseScore under the empty-case conventions."""
    if tp + fp + fn == 0:
        return CaseScore(tp, fp, fn, 1.0, 1.0, 1.0)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn) if tp else 0.0
    return CaseScore(tp, fp, fn, precision, recall, f1)


def score_case(match: CaseMatch) -> CaseScore:
    """Score one matched case: dups count as false positives, neutral findings not at all."""
    labels = [r.label for r in match.results]
    return score_counts(
        tp=labels.count("tp"),
        fp=labels.count("fp") + labels.count("dup"),
        fn=len(match.missed),
    )


def macro_average(scores: Sequence[CaseScore]) -> Averages:
    """Mean of the per-case precision, recall and F1."""
    if not scores:
        raise ValueError("macro_average needs at least one case")
    n = len(scores)
    return Averages(
        precision=sum(s.precision for s in scores) / n,
        recall=sum(s.recall for s in scores) / n,
        f1=sum(s.f1 for s in scores) / n,
    )


def micro_average(scores: Sequence[CaseScore]) -> CaseScore:
    """Score from counts summed over all cases."""
    if not scores:
        raise ValueError("micro_average needs at least one case")
    return score_counts(
        tp=sum(s.tp for s in scores),
        fp=sum(s.fp for s in scores),
        fn=sum(s.fn for s in scores),
    )
