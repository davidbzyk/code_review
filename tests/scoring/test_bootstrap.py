"""Paired cluster bootstrap of the difference between two arms."""

from __future__ import annotations

import pytest

from review_core.scoring.bootstrap import PairedScore, paired_bootstrap


def test_observed_difference_is_the_mean_of_per_case_differences():
    items = [
        PairedScore("pr1", 0.9, 0.5),
        PairedScore("pr2", 0.7, 0.5),
        PairedScore("pr3", 0.5, 0.5),
    ]
    result = paired_bootstrap(items, resamples=200, seed=1)
    assert result.observed == pytest.approx((0.4 + 0.2 + 0.0) / 3)


def test_slices_of_one_pull_request_move_together():
    # pr1 holds two slices whose differences are +1 and -1; pr2 has one slice with 0.
    # Resampling whole pull requests always draws the two pr1 slices as a pair, so every
    # resample mean is exactly 0. Resampling slices on their own would spread well past it.
    items = [
        PairedScore("pr1", 1.0, 0.0),
        PairedScore("pr1", 0.0, 1.0),
        PairedScore("pr2", 0.5, 0.5),
    ]
    result = paired_bootstrap(items, resamples=2000, seed=7)
    assert result.observed == 0.0
    assert (result.low, result.high) == (0.0, 0.0)


def test_two_clusters_interval_spans_the_possible_resample_means():
    # Differences 1 and 0 in separate clusters: resample means can only be 0, 0.5 or 1.
    items = [PairedScore("pr1", 1.0, 0.0), PairedScore("pr2", 0.0, 0.0)]
    result = paired_bootstrap(items, resamples=2000, seed=3)
    assert result.observed == 0.5
    assert (result.low, result.high) == (0.0, 1.0)


def test_identical_differences_give_a_point_interval():
    items = [PairedScore(f"pr{i}", 0.75, 0.25) for i in range(5)]
    result = paired_bootstrap(items, resamples=500, seed=2)
    assert (result.low, result.observed, result.high) == (0.5, 0.5, 0.5)


def test_same_seed_gives_the_same_result_and_a_different_seed_may_differ():
    items = [PairedScore(f"pr{i}", i / 10, 0.3) for i in range(8)]
    first = paired_bootstrap(items, resamples=300, seed=11)
    again = paired_bootstrap(items, resamples=300, seed=11)
    assert first == again
    assert first.resamples == 300 and first.confidence == 0.95


def test_defaults_are_ten_thousand_resamples_and_95_percent():
    items = [PairedScore("pr1", 1.0, 0.0), PairedScore("pr2", 0.0, 0.0)]
    result = paired_bootstrap(items, seed=0)
    assert result.resamples == 10_000
    assert result.confidence == 0.95


def test_entry_level_sensitivity_reuses_the_resampler_with_entry_ids_as_clusters():
    # Each entry is its own cluster; the score is 1 when the arm found it, else 0.
    items = [PairedScore("e1", 1.0, 0.0), PairedScore("e2", 1.0, 0.0), PairedScore("e3", 0.0, 0.0)]
    result = paired_bootstrap(items, resamples=1000, seed=5)
    assert result.observed == pytest.approx(2 / 3)
    assert 0.0 <= result.low <= result.observed <= result.high <= 1.0


def test_empty_input_and_bad_arguments_are_errors():
    with pytest.raises(ValueError):
        paired_bootstrap([], resamples=10, seed=0)
    item = [PairedScore("pr1", 1.0, 0.0)]
    with pytest.raises(ValueError):
        paired_bootstrap(item, resamples=0, seed=0)
    with pytest.raises(ValueError):
        paired_bootstrap(item, resamples=10, confidence=1.0, seed=0)
