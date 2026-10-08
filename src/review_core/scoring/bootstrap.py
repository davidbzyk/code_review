"""Paired cluster bootstrap of the difference between two arms (KTD18). Standard library only.

Items are grouped by cluster key (a pull request id for the headline analysis, an entry id for
the entry-level sensitivity analysis). Each resample draws whole clusters with replacement, so
items of one cluster always move together.
"""

from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class PairedScore:
    """One case's score under arm A and arm B (already averaged over repeats), and its cluster."""

    cluster: str
    a: float
    b: float


@dataclass(frozen=True)
class BootstrapResult:
    """Observed mean difference (A minus B) and its percentile interval."""

    observed: float
    low: float
    high: float
    resamples: int
    confidence: float


def paired_bootstrap(
    items: Sequence[PairedScore],
    resamples: int = 10_000,
    confidence: float = 0.95,
    seed: int = 0,
) -> BootstrapResult:
    """Bootstrap the mean of a - b over items, resampling clusters; reproducible from seed."""
    if not items:
        raise ValueError("paired_bootstrap needs at least one item")
    if resamples < 1:
        raise ValueError("resamples must be at least 1")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    groups: dict[str, list[float]] = defaultdict(list)
    for item in items:
        groups[item.cluster].append(item.a - item.b)
    clusters = [(sum(diffs), len(diffs)) for diffs in groups.values()]
    total, count = (sum(c[0] for c in clusters), sum(c[1] for c in clusters))
    rng = random.Random(seed)
    k = len(clusters)
    means = []
    for _ in range(resamples):
        drawn = rng.choices(clusters, k=k)
        means.append(sum(c[0] for c in drawn) / sum(c[1] for c in drawn))
    means.sort()
    tail = (1 - confidence) / 2
    low = means[int(tail * resamples)]
    high = means[min(resamples - 1, int((1 - tail) * resamples))]
    return BootstrapResult(total / count, low, high, resamples, confidence)
